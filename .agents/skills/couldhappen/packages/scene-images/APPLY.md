# Applying scene-images

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first. Before you start, tell the Director in plain words: images cost a small amount each, the scene description is sent to the image provider, it needs a key in the writer session's environment, and you will ask before running the script. Ask which parts they want; parts 4 and 5 (theme, backdrop) are optional.

Use the usual workspace rules throughout: `writer pause` before editing public files, validate and release, restart the helper after Python changes and Vite after helper restarts, update `docs/public-contract.md` for public-file changes, record the setup where a fresh session can find it from `START_HERE.md`, and commit. On Windows set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` when generating entries and avoid non-ASCII characters in heredocs. Keep a standing wait running after every turn.

## 1. The key and the script

Do not search the machine for a key. If `OPENAI_API_KEY` (or the key of whichever provider the Director chose) is not set in your session's environment, tell the Director how to set it for the process that runs you and stop here. Never write the key into any file, log, entry or command line.

Copy [files/scene_image.py](files/scene_image.py) to `tools/scene_image.py`. With the Director's approval, run `python tools/scene_image.py --models` (a free listing), choose a cheap tier, and set `OPENAI_IMAGE_MODEL` for the writer session. If the Director prefers another provider, adapt the script and keep its contract: prompt file in, PNG in `public/assets/` out, file name printed.

## 2. Sheet file and validator

The reader needs the optional `public/sheet.json` for the quick action and the theme. If the sheet is not installed, apply part 3 of [rpg-mechanics](../rpg-mechanics/APPLY.md) now (a sheet with only `actions` and `theme` is fine; the RPG sheet content is not required).

## 3. The picture and the button

Workflow for one picture: write a short, concrete prompt for the current moment (setting, who is present, light, mood, "no text"), save it to a private file, run the script after approval, look at the result, then publish it by putting it in `public/cast.json` as a character with id `scene`, name `Current scene`, a one-line description, and the PNG as `portrait`. Replace the previous `scene` entry and delete its PNG. Publish only images you intend to be public.

Add a quick action: put `{"label": "Picture scene", "body": "Picture the current scene."}` in `actions` of `public/sheet.json` (the validator allows up to four actions of up to 40 characters for the label and 500 for the body). In the reader:

- `web/src/components/Composer.svelte`: in the Story channel only, render each action as a button beside Send. Pressing one saves a Director entry with the action's exact body, using the same payload shape as `submit()` in `web/src/lib/api.js` (`schema_version`, `workspace_id`, `generation`, `channel: 'director'`, a fresh `crypto.randomUUID()` id, `body`). Show a short status. Disable the buttons when Director saving is not permitted (`snapshot.permissions.director.allowed`) or the connection is down. If a save has an uncertain receipt, tell the player to check the Director channel before pressing again.
- When the entry `Picture the current scene.` arrives in Director: write the prompt, generate the image, update the `scene` entry, mark the entry `addressed`, and reply briefly.

## 4. Optional: click to enlarge

In `web/src/components/CastPanel.svelte` make each portrait a `<button>` that opens a full-screen dialog: `role="dialog"`, `aria-modal`, a dark scrim, the picture scaled to fit with `object-fit: contain`, a close button, and click-outside to close. Escape closes only the picture and stops propagation so the Cast drawer stays open. Move focus to the close button when it opens and return it to the opener when it closes. Test it in a real browser.

## 5. Optional: scene theme and backdrop

The sheet's `theme` is `{name, scheme: "light"|"dark", backdrop: bool, vars: {<name>: "#rrggbb"}}`. Allowed names: accent, accent-deep, highlight, highlight-deep, ink, muted, line, line-soft, reading, surface, panel, panel-deep, side-bg, link. In `web/src/App.svelte` add an effect that maps each name onto the reader's own CSS variables (`accent` to `--petrol`, `accent-deep` to `--petrol-deep`, `highlight` to `--saffron`, `highlight-deep` to `--saffron-deep`, `side-bg` to `--cast-bg`; the rest keep their names), removing any variable the theme no longer sets, sets `data-scheme` on the root to `dark` or `light`, and, when `backdrop` is true, sets `--backdrop: url("/api/assets/<portrait>?v=<hash>")` from the `scene` cast entry's portrait and the snapshot's asset hash.

In `web/src/styles.css` make text, panels and controls use the variables instead of fixed colours (root and body text `var(--ink)`, the side panel `var(--cast-bg, ...)`, links `var(--link, ...)`, the textarea background, its placeholder, disabled buttons, the blockquote colour), add `:root[data-scheme='dark'] { color-scheme: dark; }`, and add a fixed `body::before` behind everything that paints `var(--backdrop, none)` centered, covering, at about .35 opacity. Change the theme with the mood of the scene and check contrast for text in a real browser. Do not hard-code colours that came from another story.

## 6. Record and verify

Record in `START_HERE.md`: where the script and prompts are, which provider and model, that the key lives only in the environment, the permission and cost notes, the `scene` entry convention, and the restart rule. Record the package in `notes/packages.md`. Run `python -m unittest discover -s tests -p "test_*.py"` and, in `web/`, `npm run check`. Verify the live snapshot (workspace and generation match), try the button and the enlarge view in a real browser, commit, and start a fresh standing wait. Report to the Director what works, the cost of the first image and what you could not verify. Show the first image and ask if cost and quality are right.
