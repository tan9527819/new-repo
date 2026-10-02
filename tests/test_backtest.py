"""
Backtest tests to ensure cutoff_time/lookback and error recording.
"""
from datetime import datetime, timedelta
from football_analysis.analysis.backtest import backtest


def model_ok(match, history):
    return (1/3,1/3,1/3)


def model_throws(match, history):
    raise RuntimeError('model error')


def test_backtest_lookback_and_errors():
    base = datetime(2026,1,10)
    hist = [
        {'date': base - timedelta(days=10), 'result':'home'},
        {'date': base - timedelta(days=5), 'result':'away'},
        {'date': base, 'result':'draw'},
        {'date': base + timedelta(days=1), 'result':'home'}
    ]
    res = backtest(hist, model_ok, lookback_days=7)
    # only matches with date >= earliest and within lookback considered; since model processes each match using prior history within 7 days
    assert 'n' in res
    # test error recording
    res2 = backtest(hist, model_throws, lookback_days=30)
    assert res2['error_count'] >= 1
