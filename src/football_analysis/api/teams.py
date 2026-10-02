"""
teams 资源封装（占位）。
"""
from .client import APIFootballClient
from typing import Optional


class TeamsClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def get_team(self, team_id: int):
        return self.client.get(f'/teams?id={team_id}')
