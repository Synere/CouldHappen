# Implementation progress

Current state and next steps only. The dated history of how the project got here is the [progress log](history/progress-log.md); evidence for every claim below is in [validation results](validation-results.md).

## Current state (2026-11-05)

- **Application:** the approved first scope is implemented: the writer skill, the Python helper, the Svelte/Vite Woven reader, card import and portraits, checkpoints, and recovery. All mechanical checks pass.
- **Release:** the latest is `release/dist/couldhappen-0.1.7.zip` (SHA-256 `d21a43f2...`, built from the public commit and published as GitHub release `v0.1.7`), the first AGPL-3.0-or-later release, with the drift-report fixes; it passed `scripts/smoke_release.py` (18 of 18). Builds are deterministic from a tracked commit; see [Building a release](setup.md#building-a-release).
- **Hosts:** all four are experimental. opencode has one largely successful story-workspace test, which found two problems (no standing wait after setup; the `portrait` path), both fixed since. Claude Code has one largely successful session (0.1.4, Sonnet 5.5) whose four problems are fixed since. Codex CLI and Pi with OpenRouter are untested. See [host integrations](reference-hosts.md).
- **Skill:** rewritten for clarity on 2026-11-05 and checked by a fresh-context reviewer; not yet run on a host.
- **Not yet observed on any host:** native checkpoint hooks reached and trusted; fresh-context *continuation of fiction* (reentry itself was observed); the standing-wait and portrait fixes on a real session; closing the game on request; the wait check after a host restart.

## Resume here

Read the [README](../README.md), this note, and [validation results](validation-results.md). Use the [approved design](designs/couldhappen.md) for requirements; do not restart brainstorming or an overall design review. Inspect `git status` before editing. Preserve the approved architecture, the creative-initiative principle, the Woven direction, and the existing Impeccable hooks in `.codex/`.

Do not run a durable story in this repository. Test from a workspace unpacked from a release ZIP.

## Next steps

1. **Re-test the fixes.** On any host, from a fresh release workspace, confirm that the standing wait starts at the end of setup with no chat prompt, and that `portrait` accepts the original card path.
2. **More hosts, any order.** Codex CLI, Claude Code (including skill discovery), and Pi with OpenRouter, each with a human-selected model. Record results in [validation results](validation-results.md) and the status table in [host integrations](reference-hosts.md).
3. **Fresh-context continuation.** After reentry from files alone, continue the fiction through browser input and compare it against the maintained records.
4. **Drift report.** Run `egm-drift-report` over the [design](designs/couldhappen.md), [distribution design](designs/distribution-and-workspaces.md), and [public contract](public-contract.md) before a wider release.
5. **Publish.** Follow the checklist in [ADR 0004](decisions/0004-publish-with-fresh-history.md): drift report, tree audit, 0.1.7, fresh history.
6. **Writing-style package (idea, not started).** A general `writing-style` director package that steers the writer's prose, like SillyTavern presets but without per-prompt injection. Design sketch:
   - A distilled active guide (about 500 tokens: voice, POV and tense, rhythm, banned phrases, two or three voice anchors) in `notes/style/guide.md`, linked from `START_HERE.md`.
   - A per-turn step to re-read it before each writer entry, plus a rule to re-read the full guide when unsure the style still holds (context swamped, fresh session, after compaction).
   - A `tools/style_check.py` lint run on the entry body file before append: banned phrases, repeated openers, long paragraphs, POV or tense slips. It cannot judge taste, and the package says so.
   - No bundled style. If the player asks to use a SillyTavern-style preset, the writer imports it as data: keep only enabled prose-style blocks, drop samplers, prefill, jailbreaks, depth settings and regex scripts, turn macros into plain wording, show the Director what was kept and dropped, and write the guide only after they confirm. Optional preset modules become switchable style modules, like the `game-master` layers.
   - Content boundaries from the `game-master` contract win over the style guide in a conflict.
   - Open: the cap on guide size, and whether it shares the per-turn routine with `game-master`.

## Open gaps

- **Literal comp pixel gates.** `.impeccable/build/state.json` stays at `spec`. Closing it would mean fabricating the comp's illustrative scene and portraits, which the design forbids. Do not use `--force` unless the author explicitly downgrades comp authority, and do not claim a pixel pass.
- **Dependency audit.** Two low findings in dev/build tooling (`deepmerge` under `@sveltejs/vite-plugin-svelte`); the production audit is clean. Fixing them needs an upstream patch or a deliberate override.
- **Native assurance.** Checkpoint examples are not activated by default. A clean tree shows recorded changes, not the semantic completeness of the world record.
- **Portrait framing.** If a real portrait library shows problems with the 4:3 contain treatment, revisit the framing with the Director rather than transforming card pixels.

## Evidence levels

Keep these separate: implemented behavior (source and scripts); automated checks (tests, check, build); visual observations (reviewer screenshots with synthetic data); and actual host/story observations. Only the last establishes that something works on a host, and so far that exists for opencode alone.
