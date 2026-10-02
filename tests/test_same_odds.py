# tests for same_odds
import pandas as pd
from football_analysis.analysis.same_odds import find_same_odds_from_df, find_similar_odds_from_df
from datetime import datetime


def test_same_odds_exact():
    df = pd.DataFrame({
        'home_odds':[1.9,2.0],
        'draw_odds':[3.4,3.1],
        'away_odds':[4.2,3.5],
        'league':['L','L'],
        'timestamp':['2026-01-01T00:00:00','2026-01-02T00:00:00']
    })
    res = find_same_odds_from_df(df, (1.9,3.4,4.2))
    assert len(res) == 1


def test_find_similar_odds():
    df = pd.DataFrame({
        'home_odds':[1.9,2.5,1.95],
        'draw_odds':[3.4,3.0,3.5],
        'away_odds':[4.2,2.8,4.0],
        'handicap':[0.0,0.0,0.0],
        'bookmaker':['bet365','other','bet365'],
        'league':['L','L','L'],
        'timestamp':['2026-01-01T00:00:00','2026-01-02T00:00:00','2026-01-03T00:00:00']
    })
    target = {'home_odds':1.9,'draw_odds':3.4,'away_odds':4.2,'handicap':0.0,'bookmaker':'bet365','timestamp':datetime(2026,1,1,0,0),'league':'L'}
    res = find_similar_odds_from_df(df, target, top_k=2)
    assert len(res) == 2
