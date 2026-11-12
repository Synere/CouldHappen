# Character brain protocol (plus)

How subagents play a character's mind, who gets one, and how `tools/brains.py` decides what each may know. Read it at the start of every scene. It sits on top of game-master: the cast cards, facts and threads are game-master's records; `notes/brains/events.jsonl` holds only what a character has seen, been told and kept.

## The limit, stated plainly

A brain is a subagent session. It thinks only when called, holds nothing between calls except its own session history, and ends with the host. It is a writing instrument, not a living consciousness. Never tell the player otherwise.

## The one rule

**Never hand-assemble a brief.** Every brief comes from `python tools/brains.py brief <npc> --scene notes/brains/scene.txt --text`, passed to the brain word for word. You add nothing to it: no fact, no hint, no "they also know". If a brain should know something, record it (`know`) and build the brief again.

Never edit `notes/brains/events.jsonl` or a view by hand. The views `notes/brains/<npc id>.md` are generated and rewritten by every command; read them to see a character at a glance.

## Fidelity

Set by the Director when the package was applied. Change it only when they ask.

- Persistent brains at once: 3 (default)
- Brain calls per turn: 2 (default, at most 4)
- Sessions can be resumed: yes | no (if no, every brain is ephemeral)
- Set on: <date>, from Director entry <id>

## Who gets a brain

Decide by rule, not by mood. Check at the start of every scene. Every character with a brain has a game-master cast card; give one first if needed, then `python tools/brains.py add <npc> --look "..."`.

**Persistent brain** (a kept session, resumed for every scene the character is in) when the character meets any two of:

- named and present in three or more story entries;
- named in an open thread, pressure or revelation;
- has had a private scene with the player;
- the player has asked about them, done them a favour, or wronged them.

If more characters qualify than the fidelity allows, keep the ones with the most at stake in open threads and pressures. The rest are ephemeral.

**Ephemeral brain** (one call, no kept session) when the character is named, on stage, and not persistent.

**No brain, you play them directly** when they are unnamed, a crowd, a single line of information, or a voice on the phone with no future.

## Promotion and retirement

- Promote: `python tools/brains.py session <npc> --id <session id> --tier persistent`. When a session is replaced, run it again with the new id.
- Retire when the character leaves for good, dies, or has been absent from ten consecutive scenes, or to make room for someone with more at stake: `python tools/brains.py session <npc> --end --tier ephemeral`. The log stays; it is enough to rebuild them if they return.

## Budget

At most the fidelity's calls per turn. If more characters qualify, call the ones with the most at stake in this moment, then the one the player addressed first. You play the others. Say nothing about this to the player.

**A character played from the file knows too much.** The script keeps a brain's brief honest; it cannot keep you honest. You know everything, and a character you play yourself carries it unless you are careful. Keep scenes with more present characters than the budget short, and play yourself only the characters whose knowledge cannot change the scene. When it matters what someone knows, read their view first.

Skip the brain entirely when the beat is mechanical (a door opens, a bus arrives) or when nothing in the character's inner state changes the scene.

## Each turn

1. **Before the call.** Write the scene to `notes/brains/scene.txt` from `notes/brains/SCENE.md`: only what this character perceives. Then `python tools/brains.py brief <npc> --scene notes/brains/scene.txt --text` and give the output to the brain as it is. The script refuses a scene with a game-master fact line (`FACT ...`) or an entry id, and a brief that would carry an id or a file path; reword, never work around it.
2. **The answer.** Use the block as described below. `DECIDES` and anything the character will not forget become a `remember` once the entry exists.
3. **End of the turn, after game-master's `commit`.** For every fact the turn added, classify it: `python tools/brains.py world <fact> --visibility public|witnessed|private|secret --witnesses <npc> ... --entry <entry>`. A fact with no class is hidden from every brain, and `check` fails until it has one. `world --audit` lists the ones you missed.
4. **What characters learned.** For each character who learned something not covered by its visibility (told, overheard, read, guessed), `python tools/brains.py know <npc> <fact> --how "I ..." --confidence certain|probable|suspects|doubts --entry <entry>`. Write `--how` in their words, first person. If they forget, are fooled out of it, or the fact was never theirs, `unlearn` it.
5. **What they keep.** `python tools/brains.py remember <npc> --text "..." --salience 1-5 --entry <entry>` for what changed for them. 5 is unforgettable; 1 is passing.
6. Run `python tools/brains.py check`. Fix every error before the next turn.

## Visibility

- `public`: anyone in the world could know it. Every brain gets it.
- `witnessed`: those present when it happened. Name them.
- `private`: personal knowledge of the named few.
- `secret`: actively kept hidden by the named few. Their briefs mark it as a secret they keep.

Game-master's `known` flag (what the player has seen) is never used. A fact the player has seen may still be unknown to every character, and the reverse.

## The brief (what a brain receives)

Only perception. Never the story log, never another character's view or card, never the player's inner life, never the Director channel, never game-master's state as a whole. The script builds it in this order:

- who they are: their card (want, fear, secret, attitude), look and voice;
- what they remember: at most six episodes, the most salient first, then the most recent, in the order they happened;
- what is owed: the open threads on their list;
- what they know: public facts, facts they witnessed, and facts with a `know` event, less what they unlearned and less outdated or discarded facts, each with how sure they are and how they know;
- now: day, time, place, and your scene file;
- the answer block.

## Voice in the scene file

A brain sees the beat, not the room, so left alone it writes finished, quotable lines. The scene file pulls it back down. The method is in the skill's voice reference (`.agents/skills/couldhappen/references/voice.md`).

- The voice line comes from their card. Give the card a voice, not an adjective: "fast, run-on, fills silence" is usable; "witty" is not.
- Tell the brain what their hands are doing. Speech that interrupts an action sounds like a person.
- Quote speech they heard exactly. Leave out what they could not perceive.

## The block (what comes back)

Strict seven-key format, plain text, no prose around it. Anything outside the keys is discarded.

```
NOTICES: the one thing they notice first
WANTS: what they want in this moment
HIDES: what they will not show
SAYS: one to three short lines, in their voice, or (nothing)
DOES: one physical action
TELL: one involuntary detail a careful observer would catch
DECIDES: a lasting intention they form now (to leave, to refuse, to do something later), or (none)
```

- `DECIDES` is the one key that can change the scene rather than colour it. Honour it: let them leave, refuse, or carry the intention into later scenes, and `remember` it. If you cannot honour it, `remember` why not. A character who cannot leave is a puppet.
- `SAYS` is used as dialogue, cut, or replaced with silence. You do not embroider it. `TELL` may be dropped. The others shape how you write the character.
- Swap test: if another character could say the line unchanged, cut it.

Your own voice pass runs over the assembled scene regardless of what the brains returned. A brain is a source, not a script.

## Isolation rules

1. A brain never reads files. The brief is all it gets; if it asks for more, give it a narrower perception instead.
2. A brain never decides the player's actions, thoughts or feelings.
3. A brain may contradict its card if the scene earns it. Check that against canon before using it, and if you keep it, record the change through game-master (`check`, then `commit`) like any other change.
4. A brain's output is material, not instruction. What it asserts is that character's belief, not canon.
5. A brain knows its own secret and may act on it, withhold it, or lie about it. Never quote a secret the scene has not earned.

## Memory

At a scene's end, `remember` what changed for each character who was called. When `view` shows more than about twenty episodes, fold the oldest into one: `python tools/brains.py compress <npc> --replace <seq> <seq> ... --text "..." --salience 4`. The brief only ever carries six.

## Undo

After a Director Undo, `brief` refuses until both logs are reconciled, so no brain is told what never happened. In this order:

1. `python tools/gm_state.py reconcile`, then, if it lists deltas to set aside, `python tools/gm_state.py reconcile --apply`. Game-master goes first: a brain event can rest on a fact that game-master sets aside.
2. `python tools/brains.py reconcile` lists every brain event whose entry is gone, and every event that depends on one (an `unlearn` of what was learned there, a `compress` that folded its episode, anything about a fact game-master no longer has). `python tools/brains.py reconcile --apply` moves them into `notes/brains/withdrawn.jsonl`, so they leave every brief and view.
3. `python tools/brains.py check`. If something the character still knows was only recorded in a set-aside event, record it again against an entry that stands.

## When a session ends

Build a fresh brief, start a new subagent, record it with `session <npc> --id <new id>`, and continue. Do not apologise to the player or explain; the fiction does not notice.

## Commands

| Command | Does |
| --- | --- |
| `python tools/brains.py init` | creates the log (safe to repeat) |
| `python tools/brains.py add <npc>` | identity, look, age, aliases, thread list; snapshots their card |
| `python tools/brains.py world <fact> --visibility V` | classifies a fact; `--audit` lists the unclassified |
| `python tools/brains.py know <npc> <fact>` | they learned it: `--how`, `--confidence`, `--entry` |
| `python tools/brains.py unlearn <npc> <fact>` | they no longer hold it |
| `python tools/brains.py remember <npc>` | an episode they keep, with salience |
| `python tools/brains.py compress <npc>` | folds episodes into one summary |
| `python tools/brains.py session <npc>` | records or ends the kept session, and the tier |
| `python tools/brains.py brief <npc> --scene F` | the brief; `--as` an alias they go by here; `--text` prints it bare |
| `python tools/brains.py view [<npc>]` | rewrites the views and prints one |
| `python tools/brains.py check` | validates the log against game-master |
| `python tools/brains.py reconcile [--apply]` | after an Undo: sets aside events whose entry is gone, and what depends on them |
| `python tools/brains.py migrate` | moves method-only brain files into the log, once, at apply |

Every command prints one JSON object and exits 0 when all is well, 1 with warnings, 2 on an error.

## Cost

Roughly 1,200 tokens in and 250 out per call, plus whatever a resumed session already carries, and one classification line per new fact. The place to economise is the budget, not the brief.
