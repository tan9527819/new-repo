"""
赔率标准化：把不同 bookmaker / market 的表示统一为数值特征。
"""
from typing import Dict, Any, Tuple, Optional
import datetime

import numpy as np


def normalize_timestamp(value: Optional[str]) -> Optional[datetime.datetime]:
    if value is None:
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        try:
            return datetime.datetime.fromtimestamp(float(value))
        except Exception:
            return None


def normalize_bookmaker(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None
    n = name.strip().lower()
    # simple normalization map, extendable
    aliases = {
        'pinnacle': 'pinnacle',
        'bet365': 'bet365',
        'bet365.com': 'bet365',
        'betfair': 'betfair',
    }
    for k, v in aliases.items():
        if k in n:
            return v
    return n


def normalize_1x2(odds_tuple: Tuple[Any, Any, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Convert raw 1X2 odds (may be strings) to floats and validate positive.
    Returns (home, draw, away) or (None, None, None) on failure for each.
    """
    out = []
    for v in odds_tuple:
        try:
            if v is None:
                out.append(None)
            else:
                fv = float(v)
                if fv <= 0:
                    out.append(None)
                else:
                    out.append(round(fv, 3))
        except Exception:
            out.append(None)
    return tuple(out)  # type: ignore


def normalize_handicap(handicap_raw: Optional[Any]) -> Optional[float]:
    if handicap_raw is None:
        return None
    try:
        return float(handicap_raw)
    except Exception:
        # sometimes handicap like "+0.25" or "1/4"; try replacement
        try:
            s = str(handicap_raw).replace('\u00bc', '0.25').replace('½', '.5').replace('¼', '.25')
            return float(s)
        except Exception:
            return None


def to_feature_vector(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a raw odds record (dict) to a standardized numeric feature dict.
    Expected keys (case-insensitive): 'home_odds','draw_odds','away_odds','handicap','bookmaker','timestamp','league'
    """
    h, x, a = normalize_1x2((record.get('home_odds'), record.get('draw_odds'), record.get('away_odds')))
    hand = normalize_handicap(record.get('handicap'))
    bm = normalize_bookmaker(record.get('bookmaker'))
    ts = normalize_timestamp(record.get('timestamp'))
    league = record.get('league')
    # feature vector
    vec = {
        'home_odds': h,
        'draw_odds': x,
        'away_odds': a,
        'handicap': hand,
        'bookmaker': bm,
        'timestamp': ts,
        'league': league,
    }
    return vec
