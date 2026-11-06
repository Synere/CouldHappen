## docs/designs/couldhappen.md

- **Runtime story images are a stated non-goal, but the product now ships them.** Non-Goals say "Runtime story image generation ... deferred. The initial scene uses supplied card PNGs", and Goal 10 says "without requiring a provider integration or runtime image generation". The `scene-images` Director package (`.agents/skills/couldhappen/packages/scene-images/`, `files/scene_image.py`) calls an image provider, and the core code carries its reader side: picture lines in entries (`helpers/files.py` `PICTURE`/`pictures`, `web/src/lib/markdown.js` `splitBody`, `ProseEntry.svelte`, `Lightbox.svelte`), the `portrait_button` cast flag and the "Make portrait" request (`App.svelte` `requestPortrait`, `CastPanel.svelte`). The design never mentions them.
- **Entry bodies are no longer "ordinary unescaped prose".** The design says each entry carries "ordinary unescaped prose" and the public agreement covers entry parsing, cast display, writer controls, snapshots, receipts and recovery. The snapshot now also validates pictures attached to entries (`files.snapshot` rejects an entry whose picture is missing or invalid, closing saving) and adds them to `assets`. That is a public-agreement change with no counterpart in the design.
- **Director packages are not in the design.** The design's "Workspace materials" table and "Keep the package small and adaptable" goal list a skill, templates, helpers and frontend only. The skill now ships `packages/` (`rpg-mechanics`, `scene-images`, `game-master`, `AUTHORING.md`, `INDEX.md`), a mechanism for packaging and sharing a story's own setup, and a skill section "Director packages". The design says nothing about packages, applying them, authoring them, or the rule that discussion only proposes one and the writer applies it on a later explicit yes.
- **Cast-panel behavior beyond the design.** The design's cast panel shows disclosed cast. The reader and skill now also support `present: false` (hide a character, keep the entry), a writer rule to keep the cast to "who matters now" (skill Always 8), and a per-character "Make portrait"/"New portrait" button. None is in the design; only the contract covers `present` and `portrait_button`.
- **`import-card` now writes a readable copy, which the design omits.** The design says only "preserve original source and supplied portraits". `helpers/cards.py` `readable()` also writes `imports/<sha>/card.md`, a plain-text copy of every field and lorebook entry, and the receipt gains `readable_file`. The skill asks the writer for fidelity to it. This is documented in the contract and skill but not the design.
- **The writer-skill reference set grew without a design counterpart.** `references/what-this-can-do.md` and the "what can you do?" flow are described in `AGENTS.md` and the skill but not in the design's "Capability-driven skill and reference integrations".
- **Stale status line.** "Last updated: 2026-11-05" and "Changes since approval are folded into the text below" are false for the items above, which landed on 2026-11-05 to 2026-11-06.

## docs/designs/distribution-and-workspaces.md

- **A second story-creation path exists that the design does not describe.** `python -m helpers new-story --root <workspace> --destination <folder>` (`helpers/stories.py`) extracts the root (baseline) commit of an existing workspace into a new folder, nulls `workspace_id`, and validates. The design says "The initial mechanism is a **release ZIP**" and lists only that creation sequence. `new-story` is documented only in the skill (`references/writing.md:49`).
- **`new-story` has no counterpart in the confirmation checklist.** The checklist (items 1 to 10) verifies a workspace unpacked from a release ZIP. A `new-story` folder is never checked for a null UUID, no `.git`, no story content, or a clean `validate`, other than the `snapshot` call inside `new_story`. It also relies on the workspace having exactly one root commit, which the design states only as a ZIP-flow outcome (checklist item 8).
- **"Links in code spans are not checked" is false.** Builder step 7 says "reference-style links, autolinks, and links in code spans are not checked". `scripts/build_release.py` `LINK = re.compile(r'\]\(([^)]+)\)')` runs over the whole Markdown text with no code-span or fence stripping, so an inline link inside backticks is checked and can fail the build. The picture-line example had to be reworded to avoid it (commit f723bb3, "describe the picture line without link syntax"), which confirms the behavior.
- **The shipped skill includes package scripts with a Python-version requirement the design does not state.** `helpers/stories.py` calls `tarfile.extractall(..., filter='data')`, which needs Python 3.11.4 or later (3.12 or later without the backport). `docs/setup.md` and `README.md` say "Python 3.11+", so 3.11.0 to 3.11.3 fails `new-story` with a `TypeError`, reported as a generic error.
- **The included-contents list omits what is now inside the skill.** "Include" says `.agents/skills/couldhappen/` (portable writer skill and references). It now also holds `packages/` with executable helper scripts (`gm_state.py`, `roll.py`, `sheet-validator.py`, `scene_image.py`) that call out to a third-party image provider. The design's privacy section ("Privacy and sharing") does not mention that a package may send scene text to a provider.

## docs/public-contract.md

