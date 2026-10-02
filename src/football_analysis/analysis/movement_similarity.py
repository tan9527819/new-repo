"""
基于赔率变盘的相似性匹配：匹配“初盘->当前盘”变化模式到历史变化样本。
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from .odds_movement import compute_basic_movement

MIN_SAMPLE_SIZE = int(__import__('os').getenv('MIN_SAMPLE_SIZE', '5'))


def movement_similarity(initial: Dict[str, Any], current: Dict[str, Any], historical_changes: List[Dict[str, Any]], top_k: int = 20) -> Dict[str, Any]:
    """
    historical_changes: list of dicts each with keys 'initial' and 'current' (both dicts with home/draw/away/handicap) and 'result' (match outcome)
    Returns top matches and aggregated statistics
    """
    target_change = compute_basic_movement(initial, current)
    # compute distance between changes
    rows = []
    for h in historical_changes:
        try:
            ch = compute_basic_movement(h['initial'], h['current'])
            # vectorize: home_change, draw_change, away_change, handicap_change
            vec_t = np.array([x if x is not None else 0.0 for x in [target_change['home_odds_change'], target_change['draw_odds_change'], target_change['away_odds_change'], target_change['handicap_change']]])
            vec_h = np.array([x if x is not None else 0.0 for x in [ch['home_odds_change'], ch['draw_odds_change'], ch['away_odds_change'], ch['handicap_change']]])
            dist = float(np.linalg.norm(vec_t - vec_h))
            rows.append({'hist': h, 'dist': dist, 'change': ch})
        except Exception:
            continue
    if not rows:
        return {'sample_size': 0, 'top_matches': [], 'aggregates': {}, 'conclusion': 'evidence_insufficient'}
    df = pd.DataFrame(rows).sort_values('dist')
    top = df.head(top_k).to_dict(orient='records')
    sample_size = len(df)
    # aggregate outcomes
    outcomes = [t['hist'].get('result') for t in top if 'result' in t['hist']]
    # compute stats
    stats = {}
    if outcomes:
        total = len(outcomes)
        home_wins = sum(1 for o in outcomes if o == 'home')
        draws = sum(1 for o in outcomes if o == 'draw')
        away_wins = sum(1 for o in outcomes if o == 'away')
        stats['home_win_pct'] = home_wins / total
        stats['draw_pct'] = draws / total
        stats['away_win_pct'] = away_wins / total
        stats['sample_size'] = total
    else:
        stats['sample_size'] = 0
    conclusion = 'evidence_insufficient'
    if stats.get('sample_size', 0) >= MIN_SAMPLE_SIZE:
        conclusion = 'evidence_present'
    return {'sample_size': sample_size, 'top_matches': top, 'aggregates': stats, 'conclusion': conclusion}
