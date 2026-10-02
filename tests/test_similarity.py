# tests for similarity and normalizer
from football_analysis.analysis.odds_normalizer import to_feature_vector, normalize_1x2, normalize_handicap
from football_analysis.analysis.similarity import similarity_score, top_matches
import datetime


def test_normalizer_basic():
    rec = {'home_odds': '1.90', 'draw_odds': '3.40', 'away_odds': '4.20', 'handicap': '0', 'bookmaker': 'Bet365', 'timestamp': '2026-10-02T12:00:00Z', 'league': 'Premier'}
    v = to_feature_vector(rec)
    assert v['home_odds'] == 1.9
    assert v['bookmaker'] == 'bet365'
    assert isinstance(v['timestamp'], datetime.datetime)


def test_similarity_score():
    t = {'home_odds':1.9,'draw_odds':3.4,'away_odds':4.2,'handicap':0.0,'bookmaker':'bet365','timestamp':datetime.datetime(2026,10,2,12,0),'league':'premier'}
    c = {'home_odds':1.95,'draw_odds':3.5,'away_odds':4.1,'handicap':0.0,'bookmaker':'bet365','timestamp':datetime.datetime(2026,10,2,10,0),'league':'premier'}
    s = similarity_score(t, c)
    assert 0.0 <= s['score'] <= 1.0
    top = top_matches(t, [c], top_k=1)
    assert len(top) == 1
