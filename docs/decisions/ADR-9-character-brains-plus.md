---
status: accepted
date: 2026-11-12
decision-makers: Project author
---

# ADR-9 — Add character-brains-plus, a scripted brain package

> In the context of the character-brains package, whose only gate on what a character knows is the writer's judgment and game-master's player-facing `known` flag, facing leaks that make scenes richer and so are never caught, we decided to keep the method-only package and add a second one, character-brains-plus, whose stdlib script `tools/brains.py` keeps an append-only brain event log and is the only way to build a brief, to achieve isolation by construction plus persistent per-character state for the stories that want it, accepting two packages to keep in step, one classification line per new fact, and a second store beside game-master.

## Context and Problem Statement

The package shipped by [ADR-7](ADR-7-character-brains-and-voice.md) is method only: four Markdown files and no code. The author has a live story using it and reports it works well. An external design brief (kept outside this repository) lists fourteen findings against it. The author accepted F1 to F13 on 2026-11-12 and deferred F14, the instruments:

* **F1, F2:** the brief carries "established facts they could know", judged by the writer on every call, and the only hard gate is `known: false`, which records what the *player* has seen, not what a character knows.
* **F3 to F6:** no provenance or confidence for what a character knows, no false beliefs, no model of what one character thinks another knows, no record of a character's lies and promises.
* **F7, F8:** no body, mood or desire state; an earlier install improvised mood numbers on every call.
* **F9:** the game-master card is re-shown each call and outlasts newer memory, so a character's arc reverts.
* **F10, F11:** no life between calls, and an answer block that cannot leave, refuse or commit to a later act.
* **F12:** past the per-turn call budget, the rest of the cast is played with full knowledge, and the protocol does not say so.
* **F13:** a Director Undo leaves brain memory that cites the withdrawn entry.

Most of these need structured state that a Markdown file and a prose rule cannot enforce.

## Considered Options

* Keep the package method only and tighten the protocol text.
* Replace the package with a script that keeps an append-only event log, mirroring game-master's `gm_state.py`.
* Keep the method-only package and add the script as a second package.
* Add brain fields to game-master's own state.

## Decision Outcome

Chosen option: **a second package**, selected by the project author on 2026-11-12. Only a builder that reads one store can keep a fact out of a brief by construction (F1), and an append-only log citing entries gives Undo (F13) and history for drift (F9) the same way game-master already does. But the method-only package works in a live story, costs no per-turn bookkeeping and suits light stories, so it stays, and the script ships beside it.

* `character-brains` stays method only. It takes the findings that need no script: the plain F12 text, a `DECIDES` answer key (F11), and an optional `desire` line in the brain file (F8).

* `character-brains-plus` installs `tools/brains.py`, Python stdlib only, same command style, exit codes and `--root` as `gm_state.py`.
* `notes/brains/events.jsonl` is the only source of truth. `notes/brains/<npc id>.md` becomes a generated view at the path the method-only package uses.
* Every game-master fact has a brain visibility class (`public`, `witnessed`, `private`, `secret`); no class means hidden from every brain. Game-master's `known` flag is never read to decide what a brief carries.
* The character's card (`want`, `fear`, `secret`, `voice`, `attitude`) stays in game-master. The log keeps a snapshot only to detect drift.
* F12 is handled in the protocol text only: it says plainly that a character played from the file knows too much. The script does not enforce the budget.
* F14 is deferred: no answer parser, audit command, cost ledger or built-in selftest yet. The repository's own tests still cover the script.
* The desire block (F8) ships without an age gate at first; the gate is its own ticket.
* The two packages cannot be installed together, since both write `notes/brains/`. Applying the plus package offers to migrate method-only brain files into the log.

The work is cut into tickets in the [character-brains-plus plan](../plans/character-brains-plus.md).

### Consequences

* Good, because what a brain may know is decided by recorded events, not by the writer's memory on each call.
* Good, because Undo, drift review and migration all work from one log.
* Good, because a story that does not want the bookkeeping keeps the light package.
* Bad, because two protocols repeat the brief's rules and must be kept in step.
* Bad, because the plus package is a script of game-master's order of size.
* Bad, because the writer classifies every new fact each turn, and a brain store now sits beside game-master, which ADR-7 avoided for the card. The card itself still lives only in game-master.
* Bad, because without F14's instruments a leak the builder lets through is still found only by reading.

### Confirmation

`tests/` covers the plus package's `brains.py`: a brief built from a fixture holds exactly the facts its visibility classes and `know` events allow, and none of game-master's other facts, whatever their `known` flag. `tests/test_skill_docs.py` passes with both packages in the pages the writer reads, and the method-only protocol has the `DECIDES` key and the F12 text.
