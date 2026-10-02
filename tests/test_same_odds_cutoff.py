"""
same_odds test additions to cover cutoff and timestamp normalization.
"""
# Adding tests for cutoff behavior
import pandas as pd
from football_analysis.analysis.same_odds import find_same_odds_from_df
from datetime import datetime


def test_same_odds_cutoff():
    df = pd.DataFrame({
        'home_odds':[1.9,1.9],
        'draw_odds':[3.4,3.4],
        'away_odds':[4.2,4.2],
        'timestamp':['2026-01-01T00:00:00','2026-02-01T00:00:00'],
        'league':['L','L']
    })
    res_all = find_same_odds_from_df(df, (1.9,3.4,4.2))
    assert len(res_all) == 2
    res_cut = find_same_odds_from_df(df, (1.9,3.4,4.2), cutoff='2026-01-15')
    assert len(res_cut) == 1
