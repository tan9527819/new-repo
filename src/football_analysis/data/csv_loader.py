"""
CSV Loader：
- 读取历史赔率 CSV
- 自动识别常见列名
- 基础清洗（日期解析、赔率转浮点、盘口字段归一）
- 不修改原始 CSV
"""

from pathlib import Path
from typing import Tuple, List
import pandas as pd
import numpy as np

COMMON_DATE_COLUMNS = ['date', 'match_date', 'kickoff', 'datetime']
COMMON_HOME_COLUMNS = ['home_team', 'home', 'homeName', 'Home']
COMMON_AWAY_COLUMNS = ['away_team', 'away', 'awayName', 'Away']
COMMON_HOME_ODDS = ['home_odds', '1', 'odds_1', 'odds_home', 'homeWin']
COMMON_DRAW_ODDS = ['draw_odds', 'X', 'odds_x', 'odds_draw', 'draw']
COMMON_AWAY_ODDS = ['away_odds', '2', 'odds_2', 'odds_away', 'awayWin']
COMMON_HANDICAP = ['handicap', 'handicap_line', 'spread']
COMMON_HANDICAP_HOME = ['handicap_home_odds', 'handicap_1']
COMMON_HANDICAP_AWAY = ['handicap_away_odds', 'handicap_2']


class CSVLoadError(Exception):
    pass


def _find_column(df_cols: List[str], candidates: List[str]):
    for c in candidates:
        if c in df_cols:
            return c
    # case-insensitive search
    lower = {col.lower(): col for col in df_cols}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def read_and_clean_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise CSVLoadError(f'CSV file not found: {path}')
    df = pd.read_csv(p)
    cols = list(df.columns)

    # Identify main columns
    date_col = _find_column(cols, COMMON_DATE_COLUMNS)
    home_col = _find_column(cols, COMMON_HOME_COLUMNS)
    away_col = _find_column(cols, COMMON_AWAY_COLUMNS)
    home_odds_col = _find_column(cols, COMMON_HOME_ODDS)
    draw_odds_col = _find_column(cols, COMMON_DRAW_ODDS)
    away_odds_col = _find_column(cols, COMMON_AWAY_ODDS)
    handicap_col = _find_column(cols, COMMON_HANDICAP)
    handicap_home_col = _find_column(cols, COMMON_HANDICAP_HOME)
    handicap_away_col = _find_column(cols, COMMON_HANDICAP_AWAY)

    missing = []
    if not date_col:
        missing.append('date')
    if not home_col:
        missing.append('home_team')
    if not away_col:
        missing.append('away_team')
    if not home_odds_col:
        missing.append('home_odds')
    if not draw_odds_col:
        missing.append('draw_odds')
    if not away_odds_col:
        missing.append('away_odds')

    if missing:
        raise CSVLoadError(f'Missing required columns: {missing}. Found columns: {cols}')

    # Work on a copy to avoid changing original CSV
    out = df.copy()

    # Parse date
    out['date'] = pd.to_datetime(out[date_col], errors='coerce')
    n_bad_dates = out['date'].isna().sum()
    if n_bad_dates > 0:
        print(f'[warning] {n_bad_dates} rows have unparseable dates; they will be NaT')

    # Teams
    out['home_team'] = out[home_col].astype(str)
    out['away_team'] = out[away_col].astype(str)

    # Odds to numeric
    for col, name in [(home_odds_col, 'home_odds'), (draw_odds_col, 'draw_odds'), (away_odds_col, 'away_odds')]:
        out[name] = pd.to_numeric(out[col], errors='coerce')
        n_nan = out[name].isna().sum()
        if n_nan > 0:
            print(f'[warning] {n_nan} rows: {name} could not be converted to numeric')

    # Handicap fields
    if handicap_col:
        out['handicap'] = pd.to_numeric(out[handicap_col], errors='coerce')
    else:
        out['handicap'] = np.nan

    if handicap_home_col:
        out['handicap_home_odds'] = pd.to_numeric(out[handicap_home_col], errors='coerce')
    else:
        out['handicap_home_odds'] = np.nan

    if handicap_away_col:
        out['handicap_away_odds'] = pd.to_numeric(out[handicap_away_col], errors='coerce')
    else:
        out['handicap_away_odds'] = np.nan

    # Source column
    if 'source' not in out.columns:
        out['source'] = str(p)

    return out


def infer_columns(path: str):
    df = read_and_clean_csv(path)
    # Return standardized subset
    cols = ['date', 'home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds', 'handicap', 'handicap_home_odds', 'handicap_away_odds', 'source']
    return df[cols]
