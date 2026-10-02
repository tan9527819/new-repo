"""
CSV schema and mapping utilities.
Defines canonical columns and provides a mapping layer from arbitrary CSV columns.
Canonical names use consistent home_odds/draw_odds/away_odds naming.
"""
from typing import Dict, List
import pandas as pd

CANONICAL_COLUMNS = [
    'match_id', 'fixture_id', 'date', 'league', 'season', 'home_team', 'away_team', 'status',
    # result fields
    'result', 'home_score', 'away_score',
    # 1X2 snapshot
    'bookmaker', 'market', 'selection', 'home_odds', 'draw_odds', 'away_odds', 'timestamp',
    # handicap snapshot
    'handicap', 'handicap_home_odds', 'handicap_away_odds',
]

# common alternative names mapped to canonical
COLUMN_ALIASES = {
    # dates
    'match_date': 'date', 'kickoff': 'date', 'datetime': 'date',
    # teams
    'home': 'home_team', 'homename': 'home_team', 'away': 'away_team', 'awayname': 'away_team',
    # 1X2 shorthand
    '1': 'home_odds', 'x': 'draw_odds', '2': 'away_odds',
    # common odds column variants mapped to canonical
    'odds_home': 'home_odds', 'odds_draw': 'draw_odds', 'odds_away': 'away_odds',
    'home_odds': 'home_odds', 'draw_odds': 'draw_odds', 'away_odds': 'away_odds',
    # ids
    'fixture_id': 'fixture_id', 'match_id': 'match_id',
    # others
    'bookmaker': 'bookmaker', 'market': 'market', 'selection': 'selection',
    'line': 'handicap', 'handicap': 'handicap', 'spread': 'handicap',
    'odds': 'home_odds',  # ambiguous: interpreted as home_odds when no selection provided
    'timestamp': 'timestamp',
    'result': 'result', 'home_score': 'home_score', 'away_score': 'away_score',
    'season': 'season', 'status': 'status', 'league': 'league',
}


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attempt to map dataframe columns to canonical schema without modifying source file.
    Returns a new DataFrame with as many canonical columns populated as possible.
    """
    out = pd.DataFrame()
    cols = list(df.columns)
    lower_map = {c.lower(): c for c in cols}
    for alias, canon in COLUMN_ALIASES.items():
        # try direct match
        if alias in df.columns:
            out[canon] = df[alias]
            continue
        # try lowercase match
        if alias.lower() in lower_map:
            out[canon] = df[lower_map[alias.lower()]]
            continue
        # try canonical name present directly
        if canon in df.columns:
            out[canon] = df[canon]
    # Keep original columns accessible under 'raw_*' prefix
    for c in cols:
        out[f'raw_{c}'] = df[c]
    return out
