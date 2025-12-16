#!/usr/bin/env python3
"""
Validates picks.json structure and required fields.
Verifies game_ids match games in games.json.
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["game_id", "sport", "game", "pick", "reasoning", "created_at"]
PICK_REQUIRED_FIELDS = ["odds", "confidence", "updated_at"]  # Additional fields for actual picks (not NO PICK)
VALID_SPORTS = ["NBA", "NCAAB"]
VALID_CONFIDENCE = ["low", "medium", "high"]

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config.json"
    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)

def load_games(games_path):
    """Load games.json and return set of game_ids."""
    if not games_path.exists():
        return set()
    with open(games_path) as f:
        data = json.load(f)
    return {g["game_id"] for g in data.get("games", [])}

def validate_pick(pick, index, valid_game_ids):
    """Validate a single pick entry. Returns list of errors."""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in pick:
            errors.append(f"Pick {index}: missing required field '{field}'")

    if "game_id" in pick and pick["game_id"] not in valid_game_ids:
        errors.append(f"Pick {index}: game_id '{pick['game_id']}' not found in games.json")

    if "sport" in pick and pick["sport"] not in VALID_SPORTS:
        errors.append(f"Pick {index}: invalid sport '{pick['sport']}'")

    is_no_pick = pick.get("pick") == "NO PICK"

    if not is_no_pick:
        for field in PICK_REQUIRED_FIELDS:
            if field not in pick:
                errors.append(f"Pick {index}: missing required field '{field}' for actual pick")

        if "confidence" in pick and pick["confidence"] not in VALID_CONFIDENCE:
            errors.append(f"Pick {index}: invalid confidence '{pick['confidence']}' (must be low/medium/high)")

        if "odds" in pick and not isinstance(pick["odds"], (int, float)):
            errors.append(f"Pick {index}: odds must be a number")

    return errors

def validate_picks_file(picks_path, games_path):
    """Validate the picks.json file. Returns (is_valid, errors, stats)."""
    errors = []

    if not picks_path.exists():
        return False, ["picks.json does not exist"], {}

    try:
        with open(picks_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], {}

    if "created_at" not in data:
        errors.append("Missing 'created_at' field")

    if "picks" not in data:
        errors.append("Missing 'picks' array")
        return False, errors, {}

    if not isinstance(data["picks"], list):
        errors.append("'picks' must be an array")
        return False, errors, {}

    valid_game_ids = load_games(games_path)
    picks = data["picks"]

    stats = {
        "total": 0,
        "actual_picks": 0,
        "no_picks": 0,
        "NBA": 0,
        "NCAAB": 0,
        "low": 0,
        "medium": 0,
        "high": 0
    }

    for i, pick in enumerate(picks):
        pick_errors = validate_pick(pick, i, valid_game_ids)
        errors.extend(pick_errors)

        stats["total"] += 1

        if pick.get("pick") == "NO PICK":
            stats["no_picks"] += 1
        else:
            stats["actual_picks"] += 1
            conf = pick.get("confidence")
            if conf in VALID_CONFIDENCE:
                stats[conf] += 1

        sport = pick.get("sport")
        if sport in ["NBA", "NCAAB"]:
            stats[sport] += 1

    return len(errors) == 0, errors, stats

def main():
    config = load_config()
    base_path = Path(__file__).parent.parent.parent
    picks_path = base_path / config["paths"]["picks"]
    games_path = base_path / config["paths"]["games"]

    print(f"Validating {picks_path}...")
    is_valid, errors, stats = validate_picks_file(picks_path, games_path)

    if not is_valid:
        print("\nValidation FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("\nValidation PASSED")
    print(f"\nSummary:")
    print(f"  Total entries: {stats['total']}")
    print(f"  Actual picks: {stats['actual_picks']}")
    print(f"  No picks: {stats['no_picks']}")
    print(f"\nBy sport:")
    print(f"  NBA: {stats['NBA']}")
    print(f"  NCAAB: {stats['NCAAB']}")
    print(f"\nBy confidence:")
    print(f"  High: {stats['high']}")
    print(f"  Medium: {stats['medium']}")
    print(f"  Low: {stats['low']}")

    if stats["high"] > 2:
        print(f"\n  Warning: {stats['high']} high confidence picks (recommended max: 2)")

    if stats["actual_picks"] == 0:
        print("\n  Warning: No actual picks in file")

if __name__ == "__main__":
    main()
