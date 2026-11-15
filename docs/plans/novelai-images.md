---
type: plan
status: proposed
updated: 2026-11-16
---

# NovelAI images

**Purpose.** NovelAI as a second image provider in the `scene-images` package, with a NovelAI prompt guide the writer reads when it makes a picture. This is an idea, not started. Ends when the provider and its guide ship in `scene-images` with their entries in the pages the writer reads, or when the idea is abandoned.

## ISS-32 — NovelAI provider for scene-images

Raised by the author on 2026-11-16. NovelAI suits illustrated stories and is more permissive about mature content than the example OpenAI provider, and Opus subscribers get free images at normal size. Nothing is built yet.

## What we found

Read on 2026-11-16, nothing run against the API:

- **[NovelAI-Image-MCP](https://github.com/xinvxueyuan/NovelAI-Image-MCP)** (MIT, commit `d54fe41`, 2026-11-12). An MCP server plus a `typer` CLI, `novelai-image-mcp generate`, that saves a PNG and prints its path. It covers V5 (`nai-diffusion-5-full`, `-curated`, `-inpainting`) and multi-character prompts (`characterPrompts`, `char_captions`). Its code says V5 rejects vibe transfer, so it can't use reference images on V5. Neither the server nor the CLI is stdlib-only: both need Python 3.13 and pull in `fastmcp`, `httpx` and `curl_cffi`. Its `nai/http.py` says NovelAI's Cloudflare front resets plain TLS connections from scripts. We haven't confirmed that.
- **nai5-prompting** (Miint-Sunny, GPL-3.0-only, v1.2.8, local copy in `../nai5-prompting`). 11 skills with about 500 KB of references; `nai5-writing/references/illustration.md` alone is 100 KB. The parts this plan needs:
  - `nai5-writing`: field responsibilities, the base prompt with `Character N:` lines and the negative prompt (UC), quality tags, tags or sentences, weights, and the interaction prefixes.
  - Danbooru guidance in `illustration.md`: canonical character and work names, the name spelling convention, and the clothing-state table where similar-looking tags mean different clothes.
  - `oc-character-design`: visual identity and silhouette.
  - `nai5-scene-design`: place, light and framing.
  - `nai5-reverse-prompt`: turning a picture into a V5 prompt, marking what was seen, inferred or given by the user.
- **NovelAI's terms** ([terms of service](https://novelai.net/terms), updated 2025-12-08; [image API docs](https://image.novelai.net/docs/index.html)), as the author confirmed on 2026-11-16:
  - **Allowed:** personal, user-initiated integrations that use a Persistent API Token in the `Authorization` header.
  - **Endpoints:** third-party tools should call only the `/ai/` generation endpoints, not account or subscription endpoints.
  - **Prohibited:** scraping, overloading the service, bypassing technical restrictions, and sharing or reselling one account.
  - **Quota:** API calls draw on the same quota as the web interface.

  CouldHappen fits these terms. Every picture is started by the Director, and each Director uses their own account and token.

## Approach

**Provider, not a new package.** The reader-side parts of `scene-images` (the picture line, the button, portraits, the theme) stay as they are. Add `files/scene_image_nai.py` with the existing contract: a prompt file in, a PNG in `public/assets/` out, the file name printed. Add a "NovelAI provider" section to APPLY. The key is `NOVELAI_TOKEN`, a persistent `pst-` token in the writer session's environment. Never take a username and password.

**Default generation settings: the most the Opus free tier allows, with Effort High.** The author set this on 2026-11-16:
- **Steps:** 23. The author confirmed on 2026-11-16 that the capture was taken with Effort High, so High sends 23 steps. With Medium, the UI hides the steps input; what Medium sends is unknown.
- **Sizes:** NovelAI's Normal sizes only: portrait 832×1216, landscape 1216×832, square 1024×1024. The writer picks the orientation that fits the moment, portrait for one person and landscape for a place or a group.
- **Other settings:** sampler `k_euler_ancestral`, noise schedule `karras`, guidance 5.
- **Anything that costs Anlas** (a larger size, more steps) needs the Director's explicit request each time.

**Effort**, from NovelAI's [announcement](https://journal.novelai.net/novelai-diffusion-v5-full-effort-toggle/) (added to V5 Full on 2026-10-08):
- **High** is the old behaviour, with adjustable steps; NovelAI's comparisons use 23 steps.
- **Medium** is a distilled model locked at 14 steps. It costs about 42% less of the Opus usage limit, and NovelAI's blind tests rated it about equal to High at 23 steps. It doesn't allow some settings to change; for negatives NovelAI suggests negative emphasis in the prompt.
- **Third-party clients (not verified by us)** say Medium uses the model `nai-diffusion-5-full-medium`, fixes the sampler, the Heavy UC and CFG rescale, and ignores custom negative prompts. If so, the package's own UC, including the `nsfw` choice, does nothing on Medium.
- **Default:** High at 23 steps. Medium can be offered later as a cheaper option.

**Quality tags and UC defaults**, from NovelAI's docs ([quality tags](https://docs.novelai.net/en/image/qualitytags/), [undesired content](https://docs.novelai.net/en/image/undesiredcontent/)):
- **Quality tags (Standard):** append `, very aesthetic, masterpiece, no text` to the end of the base prompt, and send `qualityPresetId` `none` so they aren't added twice. `no text` suits story pictures; drop it only for a picture that needs readable text. (Light is `, very aesthetic, amazing quality, no text`.)
- **UC (Heavy V5):** `lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page`, written into the UC and also sent as `ucPresetId` `heavy`, the way the web UI does.
- **`nsfw`:** not part of the preset, and left out by default. APPLY doesn't ask about it. It's prepended only after the Director says they don't want NSFW pictures, and that choice is recorded in `notes/style.txt` (the author's decision, 2026-11-16).
- **Image-specific exclusions** go in the prompt as negative emphasis (`-1.5::thing::`), not in the UC, as nai5-prompting advises.