- **`new-story` is undocumented.** "Other commands" lists `checkpoint`, `import-card` and `portrait` only. `new-story` (`helpers/__main__.py`) is a public command with a JSON result: `{"status":"created","path":...,"baseline":<sha>}`, and errors for a nonempty destination, a destination inside or around the workspace, a baseline count other than one, and an unsafe archive path.
- **`validate`, `serve` and `entry` are not described as commands.** `python -m helpers validate` prints `{"status":"valid"}` and exits 2 on invalid records. `serve --frontend-origin ... [--previous-helper-stopped]` is mentioned only in passing ("serve --previous-helper-stopped"). `entry --body-file` is mentioned only as a way to encode text.
- **"All commands print one JSON object" is not true for `entry`.** `helpers entry` writes the raw encoded entry text to stdout, with no JSON. `serve` prints one JSON line and then keeps running.
- **Picture-line syntax limits are not stated.** The code accepts a caption of 0 to 200 characters containing no `]` or newline, a file name of 1 to 121 characters matching `[A-Za-z0-9][A-Za-z0-9._-]*\.png`, and trailing whitespace on the line, but not leading whitespace (`files.PICTURE`; `web/src/lib/markdown.js` repeats the same pattern). The contract says only "a Markdown image on a line of its own". The same regex lives in two places (Python and JavaScript) with no check that they agree.
- **The portrait button label is not exact.** The contract says the Cast panel offers a "Make portrait" button. `CastPanel.svelte` shows "New portrait" when the character already has a `portrait`. It also disables the button while saving is closed for the Director channel (`canRequest` in `App.svelte`), which the contract does not state.
- **`wait-view` is described, but `invalidate` ownership is not enforced as written.** "`writer invalidate --token` rotates generation under an owned pause". `Bridge.control` for `invalidate` checks only the token. After `pause` then `close`, the token is not cleared (`close` sets `owner` false but leaves `self.token`), so `invalidate` is accepted with no ownership.
- **`close` leaves `paused` set.** The contract says `close` "closes acceptance, drains accepted saves, validates ..., and disarms". If the workspace is paused when `close` succeeds, the persisted `paused` flag stays true (`state.update(owner=False, armed=False)`), and a later `claim` clears it silently. The contract does not describe closing while paused.

## Not covered by this run

- The packages' own `PACKAGE.md` and `APPLY.md` files are not design documents and were read only to find which core behavior they depend on. `scene-images/PACKAGE.md` listed `helpers/files.py`, `helpers/bridge.py`, `web/src` (App, Cast panel) and `docs/public-contract.md` under `touches`, although the picture-line, enlarge dialog and `portrait_button` changes are now in core. Those files are still touched only for the optional sheet (through `rpg-mechanics` part 3), the Composer and the theme. `rpg-mechanics` Part 3 still tells the writer to add a `sheet` field to `snapshot()`, which the contract does not list; its `APPLY.md` says to update the contract when it does.
- `docs/designs/creative-practice-examples.md`, `SITEMAP.md` and `impeccable_direction_notes.md` were left out on purpose, as the distribution design's "Drift input" section directs.

## Triage (2026-11-06)

**Fix the code** (the documents are right):

1. `invalidate` must require current ownership, not closing, and the owned pause token. Today it checks only the token, and `close` leaves the token set.
2. `close` must refuse while a pause is held ("release first"), so a closed workspace never persists `paused: true`.
3. A test that the Python `PICTURE` pattern (`helpers/files.py`) and the JavaScript one (`web/src/lib/markdown.js`) accept and reject the same lines, since they are copies of each other.

**Fix the documents** (the code is right):

4. Contract: add `new-story`, `validate`, `serve` and `entry` to "Other commands"; say `entry` prints raw entry text and `serve` stays running (the "one JSON object" rule applies to the others); state the picture-line limits; say the portrait button reads "New portrait" once a portrait exists and is disabled while Director saving is closed.
5. Distribution design: describe `new-story` as a second creation path and say what verifies it (`validate` only); say the link check also reads inline links inside code spans; name `packages/` in the skill contents and note that a package may send scene text to a third-party provider; state Python 3.11.4 or later (also `docs/setup.md` and `README.md`), because `new-story` uses `tarfile` extraction filters.
6. Design: reword the image non-goal to say generation stays in an optional package while the reader supports pictures and portrait requests; add pictures to the entry-body description, Director packages to the workspace materials, `present`, and the readable `card.md` copy; refresh "Last updated".
7. `scene-images/PACKAGE.md` `touches`: drop `helpers/files.py`, `helpers/bridge.py`, `web/src` pieces and the contract, now in core; keep the `sheet` note in `rpg-mechanics` as is.

**Decide:**

8. Whether the design should describe Director packages in full or only link to the skill's `packages/INDEX.md`. Recommended: a short design section plus the link, so the design does not duplicate package contents.

**Done (2026-11-06):** items 1 to 7 are fixed and item 8 is decided: the design now has a short "Director packages" section that links to the skill's package index.

1. `invalidate` requires ownership and a non-closing workspace; test `test_invalidate_requires_ownership`.
2. `close` refuses while paused; test `test_close_refuses_while_paused`.
3. Shared fixture `tests/fixtures/picture_lines.json`, run by `test_picture_line_fixture` (Python) and a `splitBody` test (JavaScript).
4. Contract: `validate`, `serve`, `entry` and `new-story` added; `entry` and `serve` exempted from "one JSON object"; picture-line limits and the "New portrait" label stated; `invalidate` and `close` behavior stated.
5. Distribution design, `docs/setup.md` and `README.md`: `new-story` as a second path, code-span links checked, packages and provider text noted, Python 3.11.4 or later.
6. Design: image non-goal reworded, pictures in entries, `present` and `portrait_button`, `card.md`, Director packages, date refreshed.
7. `scene-images/PACKAGE.md` `touches` corrected. It still touches `helpers/files.py`, `helpers/bridge.py` and the contract for the optional sheet only, so the earlier note in "Not covered by this run" was partly wrong and is corrected above.
