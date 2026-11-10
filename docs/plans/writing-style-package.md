---
type: plan
status: proposed
updated: 2026-11-11
---

# Writing-style package

**Purpose.** A general `writing-style` director package that steers the writer's prose, like SillyTavern presets but without per-prompt injection. This is an idea, not started. Ends when the package ships in `packages/` with its entries in the pages the writer reads, or when the idea is abandoned.

## ISS-8 — Writing-style package

Moved from the Next steps in [implementation progress](../history/implementation-progress.md) on 2026-11-11. Nothing is built yet.

## Approach

Design sketch:

- A distilled active guide (about 500 tokens: voice, POV and tense, rhythm, banned phrases, two or three voice anchors) in `notes/style/guide.md`, linked from `START_HERE.md`.
- A per-turn step to re-read it before each writer entry, plus a rule to re-read the full guide when unsure the style still holds (context swamped, fresh session, after compaction).
- A `tools/style_check.py` lint run on the entry body file before append: banned phrases, repeated openers, long paragraphs, POV or tense slips. It cannot judge taste, and the package says so.
- No bundled style. If the player asks to use a SillyTavern-style preset, the writer imports it as data: keep only enabled prose-style blocks, drop samplers, prefill, jailbreaks, depth settings and regex scripts, turn macros into plain wording, show the Director what was kept and dropped, and write the guide only after they confirm. Optional preset modules become switchable style modules, like the `game-master` layers.
- Content boundaries from the `game-master` contract win over the style guide in a conflict.

When it ships, add it to `packages/INDEX.md`, the skill's `SKILL.md` reference list and `references/what-this-can-do.md` (see [AGENTS.md](../../AGENTS.md)).

## Open

- The cap on guide size.
- Whether it shares the per-turn routine with `game-master`.

## Decision log

Give the note a `dec-prefix` in its frontmatter when the first row goes in.

| ID | Decision | Date | Why |
| --- | --- | --- | --- |
