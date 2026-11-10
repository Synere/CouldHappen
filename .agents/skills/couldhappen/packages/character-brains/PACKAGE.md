---
name: character-brains
summary: Recurring characters get their own subagent brain that sees only what that character perceives, so they keep their own minds, secrets and voices across scenes.
couldhappen: 0.1.20
includes: method
requires: game-master with layers 1 to 4 on, and a host that can start subagent sessions
touches: notes/brains/ (private protocol and one file per character), game-master layers, START_HERE.md, notes/packages.md. No public file, helper or reader code changes.
cost: no money or keys. Each brain call is a subagent session of roughly 1,200 tokens in and 250 out, plus whatever a resumed session already carries; the Director sets how many calls a turn may make.
---

# Character brains

You play the whole cast, so every character knows what you know. A brain fixes that for the characters who matter: a subagent that is briefed only with what one character perceives, remembers and wants, and answers with what they notice, want, hide, say and do. You still write the scene. A brain is a source, not a script.

## What a player gets

- Characters who do not know things they were never told, and who act on their own secrets.
- People who sound like themselves and stay recognisable across scenes (it works with the [voice](../../references/voice.md) reference).
- Surprises: a brain may lie, withhold, misread or refuse, and you keep what the scene earns.

## How it fits game-master

It needs [game-master](../game-master/PACKAGE.md) with layers 1 to 4 on, and keeps no second set of records:

- A brain's sheet is the character's **layer 3 cast card** (`want`, `fear`, `secret`, `voice`, `attitude`), plus a `look` line in the brain file.
- What the character **may know** is limited by layer 1 facts and the **layer 4** hidden truths (facts with `"known": false`). The brain file lists the fact ids that character has learned, and the brief never carries any other hidden truth.
- Open **layer 2** threads that involve the character (a promise, a debt, a relationship) go into the brief as what they remember being owed.

## Fidelity

When it is applied, the Director chooses how closely characters are tracked: how many keep a **persistent** brain (a kept subagent session, resumed scene to scene) and how many brain calls a turn may make. The defaults are three persistent brains and two calls per turn. Fewer is cheaper and faster; more makes a larger cast feel alive. It can be changed at any time.

## What it changes

A private protocol at `notes/brains/PROTOCOL.md`, one file per tracked character in `notes/brains/`, and a section in `START_HERE.md`. It switches on any game-master layer from 2 to 4 that is off, after asking. Nothing public changes; the player sees only the story.

## Limits

A brain is a subagent session. It thinks only when called, holds nothing between calls except its own session history, and ends with the host. It is a writing instrument, not a living consciousness, and you never tell the player otherwise. A host that cannot start subagents cannot use this package; one that cannot resume sessions can use only one-call brains.

Apply it with [APPLY.md](APPLY.md).
