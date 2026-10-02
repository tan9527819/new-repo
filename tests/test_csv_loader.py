# tests for csv loader
import pandas as pd
import tempfile
import os
from football_analysis.data.csv_loader import read_and_clean_csv, infer_columns, CSVLoadError


def test_read_and_clean_csv(tmp_path):
    data = pd.DataFrame({
        'match_date': ['2026-01-01 15:00', 'invalid_date'],
        'home': ['Team A', 'Team B'],
        'away': ['Team C', 'Team D'],
        '1': [1.5, 'NaN'],
        'X': [3.2, 3.0],
        '2': [6.0, 2.5],
    })
    p = tmp_path / 'test_odds.csv'
    data.to_csv(p, index=False)

    df = read_and_clean_csv(str(p))
    assert 'date' in df.columns
    assert 'home_team' in df.columns
    assert 'home_odds' in df.columns
    # second row has NaN home_odds
    assert df['home_odds'].isna().sum() >= 1

    # infer_columns returns subset
    sub = infer_columns(str(p))
    assert list(sub.columns) == ['date', 'home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds', 'handicap', 'handicap_home_odds', 'handicap_away_odds', 'source']

    # missing required columns should raise
    p2 = tmp_path / 'bad.csv'
    pd.DataFrame({'a':[1]}).to_csv(p2, index=False)
    try:
        read_and_clean_csv(str(p2))
        raised = False
    except CSVLoadError:
        raised = True
    assert raised
