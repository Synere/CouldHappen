---
type: research
status: completed
updated: 2026-11-11
---

# Browser input reaching an existing agent

**Purpose.** A record of what was investigated before the design was approved. It is kept as evidence and is not updated.

> Historical research record. Current scope and implementation decisions are in the [approved design](../designs/couldhappen.md); start a future implementation session with the [handoff](../history/implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../history/archive/README.md).

- Investigated: 2026-11-03 (Asia/Manila)
- Stage: EGM clarification; source investigation, not a design or implementation
- Scope: Trace browser input, local waiting, and output display in the two projects the user identified.
- Evidence: Source inspection at the revisions below. Neither project was installed or run for this investigation. The user's firsthand experience is recorded separately from the source findings.

## Finding

Impeccable contains a close precedent for the proposed workflow: a local question page can write an answer file, and an agent-invoked terminal command waits for that file and returns its contents. Its Live mode supplies a second precedent using local HTTP event delivery. These mechanisms give the host a tool result to continue from; they do not independently restart a finished agent session.

The decision page is part of a shared workflow shipped for multiple agents. Claude Code and Codex are two hosts where the user reports having used it successfully. Browser input reaching an existing agent is therefore an established precedent for this investigation; the remaining compatibility work concerns our repeated story loop, session limits, recovery, and chosen hooks.

The HyperFrames path inspected here demonstrates launching a browser studio, refreshing it after file changes, and letting an agent retrieve browser selection context. That path does not establish the same continuous browser-input loop. This is a limit of the inspected path, not a claim that every HyperFrames release or integration lacks such a loop.

## Impeccable: decision-page path

Revision: `9fadc41729c38fd47d7ae622b501558653f9d2e9`.

