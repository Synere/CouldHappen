# Validation results — 2026-11-04

Implementation evidence, recorded in Asia/Manila. This is not a compatibility certificate or an actual scene report. The approved first-scope application surface and its Woven UI finish are implemented and mechanically checked; native-host execution, supplied story/cards, fresh-context continuation, checkpoint-limited Undo, and the literal comp pixel gates remain unperformed or intentionally open. See the [implementation handoff](implementation-progress.md).

Runtime observed: Windows; Python 3.14.2; Node 25.6.0; npm 11.8.0; Git 2.53.0.windows.1. Exact approved frontend pins installed successfully and generated `web/package-lock.json`. The targeted minimum runtimes were not separately exercised.

## Current check matrix

| Check | Observed outcome |
| --- | --- |
| `python -m helpers validate --root .` | Valid empty public workspace. Does not initialize story content or claim ownership. |
| `python -m unittest discover -s tests -p "test_*.py"` | 38 tests passed (2026-11-05, after the portrait-path test was added). Includes the public-PNG, writer-close validation, and release-builder tests. |
| `npm run check` in web | Zero errors and zero warnings. |
| `npm run test:unit` in web | Four tests passed. |
| `python tests/run_browser.py` | Four Chromium tests passed in the development suite; a further four passed from the unpacked release workspace. |
| `npm run build` in web | Passed; optional distribution output is ignored. |
| `python scripts/build_release.py --ref refs/heads/publish` (0.1.7 public build, 2026-11-05) | Rebuilt from the public one-commit history (`535dbae`, same tree as `main` at `af8ea9b`), SHA-256 `d21a43f28996a8fed9f72864eaafbae385105bb8bc13fd4136ccb125e7f3a5b6`; smoke test 18 passed, 0 failed. Published as GitHub release `v0.1.7` on `Synere/CouldHappen`. Supersedes the private-commit build below. |
| `python scripts/build_release.py --ref HEAD` (0.1.7, 2026-11-05) | Built `release/dist/couldhappen-0.1.7.zip`, 75 files, source `cc90319`, SHA-256 `45ff03ab277f1bf24640d4e41468f3657804c99e16296123884b914c178659b1`. First AGPL-3.0-or-later release ([ADR 0003](decisions/0003-license-agpl.md)); includes the drift fixes (retry identity before permission, ownership on release, empty story checkpoint exclusions, ZIP self-verification). The builder now re-reads the finished ZIP. |
| `python scripts/smoke_release.py release/dist/couldhappen-0.1.7.zip` | 18 passed, 0 failed. |
| Pre-publish tree audit (2026-11-05, Sonnet subagent, read-only, 130 tracked files) | No secrets, personal emails, story content, or machine-specific files tracked; one local path prefix in the drift report removed. Remaining cosmetic: some historical docs cite `.impeccable/` paths without a "kept locally" marker. |
| `python scripts/build_release.py --ref HEAD` (0.1.6, 2026-11-05) | Built `release/dist/couldhappen-0.1.6.zip`, 75 files, source `23ef252`, SHA-256 `a55911e49182a44362a292d7e0d397a9654f82fd6ac644197c40d1bc5aa9bdab`. Adds `python -m helpers stop`, UTF-8 helper output, isolated package-test fixtures, and the skill's wait check after a host restart. |
| `python scripts/smoke_release.py release/dist/couldhappen-0.1.6.zip` | 18 passed, 0 failed (45 Python tests inside the release). Stop, closing, and the restart check are not exercised by the smoke test. |
| `python scripts/build_release.py --ref HEAD` (0.1.5, 2026-11-05) | Built `release/dist/couldhappen-0.1.5.zip`, 75 files, source `0afef77`, SHA-256 `88e079b3456b21e79bdd5617599481beb4f2bc0d55f8d7507b192d91da42f509`. Adds the "Closing the game" procedure to the writer skill and a "Stop" section to the README. |
| `python scripts/smoke_release.py release/dist/couldhappen-0.1.5.zip` | 18 passed, 0 failed. The smoke test does not exercise closing; that needs a real session. |
| `python scripts/build_release.py --ref HEAD` (0.1.4, 2026-11-05) | Built `release/dist/couldhappen-0.1.4.zip`, 75 files, source `ba44ae2`, SHA-256 `caf6bbdeba72c677d35ef32f68192a76d5fc33b8501083551d4150765e3235b4`. Adds the README note telling players to ask their agent to set up. |
| `python scripts/smoke_release.py release/dist/couldhappen-0.1.4.zip` | 18 passed, 0 failed: release metadata, null UUID, no dev-only text, npm ci, validate, helper, claim and UUID, reader snapshot match, quiet wait, one baseline commit, clean checkpoint, Python tests, check, unit, build, Chromium. No host/story session run yet. |
| `python scripts/build_release.py --ref HEAD` (0.1.3, 2026-11-05) | Built `release/dist/couldhappen-0.1.3.zip`, 75 files, source `d07ecdd`, SHA-256 `d16a3694e6f7d38b6cb6aa404a48e1f87fe7760d913fe3d0c831a9c2b07468ab`. First release built from single-source docs (dev-only blocks stripped) with the rewritten writer skill. |
| 0.1.3 clean release smoke workspace | 36 Python, check, 4 unit, build, 4 Chromium, validate, claim, quiet wait, one baseline commit, clean checkpoint, and the portrait guidance message all passed; no shipped Markdown contains a dev-only marker. No host/story session run yet. |
| `python scripts/build_release.py --ref HEAD` (0.1.2, 2026-11-05) | Built `release/dist/couldhappen-0.1.2.zip`, 75 files, source `dd17b1e`, SHA-256 `34f21988a6b0d87925ce2fc2dc7755f28be0bc03e67d199585f5e25fc40ef3aa`. Adds the Claude Code skill entry point. |
| 0.1.2 clean release smoke workspace | Same checks as 0.1.1, all passed (36 Python, check, 4 unit, build, 4 Chromium, validate, claim, quiet wait, one baseline commit, clean checkpoint). `.claude/skills/couldhappen/SKILL.md` is present and tracked in the baseline commit; `.claude/settings.local.json` is ignored. Claude Code discovering the skill was not observed. |
| `python scripts/build_release.py --ref HEAD` (0.1.1, 2026-11-05) | Built `release/dist/couldhappen-0.1.1.zip`, 74 files, source `3676597`, SHA-256 `d4ea6a6965c33efab3d8c171cf4f4ba22cc5666e5f279f2b22d1fab2e3f428bb`. Includes the standing-wait skill fix and the portrait-path fix. |
| 0.1.1 clean release smoke workspace | Outside any repository: 36 Python tests, `npm ci`, check (0 errors/warnings), 4 unit, build, and 4 Chromium tests passed; validate clean; helper claim initialized a UUID; a quiet `wait --timeout 2` returned exit 3; one baseline commit at the workspace root; `checkpoint check` clean; `portrait` on a non-card file returned the new guidance message. No host/story session was run against 0.1.1. |
| `python scripts/build_release.py --ref HEAD` (0.1.0) | Built `release/dist/couldhappen-0.1.0.zip`, 74 files, source `5db91d0`, SHA-256 `0970bc6ec26bb6bf84b747728050e3d8187706edd032326084f953d8cad27fb5`; release-builder tests compare byte-identical rebuilds. |
| Clean release smoke workspace | 35 Python tests, 4 Chromium tests, `npm ci`, check, unit, and build passed; helper claim initialized a UUID; the first baseline commit contained it; `checkpoint check` returned clean. |
| `python -m helpers checkpoint check --root .` | Returned `{"status":"clean","paths":[]}` after commit `e5f3eaf`. This establishes recorded Git changes, not semantic completeness of the world record. |
| Svelte autofixer | Invoked on App and all four components after the final edits. App/CastPanel/Composer had no issues. Conversation has generic `$effect`/`bind:this` suggestions for intentional DOM scroll synchronisation and the scroll-element reference. ProseEntry reports the generic `@html` XSS warning for sanitized authored Markdown. Browser tests exercise actual script/img/SVG injection refusal. This is not a clean-findings-list claim. |
| `impeccable detect --json` | Returned `[]` on App, all four components, and `styles.css` after the final edits. Not a whole-surface ship proof by itself. |
| `git diff --check` | Passed for tracked changes at the time of this record. |
| Existing `.codex/hooks.json` | No diff; checkpoint examples were not activated. |

