"""
扩展数据模型，加入 OddsRecord，并完善 MatchRecord 字段。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass
class MatchRecord:
    match_id: Optional[str]
    date: Optional[Any]
    league: Optional[str]
    season: Optional[Any]
    home_team: Optional[str]
    away_team: Optional[str]
    status: Optional[str]
    home_odds: Optional[float]
    draw_odds: Optional[float]
    away_odds: Optional[float]
    handicap: Optional[float]
    handicap_home_odds: Optional[float]
    handicap_away_odds: Optional[float]
    source: Optional[str]

    def to_dict(self):
        return {
            'match_id': self.match_id,
            'date': self.date,
            'league': self.league,
            'season': self.season,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'status': self.status,
            'home_odds': self.home_odds,
            'draw_odds': self.draw_odds,
            'away_odds': self.away_odds,
            'handicap': self.handicap,
            'handicap_home_odds': self.handicap_home_odds,
            'handicap_away_odds': self.handicap_away_odds,
            'source': self.source,
        }


@dataclass
class OddsRecord:
    fixture_id: Optional[str]
    bookmaker: Optional[str]
    market: Optional[str]
    selection: Optional[str]
    line: Optional[Any]
    odds: Optional[float]
    timestamp: Optional[Any]
    raw: Optional[Any]

    def to_dict(self):
        return {
            'fixture_id': self.fixture_id,
            'bookmaker': self.bookmaker,
            'market': self.market,
            'selection': self.selection,
            'line': self.line,
            'odds': self.odds,
            'timestamp': self.timestamp,
            'raw': self.raw,
        }