**Staying within the terms.** The package spells these out:
- **Director-started only.** A picture is made only when the Director presses a button or asks for one. The package never makes pictures on its own each turn.
- **Retry cap.** The existing picture check stops after three tries.
- **One account per Director.** The token is the Director's own, and the package never offers a shared one.
- **Generation endpoints only.** The script calls only `/ai/` generation endpoints. That rules out the MCP's balance and subscription tools.

**Transport: try the plain way first.** The first slice is a stdlib `urllib` request to `image.novelai.net/ai/generate-image` with the token. The MCP repo uses `curl_cffi` to make its requests look like Chrome so Cloudflare lets them through. That may count as "bypassing technical restrictions" under the terms, so the package doesn't take it on as a fallback by default. If plain HTTPS is refused, stop and decide then: ask NovelAI what a script should send, or drop the provider. No MCP server config either, since it would differ on every host.

**Probe, 2026-11-16 (no token).** A stdlib `urllib` POST to `/ai/generate-image` from Python 3.14 on Windows got through:
- **Default user agent:** Cloudflare rejected `Python-urllib/3.x` with `403`, error 1010 (a blocked client signature).
- **Honest user agent:** with `User-Agent: couldhappen-scene-image/0.1`, the request reached NovelAI's backend and got its own `401 Unauthorized` JSON.
- **No TLS reset:** plain HTTPS works with no impersonation. The script must send a user agent that names itself.
- **Not yet tested:** an authenticated generation, including whether V5 accepts this payload and that a non-streamed request returns a ZIP holding the PNG.

**Authenticated try, 2026-11-16.** The author ran the test with their own token. NovelAI answered `HTTP 400` with an empty body, so it rejected the payload. The V5 web UI has **Mode** (for example Anime) and **Effort** (Medium, High) settings that NovelAI-Image-MCP doesn't send; its V5 payload is marked "pending live verification". The web UI's V5 request, from its DevTools headers:
- **Endpoint:** `POST /ai/generate-image-stream`, not `/ai/generate-image`.
- **Request body:** `multipart/form-data`, about 2 KB, not JSON.
- **Response:** `application/msgpack`, a stream of events rather than a ZIP.

The request body is a single part named `request` (`filename="blob"`, `application/json`) holding the usual `{input, model, action, parameters}`, plus `use_new_shared_trial: true`. In that capture:
- **Steps and guidance:** `steps` 23, `scale` 7.
- **Mode and Effort:** neither is a field of its own. Effort High sent `steps` 23 (confirmed by the author). Mode probably sets the model or the presets. Not confirmed.
- **Quality and UC presets:** `qualityPresetId` is `none` and `ucPresetId` is `heavy`. The UI writes the quality tags and the UC text straight into the prompts. Its UC text starts with `nsfw`, the author's own addition; the package leaves `nsfw` out by default.
- **V5-only fields:** `straight_alpha`, `tag_hint_qt`, `tag_hint_uc_preset`, `inpaintImg2ImgStrength`.
- **Output:** `image_format` `webp`, `stream` `msgpack`.

