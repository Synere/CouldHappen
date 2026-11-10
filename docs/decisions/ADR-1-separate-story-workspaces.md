---
status: accepted
date: 2026-11-05
decision-makers: Project author (pending)
consulted:
informed:
---

# ADR-1 — Separate story workspaces from the development repository

> In the context of a portable workspace where the development repository and a real story would share one Git history, facing mixed history, a `writer close` that sees development changes, and avoidable privacy risk, we decided that every real story runs in its own clean workspace with a fresh Git history, created first from a release ZIP, to achieve story history and private material kept apart from development, accepting one more setup step and package updates that do not flow automatically.

- **Related:** [Distribution and workspaces](../designs/distribution-and-workspaces.md), [ADR-2](ADR-2-publish-clean-release.md), [approved design](../designs/couldhappen.md), [implementation progress](../history/implementation-progress.md) (history since ADR-8)

## Context and Problem Statement

The approved design makes the directory itself the portable workspace: the writer skill, helper source, frontend, public conversations, imports, and documentation live together. That is convenient for copying, but it currently means the development repository and a real story share one Git history.

Concrete consequences of the current arrangement:

* `couldhappen.json` scopes the fiction checkpoint to `.`; the exclusions cover historical documentation but not `web/`, `helpers/`, `tests/`, or current design/operations documents.
* `writer close` checks the whole scoped tree. Uncommitted development work makes the story tree dirty; a writer could commit development changes merely to close the story.
* The writer may edit helper/frontend source and its own skill/method files by design, so “writer files” and “developer files” are not a strict filesystem boundary.
* Git commit authorship is normally the same user identity. A commit does not reliably say whether the writer or a developer made a change.
* A public repository/fork containing a story would expose that story’s commits by default.
* A clean development history does not prevent a story workspace’s imports and private records from being exposed if the user publishes the story repository.

The development history is useful upstream, but it is not the artifact a player should inherit when beginning a story.

## Decision drivers

* Keep each story’s history and private material separate from development history.
* Preserve the portable-workspace property: a story workspace can be copied, archived, and reopened without the development repository.
* Keep the writer able to edit source, skills, and methods as part of its creative practice.
* Avoid requiring a new application architecture or a rewrite of the approved product design.
* Make ownership boundaries as enforceable as practical, not only conventional.
* Keep setup understandable for a local human and an existing agent.

## Considered options

1. **Keep one repository for development and stories.** Simplest and fully supported by the current code. Rejected as the default for real stories because it mixes history, makes `writer close` sensitive to development changes, and creates avoidable privacy risk.
2. **Use a branch or Git worktree for each story.** Shares one object database and repository ancestry; a worktree still belongs to the development repository. Better than one working tree, but not a durable privacy or history boundary. Rejected as the primary model.
3. **Create a separate clean story workspace per story.** A copy of the release package with its own `.git`, `.couldhappen/`, public logs/cast, imports, and commits. The development repository remains upstream. Recommended.
4. **Generate a story workspace from a release ZIP.** A distribution mechanism for option 3. It removes manual copying and controls exactly which files ship. Recommended as the initial creation mechanism.

## Decision Outcome

**Chosen option: 3, with 4 as the initial creation mechanism.**

* The development repository is the upstream package. It retains full implementation, design, review, and validation history.
* Every real story runs in its own clean workspace with a fresh Git history. The story workspace starts with empty public conversations/cast and a new workspace identity when the helper first starts.
* A release ZIP is the initial way to create that workspace. The ZIP has a null workspace UUID; setup/claim initializes the UUID; the first baseline commit includes the initialized UUID.
* A story workspace may be copied or archived independently. Its history belongs to that story; it does not carry development commits.
* The writer may edit source, skills, methods, and records inside the story workspace. Those edits are local story-workspace changes. If they are useful upstream, they are propagated deliberately as a reviewed patch or copy; automatic bidirectional merging is not promised. “Upstream” means the release source, not a Git remote to add to the story.
* A durable story must not be created in the development repository merely because the release ZIP is not ready. A disposable copy is acceptable only for a smoke test.

### Privacy and sharing

* Story workspaces are private/local by default. Publishing one is a deliberate user action.
* Imports, portraits, private writer records, and story history are tracked by default because the workspace is the archive unit. A public remote or shared archive exposes them.
* A redacted/shareable export is not implemented in v1. Users who want one should copy only the public conversations, cast, and assets they intend to publish.
* The development repository may be public only after a deliberate history and secrets audit. The current public logs/cast are empty, but that is not a permanent guarantee.
* The software license (AGPL-3.0-or-later, [ADR-3](ADR-3-license-agpl.md)) covers the package source, not the user’s story or imported third-party card material.

### Consequences

**Positive**

* The writer’s checkpoints, closure checks, and history concern the story and its local package, not the upstream development process.
* A story can be kept private or archived without exposing development history.
* `writer close` no longer sees unrelated uncommitted development work.
* The portable-workspace claim becomes concrete: copy the story workspace, keep the story.

**Negative**

* Creating and maintaining a story workspace is one additional setup step.
* Package updates do not flow automatically; they require deliberate replacement or merging.
* Story workspaces can diverge if the writer edits source. That is acceptable for creative initiative, but it must be visible when reviewing or exporting changes.
* A shared story repository exposes tracked imports and private records unless the user redacts them.

**Neutral**

* The writer still shares source with the package. The strong boundary is the repository, not a per-file ownership map.
* Existing development commits are preserved. This decision does not rewrite history.

### Confirmation

The canonical confirmation checklist is in [Distribution and workspaces](../designs/distribution-and-workspaces.md#confirmation-checklist). It covers the release ZIP, exact contents, setup/claim, UUID/baseline commit, clean checkpoint, workspace independence, copied-workspace reopening, and the host/story observation.

## Pros and cons of the options

### Single repository

* Good, because there is no extra setup; current behavior.
* Bad, because history and privacy mix; development changes can affect story closure.

### Branch or worktree

* Good, because there is less copying; source stays shared.
* Bad, because it shares repository ancestry and object database; isolation is organizational, not durable.

### Separate clean workspace

* Good, because it gives clean history, independent privacy/archive, and clear closure scope.
* Bad, because it adds setup and update propagation.

### Generated release ZIP

* Good, because it is repeatable, curated, and can exclude development artifacts.
* Bad, because it is another artifact to build and maintain; v1 has no updater.

## More information

* Normative packaging behavior: [Distribution and workspaces](../designs/distribution-and-workspaces.md)
* Publication model: [ADR-2](ADR-2-publish-clean-release.md)
* Approved product design: [CouldHappen](../designs/couldhappen.md)
* Validation procedure: [Validation](../validation.md)
