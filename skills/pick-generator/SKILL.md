---
name: pick-generator
description: Analyzes games from games.json and generates betting picks with reasoning. Use after running game-scraper to produce today's picks.
---

# Pick Generator

## Purpose
Analyze each game individually, apply betting knowledge, and generate picks for `data/picks.json`.

## Workflow

1. **Read data files**
   - Load `data/games.json` for today's games
   - Load `data/history.json` for past performance context (if exists)
   - Load `config.json` for power conference list

2. **Process EACH game one at a time**

   For each game:

   a. **Check if game started** — Compare `game_time` to current time. Skip if already started.

   b. **Filter NCAAB non-power conference** — For NCAAB games, skip if NEITHER team is in a power conference:
      - ACC, Big Ten, SEC, Big 12, Big East, Pac-12
      - If unsure about conference, search to verify

   c. **Read knowledge file**
      - NBA game → Read `NBA_KNOWLEDGE.md`
      - NCAAB game → Read `NCAAB_KNOWLEDGE.md`

   d. **Search for game context**
      - Injuries and player status
      - Recent form (last 5 games)
      - Public betting percentages
      - Relevant news or storylines

   e. **Apply betting strategy** — Read `BETTING_STRATEGY.md` principles

   f. **Make decision: PICK or NO PICK**
      - If NO PICK: Note brief reason and move on
      - If PICK: Continue to next step

   g. **For picks, determine:**
      - **Bet type**: Choose ONE of spread, moneyline, or total (whichever has best value)
      - **Reasoning**: 1-2 sentences max
      - **Confidence**: low, medium, or high
        - Low: Slight lean, borderline
        - Medium: Solid reasoning, would bet
        - High: Strong conviction (max 1-2 per day)

3. **Write picks to `data/picks.json`**

4. **Run validation**
   ```bash
   python skills/pick-generator/save_picks.py
   ```

## Output Format

```json
{
  "created_at": "2025-12-16T15:00:00Z",
  "picks": [
    {
      "game_id": "nba-2025-12-16-sas-nyk",
      "sport": "NBA",
      "game": "Spurs vs Knicks",
      "pick": "Spurs +2.5",
      "odds": -110,
      "reasoning": "Wembanyama back, public heavy on Knicks, value on underdog.",
      "confidence": "medium",
      "created_at": "2025-12-16T15:00:00Z",
      "updated_at": "2025-12-16T15:00:00Z"
    }
  ]
}
```

## NO PICK Entry (Optional)

Games that were analyzed but passed on can be logged:

```json
{
  "game_id": "ncaab-2025-12-16-duke-unc",
  "sport": "NCAAB",
  "game": "Duke vs UNC",
  "pick": "NO PICK",
  "reasoning": "Line looks accurate, no clear edge.",
  "confidence": null,
  "created_at": "2025-12-16T15:00:00Z"
}
```

## Required Fields for Picks

| Field | Description |
|-------|-------------|
| game_id | Must match a game in games.json |
| sport | NBA or NCAAB |
| game | "Away vs Home" format |
| pick | The actual bet (e.g., "Spurs +2.5", "Over 228.5", "Knicks ML") |
| odds | American odds (e.g., -110, +120) |
| reasoning | 1-2 sentences explaining the pick |
| confidence | low, medium, or high |
| created_at | ISO timestamp when pick was made |
| updated_at | ISO timestamp, same as created_at initially |

## Key Rules

- Process games ONE AT A TIME — don't batch analyze
- Always check game time before picking
- Search for fresh context on each game
- Passing is acceptable — don't force picks
- One bet type per game only
- Keep reasoning brief
