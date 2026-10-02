"""
CSV schema and mapping utilities.
Defines canonical columns and provides a mapping layer from arbitrary CSV columns.
"""
from typing import Dict, List
import pandas as pd

CANONICAL_COLUMNS = [
    'match_id', 'fixture_id', 'date', 'league', 'season', 'home_team', 'away_team',
    'bookmaker', 'market', 'selection', 'line', 'odds', 'timestamp',
    'result', 'home_score', 'away_score'
]

# common alternative names mapped to canonical
COLUMN_ALIASES = {
    'match_date': 'date', 'kickoff': 'date', 'datetime': 'date',
    'home': 'home_team', 'homeName': 'home_team', 'away': 'away_team', 'awayName': 'away_team',
    '1': 'home_odds', 'X': 'draw_odds', '2': 'away_odds',
    'home_odds': 'odds_home', 'draw_odds': 'odds_draw', 'away_odds': 'odds_away',
    'fixture_id': 'fixture_id', 'match_id': 'match_id',
    'bookmaker': 'bookmaker', 'market': 'market', 'selection': 'selection',
    'line': 'line', 'handicap': 'line', 'odds': 'odds', 'timestamp': 'timestamp',
    'result': 'result', 'home_score': 'home_score', 'away_score': 'away_score'
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
