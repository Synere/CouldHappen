> Adapted from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8 (`nai5-reverse-prompt`: reverse.md).
> Copyright (C) 2026 Miint-Sunny
> SPDX-License-Identifier: GPL-3.0-only
> Modified for CouldHappen on 2026-11-16: rewritten for turning a portrait into a character's cast block and for checking a picture that drifted; shortened and reworded, CouldHappen's cast files and the story as a fourth source added. This page as a whole is under GPL-3.0-only; see [NOTICE.md](NOTICE.md) and [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt).

# Reverse prompting: from a picture to tags

Read this when a card supplies a portrait, when the first portrait of a cast member has been approved, or when a picture drifted and you need to see what it actually shows. It turns what you see in a picture into a cast block ([characters.md](characters.md)) or into a list of differences. [core.md](core.md) and [danbooru.md](danbooru.md) still apply.

## Mark where each detail came from

Keep the sources apart, in the block's `#` notes and in what you tell the Director:

- **Original prompt:** some pictures carry the prompt that made them in their metadata (a NovelAI PNG does). If there is one, say so and start from it, but keep only appearance and clothing; quality tags, UC and artist tags in it are not the character. Its artist tags can be offered to the Director for the story's style block, never applied on your own (`python tools/nai_tags.py --png <file>` lists them; see [core.md](core.md), "Choosing artist tags").
- **Seen:** what is plainly visible in the picture.
- **Inferred:** what you judged from the picture but could be wrong (an eye colour in shadow, a garment half hidden).
- **The story:** what the prose or card says. **The story wins** wherever it disagrees with the picture. Write the story's version into the block and tell the Director the picture differs.

Never present an inference as something seen.

## Scope

For a cast block, read only the person: build, species traits, hair, eyes, skin, marks, accessories, clothes. Leave out the pose, expression, camera, place and light; they belong to each picture, not to the character. To check a drifted picture, read everything the prompt asked for and list the differences.

## Look at the picture

1. **Sort what you see by where it goes.** Gender and stable appearance go on the block's first line; clothes and accessories on the second. In a full picture, the people count, held objects, pose, gaze, framing, place and light belong to the base prompt.
2. **Clothes from the outside in,** each garment with its colour, outline, material and visible state ([danbooru.md](danbooru.md), "Clothes"). Check clothing-state tags against the confusable table before you use one.
3. **Do not judge camera height from size alone.** A small, far figure is distance, not `from above`. Look for the tops or undersides of things and the horizon; if it is unclear, leave the camera out.
4. **Hidden or blurred parts stay unknown.** Write what you can confirm (an outline, a colour) and note the gap. Do not fill it in from what is usual.
5. **Check back** against the picture: every tag points to something visible, nothing in the block is pose or place, and every inferred detail is noted as inferred.

## What never comes from the picture

- **Who it is.** Do not recognise a known character from their looks. Use a canonical name only when the card or the Director says who it is; otherwise describe what is visible.
- **Who drew it.** Do not claim a picture was drawn by a given artist. Matching a reference's style with artist tags is a separate step with its own checks and the Director's choice ([core.md](core.md), "Choosing artist tags"); a cast block never carries artist tags, and the style stays the story's block in `notes/style.txt`.
- **Quality tags, UC and negative emphasis.** None of these describe the character.
- **Tagger output.** Do not treat an automatic tagger's guesses as fact.

## Turning a card portrait into a block

1. Read the card's text description first, then look at the portrait.
2. Write the block's two lines from what you see, marking each detail seen or inferred in notes, and the card's words beside them.
3. Where the card's text and its portrait disagree, the text is the story: follow it and tell the Director.
4. Make the first NovelAI portrait from the block and compare it with the card's portrait. Fix tags that missed (a wrong hair colour, a garment that changed shape), then save the block.

## A picture that drifted

When the picture check finds a difference, read the picture as above and write down what it shows against what the prompt asked: "asked `upper body`, shows full body sitting"; "asked `braid`, shows loose hair". Fix only those differences for the retry: one change per difference, the rest of the prompt and the cast blocks unchanged.
