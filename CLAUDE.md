# Betting Agent — Project Instructions

## Available Skills

When asked to run a skill, read its SKILL.md first then follow the workflow.

| Trigger | Skill Location | What It Does |
|---------|----------------|--------------|
| "run game scraper", "get today's games", "fetch games" | skills/game-scraper/SKILL.md | Search web for games and odds |
| "run pick generator", "make picks", "generate picks" | skills/pick-generator/SKILL.md | Analyze games and create picks |
| "run logger", "log picks", "save picks to history" | skills/logger/SKILL.md | Move picks to history.json |
| "run results", "check results", "update results" | skills/results-checker/SKILL.md | Fetch scores and evaluate picks |

## Workflow Order

Typical daily flow:
1. Game scraper → gets games.json
2. Pick generator → creates picks.json
3. Logger → moves picks to history.json
4. (Next day) Results checker → updates history with WIN/LOSS

## Key Files

- `config.json` — paths and settings
- `data/games.json` — today's games
- `data/picks.json` — today's picks
- `data/history.json` — all picks with results
