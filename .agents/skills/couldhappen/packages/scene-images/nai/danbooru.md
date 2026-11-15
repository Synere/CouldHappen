> Adapted from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8 (`nai5-writing`: illustration.md and sources.md; `nai5-costume-writing`: costume.md).
> Copyright (C) 2026 Miint-Sunny
> SPDX-License-Identifier: GPL-3.0-only
> Modified for CouldHappen on 2026-11-16: rewritten as a tag reference for turning story prose into a NovelAI V5 prompt; sections chosen, shortened and reworded, CouldHappen's tag helper and its rules added. This page as a whole is under GPL-3.0-only; see [NOTICE.md](NOTICE.md) and [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt).

# Danbooru tags for story pictures

Read this with [core.md](core.md) before every NovelAI picture. NovelAI V5 learned from Danbooru-tagged pictures, so a canonical tag moves the picture far more reliably than a phrase you made up.

## Finding the right tag

Use four sources, in this order:

1. **What you know.** You know the common tags. You go wrong in three ways: invented tags (`black long hair` instead of `long hair, black hair`), similar-looking tags that mean something else (`loose socks` are baggy socks, not slipped ones), and rare tags that barely move the picture.
2. **This page:** the tags story pictures usually need, and the confusable table below.
3. **The tag helper**, for any tag you are not sure exists: `python tools/nai_tags.py "socks rolled" "upper bo"`. It asks NovelAI's own tag suggester, so its counts show what the model learned, not raw Danbooru. Only a suggestion that starts with your query confirms a tag; the helper hides the rest. Counts top out at 10000, which only means "common". An exact match with a count of a few hundred or more is safe to use; no match, or a count in the tens, means describing that detail in a sentence instead. For example, `socks rolled down` has a count of 28: write "her socks have slipped down to her ankles" instead.
4. **The Danbooru wiki, for meaning.** The helper says a tag exists, not what it means. When meaning matters, as with clothing state or `X focus` tags, read the tag's wiki page: `https://danbooru.donmai.us/wiki_pages/<tag_with_underscores>` (the [Safebooru mirror](https://safebooru.donmai.us/wiki_pages/help%3Aapi) shows only safe pictures). Check the tag is a general tag, not an alias or deprecated.

Match in this order: the exact canonical tag, the canonical tag behind an alias, a broader stable tag, then a plain sentence. Never invent an underscore tag and treat it as checked.

## Spelling