The stream is 4-byte big-endian length frames, each a MessagePack map; the last has `event_type: "final"` and the image bytes. The test script now copies this request, asks for `png`, and reads the stream with a stdlib MessagePack decoder (offline self-test passes).

**Working generation, 2026-11-16.** The author ran the rebuilt script with their own token:
- **Response:** `200`, `application/msgpack`, 1.78 MB.
- **Image:** a valid 832×1216 PNG (1.43 MB) at 23 steps, from plain stdlib HTTPS with an honest user agent. PNG output works on V5.

Against its prompt:
- **Matched:** one girl, long black hair, green eyes, white shirt, indoors by a window, soft light, looking at viewer.
- **Didn't match:** `upper body`. The image shows her full length, sitting, in an unbuttoned shirt with bare legs, more suggestive than the prompt asked for, even with `nsfw` in the UC.

Two lessons for the package:
- **The picture check is necessary.** Framing tags don't always hold.
- **Use our own quality block.** The prefix copied from the capture carries the author's own tags (`thin legs ::` and others), which likely pulled the framing toward the legs.

**Simpler endpoint works too, 2026-11-16.** A retry of the first test (author's run, own token) used the capture's parameters as plain JSON to the non-stream `/ai/generate-image`, without `stream` or `use_new_shared_trial`:
- **Result:** a ZIP holding a valid 832×1216 PNG (1.22 MB) at 23 steps.
- **Why the first try failed:** its parameters were MCP-derived and out of date (or the token paste went wrong), not the endpoint.
- **Prompt:** short and our own, with no personal tags. Every tag held: one girl, long black hair, green eyes, white shirt, upper body, by a window, soft light, looking at the viewer.

**Choice for the package:** use `/ai/generate-image` with JSON. The ZIP response is read with the stdlib `zipfile`, so no MessagePack reader is needed. Keep the stream endpoint as a documented fallback.

**Character consistency without reference images.** V5 doesn't take reference images, so part 6 of APPLY ("portraits as references") changes for this provider. Each cast member gets a fixed appearance tag block in `notes/prompts/cast/<id>.txt`, put on their `Character N:` line in every picture. Reverse prompting writes that block:
- **From an existing portrait:** the portrait a card supplies, or the first approved generated portrait, becomes the tag block.
- **Marking sources:** the writer marks what it saw in the picture, what it inferred, and what the story says. The story wins where they disagree.
- **Checking:** the existing picture check gains one question: does each character still match their tag block?

**The guide translates the prose; it does not design.** The story already decides the scene and how the characters look. The writer's job is to recreate that moment faithfully in NovelAI's terms, not to invent a composition. So the guide is a translation guide, and the design methods in nai5-prompting (a character's core, world relationships, scene ideation) stay out. Its rules:

- **Danbooru tags wherever a tag exists.** People, counts, body, hair, clothes, clothing state, pose, expression, framing, camera height, light and place are all written as canonical Danbooru tags. Check a tag against the Danbooru wiki when unsure what it means; similar-looking tags can mean different clothes.
- **Sentences only where tags can't express it.** Use a sentence for who holds or touches what, who is in front of whom, and where each person is looking. This matches nai5-prompting's own rule: tags list objects and their attributes, sentences connect them.
- **Nothing the prose doesn't support.** Don't add props, people, clothing or a mood the story didn't give.
- **Fix what the prose doesn't say.** When the picture needs a detail the prose leaves open, such as hair colour, choose it once and record it in the cast tag block so it never changes. Don't let it vary from picture to picture.
- **Follow the story when they differ.** The prose wins over a tag block or a supplied portrait, and the writer tells the Director about the difference.

A `references/` set inside the package, split so the writer reads the core and danbooru pages for every picture and the others on demand:

| Page | Keeps from nai5-prompting | When the writer reads it |
| --- | --- | --- |
| core | the field layout (base, `Character N:`, UC), quality tags and UC defaults, the translation rules above, weights, interaction prefixes, final checks against the prose | every picture |
| danbooru | the tag vocabulary by category (body, hair, clothes, clothing state, pose, expression, framing, light, place), canonical names and the spelling convention, the confusable-tag table, checking the wiki | every picture |
| characters | turning the story's description of a person into a cast tag block, recording chosen details, keeping it in step as the story changes their looks | a new cast member, a portrait request, a change of look in the story |
| scenes | turning the story's place and moment into framing, camera height, light and how much of the frame each thing takes up | a new location, a wide shot, more than one person in frame |
| reverse | image to tag block, the three source marks, scope | a supplied portrait, a portrait made for the first time, a picture that drifted |

### What we take from nai5-prompting

By source section (v1.2.8). "Adapt" means rewrite for the writer's job of turning prose into tags, keeping the rule and its examples, not copying the text.

| Our page | Source | Sections |
| --- | --- | --- |
| core | `nai5-writing/references/conventions.md` | Field Responsibilities; Assemble the Final Draft; Quality Tags and UC (the term-deletion table, negative emphasis instead of UC); Weights; Multiple Characters: Syntax; Text Rendering; V5 Switches and Limitations |
| core | `nai5-writing/references/illustration.md` | Character Types and Appearance Fields; Complete Template and Writing Checks; Put Complete Appearance in Character Fields; Order Within the Base Prompt; A Prompt Is a Sequence of Functional Blocks; Choose Tags or Sentences; Multi-Person Interaction and Prefix usage (`source#`, `target#`, `mutual#`); `Character N` Mapping; Single-Person UC Presets for Multi-Person Images; Troubleshooting; Final Checks |
| danbooru | `illustration.md` | Objects and Attributes Suited to Tag Phrases: Number of people, Species Traits, Framing and Viewpoint, Posture, Clothing State (the confusable-tag table), Body-Part Focus, IP and character name (spelling convention), Check semantic conflicts |
| danbooru | `nai5-costume-writing/references/costume.md` | Check the AI corresponding name on Danbooru; Levels of Word Choice; Division of labor between tags and natural language; Commonly Misused Terms |
| danbooru | `nai5-writing/references/sources.md` | the Danbooru tag wiki and API links, for checking a tag |
| characters | `illustration.md` | Character-Field Detail: Original vs. Franchise Characters |
| characters | `nai5-costume-writing/references/costume.md` | Expressing Garment Components; Writing from User-Supplied Clothing Strings (for a card's outfit text); Including the Outfit in a Complete Image |
| characters | `oc-character-design/references/character.md` | Establish Visual Identity and Overall Silhouette only, as what a tag block must capture |
| scenes | `illustration.md` | Use Sentences for Space, Ownership, and Action Relationships (spatial relationships, perspective, how much of the frame, action in progress, light and shadow, integrity of scene objects, syntactic convention); Relative Position and Frame Coverage; Layout and Background Treatment |
| scenes | `nai5-illustration-composition/references/composition.md` | Camera, Space, and Visual Hierarchy; Arrange bodies and objects from action targets; Light, color, material and atmosphere, as rules for showing the story's moment, not choosing one |
| reverse | `nai5-reverse-prompt/references/reverse.md` | all of it: three sources marked separately, scope, read grammar first, look at the picture, what not to infer, delivery |

Left out:
- **Design and ideation:** `nai5-ideas`, `nai5-art-direction`, `oc-costume-design`; most of `oc-character-design` and `nai5-scene-design`, which invent things the prose already decides.
- **Comics:** `nai5-comic-storyboard`, `nai5-comic-writing`, and the panel sections of `illustration.md`.
- **Agent-to-user rules:** Exact Edits and protected original strings, which are about a user's own prompt text.
- **Colour:** the colour-mode sections (monochrome and partial monochrome) unless a story calls for them.
- **Background research:** the `background.md` methods, which also carry a separate MIT notice.

A Director who wants these can install the full skill, and the package says how. The source sections add up to roughly 120 KB; the adapted pages should be far smaller. The budget is still open.

**License.** nai5-prompting is GPL-3.0-only. GPLv3 §13 and AGPLv3 §13 allow combining it with CouldHappen's AGPL-3.0-or-later, as long as the adapted pages keep its copyright line, source link and NOTICE. Record bundling third-party GPL text as an ADR before the guide ships. If we adapt NovelAI-Image-MCP's request format, credit it under MIT.

When it ships, update `packages/INDEX.md`, the skill's `SKILL.md` reference list and `references/what-this-can-do.md` (see [AGENTS.md](../../AGENTS.md)).

## Possible slices

To be agreed before they become rows:

1. `scene_image_nai.py` from the working non-stream test script (JSON in, ZIP out): one generated PNG through the contract over plain HTTPS (transport and payload proven on 2026-11-16).
2. The core and danbooru pages, and the APPLY section for one-character scenes.
3. Cast tag blocks with the reverse page: portraits on V5 and multi-character scenes, plus the extra question for the picture check.
4. The characters and scenes pages, the license ADR, and the writer's capability pages.

## Open

- Whether V5 has gained any reference-image feature since the MCP's note. If not, whether to offer V4.5 with vibe transfer as an alternative for portraits.
- The size budget for the guide. The danbooru page carries most of the weight; leaving the design methods out keeps the rest small.
