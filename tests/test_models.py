# tests for models
from datetime import datetime
from football_analysis.data.models import MatchRecord


def test_matchrecord_to_dict():
    m = MatchRecord(match_id='1', date=datetime(2026,1,1), league='A', home_team='H', away_team='A', home_odds=1.5, draw_odds=3.2, away_odds=6.0, handicap=0.0, handicap_home_odds=None, handicap_away_odds=None, source='csv')
    d = m.to_dict()
    assert d['home_team'] == 'H'
    assert d['home_odds'] == 1.5
