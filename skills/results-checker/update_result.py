#!/usr/bin/env python3
"""
Evaluates a single pick against final scores and updates history.json.
Usage: python update_result.py <game_id> <team1_name> <team1_score> <team2_name> <team2_score>
"""

import json
import re
import sys
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


def save_json(path, data):
    """Save data to JSON file with pretty formatting."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def teams_match(input_name, full_name):
    """Check if input matches the team (case-insensitive, partial match)."""
    return input_name.lower() in full_name.lower()


def parse_pick(pick_str):
    """
    Parse pick string into structured data.

    Returns dict with:
      - type: 'spread', 'total', or 'moneyline'
      - For spread: team, line
      - For total: direction ('over'/'under'), number
      - For moneyline: team
    """
    pick_str = pick_str.strip()

    # Match Over/Under totals: "Over 228.5" or "Under 150"
    total_match = re.match(r'^(Over|Under)\s+([\d.]+)$', pick_str, re.IGNORECASE)
    if total_match:
        return {
            'type': 'total',
            'direction': total_match.group(1).lower(),
            'number': float(total_match.group(2))
        }

    # Match Moneyline: "Knicks ML" or "Team Name ML"
    ml_match = re.match(r'^(.+?)\s+ML$', pick_str, re.IGNORECASE)
    if ml_match:
        return {
            'type': 'moneyline',
            'team': ml_match.group(1).strip()
        }

    # Match Spread: "Knicks -2.5" or "Spurs +2.5" or "Team Name -5"
    spread_match = re.match(r'^(.+?)\s+([+-][\d.]+)$', pick_str)
    if spread_match:
        return {
            'type': 'spread',
            'team': spread_match.group(1).strip(),
            'line': float(spread_match.group(2))
        }

    return None


def get_team_from_game(game_str, team_name):
    """
    Determine if team is home or away from game string.
    Game format: "Away vs Home" (e.g., "Spurs vs Knicks")

    Returns 'home' or 'away' or None if not found.
    """
    parts = game_str.split(' vs ')
    if len(parts) != 2:
        return None

    away_team = parts[0].strip()
    home_team = parts[1].strip()

    # Check for exact match or partial match
    if team_name.lower() == home_team.lower() or team_name.lower() in home_team.lower():
        return 'home'
    if team_name.lower() == away_team.lower() or team_name.lower() in away_team.lower():
        return 'away'

    return None


def evaluate_spread(pick_data, game_str, home_score, away_score):
    """Evaluate a spread pick. Returns WIN, LOSS, or PUSH."""
    team = pick_data['team']
    line = pick_data['line']

    position = get_team_from_game(game_str, team)
    if not position:
        return None, f"Could not determine if '{team}' is home or away in '{game_str}'"

    if position == 'home':
        picked_score = home_score
        opponent_score = away_score
    else:
        picked_score = away_score
        opponent_score = home_score

    # Calculate: picked_team_score - opponent_score + line
    margin = picked_score - opponent_score + line

    if margin > 0:
        return 'WIN', None
    elif margin < 0:
        return 'LOSS', None
    else:
        return 'PUSH', None


def evaluate_total(pick_data, home_score, away_score):
    """Evaluate a total (over/under) pick. Returns WIN, LOSS, or PUSH."""
    direction = pick_data['direction']
    number = pick_data['number']

    total = home_score + away_score

    if direction == 'over':
        if total > number:
            return 'WIN', None
        elif total < number:
            return 'LOSS', None
        else:
            return 'PUSH', None
    else:  # under
        if total < number:
            return 'WIN', None
        elif total > number:
            return 'LOSS', None
        else:
            return 'PUSH', None


def evaluate_moneyline(pick_data, game_str, home_score, away_score):
    """Evaluate a moneyline pick. Returns WIN, LOSS, or PUSH."""
    team = pick_data['team']

    position = get_team_from_game(game_str, team)
    if not position:
        return None, f"Could not determine if '{team}' is home or away in '{game_str}'"

    if position == 'home':
        picked_score = home_score
        opponent_score = away_score
    else:
        picked_score = away_score
        opponent_score = home_score

    if picked_score > opponent_score:
        return 'WIN', None
    elif picked_score < opponent_score:
        return 'LOSS', None
    else:
        return 'PUSH', None


def main():
    # Parse arguments
    if len(sys.argv) != 6:
        print("Usage: python update_result.py <game_id> <team1_name> <team1_score> <team2_name> <team2_score>")
        print("Example: python update_result.py ncaab-2025-12-16-tenn-lou Tennessee 83 Louisville 62")
        sys.exit(1)

    game_id = sys.argv[1]
    team1_name = sys.argv[2]
    team2_name = sys.argv[4]

    try:
        team1_score = int(sys.argv[3])
        team2_score = int(sys.argv[5])
    except ValueError:
        print(f"Error: Scores must be integers. Got: {sys.argv[3]}, {sys.argv[5]}")
        sys.exit(1)

    # Load config, games, and history
    config = load_config()
    base_path = Path(__file__).parent.parent.parent
    games_path = base_path / config["paths"]["games"]
    history_path = base_path / config["paths"]["history"]

    games_data = load_json(games_path, {"games": []})
    history = load_json(history_path, [])

    if not history:
        print(f"Error: history.json is empty or not found")
        sys.exit(1)

    # Find the game in games.json to get home/away teams
    game_info = None
    for game in games_data.get("games", []):
        if game.get("game_id") == game_id:
            game_info = game
            break

    if not game_info:
        print(f"Error: game_id '{game_id}' not found in games.json")
        sys.exit(1)

    home_team_full = game_info.get("home_team", "")
    away_team_full = game_info.get("away_team", "")

    # Match input team names to home/away
    home_score = None
    away_score = None
    home_team_matched = None
    away_team_matched = None

    # Check if team1 is home or away
    if teams_match(team1_name, home_team_full):
        home_score = team1_score
        home_team_matched = team1_name
    elif teams_match(team1_name, away_team_full):
        away_score = team1_score
        away_team_matched = team1_name
    else:
        print(f"Error: '{team1_name}' does not match home team '{home_team_full}' or away team '{away_team_full}'")
        sys.exit(1)

    # Check if team2 is home or away
    if teams_match(team2_name, home_team_full):
        if home_score is not None:
            print(f"Error: Both '{team1_name}' and '{team2_name}' match home team '{home_team_full}'")
            sys.exit(1)
        home_score = team2_score
        home_team_matched = team2_name
    elif teams_match(team2_name, away_team_full):
        if away_score is not None:
            print(f"Error: Both '{team1_name}' and '{team2_name}' match away team '{away_team_full}'")
            sys.exit(1)
        away_score = team2_score
        away_team_matched = team2_name
    else:
        print(f"Error: '{team2_name}' does not match home team '{home_team_full}' or away team '{away_team_full}'")
        sys.exit(1)

    # Verify we have both scores
    if home_score is None or away_score is None:
        print(f"Error: Could not assign both home and away scores")
        sys.exit(1)

    # Find the history entry
    entry_idx = None
    for idx, entry in enumerate(history):
        if entry.get("game_id") == game_id:
            entry_idx = idx
            break

    if entry_idx is None:
        print(f"Error: game_id '{game_id}' not found in history.json")
        sys.exit(1)

    entry = history[entry_idx]

    # Check if already has result
    if entry.get("result") != "PENDING":
        print(f"Warning: {game_id} already has result '{entry.get('result')}'. Skipping.")
        sys.exit(0)

    # Parse the pick
    pick_str = entry.get("pick")
    pick_data = parse_pick(pick_str)

    if not pick_data:
        print(f"Error: Could not parse pick format: '{pick_str}'")
        sys.exit(1)

    game_str = entry.get("game")

    # Evaluate based on pick type
    if pick_data['type'] == 'spread':
        result, error = evaluate_spread(pick_data, game_str, home_score, away_score)
    elif pick_data['type'] == 'total':
        result, error = evaluate_total(pick_data, home_score, away_score)
    elif pick_data['type'] == 'moneyline':
        result, error = evaluate_moneyline(pick_data, game_str, home_score, away_score)
    else:
        print(f"Error: Unknown pick type: {pick_data['type']}")
        sys.exit(1)

    if error:
        print(f"Error: {error}")
        sys.exit(1)

    # Build final score string using matched team names (capitalize first letter)
    final_score = f"{home_team_matched.title()} {home_score}, {away_team_matched.title()} {away_score}"

    # Update entry
    history[entry_idx]["result"] = result
    history[entry_idx]["final_score"] = final_score

    # Save
    save_json(history_path, history)

    # Print confirmation
    print(f"Updated {game_id}: {pick_str} -> {result} ({final_score})")


if __name__ == "__main__":
    main()
