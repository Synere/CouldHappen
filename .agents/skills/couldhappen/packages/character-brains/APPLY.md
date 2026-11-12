# Applying character-brains

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first.

## 0. What to tell the Director

Before you change anything, say in a few sentences:

- Recurring characters get a subagent brain that sees only what that character perceives. You still write every scene.
- It needs game-master with layers 1 to 4 on. Name any layer that is off now, and what turning it on adds to each turn's bookkeeping.
- Cost: no money or keys. Each brain call is a subagent session (about 1,200 tokens in, 250 out). Nothing public changes and no restart is needed.

Then ask the **fidelity** questions, two at a time, with the defaults as suggestions:

1. **How many characters keep a persistent brain** at once? Default 3. A persistent brain is a kept subagent session, resumed in every scene the character is in.
2. **How many brain calls may a turn make?** Default 2, at most 4. Characters past the budget are still played, by you, from their files.

If the Director says "you decide", propose numbers for this story's cast and wait for a yes. Do not install anything until they answer.

## 1. Check the prerequisites

1. **Not the plus package.** If `notes/brains/events.jsonl` exists, this story uses [character-brains-plus](../character-brains-plus/PACKAGE.md). Stop: the two cannot be installed together. Tell the Director, and do not write brain files beside its log.
2. **game-master.** `tools/gm_state.py` and `notes/gm/` exist. If not, the Director must agree to game-master first; apply it with its own `APPLY.md`.
3. **Layers.** Run `python tools/gm_state.py layers`. Turn on any of 2, 3 and 4 that is off with `python tools/gm_state.py layers --on 2 3 4`, then follow step 3 of game-master's APPLY.md ("Switching on a further layer") for each one you turned on.
4. **Subagents.** Confirm from your own tools that you can start a subagent session with a brief and read its answer, and whether you can resume one later by id. If you cannot start one, stop and tell the Director the package cannot run here. If you cannot resume, every brain is ephemeral (one call, no kept session); say so, and record it.

## 2. Install

1. Copy [files/PROTOCOL.md](files/PROTOCOL.md) to `notes/brains/PROTOCOL.md`. Fill its "Fidelity" section with the Director's answers and the date, and note whether sessions can be resumed.
2. Copy [files/brain-template.md](files/brain-template.md) to `notes/brains/TEMPLATE.md`. It is a template, not a character.
3. For each recurring character who already qualifies under the protocol's "Who gets a brain", make sure they have a layer 3 cast card, then copy the template to `notes/brains/<npc id>.md` and fill it: `look`, a `desire` line if the story calls for one, the fact ids they know, and a first memory from the story so far. Do not start sessions yet; the first scene they are in does that.

Private notes under `notes/` need no pause. Nothing here touches public files.

## 3. Record

1. Add a "Character brains" section to `START_HERE.md`: what the package is, that each turn follows `notes/brains/PROTOCOL.md`, the fidelity numbers, and where the brain files are.
2. Add the package to `notes/packages.md`: name, version, date, the fidelity answers, whether sessions can be resumed, and any game-master layer you turned on.
3. Commit.

## 4. Report

Tell the Director in plain language what now happens each turn, who has a brain now, and what you could not check (for example, that resuming a session was not tested yet). Then start a fresh standing wait.

## Changing fidelity later

When the Director asks, update the "Fidelity" section of `notes/brains/PROTOCOL.md` and the line in `notes/packages.md`. Lowering the number of persistent brains retires the sessions with the least at stake; their files stay.

## What this package does not do

It does not create characters, write the story, or decide anything for the player. It does not change game-master's records or rules; a brain's answer that would change canon is checked by you and recorded through game-master like anything else.
