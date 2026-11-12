---
type: plan
status: active
updated: 2026-11-11
---

# Host validation

**Purpose.** Observe the release on real hosts, from a fresh workspace unpacked from a release ZIP, until each behaviour below has been seen working or failing on at least one host. Ends when every item here is closed in the [issues register](../issues.md). Results go in [validation results](../validation-results.md) and the status table in [host integrations](../reference-hosts.md); the procedure is in [validation](../validation.md).

Only an actual host/story observation establishes that something works on a host. Source, automated checks and reviewer screenshots do not.

## ISS-1 — Re-test the fixes

On any host, from a fresh release workspace, confirm that the standing wait starts at the end of setup with no chat prompt, and that `portrait` accepts the original card path.

**Closed 2026-11-11.** The author reports both working across several later story sessions.

## ISS-2 — More hosts

Any order: Codex CLI, Claude Code (including skill discovery), and Pi with OpenRouter, each with a human-selected model.

## ISS-3 — Fresh-context continuation

After reentry from files alone, continue the fiction through browser input and compare it against the maintained records. Reentry itself had been observed; continuing the fiction afterwards had not.

**Closed 2026-11-11.** The author restarted with a fresh context on Claude Code and on opencode and continued the fiction from the workspace files through the reader; both worked.

## ISS-7 — Try character-brains

Try character-brains on a host with subagents, from a fresh release workspace with game-master layers 1 to 4 ([ADR-7](../decisions/ADR-7-character-brains-and-voice.md)).

**Closed 2026-11-12.** The author is playing a live 0.1.22 story with character-brains on Claude Code with Opus, with every game-master layer on, and reports it works well.

## ISS-13 — Native checkpoint hooks

Not yet observed on any host: native checkpoint hooks reached and trusted.

## ISS-14 — Closing the game on request

Not yet observed on any host: the writer closing the game when the player asks.

## ISS-15 — Wait check after a host restart

Not yet observed on any host: the skill's wait check after a host restart. A restart is known to end the wait silently.

## ISS-16 — Voice reference on a host

The voice method became a writer reference on 2026-11-11 ([ADR-7](../decisions/ADR-7-character-brains-and-voice.md)) and has not run on a host yet.
