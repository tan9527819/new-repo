# tests for backtest (using trivial model)
from football_analysis.analysis.backtest import backtest


def simple_model(match, history):
    # naive model: predict uniform probabilities
    return (1/3,1/3,1/3)


def test_backtest_empty():
    hist = []
    res = backtest(hist, simple_model)
    assert res.get('n',0) == 0


def test_backtest_basic():
    hist = [
        {'date': '2026-01-01', 'initial_odds': None, 'current_odds': None, 'result': 'home'},
        {'date': '2026-02-01', 'initial_odds': None, 'current_odds': None, 'result': 'away'},
    ]
    res = backtest(hist, simple_model)
    # model will process matches; since dates are strings, comparison may skip; ensure it handles gracefully
    assert 'n' in res
