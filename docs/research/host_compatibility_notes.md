---
type: research
status: completed
updated: 2026-11-11
---

# Existing-host compatibility: first investigation

**Purpose.** A record of what was investigated before the design was approved. It is kept as evidence and is not updated.

> Historical research record. Current scope and implementation decisions are in the [approved design](../designs/couldhappen.md); start a future implementation session with the [handoff](../history/implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../history/archive/README.md).

- Date: 2026-11-03 (Asia/Manila)
- Stage: EGM clarification; documentation and read-only local observations
- No writer session, model call, browser helper, or hook was launched or configured for this check.

## Local observations

Both executables are installed: `codex --version` returned `codex-cli 0.165.0`; `claude --version` returned `2.1.300 (Claude Code)`.

`codex features list` reports `hooks`, `shell_tool`, and `unified_exec` as stable and enabled in that CLI invocation. This establishes available feature settings, not that project hooks are trusted, installed, or exercised in this chat. The IDE extension, desktop surface, and a separately launched CLI may differ.

The user has already reported successful Impeccable browser interaction with both Claude Code and Codex. Source evidence for that workflow remains in docs/research/browser_handoff_research.md.

## Support targets and OpenRouter requirement

The user requires support for Claude Code and Codex. OpenCode, Pi, Hermes, and DeepSeek Harness are additional candidates to compare, rather than four more hosts already promised for the first demonstration.

At least one supported host must allow the human to choose underlying models through OpenRouter. This may be a host already in the required set if its integration meets our needs; it does not inherently require a third host or a provider client owned by this workspace. Preserve the user's aim of model choice rather than pinning the writer to one vendor or a previously selected DeepSeek version.

### Initial primary-source findings

