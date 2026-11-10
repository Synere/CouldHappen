# Packaging Goldfish-style review — 2026-11-05

- **Status:** Completed; findings resolved in the proposal — see [resolution record](2026-11-05_packaging-resolution.md). Focused re-review skipped by author.
- **Review type:** Manual fresh-context Goldfish-style review in OpenCode, **not** a certified EGM Goldfish review
- **Packet:** [2026-11-05_packaging-goldfish-review-packet.md](2026-11-05_packaging-goldfish-review-packet.md)
- **Documents under review:** [ADR-1](../decisions/ADR-1-separate-story-workspaces.md), [ADR-2](../decisions/ADR-2-publish-clean-release.md), [Distribution and workspaces](../designs/distribution-and-workspaces.md)
- **Verdict:** **Accept with changes — not ready to move from Proposed to Accepted.**

## Scope and limits

The reviewer received only the packet and the documents it names. It did not read the implementation handoff, implementation progress, validation results, prior chat, or implementation code. It used read-only inspection and did not edit files.

The review ran in the full project workspace rather than a clean directory/profile. No `AGENTS.md` or other project instruction file was visible to the reviewer, but the packet’s isolation limitation still applies: OpenCode’s EGM integration is experimental, and a fresh conversation is not proof of full Goldfish isolation.

The reviewer read more of `docs/designs/couldhappen.md` than the packet’s selected sections because it read contiguous ranges. It also read all of `docs/setup.md` rather than only the boundary note. It disclosed both deviations and weighted them accordingly.

## Material findings

### P1-1 — Release contents are not enforceable

The proposed allowlist/exclude list is prose, not a release manifest. No build procedure, exact ZIP file list, checksum, or content scan is defined. A ZIP could pass the listed “absent directory” checks while still containing a real story, imported card, populated `START_HERE.md`, development UUID, private writer record, or a sensitive document that was accidentally included.

The allowlist is also explicitly provisional: `tests/`, `PRODUCT.md`, the approved design, and the docs index remain unresolved release decisions. A provisional allowlist cannot be the normative packaging contract.

### P1-2 — The privacy model misses story/private-data exposure

A fresh `.git` prevents inheriting development commits, but the story workspace intentionally tracks imported cards, portraits, private writer records, and full story history. A public remote or shared archive exposes all of it. “Story privacy is the default” is guidance, not a mechanism.

The development repository’s own visibility is also undecided. If it is public and its history contains test stories, imported cards, credentials, or personal notes, the clean release does not fix that upstream exposure.

### P1-3 — Baseline and workspace-UUID sequence is contradictory

The documents describe incompatible creation sequences:

* the distribution design says unpack → `git init` → initial baseline commit → `npm ci` → setup/claim;
* `docs/setup.md` puts the initial baseline checkpoint after setup/claim;
* `couldhappen.json` receives its workspace UUID during helper setup.

If the baseline commit happens before setup, the UUID leaves the tree dirty. If it happens after setup, the single initial commit contains the UUID, contradicting “`couldhappen.json` starts without a workspace UUID.” The independence check also fails if the workspace is unpacked inside an enclosing repository.

### P1-4 — The approved design still says the opposite; the public contract points to an excluded authority

The approved design still normatively says the directory itself is the initial distributable workspace. The blockquote amendment points at a Proposed document, but does not supersede the binding sentence. The public contract names the approved design as the authoritative detailed specification, while the proposed release excludes `docs/designs/` — a dangling authority link.

The primary instructions in `README.md` and `docs/setup.md` still lead with “open this directory and set up,” even though their boundary notes say not to run a durable story there.

### P1-5 — The update/propagation model is claimed but deferred

ADR-2 lists a repeatable release and update path as a decision driver, but v1 provides only manual ZIP replacement. There is no version, source commit, manifest, conflict-detection procedure, or defined upstream-patch process. The future updater is unimplemented and described only as something that “may” exist.

## P2 findings

* Release templates/rewrites are undefined for `README.md`, `START_HERE.md`, `couldhappen.json`, `DESIGN.md`, and the docs index. The release is provider-neutral but not offline-self-contained because `npm ci` needs a registry.
* “Empty” public files are ambiguous. The contract requires title-only logs and schema-valid empty `cast.json`/`work.json`; the ADR checklists omit `work.json` and the required `couldhappen.json` fields.
* `.gitignore` lacks common OS/editor artifacts such as `.DS_Store`, `Thumbs.db`, `desktop.ini`, and swap files; `writer close` checks Git but not public validation.
* MIT covers the package, not user stories or imported third-party material. “No commercial sale planned” is an intention, not a license restriction. Third-party notices are not defined.
* The confirmation checklists differ across ADR-1, ADR-2, and the distribution design. Several checks are manual and lack expected output or evidence format.
* The decision index linkage required by ADR-0 was not verified because the packet excluded `docs/decisions/README.md`.

## Recommended resolution before Accepted

1. Define a release manifest and deterministic ZIP build with source commit, version, checksums, exact file-list comparison, link check, and private-content scan.
2. Decide and document the privacy model: development-repository visibility/audit, story-repository remote policy, whether imports/private records are tracked by default, and what a shareable/redacted export excludes.
3. Fix the creation sequence: release ZIP has a null UUID; story workspace runs `npm ci` and setup/claim, writes the UUID, then makes the first baseline commit; `checkpoint check` runs after that commit.
4. Make the packaging model normative: once accepted, amend the approved design’s distributable-workspace sentence, update the public contract authority, and make the release link work. Replace the development README/setup primary instructions rather than only annotating them.
5. Either define a minimal manual update procedure or explicitly descope updates from v1 and remove the “repeatable update path” claim.
6. Resolve the release contents and user-facing templates, including `work.json`, title-only logs, `couldhappen.json` fields, `START_HERE.md`, `README.md`, `DESIGN.md`, third-party notices, and a release docs index.
7. Add OS/editor artifacts to `.gitignore` and define the relationship between `writer close`, public validation, uncommitted writer experiments, and external private records.
8. Unify the confirmation checklist into one canonical checklist in the distribution design and reference it from both ADRs.

## Files read by the reviewer

* The review packet.
* ADR-0, ADR-1, ADR-2.
* `docs/designs/distribution-and-workspaces.md`.
* `docs/designs/couldhappen.md`, contiguous ranges covering the required sections plus adjacent sections.
* `docs/public-contract.md`.
* `LICENSE`.
* `README.md`.
* `docs/setup.md`.

Not read: implementation handoff, implementation progress, validation results, prior chat, code-review reports, `docs/validation.md`, the decision index, `PRODUCT.md`, the writer skill, or implementation code.

## Current status

The findings were resolved in the revised ADRs, accepted distribution design, release manifest/builder, release templates, and tests. The author authorized skipping the focused re-review, so the decisions were accepted without a certified EGM re-review. See the [resolution record](2026-11-05_packaging-resolution.md). No application story or native host was run.
