# Applying game-master

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first. Tell the Director in a sentence or two what you will add: a private state script, a short routine each turn, and a session-zero conversation. Say what it costs (a little extra work per turn, no money, no keys) and that it changes no public file, so no restart is needed.

This package is built in phases. This file covers **Phase 1, Continuity** (sections 1 to 4), **Phase 2, Memory** (section 5) **Phase 3, Living world** (section 6) and **Phase 4, Discovery** (section 7); section 8 verifies whichever you applied. If later phases have been added to the package folder, apply them one at a time, each only after the previous one has been used in play, and each with the Director's go-ahead.

Use the usual workspace rules: pause before appending to public logs, validate and release, record where a fresh session finds it from `START_HERE.md`, commit, and keep a standing wait running after every turn. Private notes under `notes/` need no pause. On Windows set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` when generating entries and avoid non-ASCII characters in heredocs.

## 1. Install

1. Copy [files/gm_state.py](files/gm_state.py) to `tools/gm_state.py` (create `tools/` if needed).
2. Run `python tools/gm_state.py init`. It creates `notes/gm/deltas.jsonl` and `notes/gm/withdrawn.jsonl`.
3. Copy [files/protocol.md](files/protocol.md) to `notes/gm/protocol.md`. Read it in full; you will follow it every turn.

## 2. Session zero (with the Director)

Ask in Director, briefly and in plain language. Offer your own suggestions drawn from the story so far so the Director can just say yes. Do not turn it into a questionnaire; two or three questions at a time is plenty.

- **Genre and tone.** What kind of story is this, and how should it feel (grim, wry, tender, tense)?
- **Boundaries.** Anything to avoid, soften, or only hint at? Any literal words or topics that must never appear (these become `banned_terms`)?
- **Promises.** What does the story promise to deliver (mystery solved, slow-burn romance, earned victories, real danger)?
- **What the player wants.** The protagonist's goals, loyalties, flaws, or hooks you should keep feeding back to them (`wants`).

Do not guess boundaries. If the story already has a clear voice and the Director says "you decide," propose a contract and ask them to confirm it.

Then write the contract as the first delta, citing the Director entry in which they answered:

```json
{"entry": "<director entry id>", "why": "Director answered session zero",
 "ops": [{"op": "set", "kind": "contract", "fields":
   {"genre": "...", "tone": "...", "boundaries": ["..."], "banned_terms": [], "promises": ["..."], "wants": ["..."]}}]}
```

Write it to `notes/gm/pending.json`, then `check` and `commit`. Revisit the contract only when the Director's preferences change.

## 3. Seed the state if the story is already underway

Read the story and your notes. Add only what the next scenes need: the current situation, and at most about twenty facts that would hurt if contradicted. Cite the entry where each became true (a writer entry for events, a Director entry for what they told you). Mark `established` only what the fiction has actually shown. Mark what characters merely say or believe `rumour`, and your own unshown ideas `provisional`. Tag every fact with the names and places it concerns. Do the seed in two or three deltas, not one.

Set `known` to false for anything the protagonist has not learned. That is what keeps a secret out of the player's view later.

## 4. Wire it into play

1. Add a short "Game master" section to `START_HERE.md`: what the package is, that every turn follows `notes/gm/protocol.md`, the commands (`hot`, `check`, `commit`, `reconcile`), and that Phase 1 does not enforce meaning-level checks.
2. Record the package in `notes/packages.md` (name, version, date, phase applied, what you chose not to do).
3. From now on follow the protocol each turn. After a Director Undo, run `reconcile`, then `reconcile --apply`, as part of the "Reconcile" step of the Undo procedure (`references/recovery.md`), before the next turn. Note that in `notes/packages.md` so a fresh session does it too.

## 5. Phase 2: memory (threads)

Apply this once Phase 1 has been in use and the Director agrees. It needs no new files: the script you installed already includes threads and `review`. If you installed an older copy of `tools/gm_state.py`, replace it with [files/gm_state.py](files/gm_state.py) (the log format is unchanged, so existing state keeps replaying) and refresh `notes/gm/protocol.md` from [files/protocol.md](files/protocol.md).

1. Read the "Threads" section of the protocol.
2. Backfill: open threads for the promises, mysteries and consequences the story has already taken on (at most about ten; the ones that would hurt if forgotten). Cite the entry where each began. Give promises with a clear deadline a `due_day`.
3. From now on, at each scene boundary, `touch` the threads that advanced, and at each chapter or session boundary run `review` and retire what has run its course.
4. Update the "Game master" section of `START_HERE.md` and the entry in `notes/packages.md` (phase 2 applied, date).
5. Verify: `python tools/gm_state.py hot` shows the threads under the contract and situation; `review` runs.

## 6. Phase 3: living world (pressures and cast)

Apply this after Phase 2 has been used in play and the Director agrees. Again no new files: replace `tools/gm_state.py` and `notes/gm/protocol.md` with the current copies from [files/](files/) if yours are older (the log format is unchanged).

1. Read the "Pressures and cast" section of the protocol.
2. Design the opposition with the Director's tone in mind. Add two to four pressures: the actors who want something the protagonist touches. For each give a goal, a next action, a trigger, and (where a deadline helps) a clock and a consequence. Prefer one pressure that already threatens something the player cares about (see the contract's `wants`) over several distant ones.
3. Add cast cards for the three to six recurring characters, one short phrase per field. Do not invent secrets just to fill the field; leave it out until the fiction supplies one.
4. Add the rule to your routine: at every scene boundary, ask "who wants something and is not getting it?" and advance a pressure only with a basis and a reason. Run `review` before narrating a time skip.
5. Update the "Game master" section of `START_HERE.md` and `notes/packages.md` (phase 3 applied, date).

## 7. Phase 4: discovery (revelations)

Apply this after Phase 3 has been used in play and the Director agrees. No new files: refresh `tools/gm_state.py` and `notes/gm/protocol.md` from [files/](files/) if yours are older (the log format is unchanged).

1. Read the "Revelations" section of the protocol.
2. List the truths the story needs the player to learn (a culprit, a location, a motive). Add each as a hidden fact (`known: false`) and a `required` revelation with three routes of different kinds. Add optional truths only if they are worth the bookkeeping.
3. Do not invent routes that depend on events you have not yet decided; a route can be as small as a phrase.
4. From now on: when the player surprises you, check the routes before improvising; when a route is lost, `block` it and add another; when the player learns something, `clue` or `reveal` in the same delta as the scene that shows it.
5. Update the "Game master" section of `START_HERE.md` and `notes/packages.md` (phase 4 applied, date).

## 8. Verify and report

1. `python tools/gm_state.py hot` prints a compact context of roughly 1,000 tokens or less. If it is longer, you tagged or pinned too much; trim.
2. Make a deliberately bad delta in a scratch file (for example, an established fact with its text edited) and confirm `check --file` rejects it. Delete the scratch file.
3. Run `python -m unittest discover -s tests -p "test_*.py"`.
4. Commit the notes and tool. Start a fresh standing wait.

Report briefly to the Director what now works, which rules the script enforces (structure, status changes, reasons, time order, banned terms, cited entry exists), and which it cannot (contradiction of canon, unauthorised protagonist decisions, prose matching state). Those stay with you as self-checks.
