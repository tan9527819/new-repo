"""
Failure analysis utilities to find where models fail.
"""
from typing import List, Dict, Any
from collections import defaultdict


def analyze_failures(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    # records: list with fields 'initial_odds','current_odds','result','league','bookmaker','handicap'
    stats = defaultdict(lambda: {'n':0,'correct':0})
    for r in records:
        key = (r.get('league'), r.get('bookmaker'))
        stats[key]['n'] += 1
        if r.get('predicted') == r.get('result'):
            stats[key]['correct'] += 1
    out = {}
    for k,v in stats.items():
        league, bookmaker = k
        out[f'{league}::{bookmaker}'] = {'n': v['n'], 'accuracy': v['correct']/v['n'] if v['n']>0 else None}
    return out
