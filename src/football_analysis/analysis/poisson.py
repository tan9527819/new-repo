"""
泊松模型与校准相关函数占位。
用途：
- 使用历史进球数据估计到主队/客队的期望进球数
- 校准泊松模型输出使其更符合观察到的进球分布
"""

import numpy as np


def poisson_pmf(k, lamb):
    from math import exp, factorial
    return (lamb**k) * exp(-lamb) / factorial(k)


def estimate_lambda(home_goals: np.ndarray, away_goals: np.ndarray):
    """基于历史比赛估计进球期望（示例）。"""
    return np.mean(home_goals), np.mean(away_goals)


def calibrate_poisson(pred_probs, observed_counts):
    """校准方法占位（比如使用 isotonic regression / Platt scaling 等）。"""
    raise NotImplementedError
