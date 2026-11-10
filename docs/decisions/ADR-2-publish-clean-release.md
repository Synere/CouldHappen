---
status: accepted
date: 2026-11-05
decision-makers: Project author (pending)
consulted:
informed:
---

# ADR-2 — Publish a clean release, not the development history

> In the context of a portable fiction workspace that players copy and fill with their own story, facing a development repository whose history, review artifacts and validation records a player should not inherit, we decided to publish a deterministic release ZIP built from a tested commit by the release manifest, with a GitHub template or an installer as later options, to achieve a clean, self-contained and verifiable starting workspace, accepting a release build to maintain, a contents review, and manual updates.

## Context and Problem Statement

CouldHappen is intended to be a portable fiction workspace that users copy, open in their own agent, and fill with their own story. Publishing the current development repository directly would give users the implementation history, design-review artifacts, and internal validation records. If they fork it publicly, their story content would also be public by default.

A distribution artifact needs to be clean, self-contained for operation, and safe to start from. The development repository remains valuable as the upstream source and design record, but it is not the thing a player should inherit.

On 2026-11-05 the project author selected a **release ZIP first** for simplicity and **MIT** as the license. A GitHub template or installer remains a later option.

## Decision Drivers

* Clean story history and user privacy.
* A self-contained, verifiable portable workspace that can be copied and archived.
* A clear difference between what users receive and what the project team maintains.
* No rewrite or deletion of the existing development history.
* A repeatable release build, even if v1 has no automatic updater.
* The writer must still be able to inspect and edit the workspace source as creative practice.

## Considered Options

1. **Publish the development repository as the product.** Users clone or fork it.
2. **Publish a clean GitHub template repository.** Users create a new repository from it.
3. **Publish a release ZIP.** Users download, verify, unpack, and initialize their own repository.
4. **Build an installer/updater CLI.** Similar to `npx impeccable install`, but for a complete workspace rather than a skill pack.

## Decision Outcome

Chosen option: "3 first, with 2 as an optional later convenience and 4 as a possible later update mechanism."

The development repository remains upstream. The public distribution is a deterministic release ZIP built from a tested commit using `release.manifest.json` and `scripts/build_release.py`.

### Release requirements

* The release has a version, source commit, source date, contract version, manifest hash, and file count in an embedded `release.json`.
* The ZIP and a `.sha256` sidecar are published together.
* The build reads tracked files from a named commit, not the working tree, and requires a clean worktree by default.
* The release manifest is the normative allowlist and includes template overrides, required paths, forbidden paths, and content-scan markers.
* The builder verifies the exact file list, required/forbidden paths, configured secret markers, and relative Markdown links before writing the ZIP.
* The ZIP has deterministic path order and timestamps.
* A release candidate is smoke-tested from the ZIP, not the development repository.

### Contents and authority

* The release includes the writer skill, helpers, frontend, fonts/OFL notices, tests, empty public data, imports placeholder, reentry template, setup/contract docs, `DESIGN.md`, and the `LICENSE`.
* Development-only artifacts do not ship: `.git`, `.impeccable`, planning/research/review/archive folders, `.research`, `goldfish_reviews`, internal handoff/progress records, decisions/designs, release tooling/templates, `PRODUCT.md`, development hooks, runtime state, imports, public assets, and credentials.
* The public contract is self-contained for runtime behavior and does not link to an excluded design document. The approved design remains upstream product/design authority.
* `couldhappen.json`, `.gitignore`, and the public files are release templates. Shipped Markdown is the development file with its `dev-only` blocks removed by the builder (changed 2026-11-05 from separate Markdown templates, which drifted from their development copies).
* The software license was **MIT** (`LICENSE` at the repository root); [ADR-3](ADR-3-license-agpl.md) replaced it with AGPL-3.0-or-later on 2026-11-05. The license covers the package source, not a user’s story or imported third-party card material. “No commercial sale is planned” is an intention, not a license restriction. Bundled font OFL notices ship under `web/fonts/`; npm dependencies retain their own licenses.

### Privacy

* Story workspaces are private/local by default.
* Imports, portraits, private records, and story history are tracked by default because the workspace is the archive unit. A public remote exposes them.
* A redacted/shareable export is not implemented in v1.
* The development repository may be public only after a deliberate history and secrets audit; [ADR-4](ADR-4-publish-with-fresh-history.md) does this by publishing a fresh history. The clean release does not repair an already-exposed development history.

### Updates

Version 1 has no automatic updater and no promised in-place update path. Users deliberately unpack or merge a new release while preserving `public/`, `imports/`, private records, and `.couldhappen/`. A future updater is a later tool, not part of the v1 promise.

### Consequences

* Good, because users begin with clean history and an empty story.
* Good, because publishing no longer requires exposing development history or encouraging public story forks.
* Good, because the development repository can retain its full EGM, design, and validation trail.
* Good, because the release build is manifest-driven, deterministic, and independently checkable.
* Bad, because a release build, template maintenance, and contents review are now required.
* Bad, because ZIP updates are manual and existing story workspaces can diverge.
* Bad, because users must manage story-repository visibility and private tracked material themselves.
* Neutral, because a GitHub template or installer can be added later without changing the clean-workspace decision.
* Neutral, because the existing development history is preserved and does not need rewriting.

### Confirmation

The canonical checklist is in [Distribution and workspaces](../designs/distribution-and-workspaces.md#confirmation-checklist). It covers the deterministic build, exact ZIP contents, forbidden/private material, template state, link integrity, setup/claim UUID sequence, first baseline commit, clean checkpoint, workspace independence, copied-workspace reopening, and host/story observation.

## Pros and Cons of the Options

### Publish the development repository

* Good, because there is no separate release artifact.
* Bad, because users inherit development history and internal process artifacts.
* Bad, because a public fork containing a story is public by default.
* Bad, because it conflates distribution with development.

### Clean GitHub template repository

* Good, because GitHub creates a new repository with a fresh initial commit.
* Good, because users can choose private visibility.
* Bad, because it is GitHub-specific and requires maintaining a template repository.
* Neutral, because the same manifest could build both a ZIP and a template later.

### Release ZIP

* Good, because it is simple, provider-neutral, and easy to inspect.
* Good, because the source commit and checksums can be published with it.
* Good, because users explicitly initialize their own repository.
* Bad, because updates and provenance are less discoverable.
* Bad, because users need one more manual step.

### Installer/updater CLI

* Good, because it can materialize a workspace and later update source without touching story data.
* Bad, because it is a new product tool to design, secure, test, and maintain.
* Neutral, because it can be added later without changing the clean-workspace decision.

## More Information

* [ADR-1](ADR-1-separate-story-workspaces.md) — clean story workspaces.
* [Distribution and workspaces](../designs/distribution-and-workspaces.md) — the normative packaging contract.
* [Decision index](README.md).
* [Impeccable install model](https://impeccable.style/docs) — a comparable separation of installed artifact from development repository.
