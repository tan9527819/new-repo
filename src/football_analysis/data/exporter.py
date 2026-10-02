"""
CSV 导出器：将标准化的 MatchRecord / OddsRecord 写入历史 CSV，支持追加与去重。
"""
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
import os

from .models import MatchRecord, OddsRecord


HIST_DIR = Path(os.getenv('HISTORICAL_DATA_PATH', './data/historical')).parent / 'historical'
HIST_DIR.mkdir(parents=True, exist_ok=True)
MATCHES_CSV = HIST_DIR / 'matches.csv'
ODDS_CSV = HIST_DIR / 'odds.csv'


def _ensure_df(cols, path: Path):
    if path.exists():
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=cols)


def export_matches(records: List[MatchRecord], path: Path = MATCHES_CSV):
    cols = ['match_id', 'date', 'league', 'season', 'home_team', 'away_team', 'status', 'home_odds', 'draw_odds', 'away_odds', 'handicap', 'handicap_home_odds', 'handicap_away_odds', 'source']
    df_existing = _ensure_df(cols, path)
    df_new = pd.DataFrame([r.to_dict() for r in records])
    if df_new.empty:
        return path
    df_combined = pd.concat([df_existing, df_new], ignore_index=True, sort=False)
    # dedupe by match_id
    if 'match_id' in df_combined.columns:
        df_combined = df_combined.drop_duplicates(subset=['match_id'], keep='last')
    df_combined.to_csv(path, index=False)
    return path


def export_odds(records: List[OddsRecord], path: Path = ODDS_CSV):
    cols = ['fixture_id', 'bookmaker', 'market', 'selection', 'line', 'odds', 'timestamp', 'raw']
    df_existing = _ensure_df(cols, path)
    df_new = pd.DataFrame([r.to_dict() for r in records])
    if df_new.empty:
        return path
    df_combined = pd.concat([df_existing, df_new], ignore_index=True, sort=False)
    # dedupe by fixture_id + bookmaker + market + selection + line + timestamp
    subset = ['fixture_id', 'bookmaker', 'market', 'selection', 'line', 'timestamp']
    existing_cols = [c for c in subset if c in df_combined.columns]
    if existing_cols:
        df_combined = df_combined.drop_duplicates(subset=existing_cols, keep='last')
    df_combined.to_csv(path, index=False)
    return path
