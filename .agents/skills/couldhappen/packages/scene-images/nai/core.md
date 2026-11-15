> Adapted from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8 (`nai5-writing`: conventions.md and illustration.md).
> Copyright (C) 2026 Miint-Sunny
> SPDX-License-Identifier: GPL-3.0-only
> Modified for CouldHappen on 2026-11-16: rewritten as a guide for turning a story's prose into a NovelAI V5 prompt file; sections chosen, shortened and reworded, CouldHappen's quality and UC defaults added. This page as a whole is under GPL-3.0-only; see [NOTICE.md](NOTICE.md) and [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt).

# NovelAI prompts: the core

Read this and [danbooru.md](danbooru.md) before every NovelAI picture. They tell you how to write the prompt file that `tools/scene_image_nai.py` sends. The other pages in this folder cover characters, scenes and reverse prompting; read them when the moment needs them.

## Your job: translate, do not design

The story has already decided the moment: who is there, what they look like, what they hold, where they are, the light. Your job is to recreate that moment faithfully in NovelAI's terms, not to compose a better picture.

- **Danbooru tags wherever a tag exists.** People, counts, body, hair, clothes, clothing state, pose, expression, framing, camera height, light and place are canonical Danbooru tags. Check any tag you are not sure of ([danbooru.md](danbooru.md)).
- **Sentences only where tags cannot say it.** Tags list objects and their attributes; sentences connect them: who holds or touches what, who is in front of whom, where each person is looking, how much of the frame something fills.
- **Nothing the prose does not support.** No props, people, clothes or mood the story did not give.
- **Fix what the prose leaves open.** When the picture needs a detail the prose never states, such as hair colour, choose it once, record it in the character's appearance tags, and never let it vary from picture to picture.
- **Follow the story when they differ.** The prose wins over recorded appearance tags or a supplied portrait. Tell the Director about the difference.

## The fields

A V5 prompt has three parts. The prompt file holds the first two; the script adds the third.

| Field | What goes in it |
| --- | --- |
| **Base prompt** | The number of people, objects, action, expression, gaze, framing, camera, place, time, light, relationship sentences, the style block. With two or more people, each person's action, expression and gaze go on their own `Character N:` line at the end. Never appearance or clothes. |
| **Character fields** | One per person in frame, even for a single person: `girl`, `boy` or `other` first (no number), then appearance on one line and clothing on the next. Never action, expression, gaze, camera or place. |
| **Undesired content (UC)** | Added by the script: NovelAI's Heavy V5 UC, with `nsfw` first only when `notes/style.txt` has the line `nsfw: no`. You do not write it. |

Appearance in both fields is the most common mistake:

- Wrong: base `1girl, solo, silver hair, ahoge, white dress, from below` and Character 1 `girl, silver hair, ahoge, white dress`.
- Right: base `1girl, solo, from below, snowy plains, backlighting, looking at viewer,` and Character 1 `girl, silver hair, long hair, ahoge,` / `white dress, frills, white gloves,`.

## The prompt file

```text
<people count>, <held objects, things leaned on, things that block the view>,
<pose, expression, gaze: one person only>, <framing and camera>, <place, time, light>,
<relationship sentences>,
<technique words this picture really needs>,
<negative-emphasis line for this picture's exclusions, if any>,

Character 1: girl, <action, pose, expression, gaze>,
Character 2: boy, <action, pose, expression, gaze>,

<the style block from notes/style.txt, word for word>

[Character 1]
girl, <appearance>,
<clothing and accessories>,
[Character 2]
boy, <appearance>,
<clothing and accessories>,
```

- **Order in the base prompt:** people count, objects, pose and expression and gaze, framing and camera, place and time and light, relationship sentences, technique, exclusions. The people count is always first and appears once.
- **One person:** no `Character 1:` line in the base prompt; their pose, expression and gaze go on the second line. They still get a `[Character 1]` field.
- **Two or more people:** no action, pose, expression or gaze tags in the first lines (`hug`, `sitting`, `smile`, `looking at another`), or the model cannot tell who does what. After a blank line, one `Character N:` line per person, gender first. Number people from the viewer's left, `Character 1` leftmost, and use the same numbers for the `[Character N]` fields.
- **Relationship sentences:** one or two simple English sentences. First who is on the left and who on the right, then who does what to whom, with the contact and holding the prose gives. Identify people by a short visible anchor ("the girl with headphones"), never "Character 1" and never the full appearance list.
- **Commas:** end every base and character line with a comma, and end sentences with a comma instead of a full stop. Leave the style block exactly as written.
- **Blank lines** separate sections. Do not use `|` for that.
- **Notes:** lines starting with `#` are yours and are not sent. Use them for where a chosen detail came from.
- **Length** follows the picture. Every tag should solve a visible problem; do not stack synonyms. V5 Full reads about 1,500 tokens.

## Interactions between people

When one person acts on another, mark the direction on each person's `Character N:` line with the same action tag:

- `source#hug` on the one who does it, `target#hug` on the one it is done to.
- `mutual#holding hands`, `mutual#eye contact` when both do the same thing to each other.
- No prefix for what a person does alone, and none when people are not interacting.

Only these three prefixes exist; `female#hug` or `char1#hug` do nothing. Put a prefix only on a real action tag; when no tag exists, describe the action in the relationship sentence. One person can carry both directions:

```text
Character 1: girl, source#headpat,
Character 2: girl, target#headpat, source#hug,
Character 3: boy, target#hug,
```

`target#` sets direction, not energy: the one carried in `target#piggyback` can be the one pointing and shouting. When people look at each other, write `looking at another` on each line and put a height difference in a sentence ("the standing girl looks down at the squatting one"). If the result swaps who does what, check the prefixes first, then move each person's action line into the end of their own `[Character N]` field (`looking at target` there, instead of `looking at another`).