| Candidate | OpenRouter evidence | What remains unverified for this workspace |
| --- | --- | --- |
| OpenCode | Current V2 docs include a native OpenRouter provider/catalog and OpenRouter model IDs. [Provider docs](https://opencode.ai/v2/docs/providers#gateways). | Version to support, portable skill discovery, wait behavior, and concrete checkpoint enforcement. Do not mix V1 and V2 configuration assumptions. |
| Pi | Provider docs describe OpenRouter login/key support and model discovery. [Provider docs](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/providers.md#openrouter). The previously named badlogic/pi-mono repository redirects to earendil-works/pi. | The extension/hook and waiting integration needed by the story workspace, actual local installation/version, and representative model behavior. |
| Hermes | Current model documentation shows OpenRouter as the main provider and supports switching its model. [Model configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models). | Current project-local packaging, wait lifecycle, and useful hooks in an ordinary existing session. The prior project's pinned host/controller is not the baseline. |
| DeepSeek Harness | OpenRouter documents an Ori launcher that configures and launches the existing DeepSeek Harness with OpenRouter model choice. [OpenRouter's DSH integration](https://openrouter.ai/ori/harness/dsh). | Native versus launcher-dependent setup, project skills, hooks, local input delivery, and the added launch dependency. No adoption of Ori is selected. |
| Claude Code / Codex through an OpenRouter integration | The same OpenRouter page lists launch paths for these existing agents. This is evidence of an integration offered by OpenRouter, not proof that every host feature and model pairing works for us. [OpenRouter integration listing](https://openrouter.ai/ori/harness/dsh). | Exact compatibility and whether this is simpler than using native OpenRouter support in another host. Neither required host's normal account behavior is replaced by assumption. |

OpenRouter model selection and reliable operation of this workspace are separate claims. The capability check must still establish file/tool use and the required lifecycle for the chosen host/model pair. Keep model choice open; do not turn that goal into an untested promise that every catalog model performs identically or follows the skills reliably.

This is a documentation shortlist. No additional host, launcher, credentials, or model was installed, configured, or called.

## Claude Code

The documented shell supports background commands, output files, and host-managed task lifetimes. An interactive local session differs from a non-interactive `-p` run, so a print-mode process should not be treated as equivalent to the existing interactive session. [Interactive session behavior](https://code.claude.com/docs/en/interactive-mode#background-bash-commands).

There is also a documented native `Monitor` tool: a small script can emit lines when inputs change and the host delivers those events to Claude. Watches expire and require renewal. On Windows the tool requires Git Bash; some provider/configuration combinations require a newer version than the locally observed one. Its availability in the user's actual session remains untested. This is an alternative host integration for the same shared files, not a reason to add a browser-to-model API. The tools reference also distinguishes shell timeouts and task lifetimes. [Tools reference](https://code.claude.com/docs/en/tools-reference#monitor-tool).

Hooks support concrete blocking decisions. `Stop` can require continuation; project settings and skill frontmatter are documented hook sources. Registration, trust, limits, and runtime behavior must be checked for the selected packaging. Watching files through a `FileChanged` hook is not by itself evidence that the writer receives another story input. [Hook reference](https://code.claude.com/docs/en/hooks).

## Codex

OpenAI documents long-lived command sessions using `exec_command` and output retrieval through `write_stdin`. This supports the yielded-foreground wait pattern described by Impeccable. A process running separately is not, by itself, a promise that an idle writer resumes; servicing its result remains necessary. [Official tool guidance](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide).

Project-local hooks can live in `.codex/hooks.json` or project configuration. Non-managed hooks require review and trust of their current definition; changed definitions are skipped pending review. `Stop` can request continuation with a reason. Command hooks are supported, while prompt/agent hook handlers are currently parsed but skipped. These facts matter for packaging and writer-edited hooks: writing a hook file and activating it are distinct operations. [Official hook reference](https://learn.chatgpt.com/docs/hooks).

This is documented behavior plus a local feature-settings observation. No hook enforcement or autonomous input pickup has been tested on the installed CLI or the current IDE session. Documentation may include capabilities whose exact release/surface coverage still needs checking.

## Consequences for the smallest package

The same public story/Director files and local browser/file helper can remain portable. Host-specific guidance can explain whether to use an ordinary command wait, a host background task with result delivery, or an available native monitor. Do not require all hosts to expose every option.

The script should stay quiet when there is no input and report only new human entries. Polling or watching can happen locally without model calls for every filesystem check. A helper timeout, monitor deadline, or output-service call can still cause host/model overhead; actual idle usage remains to be observed.

### Hook boundaries need deliberate selection

A host turn can contain several story exchanges if the writer repeatedly waits through its tools. A `Stop` hook checks at the end of that host turn, so it does not automatically enforce a checkpoint after every prose response. This is an inference from the documented event boundary and our proposed loop.

The user accepts writer-chosen commit granularity. Do not silently add a commit-per-response rule to solve that mismatch. Investigate which concrete checkpoint condition is useful, and whether to check it at host completion, before an input wait, or another supported boundary. A lightweight helper check may complement a host hook; no choice is made here.

Hook checks can establish file/commit conditions. They cannot prove that every important character fact was recorded or that a hidden explanation is believable.

### First-host selection remains open

Claude Code's interactive background-work path and the documented Monitor alternative made it a useful initial candidate for observing input delivery; Codex has a documented command-session path and locally enabled hooks. The required OpenRouter route now also makes OpenCode and Pi useful direct-provider comparisons, with Hermes and DeepSeek Harness still candidates. The same shared files/helper may cover several hosts, so documentation alone does not establish a decisive code-size winner. Compare setup, waiting, hooks, and model behavior without introducing an application-owned controller.

## Restart without saved host context

The user explicitly requires continuation from durable workspace files without the prior agent context window. Resuming saved host conversation history is a convenience, not a dependency. The workspace must make its prose, established events/disclosures, private plans, characters, preferences, Director corrections, and working-note entry points discoverable enough for a fresh compatible session to continue. It need not preserve private model reasoning or impose a fixed internal world schema.

The working reopen experience is to start a compatible agent in the existing story directory, invoke its writer guidance, and have it read the saved materials and reopen the local interface as needed. A persisted browser log and a resumed host transcript are different things. A closed helper may need relaunching; no process is assumed to survive closing the host.

Whether a real writer captured enough knowledge for this to work is an outcome to evaluate. A hook proving files or commits exist does not prove that outcome. The remaining uncertainty is execution quality and discoverability, not whether saved context history is required.

## Evidence still needed before compatibility claims

- The actual host surface can start the local interface and return a browser-written input to the existing writer session repeatedly.
- Waiting is local, with observed host handling and idle overhead; timeouts do not silently abandon the session.
- The chosen checkpoint hook actually runs and blocks or redirects completion as intended under normal host permissions.
- Restart/resumption reads durable workspace materials and preserves the human's corrections, rather than merely reopening an old transcript.
- Changed skills/hooks have a clear activation path that respects the selected host's normal trust behavior.

These are focused compatibility questions, not an approved implementation sequence or the earlier project's evidence gates. Do not start a custom harness to avoid finding out what the existing host supplies.
