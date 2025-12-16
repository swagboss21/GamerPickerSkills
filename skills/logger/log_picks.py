#!/usr/bin/env python3
"""
Moves picks from picks.json to history.json with PENDING status.
Skips NO PICK entries and duplicates.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def load_config():
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

def save_json(path, data):
    """Save data to JSON file with pretty formatting."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    config = load_config()
    base_path = Path(__file__).parent.parent.parent

    picks_path = base_path / config["paths"]["picks"]
    games_path = base_path / config["paths"]["games"]
    history_path = base_path / config["paths"]["history"]

    # Load data
    picks_data = load_json(picks_path, {"picks": []})
    games_data = load_json(games_path, {"games": []})
    history = load_json(history_path, [])

    # Build game_id -> game_time lookup
    game_times = {g["game_id"]: g["game_time"] for g in games_data.get("games", [])}

    # Track existing game_ids in history
    existing_ids = {h["game_id"] for h in history}

    # Process picks
    added = 0
    skipped_no_pick = 0
    skipped_duplicate = 0

    for pick in picks_data.get("picks", []):
        game_id = pick.get("game_id")

        # Skip NO PICK entries
        if pick.get("pick") == "NO PICK":
            skipped_no_pick += 1
            continue

        # Skip duplicates
        if game_id in existing_ids:
            skipped_duplicate += 1
            continue

        # Create history entry
        history_entry = {
            "game_id": game_id,
            "sport": pick.get("sport"),
            "game": pick.get("game"),
            "pick": pick.get("pick"),
            "odds": pick.get("odds"),
            "reasoning": pick.get("reasoning"),
            "confidence": pick.get("confidence"),
            "pick_time": pick.get("created_at"),
            "game_time": game_times.get(game_id),
            "result": "PENDING",
            "final_score": None
        }

        history.append(history_entry)
        existing_ids.add(game_id)
        added += 1

    # Save updated history
    save_json(history_path, history)

    # Report results
    print(f"Logger complete:")
    print(f"  Added to history: {added}")
    print(f"  Skipped (NO PICK): {skipped_no_pick}")
    print(f"  Skipped (duplicate): {skipped_duplicate}")
    print(f"  Total in history: {len(history)}")

    # List pending picks
    pending = [h for h in history if h["result"] == "PENDING"]
    if pending:
        print(f"\nPending picks ({len(pending)}):")
        for p in pending:
            print(f"  - {p['game']}: {p['pick']} ({p['confidence']})")

if __name__ == "__main__":
    main()
