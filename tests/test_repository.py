# tests for repository
import pandas as pd
from pathlib import Path
from football_analysis.data.repository import load_matches, find_similar_matches, find_same_odds, get_recent_results


def create_sample_csv(tmp_path):
    data = pd.DataFrame({
        'match_date': ['2026-01-01', '2026-01-02', '2026-01-03'],
        'home': ['A', 'B', 'C'],
        'away': ['X', 'Y', 'Z'],
        '1': [1.5, 2.0, 1.6],
        'X': [3.2, 3.0, 3.3],
        '2': [6.0, 4.0, 5.8],
    })
    p = tmp_path / 'hist.csv'
    data.to_csv(p, index=False)
    return str(p)


def test_load_and_queries(tmp_path, monkeypatch):
    path = create_sample_csv(tmp_path)
    # set env path
    monkeypatch.setenv('HISTORICAL_DATA_PATH', path)
    recs = load_matches(n=2)
    assert len(recs) == 2

    sims = find_similar_matches((1.5,3.2,6.0), top_k=2)
    assert len(sims) <= 2

    same = find_same_odds((1.5,3.2,6.0))
    assert not same.empty

    recent = get_recent_results()
    assert not recent.empty
