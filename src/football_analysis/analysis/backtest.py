"""
回测接口：使用历史数据测试相似性+变盘匹配的表现。

注意：此模块不访问网络，基于传入的历史数据进行回测。
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss


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
    # compute average brier across classes (approx)
    bs = np.mean([brier_score_loss([1 if y==c else 0 for y in y_true], [p[c] for p in ps]) for c in range(3)])
    # log loss
    try:
        ll = log_loss(y_true, ps, labels=[0,1,2])
    except Exception:
        ll = None
    return {'accuracy': acc, 'brier_score': float(bs), 'log_loss': float(ll) if ll is not None else None}


def backtest(historical_matches: List[Dict[str, Any]], model_func, lookback_days: int = 365) -> Dict[str, Any]:
    """
    historical_matches: list of dict containing at least 'date', 'initial_odds', 'current_odds', 'result'
    model_func: function(match, history)->pred_prob (p_home,p_draw,p_away)
    """
    preds = []
    truths = []
    for match in historical_matches:
        # build history up to (but not including) match['date']
        hist = [h for h in historical_matches if h['date'] < match['date']]
        try:
            p = model_func(match, hist)
            if p is None:
                continue
            preds.append(p)
            truths.append(match.get('result'))
        except Exception:
            continue
    if not preds:
        return {'n': 0}
    evals = evaluate_predictions(preds, truths)
    evals['n'] = len(preds)
    return evals
