"""
Tests for models, repository and schema updates.
"""
from datetime import datetime
import pandas as pd
from football_analysis.data.models import MatchRecord
from football_analysis.data.schema import map_columns
from football_analysis.data.repository import _df_to_matchrecord


def test_matchrecord_season_status():
    r = pd.Series({'match_id': '123', 'date': datetime(2026,1,1), 'league': 'L', 'season': 2026, 'home_team': 'H', 'away_team': 'A', 'status': 'NS'})
    m = _df_to_matchrecord(r)
    assert m.match_id == '123'
    assert m.season == 2026
    assert m.status == 'NS'


def test_schema_map_odds_fields():
    df = pd.DataFrame({'odds_home':[1.9], 'odds_draw':[3.4], 'odds_away':[4.2], 'match_date':['2026-01-01']})
    out = map_columns(df)
    assert 'home_odds' in out.columns
    assert 'odds_home' not in out.columns