1. The agent supplies a question payload. `serve-question --start` starts a detached local server. The server binds to loopback, records its address, and opens the system browser. The command also has a foreground serving mode. [Start and serve source](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/context/src/serve_question.rs#L1483-L1635).
2. The browser posts the answer to `/answer`. In detached mode the server writes `.impeccable/questions/<key>.answer.json`. [Answer handler](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/context/src/serve_question.rs#L1787-L1903).
3. The agent invokes `serve-question --wait --key ...`. That command checks for the answer file locally, sleeping between checks. On receipt it prints the answer and exits. It can also return that it is still waiting, that the page closed, or that the server failed. [Wait implementation](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/context/src/serve_question.rs#L1311-L1405).

This is a file-backed handoff. HTTP connects the browser to a local helper; the host's normal terminal tool delivers the helper's result to the agent. A direct browser-to-model integration is unnecessary for this path. That last sentence is an inference from the traced path, not a compatibility test on our intended host.

The wait defaults to a bounded period and may need calling again. Do not equate local file checking with repeated model calls: the individual checks run inside the helper. Returning a no-input result to the agent can still create model overhead. Its timing values are evidence about Impeccable, not selected CouldHappen defaults. [Wait timing and result handling](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/context/src/serve_question.rs#L1316-L1385).

## Support across agents

Impeccable's installation documentation lists Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Grok Build, Antigravity, OpenCode, Pi, Hermes Agent, Devin, Replit Agent, Kiro, and other tools, with matching builds. Its new-work documentation presents the browser picker as a general workflow and explains that choices move into the conversation when the browser page cannot run. [Installation and tool support](https://impeccable.style/tutorials/getting-started/), [Browser picker documentation](https://impeccable.style/docs/new-work/).

The source skill directs the agent to load the new-work reference for a new surface. Published Claude Code, Gemini CLI, and shared-agent bundles each contain the same decision-page command and wait guidance. This supports treating the mechanism as a portable package convention, with host-specific execution handling where needed. [Source skill setup](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/skill/SKILL.src.md#L19-L23), [Claude Code reference](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.claude/skills/impeccable/reference/new-work.md#L53), [Gemini CLI reference](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.gemini/skills/impeccable/reference/new-work.md#L53), [Shared-agent reference](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.agents/skills/impeccable/reference/new-work.md#L53).

Overall package support and inspected bundles are evidence of the intended reach; this investigation has not run a test matrix across every listed host. Such a matrix is not required to acknowledge the existing precedent or continue brainstorming. The user's two firsthand examples give us practical initial candidates without requiring a host choice now.

## Impeccable: Live path

Live mode documents a repeated cycle: start the helper, open the page, run `live-poll`, handle an event, reply, and poll again. It distinguishes host handling: Claude Code background completion notifications, Cursor background-terminal notifications, and a Codex foreground command that yields an execution session and must keep being read. These are Impeccable's instructions, not independently verified host guarantees. [Live workflow and host policies](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/skill/reference/live.md#L13-L30).

The implementation receives browser events over HTTP and makes them available through `/poll`. The CLI waits through local HTTP requests and returns an event to its caller. This is not the decision page's answer-file transport. [Browser events and agent poll routes](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/live/src/live_server.rs#L931-L971), [CLI waiting](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/crates/live/src/live_poll.rs#L347-L399).

Live includes recovery journals and event-delivery bookkeeping beyond a basic wait. They address its own editing workflow; they are not automatically required for a story workspace. [Live recovery guidance](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/skill/reference/live.md#L70-L80).

## HyperFrames: inspected Studio path

Revision: `5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e`.

- The preview command can start or reuse a background preview and open Studio in a browser. [Preview startup](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/cli/src/commands/preview.ts#L517-L573).
- Studio publishes its selected element to a local API. The matching route stores the current selection in an in-memory map. [Browser publisher](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/studio/src/hooks/useStudioSelectionPublisher.ts#L29-L62), [Selection storage and routes](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/studio-server/src/routes/selection.ts#L100-L139).
- `preview --selection` retrieves that information; `preview --context` advertises a broader agent-readable context. These are explicit CLI reads. [CLI context options](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/cli/src/commands/preview.ts#L201-L225), [Selection retrieval](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/cli/src/commands/preview.ts#L947-L1023).
- A file watcher sends change notifications to the browser through a server event stream. This explains file edits appearing in Studio; that direction of notification does not itself wake the writer. [File-change stream](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/cli/src/server/studioServer.ts#L962-L1008).

## Implications to discuss

The closest starting pattern is Impeccable's file-backed decision-page handoff, extended conceptually to repeated story inputs and outputs. Reusing that pattern need not mean importing its implementation, design-specific payload, native binary, telemetry, or all its lifecycle rules. This is a proposal, not an accepted dependency or package specification.

A candidate minimal loop remains: the host starts an editable browser page and local file helper; the writer runs a local input wait; the human submits through the browser; a new human entry in a shared file lets that wait return; the writer reads input, writes story and notes, then waits again. The helper handles local I/O. Story decisions and the agent session remain with the existing writer and host. The user's latest proposal places story inputs and responses in the same conversation file, with a likely separate Director log; this is a CouldHappen proposal, not a claim about Impeccable's file layout.

An HTTP listener used only to bridge a browser to local files fits the user's allowed local-helper role. It does not require an application-owned agent execution service. A helper that begins choosing model calls, owning writer sessions, or coordinating every story turn would change that cost and responsibility boundary and needs separate justification.

The loop needs a small way to distinguish new input from previously handled input and to avoid processing half-written input messages. Incremental prose output is a separate, intentional display choice. The precedents establish neither a required schema nor the smallest solution for our story workspace. Verification should target the added requirements: repeated play, interruption, correction, restart, and any blocking hooks we choose to rely on. Do not reopen basic browser-to-agent feasibility as though no working examples exist.

Both the decision page and Studio show that an interface can respond to files arriving or changing. That supports incremental file-driven display as a possibility; it does not establish access to model tokens while the writer is generating them. The user now favors incremental file-driven prose updates with freedom of editing method; see the working display discussion in docs/planning/brainstorming_notes.md. [Decision-page image arrival behavior](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/skill/reference/new-work.md#L53), [Studio change stream](https://github.com/heygen-com/hyperframes/blob/5e30bbdbe14b8295f8102c6439aa8bfdacc0fd1e/packages/cli/src/server/studioServer.ts#L962-L1008).

## User decisions and remaining questions

- Confirmed by the user: launch the workspace in an existing agent, open the browser, wait locally for browser input, continue writing, and wait again is the intended ordinary workflow.
- Confirmed by the user: use Impeccable to design the initial template interface. This does not select an aesthetic, frontend stack, or Impeccable as a runtime dependency during play.
- User-reported evidence: they used Impeccable's browser interaction successfully with both Claude Code and Codex. Exact versions were not supplied. Both are initial compatibility candidates; no exclusive first host has been selected.
- Research update: the decision-page workflow is shared across multiple published agent bundles. The earlier emphasis on only two or three host-specific Live instructions understated this broader support.
- Accepted presentation direction: save prose normally and animate new prose in the browser; explain that behavior to the writer. The writer may choose its editing tools and scripts. Established prose changes only on Director instruction; authorized revisions can update directly, with an indicator if inexpensive. No implementation exists yet.
- Working public-file proposal: human story inputs and writer responses share one conversation log, with Director discussion probably in a separate shared log. Private notes remain separate. Input recognition, conflicting saves, and coordination between logs still need discussion.
- Latest user direction: the writer chooses whether to block Director submissions during prose production. Browser Stop is deferred, in favor of being able to Undo an unwanted interaction through Git-based workspace recovery. The writer chooses commit times; hooks should ensure changed work is checkpointed. Hook enforcement and Undo mechanics are requirements to investigate, not capabilities established by the Impeccable source inspection.
- Undo clarification: this is a Director instruction. The user accepts that available commits limit restoration precision, and the writer must state those limits honestly. After restoring, it asks for direction in the Director conversation and waits before writing more fiction. Exact per-interaction rollback is not required.
- Image direction: use supplied character-card PNGs in the first short demonstration, with AI generation deferred. The user authorized selective read-only inspection of MightHappen's imagery work; findings are in docs/research/prior_imagery_findings.md. Initial adaptable generation guidance remains a package goal.
- Template update: the cast panel is accepted, Accept/Revise is removed, and an actual fresh Impeccable comp-led design pass is scheduled after the minimum demonstration has a concrete brief. Skill installation and API-key presence are confirmed; no image request or credential validation was performed.
- The user accepted the short-demonstration scope. Initial official-doc and local CLI findings are in docs/research/host_compatibility_notes.md; both hosts remain candidates, with no live writer-loop or hook test claimed.
- Restart direction: fresh-context continuation must work from durable workspace files; saved host chat history is optional.
- Support targets: Claude Code and Codex are required, with OpenCode/Pi/Hermes/DeepSeek Harness as additional candidates and an existing-host OpenRouter route required. Expanded source findings are in docs/research/host_compatibility_notes.md.
- The anchored hypothesis in docs/history/planning/brainstorming_notes.md is now presented for the user's EGM readiness decision. No Goldfish transition has been approved.
- Still open: acceptable exceptional interruptions, host lifetime and resumption, demonstration scene and coverage, display/reveal details, public portrait association, and recovery mechanics.

Stay in brainstorming. Host selection, Goldfish readiness, formal drafting, and implementation have not been approved by these findings.
