# tests for new CLI and schema mapping (using temp CSVs)
import pandas as pd
import tempfile
import os
from football_analysis.data.schema import map_columns
from football_analysis.cli import cmd_inspect_csv, cmd_similar, cmd_movement


def test_schema_map():
    df = pd.DataFrame({'match_date':['2026-01-01'],'home':['H'],'away':['A'],'1':[1.9],'X':[3.4],'2':[4.2]})
    out = map_columns(df)
    assert 'date' in out.columns
    assert 'raw_match_date' in out.columns


def test_cli_inspect(tmp_path, capsys):
    p = tmp_path / 'odds.csv'
    df = pd.DataFrame({'fixture_id':[1], 'bookmaker':['B'], 'odds':[1.9], 'timestamp':['2026-01-01T00:00:00'], 'result':[None]})
    df.to_csv(p, index=False)
    class Args: pass
    args = Args(); args.path = str(p)
    cmd_inspect_csv(args)
    captured = capsys.readouterr()
    assert 'CSV Inspection' in captured.out


def test_cli_similar(tmp_path, capsys):
    p = tmp_path / 'odds.csv'
    df = pd.DataFrame({'fixture_id':[1], 'home_odds':[1.9], 'draw_odds':[3.4], 'away_odds':[4.2], 'bookmaker':['B'], 'timestamp':['2026-01-01T00:00:00'], 'league':['L']})
    df.to_csv(p, index=False)
    # monkeypatch HIST_ODDS path
    os.environ['HISTORICAL_ODDS_PATH'] = str(p)
    class Args: pass
    args = Args(); args.home_odds=1.9; args.draw_odds=3.4; args.away_odds=4.2; args.handicap=None; args.bookmaker=None; args.league=None; args.top_k=1; args.cutoff=None
    cmd_similar(args)
    captured = capsys.readouterr()
    assert 'matched_count:' in captured.out


def test_cli_movement(tmp_path, capsys):
    p = tmp_path / 'odds.csv'
    df = pd.DataFrame({'fixture_id':[1,1], 'home_odds':[2.1,1.9], 'draw_odds':[3.3,3.45], 'away_odds':[3.2,3.7], 'handicap':[0.0,0.25], 'timestamp':['2026-01-01T00:00:00','2026-01-01T01:00:00']})
    df.to_csv(p, index=False)
    os.environ['HISTORICAL_ODDS_PATH'] = str(p)
    os.environ['HISTORICAL_MATCHES_PATH'] = str(tmp_path / 'matches.csv')
    class Args: pass
    args = Args(); args.open_home=2.1; args.open_draw=3.3; args.open_away=3.2; args.current_home=1.9; args.current_draw=3.45; args.current_away=3.7; args.top_k=1
    cmd_movement(args)
    captured = capsys.readouterr()
    assert 'historical_similar_count:' in captured.out
