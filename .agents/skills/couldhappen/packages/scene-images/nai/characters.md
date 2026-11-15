> Adapted from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8 (`nai5-writing`: illustration.md; `nai5-costume-writing`: costume.md; `oc-character-design`: character.md).
> Copyright (C) 2026 Miint-Sunny
> SPDX-License-Identifier: GPL-3.0-only
> Modified for CouldHappen on 2026-11-16: rewritten as a guide for turning a story's description of a person into a fixed NovelAI appearance block; sections chosen, shortened and reworded, CouldHappen's cast files added. This page as a whole is under GPL-3.0-only; see [NOTICE.md](NOTICE.md) and [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt).

# Characters: one look, every picture

Read this when a cast member is drawn for the first time, when a portrait is asked for, and when the story changes how someone looks. [core.md](core.md) and [danbooru.md](danbooru.md) still apply.

NovelAI V5 takes no reference pictures, so a character looks the same from picture to picture only if their appearance tags are the same every time. Each cast member drawn in a picture gets a **cast block**, `notes/prompts/cast/<cast id>.txt`, and every picture uses it unchanged.

## The cast block

```text
# Whisper (cast id whisper). Story: "silver-grey braid", "eyes like rain", wiry, scar on left hand.
# Chosen 2026-11-16: grey eyes (the story gives no colour), fair skin.
girl, long hair, grey hair, braid, grey eyes, fair skin, slender, scar on hand,
dark green cloak, hood down, leather vest, white shirt, brown pants, boots,
```

- **First line of tags:** `girl`, `boy` or `other` (no number), then the stable appearance: build, species traits, hair length, colour and style, eyes, skin, marks and the accessories that make them recognisable.
- **Second line:** the clothes they usually wear, outermost first, each colour next to its garment.
- **Notes** (lines starting with `#`, never sent): where each detail came from, and every detail you chose because the prose left it open.
- In a picture, use the header `[Character N = <cast id>]`: the script puts the block's tags into that field, so they cannot drift. Add lines under the header only for what this moment changes (a different outfit replaces the clothing line; see below).

## From the story's words to the block

1. **Collect what the story says.** Read the character's card, their cast entry and every description of them so far. Quote the words in a note.
2. **Translate each one into Danbooru tags** ([danbooru.md](danbooru.md)): "silver-grey braid" is `grey hair, braid`; "wiry" is `slender`; "pointed ears" is `pointy ears`. Keep every detail that identifies them, even if the block gets long: dropping one to save space changes who they look like.
3. **Choose what the picture needs and the prose leaves open,** such as eye colour or hair length, once. Choose something that fits the story's tone and what is said. Record each choice in a note, so it never changes from picture to picture. Tell the Director what you chose when you show the first portrait; they may correct it.
4. **Do not invent identity.** No extra scars, colours or accessories just to make them distinctive; no organs a species name does not show in the story.
5. **Judge by silhouette.** A character is recognised first by shape: build, hair outline, clothes' outline, a non-human structure. Make sure those are in the block before the small details.

## A known character

If a cast member is a character from an existing work, start their block with the gender and their canonical Danbooru name (`girl, archetto (arknights)`); the name brings their usual look. Add only what the story specifies, item by item, with its colour and position. A story that says only "in a swimsuit" adds `swimsuit`, not a collar or ribbons you guessed. Never put the name in the base prompt.

## Clothes from the card or the prose

A card's outfit text or a costume the prose describes becomes the clothing line:

- **Each garment once,** as one phrase that defines it: `dark purple knee boots with low silver heels`, not `knee boots` plus a sentence repeating them.
- **From the main noun outward:** what it is, its outline, structure, material, decoration, how it is worn.
- **In wearing order:** head and neck, upper body, waist, lower body, legs and feet, accessories.
- **Sentences only for relationships** (layers, one-sided states, a carried prop), with the garment as subject: `A long scarf is wrapped twice around her neck,`. Never "She wears...".
- **Only what shows.** How it fastens or what is underneath stays out unless it is visible.

A change of clothes for one scene replaces the clothing line in that picture only: write the new clothes under the header; the appearance line stays the block's. A lasting change (a new uniform, a cut braid) updates the block, with a dated note.

## When the story changes their look

The prose wins. If the story gives a detail that differs from the block (a scar gained, hair cut, a colour the story finally names), update the block at once, note the date and the entry, and tell the Director that earlier pictures show the old look. Never keep a chosen detail that the story has since contradicted.

## Portraits

A "Make portrait" request (APPLY part 4) uses the block unchanged, `--size portrait`, a plain background so the likeness carries over, and framing from the head and shoulders to the waist: `1girl, solo, portrait, looking at viewer, simple background,` or `upper body`. `visual novel sprite` and `transparent background` give a cutout figure if the reader shows portraits that way. The first portrait you and the Director approve is the reference for the look: if the block was written from words, check the portrait against it and fix the block where the picture got something better or the story agrees with the picture. If a card supplies a portrait, write the block from it with [reverse.md](reverse.md) first.

## The check

For every picture with cast members, the picture check in APPLY part 3 adds one question: **does each character still match their cast block?** Hair, eyes, build, the identifying marks and the clothes. If one drifted, retry with the field written out in full under a plain `[Character N]` header in that picture's file, the missed tag weighted (`1.2::braid::`) or moved earlier; do not rewrite the description, and leave the block itself unchanged unless the story says otherwise.
