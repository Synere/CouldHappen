# Packaging review resolution — 2026-11-05

- **First review:** [manual Goldfish-style review](2026-11-05_packaging-goldfish-review.md) — accept with changes
- **Author decision:** approved the documented defaults and authorized skipping the focused re-review
- **Focused re-review:** not run; no certified EGM claim
- **Decision status:** ADR-1/ADR-2 and [Distribution and workspaces](../designs/distribution-and-workspaces.md) accepted

## Finding resolution

| Finding | Resolution |
| --- | --- |
| P1-1 release contents not enforceable | `release.manifest.json` is the normative allowlist/template/required/forbidden/content configuration. `scripts/build_release.py` reads a named commit, applies the manifest, checks required/forbidden paths, scans text for secret markers, verifies relative Markdown links, builds a deterministic ZIP, embeds `release.json`, and writes a SHA-256 sidecar. `tests/test_release.py` builds twice, compares bytes, checks required/forbidden paths, template state, and metadata. |
| P1-2 privacy not a mechanism | Accepted privacy model: story workspaces private/local by default; imports and private records tracked as the archive unit; public remote exposes them; redacted export is not v1; development repository requires a history/secrets audit before public exposure. Release ZIP excludes runtime, imports, public assets, `.env*`, and development material. |
| P1-3 baseline/UUID contradiction | Release ZIP carries a null UUID. Story creation runs `npm ci`, validates, setup/claim writes the UUID, then the first baseline commit includes it; `checkpoint check` follows. Confirmed in a clean release smoke workspace. |
| P1-4 approved design/public contract authority | The approved design now states that durable stories run from the accepted release ZIP, with an accepted amendment and normative precedence. The public contract is self-contained for runtime. Release templates replace the development README/setup. |
| P1-5 update path deferred | V1 explicitly has no automatic updater or promised in-place update path. Updates are manual replacement/merge while preserving story data. A future updater is later scope. |
| P2 release templates/notices | Release templates exist for README, START_HERE, couldhappen.json, `.gitignore`, docs index, setup, reference hosts, and public files. Font OFL notices ship; dependency licenses remain with installed packages. |
| P2 empty-file/work.json ambiguity | Release templates define title-only logs and schema-valid empty cast/work; canonical confirmation checklist covers them. |
| P2 OS metadata/close validation | Dev/release `.gitignore` ignore common OS/editor metadata and release test output. `writer close` now validates public records before disarming; a bridge regression test covers invalid records. |
| P2 MIT scope/third-party material | MIT is recorded as covering the package source, not user stories or imported card material. “No commercial sale planned” is an intention, not a restriction. |
| P2 inconsistent checklists | One canonical checklist lives in [Distribution and workspaces](../designs/distribution-and-workspaces.md#confirmation-checklist); both ADRs reference it. |

## Release evidence

- Source commit: `5db91d0` (accepted packaging state)
- Release artifact: `release/dist/couldhappen-0.1.0.zip`
- SHA-256: `0970bc6ec26bb6bf84b747728050e3d8187706edd032326084f953d8cad27fb5`
- Files: 74
- Release tests: 2 passed (`test_release`), including byte-identical rebuilds
- Full development Python suite: 37 tests passed
- Release workspace smoke: 35 Python tests passed; 4 Chromium tests passed; `npm ci`, `svelte-check`, unit tests, and Vite build passed
- Release smoke setup: helper claim initialized a UUID; the first Git commit included it; `checkpoint check` returned clean
- The release workspace was created outside the development repository and resolved its own Git top level

The release artifact is ignored by Git. The source commit, manifest hash, and SHA-256 identify the tested candidate.

## Limits

- The focused re-review was skipped by author authorization.
- This is not a certified EGM Goldfish review and does not establish native-host, supplied-card, narrative, fresh-context, or Undo evidence.
- The release zip still requires npm registry access during setup; it is provider-neutral, not offline-self-contained.
- The release smoke is not the actual story acceptance test.
