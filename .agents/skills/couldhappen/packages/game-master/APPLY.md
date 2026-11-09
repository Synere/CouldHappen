# Applying game-master

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first.

## 0. What to tell the Director

When the Director asks for the package, say plainly, in a few sentences and before you change anything:

- It is five **layers**, each building on the one below and each switchable on or off **at any time**: 1 continuity (what is true), 2 memory (promises and open questions), 3 living world (factions that act on their own, cast cards), 4 discovery (hidden truths with several ways to find them), 5 pacing (scene rhythm and quality warnings).
- Layer 1 is the foundation. Switching on any layer also switches on layer 1.
- More layers means more bookkeeping each turn. A light start is fine: say what you would pick for this story and why (for example 1 and 2 for a slow character piece, 1 to 4 for a mystery), and let them decide. "All of them" is a valid answer.
- Cost: no money, no keys, a little extra work per turn. It changes no public file, so no restart is needed.

Then ask which layers they want on. Do not install anything until they answer. If they say "you decide", propose a set and wait for a yes.

Throughout, use the usual workspace rules: pause before appending to public logs, validate and release, record where a fresh session finds it from `START_HERE.md`, commit, and keep a standing wait running after every turn. Private notes under `notes/` need no pause. On Windows set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` when generating entries and avoid non-ASCII characters in heredocs.

## 1. Install (once)

1. Copy [files/gm_state.py](files/gm_state.py) to `tools/gm_state.py` (create `tools/` if needed).
2. Run `python tools/gm_state.py init`, then set the layers the Director chose: `python tools/gm_state.py layers --on 2 3` (and `--off` for any you do not want; with no `layers.json` all five are on, so always set it). `python tools/gm_state.py layers` shows the state.
3. Copy [files/protocol.md](files/protocol.md) to `notes/gm/protocol.md`. Read the opening, "Each turn", and the sections for the layers that are on. Follow only those; a layer that is off is not yours to maintain, and the script refuses its records.

## 2. Layer 1, continuity: session zero (always)

Ask in Director, briefly and in plain language. Offer your own suggestions drawn from the story so far so the Director can just say yes. Two or three questions at a time is plenty.

- **Genre and tone.** What kind of story is this, and how should it feel (grim, wry, tender, tense)?
- **Boundaries.** Anything to avoid, soften, or only hint at? Any literal words or topics that must never appear (these become `banned_terms`)?
- **Promises.** What does the story promise to deliver (mystery solved, slow-burn romance, earned victories, real danger)?
- **What the player wants.** The protagonist's goals, loyalties, flaws, or hooks you should keep feeding back to them (`wants`).

Do not guess boundaries. If the story already has a clear voice and the Director says "you decide," propose a contract and ask them to confirm it. Mark the entry `addressed` and wait; the contract is written when they answer, so this spans at least two turns.

Then write the contract as the first delta, citing the Director entry in which they answered:

```json
{"entry": "<director entry id>", "why": "Director answered session zero",
 "ops": [{"op": "set", "kind": "contract", "fields":
   {"genre": "...", "tone": "...", "boundaries": ["..."], "banned_terms": [], "promises": ["..."], "wants": ["..."]}}]}
```

Write it to `notes/gm/pending.json`, then `check` and `commit`. Revisit the contract only when the Director's preferences change.

If the story is already underway, seed the state: the current situation and at most about twenty facts that would hurt if contradicted, citing the entry where each became true (a writer entry for events, a Director entry for what they told you). Mark `established` only what the fiction has actually shown; mark what characters merely say or believe `rumour` and your own unshown ideas `provisional`. Tag every fact with the names and places it concerns. Set `known` to false for anything the protagonist has not learned, including every provisional idea. Do it in two or three deltas, not one.

## 3. Switching on a further layer

Do this whenever the Director asks, at any point in the story, or when you have proposed it and they said yes. Run `python tools/gm_state.py layers --on N`, refresh `tools/gm_state.py` and `notes/gm/protocol.md` from `files/` if your copies are older (the log format never changes), read that layer's section of the protocol, then do its setup:

- **Layer 2, memory.** Open threads for the promises, mysteries and consequences the story has already taken on (at most about ten; the ones that would hurt if forgotten). Cite the entry where each began; give promises with a clear deadline a `due_day`. From then on `touch` threads that advance and run `review` at chapter or session boundaries.
- **Layer 3, living world.** Design the opposition with the story's tone in mind: two to four pressures (goal, next action, trigger, and where a deadline helps a clock and consequence), preferring one that already threatens something the player cares about. Add cast cards for the three to six recurring characters, one short phrase per field; leave a field out until the fiction supplies it. At every scene boundary ask "who wants something and is not getting it?", and run `review` before narrating a time skip.
- **Layer 4, discovery.** List the truths the player must learn. Add each as a hidden fact (`known: false`) and a `required` revelation with three routes of different kinds. The fact may start `provisional` while you are still deciding, but it must be `established` before (or in the same delta as) the reveal. Add optional truths only if they are worth the bookkeeping. When the player surprises you, check the routes first; when one is lost, `block` it and add another.
- **Layer 5, pacing.** Open a scene for the current moment (mode, agenda, exit condition, `serves`); you do not need to backfill past scenes. From then on close and open scenes as the story moves and run `boundary` at each boundary. Treat its warnings as advice, never as orders.

Say in one line what you switched on and what you will now do differently.

## 4. Switching a layer off

Run `python tools/gm_state.py layers --off N` when the Director asks, or when you judge a layer is costing more than it gives (and tell them). The layer's records stay in the log but disappear from `hot`, warnings and `state`, and the script refuses new ones; switching it on again restores them exactly. You stop maintaining that layer. Layer 1 cannot be switched off.

## 5. Record it

1. Add or update a short "Game master" section in `START_HERE.md`: what the package is, which layers are on (`python tools/gm_state.py layers`), that every turn follows `notes/gm/protocol.md`, the commands (`hot`, `check`, `commit`, `schema`, `boundary`, `review`, `reconcile`, `layers`), and that meaning-level checks are yours.
2. Record the package in `notes/packages.md` (name, version, date, layers on, changes to the layer set with dates). A fresh session reads this before proposing anything.
3. After a Director Undo, run `reconcile`, then `reconcile --apply`, as part of the "Reconcile" step of the Undo procedure (`references/recovery.md`), before the next turn. Note that in `notes/packages.md` so a fresh session does it too.

## 6. Verify and report

1. `python tools/gm_state.py hot` prints a compact context of roughly 1,000 tokens or less, and its first line lists the layers on. If it is longer, you tagged or pinned too much; trim.
2. Make a deliberately bad delta in a scratch file (for example, an established fact with its text edited) and confirm `check --file` rejects it. Delete the scratch file.
3. Run `python -m unittest discover -s tests -p "test_*.py"`.
4. Commit the notes and tool. Start a fresh standing wait.

Report briefly to the Director what now works, which rules the script enforces (structure, status changes, reasons, time order, banned terms, cited entry exists, and for the layers on their own rules), and which it cannot (contradiction of canon, unauthorised protagonist decisions, prose matching state, whether a clue or off-screen move actually reached the page). Those stay with you as self-checks.
