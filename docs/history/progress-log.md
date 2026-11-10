# Progress log (history)

> **History, not current instructions.** This is the full implementation handoff as it stood on 2026-11-05, kept as a dated log. The short current handoff is [implementation progress](../implementation-progress.md); add new dated entries at the end of this file.

Date: 2026-11-04, Asia/Manila. This continuation completed the remaining application implementation and the Woven UI finish pass. The approved first-scope application surface is implemented and mechanically checked. Native-host execution, supplied story/card scenes, fresh-context continuation, checkpoint-limited Undo, and the literal comp pixel gates remain unperformed or intentionally open. This handoff does not convert those into passes.

## Resume here

Read [README.md](../../README.md), this note, [validation results](../validation-results.md), then the original [implementation handoff](implementation_handoff.md) and approved [design](../designs/couldhappen.md) as needed. Do not restart brainstorming or another overall design review. The creative-initiative amendment is approved. Optional skill examples derive from [creative practices](../designs/creative-practice-examples.md) and are not features to implement.

Inspect `git status` before editing. Preserve the approved architecture, the creative-initiative principle, Woven direction/provenance, documentation, and the existing Impeccable hooks. Do not re-scaffold the app or discard follow-up work. The initial checkpoint commit is in Git history; use history for actual IDs. Development commits do not establish native checkpoint enforcement or story validation.

## Present implementation

- Portable writer skill and focused references, with the initiative principle near the beginning and self-contained optional examples. START_HERE is initially free of invented world records.
- Empty public Story/Director logs and cast; work mode `play`; `couldhappen.json` UUID remains null until actual helper setup. Free private methods/records are retained; no model client/controller was introduced.
- Standard-library Python parser/atomic saves/public validation; loopback helper; workspace lock; closed startup; acknowledged draining pause/token; separate production block; retry IDs; generation invalidation; writer-led recovery; local pending-input wait; card import and stripped public portrait preparation.
- Public portrait reads now revalidate path containment and PNG critical structure at snapshot construction and asset serving, with a 32 MiB read bound. This resolves the earlier public-PNG policy gap under the design's stricter "referenced, validated" reading; the portrait helper still validates at export. See "Spec gaps" below.
- Scoped read-only Git checks/inspection, Python native Stop examples, and Pi before-settle extension example. No active checkpoint hooks were installed; `.codex/hooks.json` remains unchanged.
- Svelte/Vite Woven reader with exact approved pins and generated lockfile, local OFL fonts, separate conversation drafts, sanitization/reveal, scroll preservation, responsive disclosed cast, narrow proxy/filesystem boundaries, and browser tests.
- UI finish (this session): the approved Woven topology and palette are carried through; the signature role rule is a paired petrol/saffron 3px thread with a two-diamond interlace at the 62% split; the cast is a separate framed column and a narrow-screen drawer with scrim, close control, Escape, `inert` background, dialog semantics, and focus return. New long writer passages open at their start; a bottom reading-edge fade prevents a stray next-entry sliver; recovery/blocked/empty states are explicit; portrait frames show an honest initial fallback while loading or if an image fails.
- `DESIGN.md` and `.impeccable/design.json` now document the built system. The development surface brief is `.impeccable/surfaces/web-src-app-svelte.md`.
- Operational setup, public contract, host examples, validation procedure/results, and an honest unrun scene record. Original documentation/provenance remain present.

## UI finish and review record

The independent Impeccable finish reviewer examined the rendered surface with fresh context, using the approved Woven comp, the direction contract, the craft floor, and the captured screenshots. Its first pass returned `fix` for five issues. Four were fixed and recaptured: recovery entry slicing, blank blocked-cast frames, drawer focus containment, and channel-aware recovery copy. A verdict pass confirmed the four UI fixes with no new regressions and called the UI shippable at this scope; a final capture check confirmed the last composer-edge sliver was gone and returned `ship` for that check. The build-state record finding was not fixed: `.impeccable/build/state.json` remains at `spec` because the literal comp pixel gates would require reproducing illustrative assets that the approved data boundary forbids. No `--force` bypass was used, and no pixel gate is claimed passed. This is a disclosed record-level exception, not a UI failure.