## Quality tags and undesired content

The script appends the Standard quality tags, `very aesthetic, masterpiece, no text`, and sends the Heavy V5 UC. Do not write either in the prompt file; they would be added twice.

- **Text in the picture** (a sign, a letter, a speech bubble): `no text` and `logo` would suppress it. Run the script with `--text`, put the wording in double quotes, and say what it is written on and where: `A wooden sign above the door reads "Closed",`. Do not put quotes around anything that should not be drawn.
- **Excluding one thing from this picture:** use negative emphasis on the last content line of the base prompt, before the `Character N:` lines, never the UC: `-1.5::umbrella::,`. Use it only for an exclusion the prose demands or a fix for something an earlier try got wrong, never to list opposites by habit. Deepen to `-3` if `-1` is not enough.
- **Conceptual inversion:** `-1::simple background::` for an empty white background the prose did not want; `-1::monochrome::` for colour that came out washed out.
- **NSFW:** never ask. If the Director says they do not want NSFW pictures, add the line `nsfw: no` to `notes/style.txt`.
- **Multiple views, a reference sheet, deliberate blank space or a logo as the subject** conflict with the Heavy UC. The script cannot change the preset; tell the Director instead of hoping.

## Weights

| Syntax | Effect |
| --- | --- |
| `1.2::tag::` | Stronger, up to the closing `::` |
| `0.5::tag::` | Weaker (0 to 1) |
| `-2::tag::` | Removes or inverts (above) |

New tags are unweighted. Add a weight only when a tried picture shows a tag being ignored, and change one thing at a time. Without a closing `::` a weight runs to the end of the prompt. A tag ending in a number before `::` is read as a weight: write `artist153, ::`, not `artist153::`.

## The style block

One story keeps one art style through a fixed block in `notes/style.txt`: tags for the medium and technique (`watercolor (medium)`, `anime coloring`, `flat color`, `sketch`) and any NovelAI artist tags the Director gives, kept exactly as given, with their order, weights, spaces and years. Paste it unchanged after a blank line, after the `Character N:` lines and before the `[Character 1]` field. Never add, reorder or reweight it for one picture. If the Director changes it, change the file, not one prompt.

## V5 switches

These are tags that act as switches, never quality boosters. Add one only when the picture calls for it.

- **Complexity** sets how much visual detail V5 spends on the picture. It is not steps (how many sampling passes) and not size (the canvas). Leave it out by default.
  - `low complexity`: very little detail, a noticeably simplified, stylised look. Only when the prose describes a stark or minimal moment and the style suits it.
  - `medium complexity`: a modest amount of detail.
  - `high complexity`: dense detail, for a busy place the prose describes in detail (a market, a cluttered workshop), often with `vn bg` and `depthness`.
  - `ultra complexity`: the most detail; restyles the picture noticeably.

  Too much makes results stiff or repetitive, and low and ultra change the look, so check the first picture with it against the style block.
- **Visual novel tags:** `visual novel sprite` for a cast portrait, `visual novel cg` for a story-event picture, `visual novel bg` (`vn bg`) for a place with nobody in it, `visual novel art` for the overall style. Untested in the reader; check the result.
- **Transparency:** `transparent background` for a cutout portrait; `alpha transparency` for effects that should be see-through in the file (magic, flame); `has alpha` after light or particle tags. For a see-through object inside a full scene, describe it instead (`transparent umbrella`).
- `depthness` deepens shadows. `attractive male` is a V5 tag for a handsome man.
- Do not use era tags (`meta:golden era`) or `res_mult`.

## When a picture comes back wrong

Check the prompt file against the prose first; do not change the moment to make it easier to draw.

| Symptom | Try |
| --- | --- |
| Wrong framing (`upper body` gave a full-length picture) | Make sure only one framing tag is there and nothing else asks for legs or feet; add a sentence about what the frame shows. |
| Tag ignored | Move it forward, split it into separate tags, weight it slightly, or say it in a sentence. |
| Someone else's hair or clothes on a person | Appearance only in `[Character N]` fields, not in the base; anchors in sentences; check the people count is written once. |
| Who does what is swapped | Check `source#`/`target#`; describe by appearance, not number; move action lines into the fields. |
| Low camera did not happen | `from below`, and check no other framing tag fights it. |
| Socks, gloves or clothes changed shape | A clothing-state tag means something else ([danbooru.md](danbooru.md)); say the state in a sentence. |
| Backlit face too dark | Only if the prose allows it: `front lighting`, or `-2::backlighting::`. |
| Empty white background | Describe the place the prose gives; `-1::simple background::` only if needed. |
| Text missing | `--text`, quotes, and the surface the text is on. |
| Whole picture turned to noise | A number right before `::` was read as a weight. |

## Final checks before you run the script

- The moment matches the prose: the people, what they hold, the place, the light. Nothing added.
- The people count is first and written once; `solo` only for one person and no animals; `girl`/`boy` without numbers in the fields.
- Every person in frame has a `[Character N]` field with gender, appearance and clothing only, the same appearance tags as their earlier pictures.
- With two or more people: no action tags in the first lines, one `Character N:` line each, prefixes on interactions, a short left-to-right sentence.
- Framing, gaze and pose tags do not contradict each other ([danbooru.md](danbooru.md), "Contradictions").
- Every tag you were unsure of has been checked; clothing-state tags against the confusable table.
- No quality tags and no UC in the file; the style block pasted unchanged; `--text` only with quoted text.
- Exclusions as negative emphasis on the last content line, only when needed.

After the picture comes back, run the picture check in APPLY part 3.
