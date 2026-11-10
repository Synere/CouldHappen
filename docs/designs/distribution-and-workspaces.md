# Distribution and story workspaces

- **Status:** Accepted — 2026-11-05
- **Date:** 2026-11-05
- **Related:** [ADR-1](../decisions/ADR-1-separate-story-workspaces.md), [ADR-2](../decisions/ADR-2-publish-clean-release.md), [ADR-0](../decisions/ADR-0-use-markdown-architectural-decision-records.md), [approved design](couldhappen.md), [public contract](../public-contract.md)
- **Scope:** Packaging, release construction, story-workspace lifecycle, privacy, and update boundaries. This does not change the fiction model, UI direction, or runtime helper contract.

## Relationship to the approved design

The approved design describes the directory as the initial distributable workspace, with skills and source alongside story files. That remains the development baseline and the reason the package is copyable.

This design defines the distribution boundary:

* the **development repository** is upstream source and design evidence;
* a **release ZIP** is the clean, user-facing artifact;
* a **story workspace** is a private or local copy with its own Git history and runtime.

### Normative precedence

Now that this design is accepted:

* it supersedes the approved design's packaging statement (its former implementation step 1, kept in the [implementation plan](../history/design-alternatives-and-plan.md)) and the development README/setup instructions that lead with opening this repository for a durable story;
* the approved design remains normative for product behavior, the fiction model, UI direction, helper behavior, and the public runtime contract;
* the public contract is the normative runtime agreement for a workspace and must not depend on a document excluded from the release;
* ADRs explain rationale and alternatives; they do not replace this design or the public contract.

The current single-repository behavior remains the development baseline; durable stories run only in a clean release workspace.

## Definitions

| Term | Meaning |
| --- | --- |
| Development repository | The current repository. Holds full implementation history, design/EGM evidence, review artifacts, internal handoffs, release tooling, and development hooks. |
| Release ZIP | A deterministic archive built from a tested commit using `release.manifest.json` and `scripts/build_release.py`. |
| Story workspace | A user-created repository or local directory unpacked from the release ZIP. Owns its own Git history, `.couldhappen/` runtime, public conversations/cast, imports, and private writer records. |
| Release manifest | `release.manifest.json`, the machine-readable allowlist, exclusions, template overrides, required paths, and content checks. |
| Runtime | Files under `.couldhappen/`; local, Git-excluded, never browser-served. |
| Story content | Public conversations/cast/work/assets, imports, and writer-created private records. |

## Normative model

1. **The development repository is upstream.** It is not the default place to run a durable story. Its history may contain development, design, review, and validation commits that a player should not inherit.
2. **Every real story has its own workspace.** The story workspace starts from the release ZIP. It has a fresh Git history, no development commits, and its own workspace UUID.
3. **A story workspace is independently copyable and archivable.** Copying it preserves its story, imports, records, and Git history without the development repository.
4. **The writer may edit its local source.** The skill, helper, frontend, methods, and records remain editable by design. Such edits are local story-workspace changes. They may be proposed upstream, but no automatic bidirectional merge exists.
5. **Development-only material is not shipped.** Design-review artifacts, planning/research/review history, internal handoffs, development hooks, release tooling, and implementation evidence stay upstream.
6. **Story privacy is the user's responsibility, with safe defaults.** Story workspaces are private/local by default. Imports and private records are tracked because the workspace is the archive unit. A public remote or shared archive exposes them; a redacted/shareable export is not yet implemented.
7. **The development repository's history is preserved.** This model does not rewrite or purge existing commits.
8. **Version 1 uses a release ZIP under the AGPL-3.0-or-later license** ([ADR-3](../decisions/ADR-3-license-agpl.md); MIT until 2026-11-05). A GitHub template or installer can be added later. No automatic updater is provided in v1.

## Story-workspace creation and baseline

The initial mechanism is a **release ZIP**:

