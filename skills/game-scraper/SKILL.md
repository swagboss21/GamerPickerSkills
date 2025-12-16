---
name: game-scraper
description: Fetches today's NBA and NCAAB games with odds and times. Use when collecting games to analyze for betting picks.
---

# Game Scraper

## Purpose
Search the web for today's games and betting odds, then save to `data/games.json`.

## Workflow

1. Read `config.json` to get enabled sports
2. For each enabled sport, search the web for today's games and odds
3. Collect: teams, game time (ISO 8601), spread, moneyline, total, venue
4. Combine all games into one list
5. Write to `data/games.json`
6. Run `python skills/game-scraper/save_games.py` to validate

## Search Strategy

**NBA**: Search for "NBA games today odds spreads" on ESPN, CBS Sports, or covers.com

**NCAAB**: Search for "college basketball games today odds" — scrape ALL games (filtering by conference happens in pick-generator)

## Output Format

```json
{
  "fetched_at": "2025-12-16T14:00:00Z",
  "games": [
    {
      "game_id": "nba-2025-12-16-sas-nyk",
      "sport": "NBA",
      "away_team": "San Antonio Spurs",
      "home_team": "New York Knicks",
      "game_time": "2025-12-16T20:30:00-05:00",
      "spread": "Knicks -2.5",
      "moneyline": "Knicks -140 / Spurs +120",
      "total": "O/U 228.5",
      "venue": "Madison Square Garden"
    }
  ]
}
```

## Game ID Convention

`{sport}-{date}-{away_abbrev}-{home_abbrev}` (lowercase)

Examples:
- `nba-2025-12-16-sas-nyk`
- `ncaab-2025-12-16-duke-unc`

## Required Fields

| Field | Description |
|-------|-------------|
| game_id | Unique identifier |
| sport | NBA or NCAAB |
| away_team | Full team name |
| home_team | Full team name |
| game_time | ISO 8601 with timezone |
| spread | e.g., "Knicks -2.5" |
| moneyline | e.g., "Knicks -140 / Spurs +120" |
| total | e.g., "O/U 228.5" |
| venue | Arena name |
