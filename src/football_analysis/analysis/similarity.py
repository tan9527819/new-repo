"""
相似度计算模块。可配置权重，不硬编码。

计算可解释的 similarity_score，基于多个部分。
"""
from typing import Dict, Any, List, Tuple
import math
import numpy as np

DEFAULT_WEIGHTS = {
    'odds': 0.5,
    'handicap': 0.2,
    'bookmaker': 0.1,
    'time': 0.1,
    'league': 0.1,
}


def _odds_distance(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    # Euclidean distance on available 1x2 odds
    keys = ['home_odds', 'draw_odds', 'away_odds']
    vals_a = []
    vals_b = []
    for k in keys:
        va = a.get(k)
        vb = b.get(k)
        if va is None or vb is None:
            # penalize missing data by a fixed large value
            return float('inf')
        vals_a.append(float(va))
        vals_b.append(float(vb))
    return float(np.linalg.norm(np.array(vals_a) - np.array(vals_b)))


def _handicap_distance(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    ha = a.get('handicap')
    hb = b.get('handicap')
    if ha is None or hb is None:
        return float('inf')
    return abs(float(ha) - float(hb))


def _bookmaker_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    return 1.0 if (a.get('bookmaker') and b.get('bookmaker') and a.get('bookmaker') == b.get('bookmaker')) else 0.0


def _time_similarity(a: Dict[str, Any], b: Dict[str, Any], window_hours: float = 24.0) -> float:
    ta = a.get('timestamp')
    tb = b.get('timestamp')
    if ta is None or tb is None:
        return 0.0
    diff = abs((ta - tb).total_seconds()) / 3600.0
    return max(0.0, 1.0 - (diff / window_hours))


def _league_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    la = a.get('league')
    lb = b.get('league')
    if la is None or lb is None:
        return 0.0
    return 1.0 if str(la).lower() == str(lb).lower() else 0.0


def similarity_score(target: Dict[str, Any], candidate: Dict[str, Any], weights: Dict[str, float] = None, time_window_hours: float = 24.0) -> Dict[str, Any]:
    w = DEFAULT_WEIGHTS.copy()
    if weights:
        w.update(weights)
    # compute components
    odds_dist = _odds_distance(target, candidate)
    handicap_dist = _handicap_distance(target, candidate)
    bm_sim = _bookmaker_similarity(target, candidate)
    time_sim = _time_similarity(target, candidate, window_hours=time_window_hours)
    league_sim = _league_similarity(target, candidate)

    # transform distances to similarity in [0,1] by simple function
    # odds similarity: exp(-alpha * dist)
    odds_sim = 0.0
    if math.isfinite(odds_dist):
        odds_sim = math.exp(-0.5 * odds_dist)
    handicap_sim = 0.0
    if math.isfinite(handicap_dist):
        handicap_sim = math.exp(-1.0 * handicap_dist)

    # combine weighted
    total_weight = sum(w.values())
    score = (
        w['odds'] * odds_sim +
        w['handicap'] * handicap_sim +
        w['bookmaker'] * bm_sim +
        w['time'] * time_sim +
        w['league'] * league_sim
    ) / (total_weight if total_weight > 0 else 1.0)

    return {
        'score': float(score),
        'components': {
            'odds_sim': odds_sim,
            'handicap_sim': handicap_sim,
            'bookmaker_sim': bm_sim,
            'time_sim': time_sim,
            'league_sim': league_sim,
        }
    }


def top_matches(target: Dict[str, Any], candidates: List[Dict[str, Any]], top_k: int = 10, weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
    scored = []
    for c in candidates:
        s = similarity_score(target, c, weights)
        entry = c.copy()
        entry['_similarity'] = s
        scored.append(entry)
    scored.sort(key=lambda x: x['_similarity']['score'], reverse=True)
    return scored[:top_k]
