> Adapted from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8 (`nai5-writing`: illustration.md and conventions.md; `nai5-illustration-composition`: composition.md).
> Copyright (C) 2026 Miint-Sunny
> SPDX-License-Identifier: GPL-3.0-only
> Modified for CouldHappen on 2026-11-16: rewritten as a guide for showing the story's place and moment in a NovelAI V5 picture; sections chosen, shortened and reworded, CouldHappen's character positions added. This page as a whole is under GPL-3.0-only; see [NOTICE.md](NOTICE.md) and [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt).

# Scenes: the place and the moment

Read this for a new location, a wide shot, or more than one person in frame. [core.md](core.md) and [danbooru.md](danbooru.md) still apply. The prose has already chosen the moment; this page is about showing it, not about finding a more dramatic one.

## What must be seen first

Ask what the moment is about: a face, a handover, a room, two people's distance. Choose the framing so that part fits, then everything else supports it.

- **Framing from the parts that must show** ([danbooru.md](danbooru.md), "Framing and camera"). A handover needs both hands in frame; a duel at a distance needs `full body` or `wide shot`.
- **Orientation:** `--size portrait` for one person, `--size landscape` for a place or a group, `--size square` when neither fits.
- **Camera height and direction only when the prose implies them:** "she looked up at the tower" suggests `from below`; "from the gallery, he saw the hall" suggests `from above`. Plain eye level needs no tag.
- If the parts the prose requires cannot all fit, change the framing, never drop a required part silently.

## Space in sentences

Tags list what is there; sentences place it. Use present tense, one function per sentence, and identify people by their position or a short visible anchor, never by name or "Character 1".

- **Who is in front, who behind, who owns what:** `The girl with a short black bob stands on the left beneath a red safelight, The girl with a long braid stands farther back on the right beside an enlarger, The umbrella belongs only to the girl with the braid,`. Ownership sentences are the main way to stop props and colours moving from one person to another.
- **Do not guess who does what.** If the prose does not say who holds the lantern, write only what it does say (`each traveller carries their own pack,`), not an invented assignment.
- **Depth:** compare near and far in one sentence: `One hand reaches toward the viewer, very close, while the rest of her recedes into the corridor,`.
- **How much of the frame something fills** is a sentence, not a tag: `The burning ship fills the right half of the frame, small figures watch from the dock on the left,`.
- **Action in progress:** a tag says `running`; a sentence says the moment: `She is caught mid-stride, her cloak and hair streaming behind her,`.
- **Light:** say where it comes from, what it falls on and where the shadow goes, and a second light if the prose has one: `The red safelight fills the room, and a thin strip of neutral light enters beneath the closed door,`. Pair it with a light tag (`backlighting`, `candlelight`); check the result, since direction sentences sometimes come out reversed.
- **Objects that must be there:** list them as tags or in one sentence, and ask that they stay distinct: `The workbench holds separate jars, a brass scale, a mortar and a cracked lantern, each clearly recognisable,`.

Each contact follows from the action: who reaches for what, which hand holds, what bears the weight. Write the contact the prose gives, not more.

## Where each person stands: positions

V5 can place each character on the canvas. When the prose places people ("she waits at the door on the left; he sits by the fire on the right"), give each `[Character N]` header a position: x from 0 (left edge) to 1 (right edge), y from 0 (top) to 1 (bottom).

```text
[Character 1 @ 0.25,0.6]
girl, long hair, red hair,
grey coat,
[Character 2 = brann @ 0.75,0.55]
```

- Give every character a position or none. With positions, the script sends them and turns on NovelAI's position setting; without them, NovelAI places people itself.
- Number people from the viewer's left, as always, and keep the numbers in the base prompt's `Character N:` lines.
- Position only sets where a person is in the frame. y is not depth: a lower point tends to read as nearer, a higher one as farther, but say depth in a sentence too ("the boy with the bicycle is far up the street, small in the frame").
- Points too close together cause swapped looks and merged people; keep them apart unless the prose puts people together.
- Leave positions out when the prose does not place people.

## Complexity, and places with nobody in them

`low/medium/high/ultra complexity` sets how much detail V5 spends ([core.md](core.md), "V5 switches"). Add it only when the prose describes a detailed or a stark scene:

- A crowded market, a cluttered workshop, a library described shelf by shelf: `high complexity`, with `detailed background`.
- An empty plain, a bare cell, fog: `low complexity` only if the style block suits a simplified look; otherwise describe the emptiness.
- `ultra complexity` restyles the picture; try it only after high was not enough.

For a place with nobody in it, start with `no humans`, write no character fields, and consider `visual novel bg` with `high complexity` and `depthness`. For a story-event picture with people, `visual novel cg` gives the event-illustration look. Both are untested in the reader; check the first result.

## Backgrounds

Describe the place the prose gives rather than leaving the background empty. `simple background` or `white background` only for a portrait. `depth of field` or `blurry background` blurs the far plane; do not use them when the far plane holds something the prose needs. If one layer should be soft, say which.

## The check

To the picture check in APPLY part 3 add: are people where the prose puts them (left and right, near and far)? Does each prop belong to the right person? Is the light from where the prose says?
