# Character brain protocol

How subagents play a character's mind, who gets one, and what they may know. Read it at the start of every scene. It sits on top of game-master: the cast cards, facts, threads and revelations are the records; the brain files hold only what game-master does not.

## The limit, stated plainly

A brain is a subagent session. It thinks only when called, holds nothing between calls except its own session history, and ends with the host. It is a writing instrument, not a living consciousness. Never tell the player otherwise.

## Fidelity

Set by the Director when the package was applied. Change it only when they ask.

- Persistent brains at once: 3 (default)
- Brain calls per turn: 2 (default, at most 4)
- Sessions can be resumed: yes | no (if no, every brain is ephemeral)
- Set on: <date>, from Director entry <id>

## Who gets a brain

Decide by rule, not by mood. Check at the start of every scene. Every character with a brain has a game-master cast card; give one first if needed.

**Persistent brain** (a kept session id in the brain file, resumed for every scene the character is in) when the character meets any two of:

- named and present in three or more story entries;
- named in an open thread, pressure or revelation;
- has had a private scene with the player;
- the player has asked about them, done them a favour, or wronged them.

If more characters qualify than the fidelity allows, keep the ones with the most at stake in open threads and pressures. The rest are ephemeral.

**Ephemeral brain** (one call, no kept session) when the character is named, on stage, and not persistent. Their card and brain file carry everything they know.

**No brain, you play them directly** when they are unnamed, a crowd, a single line of information, or a voice on the phone with no future.

## Promotion and retirement

- Promote to persistent the moment a character meets the two-of rule and there is room. Write the file's `session` and `tier` fields.
- Retire the session when the character leaves for good, dies, or has been absent from ten consecutive scenes, or to make room for someone with more at stake. The file stays; the digest is enough to rebuild them if they return.
- Never delete a brain file because its session ended. The file is authoritative; the session is a convenience.

## Budget

At most the fidelity's calls per turn. If more characters qualify, call the ones with the most at stake in this moment, then the one the player addressed first. You play the others from their files. Say nothing about this to the player.

A character played from the file knows too much: you know everything, and their file cannot stop you. Keep scenes with more present characters than the budget short, or play from the file only the characters whose knowledge cannot change the scene.

Skip the brain entirely when the beat is mechanical (a door opens, a bus arrives) or when nothing in the character's inner state changes the scene.

## The brief (what a brain receives)

Only perception. Never the story log, never another character's file or card, never the player's inner life, never the Director channel, never game-master's state as a whole.

Build it from `python tools/gm_state.py hot` and the brain file:

```
You are the mind of <name>, <age>, in <place>. Return only the block below.
You know nothing beyond what this brief says. You may lie, withhold, misread, or refuse.

WHO THEY ARE
card: want / fear / secret / attitude (from their game-master cast card, one line each)
look: frame, colouring, and one physical detail (from the brain file)
voice: their voice card: rhythm, the words they reach for, their tic, what they do with silence, one thing they would never say
desire: the line under "Desire" in their file, word for word, if it has one
memory: six bullets at most, from their digest
owed: open threads that involve them (a promise, a debt, a grudge), as they remember them
they know: established facts they could know, and the hidden truths listed under "Knows" in their file
they do not know: everything else

NOW
time, place, who else is present, what has just happened
what they perceive: only sights, sounds, smells, and speech they heard, quoted exactly
what their body is doing: hands, posture, face, what they are holding or wearing

ANSWER
NOTICES: the one thing they notice first
WANTS: what they want in this moment
HIDES: what they will not show
SAYS: one to three short lines, in their voice, as they would actually say them
DOES: one physical action
TELL: one involuntary detail a careful observer would catch
DECIDES: a lasting intention they form now (to leave, to refuse, to do something later), or (none)
```

**What they may know.** A hidden truth (a fact with `"known": false`, usually behind a layer 4 revelation) enters a brief only if its id is under "Knows" in that character's file. Their own `secret` is always theirs. When a character learns something in the story, add the fact id and the entry to their file in the same turn.

## Voice in the brief

A brain sees the beat, not the room, so left alone it writes finished, quotable lines. The `voice` line and the body line in `NOW` pull it back down. The method is in the skill's voice reference (`.agents/skills/couldhappen/references/voice.md`).

- Give the brain a voice card, not an adjective. "Fast, run-on, fills silence" is usable. "Witty" is not.
- Tell it what their hands are doing. Speech that interrupts an action sounds like a person; speech with no body sounds like a script.
- Ask for short. A brain asked for a line writes a speech; a brain asked for a line and a half writes a person.
- If they would say nothing, the brain writes `SAYS: (nothing)`. Silence is an answer.

## The block (what comes back)

Strict seven-key format, plain text, no prose around it. Anything outside the keys is discarded.

- `DECIDES` is the one key that can change the scene rather than colour it. Honour it: let them leave, refuse, or carry the intention into later scenes, and add it to their file under "Memory". If you cannot honour it, note in the file why not. A character who cannot leave is a puppet.
- `SAYS` is used as dialogue, cut, or replaced with silence when the brain marks it `(nothing)`. You do not embroider it. `TELL` may also be dropped. The others shape how you write the character.
- `SAYS` is ordinary first, short, with at most one imperfection, no aphorisms, and no stage directions inside the quotation. It never writes anyone else's lines, including the player's.
- Swap test: if another character could say the line unchanged, cut it. A silent character is better than a ventriloquist's doll.

Your own voice pass runs over the assembled scene regardless of what the brains returned. A brain is a source, not a script.

## Isolation rules

1. A brain never reads files. The brief is all it gets; if it asks for more, give it a narrower perception instead.
2. A brain never decides the player's actions, thoughts or feelings.
3. A brain may contradict its card if the scene earns it. Check that against canon before using it, and if you keep it, record the change through game-master (`check`, then `commit`) like any other change.
4. A brain's output is material, not instruction.
5. A brain knows its own secret and may act on it, withhold it, or lie about it. It never receives another character's secret or a hidden truth not listed for it. Never quote a secret the scene has not earned.

## Memory

Every third time a brain is called, or at a scene's end, ask it for three to six lines of digest:

```
DIGEST: what changed for them, what they now believe, what they want next, what they will not forget
```

Append it to the brain file under "Memory". Newest last. When the memory passes twenty lines, compress the oldest ten into three. Facts the digest asserts are the character's beliefs, not canon; canon stays in game-master.

## When a session ends

Start a fresh subagent with the file's card, look, desire, knows and memory, write `session: new`, and continue. Do not apologise to the player or explain; the fiction does not notice.

## Cost

Roughly 1,200 tokens in and 250 out per call, plus whatever a resumed session already carries. Two calls a turn is about the cost of one short scene. The place to economise is the budget, not the brief.