The independent documenter then authored `DESIGN.md` and `.impeccable/design.json` from the built system. It did not alter application source, PRODUCT.md, the approved comp, or documentation. The finished work is committed as `e5f3eaf`; the scoped checkpoint check returned clean afterward. That check records Git changes, not narrative continuity.

## Latest mechanical checks

**37 Python + 4 frontend unit + 4 Chromium tests passed; Svelte check zero errors/warnings; Vite build passed; Svelte autofixer had no issues on App, CastPanel, or Composer and only intentional `{@html}`/effect/`bind:this` suggestions elsewhere; `impeccable detect --json` returned `[]`; `npm audit` reports 2 low dev/build-tooling findings with no fix available, production audit clean.** The release builder produced a 74-file deterministic ZIP at `release/dist/couldhappen-0.1.0.zip` (SHA-256 `0970bc6e...`); a clean release workspace passed 35 Python tests, 4 Chromium tests, `npm ci`, check, unit, build, helper claim/UUID initialization, first baseline commit, and a clean checkpoint. See [validation results](../validation-results.md) for exact scope and caveats. Test helper/Vite child processes were stopped by the runner. No services were started against the real workspace; no story session is armed. No real scene/card/account/model input was invented.

## Distribution and story-workspace decision (accepted 2026-11-05)

The packaging boundary is now accepted:

- [ADR-0](../decisions/ADR-0-use-markdown-architectural-decision-records.md) records the MADR convention.
- [ADR-1](../decisions/ADR-1-separate-story-workspaces.md) establishes a clean, separately versioned story workspace for every real story.
- [ADR-2](../decisions/ADR-2-publish-clean-release.md) establishes a deterministic release ZIP rather than the development history, under MIT.
- [Distribution and workspaces](../designs/distribution-and-workspaces.md) is the accepted normative packaging contract.
- The approved design contains an accepted amendment superseding its original distributable-workspace statement for packaging.

The baseline is tagged `baseline-2026-11-04` at `4db8ed2`. Do not run a durable story in this development repository; use a disposable copy for a smoke test only. The next step is to create a clean story workspace from the release ZIP, run the host/story acceptance test there, update docs from findings, then run the final `egm-drift-report` over the curated normative documents before publishing.

On 2026-11-05 the author selected **MIT** and a **release ZIP first**. A manual fresh-context Goldfish-style review returned **accept with changes**; the documented P1 findings were revised, and the author authorized skipping the focused re-review and moving forward. The review was not a certified EGM Goldfish review. See [review](../reviews/2026-11-05_packaging-goldfish-review.md) and [resolution record](../reviews/2026-11-05_packaging-resolution.md).

The release candidate is `release/dist/couldhappen-0.1.0.zip` (SHA-256 `0970bc6e...`, source commit `5db91d0`, 74 files). It was smoke-tested in a clean workspace outside this repository: 35 Python tests, 4 Chromium tests, check, unit, build, claim/UUID initialization, first baseline commit, and clean checkpoint. The artifact is ignored by Git; reproduce it with `python scripts/build_release.py --ref <tested-commit>`.

## First story-workspace acceptance test (2026-11-05, opencode)

The author ran the first real host/story acceptance test with opencode in a separate `CouldHappen-story` workspace. **It was largely successful.** Observed: setup from prerequisites through claim, Git baseline, and clean checkpoint; a real PNG card import with a stripped public portrait and deliberate cast disclosure; many Story and Director exchanges under pause/release with per-exchange commits; the writer building its own `tools/combat.py` method; Director Undo restoring an earlier exchange with verbatim archive and `awaiting_director`; a full reset archived the same way; and a second, fresh session that reconstructed the state accurately from the maintained files alone. Once a background `wait --timeout 0` was running, browser input woke the writer with no chat prompt.

Two problems were found and fixed. The main one: after setup the writer did not leave a wait running, so the first Director message went unread until the player prompted in chat. The skill (`SKILL.md`, `capabilities.md`, `setup.md`, `writing.md`), setup docs and their release templates, reference hosts, public contract, and design now require a standing wait from the end of setup and before every turn ends, preferring a background `wait --timeout 0` the host reports back on. Undo, reset, card import, and fresh-context reentry worked. The `portrait` path papercut was also fixed: `import-card` prints `source_path`, and `portrait` accepts the imported original or its folder. See [validation results](../validation-results.md). Both fixes ship in release **0.1.1** (`release/dist/couldhappen-0.1.1.zip`, SHA-256 `d4ea6a69...`, source `3676597`, 74 files), which passed a clean-workspace smoke test. Neither fix has been re-run on a real host yet.

