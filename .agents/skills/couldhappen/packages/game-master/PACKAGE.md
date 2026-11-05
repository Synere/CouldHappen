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

This package gives the writer a compact, private memory and a short routine to use it every turn. It is five layers, each building on the one below. The Director chooses which are on, and can switch any of them on or off at any time (`python tools/gm_state.py layers`). Layer 1 is the foundation and is always on; layers 2 to 5 each need only layer 1. A layer that is off is invisible and the script refuses its records, so switching it back on restores exactly what was recorded. More layers means more bookkeeping each turn, so a light start is fine.

| Layer | Adds | Status |
| --- | --- | --- |
| 1 Continuity | The contract (genre, tone, limits, what the player wants), canon facts with a status and a source, the current situation, and a validated, append-only record of every change. | **Available** |
| 2 Memory | Open threads: promises, mysteries, consequences, relationships, callbacks, each with a lifecycle (open, active, dormant, resolved, discarded), optional due day, and soft warnings for overdue or forgotten ones. A `review` report for scene and chapter boundaries. | **Available** |
| 3 Living world | Pressures: factions, antagonists and NPCs with a goal, a next action, a trigger and an optional clock, which move only when time, events or the player justify it (an off-screen move must leave evidence). Compact cast cards (want, fear, secret, voice, attitude) shown for whoever is in the scene. | **Available** |
| 4 Discovery | Hidden truths kept apart from where they are found, each with several routes (aim for three for anything the story needs the player to learn). Routes can be used, blocked or added as the player surprises you, and a truth only becomes known when the story shows how. A required truth with no open route is flagged as a dead end. | **Available** |
| 5 Narrative quality | A scene record (mode, agenda, tension, exit condition, what it serves), a scene-boundary checklist, and soft warnings about pacing: the same mode four times, a scene whose purpose is done, three scenes that serve nothing the protagonist wants. | **Available** |

## What a player gets

A story that remembers what is true, where it is, and what it promised; that does not silently turn rumours into facts; and whose writer can be checked by a script instead of trusted blindly.

## What it changes

Two new private places: `tools/gm_state.py` (stdlib only) and `notes/gm/` (state, protocol, the writer's session-zero notes). Nothing public changes. The player sees only the story, as before. A Director who wants to inspect the notes can ask the writer to show the current state (`python tools/gm_state.py hot`, or `state` for everything).

## How it stays honest

- Every change to the state cites the story or Director entry that justifies it. If the Director undoes story development, the changes that depended on the withdrawn entries are set aside (`reconcile`), not left to haunt the next session.
- The script checks what can be checked: ids, legal status changes, a reason for every promotion, replacement or retirement, time moving forward, banned terms, the existence of the cited entry, and that a promise is resolved with an outcome (fulfilled, broken or released) in an entry that comes after the one that made it. It does **not** judge meaning. Whether a passage contradicts canon, or makes a decision for the protagonist, stays a self-check by the writer (listed in the protocol). The package does not claim otherwise.

Apply it with [APPLY.md](APPLY.md).
