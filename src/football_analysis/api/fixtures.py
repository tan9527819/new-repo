"""
增强的 fixtures 客户端实现，包含真实解析与分页支持。
"""
from typing import Optional, List, Dict, Any
from .client import APIFootballClient, APIError
from ..data.models import MatchRecord
import logging

logger = logging.getLogger(__name__)


class FixturesClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def _parse_fixture_item(self, item: Dict[str, Any]) -> MatchRecord:
        # item expected to follow API-Football v3 structure
        fixture = item.get('fixture', {})
        league = item.get('league', {})
        teams = item.get('teams', {})

        match_id = fixture.get('id')
        date = fixture.get('date')
        # API returns ISO date string; keep string or convert later in standardizer
        season = league.get('season')
        league_name = league.get('name')
        status = fixture.get('status', {}).get('short') or fixture.get('status', {}).get('long')

        home = teams.get('home', {})
        away = teams.get('away', {})

        rec = MatchRecord(
            match_id=str(match_id) if match_id is not None else None,
            date=date,
            league=league_name,
            season=season,
            home_team=home.get('name'),
            away_team=away.get('name'),
            status=status,
            home_odds=None,
            draw_odds=None,
            away_odds=None,
            handicap=None,
            handicap_home_odds=None,
            handicap_away_odds=None,
            source='api-football-fixtures',
        )
        return rec

    def get_fixtures(self, date_from: Optional[str] = None, date_to: Optional[str] = None, league: Optional[int] = None, season: Optional[int] = None, page: int = 1, per_page: int = 100) -> List[MatchRecord]:
        params = {'page': page}
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        if league:
            params['league'] = league
        if season:
            params['season'] = season

        try:
            resp = self.client.get('/fixtures', params=params)
        except APIError as e:
            logger.error('API error when fetching fixtures: %s', e)
            raise

        if not isinstance(resp, dict) or 'response' not in resp:
            raise APIError('Unexpected fixtures response format')

        items = resp.get('response') or []
        results = []
        for it in items:
            try:
                results.append(self._parse_fixture_item(it))
            except Exception as ex:
                logger.warning('Failed to parse fixture item: %s', ex)
        return results

    def iter_fixtures(self, date_from: Optional[str] = None, date_to: Optional[str] = None, league: Optional[int] = None, season: Optional[int] = None, per_page: int = 100):
        """Generator that pages through results until empty page returned.
        """
        page = 1
        while True:
            results = self.get_fixtures(date_from=date_from, date_to=date_to, league=league, season=season, page=page, per_page=per_page)
            if not results:
                break
            for r in results:
                yield r
            page += 1