## UI finish review and documentation

The independent Impeccable finish reviewer ran with fresh context against the approved Woven comp, the direction contract in `.impeccable/surfaces/web-src-app-svelte.md`, the craft floor, and the review screenshots. Its first pass returned `fix` for five findings:

1. Recovery views sliced the first entry at the top — fixed by entry-aware bottom settling and a second animation-frame measurement; recaptured.
2. `blocked.png` showed blank cast portrait frames — fixed with an initial-letter fallback behind the image and an image-completion wait in the capture; recaptured.
3. The cast drawer did not contain focus — fixed with `inert` background layers, `role="dialog"`/`aria-modal` while open, focus to the close control, Escape, and focus return to the Cast toggle. Browser assertions cover focus, Escape, inert removal, and dialog attributes.
4. The build-state record remains at `spec` with later phases pending — **not fixed**. No sanctioned skip exists; `--force` is reserved for an explicit user downgrade of comp authority, which was not given. This is an open record-level exception, not a pixel pass.
5. Recovery copy contradicted the Director location — fixed with channel-aware banner text and a recovery-specific composer helper; recaptured.

A verdict pass confirmed fixes 1, 2, 3, and 5 resolved, no new material regression, and called the UI shippable at this scope; the desktop composer-edge sliver was still present. After the fade stacking was corrected, a final capture check found the sliver resolved and returned `ship` for that check. The build-state record finding remains open and was explicitly excluded from the check. There is no whole-run pixel-gate pass. The independent documenter then wrote `DESIGN.md` and `.impeccable/design.json` from the built system; it changed no application source, PRODUCT.md, approved comp, or documentation.

