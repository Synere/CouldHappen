# Implementation progress (history)

> **Frozen on 2026-11-11, not current instructions** ([ADR-8](../decisions/ADR-8-open-work-in-the-register.md)). Open work is in the [issues register](../issues.md), plans are in [docs/plans/](../plans/), host status is in [host integrations](../reference-hosts.md), and the current release is on the GitHub releases page.

Current state only; open work is in the [issues register](../issues.md). The dated history of how the project got here is the [progress log](progress-log.md); evidence for every claim below is in [validation results](../validation-results.md).

## Current state (2026-11-05)

- **Application:** the approved first scope is implemented: the writer skill, the Python helper, the Svelte/Vite Woven reader, card import and portraits, checkpoints, and recovery. All mechanical checks pass.
- **Release:** the latest is `release/dist/couldhappen-0.1.7.zip` (SHA-256 `d21a43f2...`, built from the public commit and published as GitHub release `v0.1.7`), the first AGPL-3.0-or-later release, with the drift-report fixes; it passed `scripts/smoke_release.py` (18 of 18). Builds are deterministic from a tracked commit; see [Building a release](../setup.md#building-a-release).
- **Hosts:** all four are experimental. opencode has one largely successful story-workspace test, which found two problems (no standing wait after setup; the `portrait` path), both fixed since. Claude Code has one largely successful session (0.1.4, Sonnet 5.5) whose four problems are fixed since. Codex CLI and Pi with OpenRouter are untested. See [host integrations](../reference-hosts.md).
- **Skill:** rewritten for clarity on 2026-11-05 and checked by a fresh-context reviewer; not yet run on a host.
- **2026-11-11, from a player package (erotic-sandbox):** the stock reader is restyled as a dim petrol room ([ADR-6](../decisions/ADR-6-dark-petrol-reader.md)); the voice method is a writer reference and `character-brains` is a new package that requires game-master layers 1 to 4 ([ADR-7](../decisions/ADR-7-character-brains-and-voice.md)). Mechanical checks and the browser tests pass; neither the voice reference nor character-brains has run on a host yet, and the README and GitHub screenshots still show the old reader.
- **Not yet observed on any host:** native checkpoint hooks reached and trusted; fresh-context *continuation of fiction* (reentry itself was observed); the standing-wait and portrait fixes on a real session; closing the game on request; the wait check after a host restart.

## Resume here

Read the [README](../../README.md), this note, the [issues register](../issues.md), and [validation results](../validation-results.md). Use the [approved design](../designs/couldhappen.md) for requirements; do not restart brainstorming or an overall design review. Inspect `git status` before editing. Preserve the approved architecture, the creative-initiative principle, the Woven direction, and the existing Impeccable hooks in `.codex/`.

Do not run a durable story in this repository. Test from a workspace unpacked from a release ZIP.

## Open work

Moved on 2026-11-11 to the [issues register](../issues.md) as ISS-1 to ISS-12, with their home sections in [host validation](../plans/host-validation.md), [public release](../plans/public-release.md), [known limitations](../plans/known-limitations.md) and the [writing-style plan](../plans/writing-style-package.md).

## Evidence levels

Keep these separate: implemented behavior (source and scripts); automated checks (tests, check, build); visual observations (reviewer screenshots with synthetic data); and actual host/story observations. Only the last establishes that something works on a host, and so far that exists for opencode alone.
