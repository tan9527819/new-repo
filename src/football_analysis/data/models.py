"""
数据标准化模型：MatchRecord
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MatchRecord:
    match_id: Optional[str]
    date: Optional[datetime]
    league: Optional[str]
    home_team: Optional[str]
    away_team: Optional[str]
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
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_odds': self.home_odds,
            'draw_odds': self.draw_odds,
            'away_odds': self.away_odds,
            'handicap': self.handicap,
            'handicap_home_odds': self.handicap_home_odds,
            'handicap_away_odds': self.handicap_away_odds,
            'source': self.source,
        }