## Public PNG validation

The earlier unresolved policy gap is closed under the stricter reading of the design's "referenced, validated public PNG assets" requirement. `helpers.files.public_asset` now resolves the public path, enforces the 32 MiB bound, validates PNG signature/chunk structure/CRCs/critical order through `helpers.cards.chunks`, and only then hashes or serves the bytes. `files.snapshot` and the bridge asset route both use it. New tests cover a referenced corrupt PNG failing snapshot validation and returning 404 from `/api/assets/`, plus an unreferenced valid asset remaining unavailable. The portrait helper still validates at export. The author may override this if creation-time validation alone was intended.

## Browser and UI coverage

Browser checks cover saved entries and exact request identity after a deliberately dropped receipt, uncertain absent text across generation change without replay, same-ID revision, Markdown sanitization, separate drafts, blocked controls, refresh, earlier reading position, actual CSS HMR, keyboard submission, mobile cast, drawer focus/Escape/inert/dialog behavior, recovery waiting, no horizontal overflow at the tested narrow widths, and empty setup. The recovery case reloads after the generation change instead of racing the next poll with a stale generation. Filesystem probes cover explicit private/runtime paths, encoded traversal, and /@fs through Vite plus Python asset traversal; a temporary source module importing the existing private fixture from the temporary workspace is refused by Vite without leaking its contents. Tests are representative, not completion of every planned boundary.

Screenshots in `.impeccable/review/` were recaptured from temporary synthetic fixtures after the UI fixes: `desktop.png`, `mobile.png`, `tablet.png`, `narrow-320.png`, `mobile-cast.png`, `director.png`, `focus.png`, `blocked.png`, `recovery.png`, `recovery-director.png`, `desktop-draft.png`, `mobile-draft.png`, `empty.png`, and `empty-mobile.png`. The cast portraits are abstract diamond placeholders, not supplied or fabricated card portraits. The browser suite also writes its own `desktop.png`/`mobile.png`/`empty.png` from its red 1-pixel fixture; the richer review set is recaptured separately afterward. No test content is saved in the real public logs/cast. Temporary test processes were terminated by their owned handles and temporary data removed.

## Earlier checkpoint evidence (superseded where counts differ)

The previous handoff recorded 31 Python tests; the focused caret regression was already in the suite when this continuation began (32 tests). This session added two public-PNG tests, one writer-close validation test, and two release-builder tests, for a current total of 37, plus the UI finish and release changes. Earlier details retained below for provenance:

Python checks cover exact LF-normalized body roundtrips (reserved markers, backslashes, trailing newlines), malformed records, cross-log duplicate IDs and recovery pointers, actual loopback requests, an accepted append held behind a barrier while pause waits, refusal of later appends, retained human+writer entries after release, identical retry/conflict, origin/control protection, body limits, last coherent view on partial files, startup closure, production/edit independence, and recovery pending selection. Card fixtures independently construct PNG chunks and compare IDAT bytes while stripping public text metadata; flat V1/V2/V3 JSON and PNG extraction are exercised. Scoped Git checks use temporary repositories, including a nested workspace. Python native adapters are tested for clean/dirty/error/inactive translation. Pi's extension is source-inspected only. Added coverage: exclusive/stale helper locks with age-only recovery refused, bounded wait timeout/exit 3 and CLI error/exit 2 paths, atomic replacement failure preserving the previous file, malformed cast variants and symlink/junction asset escapes, PNG critical-structure/order/header and metadata/source limits, and checkpoint inspect/check exclusion agreement plus Git-style glob boundaries, bracket classes, rename, deletion, unmerged, and parent-repository cases. The `private/*.md` regression confirms inspection no longer hides `private/nested/kept.md` while checking reports it dirty; the `private[!x]kept.md` case confirms a negated bracket class does not cross `/`.

Browser checks cover the current reader/composer/cast behavior described above. The reading-position test still proves an earlier anchor survives a new writer entry, refresh, and actual CSS HMR; the drawer test now also proves focus return and inert removal. These remain representative tests, not an exhaustive security or compatibility proof.

## Dependency audit review (unchanged, current)

Command: `npm audit --json` in `web/` with Node 25.6.0 / npm 11.8.0. Result: 2 low, 0 moderate, 0 high, 0 critical. `npm audit --omit=dev` reports zero.

| Finding | Path | Shipped or dev-only | Fix requirement |
| --- | --- | --- | --- |
| deepmerge 4.3.1 prototype poisoning, GHSA-gcqx-w48m-w2h4 (CWE-1321, CVSS 5.3) | transitive under `@sveltejs/vite-plugin-svelte@7.3.1` | Dev/build-only. `deepmerge` is marked `"dev": true` in `package-lock.json`; `npm ls deepmerge --all --omit=dev` is empty; the plugin is a `devDependency`; the browser-served `dist` bundle does not reference deepmerge. The approved ordinary play mode uses the Vite dev server, so it is present in that local server-side toolchain. | No `fixAvailable`. deepmerge 4.3.1 is the latest published version and is inside the advisory range; the latest plugin still declares `deepmerge: ^4.3.1`. A fix needs an upstream patch or a deliberate override (not applied because it would replace an approved pin). |
| @sveltejs/vite-plugin-svelte 7.3.1 | direct devDependency | Dev/build-only; not part of the browser-served production bundle, but used by the approved Vite live-play server. | Inherits the deepmerge finding; same upstream dependency fix. |

Impact: the advisory concerns `mergeObject()` prototype poisoning when untrusted objects are merged. The plugin uses deepmerge for server-side build/dev configuration; the app does not pass untrusted runtime input through it. This is a low-severity local-tooling observation, not an observed application exploit. Approved pinned versions were not changed.

## Story-workspace test session — 2026-11-05 (opencode)

The author ran two sessions in a separate `CouldHappen-story` workspace using opencode (not one of the three planned reference hosts; the model is not recorded in the exported logs) and supplied the exported transcripts. Findings:

| Observation | Outcome |
| --- | --- |
| Setup | Prerequisites, `npm ci`, validate, helper and Vite, claim, Git baseline, browser save, a 30-second serviced wait, and clean checkpoint all succeeded. Vite's first start failed with a native memory-allocation error with under 1 GB free; a retry succeeded. |
| **Standing wait after setup** | **Failed.** The writer treated the setup wait as a one-off check, reasoned that a background `--timeout 0` wait "never completes", and ended the turn with nothing listening. The player's first Director message stayed unread until they asked in chat why it was not being checked. Cause: the skill said to *verify* a wait during setup and to service one after prose, but never to leave one running before a turn ends. Fixed by the skill, setup, contract, and design amendment of 2026-11-05. |
| Background wait on opencode | After the prompt, the writer ran `python -u -m helpers wait --root . --timeout 0` as a background job; opencode reported its completion, and browser Story and Director entries woke the writer without chat prompts across many exchanges, renewed after each one. |
| Card import and portrait | `import-card` preserved the PNG card under `imports/<hash>/`. `portrait` first rejected the original download path ("must be a preserved imported source.png") and succeeded with the imported `source.png`. Fixed 2026-11-05: `import-card` now prints `source_path`, and `portrait` accepts the original file (once imported) or the import folder, always reading the preserved copy. |
| Play, Director discussion, writer methods | Several Story and Director exchanges under pause/release with per-exchange commits; the writer built its own `tools/combat.py` and combat note as a retained method. |
| Director Undo | Restored the story to an earlier exchange, archived removed entries verbatim under `docs/writer/archive/`, retained methods, set `awaiting_director` with a new question, and kept Story closed. A later full reset was archived the same way. |
| Fresh-context continuation | The second session reread the maintained files alone and accurately reported mode, question ID, permissions, empty canon, retained methods, and archive, without claiming ownership or writing. |
| Native checkpoint hooks | Not installed or observed in this test. |

