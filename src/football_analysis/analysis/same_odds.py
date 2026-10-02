"""
历史同赔搜索：在历史 CSV 中查找相同或接近的赔率记录。
This module now normalizes timestamps and supports cutoff filtering to prevent data leakage.
"""
from typing import Tuple, Optional, List, Dict, Any
import os
import pandas as pd
from .odds_normalizer import to_feature_vector, normalize_timestamp


def _ensure_timestamp(val):
    if val is None:
        return None
    if isinstance(val, pd.Timestamp):
        return val.to_pydatetime()
    try:
        return normalize_timestamp(str(val))
    except Exception:
        return None


def find_same_odds_from_df(df: pd.DataFrame, odds_tuple: Tuple[float, float, float], tol: float = 1e-6, league: Optional[str] = None, cutoff=None) -> pd.DataFrame:
    # if cutoff provided, ensure timestamp column exists and filter
    if cutoff is not None and 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            cutoff_ts = pd.to_datetime(cutoff)
            df = df[df['timestamp'] < cutoff_ts]
        except Exception:
            pass
    h, x, a = odds_tuple
    cond = (df.get('home_odds').notna()) & (df.get('draw_odds').notna()) & (df.get('away_odds').notna())
    cond = cond & (df['home_odds'].sub(h).abs() <= tol) & (df['draw_odds'].sub(x).abs() <= tol) & (df['away_odds'].sub(a).abs() <= tol)
    if league:
        cond = cond & (df['league'].astype(str).str.lower() == str(league).lower())
    return df[cond]


def find_similar_odds_from_df(df: pd.DataFrame, target: Dict[str, Any], top_k: int = 20, weights: Optional[Dict[str, float]] = None, cutoff=None) -> List[Dict[str, Any]]:
    from .similarity import top_matches
    # prepare candidates list
    candidates = []
    # normalize timestamp column if present
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception:
            pass
    # apply cutoff to prevent leakage
    if cutoff is not None and 'timestamp' in df.columns:
        try:
            cutoff_ts = pd.to_datetime(cutoff)
            df = df[df['timestamp'] < cutoff_ts]
        except Exception:
            pass
    for _, row in df.iterrows():
        # construct rec using possible column names
        rec = {
            'home_odds': row.get('home_odds') if 'home_odds' in row.index else (row.get('odds') if row.get('selection') in ('Home','1','home') else None),
            'draw_odds': row.get('draw_odds') if 'draw_odds' in row.index else (row.get('odds') if row.get('selection') in ('Draw','X','draw') else None),
            'away_odds': row.get('away_odds') if 'away_odds' in row.index else (row.get('odds') if row.get('selection') in ('Away','2','away') else None),
            'handicap': row.get('handicap') if 'handicap' in row.index else row.get('line') if 'line' in row.index else None,
            'bookmaker': row.get('bookmaker') if 'bookmaker' in row.index else None,
            'timestamp': _ensure_timestamp(row.get('timestamp')) if 'timestamp' in row.index else None,
            'league': row.get('league') if 'league' in row.index else None,
            'meta': row.to_dict(),
        }
        candidates.append(rec)
    # normalize target timestamp
    if 'timestamp' in target:
        target = target.copy()
        target['timestamp'] = _ensure_timestamp(target.get('timestamp'))
    return top_matches(target, candidates, top_k=top_k, weights=weights)
