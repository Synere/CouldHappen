---
name: rpg-mechanics
summary: Fair, visible dice with rules designed for this story's setting, plus an optional character sheet panel in the reader.
couldhappen: 0.1.7
includes: method
requires: nothing
touches: tools/roll.py, notes/rules.md (private); optionally public/sheet.json, helpers/files.py, helpers/bridge.py, web/src (the Cast panel), docs/public-contract.md, START_HERE.md
cost: none. No network, no keys.
---

# RPG mechanics

Gives the story honest, crunchy mechanics. Every uncertain outcome is rolled with a real random source and shown in the prose (dice, modifiers, total, difficulty). The rules are designed from this story's fiction rather than copied from any game. Optionally, the character's current state (health, resources, gear, skills, recent rolls) is shown in a sheet panel beside the story.

What a player gets: visible rolls they can trust, consequences that follow, progression, and (with the sheet) an at-a-glance status.

What it changes: a new script and a private rules note. The sheet is optional; it changes helper and reader code, so it needs a helper restart and a Vite restart.

Apply it with [APPLY.md](APPLY.md). Part 3 (the sheet panel) is also used by [scene-images](../scene-images/PACKAGE.md) for themes and quick actions.
