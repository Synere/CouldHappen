---
name: scene-images
summary: Pictures inside the story turn they belong to, checked against the scene before they are kept, a "Picture scene" button, a "Make portrait" button per cast member, portraits reused as references so characters stay consistent, and an optional colour theme.
couldhappen: 0.1.12
includes: method
requires: an image provider API key in the writer's own environment (the example script uses OpenAI); the optional sheet file from rpg-mechanics part 3 (this package adds it if missing)
touches: tools/scene_image.py, notes/style.txt, notes/prompts/, public/story.md (picture lines), public/cast.json (`portrait`, `portrait_button`), public/assets/, public/sheet.json, helpers/files.py and helpers/bridge.py (only for the optional sheet, through rpg-mechanics part 3), web/src (Composer, the theme in App, styles), docs/public-contract.md (sheet only), START_HERE.md. The reader already shows picture lines, the enlarge dialog and the cast portrait button, so none of those need editing
cost: a small charge per image, roughly a cent or two at low quality; regenerating after a failed check and editing with reference pictures cost more. The scene description you write is sent to the image provider. The key is never stored in any file.
---

# Scene images

Gives the story pictures. The player presses "Picture scene" next to Send and the writer makes one cheap image of the current moment, checks it against the scene (regenerating up to three times), and attaches it to the story turn it depicts, where it can be clicked to enlarge. A "Make portrait" button on each cast member asks for a portrait, and those portraits are then passed to the image provider as references so characters keep their faces across scenes. Optionally the reader takes on the mood of the scene: its colours, and the picture as a faint backdrop.

What it needs from the player: an image provider key available as an environment variable of the writer's session (the writer must not search for it), and approval to run the image script. Show the Director the first image and ask if the cost and quality are right.

Apply it with [APPLY.md](APPLY.md). The provider is replaceable: the contract is "a prompt file in, a PNG in `public/assets/` out".
