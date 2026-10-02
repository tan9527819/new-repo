"""
Update CLI to include CSV inspection, similarity, movement matching, analyze and backtest CLI commands.
"""
import argparse
import os
import logging
import json
from typing import Optional
import pandas as pd
from datetime import datetime

from .api.client import APIFootballClient
from .api.fixtures import FixturesClient
from .api.odds import OddsClient
from .data.exporter import export_matches, export_odds
from .data.cache import get_cache, set_cache
from .data.csv_loader import read_and_clean_csv, infer_columns
from .data.quality import quality_report_matches, quality_report_odds
from .data.schema import map_columns
from .analysis.same_odds import find_same_odds_from_df, find_similar_odds_from_df
from .analysis.movement_similarity import movement_similarity
from .analysis.odds_normalizer import to_feature_vector
from .analysis.report import generate_report

logger = logging.getLogger(__name__)

HIST_MATCHES = os.getenv('HISTORICAL_MATCHES_PATH', './data/historical/matches.csv')
HIST_ODDS = os.getenv('HISTORICAL_ODDS_PATH', './data/historical/odds.csv')
REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)


def cmd_inspect_csv(args):
    path = args.path or HIST_ODDS
    if not os.path.exists(path):
        print('CSV not found:', path)
        return
    df = pd.read_csv(path)
    total = len(df)
    matches = df['fixture_id'].nunique() if 'fixture_id' in df.columns else df.get('match_id', pd.Series()).nunique()
    bookmakers = df['bookmaker'].nunique() if 'bookmaker' in df.columns else 0
    leagues = df['league'].nunique() if 'league' in df.columns else 0
    date_min = df['timestamp'].min() if 'timestamp' in df.columns else None
    date_max = df['timestamp'].max() if 'timestamp' in df.columns else None
    valid_odds = df['odds'].notna().sum() if 'odds' in df.columns else 0
    missing = df.isna().sum().to_dict()
    duplicates = int(df.duplicated().sum())
    nonpositive = int((df['odds'].dropna() <= 0).sum()) if 'odds' in df.columns else 0
    has_result = int(df['result'].notna().sum()) if 'result' in df.columns else 0
    no_result = total - has_result
    print('CSV Inspection:', path)
    print(' total_records:', total)
    print(' unique_matches:', matches)
    print(' bookmakers:', bookmakers)
    print(' leagues:', leagues)
    print(' date_range:', date_min, '->', date_max)
    print(' valid_odds:', valid_odds)
    print(' missing_counts (sample):', dict(list(missing.items())[:10]))
    print(' duplicates:', duplicates)
    print(' nonpositive_odds:', nonpositive)
    print(' has_result:', has_result)
    print(' no_result:', no_result)


def cmd_similar(args):
    # Build target dict
    target = {
        'home_odds': args.home_odds,
        'draw_odds': args.draw_odds,
        'away_odds': args.away_odds,
        'handicap': getattr(args, 'handicap', None),
        'bookmaker': getattr(args, 'bookmaker', None),
        'timestamp': datetime.utcnow(),
        'league': getattr(args, 'league', None),
    }
    if not os.path.exists(HIST_ODDS):
        print('Historical odds CSV not found:', HIST_ODDS)
        return
    df = pd.read_csv(HIST_ODDS)
    # enforce cutoff if provided
    cutoff = getattr(args, 'cutoff', None)
    if cutoff:
        df = df[df['timestamp'] < cutoff]
    # find similar
    sim = find_similar_odds_from_df(df, target, top_k=args.top_k)
    print('matched_count:', len(sim))
    if sim:
        top = sim[0]
        print('top_similarity:', top.get('_similarity'))
        meta = top.get('meta', {})
        print('match sample:', {k: meta.get(k) for k in ['fixture_id','date','league','home_team','away_team','home_odds','draw_odds','away_odds','bookmaker','timestamp','result'] if k in meta})


def _fixture_initial_current_from_odds(df_odds, fixture_id: str):
    sub = df_odds[df_odds['fixture_id'].astype(str) == str(fixture_id)].copy()
    if sub.empty:
        return None, None
    # ensure timestamp parsed
    try:
        sub['timestamp'] = pd.to_datetime(sub['timestamp'])
    except Exception:
        pass
    sub = sub.sort_values('timestamp')
    # initial: earliest, current: latest
    first = sub.iloc[0]
    last = sub.iloc[-1]
    initial = {'home_odds': first.get('home_odds') if 'home_odds' in first.index else None,
               'draw_odds': first.get('draw_odds') if 'draw_odds' in first.index else None,
               'away_odds': first.get('away_odds') if 'away_odds' in first.index else None,
               'handicap': first.get('handicap') if 'handicap' in first.index else None}
    current = {'home_odds': last.get('home_odds'), 'draw_odds': last.get('draw_odds'), 'away_odds': last.get('away_odds'), 'handicap': last.get('handicap')}
    return initial, current


