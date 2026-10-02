"""
API-Football 基础客户端与资源封装。

注意：API_KEY 必须从环境变量 API_FOOTBALL_KEY 读取。
"""

from .client import APIFootballClient
from .fixtures import FixturesClient
from .teams import TeamsClient
from .leagues import LeaguesClient
from .odds import OddsClient

__all__ = [
    'APIFootballClient',
    'FixturesClient',
    'TeamsClient',
    'LeaguesClient',
    'OddsClient',
]
