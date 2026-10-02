"""
简单的 CLI 用于拉取/同步数据并运行质量检查。
"""
import argparse
import os
import logging
from typing import Optional

from .api.client import APIFootballClient
from .api.fixtures import FixturesClient
from .api.odds import OddsClient
from .data.exporter import export_matches, export_odds
from .data.cache import get_cache, set_cache
from .data.csv_loader import read_and_clean_csv
from .data.quality import quality_report_matches, quality_report_odds

logger = logging.getLogger(__name__)


def cmd_fixtures(args):
    client = APIFootballClient()
    fc = FixturesClient(client)
    fixtures = fc.get_fixtures(date_from=args.date, date_to=args.date) if args.date else fc.get_fixtures()
    # export
    export_matches(fixtures)
    print(f'Exported {len(fixtures)} fixtures')


def cmd_odds(args):
    client = APIFootballClient()
    oc = OddsClient(client)
    cache_key = f'fixture_{args.fixture_id}'
    data = get_cache(cache_key)
    if data is None:
        odds = oc.get_odds(args.fixture_id)
        # cache raw API response as list of dicts
        set_cache(cache_key, [o.to_dict() for o in odds])
    else:
        # reconstruct OddsRecord objects minimally
        from .data.models import OddsRecord
        odds = [OddsRecord(**o) for o in data]
    export_odds(odds)
    print(f'Exported {len(odds)} odds rows')


def cmd_sync(args):
    # sync fixtures for date and then odds for each fixture
    client = APIFootballClient()
    fc = FixturesClient(client)
    oc = OddsClient(client)
    fixtures = list(fc.iter_fixtures(date_from=args.date, date_to=args.date))
    export_matches(fixtures)
    print(f'Exported {len(fixtures)} fixtures')
    # for each fixture get odds
    all_odds = []
    for f in fixtures:
        fid = int(f.match_id) if f.match_id else None
        if not fid:
            continue
        cache_key = f'fixture_{fid}'
        data = get_cache(cache_key)
        if data is None:
            odds = oc.get_odds(fid)
            set_cache(cache_key, [o.to_dict() for o in odds])
        else:
            from .data.models import OddsRecord
            odds = [OddsRecord(**o) for o in data]
        export_odds(odds)
        all_odds.extend(odds)
    print(f'Exported {len(all_odds)} total odds rows')


def cmd_quality(args):
    path = os.getenv('HISTORICAL_DATA_PATH', './data/historical/matches.csv')
    if os.path.exists(path):
        df = read_and_clean_csv(path)
        report = quality_report_matches(df)
        print('Matches quality:')
        for k, v in report.items():
            print(f'  {k}: {v}')
    odds_path = './data/historical/odds.csv'
    if os.path.exists(odds_path):
        import pandas as pd
        df2 = pd.read_csv(odds_path)
        report2 = quality_report_odds(df2)
        print('Odds quality:')
        for k, v in report2.items():
            print(f'  {k}: {v}')


def main():
    parser = argparse.ArgumentParser(prog='football_analysis')
    sub = parser.add_subparsers(dest='cmd')

    p_f = sub.add_parser('fixtures')
    p_f.add_argument('--date', help='YYYY-MM-DD')

    p_o = sub.add_parser('odds')
    p_o.add_argument('--fixture-id', type=int, required=True)

    p_s = sub.add_parser('sync')
    p_s.add_argument('--date', help='YYYY-MM-DD')

    p_q = sub.add_parser('quality')

    args = parser.parse_args()
    if args.cmd == 'fixtures':
        cmd_fixtures(args)
    elif args.cmd == 'odds':
        cmd_odds(args)
    elif args.cmd == 'sync':
        cmd_sync(args)
    elif args.cmd == 'quality':
        cmd_quality(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
