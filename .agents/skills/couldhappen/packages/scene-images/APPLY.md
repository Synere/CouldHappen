# Applying scene-images

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first. Before you start, tell the Director in plain words: images cost a small amount each, the scene description is sent to the image provider, it needs a key in the writer session's environment, and you will ask before running the script. Ask which parts they want; parts 4 to 6 and the theme in part 7 are optional.

Use the usual workspace rules throughout: `writer pause` before editing public files, validate and release, restart the helper after Python changes and Vite after helper restarts, update `docs/public-contract.md` for public-file changes, record the setup where a fresh session can find it from `START_HERE.md`, and commit. On Windows set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` when generating entries and avoid non-ASCII characters in heredocs. Keep a standing wait running after every turn.

## 1. The key and the script

Do not search the machine for a key. If `OPENAI_API_KEY` (or the key of whichever provider the Director chose) is not set in your session's environment, tell the Director how to set it for the process that runs you and stop here. Never write the key into any file, log, entry or command line.

Copy [files/scene_image.py](files/scene_image.py) to `tools/scene_image.py`. With the Director's approval, run `python tools/scene_image.py --models` (a free listing), choose a cheap tier, and set `OPENAI_IMAGE_MODEL` for the writer session. Size and quality default to `1024x1024` and `low`; `OPENAI_IMAGE_SIZE` and `OPENAI_IMAGE_QUALITY` change them. If the Director prefers another provider, adapt the script and keep its contract: prompt file in (and optional reference pictures), PNG in `public/assets/` out, file name printed.

Create `notes/style.txt` with the art style in a few lines (medium, palette, camera, "realistic human scale, no text") and a short list of things to avoid. Put its text at the start of every prompt so you never retype it.

## 2. Sheet file and validator

The reader needs the optional `public/sheet.json` for the quick action and the theme. If the sheet is not installed, apply part 3 of [rpg-mechanics](../rpg-mechanics/APPLY.md) now (a sheet with only `actions` and `theme` is fine; the RPG sheet content is not required).

## 3. The picture, in the turn it belongs to

The reader shows a picture inside the story turn it was made for. A line by itself in a writer entry that is a Markdown image (an exclamation mark, the caption in square brackets, then `/api/assets/<file>.png` in parentheses, with no spaces) appears under that turn as a figure with the caption, and a click enlarges it. The caption is the alt text, so write it as a plain sentence about the scene. The file must be in `public/assets/` first: an entry that names a missing or invalid PNG makes the snapshot fail. Picture lines inside code fences are ignored.

Workflow for one picture, every time:

1. Write a short, concrete prompt for the moment (setting, who is present, light, mood, scale, "no text") and save it to a private file such as `notes/prompts/<n>.txt`, with `notes/style.txt` first.
2. Choose references (part 6), run `python tools/scene_image.py notes/prompts/<n>.txt` (with `--ref` files when characters appear) after approval, and note the file name.
3. **Check it.** Open the PNG and compare it with the scene facts in the story: who is there, what they hold, how many figures, the scale of things, the light and the place. List the differences. If any matter, fix the prompt by saying plainly what was wrong ("one skeleton, human-sized, no floating spheres"), regenerate, and compare again. Stop after three tries and keep the best one. Tell the Director what is still off instead of hiding it.
4. Only then attach it: `writer pause`, add the picture line at the end of the body of the writer entry for that turn, `validate`, `release`. If the turn is already published, edit that entry and keep its id. Never attach a story picture to a Director entry.
5. Delete the generated files you rejected.

Add a quick action: put `{"label": "Picture scene", "body": "Picture the current scene."}` in `actions` of `public/sheet.json` (the validator allows up to four actions of up to 40 characters for the label and 500 for the body). In the reader:

- `web/src/components/Composer.svelte`: in the Story channel only, render each action as a `button.action` beside Send, wrapping the actions and Send in a `div.composer-actions` (the stock stylesheet already styles both). Pressing one saves a Director entry with the action's exact body, using the same payload shape as `submit()` in `web/src/lib/api.js` (`schema_version`, `workspace_id`, `generation`, `channel: 'director'`, a fresh `crypto.randomUUID()` id, `body`). Show a short status. Disable the buttons when Director saving is not permitted (`snapshot.permissions.director.allowed`) or the connection is down. If a save has an uncertain receipt, tell the player to check the Director channel before pressing again.
- When the entry `Picture the current scene.` arrives in Director: make the picture as above for the latest story turn, mark the entry `addressed`, and reply briefly, including any differences that remain.

## 4. Cast portraits and the portrait button

Set `"portrait_button": true` in `public/cast.json` (a top-level boolean beside `characters`). The Cast panel then shows a "Make portrait" button on every character except the legacy `scene` entry ("New portrait" once one exists), disabled whenever Director saving is closed. Pressing it saves one Director entry: `Make a portrait for <name> (cast id <id>).` The reader never retries it; after an uncertain save it tells the player to check the Director channel.

When such an entry arrives:

1. Read the character's description and what the story has shown of their looks. Do not invent features that contradict the story.
2. Write a portrait prompt (head and shoulders or three-quarter view, plain background so the likeness carries over, `notes/style.txt` first) and generate it.
3. Run the check from part 3: one person, the described features, no stray text.
4. Move the PNG to `public/assets/portrait-<id>.png`, replacing and deleting any older portrait of that character, and set it as the character's `portrait` in `public/cast.json`.
5. Mark the entry `addressed` and reply. If you cannot match the request to a cast id, ask in Director instead of guessing.

## 5. Optional: enlarge cast portraits

In `web/src/components/CastPanel.svelte` make each portrait a `<button>` that opens the reader's `Lightbox.svelte` (the same dialog the story pictures use). Keep focus on its close button while it is open and return focus to the opener. Escape closes only the picture and stops propagation so the Cast drawer stays open. Test it in a real browser.

## 6. Portraits as references

A drawn character should look like the same person every time. When a picture shows a cast member who has a `portrait`, pass that portrait to the provider as an input image: `python tools/scene_image.py notes/prompts/<n>.txt --ref public/assets/portrait-whisper.png public/assets/portrait-brann.png`. The script then calls the provider's image-edit endpoint instead of plain generation. Rules:

- Order the files and say so in the prompt: "The first picture is Whisper (keep her face, hair and clothes). The second is Brann." The prompt still carries the scene; the references carry the faces. Say that they are references, not a layout to copy.
- Pass only the two or three characters who are clearly in frame, only files under `public/assets/`, and only characters the story has already disclosed. Never pass a private import.
- If the provider rejects input images, describe the characters in words instead and tell the Director.
- An edit with references costs more than plain generation, depending on the model. Tell the Director before the first one.

Run the check from part 3 and add one question: do the faces still match the references?

## 7. Optional: scene theme and backdrop

The sheet's `theme` is `{name, scheme: "light"|"dark", backdrop: bool, vars: {<name>: "#rrggbb"}}`. Allowed names: accent, accent-deep, highlight, highlight-deep, ink, muted, line, line-soft, reading, surface, panel, panel-deep, side-bg, link. The stock stylesheet already takes every colour from these variables (its secondary tones are mixed from them) and already has the backdrop layer, a fixed `body::before` that paints `var(--backdrop)` blurred and faint. It shows nothing until you set `--backdrop`. So this step changes only `web/src/App.svelte`:

1. **Map the theme.** Add an effect that maps each name onto the reader's CSS variables on `document.documentElement` (`accent` to `--petrol`, `accent-deep` to `--petrol-deep`, `highlight` to `--saffron`, `highlight-deep` to `--saffron-deep`, `side-bg` to `--cast-bg`; the rest keep their names), removing any variable the theme no longer sets, and sets `data-scheme` on the root to the theme's `scheme` (default `dark`). Set `document.title` and the topbar `<h1>` to `theme.name` when there is one (keep `title="CouldHappen"` on the `<h1>`), and fall back to "CouldHappen".
2. **The backdrop.** When `backdrop` is true, set `--backdrop: url('/api/assets/<file>?v=<hash>')` from the newest picture in the story: walk `snapshot.story` from the end, take the first picture `splitBody(entry.body).pictures` (from `web/src/lib/markdown.js`) finds whose name has a hash in `snapshot.assets`. Otherwise set it to `none`.
3. **The sampled accent (optional, recommended with the backdrop).** When the backdrop is on, load that picture into an `Image`, draw it into a 24×24 canvas, and average the hue of its saturated mid-tone pixels (weight by saturation, skip near-black, near-white and grey pixels; average hues as vectors so reds near 0° and 360° do not cancel). Clamp saturation to 30–52% and lightness to 54–66%, and set `--petrol` to `hsl(h s l)` and `--petrol-deep` to the same hue 18 points darker (not below 38%). Return `null`, and leave the theme's accent alone, if the canvas cannot be read or fewer than about 2% of pixels count. A cool scene then cools the reader's structure and a warm one warms it. Cancel a load that finishes after the picture changed.

Example themes. The stock reader is dark petrol, so a theme is only needed for a different mood. A warm, dim room:

```json
"theme": {"name": "Your story", "scheme": "dark", "backdrop": true, "vars": {"accent": "#c6924f", "accent-deep": "#9a6c33", "highlight": "#b45a62", "highlight-deep": "#8e4149", "ink": "#ece0cd", "muted": "#a18b74", "line": "#3a2d23", "line-soft": "#251d17", "reading": "#0e0b09", "surface": "#14100d", "panel": "#191410", "panel-deep": "#221a15", "side-bg": "#0b0807", "link": "#d0a267"}}
```

Change the theme with the mood of the scene and check text contrast in a real browser. Do not hard-code colours that came from another story.

## 8. Record and verify

Record in `START_HERE.md`: where the script, `notes/style.txt` and the prompts are, which provider and model, that the key lives only in the environment, the permission and cost notes, the picture line convention, `portrait_button`, the check-and-retry rule, the reference rule, and the restart rule. Record the package in `notes/packages.md`. Run `python -m unittest discover -s tests -p "test_*.py"` and, in `web/`, `npm run check`. Verify the live snapshot (workspace and generation match), and try in a real browser the button, a picture in the latest story turn with its enlarge view, and a portrait request in the Cast panel. Commit and start a fresh standing wait. Report to the Director what works, the cost of the first image, the differences the check found and what you could not verify. Show the first image and ask if cost and quality are right.
