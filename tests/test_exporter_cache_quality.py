# tests for exporter, cache and quality
import tempfile
import os
from football_analysis.data.exporter import export_matches, export_odds, MATCHES_CSV, ODDS_CSV
from football_analysis.data.models import MatchRecord, OddsRecord
from football_analysis.data.cache import set_cache, get_cache
from football_analysis.data.quality import quality_report_matches, quality_report_odds
import pandas as pd


def test_exporter_and_quality(tmp_path, monkeypatch):
    # override historical dir via env
    hist_dir = tmp_path / 'historical'
    hist_dir.mkdir()
    monkeypatch.setenv('HISTORICAL_DATA_PATH', str(tmp_path / 'historical' / 'matches.csv'))
    # create sample match
    m = MatchRecord(match_id='1', date='2026-10-02', league='L', season=2026, home_team='H', away_team='A', status='NS', home_odds=1.5, draw_odds=3.2, away_odds=6.0, handicap=0.0, handicap_home_odds=None, handicap_away_odds=None, source='test')
    p_matches = export_matches([m], path=hist_dir / 'matches.csv')
    assert os.path.exists(p_matches)
    df = pd.read_csv(p_matches)
    assert df.iloc[0]['home_team'] == 'H'

    o = OddsRecord(fixture_id='1', bookmaker='B', market='Match Winner', selection='Home', line=None, odds=1.5, timestamp='2026-10-02T00:00:00', raw={})
    p_odds = export_odds([o], path=hist_dir / 'odds.csv')
    assert os.path.exists(p_odds)
    df2 = pd.read_csv(p_odds)
    assert df2.iloc[0]['bookmaker'] == 'B'

    # cache
    set_cache('fixture_1', {'ok': True})
    c = get_cache('fixture_1')
    assert c is not None

    # quality
    report = quality_report_matches(df)
    assert report['total_rows'] == 1
    report2 = quality_report_odds(df2)
    assert report2['total_rows'] == 1
