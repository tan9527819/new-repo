# tests for odds movement and movement similarity
from football_analysis.analysis.odds_movement import compute_basic_movement
from football_analysis.analysis.movement_similarity import movement_similarity


def test_compute_basic_movement():
    initial = {'home_odds':2.1,'draw_odds':3.3,'away_odds':3.2,'handicap':0.0}
    current = {'home_odds':1.9,'draw_odds':3.45,'away_odds':3.7,'handicap':0.25}
    m = compute_basic_movement(initial, current)
    assert 'home_odds_change' in m
    assert m['movement_type'] == 'home_strengthening'


def test_movement_similarity_insufficient():
    initial = {'home_odds':2.1,'draw_odds':3.3,'away_odds':3.2,'handicap':0.0}
    current = {'home_odds':1.9,'draw_odds':3.45,'away_odds':3.7,'handicap':0.25}
    historical = [
        {'initial': initial, 'current': current, 'result': 'home'}
    ]
    res = movement_similarity(initial, current, historical, top_k=1)
    assert res['sample_size'] == 1
    assert res['conclusion'] in ('evidence_present','evidence_insufficient')
