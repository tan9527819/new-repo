# tests for fixtures and odds parsing using mocked API
import pytest
from football_analysis.api.client import APIFootballClient
from football_analysis.api.fixtures import FixturesClient
from football_analysis.api.odds import OddsClient

class DummyClient:
    def __init__(self, resp):
        self._resp = resp
    def get(self, path, params=None):
        return self._resp


def test_fixtures_parsing():
    sample = {
        'response': [
            {
                'fixture': {'id': 1001, 'date': '2026-10-02T15:00:00+00:00', 'status': {'short': 'NS'}},
                'league': {'id': 200, 'name': 'Test League', 'season': 2026},
                'teams': {'home': {'id': 10, 'name': 'Home FC'}, 'away': {'id': 20, 'name': 'Away FC'}}
            }
        ]
    }
    client = DummyClient(sample)
    fc = FixturesClient(client)
    res = fc.get_fixtures(date_from='2026-10-02')
    assert len(res) == 1
    m = res[0]
    assert m.home_team == 'Home FC'
    assert m.away_team == 'Away FC'
    assert m.league == 'Test League'
    assert m.match_id == '1001'


def test_odds_parsing():
    sample = {
        'response': [
            {
                'bookmakers': [
                    {
                        'id': 5,
                        'name': 'BestBook',
                        'bets': [
                            {'id': 1, 'name': 'Match Winner', 'values': [
                                {'value': 'Home', 'odd': '1.90'},
                                {'value': 'Draw', 'odd': '3.50'},
                                {'value': 'Away', 'odd': '4.20'}
                            ]},
                            {'id': 2, 'name': 'Asian Handicap', 'values': [
                                {'value': '0', 'odd': None, 'handicap': '0', 'odd_home': '2.00', 'odd_away': '1.90'},
                            ]}
                        ]
                    }
                ]
            }
        ]
    }
    client = DummyClient(sample)
    oc = OddsClient(client)
    res = oc.get_odds(12345)
    # should produce multiple OddsRecord objects
    assert any(r.bookmaker == 'BestBook' for r in res)
    # at least 3 for 1X2
    assert sum(1 for r in res if r.market == 'Match Winner') == 3