1. download the release ZIP and verify its `.sha256` sidecar;
2. unpack it into a private/local directory;
3. `cd web` and run `npm ci`;
4. run `python -m helpers validate --root .` from the workspace root;
5. start the helper and Vite as described in `docs/setup.md`;
6. run `python -m helpers writer claim --root .` after inspecting the workspace; claim establishes writer ownership (the workspace UUID in `couldhappen.json` was already initialized when the helper started in step 5);
7. verify a browser save and a serviced wait;
8. initialize Git in the story workspace and make the first baseline commit, including the initialized UUID;
9. run `python -m helpers checkpoint check --root .`; it must be clean;
10. start a standing wait for the player's first entry before reporting setup complete.

A second path starts another story from an existing story workspace: `python -m helpers new-story --root . --destination <folder>` extracts that workspace's root (baseline) commit into a new, separate folder with a null `workspace_id`, no Git history, and none of the first story's records, imports, assets or edits. The new folder then follows steps 3 to 10 above. Only `validate` checks it (the command runs it before reporting success); the confirmation checklist below is written for the ZIP and applies to the new folder from step 6 on. The command needs a workspace with exactly one root commit, which the ZIP flow guarantees.

The release ZIP itself contains `couldhappen.json` with `workspace_id: null`. The **story workspace's first commit** contains the initialized UUID. There is no separate pre-setup baseline commit. The workspace must not be initialized inside an enclosing Git repository; `git rev-parse --show-toplevel` must resolve to the story workspace. Setup checks this before the baseline commit in step 8; the helpers themselves tolerate a nested repository, and the check keeps setup from committing into an enclosing one.

A created story workspace must contain:

* title-only `public/story.md` and `public/director.md`;
* schema-valid `public/cast.json` with an empty `characters` array;
* schema-valid `public/work.json` with `mode: "play"` and `director_question_id: null`;
* `couldhappen.json` with `schema_version`, `poll_interval_ms`, and checkpoint scope/exclusions; UUID present once the helper has started, and in the baseline commit;
* no `.git` from the development repository;
* no release/dev/private material that `release.manifest.json` excludes.

## Release construction

`release.manifest.json` is the normative release contents definition. `scripts/build_release.py` builds a ZIP from a named Git commit and refuses to build when the worktree is dirty unless explicitly overridden for development.

The builder must:

1. resolve the source commit and record it;
2. read tracked files from that commit, not the working tree;
3. apply the manifest include/exclude globs;
4. remove `<!-- dev-only -->` … `<!-- /dev-only -->` blocks from selected Markdown, refusing unclosed, nested, or inline markers; replace the data files listed under `templates` with their release variants in `release/`;
5. verify every `required` path is present and every `forbidden` path is absent;
6. scan text files for configured secret/private markers;
7. verify every relative inline Markdown link (`[text](path)`) resolves inside the ZIP, including one written inside a code span or fence, so example link syntax in shipped text is avoided; reference-style links and autolinks are not checked;
8. write a deterministic ZIP with sorted paths and fixed timestamps;
9. include `release.json` with schema version, package version, contract version, source commit, source date, manifest hash, and file count;
10. write a `.sha256` sidecar outside the ZIP;
11. print a JSON result containing the source commit, output path, file count, and archive hash.

The release is not “offline self-contained”: `npm ci` requires the npm registry, and the setup verifies the actual runtime. Python 3.11.4 or later is required. It is provider-neutral and independent of the development Git history.

## Distribution contents

The manifest is authoritative. The following summarizes it.

### Include

