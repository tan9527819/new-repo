"""
赔率变盘分析：计算初盘/中盘/即时盘之间的变化量和类型。
"""
from typing import Dict, Any, Optional
import numpy as np


def compute_basic_movement(initial: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    # expects dicts with keys: home_odds, draw_odds, away_odds, handicap
    def _safe_float(d, k):
        v = d.get(k)
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    ih = _safe_float(initial, 'home_odds')
    ix = _safe_float(initial, 'draw_odds')
    ia = _safe_float(initial, 'away_odds')
    ch = _safe_float(current, 'home_odds')
    cx = _safe_float(current, 'draw_odds')
    ca = _safe_float(current, 'away_odds')

    result = {}
    if ih is not None and ch is not None:
        result['home_odds_change'] = round(ch - ih, 3)
    else:
        result['home_odds_change'] = None
    if ix is not None and cx is not None:
        result['draw_odds_change'] = round(cx - ix, 3)
    else:
        result['draw_odds_change'] = None
    if ia is not None and ca is not None:
        result['away_odds_change'] = round(ca - ia, 3)
    else:
        result['away_odds_change'] = None

    # handicap change
    ihc = _safe_float(initial, 'handicap')
    chc = _safe_float(current, 'handicap')
    if ihc is not None and chc is not None:
        result['handicap_change'] = round(chc - ihc, 3)
    else:
        result['handicap_change'] = None

    # movement type simple heuristic
    # if home odds decreased significantly -> home_strengthening
    if result['home_odds_change'] is not None and result['home_odds_change'] < -0.05:
        movement = 'home_strengthening'
    elif result['away_odds_change'] is not None and result['away_odds_change'] < -0.05:
        movement = 'away_strengthening'
    else:
        movement = 'neutral'
    result['movement_type'] = movement

    # confidence: based on magnitude of change
    changes = [c for c in [result['home_odds_change'], result['draw_odds_change'], result['away_odds_change']] if c is not None]
    if changes:
        mag = float(np.mean([abs(c) for c in changes]))
        conf = min(1.0, mag / 0.5)
        result['confidence'] = round(conf, 2)
    else:
        result['confidence'] = 0.0

    return result
