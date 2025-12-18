---
name: results-checker
description: Updates PENDING picks with WIN/LOSS/PUSH results. Use after games have finished to update history.json with final scores and outcomes.
---

# Results Checker

## Purpose

Update pending picks in history.json with game results after games have finished.

## Workflow

1. Run `get_pending.py` to see which games need results
2. For each game: search "{away} {home} final score {date}"
3. For each game: run `update_result.py {game_id} {team1} {score1} {team2} {score2}`

## Script 1: get_pending.py

Lists PENDING games that finished at least 3 hours ago.

### Usage

```bash
python skills/results-checker/get_pending.py
```

### Output Format

```
game_id | teams | date
```

### Example

```
nba-2025-12-16-sas-nyk | Spurs vs Knicks | 2025-12-16
ncaab-2025-12-16-dep-stj | DePaul vs St. John's | 2025-12-16
```

If no games need updating: "No pending games to update"

## Script 2: update_result.py

Evaluates a single pick against the final score and updates history.json.

### Usage

```bash
python skills/results-checker/update_result.py {game_id} {team1} {score1} {team2} {score2}
```

### Arguments

| Arg | Description |
|-----|-------------|
| game_id | The game identifier (e.g., nba-2025-12-16-sas-nyk) |
| team1 | First team name (partial match, case-insensitive) |
| score1 | First team's final score |
| team2 | Second team name (partial match, case-insensitive) |
| score2 | Second team's final score |

Team names are matched against `home_team` and `away_team` in games.json using partial, case-insensitive matching. Order doesn't matter.

### Examples

```bash
# Either order works:
python skills/results-checker/update_result.py nba-2025-12-16-sas-nyk Knicks 124 Spurs 113
python skills/results-checker/update_result.py nba-2025-12-16-sas-nyk Spurs 113 Knicks 124

# Output: Updated nba-2025-12-16-sas-nyk: Knicks -2.5 -> WIN (Knicks 124, Spurs 113)
```

### Pick Types Supported

| Pick Format | Example |
|-------------|---------|
| Team spread | "Knicks -2.5" or "Spurs +2.5" |
| Over total | "Over 228.5" |
| Under total | "Under 150" |
| Moneyline | "Knicks ML" |

## Result Values

| Result | When Applied |
|--------|--------------|
| WIN | Pick covered the spread, hit the total, or ML team won |
| LOSS | Pick did not cover |
| PUSH | Exact spread/total match (no winner) |
| CANCELLED | Game cancelled or postponed (manual entry) |

## Error Handling

- game_id not found: prints error, exits 1
- Pick format unrecognized: prints error, exits 1
- Invalid score: prints error, exits 1
- Already has result (not PENDING): prints warning, skips, exits 0
