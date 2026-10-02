"""
Backtest improvements: enforce cutoff_time and lookback_days, and record errors instead of silently continuing.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss
from datetime import datetime, timedelta


def evaluate_predictions(pred_probs: List[Tuple[float, float, float]], truths: List[str]) -> Dict[str, Any]:
    # pred_probs: list of (p_home, p_draw, p_away)
    # truths: 'home'/'draw'/'away'
    y_true = []
    ps = []
    for p, t in zip(pred_probs, truths):
        if t == 'home':
            y_true.append(0)
        elif t == 'draw':
            y_true.append(1)
        else:
            y_true.append(2)
        ps.append(p)
    # compute accuracy
    preds = [np.argmax(p) for p in ps]
    acc = sum(1 for i, p in enumerate(preds) if p == y_true[i]) / len(y_true)
    # brier: compute for multi-class by flattening one-vs-all for true class probabilities
    bs = np.mean([brier_score_loss([1 if y==c else 0 for y in y_true], [p[c] for p in ps]) for c in range(3)])
    # log loss
    try:
        ll = log_loss(y_true, ps, labels=[0,1,2])
    except Exception:
        ll = None
    return {'accuracy': acc, 'brier_score': float(bs), 'log_loss': float(ll) if ll is not None else None}


def backtest(historical_matches: List[Dict[str, Any]], model_func, lookback_days: int = 365) -> Dict[str, Any]:
    """
    historical_matches: list of dict containing at least 'date'(datetime) , 'initial_odds', 'current_odds', 'result'
    model_func: function(match, history)->pred_prob (p_home,p_draw,p_away)
    """
    # sort by date ascending
    sorted_matches = sorted(historical_matches, key=lambda m: m.get('date'))
    preds = []
    truths = []
    errors = []
    skipped = 0
    lookback_delta = timedelta(days=lookback_days)
    for match in sorted_matches:
        match_date = match.get('date')
        if match_date is None:
            errors.append({'match': match, 'reason': 'missing_date'})
            continue
        if isinstance(match_date, str):
            try:
                match_date = datetime.fromisoformat(match_date)
            except Exception as e:
                errors.append({'match': match, 'reason': f'invalid_date:{e}'})
                continue
        # build history up to (but not including) match_date and within lookback
        hist = [h for h in sorted_matches if h.get('date') and h.get('date') < match_date and (match_date - h.get('date')) <= lookback_delta]
        try:
            p = model_func(match, hist)
            if p is None:
                skipped += 1
                continue
            preds.append(p)
            truths.append(match.get('result'))
        except Exception as e:
            errors.append({'match': match, 'reason': str(e)})
    result = {'n': len(preds), 'skipped': skipped, 'error_count': len(errors), 'errors': errors}
    if preds:
        evals = evaluate_predictions(preds, truths)
        result.update(evals)
    return result
