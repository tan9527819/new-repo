"""
Odds resource parsing for API-Football v3.

功能：
- 根据 fixture_id 获取赔率数据
- 解析 bookmakers、1X2、亚洲/让球盘口
- 保留原始 bookmaker 信息与赔率时间戳（如果有）
"""
from typing import Optional, Dict, Any, List
from .client import APIFootballClient, APIError
from ..data.models import OddsRecord
import logging

logger = logging.getLogger(__name__)


class OddsClient:
    def __init__(self, client: APIFootballClient):
        self.client = client

    def _parse_bookmaker(self, fixture_id: int, bookmaker: Dict[str, Any]) -> List[OddsRecord]:
        # bookmaker: { 'id', 'name', 'bets': [ { 'id', 'name', 'values': [ { 'value', 'odd', 'odd_usd' } ] } ] }
        records: List[OddsRecord] = []
        b_id = bookmaker.get('id')
        b_name = bookmaker.get('name')
        bets = bookmaker.get('bets', [])
        for bet in bets:
            market = bet.get('name')
            values = bet.get('values', [])
            # For 1X2 market, values typically include 'Home', 'Draw', 'Away' or '1','X','2'
            if market and values:
                # 1X2: create separate records per selection
                for val in values:
                    selection = val.get('value')
                    odds = val.get('odd')
                    timestamp = val.get('date') or val.get('timestamp') or None
                    # Some bookmakers include 'handicap' or 'line' information in value
                    line = val.get('handicap') if 'handicap' in val else (val.get('line') if 'line' in val else None)
                    rec = OddsRecord(
                        fixture_id=str(fixture_id),
                        bookmaker=b_name,
                        market=market,
                        selection=selection,
                        line=line,
                        odds=float(odds) if odds is not None else None,
                        timestamp=timestamp,
                        raw=bookmaker,
                    )
                    records.append(rec)
        return records

    def get_odds(self, fixture_id: Optional[int] = None) -> List[OddsRecord]:
        if fixture_id is None:
            raise ValueError('fixture_id is required')
        params = {'fixture': fixture_id}
        try:
            resp = self.client.get('/odds', params=params)
        except APIError as e:
            logger.error('API error when fetching odds: %s', e)
            raise

        if not isinstance(resp, dict) or 'response' not in resp:
            raise APIError('Unexpected odds response format')

        out: List[OddsRecord] = []
        items = resp.get('response') or []
        for it in items:
            # Each item may contain 'bookmakers' list
            bookmakers = it.get('bookmakers', [])
            for bm in bookmakers:
                try:
                    out.extend(self._parse_bookmaker(fixture_id, bm))
                except Exception as ex:
                    logger.warning('Failed to parse bookmaker %s: %s', bm.get('name'), ex)
        return out
