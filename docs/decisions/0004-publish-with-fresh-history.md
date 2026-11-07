---
status: accepted
date: 2026-11-05
decision-makers: Project author
consulted:
informed:
---

# 0004 — Publish the development repository with a fresh history

> **Update 2026-11-07:** the private history was archived outside the repository and deleted. The fresh public history is now the only history, and `publish` was renamed `main`. References below to a private `main` and a `publish` branch describe the state at decision time.

## Context and Problem Statement

The author plans to publish the development repository on GitHub. [ADR 0002](0002-publish-clean-release.md) allows that only after a deliberate history and secrets audit. The existing history has three problems for a public repository:

* Commits before `060f7a4` carry the MIT license ([ADR 0003](0003-license-agpl.md) moved to AGPL-3.0-or-later). Anyone who receives an MIT commit may use that copy under MIT.
* Development evidence (`.research/`, `goldfish_reviews/`, `.impeccable/`) contains absolute local paths and raw captured material, and older commits carry it whatever the current tree holds.
* Auditing every past commit for secrets and paths is costly and easy to get wrong.

The release ZIPs 0.1.0 to 0.1.6 were also MIT. They were never shared beyond the author, so no one else holds an MIT grant.

## Considered Options

* Publish the existing history as it is.
* Rewrite the existing history (for example, replace `LICENSE` and remove evidence in every commit).
* Publish a fresh history: one new root commit of the cleaned current tree.

## Decision Outcome

Chosen option: **publish a fresh history**, selected by the project author on 2026-11-05. It removes the MIT versions, the evidence, and every older leak at once, and leaves only the current tree to audit. A rewrite keeps every other past mistake in place and still needs a full audit.

### Consequences

* The full development history stays private on the author's machine. The public repository starts at one root commit and grows from there.
* `.research/`, `goldfish_reviews/`, and `.impeccable/` are untracked and ignored. They stay on disk locally as evidence. Documents that cited them now say "kept locally, not published".
* The approved visual references that the design depends on (the Woven mock, its selection record, and the reader surface direction) are copied into `docs/designs/woven/` so they are published with the design.
* The MIT release ZIPs (0.1.0 to 0.1.6) are not shared. 0.1.7, the first AGPL build, is the first release given to anyone and the first GitHub release.
* The record stays honest: ADRs and the progress log still say the early releases were MIT.

### Publish checklist

1. Run the drift check over the curated documents (see the [distribution design](../designs/distribution-and-workspaces.md)) and resolve its findings.
2. ~~Decide on `.codex/hooks.json`~~: untracked and ignored on 2026-11-05, because it holds local absolute paths.
3. Audit the current tree: no absolute local paths, no secrets, no real story or imported cards (`git grep` for drive paths and secret markers; the release builder's secret scan covers the ZIP only).
4. Build and smoke-test 0.1.7.
5. Create the fresh history: an orphan branch from the audited tree, one commit, pushed to the new GitHub repository as its default branch. Never push the private branches.
6. Attach the 0.1.7 ZIP and its `.sha256` to the first GitHub release.
