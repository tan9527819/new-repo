"""
历史同赔搜索：在历史 CSV 中查找相同或接近的赔率记录。
"""
from typing import Tuple, Optional, List, Dict, Any
import os
import pandas as pd
from .odds_normalizer import to_feature_vector


def find_same_odds_from_df(df: pd.DataFrame, odds_tuple: Tuple[float, float, float], tol: float = 1e-6, league: Optional[str] = None) -> pd.DataFrame:
    h, x, a = odds_tuple
    cond = (df['home_odds'].notna()) & (df['draw_odds'].notna()) & (df['away_odds'].notna())
    cond = cond & (df['home_odds'].sub(h).abs() <= tol) & (df['draw_odds'].sub(x).abs() <= tol) & (df['away_odds'].sub(a).abs() <= tol)
    if league:
        cond = cond & (df['league'].astype(str).str.lower() == str(league).lower())
    return df[cond]


def find_similar_odds_from_df(df: pd.DataFrame, target: Dict[str, Any], top_k: int = 20, weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    from .similarity import top_matches
    # prepare candidates list
    candidates = []
    for _, row in df.iterrows():
        rec = {
            'home_odds': row.get('home_odds'),
            'draw_odds': row.get('draw_odds'),
            'away_odds': row.get('away_odds'),
            'handicap': row.get('handicap'),
            'bookmaker': row.get('bookmaker') if 'bookmaker' in row.index else None,
            'timestamp': row.get('timestamp') if 'timestamp' in row.index else None,
            'league': row.get('league') if 'league' in row.index else None,
            'meta': row.to_dict(),
        }
        # normalize timestamp if string
        from .odds_normalizer import normalize_timestamp
        candidates.append(rec)
    # normalize target
    t = target.copy()
    return top_matches(t, candidates, top_k=top_k, weights=weights)
