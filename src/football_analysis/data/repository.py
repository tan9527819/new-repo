"""
Repository mapping between dataframe rows and MatchRecord dataclass.
Fixed to include season and status fields.
"""
from typing import Optional, List, Tuple
import os
from pathlib import Path
import pandas as pd
import numpy as np

from .csv_loader import infer_columns, read_and_clean_csv
from .models import MatchRecord


def _df_to_matchrecord(row: pd.Series) -> MatchRecord:
    return MatchRecord(
        match_id=str(row.get('match_id', None)) if 'match_id' in row.index else None,
        date=row.get('date', None),
        league=row.get('league', None) if 'league' in row.index else None,
        season=row.get('season', None) if 'season' in row.index else None,
        home_team=row.get('home_team', None),
        away_team=row.get('away_team', None),
        status=row.get('status', None) if 'status' in row.index else None,
        home_odds=row.get('home_odds', None),
        draw_odds=row.get('draw_odds', None),
        away_odds=row.get('away_odds', None),
        handicap=row.get('handicap', None),
        handicap_home_odds=row.get('handicap_home_odds', None),
        handicap_away_odds=row.get('handicap_away_odds', None),
        source=row.get('source', None),
    )


def load_matches(path: Optional[str] = None, n: Optional[int] = None) -> List[MatchRecord]:
    path = path or os.getenv('HISTORICAL_DATA_PATH')
    if not path:
        raise RuntimeError('HISTORICAL_DATA_PATH not set and no path provided')
    df = read_and_clean_csv(path)
    if n:
        df = df.sort_values('date', ascending=False).head(n)
    records = [_df_to_matchrecord(r) for _, r in df.iterrows()]
    return records


def find_similar_matches(target_odds: Tuple[float, float, float], path: Optional[str] = None, top_k: int = 10):
    """基于简单欧氏距离在历史赔率中寻找相似盘口（home, draw, away）。
    target_odds: (home_odds, draw_odds, away_odds)
    """
    path = path or os.getenv('HISTORICAL_DATA_PATH')
    if not path:
        raise RuntimeError('HISTORICAL_DATA_PATH not set and no path provided')
    df = infer_columns(path)
    # Drop rows with NaN odds
    df = df.dropna(subset=['home_odds', 'draw_odds', 'away_odds'])
    if df.empty:
        return []
    X = df[['home_odds', 'draw_odds', 'away_odds']].to_numpy(dtype=float)
    import numpy as _np
    target = _np.array(target_odds, dtype=float)
    dists = _np.linalg.norm(X - target, axis=1)
    idx = _np.argsort(dists)[:top_k]
    results = df.iloc[idx].copy()
    results['distance'] = dists[idx]
    return results


def find_same_odds(odds_tuple: Tuple[float, float, float], path: Optional[str] = None, tol: float = 1e-6):
    path = path or os.getenv('HISTORICAL_DATA_PATH')
    if not path:
        raise RuntimeError('HISTORICAL_DATA_PATH not set and no path provided')
    df = infer_columns(path)
    cond = (
        (df['home_odds'].notna()) &
        (df['draw_odds'].notna()) &
        (df['away_odds'].notna()) &
        (df['home_odds'].sub(odds_tuple[0]).abs() <= tol) &
        (df['draw_odds'].sub(odds_tuple[1]).abs() <= tol) &
        (df['away_odds'].sub(odds_tuple[2]).abs() <= tol)
    )
    return df[cond]


def get_recent_results(path: Optional[str] = None, n: int = 50):
    path = path or os.getenv('HISTORICAL_DATA_PATH')
    if not path:
        raise RuntimeError('HISTORICAL_DATA_PATH not set and no path provided')
    df = read_and_clean_csv(path)
    df = df.sort_values('date', ascending=False)
    return df.head(n)