After 0.1.1 the author noted that Claude Code does not discover skills in `.agents/skills/`. A thin entry point, `.claude/skills/couldhappen/SKILL.md`, now hands off to the canonical skill and ships in the release; the manifest forbids every other `.claude/` path. All four hosts — opencode, Codex CLI, Claude Code, and Pi with OpenRouter — are marked **experimental** in [reference hosts](../reference-hosts.md), with no required test order. This ships as release **0.1.2** (`release/dist/couldhappen-0.1.2.zip`, SHA-256 `34f21988...`, source `dd17b1e`, 75 files), which passed the same clean-workspace smoke test; Claude Code's discovery of the entry point has not been observed yet.

## Remaining work

1. **Re-test the fixes.** Run a fresh story workspace from the current release on any host and confirm the standing wait starts at the end of setup with no chat prompt, and that `portrait` accepts the original card path.
2. **More host observations (experimental, any order).** Codex CLI, Claude Code (including skill discovery through `.claude/skills/`), and Pi with OpenRouter remain untested; opencode has one successful run. Use a human-selected model and a clean story workspace. Observe normal trust/permission/activation, real waits/renewals and their overhead, browser exchanges, Director discussion, production blocks, deliberate closure, and native dirty/clean completion. Native checkpoint hooks have not been observed on any host. Do not alter active hook configuration merely as implementation cleanup; merge reference examples only in the intended player setup.
3. **Supplied scene/cards.** Done once on opencode (a real PNG card, portrait disclosure, fresh-context reentry, Director Undo). Fresh-context *continuation of fiction* after reentry has not yet been observed. Synthetic browser fixtures are labelled and never saved in the real public logs/cast.
4. **Literal comp gates.** `.impeccable/build/state.json` remains at `spec` with `plates`/`hero`/`sections`/`motion`/`responsive` pending. Closing them honestly would require the comp's illustrative scene/portraits, which the approved boundary says not to fabricate or copy into public files. Do not use `--force` without an explicit user downgrade of comp authority; do not claim a pixel pass.
5. **Dependency audit.** The two low findings are dev/build-tooling-only under `@sveltejs/vite-plugin-svelte`/`deepmerge`; production audit is clean and the browser-served bundle does not include deepmerge. Approved pins remain. A fix requires an upstream patch or a deliberate override; no override was applied.
6. **Optional improvement.** If a future supplied portrait library reveals layout problems with the 4:3 contain treatment, revisit portrait framing with the Director rather than transforming supplied card pixels by default.

## Repro commands

At root: `python -m unittest discover -s tests -p "test_*.py"`; `python -m helpers validate --root .`; `python tests/run_browser.py`.

In web: `npm ci` if needed; `npm run check`; `npm run test:unit`; `npm run build`. Chromium was installed by `npx playwright install chromium`. The browser runner starts temporary services using discovered Python/Node, accepts executable overrides, and never uses real story data. Its service log must stay outside Playwright's output directory on Windows.

UI review captures are in `.impeccable/review/` (`desktop.png`, `mobile.png`, `tablet.png`, `narrow-320.png`, `mobile-cast.png`, `director.png`, `focus.png`, `blocked.png`, `recovery.png`, `recovery-director.png`, `desktop-draft.png`, `mobile-draft.png`, `empty.png`, `empty-mobile.png`). They use clearly labelled synthetic fixture data and abstract placeholder portraits, not supplied cards. The browser suite also writes its own `desktop.png`/`mobile.png`/`empty.png` when run; the richer review set is recaptured separately afterward.

## Spec gaps

