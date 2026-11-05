---
name: scene-images
summary: A "Picture scene" button that makes an image of the current moment, a click-to-enlarge view, and an optional scene backdrop and colour theme.
couldhappen: 0.1.7
includes: method
requires: an image provider API key in the writer's own environment (the example script uses OpenAI); the optional sheet file from rpg-mechanics part 3 (this package adds it if missing)
touches: tools/scene_image.py, public/cast.json (a `scene` entry), public/assets/, public/sheet.json, helpers/files.py, helpers/bridge.py, web/src (App, Cast panel, Composer, styles), docs/public-contract.md, START_HERE.md
cost: a small charge per image, roughly a cent or two at low quality. The scene description you write is sent to the image provider. The key is never stored in any file.
---

# Scene images

Gives the story pictures. The player presses "Picture scene" next to Send and the writer makes one cheap image of the current moment, shown as a `scene` entry in the Cast panel. Portraits can be clicked to enlarge. Optionally the reader takes on the mood of the scene: its colours, and the picture as a faint backdrop.

What it needs from the player: an image provider key available as an environment variable of the writer's session (the writer must not search for it), and approval to run the image script. Show the Director the first image and ask if the cost and quality are right.

Apply it with [APPLY.md](APPLY.md). The provider is replaceable: the contract is "a prompt file in, a PNG in `public/assets/` out".
