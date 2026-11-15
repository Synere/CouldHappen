# Notice for the NovelAI guide pages

The pages in this folder are adapted from **nai5-prompting**, NovelAI Diffusion V5 prompt-writing methods.

- Copyright (C) 2026 Miint-Sunny
- Project and public source: https://github.com/Miint-Sunny/nai5-prompting (version v1.2.8)
- Author and contact: https://github.com/Miint-Sunny
- SPDX-License-Identifier: GPL-3.0-only

Miint-Sunny's original contributions, arrangement, and modifications in that project are licensed under the GNU General Public License version 3. You may copy, distribute, and modify them under the terms of that license. The project is provided as is, without any warranty, including the implied warranties of merchantability or fitness for a particular purpose. The full GNU GPL version 3 text in [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt) governs the specific rights, obligations, and warranty disclaimer. If you did not receive it, obtain it at https://www.gnu.org/licenses/gpl-3.0.html.

## What was changed

The CouldHappen project modified these pages on 2026-11-16. They rewrite chosen sections of nai5-prompting as a guide for an agent that turns a story's prose into a NovelAI V5 prompt, shortened and reworded, with CouldHappen's own defaults and tools added. Each page says at its top what it adapts. As modified versions of a GPL-3.0-only work, the pages are licensed as a whole under GPL-3.0-only.

| Page | Adapted from |
| --- | --- |
| [core.md](core.md) | `nai5-writing/references/conventions.md`: field responsibilities, assembling the final draft, quality tags and UC, weights, text rendering, multiple characters, V5 switches. `nai5-writing/references/illustration.md`: character types and appearance fields, the complete template and its checks, style blocks, order within the base prompt, functional blocks, tags or sentences, multi-person interaction and prefixes, troubleshooting, final checks. |
| [danbooru.md](danbooru.md) | `illustration.md`: objects and attributes suited to tag phrases (people, species, framing, posture, clothing state, body-part focus, character names, background, semantic conflicts). `nai5-costume-writing/references/costume.md`: checking names on Danbooru, levels of word choice, tags and natural language, commonly misused terms. `nai5-writing/references/sources.md`: the Danbooru API links. |
| [characters.md](characters.md) | `illustration.md`: character-field detail for original and franchise characters. `nai5-costume-writing/references/costume.md`: expressing garment components, writing from supplied clothing strings, including the outfit in a complete image. `oc-character-design/references/character.md`: establishing visual identity and overall silhouette. |
| [reverse.md](reverse.md) | `nai5-reverse-prompt/references/reverse.md`: the three sources, scope, reading the grammar first, looking at the picture, what not to infer, delivery. |
| [scenes.md](scenes.md) | `illustration.md`: sentences for space, ownership and action (spatial relationships, perspective, frame coverage, action in progress, light and shadow, scene objects, syntactic convention), relative position and frame coverage, layout and background treatment, V5 switches. `nai5-illustration-composition/references/composition.md`: camera, space and visual hierarchy; arranging bodies and objects from action targets; light, colour, material and atmosphere, as rules for showing the story's moment. |

Nothing here is adapted from nai5-prompting's `background.md` files, so the separate MIT notice that nai5-prompting carries for Fanfic-background-assistant does not apply to these pages.

## How this sits in CouldHappen

CouldHappen is licensed AGPL-3.0-or-later. This folder is combined with it under section 13 of the GNU GPL version 3 and section 13 of the GNU AGPL version 3, and keeps its own licence, GPL-3.0-only. The rest of CouldHappen, including the scripts in `../files/`, is not adapted from nai5-prompting and stays under CouldHappen's licence.

A Director who wants nai5-prompting's full methods (ideation, art direction, comics, costume design) can install the original skill from its source above.
