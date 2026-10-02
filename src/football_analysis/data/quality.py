"""
数据质量检查工具。
返回一个 dict 报告，列出问题与统计信息。
"""
from typing import Dict, Any
import pandas as pd


def quality_report_matches(df: pd.DataFrame) -> Dict[str, Any]:
    issues = {}
    issues['total_rows'] = len(df)
    issues['missing_home'] = int(df['home_team'].isna().sum()) if 'home_team' in df.columns else None
    issues['missing_away'] = int(df['away_team'].isna().sum()) if 'away_team' in df.columns else None
    if 'date' in df.columns:
        invalid_dates = df['date'].isna().sum()
        issues['invalid_dates'] = int(invalid_dates)
    else:
        issues['invalid_dates'] = None
    # fixture_id duplicates
    if 'match_id' in df.columns:
        dup = df['match_id'].duplicated().sum()
        issues['duplicate_match_id'] = int(dup)
    # odds positive check
    for col in ['home_odds', 'draw_odds', 'away_odds']:
        if col in df.columns:
            issues[f'{col}_nonpositive'] = int((df[col].dropna() <= 0).sum())
    return issues


def quality_report_odds(df: pd.DataFrame) -> Dict[str, Any]:
    issues = {}
    issues['total_rows'] = len(df)
    issues['missing_bookmaker'] = int(df['bookmaker'].isna().sum()) if 'bookmaker' in df.columns else None
    if 'odds' in df.columns:
        issues['odds_nonpositive'] = int((df['odds'].dropna() <= 0).sum())
    if 'fixture_id' in df.columns:
        issues['duplicate_fixture_bookmaker_market'] = int(df.duplicated(subset=['fixture_id', 'bookmaker', 'market', 'selection', 'line', 'timestamp']).sum())
    return issues
