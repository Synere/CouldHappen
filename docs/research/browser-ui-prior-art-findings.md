# Browser UI prior art: findings

Answer to [the research prompt](browser-ui-prior-art-prompt.md), pasted in by the author on 2026-11-06. It is an outside recommendation, not verified against sources here (no links were supplied), and nothing in it has been implemented yet. Compare it with the "Our design" section of the prompt before acting on it.

## Recommendation

Keep CouldHappen's current architecture and improve its reliability rather than introduce another communication framework (ACP, AG-UI, MCP, or host-specific integrations). The advantage of the current approach is that almost any sufficiently capable coding agent can read files, run commands, and follow instructions.

## Five targeted improvements, in order

1. **Make `wait` as reliable as possible.** Keep it as the universal way for the agent to receive browser input. Support foreground and background execution according to the host's actual capabilities. Test interruptions, command timeouts, and repeated exchanges. Do not add a separate service that calls the model.
2. **Make browser status more truthful.** Distinguish *message saved*, *writer waiting for input*, *writer working*, and *writer disconnected or unavailable*. A running Python server does not mean the agent is listening, especially when a host ends its session unexpectedly.
3. **Harden the local helper.** Keep loopback binding, Host/Origin checks, and the narrow JSON API. Add a per-run authorization token for sensitive operations if one is not already present. Verify atomic file writes, stale-revision handling, and restart behavior.
4. **Make setup capability-driven.** The skill should inspect what its environment supports instead of assuming a host or command interface, and choose how to start the helper, wait for input, and launch the browser. The core procedure stays identical across Claude Code, Codex, Gemini CLI, and others.
5. **Test compatibility through actual gameplay.** Ten consecutive Story/Director exchanges, a long idle period, a fresh-context continuation, and Undo. Record which host configurations work, their limits, and where manual intervention is needed.

## What to keep

| Existing decision | Recommendation |
| --- | --- |
| Python standard-library helper | Keep |
| Markdown as source of truth | Keep |
| Blocking local `wait` | Keep and strengthen |
| Separate Story/Director channels | Keep |
| Edit pause and production block | Keep |
| Generation IDs and stable entry IDs | Keep |
| Writer-managed notes and methods | Keep |
| Agent Skills packaging | Keep |
| Native Claude/Codex communication adapters | Not necessary |
| New agent controller, SDK or orchestration service | Avoid |

## Principle

CouldHappen should define what needs to happen, not dictate how the agent does it. Rather than "use a background Bash process to wait for browser messages", the skill should state the requirement: maintain a serviced input wait while playing, using whatever execution mechanism lets browser submissions return control to the writer; if the environment cannot maintain that wait, say so instead of claiming to be listening.

## The one limitation to accept

No universal mechanism lets an external browser wake an agent whose host session has completely ended. Treat that as an explicit compatibility boundary: hosts with serviced waits give continuous interaction while the session is active; others need the player to return to the agent's interface. Chasing it across every host risks turning CouldHappen into an agent orchestration framework.

## Bottom line

Do not redesign. Prove that the browser-to-files-to-agent loop is dependable, secure, and recoverable across several independent coding agents.

## Notes for follow-up (added when filing)

- Items 1 and 5 match what the 2026-11-05/06 test sessions already exercised (see [validation results](../validation-results.md)): standing waits held on opencode and Claude Code, and a host restart silently ended one. The skill already says to check for a running wait at the start of every turn it did not start.
- Item 2 is not implemented: the reader shows "Saved · awaiting writer handling" but has no writer-listening state.