def cmd_movement(args):
    if not os.path.exists(HIST_ODDS):
        print('Historical odds CSV not found:', HIST_ODDS)
        return
    df = pd.read_csv(HIST_ODDS)
    initial = {'home_odds': args.open_home, 'draw_odds': args.open_draw, 'away_odds': args.open_away, 'handicap': getattr(args,'open_handicap', None)}
    current = {'home_odds': args.current_home, 'draw_odds': args.current_draw, 'away_odds': args.current_away, 'handicap': getattr(args,'current_handicap', None)}
    # build historical_changes from df by grouping fixtures
    hists = []
    for fid, group in df.groupby('fixture_id'):
        init, cur = _fixture_initial_current_from_odds(df, fid)
        if init and cur:
            # find result from matches file if exists
            result = None
            if os.path.exists(HIST_MATCHES):
                md = pd.read_csv(HIST_MATCHES)
                row = md[md['match_id'].astype(str) == str(fid)]
                if not row.empty and 'result' in row.columns:
                    result = row.iloc[0].get('result')
            hists.append({'initial': init, 'current': cur, 'result': result})
    res = movement_similarity(initial, current, hists, top_k=args.top_k)
    print('historical_similar_count:', res.get('sample_size'))
    print('conclusion:', res.get('conclusion'))
    if res.get('aggregates'):
        print('aggregates:', res['aggregates'])


def cmd_analyze(args):
    # high-level pipeline for a date
    date = args.date
    if not date:
        print('Please provide --date YYYY-MM-DD')
        return
    # load matches for date
    if not os.path.exists(HIST_MATCHES):
        print('Historical matches CSV not found:', HIST_MATCHES)
        return
    md = pd.read_csv(HIST_MATCHES)
    md['date'] = pd.to_datetime(md['date'], errors='coerce')
    day = pd.to_datetime(date)
    matches = md[md['date'].dt.date == day.date()]
    reports = []
    for _, row in matches.iterrows():
        fid = row.get('match_id') or row.get('fixture_id')
        # build market data from odds
        market_data = row.to_dict()
        # prepare cutoff - match start
        cutoff = row.get('date')
        # load historical odds and filter
        if os.path.exists(HIST_ODDS):
            od = pd.read_csv(HIST_ODDS)
            # ensure timestamp parsed
            try:
                od['timestamp'] = pd.to_datetime(od['timestamp'])
            except Exception:
                pass
            # prevent leakage
            od_hist = od[od['timestamp'] < cutoff]
        else:
            od_hist = pd.DataFrame()
        # same odds
        target = {'home_odds': row.get('home_odds'), 'draw_odds': row.get('draw_odds'), 'away_odds': row.get('away_odds'), 'handicap': row.get('handicap'), 'bookmaker': row.get('bookmaker'), 'timestamp': cutoff, 'league': row.get('league')}
        same = []
        similar = []
        movements = {}
        aggregates = {}
        quality = {}
        if not od_hist.empty:
            similar = find_similar_odds_from_df(od_hist, target, top_k=10)
        rpt = generate_report(market_data, same, similar, movements, aggregates, quality)
        reports.append({'match_id': fid, 'report': rpt})
    # save reports
    out_path = os.path.join(REPORT_DIR, f"{date}-analysis.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(reports, f, default=str, ensure_ascii=False, indent=2)
    print('Saved report to', out_path)


def cmd_backtest(args):
    # wrapper to call analysis.backtest on provided historical CSV
    from .analysis.backtest import backtest
    if not os.path.exists(HIST_MATCHES):
        print('Historical matches CSV not found:', HIST_MATCHES)
        return
    md = pd.read_csv(HIST_MATCHES)
    # build simple historical_matches list expected by backtest
    hist = []
    for _, r in md.iterrows():
        hist.append({'date': r.get('date'), 'initial_odds': None, 'current_odds': None, 'result': r.get('result')})
    def model_func(m, h):
        # naive uniform
        return (1/3,1/3,1/3)
    res = backtest(hist, model_func)
    print('backtest result:', res)


def main():
    parser = argparse.ArgumentParser(prog='football_analysis')
    sub = parser.add_subparsers(dest='cmd')

    # existing commands (fixtures, odds, sync, quality) are left in the old cli; import if needed
    p_ins = sub.add_parser('inspect-csv')
    p_ins.add_argument('--path', help='path to CSV')

    p_sim = sub.add_parser('similar')
    p_sim.add_argument('--home-odds', type=float, required=True)
    p_sim.add_argument('--draw-odds', type=float, required=True)
    p_sim.add_argument('--away-odds', type=float, required=True)
    p_sim.add_argument('--handicap', type=float, required=False)
    p_sim.add_argument('--bookmaker', type=str, required=False)
    p_sim.add_argument('--league', type=str, required=False)
    p_sim.add_argument('--top-k', type=int, default=10)
    p_sim.add_argument('--cutoff', type=str, required=False)

    p_mov = sub.add_parser('movement')
    p_mov.add_argument('--open-home', type=float, required=True)
    p_mov.add_argument('--open-draw', type=float, required=True)
    p_mov.add_argument('--open-away', type=float, required=True)
    p_mov.add_argument('--current-home', type=float, required=True)
    p_mov.add_argument('--current-draw', type=float, required=True)
    p_mov.add_argument('--current-away', type=float, required=True)
    p_mov.add_argument('--top-k', type=int, default=20)

    p_an = sub.add_parser('analyze')
    p_an.add_argument('--date', required=True)

    p_bt = sub.add_parser('backtest')

    args = parser.parse_args()
    if args.cmd == 'inspect-csv':
        cmd_inspect_csv(args)
    elif args.cmd == 'similar':
        cmd_similar(args)
    elif args.cmd == 'movement':
        cmd_movement(args)
    elif args.cmd == 'analyze':
        cmd_analyze(args)
    elif args.cmd == 'backtest':
        cmd_backtest(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
