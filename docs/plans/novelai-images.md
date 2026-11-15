---
type: plan
status: active
updated: 2026-11-16
---

# NovelAI images

**Purpose.** NovelAI as a second image provider in the `scene-images` package, with a NovelAI prompt guide the writer reads when it makes a picture. Built on 2026-11-16 (ISS-33 to ISS-37); the live checks are ISS-38. Ends when the provider and its guide ship in `scene-images` with their entries in the pages the writer reads, or when the idea is abandoned.

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

**How the writer finds the right tag.** Agreed with the author on 2026-11-16. Four sources, in order:
1. **Memory.** The model's own knowledge covers the common tags. It goes wrong in three ways: invented tags (`black long hair` instead of `long hair, black hair`), similar-looking tags that mean something else (`loose socks` are baggy socks, not slipped ones), and rare tags that barely move the image.
2. **The danbooru page.** The tags story pictures usually need, by category, plus the confusable-tag table.
3. **A tag-suggestion helper.** `tools/nai_tags.py <partial tag>` calls NovelAI's `GET /ai/generate-image/suggest-tags` (`model`, `prompt`, `lang`), the endpoint behind the web UI's autocomplete. It returns `{"tags": [{"tag", "count", "confidence"}]}`, where `count` is how often the tag occurs in NovelAI's training data. So it shows what the model learned, not raw Danbooru. It's an `/ai/` endpoint and makes no image, so it fits the terms. The writer runs it on any tag it isn't sure of. No match, or a low count, means describing that detail in a sentence instead.
   **Tried on 2026-11-16** (author's run, own token): suggest-tags answers for `nai-diffusion-5-full`, 10 suggestions per query. What the results show:
   - **Counts top out at 10000.** They show whether a tag is common, not an exact frequency. Examples: `thighhighs`, `upper body`, `loose socks` and `socks` all read 10000; `thighhighs pull` 8348; `torn socks` 4292; `socks rolled down` 28.
   - **Confidence 0.0 seems to mean a direct text match.** The real tags that start with the query all came back at 0.0. Fuzzy matches score 0.6–0.85, and many are noise: `upper bo` returned `boingo`, `bo staff`, `elder bors`.
   - **The rule for the helper:** only a match that starts with the query counts; a fuzzy match isn't a confirmation.
   - **It catches invented tags.** For socks that slipped down, the obvious tag, `socks rolled down`, has a count of only 28, so the writer would use a sentence instead. That's the mistake this check is for.
   - **Display:** the script printed long confidence decimals; round them in the real helper.
4. **The Danbooru wiki, for meaning.** The suggester says a tag exists and is common, not what it means. When meaning matters, as with clothing state or `X focus` tags, the writer reads the tag's wiki page.

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

## Further features worth using

A second pass on 2026-11-16 over nai5-prompting, NovelAI-Image-MCP's skills and NovelAI's docs found these.

From nai5-prompting:
- **A fixed style block per story.** `illustration.md` "Style blocks" says to keep the artist and technique strings verbatim (order, weights, spaces) and put them in a fixed place. That's how one story keeps one art style: `notes/style.txt` holds the block, and every prompt reuses it unchanged. This goes in the core page. Agreed with the author on 2026-11-16.
- **V5 switches suited to a story reader** (`illustration.md` "V5-Specific Switches", tag-only):
  - `visual novel sprite` for cast portraits, and `visual novel cg` or `visual novel bg` for scenes and places.
  - `transparent background`, which with V5's true alpha (`straight_alpha`) could give cutout portraits.
  - `low/medium/high/ultra complexity` as a deliberate choice, never added by default. nai5-prompting calls it a "generation computation budget" for how much visual detail goes in, separate from steps and size. High suits a busy place, and the skill pairs `vn bg` with high complexity and `depthness`. Too much can make results stiff or repetitive, and low and ultra noticeably restyle the picture. So the writer adds it only when the prose describes a detailed or a stark scene. The core page explains all four levels to the writer (the author's request, 2026-11-16).
  - These go in the core page. The author agreed to the visual-novel and transparency switches on 2026-11-16. Whether they help in the reader is untested.

From the NovelAI API (models and costs as the MCP and NovelAI's docs state them, not tested by us):
- **Inpainting** (`nai-diffusion-5-full-inpainting`, image plus mask): redraw one wrong region instead of the whole picture, such as wrong clothes or an extra hand. This could make the picture check's retry cheaper and keep the parts that were right. Whether it's free on Opus at Normal size isn't documented. Deferred by the author on 2026-11-16: inpainting means making a mask and more tool calls for each fix, so it waits until the simple check-and-regenerate loop shows it isn't enough.
- **Seed:** record each picture's seed beside its prompt in `notes/prompts/<n>.txt`, so a picture can be remade or varied deliberately. The MCP's skill recommends this too. Cheap, so slice 1.
- **Character positions:** `characterPrompts[].center` and `use_coords` place each character on the canvas; V5 is a free canvas. The writer can follow where the prose puts people ("she stands at the door, he sits by the fire"). This goes in the scenes page.
- **Precise Reference** (a reference image for a character or style): V4.5 only, and 5 extra Anlas per image ([docs](https://docs.novelai.net/en/image/precisereference/)). It's a paid alternative for portrait consistency that the Director could opt into. The V5 default stays tag blocks.

The author expects V5 to gain Precise Reference. Design for it now: keep each portrait as a file (`public/assets/portrait-<id>.png`, as today), keep `--ref` in the script's interface, and have the script refuse it with a clear message on models that don't support it. When V5 supports references, the writer passes the portraits as part 6 of APPLY already describes, and the tag blocks stay as the text side.
- **Director tools** (emotion change, background removal, line art, colourize) and **upscale:** the MCP says each spends Anlas. Emotion change could give one portrait several expressions with the same face. Leave all of these out unless a Director asks (the author agreed, 2026-11-16).

From NovelAI-Image-MCP's skills:
- **Offline cost estimate:** the MCP mirrors the web client's Anlas formula in `estimate_anlas_cost`: resolution × steps × samples, minus one free sample on Opus at 28 steps or fewer and 1024×1024 or smaller. The script can refuse non-free settings unless the Director asked for them, with no API call. Unverified against the current web client; Effort Medium changes the step term.

The author wants this only if it's accurate. Until then the script enforces the free-tier rules directly, which needs no formula: Normal sizes only, 28 steps or fewer, one sample. Anything else needs the Director's explicit request. To adopt the formula, compare its estimate with the cost the web UI shows on its Generate button for a handful of settings (sizes, steps, High and Medium). Use it only if every case matches.
- **Not useful to us:** the MCP's prompt templates. They are a generic idea-to-tags recipe, and the nai5-prompting pages already cover it better.

## Tickets

Agreed with the author on 2026-11-16. ISS-32 stays open as the umbrella until these close.

## ISS-33 — NovelAI provider script and APPLY section

Blocked by nothing. Delivers `scene-images/files/scene_image_nai.py`, built from the working non-stream test script. Start by copying it out of the 2026-11-16 session's scratchpad, `nai_generate_zip.py`, before anything clears it; the plan's request details are enough to rebuild it if it's gone. What it has to do:
- **Request:** JSON to `/ai/generate-image`, the ZIP read with `zipfile`, and an honest user agent.
- **Token:** `NOVELAI_TOKEN` from the environment, never printed.
- **Defaults:** V5 Full, Effort High at 23 steps, Normal sizes by orientation, the Standard quality tags appended with `qualityPresetId` `none`, the Heavy V5 UC, and `nsfw` only on the Director's word.
- **Seed:** recorded beside the prompt.
- **Free-tier limits:** Normal size, 28 steps or fewer and one sample, enforced unless the Director asks.
- **`--ref`:** kept in the interface, refused on V5 with a clear message.

Also delivers the "NovelAI provider" section in APPLY, with tests for the parts that run offline (payload building, limits, ZIP reading). Done when one PNG lands in `public/assets/` through the existing contract in a release workspace.

**Closed 2026-11-16, not yet observed in a story.** `files/scene_image_nai.py`, the APPLY section "NovelAI provider" and `tests/test_scene_image_nai.py` shipped. Two changes from the list above, both from reading nai5-prompting's field rules while building it:
- **Prompt file layout.** nai5-prompting keeps each person's appearance and clothes in their own character field and their action in a `Character N:` line inside the base prompt. So the prompt file sends its base text as written, and each character field sits under a `[Character N]` header line. The script maps those fields to `characterPrompts` and `char_captions`.
- **`--text`** drops `no text` from the quality tags and `logo` from the UC, as nai5-prompting's UC conflict table does for a picture with readable text.

The live checks moved to ISS-38.

## ISS-38 — Live checks of the NovelAI script

Raised on 2026-11-16 when ISS-33 closed. The offline tests cover payload building, the free-tier limits, the seed record and ZIP reading. The payload differs from the 2026-11-16 working request only in guidance (5, the author's default, against the capture's 7) and in using character fields, which no live request has sent yet. To check, in a release workspace, with the author's own token:
- **One character:** a one-person prompt file through `tools/scene_image_nai.py` lands one PNG in `public/assets/` and records its seed.
- **Two characters:** a prompt file with `[Character 1]` and `[Character 2]` fields returns a picture with two people whose looks follow their own fields.
- **Tag helper:** `tools/nai_tags.py` prints only matches that start with the query.
- **Same character twice:** one cast block used in two scenes, one of them with two characters, gives a consistent look.
- **Positions:** a two-character scene with `@ X,Y` positions puts each person where the prose does.
- **From prose:** a one-character scene written from a story passage with `nai/core.md` and `nai/danbooru.md`, its unsure tags checked with the helper, passes the picture check.

## ISS-34 — Decide on bundling adapted nai5-prompting text

Blocked by nothing. Records an ADR on shipping pages adapted from nai5-prompting (GPL-3.0-only) in the AGPL-3.0-or-later release: GPLv3 §13 and AGPLv3 §13, the notices each adapted page keeps (copyright line, source link, NOTICE), and how the release ZIP carries them. Done when the ADR is accepted.

**Closed 2026-11-16** by [ADR-10](../decisions/ADR-10-bundle-adapted-nai5-prompting-pages.md): the adapted pages go in `packages/scene-images/nai/`, GPL-3.0-only, with `NOTICE.md` and `LICENSE-GPL-3.0.txt` beside them.

## ISS-35 — Core and danbooru pages and the tag helper

Blocked by ISS-33 and ISS-34. Delivers:
- **The core page:** fields, quality and UC, weights, the translation rules, the style block in `notes/style.txt`, the V5 switches with all four complexity levels explained, and final checks.
- **The danbooru page.**
- **`tools/nai_tags.py`:** only matches that start with the query count, counts top out at 10000, and confidence is rounded.
- **The capability pages:** `packages/INDEX.md`, the skill's `SKILL.md` reference list and `references/what-this-can-do.md`.

Done when a one-character scene turns from prose into tags with checked tags and passes the picture check.

**Closed 2026-11-16, not yet observed in a story.** `nai/core.md`, `nai/danbooru.md`, `nai/NOTICE.md` and `nai/LICENSE-GPL-3.0.txt` under `scene-images/` ([ADR-10](../decisions/ADR-10-bundle-adapted-nai5-prompting-pages.md)), `files/nai_tags.py`, APPLY's pointer to them, the index and capability pages, the README licence note, and tests for the helper and the pages' notices. The skill's own `SKILL.md` reference list is unchanged: it lists the skill's references, and these pages belong to the package, which `packages/INDEX.md` already lists. The core and danbooru pages come to about 22 KB together. The live check (a one-character scene from prose to checked tags that passes the picture check) is part of ISS-38. The helper treats an exact match with a count of a few hundred or more as safe, which settles the first open question below as a working rule until a story shows otherwise.

## ISS-36 — Cast tag blocks, characters and reverse pages

Blocked by ISS-35. Delivers:
- **Cast tag blocks:** `notes/prompts/cast/<id>.txt`, with details the prose leaves open chosen once and recorded.
- **The characters page and the reverse page:** turning a card portrait or the first approved portrait into a tag block, with the three source marks.
- **The picture check's extra question:** does each character still match their tag block?

Done when the same character looks consistent across two scenes, including one with two characters.

**Closed 2026-11-16, not yet observed in a story.** `nai/characters.md` and `nai/reverse.md`, the APPLY paragraph on characters, and a `[Character N = <cast id>]` header in `scene_image_nai.py` that fills the field from `notes/prompts/cast/<cast id>.txt` (lines under the header replace the block's clothing for that picture), with tests. The script reads the block, so the tags cannot drift between pictures. The consistency check across two scenes is part of ISS-38.

## ISS-37 — Scenes page

Blocked by ISS-35. Delivers the scenes page: turning the prose's place and moment into framing, camera height, light and how much of the frame each thing takes up; character positions (`center`, `use_coords`); when to use complexity; and the `vn bg` and `vn cg` switches. Done when a multi-character scene puts people where the prose does.

**Closed 2026-11-16, not yet observed in a story.** `nai/scenes.md`, an `@ X,Y` position on `[Character N]` headers in `scene_image_nai.py` (every character or none; with positions the script sends `use_coords` and each `center`), the APPLY pointer, and tests. The multi-character check is part of ISS-38.

## Open

- What count makes a tag safe to use (a first guess: an exact match with a count of 500 or more), and whether suggest-tags uses any quota (none seen, not confirmed).
- Whether V5 has gained any reference-image feature since the MCP's note. If not, whether to offer V4.5 with vibe transfer as an alternative for portraits.
- The size budget for the guide. The danbooru page carries most of the weight; leaving the design methods out keeps the rest small.
