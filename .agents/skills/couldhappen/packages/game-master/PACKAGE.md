---
name: game-master
summary: Makes the writer run the story like an expert tabletop game master: continuity it can check, a world that moves on its own, and promises and secrets it does not forget.
couldhappen: 0.1.9
includes: method
requires: nothing
touches: tools/gm_state.py, notes/gm/ (private state and protocol), START_HERE.md, notes/packages.md. No public file, helper or reader code changes.
cost: none. No network, no keys. A little extra work each turn (about 800 to 1,200 tokens of state read, one small delta written).
---

# Game master

Prepare situations, not scripted plots. Track causes and consequences, not transcripts. Let the player's choices decide the outcome.

This package gives the writer a compact, private memory and a short routine to use it every turn. It is built in phases; each phase works on its own, and the Director can stop after any of them.

| Phase | Adds | Status |
| --- | --- | --- |
| 1 Continuity | The contract (genre, tone, limits, what the player wants), canon facts with a status and a source, the current situation, and a validated, append-only record of every change. | **Available** |
| 2 Memory | Open threads: promises, mysteries, consequences, relationships, callbacks, each with a lifecycle (open, active, dormant, resolved, discarded), optional due day, and soft warnings for overdue or forgotten ones. A `review` report for scene and chapter boundaries. | **Available** |
| 3 Living world | Pressures: factions, antagonists and NPCs with a goal, a next action, a trigger and an optional clock, which move only when time, events or the player justify it (an off-screen move must leave evidence). Compact cast cards (want, fear, secret, voice, attitude) shown for whoever is in the scene. | **Available** |
| 4 Discovery | Secrets kept apart from where they are found, with several routes to each required one. | Planned |
| 5 Narrative quality | Scene rhythm, callbacks, arc coherence, and soft warnings. | Planned |

## What a player gets

A story that remembers what is true, where it is, and what it promised; that does not silently turn rumours into facts; and whose writer can be checked by a script instead of trusted blindly.

## What it changes

Two new private places: `tools/gm_state.py` (stdlib only) and `notes/gm/` (state, protocol, the writer's session-zero notes). Nothing public changes. The player sees only the story, as before. A Director who wants to inspect the notes can ask the writer to show the current state (`python tools/gm_state.py hot`, or `state` for everything).

## How it stays honest

- Every change to the state cites the story or Director entry that justifies it. If the Director undoes story development, the changes that depended on the withdrawn entries are set aside (`reconcile`), not left to haunt the next session.
- The script checks what can be checked: ids, legal status changes, a reason for every promotion, replacement or retirement, time moving forward, banned terms, the existence of the cited entry, and that a promise is resolved with an outcome (fulfilled, broken or released) in an entry that comes after the one that made it. It does **not** judge meaning. Whether a passage contradicts canon, or makes a decision for the protagonist, stays a self-check by the writer (listed in the protocol). The package does not claim otherwise.

Apply it with [APPLY.md](APPLY.md).