- **Public PNG validation depth (resolved 2026-11-04 by implementation).** The design requires `GET /api/assets/<relative-name>` to serve "only referenced, validated public PNG assets." The implementation now treats that as a read-time requirement: `helpers.files.public_asset` resolves the path, bounds the read, validates PNG signature/chunk structure/CRCs/critical order via `helpers.cards.chunks`, and only then hashes or serves the bytes. `files.snapshot` and `helpers.bridge` both use it. Tests cover a referenced corrupt PNG failing snapshot validation and returning 404 from the asset route, plus unreferenced assets remaining unavailable. The portrait helper still validates at creation. This is the stricter reading of the contract; the author may override it if creation-time validation was intended as sufficient.
- **Literal comp pixel gates (open, recorded).** The approved Woven comp's scene prose, portraits, and biographies are illustrative. The app implements the comp's topology, palette, type hierarchy, and signature interlace while public logs/cast stay empty. The literal spec/plates/hero sequence cannot be completed without fabricating the illustrative assets, so it remains open at `spec`; this is not a pass and not a reason to restart the visual direction. See `.impeccable/composition-selection.md` and the local `.impeccable/build/state.json` note.
- **Native assurance remains guidance-only until observed.** The supplied checkpoint examples are not activated. A dirty-tree check establishes recorded changes, not semantic completeness of the world record; forced interruption or untrusted hooks can bypass checks.

## Evidence levels

Keep these separate when resuming:

- **Implemented behavior:** source, formats, helper controls, UI states, and scripts described above.
- **Automated checks:** Python/unit/Chromium/check/build/autofixer/detector results in [validation results](../validation-results.md). These are representative tests, not exhaustive proofs.
- **Visual observations:** the independent reviewer's screenshots and verdict at the stated viewports, with synthetic data. They do not establish a supplied portrait's appearance.
- **Actual host/story demonstrations:** **not run.** No Codex, Claude Code, or Pi session; no supplied cards; no fresh-context continuation; no actual Undo. File existence, source inspection, configuration, or a reviewer's confidence is not evidence of those outcomes.

## 2026-11-05 — Documentation restructure

The documentation was restructured: release text is now the tracked file with `<!-- dev-only -->` blocks stripped by the builder (prose templates under `release/` were removed); history moved to `docs/history/`; the design's alternatives and implementation plan moved to [design alternatives and implementation plan](design-alternatives-and-plan.md) with its amendments folded into the design text; and the README, progress handoff, and host notes were reduced to one home per fact.

## 2026-11-05 — Skill clarity pass and local-path cleanup

The writer skill was rewritten in plain sentences with a glossary and "Always"/"Never" lists, then checked by a fresh-context reviewer answering nine scenarios from the skill alone. Its findings were verified against the helper and fixed (pending entries re-trigger a wait; foreground-only hosts cannot keep a wait after a turn; pause needs ownership; Undo keeps human entries; repair versus substantial fiction; the portrait filename in `cast.json`). A session-log checklist was added to the [validation procedure](../validation.md). Absolute paths into the author's home directory under `docs/` became plain citations; paths remain in captured evidence (`goldfish_reviews/`, `.impeccable/`, `.research/`) and in `.codex/hooks.json`.

## 2026-11-05: Claude Code test and fixes

The author ran a 0.1.4 workspace with Claude Code on Sonnet 5.5. Skill discovery and the standing wait worked; a host restart silently ended the wait. Fixes: the skill checks for a running wait at the start of every turn a wait did not start; `python -m helpers stop` replaces stopping the helper by process name; the helper always writes UTF-8; the package tests build their own empty workspace instead of copying live public files. The writer's exported Director prompt (sheet, themes, dice, scene images) suggests upstreaming the sheet panel and defining a pack format; neither is done yet.

## 2026-11-05: Drift triage fixes

The ten triage items from the drift report were resolved. Code: a retry of an already-saved entry now returns 200 while saving is closed (`Bridge.existing` runs before the permission check); `writer release` requires ownership; the story template's checkpoint exclusions are empty; the release builder reopens the ZIP and verifies file list, null workspace ID, and empty public templates. Documents: the UUID is created by `serve`; drafts live in session storage; stale design lines were replaced with links; the public contract lists every control operation, error code, Vite deny rule, and the checkpoint, import-card, and portrait results; the distribution design records the secret-scan allowlist, release `.gitignore` patterns, and link-check scope. Nested repositories stay supported in code, and setup now checks `git rev-parse --show-toplevel` before the baseline commit.
