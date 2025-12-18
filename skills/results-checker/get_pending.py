#!/usr/bin/env python3
"""
Lists PENDING games in history.json that finished at least 3 hours ago.
Read-only - does not modify any files.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def load_config():
    """Load config.json from project root."""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def load_json(path, default=None):
    """Load JSON file or return default if not exists."""
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def parse_game_time(game_time_str):
    """Parse ISO 8601 game time string to datetime."""
    try:
        # Handle various ISO formats
        if game_time_str.endswith('Z'):
            return datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
        return datetime.fromisoformat(game_time_str)
    except (ValueError, TypeError):
        return None


def main():
    config = load_config()
    base_path = Path(__file__).parent.parent.parent
    history_path = base_path / config["paths"]["history"]

    history = load_json(history_path, [])

    if not history:
        print("No pending games to update")
        return

    now = datetime.now(timezone.utc)
    three_hours = timedelta(hours=3)
    pending_games = []

    for entry in history:
        # Only PENDING results
        if entry.get("result") != "PENDING":
            continue

        # Parse game time
        game_time = parse_game_time(entry.get("game_time"))
        if not game_time:
            continue

        # Check if game finished (3+ hours ago)
        if game_time + three_hours > now:
            continue

        # Extract date from game_time
        game_date = game_time.strftime("%Y-%m-%d")

        pending_games.append({
            "game_id": entry.get("game_id"),
            "game": entry.get("game"),
            "date": game_date
        })

    if not pending_games:
        print("No pending games to update")
        return

    # Print pending games
    for game in pending_games:
        print(f"{game['game_id']} | {game['game']} | {game['date']}")


if __name__ == "__main__":
    main()
