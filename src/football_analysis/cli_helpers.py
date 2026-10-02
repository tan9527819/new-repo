"""
CLI updates: ensure cutoff_time enforcement and robust extraction of initial/current odds from per-selection odds CSVs.
"""
# (only updating helper functions within cli.py content)
from typing import Optional
import pandas as pd


def _fixture_initial_current_from_odds(df_odds: pd.DataFrame, fixture_id: str):
    sub = df_odds[df_odds['fixture_id'].astype(str) == str(fixture_id)].copy()
    if sub.empty:
        return None, None
    # ensure timestamp parsed
    if 'timestamp' in sub.columns:
        try:
            sub['timestamp'] = pd.to_datetime(sub['timestamp'])
        except Exception:
            pass
    # If dataframe already has home_odds column, use earliest/latest rows
    if 'home_odds' in sub.columns and 'draw_odds' in sub.columns and 'away_odds' in sub.columns:
        sub = sub.sort_values('timestamp') if 'timestamp' in sub.columns else sub
        first = sub.iloc[0]
        last = sub.iloc[-1]
        initial = {'home_odds': first.get('home_odds'), 'draw_odds': first.get('draw_odds'), 'away_odds': first.get('away_odds'), 'handicap': first.get('handicap')}
        current = {'home_odds': last.get('home_odds'), 'draw_odds': last.get('draw_odds'), 'away_odds': last.get('away_odds'), 'handicap': last.get('handicap')}
        return initial, current
    # Otherwise, pivot selections by timestamp
    # create wide table per timestamp with columns home_odds, draw_odds, away_odds
    def map_selection(s):
        if pd.isna(s):
            return None
        ss = str(s).strip().lower()
        if ss in ('home','1','h'):
            return 'home'
        if ss in ('draw','x'):
            return 'draw'
        if ss in ('away','2','a'):
            return 'away'
        return None

    records = []
    for _, row in sub.iterrows():
        ts = row.get('timestamp') if 'timestamp' in row.index else None
        try:
            ts = pd.to_datetime(ts)
        except Exception:
            ts = None
        sel = map_selection(row.get('selection')) if 'selection' in row.index else None
        odds = row.get('odds')
        line = row.get('line') if 'line' in row.index else row.get('handicap') if 'handicap' in row.index else None
        bookmaker = row.get('bookmaker') if 'bookmaker' in row.index else None
        records.append({'timestamp': ts, 'selection': sel, 'odds': odds, 'line': line, 'bookmaker': bookmaker})
    if not records:
        return None, None
    wdf = pd.DataFrame(records)
    # group by timestamp and aggregate selections
    grouped = wdf.groupby('timestamp')
    snapshots = []
    for ts, g in grouped:
        row = {'timestamp': ts}
        for _, r in g.iterrows():
            if r['selection'] == 'home':
                row['home_odds'] = r['odds']
            elif r['selection'] == 'draw':
                row['draw_odds'] = r['odds']
            elif r['selection'] == 'away':
                row['away_odds'] = r['odds']
            # line/handicap: take first non-null
            if 'line' in r and r['line'] is not None:
                row['handicap'] = r['line']
        snapshots.append(row)
    if not snapshots:
        return None, None
    s_df = pd.DataFrame(snapshots).sort_values('timestamp')
    first = s_df.iloc[0].to_dict()
    last = s_df.iloc[-1].to_dict()
    initial = {'home_odds': first.get('home_odds'), 'draw_odds': first.get('draw_odds'), 'away_odds': first.get('away_odds'), 'handicap': first.get('handicap')}
    current = {'home_odds': last.get('home_odds'), 'draw_odds': last.get('draw_odds'), 'away_odds': last.get('away_odds'), 'handicap': last.get('handicap')}
    return initial, current
