# Applying game-master

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first. Tell the Director in a sentence or two what you will add: a private state script, a short routine each turn, and a session-zero conversation. Say what it costs (a little extra work per turn, no money, no keys) and that it changes no public file, so no restart is needed.

This package is built in phases. This file covers **Phase 1, Continuity**. If later phases have been added to the package folder, apply them one at a time, each only after the previous one has been used in play, and each with the Director's go-ahead.

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

## 5. Verify and report

1. `python tools/gm_state.py hot` prints a compact context of roughly 1,000 tokens or less. If it is longer, you tagged or pinned too much; trim.
2. Make a deliberately bad delta in a scratch file (for example, an established fact with its text edited) and confirm `check --file` rejects it. Delete the scratch file.
3. Run `python -m unittest discover -s tests -p "test_*.py"`.
4. Commit the notes and tool. Start a fresh standing wait.

Report briefly to the Director what now works, which rules the script enforces (structure, status changes, reasons, time order, banned terms, cited entry exists), and which it cannot (contradiction of canon, unauthorised protagonist decisions, prose matching state). Those stay with you as self-checks.
