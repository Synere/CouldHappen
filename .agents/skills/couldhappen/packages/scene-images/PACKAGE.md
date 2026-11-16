---
name: scene-images
summary: Pictures inside the story turn they belong to, checked against the scene before they are kept, a "Picture scene" button, a "Make portrait" button per cast member, portraits reused as references so characters stay consistent, and an optional colour theme.
couldhappen: 0.1.12
includes: method
requires: an image provider key in the writer's own environment (the example script uses OpenAI, and a NovelAI provider is included for a NovelAI subscription); the optional sheet file from rpg-mechanics part 3 (this package adds it if missing)
touches: tools/scene_image.py (or tools/scene_image_nai.py and tools/nai_tags.py), notes/style.txt, notes/prompts/ (and notes/prompts/cast/ for NovelAI), public/story.md (picture lines), public/cast.json (`portrait`, `portrait_button`), public/assets/, public/sheet.json, helpers/files.py and helpers/bridge.py (only for the optional sheet, through rpg-mechanics part 3), web/src (Composer, the theme in App, styles), docs/public-contract.md (sheet only), START_HERE.md. The reader already shows picture lines, the enlarge dialog and the cast portrait button, so none of those need editing
cost: with OpenAI, a small charge per image, roughly a cent or two at low quality; regenerating after a failed check and editing with reference pictures cost more. With NovelAI on an Opus subscription, pictures at Normal sizes cost no Anlas but draw on the account's quota; larger sizes or more steps cost Anlas and are made only when the Director asks. The scene description you write is sent to the image provider. With NovelAI, checking an artist tag sends that name to Danbooru's public tag list. The key is never stored in any file.
---

# Scene images

Gives the story pictures. The player presses "Picture scene" next to Send and the writer makes one cheap image of the current moment, checks it against the scene (regenerating up to three times), and attaches it to the story turn it depicts, where it can be clicked to enlarge. A "Make portrait" button on each cast member asks for a portrait, and those portraits are then passed to the image provider as references so characters keep their faces across scenes. Optionally the reader takes on the mood of the scene: its colours, and the picture as a faint backdrop.

What it needs from the player: an image provider key available as an environment variable of the writer's session (the writer must not search for it), and approval to run the image script. Show the Director the first image and ask if the cost and quality are right.

Apply it with [APPLY.md](APPLY.md). The provider is replaceable: the contract is "a prompt file in, a PNG in `public/assets/` out". Two providers come with it: OpenAI (`files/scene_image.py`) and NovelAI Diffusion V5 (`files/scene_image_nai.py`), which reads Danbooru tags and suits illustrated, anime-style stories. NovelAI comes with a guide for turning the story's prose into checked tags, in `nai/`, and a tag-checking helper.
