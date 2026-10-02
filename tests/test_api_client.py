# tests for API client
import os
import json
import pytest
from football_analysis.api.client import APIFootballClient, APIError

class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._json


def test_client_requires_key(monkeypatch):
    monkeypatch.delenv('API_FOOTBALL_KEY', raising=False)
    with pytest.raises(RuntimeError):
        APIFootballClient()


def test_client_get_calls(monkeypatch):
    monkeypatch.setenv('API_FOOTBALL_KEY', 'testkey')
    monkeypatch.setenv('API_FOOTBALL_BASE_URL', 'https://api.test')
    client = APIFootballClient()

    def fake_request(method, url, params=None, json=None, timeout=None):
        assert method == 'GET'
        assert 'fixtures' in url or 'odds' in url or 'teams' in url or 'leagues' in url
        return DummyResponse(200, json_data={'response': []})

    monkeypatch.setattr(client.session, 'request', fake_request)
    res = client.get('/fixtures')
    assert isinstance(res, dict)
    assert 'response' in res