* `.agents/skills/couldhappen/` — portable writer skill, references, and optional Director packages (`packages/`, never applied by themselves; see the skill's package index). A package script may send text such as a scene description to a third-party provider the Director chooses, with a key from the writer's own environment; the package says so before use, and the workspace stores no key.
* `.claude/skills/couldhappen/` — a full, identical copy of the skill for Claude Code, which discovers skills only under `.claude/skills/`. The builder writes it from the manifest's `mirrors` map; nothing is tracked there, so the copy cannot drift from `.agents/` in the release. A pointer stub was used through 0.1.19; it relied on the writer choosing to open the real skill.
* `helpers/` — local file, card, wait, and checkpoint operations.
* `web/` — reader source, fonts and OFL licenses, configuration, tests, and the editable-reader README; excludes generated dependencies/build/test output.
* `tests/` — local mechanical checks, excluding release-builder tests and caches.
* `public/story.md`, `public/director.md`, `public/cast.json`, `public/work.json` — release templates with empty state.
* `imports/README.md` — import procedure; no imported source.
* `START_HERE.md` — writer reentry index with no story records.
* `couldhappen.json` — null-UUID template with required config.
* `.gitignore`, `.gitattributes`; the release `.gitignore` lists local credentials (`.env`, `.env.*`, except `.env.example` forms), runtime state (`.couldhappen/`, `.impeccable/`), per-user Claude settings (`.claude/settings.local.json`), Python caches and `.venv/`, `node_modules/`, `web/dist/`, test output, `release/dist/`, interrupted-save temp files (`.couldhappen-tmp-*`), and OS/editor metadata. Story content (`public/`, `imports/`, private records) is deliberately not ignored.
* `README.md` — user-facing README (development blocks removed).
* `DESIGN.md` — built visual system.
* `LICENSE` — AGPL-3.0-or-later, the unmodified license text.
* `docs/README.md` — documentation index (development blocks removed).
* `docs/setup.md` — setup (development blocks removed).
* `docs/public-contract.md` — self-contained runtime contract.
* `docs/reference-hosts.md` — host integrations and status (development blocks removed).
* `integrations/` — opt-in native examples, not active hooks.

### Exclude

* `.git/` — development history.
* `.impeccable/`, `docs/history/`, `docs/research/`, `docs/reviews/`, `.research/`, `goldfish_reviews/`.
* `docs/issues.md` and `docs/plans/`.
* `docs/decisions/`, `docs/designs/` — rationale and internal specifications remain upstream.
* `PRODUCT.md` — current file contains development evidence; no user-facing replacement yet.
* `docs/validation.md`, `docs/validation-results.md` — internal validation material that remains upstream.
* `release/`, `scripts/`, `release.manifest.json` — release tooling and data templates.
* `.codex/`, `.claude/` other than the skill copy, and other development hook configuration; keep opt-in `integrations/` examples only.
* Generated dependencies, builds, test output, runtime state, public assets, imported source, credentials, and `.env*`.

### Release text and templates

Shipped Markdown has one source: the tracked development file. Material only developers need is wrapped in `<!-- dev-only -->` and `<!-- /dev-only -->` lines, each alone on its line, and the builder removes it; the release text is therefore always a subset of the development wording. Only data files whose content genuinely differs use templates: `release/couldhappen.json`, `release/.gitignore`, and the four `release/public/*` files. They contain no development history, real story content, or credentials.

## Ownership boundaries

There is no enforced per-file “writer” ownership marker. The practical boundary is the repository plus path conventions:

| Area | Primary role |
| --- | --- |
| `public/`, `imports/`, `START_HERE.md`, writer-created private records/methods | Story and writer material |
| `helpers/`, `web/`, `tests/`, `.agents/skills/couldhappen/` | Shared editable package; the writer may change it locally |
| `.couldhappen/` | Local runtime; ignored by Git |
| `docs/decisions/`, `docs/designs/`, development evidence | Upstream development material; absent from the release |

A clean story repository is the strong boundary. Within it, the writer can still edit source; that is intentional creative initiative, not a defect. The writer should stage explicit relevant paths rather than sweeping the tree. The checkpoint check remains evidence of recorded changes, not authorship or semantic completeness.

Deliberate closure validates the public records before disarming and refuses invalid, dirty, or error results. Uncommitted writer experiments must be committed, stashed, or otherwise accounted for before closure; they are not silently swept into a checkpoint.

## Privacy and sharing

* Story workspaces are private/local by default. Do not publish one unless the user deliberately chooses to.
* Do not add the development repository as a remote or merge its history into a story.
* Imports, portraits, private records, and story history are tracked because the story workspace is the archive unit. A public remote exposes them. A Director package that calls an outside service (for example `scene-images`) sends the text it needs to that provider; the provider and cost are the Director's choice and are stated before use.
* A redacted/shareable export is **not implemented in v1**. Users who need one should copy only the public conversations/cast/assets they intend to publish.
* The development repository is published with a fresh history: one new root commit of the audited current tree, never the private history ([ADR-4](../decisions/ADR-4-publish-with-fresh-history.md)). Development evidence (`.research/`, `goldfish_reviews/`, `.impeccable/`) is untracked and stays local; the approved Woven references live in `docs/designs/woven/`. The current repository contains no real story or imported cards; that is not a permanent guarantee.
* The license covers the package source, not the user's story or third-party imported card material. Imported cards retain their own provenance and terms.
* The release builder scans text for the configured secret markers in `release.manifest.json` (private-key headers, `OPENROUTER_API_KEY=`, `GITHUB_TOKEN=`, `sk-or-v1-`, and a boundary-fixture marker). Files under `tests/` and `web/tests/` are allowlisted for the boundary-fixture marker only, because the tests plant it on purpose. The builder excludes `.env*`, runtime state, imports, and assets by path.

## Updates and propagation

Version 1 has **no automatic updater** and no promised in-place update path. To take a new release, the user deliberately unpacks or merges package files while preserving `public/`, `imports/`, private records, and `.couldhappen/`. A future updater that handles this safely is a possible later tool, not part of the v1 promise.

Package-source changes made inside a story workspace are local. If they are useful upstream, separate them from story changes and export a reviewed patch or copy; never include story content in an upstream patch. “Upstream” means the release source, not a Git remote to add to the story.

## Confirmation checklist

This is the canonical checklist. The ADRs reference it rather than duplicating it.

A release/story workspace is confirmed when:

1. `python scripts/build_release.py --ref <tested-commit> --out release/dist/couldhappen-<version>.zip` succeeds from a clean worktree.
2. The ZIP's exact file list matches the manifest; no `forbidden` path is present; no configured secret/private marker is found.
3. The ZIP contains no `.git`, `.impeccable`, development docs, release tooling, `.env*`, runtime state, imports, public assets, or real story content.
4. `couldhappen.json`, `.gitignore`, and the public files match the release templates; the UUID is null; no shipped Markdown contains a `dev-only` marker.
5. Every relative Markdown link in the ZIP resolves.
6. Unpacked workspace: `npm ci` in `web/` succeeds; `python -m helpers validate --root .` succeeds.
7. Starting the helper initializes the UUID and claim establishes ownership; browser save and serviced wait succeed; the first baseline commit includes the UUID; `checkpoint check` is clean; a standing wait is running when setup is reported complete, so a first browser entry is picked up without a chat prompt.
8. The story workspace's `git rev-parse --show-toplevel` is that workspace, not an enclosing repository, and `git log --oneline` has one baseline commit.
9. A copied/archived story workspace reopens coherently.
10. The actual host/story acceptance observation runs from that workspace and is recorded in [validation results](../validation-results.md).

## Drift input

After this design is accepted and implemented, `egm-drift-report` should run over the curated normative documents:

* the approved product design (`docs/designs/couldhappen.md`),
* this distribution design,
* the public contract (`docs/public-contract.md`).

Do not point the drift runner at every file in `docs/designs/`; optional examples, sitemaps, and visual-provenance notes are not implementation specifications. ADRs are linked rationale, not primary drift targets. Drift is a docs-vs-code audit, not a substitute for the host/story acceptance test.

## Open questions

1. **Release docs:** v1 ships `docs/README.md`, `docs/setup.md`, `docs/public-contract.md`, and `docs/reference-hosts.md`. Validation evidence and demo records remain upstream.
2. **Later distribution:** whether a GitHub template or installer is worth adding after the ZIP release is stable.
3. **Updater:** whether a later tool can update package files while preserving story data. Explicitly out of scope for v1.
4. **Product context:** whether a user-facing `PRODUCT.md` or architecture summary should ship later.

## Out of scope

This design does not change:

* the fiction model, creative-initiative principle, or Director/Undo behavior;
* the Woven visual direction or reader components;
* the Python helper's public HTTP contract;
* the existing development Git history;
* any user's existing story content.
