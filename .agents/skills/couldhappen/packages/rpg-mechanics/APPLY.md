# Applying rpg-mechanics

Follow this only after the Director has agreed (see "Director packages" in the skill). Read [PACKAGE.md](PACKAGE.md) first and tell the Director in a sentence or two what you are about to add, including that the sheet (part 3) is optional and needs restarts. Ask whether they want the sheet.

Throughout, use the usual workspace rules: take `writer pause` before editing public files, validate and release, restart the helper after Python changes (`python -m helpers stop --root .`, then `serve`, as in `docs/setup.md`), restart Vite after helper restarts, update `docs/public-contract.md` for any public-file change, record the setup where a fresh session can find it from `START_HERE.md`, and commit. On Windows set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` when generating entries and avoid non-ASCII characters in heredocs. Keep a standing wait running after every turn.

## 1. Dice that are real

Copy [files/roll.py](files/roll.py) to `tools/roll.py` (create `tools/`). Check it: `python tools/roll.py 1d20 2d6+1` prints one JSON line per roll. From now on every uncertain outcome that you decide to roll is rolled with it, and each roll is shown in the story (dice, modifiers, total, difficulty). State the stat and difficulty before rolling. Never fudge, and never reroll secretly.

## 2. Rules designed for this story

Read [files/rules-template.md](files/rules-template.md) as a starting point only. Write this story's own rules to `notes/rules.md` (private). Design the attributes, skills, die or dice, difficulty scale, conflict, pressures and progression from the fiction: its setting, tone, genre, and the way the Director described what they want. Do not keep names, numbers or genre terms from the template that do not belong. Ask the Director about anything material you cannot infer (how lethal, how crunchy, whether there is magic or technology, whether combat should be central).

If the Director has described a character, set up their sheet from the rules in `notes/rules.md`; otherwise create it when they create the character. Link `notes/rules.md` from `START_HERE.md`.

## 3. Optional: the sheet panel

Only if the Director wants the status shown in the reader. This adds an optional public file `public/sheet.json` that the reader shows below the cast.

Format (`schema_version` 1): optional `title`, `subtitle`; `groups`, each `{title, rows: [{label, value (string or integer), note?}]}`; `log` (short strings, newest first, about 8); and the optional `theme` and `actions` keys used by the scene-images package. The snapshot carries `sheet` (`null` when the file is absent).

Do these changes, under pause, and keep each small:

1. `helpers/files.py`: add the validator from [files/sheet-validator.py](files/sheet-validator.py) just above `snapshot()`, and make `snapshot()` return `'sheet': read_sheet(root)` in its result dictionary.
2. `helpers/bridge.py`: in `view()`, add `'sheet': None` to the default dictionary used when no valid snapshot exists.
3. `web/src/lib/session.js`: add `sheet` and a `Sheet` typedef to the `Snapshot` typedef, so `npm run check` stays clean.
4. `web/src/App.svelte`: pass `sheet={snapshot.sheet}` to `CastPanel`.
5. `web/src/components/CastPanel.svelte`: accept a `sheet` prop. When it has a title, subtitle, groups or log, render below the cast: the title, the subtitle, each group as a heading plus a definition list (the row `title` attribute shows the note), and the log as a short "Recent" list. Style it quietly in `web/src/styles.css` with the existing colour variables.
6. `docs/public-contract.md`: document the optional file and its limits (it is writer-maintained, validated, and a validation error closes saving like any other public file).
7. `tests/test_files.py`: add a test that the snapshot has `sheet` `None` without the file, accepts a valid sheet, and rejects bad shapes (wrong version, unknown keys, boolean or missing row values, too many actions, a bad theme colour).

If the scene-images package is also applied, do its parts 4 to 6 on top of this.

Create `public/sheet.json` for the current character from the rules, and update it after every change to health, resources, gear, skills or experience, and add each roll to `log`. Do not publish enemy statistics or anything the character does not know.

## 4. Record and verify

Record in `START_HERE.md`: where the rules and dice script are, how rolls are shown, who owns the sheet, and the restart rule. Record the package in `notes/packages.md` (name, version 0.1.7 package, date, what you applied, what you chose not to). Run `python -m unittest discover -s tests -p "test_*.py"`, and in `web/` run `npm run check`. Verify the live snapshot (workspace and generation match) and look at the Cast panel in a real browser if the sheet is installed. Commit. Start a fresh standing wait.

Report briefly to the Director what now works and what you could not verify.
