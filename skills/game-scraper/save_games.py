#!/usr/bin/env python3
"""
Validates games.json structure and required fields.
Run after Claude writes game data to verify correctness.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ["game_id", "sport", "away_team", "home_team", "game_time", "spread", "moneyline", "total", "venue"]
VALID_SPORTS = ["NBA", "NCAAB"]

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config.json"
    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)

def validate_iso_timestamp(ts):
    """Check if timestamp is valid ISO 8601 format."""
    if ts is None:
        return False
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False

def validate_game(game, index):
    """Validate a single game entry. Returns list of errors."""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in game:
            errors.append(f"Game {index}: missing required field '{field}'")
        elif not game[field]:
            errors.append(f"Game {index}: empty value for '{field}'")

    if "sport" in game and game["sport"] not in VALID_SPORTS:
        errors.append(f"Game {index}: invalid sport '{game['sport']}' (must be NBA or NCAAB)")

    if "game_time" in game and not validate_iso_timestamp(game["game_time"]):
        errors.append(f"Game {index}: invalid ISO timestamp for game_time")

    return errors

def validate_games_file(games_path):
    """Validate the games.json file. Returns (is_valid, errors, stats)."""
    errors = []

    if not games_path.exists():
        return False, ["games.json does not exist"], {}

    try:
        with open(games_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], {}

    if "fetched_at" not in data:
        errors.append("Missing 'fetched_at' field")
    elif not validate_iso_timestamp(data["fetched_at"]):
        errors.append("Invalid ISO timestamp for 'fetched_at'")

    if "games" not in data:
        errors.append("Missing 'games' array")
        return False, errors, {}

    if not isinstance(data["games"], list):
        errors.append("'games' must be an array")
        return False, errors, {}

    games = data["games"]
    stats = {"total": len(games), "NBA": 0, "NCAAB": 0}

    for i, game in enumerate(games):
        game_errors = validate_game(game, i)
        errors.extend(game_errors)

        if "sport" in game:
            if game["sport"] == "NBA":
                stats["NBA"] += 1
            elif game["sport"] == "NCAAB":
                stats["NCAAB"] += 1

    return len(errors) == 0, errors, stats

def main():
    config = load_config()
    games_path = Path(__file__).parent.parent.parent / config["paths"]["games"]

    print(f"Validating {games_path}...")
    is_valid, errors, stats = validate_games_file(games_path)

    if not is_valid:
        print("\nValidation FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("\nValidation PASSED")
    print(f"  Total games: {stats['total']}")
    print(f"  NBA: {stats['NBA']}")
    print(f"  NCAAB: {stats['NCAAB']}")

    if stats["total"] == 0:
        print("\n  Warning: No games in file")

if __name__ == "__main__":
    main()
