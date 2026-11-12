# Applying character-brains-plus

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first.

## 0. What to tell the Director

Before you change anything, say in a few sentences:

- Recurring characters get a subagent brain, and a script builds each brain's brief from a log of what that character has seen and been told. You still write every scene.
- It needs game-master with layers 1 to 4 on. Name any layer that is off now, and what turning it on adds to each turn's bookkeeping.
- Cost: no money or keys. Each brain call is a subagent session (about 1,200 tokens in, 250 out), and each turn you record who can know each new fact. Nothing public changes and no restart is needed.
- If the story only wants characters with their own minds and not the bookkeeping, the lighter [character-brains](../character-brains/PACKAGE.md) package does that.

Then ask the **fidelity** questions, two at a time, with the defaults as suggestions:

1. **How many characters keep a persistent brain** at once? Default 3.
2. **How many brain calls may a turn make?** Default 2, at most 4. Characters past the budget are played by you, from their views.
3. **Off-screen calls?** Default off. When on, at each scene boundary one character away from the player gets one extra brain call (outside the budget) to say what they did meanwhile; the player sees only the trace it leaves, never the scene. It costs one call per boundary.

If the Director says "you decide", propose numbers for this story's cast and wait for a yes. Do not install anything until they answer.

## 1. Check the prerequisites

1. **Method-only brains.** If `notes/brains/` holds brain files from the method-only character-brains package (a hand-written file with an `npc:` line), the two packages cannot run side by side, and every `brains.py` command except `migrate` refuses while those files are there. Offer the Director two choices: keep the method-only package, or move its brains into the log (install step 2). Moving keeps every memory, and copies each file to `notes/brains/legacy/` first.
2. **game-master.** `tools/gm_state.py` and `notes/gm/` exist. If not, the Director must agree to game-master first; apply it with its own `APPLY.md`.
3. **Layers.** Run `python tools/gm_state.py layers`. Turn on any of 2, 3 and 4 that is off with `python tools/gm_state.py layers --on 2 3 4`, then follow step 3 of game-master's APPLY.md ("Switching on a further layer") for each one you turned on.
4. **Python.** `python tools/gm_state.py hot` runs. `brains.py` uses the same Python and the standard library only.
5. **Subagents.** Confirm from your own tools that you can start a subagent session with a brief and read its answer, and whether you can resume one later by id. If you cannot start one, stop and tell the Director the package cannot run here. If you cannot resume, every brain is ephemeral; say so, and record it.

## 2. Install

1. Copy [files/brains.py](files/brains.py) to `tools/brains.py`, beside `tools/gm_state.py`, and run `python tools/brains.py init`, unless you are moving method-only brains (next step).
2. **Only when moving method-only brains** (prerequisite 1), run `python tools/brains.py migrate` in place of `init`. It copies each file to `notes/brains/legacy/`, then records the character, their session and tier, and every memory line (each digest as one summary) against the last story entry (`--entry E` for another), and replaces the file with its generated view. It makes a `know` only from a `## Knows` line that names a fact id, and never guesses one: read its warnings, and for each fact a character holds that the old file did not name by id, record `know` in step 6. A `## Desire` line or a `## Sheet` stays in the legacy copy only; record a desire line yourself with `python tools/brains.py state <npc> --set desire.limits=... desire.wants=... --entry E`, limits first. The next two steps replace the old protocol and template.
3. Copy [files/PROTOCOL.md](files/PROTOCOL.md) to `notes/brains/PROTOCOL.md`. Fill its "Fidelity" section with the Director's answers and the date, and note whether sessions can be resumed. If the Director wants off-screen calls, run `python tools/brains.py settings --offscreen on`; they stay off otherwise.
4. Copy [files/scene-template.md](files/scene-template.md) to `notes/brains/SCENE.md` and [files/brain-template.md](files/brain-template.md) to `notes/brains/TEMPLATE.md`. Neither is a character.
5. **Classify the facts game-master already holds.** Run `python tools/brains.py world --audit`, and for each fact it lists run `python tools/brains.py world <fact> --visibility public|witnessed|private|secret [--witnesses <npc> ...]`. Ask of each: who in the fiction could know this? When in doubt, choose the narrower class; a brain can learn a fact later, but cannot unsee it.
6. **Add the characters who already qualify** under the protocol's "Who gets a brain". Each needs a layer 3 cast card first. Then `python tools/brains.py add <npc> --look "..." [--age N] [--alias ...] [--threads T1 ...] [--baseline valence=N energy=N ...]`, a `know` for each hidden truth they have learned (with the entry where they learned it), and a first `remember` from the story so far.
7. Run `python tools/brains.py check`. It must pass.

Private notes under `notes/` need no pause. Nothing here touches public files.

## 3. Record

1. Add a "Character brains" section to `START_HERE.md`: what the package is, that each turn follows `notes/brains/PROTOCOL.md`, that briefs come only from `python tools/brains.py brief`, the fidelity numbers, and that `notes/brains/<npc id>.md` are generated views, never edited.
2. Add the package to `notes/packages.md`: name, version, date, the fidelity answers, whether sessions can be resumed, and any game-master layer you turned on.
3. Commit.

## 4. Report

Tell the Director in plain language what now happens each turn, who has a brain now, and what you could not check (for example, that resuming a session was not tested yet). Then start a fresh standing wait.

## Changing fidelity later

When the Director asks, update the "Fidelity" section of `notes/brains/PROTOCOL.md` and the line in `notes/packages.md`. Off-screen calls go on or off with `python tools/brains.py settings --offscreen on|off`. Lowering the number of persistent brains retires the sessions with the least at stake (`python tools/brains.py session <npc> --end --tier ephemeral`); their logs stay.

## What this package does not do

It does not create characters, write the story, or decide anything for the player. It does not change game-master's records or rules; a brain's answer that would change canon is checked by you and recorded through game-master like anything else.
