---
type: research
status: completed
updated: 2026-11-11
---

# Research prompt: how do agent skills drive a browser UI?

**Purpose.** The research prompt behind the [browser UI prior-art findings](browser-ui-prior-art-findings.md), kept so the question can be asked again.

Paste everything below the line into ChatGPT (deep research / web browsing on). Bring the answer back to the repo and compare it with the "Our design" section.

---

## Task

I am building **CouldHappen**, an open-source (AGPL-3.0) interactive-fiction "skill" that runs inside general coding agents (Claude Code, Codex CLI, Cursor, Gemini CLI, opencode and similar). I want to know whether my approach to giving the skill a **browser UI** is idiomatic compared with other popular agent skills, plugins, and agent-adjacent tools, and what I should copy, avoid, or reconsider.

Please research with real, citable sources (repos, docs, changelogs, issues). Give links. Mark anything you could not verify as unverified. Do not guess at how a tool works from its name.

## Our design (what to compare against)

- The agent is the author and game master. The player reads and writes in a **browser reader** (Svelte/Vite static build) instead of the agent's terminal chat.
- A **local Python helper** (stdlib `ThreadingHTTPServer`) binds only to `127.0.0.1` on a chosen port, checks the `Host` header and the frontend origin (loopback only), and serves a small JSON API plus the built reader.
- The **files are the source of truth**: the story lives in plain Markdown in the workspace (`public/story.md`, `public/director.md`), with stable entry IDs and a `pending/addressed/deferred` disposition per human entry. The browser saves an entry; the agent must separately handle it.
- The agent **learns about browser input by blocking on a helper command** (`wait`), run as a foreground command with a timeout under the host's tool limit, or as a background command where the host supports it. Nothing runs after the agent's turn ends, so if the host cannot wait, the player must nudge the agent in chat.
- Two channels in one UI: Story (in-fiction) and Director (talking to the agent about the story).
- Concurrency controls: an edit **pause** lock, a **production block** that closes the browser channels while the agent writes, and a **generation** ID that makes the browser discard stale state.
- The skill is packaged as a portable workspace (a release ZIP) with the skill at `.agents/skills/couldhappen/`. It is host-agnostic: the host owns model calls, tools, permissions, and sessions.

## What I want to know

1. **Survey of prior art.** Find skills, plugins, MCP servers, and agent tools that put a browser or GUI in front of an agent, and classify how each one gets *user input from the UI back to the agent*. Include at least:
   - Claude Code skills/plugins and MCP servers with a local web UI (for example visual companions, dashboards, diagram or design tools, review UIs, and "live" preview servers).
   - Codex CLI, Gemini CLI, Cursor, Cline, Roo, Continue, Aider (`--browser`), Goose, OpenHands, and opencode (web UI / server mode).
   - MCP Apps / MCP UI / elicitation, ChatGPT Apps SDK widgets, and Claude artifacts: the "UI inside the host" alternative.
   - Agent protocols meant for this: ACP (Agent Client Protocol), AG-UI, A2A, and the Claude Agent SDK's streaming-input and hooks.
   - Notable non-coding examples: interactive fiction or tabletop-RPG agents, SillyTavern-style frontends, and Jupyter or notebook-style agents.

2. **Input-return mechanisms.** For each tool, which pattern does it use? Name and compare these, and any others you find:
   - blocking CLI wait or long-poll that the agent runs itself (ours)
   - the agent polling a file or a queue
   - UI posts to the agent over MCP, a webhook, or stdin
   - the UI is the host (the agent runs *inside* the web app)
   - hooks (`UserPromptSubmit`, `Stop`, a file-watcher or channel) injecting browser input into the next turn
   - Claude Code **channels** / push notifications / `Monitor` and similar "wake the agent when something happens" features
   - Codex or Gemini equivalents
   For each: how does it handle the agent being idle, the host's tool timeout, background tasks, and a closed turn?

3. **Server and security conventions.** What do popular tools do for port selection, loopback binding, `Host`/`Origin` checks, DNS-rebinding protection, CSRF tokens or per-session secrets, CORS, lifecycle (who starts and stops the server, orphaned processes, pid or lock files), and discovery (how the agent learns the URL)? Is `127.0.0.1` plus a Host check enough by current standards? Are there known incidents (for example MCP Inspector or dev-server DNS-rebinding CVEs) I should learn from?

4. **Source of truth and state.** Do others keep state in plain files like we do, in a database, or in the host's session? How do they avoid lost updates and stale views between the UI and the agent (our pause lock, production block, and generation ID)? Is there a more standard pattern (versioned documents, ETags, event sourcing, CRDTs, an append-only log)?

5. **Packaging and portability.** How do skills ship a bundled web app: prebuilt static assets in the repo or ZIP, an npm or `uvx` launcher, a Docker image, an MCP server binary? What do the Agent Skills spec (`SKILL.md`) and the cross-host conventions (`.agents/skills`, `AGENTS.md`) say or imply about running servers and helper scripts? What breaks across hosts (Windows, sandboxed shells, no background processes, tool timeouts)?

6. **UX conventions.** How do tools launch the UI (print URL, auto-open the browser, `open`/`xdg-open`, a host-integrated preview pane)? How do they show "the agent is working" and "the agent is waiting on you"? Are there conventions for two-way chat UIs next to an agent already running in a terminal?

## Deliverable

1. A comparison table: tool or pattern, input-return mechanism, server/security approach, state model, packaging, and a source link.
2. A short verdict: is our approach **idiomatic, unusual but defensible, or fragile**? Say which parts are which.
3. A ranked list of **specific changes worth making**, each with the evidence behind it, the cost, and the risk. Distinguish "adopt a standard we ignored" from "nice to have".
4. Anything we do that others do *better* or that we should explicitly document as a deliberate deviation.
5. Known pitfalls reported by users of comparable tools (issues, postmortems) that match our design.

Keep the answer under about 2,000 words plus the table, and put sources inline.
