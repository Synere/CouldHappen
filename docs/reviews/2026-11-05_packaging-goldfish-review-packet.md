# Goldfish-style review packet — packaging and story workspaces

- **Status:** Review completed — see the [review report](2026-11-05_packaging-goldfish-review.md). Verdict: accept with changes; the decisions remain Proposed.
- **Date:** 2026-11-05
- **Decisions under review:** [ADR 0001](../decisions/0001-separate-story-workspaces.md), [ADR 0002](../decisions/0002-publish-clean-release.md), and [Distribution and workspaces](../designs/distribution-and-workspaces.md)
- **Recorded author choices:** MIT license; release ZIP first; no commercial sale planned

## Reviewer instructions

Act as a fresh-context, skeptical design reviewer. You are reviewing a packaging and workspace-boundary proposal, not the quality of the fiction or the reader UI. Do not edit files. Do not implement anything. Return findings only.

Read only:

1. This packet.
2. `docs/decisions/0000-use-markdown-architectural-decision-records.md`
3. `docs/decisions/0001-separate-story-workspaces.md`
4. `docs/decisions/0002-publish-clean-release.md`
5. `docs/designs/distribution-and-workspaces.md`
6. The [approved design](../designs/couldhappen.md) sections **Selected architecture and ownership**, **Workspace materials and public agreement**, **Public changes and agent-managed setup**, **Checkpoints and host completion**, and **Detailed Implementation** step 1 (workspace/scope) and step 8 (setup).
7. `docs/public-contract.md`
8. `LICENSE` and the user-facing parts of `README.md`.
9. `docs/setup.md` only to check whether its proposed boundary note is consistent.

Do not read the implementation handoff, validation results, prior chat, code-review reports, or this project’s development discussion. The review must not inherit the proposing thread’s framing.

At the end, list every file you actually read and state whether any project or user instruction file (for example `AGENTS.md`) was automatically supplied outside this packet. If a required file was unavailable or you skipped it, say so.

## Isolation limitation

This is a **manual Goldfish-style review**, not a certified EGM Goldfish review. OpenCode’s EGM integration is experimental: project/global `AGENTS.md` may reach child agents, reviewer read-only tool isolation is not fully verified, and full draft/review workflows have not been tested. To reduce that risk, use a clean profile/directory containing only this packet and the referenced documents, or use a more thoroughly validated harness. A new chat alone does not prove isolation.

## Review question

Is the proposed model coherent, safe, and complete enough to accept before implementation?

Specifically:

* Does a separate clean story workspace solve the real problems of mixed development/story history, closure checks, and story privacy?
* Is “development repository upstream + release ZIP + story workspace” a coherent interpretation of a portable workspace?
* Are the release include/exclude lists safe and sufficient? Identify anything that should ship but does not, or should not ship but does.
* Are the checkpoint and `writer close` consequences described correctly? Does the proposal leave a hidden failure mode?
* Is the writer’s ability to edit local source compatible with clean history and deliberate upstream propagation?
* Is the update/propagation model actionable, or does it defer a problem it claims to solve?
* Does the initial baseline/confirmation checklist actually prove what it claims?
* Is MIT licensing and a ZIP-first release adequate for the stated intent?
* Does the proposal contradict the approved design or the public contract? Is the amendment pointer sufficient?
* What must be true before changing the ADRs from Proposed to Accepted?

## Required output

Return:

1. **Verdict:** accept / accept with changes / reject, with a short justification.
2. **Material findings** ranked P0/P1/P2, each naming the document and section.
3. **Contradictions or missing requirements**, especially around privacy, Git ownership, checkpoint scope, release contents, updates, and the relationship to the approved design.
4. **Specific recommended edits** that would make the proposal acceptable.
5. **Files read and isolation disclosure.**
6. **Confidence and limits** of this review.

Do not rewrite the documents. Do not create an implementation. Do not treat the absence of an objection as proof of correctness.
