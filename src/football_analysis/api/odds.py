"""
odds 资源封装（占位）。
"""
from typing import Optional
from .client import APIFootballClient


class OddsClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def get_odds(self, fixture_id: Optional[int] = None, bookmaker: Optional[int] = None):
        params = {}
        if fixture_id:
            params['fixture'] = fixture_id
        if bookmaker:
            params['bookmaker'] = bookmaker
        return self.client.get('/odds', params=params)
