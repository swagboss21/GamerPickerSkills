# Betting Agent System — Handoff Document

## What We're Building

A modular skill-based system for making sports picks, tracking reasoning, and building a historical record to improve over time.

---

## Target Sports

- **NBA** — All games
- **NCAAB** — Power conferences only (ACC, Big Ten, SEC, Big 12, Big East, Pac-12)

---

## Folder Structure
```
/betting-agent/
├── HANDOFF.md
├── config.json
├── /data/
│   ├── games.json
│   ├── picks.json
│   └── history.json
└── /skills/
    ├── /game-scraper/
    │   ├── SKILL.md
    │   └── save_games.py
    ├── /pick-generator/
    │   ├── SKILL.md
    │   └── save_picks.py
    └── /logger/
        ├── SKILL.md
        └── log_picks.py
```

---

## Skills to Build Today

### Skill 1: Game Scraper
- Search web broadly for today's games + odds (NBA, NCAAB)
- Sources: ESPN, CBS Sports, covers.com, DraftKings/FanDuel odds pages
- Save to `data/games.json` with game times as ISO timestamps
- Scrape ALL games — filtering happens in pick-generator
- Required fields: teams, time (ISO format), spread, moneyline, total, venue, sport

### Skill 2: Pick Generator
- Read `data/games.json`
- Read `data/history.json` (if exists) for past performance context
- For NCAAB: only pick power conference games
- Pick ONE bet type per game (spread, moneyline, OR total — whichever looks best)
- Can pass on games — output "NO PICK" with brief reason
- Save to `data/picks.json`
- CRITICAL: Skip games that have already started (compare game time to current time)

### Skill 3: Logger
- Move finalized picks from `data/picks.json` into `data/history.json`
- Mark them as "PENDING" for results
- Timestamp when the pick was logged

---

## Skill File Format (Required)

Every SKILL.md needs YAML frontmatter:
```yaml
---
name: game-scraper
description: Fetches today's NBA and NCAAB games with odds and times. Use when collecting games to analyze for betting picks.
---
```

- **name**: lowercase, hyphens only, max 64 chars
- **description**: what it does + when to use it, written in third person

---

## Timestamp Rules

- All times stored in ISO 8601 format with timezone
- Before generating picks, check: has the game started?
- Picks can be updated UNTIL game time (store `updated_at` timestamp)
- A pick made at 2pm for an 8pm game = valid
- A pick attempted at 8:15pm for an 8pm game = rejected

---

## Data Shapes

**games.json**
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
      "venue": "T-Mobile Arena, Las Vegas"
    }
  ]
}
```

**picks.json**
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

**history.json**
```json
[
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
]
```

---

## Pick Reasoning

Brief. 1-2 sentences max.

Examples:
- "Public heavy on favorite, line inflated. Value on underdog."
- "Back-to-back for home team, key player questionable."
- "Both teams top 20 in defensive efficiency, expect low scoring."

---

## Confidence Tiers

- **Low** — Slight lean, borderline passing. "Could go either way."
- **Medium** — Solid reasoning, would bet. "Multiple factors align."
- **High** — Strong conviction, best bet of day. "Clear edge." (Max 1-2 per day)

---

## Execution Method

Simple standalone Python scripts, manual invocation:
```bash
python skills/game-scraper/save_games.py
python skills/pick-generator/save_picks.py
python skills/logger/log_picks.py
```

---

## Best Practices (Follow These)

### Be Concise
Claude knows what NBA is, what odds are, how JSON works. Only add context Claude doesn't have.

### Scripts Handle Errors
Don't punt to Claude. Handle missing files, empty results, etc.
```python
# Good
if not games:
    print("No games found for today")
    return []

# Bad
assert len(games) > 0
```

### Validate After Saving
After writing JSON, confirm file exists and has expected shape.

### Use Checklists for Workflows
```
Task Progress:
- [ ] Step 1: Fetch games
- [ ] Step 2: Save to games.json
- [ ] Step 3: Verify file
```

### Avoid
- Windows paths (use forward slashes)
- Too many options ("use ESPN or CBS or...")
- Time-sensitive hardcoded info
- Vague descriptions

---

## Guardrails — Do NOT Over-Engineer

- No databases, just JSON files
- No external APIs, just web search
- No frontend/UI, terminal output is fine
- No backtesting yet — forward testing only
- No complex confidence algorithms — just low/medium/high
- Don't build outcome fetcher today, that's tomorrow

---

## Goal for Today

1. Build the three skills (with proper SKILL.md frontmatter)
2. Run game scraper for Dec 16
3. Generate picks for games that haven't started
4. Log picks to history
5. **Output a clean list of today's picks with reasoning**

---

## Current Context

Today is Tuesday, December 16, 2025. 

Key games:
- NBA Cup Final: Spurs vs Knicks @ 8:30 PM ET
- Multiple NCAAB games throughout the day

Some games may have already started — the system must handle this.