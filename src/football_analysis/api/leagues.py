"""
leagues 资源封装（占位）。
"""
from .client import APIFootballClient
from typing import Optional


class LeaguesClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def list_leagues(self, country: Optional[str] = None):
        params = {}
        if country:
            params['country'] = country
        return self.client.get('/leagues', params=params)
