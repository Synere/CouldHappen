# Host integrations

CouldHappen's core writer skill is harness-agnostic. The agent establishes its actual tools, permissions, wait behavior, and completion boundary. The native checkpoint examples here are optional, not compatibility certificates, and they are not installed automatically.

Use the same [setup](setup.md) and [public contract](public-contract.md) on every host. Setup step 9 defines the standing wait; this page records only what differs per host.

## Host status

All hosts are **experimental**. None is certified, and there is no required test order.

| Host | Status | Skill discovery | Observed so far |
| --- | --- | --- | --- |
| opencode | Experimental — one successful story-workspace test | Finds the skill in `.agents/skills/` | Setup, background standing wait, card import, play, Undo, reset, and fresh-context reentry. |
| Codex interactive CLI | Experimental — not yet tested | `.agents/skills/couldhappen/` | Nothing yet. |
| Claude Code interactive CLI | Experimental — one session | `.claude/skills/couldhappen/SKILL.md`, an entry point that hands off to the canonical skill | Skill discovery and a standing background wait (0.1.4, Sonnet 5.5). A host restart ends the wait silently. |
| Pi with OpenRouter | Experimental — not yet tested | Not verified; if the skill is not listed, ask Pi to read `.agents/skills/couldhappen/SKILL.md` | Nothing yet. |

On any host, asking the agent to read `.agents/skills/couldhappen/SKILL.md` explicitly always works; automatic discovery is a convenience. Edit only the canonical skill under `.agents/`.

<!-- dev-only -->
Evidence for each row lives in [validation results](validation-results.md); update both together.
<!-- /dev-only -->

## opencode

opencode lists project skills, so the writer finds `couldhappen` without being pointed at it. Its shell tool can run a command in the background and notify the agent when it finishes, so a background `python -u -m helpers wait --root . --timeout 0` works as the standing wait; renew it after each handled entry. Foreground tool calls were capped at about 45 seconds, so foreground waits must stay under that. No native checkpoint example is supplied for opencode; checkpoint assurance there is guidance-only.

## Codex interactive CLI

Read `integrations/codex/hooks.example.json`; substitute actual interpreter/workspace paths and platform-appropriate quoting. In an authorized play setup, merge the Stop fragment into `.codex/hooks.json` without replacing other hooks. Review and trust it through the native mechanism.

The wrapper reads the native event's cwd and checks persisted armed play scope. Dirty work returns exit 0 with `decision: block` and a concrete reason; clean/inactive work returns `{}`; errors return a `systemMessage` warning of unavailable assurance. `stop_hook_active` is diagnostic context, not a skip switch. Observe actual dirty/clean completion and wait behavior, including whether another hook or a host limit prevents corrective continuation.

<!-- dev-only -->
The examples were written against Codex 0.165.0; verify the installed version and its current help/settings first. Do not activate the hook in this development repository merely while implementing the application.
<!-- /dev-only -->

## Claude Code interactive CLI

Claude Code discovers the skill through `.claude/skills/couldhappen/SKILL.md`, which hands off to `.agents/skills/couldhappen/SKILL.md`. Merge `integrations/claude/settings.example.json` into `.claude/settings.json` only during an authorized play setup, and use normal native trust. The wrapper translates the same clean/dirty/error results at Stop. Demonstrate the actual shell wait and native event behavior, recording interruption and renewal limits.

<!-- dev-only -->
The example was written against Claude Code 2.1.300; verify the installed version. No newer native Monitor or background-payload semantics are assumed.
<!-- /dev-only -->

## Pi with OpenRouter

The supplied TypeScript example targets `@earendil-works/pi-coding-agent@1.5.0` and its before-settle boundary: it appends a continuation instruction while scoped work is dirty, reports errors or inability to continue, and bounds unchanged dirty-status retries. Copy `integrations/pi/checkpoint.ts` to `.pi/extensions/couldhappen-checkpoint.ts`, set `COULDHAPPEN_ROOT` and `COULDHAPPEN_PYTHON` in the host environment, and verify extension loading. OpenRouter credentials and model selection remain in the user's host configuration; no key belongs in this workspace. The human selects the actual underlying model.

## Common limits

Writer claim arms managed play; unrelated development sessions remain ungated. Deliberate closure checks Git before disarming. Tests of wrapper output do not prove hooks were reached, trusted, or able to continue. Forced termination can bypass checks. Record versions, model/provider, wait invocation, renewals, activation/trust, dirty/clean behavior, aborts, permissions, and failures. File existence or source inspection is not evidence of native execution.

<!-- dev-only -->
Follow [the validation procedure](validation.md) for scene, handoff, and Undo observations.
<!-- /dev-only -->
