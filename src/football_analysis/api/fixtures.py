"""
fixtures 资源的封装（占位）。
"""
from typing import Dict, Any, Optional
from .client import APIFootballClient


class FixturesClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def get_fixtures(self, date_from: Optional[str] = None, date_to: Optional[str] = None, league: Optional[int] = None):
        params = {}
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        if league:
            params['league'] = league
        return self.client.get('/fixtures', params=params)