## Story-workspace test session — 2026-11-05 (Claude Code, 0.1.4)

The author ran one session in `couldhappen-0.1.4-test`, unpacked from the 0.1.4 release, with Claude Code (desktop app) on Sonnet 5.5, about 75 minutes and 27 commits. Evidence: the session transcript and the workspace's Git history.

| Observation | Outcome |
| --- | --- |
| Skill discovery | Claude Code loaded the `couldhappen` skill through `.claude/skills/couldhappen/`. |
| Standing wait | **Held.** The writer started a background `wait --timeout 0` after setup and after every handled entry (about 30 cycles), each chained after its reply, pause, release, and commit. |
| Host restart | **Failed once.** The author restarted Claude Code to refresh an environment variable; the background wait ended silently, and on resuming the writer handled the chat message without checking for a wait. The author noticed. Fixed after the session: the skill now says to check for a running wait at the start of every turn a wait did not start. |
| Helper restart | After editing Python, stopping the helper by matching process names hit an empty PID ("Idle (0)") and a host safety refusal, then needed `--previous-helper-stopped`. Fixed after the session: `python -m helpers stop` drains, shuts down, and releases the lock. |
| Windows encoding | `helpers entry` failed on non-ASCII text under the legacy console code page; the writer worked around it with `PYTHONUTF8`. Fixed after the session: the helper always writes UTF-8. |
| Package tests in a story workspace | The included Python tests copied the live public files and failed once a story existed. Fixed after the session: tests build their own empty workspace. |
| Creative initiative | The writer built a dice script, private rules and campaign notes, an optional `public/sheet.json` character sheet with helper validation and a contract note, scene themes, a "Picture scene" button with an OpenAI image script, and click-to-enlarge pictures, and exported them as a setting-free Director prompt. |
| Credentials | Claude Code refused a key lookup as credential exploration; the writer did not work around it and asked the author. |
| Card handling and notes | Card treated as source material; `START_HERE.md` updated after every turn, spoilers in a private note. |
| Closing, Undo, native hooks | Not exercised. |

## Host and creative observations

| Host / creative observation | Status |
| --- | --- |
| opencode story-workspace test (2026-11-05) | Run, largely successful; see the section above. Standing-wait failure found and fixed in the skill; not re-run after the fix. Host status: experimental. |
| Codex interactive CLI browser loop, waits/renewals, trusted native checkpoint execution | Experimental; not run. Python wrapper tests are not native-host activation evidence. |
| Claude Code interactive CLI equivalent | Experimental; one largely successful 0.1.4 session (Sonnet 5.5, desktop app). Skill discovery observed. |
| Pi 1.5.0 + human-selected native OpenRouter model | Experimental; not run; published extension docs/types inspected, extension not compiled/loaded in Pi. |
| Actual prompt/card short scene and Director discussion | Not run; assets/prompt not supplied. |
| Actual fresh-context continuation using maintained files alone | Run once on opencode (2026-11-05): accurate read-only report from files alone. Fiction was not continued in that session. |
| Director Undo against actual scene history, preserved improvements, and new-direction continuation | Run once on opencode (2026-11-05): restore, verbatim archive, retained methods, and `awaiting_director` observed. |
| Independent Impeccable finish review | Run with fresh context on synthetic rendered evidence. First pass `fix`; four UI findings fixed and recaptured; final capture check `ship` for the rendered UI surface. Build-state record finding remains open. This is not native-host or actual-story evidence. |
| Impeccable design documentation | `DESIGN.md` and `.impeccable/design.json` authored by the independent documenter from the built system. |
| Literal comp spec/plates/hero gates | Open at `spec`; no pass claimed. The comp's illustrative scene/portraits are not reproduced. Adaptation boundaries are recorded in `.impeccable/composition-selection.md` and the surface brief. |
