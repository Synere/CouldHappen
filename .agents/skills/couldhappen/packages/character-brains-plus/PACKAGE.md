---
name: character-brains-plus
summary: Character brains with a script that builds every brief from a log, so a character is told only what they could know, by construction rather than by care.
couldhappen: 0.1.24
includes: method, tools/brains.py
requires: game-master with layers 1 to 4 on, Python 3, and a host that can start subagent sessions
touches: tools/brains.py, notes/brains/ (protocol, event log, generated views), game-master layers, START_HERE.md, notes/packages.md. No public file, helper or reader code changes.
cost: no money or keys. Each brain call is a subagent session of roughly 1,200 tokens in and 250 out; each turn adds one classification line per new game-master fact.
---

# Character brains plus

The same idea as [character-brains](../character-brains/PACKAGE.md): a recurring character gets a subagent brain that is briefed only with what they perceive, remember and want, and you still write every scene. The difference is how the brief is made. Here you never assemble it. A script, `tools/brains.py`, keeps an append-only log of what each character has seen, been told and kept, and it is the only way to build a brief. A fact that is not in the log for that character cannot reach their brain, however rich the scene would be with it.

## Which brain package to pick

- **character-brains** (method only): light stories, small casts, or a Director who wants no extra bookkeeping. What a character knows is your judgment on each call.
- **character-brains-plus**: stories built on secrets, lies and who-knows-what, where a leak would quietly flatten them. It costs one line of bookkeeping per new fact each turn.

The two cannot be installed together: both keep their files in `notes/brains/`. A story on the method-only package can move to this one: `migrate` moves its brain files into the log and keeps the originals in `notes/brains/legacy/`.

## What a player gets

- Characters who cannot know what they were never shown or told, because the brief is built from records, not memory.
- Knowledge with a history: how each character learned a thing, how sure they are, and what they have forgotten.
- Memories ranked by how much they matter, so the six a brain is given are the ones that count.
- Beliefs that can be wrong, a record of every lie, promise and threat a character made and to whom (with a warning when they contradict themselves to the same person), and what each character makes of the others: trust, fear, debt, and who they think knows what.
- A body and a mood that carry between scenes: pain, fear, fatigue and drink that ease with time, marks and clothes, and, where the story wants it, desire with limits the writer never crosses.
- Characters with aims of their own: standing wants, intentions they carry from scene to scene, and decisions to leave or refuse that the writer honours or records why not. If the Director wants it, one character a scene boundary also lives a little off-screen, and the player finds only the traces.

## How it fits game-master

It needs [game-master](../game-master/PACKAGE.md) with layers 1 to 4 on and reads its state by replaying game-master's own log; it never copies it.

- The character's card (`want`, `fear`, `secret`, `voice`, `attitude`) stays on their **layer 3 cast card**. The brain log keeps a snapshot only, to notice later when the card has moved on.
- Every game-master **fact** gets a brain visibility: `public` (anyone may know it), `witnessed`, `private` or `secret` (only the characters named as witnesses). A fact with no visibility is hidden from every brain. Game-master's `known` flag says what the *player* has seen and is never used here.
- A character's **threads** (layer 2) reach their brief only if they are on that character's list.

## Fidelity

As with the method-only package, the Director chooses how many characters keep a persistent brain and how many brain calls a turn may make. The defaults are three and two. Off-screen calls, one per scene boundary outside that budget, are off unless the Director turns them on.

## What it changes

`tools/brains.py`, a private protocol at `notes/brains/PROTOCOL.md`, the log `notes/brains/events.jsonl`, one generated view per character at `notes/brains/<npc id>.md`, and a section in `START_HERE.md`. It switches on any game-master layer from 2 to 4 that is off, after asking. Nothing public changes; the player sees only the story.

## Limits

A brain is a subagent session: it thinks only when called and ends with the host. It is a writing instrument, not a living consciousness, and you never tell the player otherwise. The script keeps what a brain is *told* honest; it cannot stop you from knowing too much when you play a character yourself, past the call budget. The protocol says what to do about that.

Apply it with [APPLY.md](APPLY.md).
