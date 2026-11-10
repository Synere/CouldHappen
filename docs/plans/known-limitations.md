---
type: reference
status: current
updated: 2026-11-11
---

# Known limitations

**Purpose.** Gaps that are known and deliberately left open, each with the condition that would reopen it. The rows are in the Deferred section of the [issues register](../issues.md).

## ISS-9 — Literal comp pixel gates

`.impeccable/build/state.json` stays at `spec`. Closing it would mean fabricating the comp's illustrative scene and portraits, which the design forbids. Do not use `--force` unless the author explicitly downgrades comp authority, and do not claim a pixel pass.

## ISS-10 — Dependency audit

Two low findings in dev/build tooling (`deepmerge` under `@sveltejs/vite-plugin-svelte`); the production audit is clean. Fixing them needs an upstream patch or a deliberate override. See [validation results](../validation-results.md#dependency-audit-review-unchanged-current).

## ISS-11 — Native assurance

Checkpoint examples are not activated by default. A clean tree shows recorded changes, not the semantic completeness of the world record.

## ISS-12 — Portrait framing

If a real portrait library shows problems with the 4:3 contain treatment, revisit the framing with the Director rather than transforming card pixels.
