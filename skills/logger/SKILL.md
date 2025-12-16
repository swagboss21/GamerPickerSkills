---
name: logger
description: Moves finalized picks from picks.json to history.json with PENDING status. Use after generating picks to create a permanent record.
---

# Logger

## Purpose
Transfer picks from `data/picks.json` into `data/history.json` for permanent tracking.

## Workflow

1. Run the log script:
   ```bash
   python skills/logger/log_picks.py
   ```

2. The script will:
   - Read `data/picks.json` for current picks
   - Read `data/games.json` to get game times
   - Read `data/history.json` (or create if missing)
   - For each actual pick (skip NO PICK entries):
     - Check if already logged (by game_id)
     - Add to history with `result: "PENDING"`
   - Save updated history

## History Entry Format

```json
{
  "game_id": "nba-2025-12-16-sas-nyk",
  "sport": "NBA",
  "game": "Spurs vs Knicks",
  "pick": "Spurs +2.5",
  "odds": -110,
  "reasoning": "Wembanyama back, public heavy on Knicks, value on underdog.",
  "confidence": "medium",
  "pick_time": "2025-12-16T15:00:00Z",
  "game_time": "2025-12-16T20:30:00-05:00",
  "result": "PENDING",
  "final_score": null
}
```

## Fields Added by Logger

| Field | Source |
|-------|--------|
| pick_time | From pick's `created_at` |
| game_time | From games.json |
| result | Set to "PENDING" |
| final_score | Set to null |

## Duplicate Prevention

The script skips picks where `game_id` already exists in history.json. This allows safe re-runs without creating duplicates.