- Write tags with spaces, as NovelAI shows them: `long hair`, not `long_hair`.
- Keep the words in Danbooru's order: `white thighhighs`, `hand on another's head`.
- Names of known characters and works are ASCII only, spelled exactly, family name first as Danbooru has it (`hanami saki`), with the work in ordinary brackets: `archetto (arknights)`. An alternate outfit goes inside the brackets before the work. Transliterate accents (ō to ou). Never glue name and work into one word (`archetto_arknights`).
- A named character goes in their `[Character N]` field after the gender word, `girl, archetto (arknights)`, never in the base prompt. The name brings their usual look; add only what the story changes.

## People and subjects

`1girl` `2girls` `1boy` `2boys` `1girl, 1boy` `1other` `multiple girls` `no humans`

- The count appears once, first in the base prompt. Fields say `girl`, `boy` or `other` without numbers.
- `solo` only for one person with no animals. With an animal, keep `1girl` and name the animal (`black cat`). With several people where one is the focus, `2girls, solo focus`; never `solo` with more than one person.
- `other` is for a person of unknown or no gender, or a non-human.

## Body and species

Write species traits as tags, not sentences: `cat ears` `fox ears` `rabbit ears` `pointy ears` `elf` `horns` `cat tail` `fox tail` `wings` `fang`. Body: `tall`, `petite`, `muscular`, `mature female`, `old man`, `freckles`, `scar on face`, `dark skin`, `pale skin`. Do not add organs a species name does not show in the story.

## Hair and eyes

Length, then colour, then style, as separate tags: `long hair, black hair, ponytail`; `short hair, white hair, messy hair`; `medium hair, brown hair, braid, hair over one eye, ahoge`. Eyes: `green eyes`, `heterochromia`, `closed eyes`. Accessories: `hair ribbon`, `hairclip`, `glasses`.

## Clothes

Choose words from the main garment outward: what it is, its outline, its structure, material, decoration, then how it is worn.

- **What:** `dress`, `shirt`, `jacket`, `coat`, `skirt`, `pants`, `boots`, `kimono`, `armor`. Dress, gown, robe and kimono are not interchangeable.
- **Outline:** `long dress`, `cropped jacket`, `oversized shirt`, `high-waist skirt`.
- **Structure:** `collared shirt`, `sailor collar`, `pleated skirt`, `hood`, `long sleeves`, `sleeveless`.
- **Material:** `leather jacket`, `denim`, `knit sweater`, `satin`. Sheer, translucent and transparent are different; say which layer.
- **Decoration:** `lace trim`, `embroidery`, `frills`, `print`.
- **How it is worn:** `open jacket`, `unbuttoned`, `sleeves rolled up`, `hood up`.

Keep each colour next to its garment, `navy jacket, ivory blouse, burgundy ribbon`, not a list of colours apart from a list of clothes. Define each garment once. Use a sentence, with the garment as its subject, for layers, one-sided or asymmetric states and anything without a tag: `One sleeve has slipped off her shoulder.` Never "She wears..." in a field. A vague direction from the prose ("in a swimsuit") becomes `swimsuit`, not invented details.

## Clothing state: check before you use

Some Danbooru tags name a kind of garment and others a way of wearing one. They look alike, and the wrong one silently changes the clothes.

| Tag | What it really means | Often mistaken for |
| --- | --- | --- |
| `loose socks` | baggy, thick slouch socks (a kind of sock) | socks that slipped down |
| `single thighhigh` | only one stocking worn, the other leg bare | one stocking slipped down |
| `uneven legwear` | each leg's legwear differs | a reliable way to show one slipped stocking |
| `asymmetrical legwear` | the two legs' legwear differ | a specific state |
| `thighhighs pull` | the act of pulling a stocking | a stocking that has slipped |

So `white thighhighs, loose socks` meant as "white stockings slipping down" gives thick slouch socks. Write the garment as a tag and the state as a sentence: `white thighhighs, uneven legwear,` then `One thighhigh has slipped down to bunch just below the knee,`.

## Pose

`standing` `sitting` `kneeling` `squatting` `lying` `on back` `on side` `on stomach` `sitting sideways` `crossed legs` `knees up` `hugging own legs` `leg up` `arm support` `head rest` `hand on own cheek` `arms up` `walking` `running` `leaning forward` `leaning on wall`

Use tags for the position; add a sentence for which hand rests where or which way the body turns. With two or more people, poses go on each `Character N:` line.

## Expression and gaze

Expression: `smile` `light smile` `grin` `smirk` `frown` `open mouth` `closed mouth` `blush` `tears` `crying` `angry` `surprised` `sad` `tired` `embarrassed` `expressionless`.

Gaze: `looking at viewer` `looking away` `looking to the side` `looking up` `looking down` `looking at another` `looking back` `closed eyes`. One direction per person; `looking back` and `closed eyes` can join a direction.

## Framing and camera

Pick the framing from the parts of the body the moment must show:

- `close-up` or `portrait` (face), `upper body` (waist up), `cowboy shot` (to mid-thigh), `full body` (head to feet), `wide shot` (people small in a place).
- Camera height: `from below`, `from above` (never both). Direction: `from side`, `from behind`, `straight on`, `three-quarter view`, `profile`. A height can join a direction (`from below, from side`), but two directions cannot (`from behind, from side`).
- Also: `pov`, `dutch angle`, `foreshortening`, `depth of field`, `blurry background`.

How much of the frame something takes up is a sentence, not a tag; see the scenes page if installed.

## Body-part focus

| How reliable | Tags |
| --- | --- |
| Works | `foot focus` `hip focus` `ass focus` |
| Weak; pair with a description | `eye focus` `hand focus` `back focus` `breast focus` (singular) |
| Use a sentence instead | `navel focus` `thigh focus` `leg focus` |

`sharp focus`, `soft focus` and `out of focus` are about blur, not about a body part.

## Place and light

- **Place:** `indoors`, `outdoors`, `bedroom`, `kitchen`, `classroom`, `library`, `tavern`, `street`, `alley`, `forest`, `beach`, `castle`, `ruins`, `rooftop`, `window`, `door`, `fireplace`, `table`, `chair`, `bed`.
- **Time and weather:** `day`, `night`, `sunset`, `morning`, `rain`, `snow`, `fog`, `cloudy sky`, `starry sky`.
- **Light:** `sunlight`, `moonlight`, `candlelight`, `backlighting`, `rim lighting`, `soft lighting`, `dim lighting`, `dappled sunlight`, `light rays`, `shadow`, `cinematic lighting` (only when the prose's light is dramatic).
- **Background:** `simple background`, `white background`, `dark background`, `detailed background`, `blurry background`, `transparent background`. Complexity, blur, colour and transparency are separate; only contradictions about the same area matter.

## Contradictions

Check tags by whom and which area they describe before calling them a conflict.

| Group | Rule |
| --- | --- |
| Gaze | One direction per person. Two people looking at each other: `looking at another` on each `Character N:` line, and a sentence for the height difference. |
| Framing | One framing tag. If the moment's must-see parts do not fit, change the framing, do not drop the parts. `close up` and `close-up` are the same tag; write one. |
| Pose | One body position per person. One standing and one squatting go on separate `Character N:` lines. |
| Camera | `from below` and `from above` exclude each other; `from behind` and `from side` too. |
| Count | `solo` never with `2girls`; the count never repeated in fields. |

## Words that are not tags

Some useful ideas have no tag; write them as sentences. Never make one up by joining words with underscores, and never mark a sentence's idea as a checked tag. For actions, check a ready tag first (`holding cup`, `outstretched hand`, `hand on another's shoulder`), then put what no tag says (how far the hand still is from the cup) in a sentence.

Sources for checking: the [Danbooru tag API](https://safebooru.donmai.us/wiki_pages/api%3Atags) and [API help](https://safebooru.donmai.us/wiki_pages/help%3Aapi) (Safebooru mirror). A search such as `/tags.json?search[name_or_alias_matches]=TERM*&search[hide_empty]=true&search[order]=count` lists a tag's canonical name, post count, category and whether it is deprecated.
