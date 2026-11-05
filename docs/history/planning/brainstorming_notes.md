# CouldHappen: skill-based fiction workspace investigation

> Historical planning record. Current scope and implementation decisions are in the [approved design](../../designs/couldhappen.md); start a future implementation session with the [handoff](../implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../archive/README.md).

- Author: Synere (from git configuration)
- Started: 2026-11-03 (Asia/Manila)
- Stage: EGM Step 3 — discussion and refinement after Goldfish review
- Status: All six Goldfish reviews completed; docs/planning/concepts_brief.md is a reviewed working brief awaiting user iteration and approval. Formal design, implementation, and first-host selection remain pending.
- Starting authority: The user's fresh-project handoff in this conversation. MightHappen is optional, read-only historical background; its approvals do not apply here.

## Working hypothesis

A portable project directory can give an existing agent the guidance and materials needed to act as an author and game master. A supplied, editable browser interface records human inputs in shared files and displays the writer's outputs; the host supplies the agent's execution loop, tools, and session behavior. A small local helper may bridge browser access and file waiting, provided it does not grow into an application-owned agent controller.

Support targets are Claude Code and Codex, with OpenCode, Pi, Hermes, and DeepSeek Harness under consideration. At least one supported host must offer user-selected underlying models through OpenRouter using an existing integration. Continuation must work from workspace files without saved host conversation context; resuming that context is optional.

The main uncertainty is whether a chosen host can sustain a useful browser play session by waiting locally for inputs, continuing when a wait returns, and resuming from durable files after interruption. Skill discovery alone proves none of those behaviors. Shared files are the starting communication hypothesis, open to comparison with smaller alternatives after their actual requirements are understood.

The user has since confirmed the intended ordinary workflow: open the workspace in an existing agent, have it launch the browser, wait locally for browser-written input, process each input, write the continuation and notes, and wait again. The acceptable handling of exceptional session interruptions is still open.

The current public-file proposal is a shared story conversation log: the interface adds the human's story input, and the writer adds its prose response to that same file. Director discussion would probably have its own shared log. Private notes remain separate and continue to carry the world knowledge needed after context loss.

## Decisions made during this brainstorm

- 2026-11-03: The user confirmed the launch/browser/wait/write/repeat workflow described above.
- 2026-11-03: The user selected [Impeccable](https://github.com/pbakaus/impeccable) for designing the initial template interface. No visual theme, framework, or runtime dependency follows from this choice.
- 2026-11-03: The user reported having used Impeccable's browser interaction with both Claude Code and Codex, and highlighted its broader host support. Treat both as available initial candidates, without selecting an exclusive host or assuming identical hook/session behavior.
- 2026-11-03: The user favors incremental file-driven prose display for the first version. The writer should understand the display behavior and remain free to modify prose through its available file tools, scripts, or other supported methods. A staged full response followed by a character-by-character writing helper is a possible technique; bundling such a helper remains a proposal.
- 2026-11-03: The user accepted saving prose normally and animating its appearance in the browser. Teach the writer this display behavior. The earlier character-by-character disk-writing idea is no longer needed to obtain that effect.
- 2026-11-03: The writer must preserve established prose unless the human, acting as Director, instructs it to revise it. Authorized revisions may appear immediately without animation; an indication of changed passages is desirable if inexpensive. The exact indicator is not selected.
- 2026-11-03: New user proposal: use one shared file as both the story input and prose-response conversation log, with a likely separate log for Director discussion. Treat this as the working public-file arrangement; format, concurrent access, and coordination between logs remain open.
- 2026-11-03: The user wants the writer to signal specifically when it is producing a story response, allowing the UI to block Director submissions during that phase. Private note-taking, skill creation, and other workspace work should not by themselves block Director input. The user also proposes a separate Stop control to halt story writing and allow Director discussion; the cancellation mechanism and guarantees remain open.
- 2026-11-03: Clarification superseding the mandatory-block interpretation above: the writer chooses whether to block Director submissions while producing prose. Defer the browser Stop feature for now. The user's concern is that stopping a whole agent could interfere with delegated work; exact host cancellation behavior is not assumed.
- 2026-11-03: The user reaffirmed Git for workspace history, including prose. The writer chooses meaningful commit times, with hooks ensuring changed work is checkpointed. Undo must successfully revisit the latest interaction and its associated workspace changes; one interaction may contain multiple commits. Hook events, enforcement details, and recovery mechanics remain to be investigated.
- 2026-11-03: Undo is a Director action handled through Director input. The user accepts that writer-chosen commit timing limits how precisely an interaction can be undone. The writer must explain what the available commits can recover and must not promise an exact restoration unsupported by history. This qualifies the stronger latest-interaction guarantee in the preceding entry.
- 2026-11-03: After restoring a checkpoint, the writer asks the human for direction in the Director conversation and waits for that input before producing more story prose. It does not automatically regenerate the rejected response.
- 2026-11-03: For the first short demonstration, use the PNG imagery supplied with imported character cards and defer AI image generation. The user authorized selective read-only inspection of MightHappen's imagery/UI work. Findings are in docs/research/prior_imagery_findings.md; previous-project approvals remain historical, not blanket approvals for this template.
- 2026-11-03: The user accepted the cast-panel idea and explicitly removed Accept/Revise controls from the new template direction. Undo/revision remains available through Director instructions rather than a required response-acceptance workflow.
- 2026-11-03: The user requested a fresh actual Impeccable new-work pass, explicitly comp-led, because the prior UI felt boring. Honor that choice for this application interface even if a skill default would otherwise prefer code-led. The user allowed running it now or later in brainstorming; defer the actual pass until the minimum demonstration and its main states are anchored, to give the mockups a concrete brief. This is a scheduling choice within the user's allowed timing, not a skill-imposed approval gate.
- 2026-11-03: Availability check: Impeccable's local SKILL.md is installed and a non-empty OPENAI_API_KEY is available to this process. Only presence was checked; no key value was displayed or stored, no generation request was made, and key validity/billing was not tested.
- 2026-11-03: The user accepted the proposed first short demonstration as the working scope: one scene with a world prompt and imported cards, several browser story exchanges, a Director exchange, and Git-supported Undo that reports its limits and waits for direction. This is scope alignment, not EGM readiness approval or authorization to implement.
- 2026-11-03: Claude Code and Codex are required support targets. Compare OpenCode, Pi, Hermes, and DeepSeek Harness as possible additional hosts. It is important that at least one supported host accepts the human's choice of underlying model through OpenRouter. This supersedes treating OpenRouter as merely an optional historical preference; it does not select a new application-owned provider integration.
- 2026-11-03: Fresh-context restart from workspace files is required. Saved host conversation/context history is optional and helpful, not a dependency. Important story knowledge must be durable and discoverable; the context window is supplementary reasoning context.
- 2026-11-03: The user accepted the carry-over behaviors in docs/research/carryover_audit.md. Director discussion is constructive back-and-forth that can inspire both parties and influence future writing without automatically advancing fictional time or establishing hypothetical events. Imports are Director actions; compatible adaptation is autonomous, while genuine conflicts between initial identity and an explicit world premise ask for Director guidance. Card greetings, examples, and roleplay instructions are source material rather than automatic story events or governing writer instructions.
- 2026-11-03: The user affirmed that the writer reads its prose for voice, pacing, and continuity. Preferences can be given naturally through Director input; the writer records and applies them and can reorganize its methods to fit. No fixed preference-injection machinery is implied. Director chat is the main place for discussion of work, problems, and failures; reuse host diagnostics rather than requiring a separate activity dashboard.
- 2026-11-03: The user explicitly approved the EGM review transition with "review now with the goldfishes". Begin fresh-context BRAINSTORM reviews and synthesis; this does not approve the resulting concept brief or the transition to formal drafting.

## Carried-over requirements and preferences

These come from the new handoff, rather than approval of the earlier architecture.

### Creative experience

- The agent writes prose, dialogue, characters, pacing, and consequences. One writer can portray the whole cast; delegation is optional where the host supports it.
- The human plays a character and can separately give Director instructions, discuss the story, contribute prose, and change preferences. In-world action and out-of-character communication must be distinguishable.
- Start from a human-supplied world prompt. Keep different genres and worlds possible.
- Preserve meaningful player influence and believable consequences.
- Distinguish established events, claims disclosed to the player, private plans, and possible developments. Their storage is the writer's choice.
- Hidden explanations may change to improve a believable continuation that respects established and disclosed information, including after an unexpected player deduction. Neither the player's theory nor the writer's original private plan automatically controls the truth.
- Creativity and adherence preferences must be expressible. Exact controls and storage remain open.
- Director discussion can generate inspiration, revise private possibilities, and shape preferences or methods without automatically advancing fiction or making hypothetical events canonical. Later writing may draw on that inspiration consistently with established/disclosed material. Explicit instructions can authorize continuation or changes to presented fiction.
- Import SillyTavern character cards from PNG and JSON, preserving original sources and any supplied PNG portrait. Cards establish initial identity by default; later development is allowed, with stricter adherence available as a preference. Prior import machinery and acceptance matrices are not binding.
- Imports are Director actions, including additional cards during play. Adapt compatible starting details autonomously; ask the Director when preserving a card's initial identity genuinely conflicts with an explicit world premise, and retain the resolution. Card examples, greetings, and roleplay instructions do not automatically govern the author/game master or become established events. Import does not by itself reveal the character in the public cast.

### Workspace and persistence

- Supply initial skills, supported hooks, templates, and small helper scripts. Investigate the minimum useful set.
- Maintain a readable manuscript/prose log and enough durable knowledge to continue after context loss or restart. A growing transcript must not be the primary world representation.
- Start with guidance for character tracking, disclosure tracking, preferences, and discoverable working notes. The writer may reorganize its records and change its methods; these are outcomes rather than a fixed schema.
- The writer consults previous prose for voice, pacing, and continuity, choosing useful portions rather than loading the entire log every time. Director-supplied preferences should become durable and inform subsequent work; the writer may adapt or reorganize its own methods to do so.
- The writer may edit its skills, write scripts, and use host-supported hooks and subagents. A helper called through an existing terminal tool may be sufficient for a mechanic; native tool registration is not required by default.
- Hooks may remind the writer to keep records or enforce concrete completion conditions where supported. An existence check for a checkpoint cannot establish that all important facts were recorded.
- Git is the working choice for checkpoints and recovery, reaffirmed during brainstorming. The writer chooses commit times, supported by hooks that ensure changed work is checkpointed. Aim to revisit unwanted story material with its associated notes and working changes, while being explicit about the actual restoration scope available from the commits. Exact interaction-by-interaction rollback is not guaranteed.
- Replacement after rejection must retain applicable human corrections and preferences without treating rejected assistant plans or prose as continuing story authority. File rollback alone does not establish removal from a live agent's context.
- A complete branching history tree is a possible later feature. Formal game mechanics and general tool-registration systems can wait.

### Browser and images

- Supply a minimal browser interface for play. Its presentation and code are editable materials the player or agent can customize.
- Prose, Director interaction, and preferences need understandable treatment. A reading/chat presentation is suitable; visual-novel presentation and portraits remain possible.
- Director chat is the primary place for constructive discussion, explanations of work, and actionable failure reports from the writer. Working commentary stays separate from fiction. Existing host diagnostics remain available; no separate custom activity dashboard is required. A helper/host outage may still need a plain UI status when the writer cannot report it; its exact handling remains a design question.
- Display file-driven prose changes and animate new prose in the browser after normal saves. The writer knows that this is how its writing appears and retains freedom of editing tools. Established prose stays unchanged unless the Director instructs a revision; authorized revisions can update without animation, with a changed-passage indicator if inexpensive. Raw model-token access is not required. Do not import the earlier publication protocol.
- Include initial guidance for using available image tools and exposing resulting assets to the interface. Discuss the first demonstrator's image workflow before review readiness.
- Image generation may use host or user capabilities. Do not require a particular provider or assume built-in generation. Instructions and scripts must be adaptable.
- The first short demonstration uses supplied character-card PNGs in a cast panel; AI-generated story imagery is deferred. Initial guidance for future/user-supplied generation remains part of the package goal. A separate comp-led Impeccable pass will use generated interface mockups during design; that does not add runtime image generation to the demonstration.
- No visual theme, frontend framework, or component structure is selected.

### Practical limits

- Favor trusted local use and the existing host's normal permissions. No default container, sandbox service, or elaborate permission layer.
- Use host/user credentials and configuration; keep credentials out of story records and source control.
- Cost and responsiveness matter. Claude Code and Codex may use their normal model/account setups, but the package must also support user-selected models through OpenRouter in a suitable supported host. Specific DeepSeek model versions and a workspace-owned provider client are not selected.
- Earlier numerical budgets, timeouts, dependencies, and implementation stages do not carry over.
- Keep all new investigation artifacts in CouldHappen. Do not alter MightHappen or copy credentials from it.

## New proposals, not accepted decisions

- Settle the shortest useful browser play session before choosing package contents.
- Compare hosts on the code and setup they actually require for that experience, including their behavior while waiting and after interruption.
- Consider a short scene before an eventual complete mystery arc. The eventual arc should exercise continuity, deductions, revision, and changes in the writer's working methods. The short scene's exact coverage is still open.
- Keep the browser/writer agreement limited to what must cross the boundary: recognizing new inputs, finding outputs, and handling changes to those conventions. Do not prescribe private world records through this agreement.
- Let a packaged capability check identify missing host features. Agent-created integrations may be possible, but their limits, maintenance cost, and effect on the no-custom-harness goal require examination.

## First demonstration: accepted working scope

Use one short scene initiated by a human world prompt and supplied character cards. Open the browser from the existing agent, show the card portraits in the cast panel, and sustain several player/writer exchanges through the shared story log. Include a Director exchange and an unwanted continuation that the human asks to undo; the writer explains available recovery, restores what its checkpoints support, and waits for Director guidance. Observe the resulting prose log and notes as durable materials.

The user accepted this experience sketch as the working scope. It is not an implementation plan or approved test matrix. First host and whether restart/continuation belongs in this short run or a separate early check remain open. A complete mystery arc remains the later, more demanding demonstration.

## Scheduled Impeccable design pass

Run the actual installed Impeccable workflow after the short demonstration's scope and main interaction states are clear. Use the user's explicit comp-led choice, preserve the cast-panel arrangement, remove Accept/Revise, and develop a new visual direction rather than inheriting the earlier Serial fiction look. The user wants a more interesting interface while retaining readable story prose and cross-genre use.

The [new-work documentation](https://impeccable.style/docs/new-work/) describes reviewing compositions before implementation and notes that translation into working UI may require iteration. The brainstorm pass should produce visual direction/mockups for discussion. Formal design and application implementation still wait for the EGM transitions already requested by the user.

Impeccable's skill is already installed. OPENAI_API_KEY presence was verified without exposing its value; no installation, image request, or persistent Impeccable configuration was performed in this check. At execution, read the applicable installed instructions and use the already-authorized comp-led preference without reopening that choice. The documentation distinguishes session-specific workflow choices from a saved project default; the user has selected this design pass, not a global default for unrelated projects.

## Assumptions that need evidence

| Question | Current evidence or limit |
| --- | --- |
| Which host offers the smallest working package? | Claude Code and Codex are required support targets; compare OpenCode, Pi, Hermes, and DeepSeek Harness for an existing OpenRouter route and minimal integration. No exclusive first host is selected. |
| Can a terminal wait return on browser-written input and let the writer continue repeatedly? | Not tested for a candidate host. A running helper and an idle session waking are different claims. |
| What bounds a play session? | Host limits, cancellation, quota behavior, waiting cost, and restart behavior remain unverified. Do not promise indefinite operation. |
| What session/context does the writer occupy? | A project-directory host session is the working possibility. Fresh-context continuation must use durable files; resuming host chat history is optional. A skill does not create a separate execution environment. |
| Can hooks enforce the needed concrete checks? | Both hosts document blocking/continuation hooks. Local Codex reports hooks enabled; no hook execution was tested. Host turn completion is distinct from finishing an individual story reply. See docs/research/host_compatibility_notes.md. |
| Can rejection remove the effect of rejected material? | Must examine both filesystem restoration and the writer's continuing session context. No guarantee yet. |
| Can file writes provide the desired display cadence? | Working choice: display file-driven changes with freedom of writing method. Check overwrites and file replacements as well as appends. Character animation is a possible presentation feature, not evidence of model-token streaming. |
| How does the first demonstration obtain imagery? | Use preserved character-card PNGs. AI generation is deferred; future generation depends on host/user capabilities. The template's public cast/portrait discovery convention remains open. |
| Can an editable interface preserve interoperability? | Working proposal: a shared story conversation log and a separate Director log. Requires a small discoverable agreement and a way to change it; no schema selected. |

## Alternatives to compare, not decisions already made

- Shared files plus a small local browser/file helper: starting hypothesis. Strongest objection: session continuation may still depend on host-specific behavior, and helper responsibilities can expand into a controller.
- Direct browser file access without a local server: examine actual platform support, user interaction, and watching requirements before calling it smaller.
- Existing host UI for play: a useful lower-code comparison, but evaluate it against the retained browser experience and editable presentation requirements.
- An existing project's studio/file-bridge pattern: reuse only the parts whose behavior is understood; opening a studio does not itself prove a writer can wait for or consume its inputs.
- Direct browser-to-agent API or a custom SDK/controller: not the starting requirement. Reconsider only if a retained requirement justifies the additional code and maintenance, with the trade-off made explicit.

## Prose display: current working direction

### User preference

Let the writer modify the displayed prose through whichever supported method fits its work: ordinary file editing, generated Python or other scripts, incremental appends, or replacing a file. The agreement should explain the displayed material and the browser's behavior, rather than dictate one writing tool or an append-only authoring method.

The user initially proposed staging a complete response in a temporary file and then copying it character by character to the displayed file. The subsequent choice is normal saves with browser-side animation, so a disk-writing animation helper is no longer needed for that effect. Nothing has been implemented.

### Accepted presentation direction

Save prose normally and let the browser animate its reveal. The user has accepted this and wants the agent aware of it. File-driven updates remain compatible with genuine incremental authoring. The full passage being saved before its reveal does not mean it was delivered token by token from the model. Letting the human reveal available text immediately remains a proposed convenience rather than a separately confirmed control.

Both staged character writing and browser-side reveal begin after the staged text has been composed. Neither, by itself, reduces the time spent composing that text. Chunked authoring can make some prose available before the whole response is finished, at the cost of additional writes/tool use depending on the host.

### Established prose and authorized changes

The writer must understand that established prose is preserved. Revising that text requires a Director instruction; freedom to choose an editing method is not permission to rewrite earlier story material at will. This also preserves the distinction between changing a private explanation consistently with prior disclosures and changing the disclosures themselves.

An authorized revision can appear as a direct, non-animated replacement. The user would also welcome an indication of where text changed if that is inexpensive. An elaborate diff interface or edit-history application is not selected. New-response animation must not replay the entire conversation after a file save or reload.

## Shared public conversation logs: working proposal

The user proposes that the browser and writer share the story conversation file. The browser records the human's action or prose contribution there. The writer reads it, reasons and works in its private workspace, maintains notes and other useful materials, then writes the story response back to that same file. The result is a durable, readable story conversation log without a separate input file and response file for every exchange.

Director discussion would probably use a separate shared conversation log. This keeps out-of-character discussion distinct from story material. Exact filenames, format, role markers, and links between exchanges have not been chosen. Creating custom skills, scripts, or hooks remains within the writer's supported capabilities; none is required on every response.

This log can satisfy the readable prose-log outcome if its format is suitable. It does not replace the writer's durable world notes, player-disclosure tracking, or preferences. It does not require a growing transcript to become the primary world representation, or a new copy of the manuscript after every turn.

### Questions the small agreement must answer

- The wait helper must recognize unhandled human entries rather than every change to the file. Otherwise the writer's response could wake its own input wait, or an edit could be mistaken for another player action.
- Both browser and writer can modify the same log. A replacement based on an old copy could erase an intervening entry. Agree on how the first version avoids conflicting saves without requiring one native editing tool or a new orchestration service.
- New prose and Director-authorized edits to older prose need distinguishable display behavior. A particular schema or publication protocol is not implied.
- The writer may choose to block Director submissions while producing a story response. Messages can still arrive when it leaves submissions open; how quickly they are noticed and how they are ordered relative to the next response need clarification.

The prose-writing submission block applies to both ordinary player actions and Director messages. The writer controls when to engage and release it. Private workspace work does not by itself justify an automatic block. This is not a general one-outstanding-input limit throughout all work. Browser Stop is deferred. Safe saving and messages submitted while input is open still need a small agreement.

## Writer-controlled story and Director blocking; Stop deferred

### User-requested behavior

- The writer distinguishes producing a story response from private note-taking, thinking about its own methods, creating skills, and other workspace tasks.
- The same writer-controlled signal can block both player-action and Director submissions during story-response production. The writer controls engaging and releasing the block; it is not tied to the duration of browser-side reveal animation.
- The user has deferred Stop for now and wants to rely on Undo after an unwanted response. Do not include browser cancellation as a requirement of the first demonstration.

The phase is declared by the writer; it does not require a helper to inspect or classify the model's private reasoning. A simple status signal is within the proposed small shared-file agreement. This does not approve importing the earlier Start/Finish publication tools, controller, or transaction machinery. Exact signal storage and clearing behavior are unselected.

### Earlier Stop discussion, now deferred

Earlier proposals considered a separate Stop request, a check before saving a reply, and an acknowledgment before claiming a pause. They are historical discussion, not active requirements. If Stop is revisited, distinguish interrupting composition, preventing a save, and stopping browser animation.

A file request takes effect when the writer or a supported host mechanism reads it. Immediate interruption would need a verified host capability and a way for the browser to reach it. Effects on the parent session, subagents, and running helpers would also need investigation. The user's concern about delegated work is a reason to defer this feature, not proof of a particular host's cancellation behavior.

Browser-side reveal remains independent of story production. A saved reply may still be animating while the agent has moved on to private notes. A future Stop feature must not claim the agent stopped just because the animation stopped.

## Git checkpoints and Undo: current direction

### Required outcome

The prose log is included in Git history, together with the story materials needed for recovery. The writer chooses when to commit as it works. Hooks should ensure changed work is checkpointed, using real enforcement where the selected host supports it. This is not a requirement to commit after every file write or tool call.

Undo is a Director instruction and can use the ordinary Director conversation; a dedicated browser button or separate application command is not required by this decision. The writer inspects available checkpoints and honestly explains what can be recovered. The aim is to revisit the unwanted interaction along with its associated notes and working changes, since reversing only the visible prose can leave rejected developments in private records. The user accepts that available commits may not isolate exactly one interaction. Do not silently claim a precise rollback when only a coarser checkpoint exists.

After restoration, the writer reports the result and any limits in the Director conversation, asks for further direction, and waits. It does not automatically write a replacement continuation. Retain the human's applicable corrections and preferences while awaiting that direction. A full branching history interface is still a possible later feature.

### Accepted trade-off: recovery follows the available checkpoints

The user accepts writer-chosen commit granularity as a limitation of this approach. A precise checkpoint before every interaction is not an approved requirement. There may be several commits within an interaction or a checkpoint covering more than one exchange. The writer must distinguish what Git actually records from what it can reconstruct through additional authoring; such reconstruction must not be described as an exact historical restore.

### Proposed smallest approach, not a formal design

Inspect the history for a suitable recorded checkpoint rather than blindly undoing the most recent commit. Restore the scope supported by that checkpoint and the Director's instruction, explaining any mismatch with the requested undo. Recording explicit interaction boundaries or stable Git references remains an optional improvement if later justified; it is not required to promise exact per-interaction restoration. The restoration method is unselected. Do not assume the earlier application's transaction machinery is needed.

Commit timing can remain the writer's choice while a hook checks a concrete condition at a suitable boundary, such as returning to the input wait or completing work. The hook event, condition, and blocking behavior need verification for the selected host. A commit's existence cannot establish that the notes are semantically complete or that the fiction is believable.

### Recovery concerns to resolve

- Preserve applicable human corrections and preferences across restoration. A Director message saying why a reply was rejected must not disappear merely because the story checkpoint predates it. How to preserve that message while restoring other files is open.
- Git restores recorded file contents, not the active agent's memory. The writer must treat the withdrawn continuation and its rejected plans as no longer authoritative, re-read restored materials, and continue under the retained human guidance. Whether a stronger clean-session resumption is needed remains a host-specific question.
- Account for changed files that have not yet been committed, newly created materials, and any relevant assets outside the recorded history. Keep credentials excluded. Do not claim Git automatically restores all workspace material regardless of tracking.
- Work associated with the rejected interaction must not keep writing over restored files. If subagents or helpers are still changing relevant files, the restoration needs a quiet boundary or supported control of that work. This does not require killing the entire host process.
- Preserve useful skill, helper, and interface improvements by default when undoing story developments. The Director can explicitly ask to undo those improvements too. Remove rejected story assumptions from retained materials wherever they occur; a skill's filename does not make story-specific content exempt. If the recorded commits do not cleanly separate the changes, explain that limitation and distinguish any reconstruction from an exact historical restore.

No Git repository, checkpoint helper, hooks, or Undo implementation has been created during this brainstorm. The user's discussion of automatic commits concerns the future writer workflow, not a request to commit these investigation notes now.

## Reopening and fresh-context continuation

Reopening should be simple because the story materials live in the directory. The working flow is to open that directory in a compatible agent, invoke the writer skill, and let it read its durable materials and reopen the browser helper as needed. Continuing an existing host transcript is welcome but not required.

The writer must leave enough discoverable records for a fresh session: characters, established/disclosed information, private plans and possibilities, preferences, applicable Director instructions, prose, and instructions for finding its working notes. It chooses how to organize these records. Do not require replaying the entire public conversation as the primary world model or saving private model reasoning.

This is a required outcome rather than a claim that every model will automatically keep adequate records. Evaluate continuation after context loss; concrete file/checkpoint hooks can support bookkeeping but cannot certify semantic completeness.

### Display agreement still to clarify

- Which files contain prose for the human, and which remain private working material, including temporary drafts.
- How to recognize new prose and authorized changes in the shared log so the agreed presentation works with different editing methods.
- How the interface reads changing files without assuming a specific editing tool, and handles temporary intermediate contents during a save.
- How it presents writing, waiting, interruption, and completion without prescribing the writer's private world records.

These are discussion points for a small shared-file agreement, not a new publication protocol or a formal specification.

## Reference investigation

The source investigation is recorded in [browser_handoff_research.md](../../research/browser_handoff_research.md), with revision-pinned primary-source links and a distinction between inspected behavior, user-reported experience, and host behavior still requiring verification.

Impeccable's decision-page implementation writes an answer file and supplies a terminal wait that reads it. Its Live feature instead uses local HTTP event delivery and documents host-specific waiting instructions. The inspected HyperFrames Studio path opens a browser, refreshes after file changes, and exposes browser selection to explicit CLI reads; that path does not establish automatic writer continuation. Neither project was run during this source investigation.

The decision page is part of Impeccable's shared workflow across supported agents. The published Claude Code, Gemini CLI, and shared-agent references all include it. The user reports successful use in Claude Code and Codex. Basic browser-input handoff has an established precedent; further verification should focus on the story loop's added requirements and the particular hooks and session behavior we rely on.

MightHappen's imagery documents and selected cast-panel reference have now been inspected read-only at the user's request. See [prior_imagery_findings.md](../../research/prior_imagery_findings.md). The earlier choice was to reuse source PNGs in a writer-controlled cast panel beside continuous prose. The reference was for placement; later Serial fiction styling and old application protocols are not automatically selected here. The prior implementation status reports a bootstrap rather than a completed playable UI.

Read-only host observations and official documentation findings are in [host_compatibility_notes.md](../../research/host_compatibility_notes.md). Installed CLIs report Codex 0.165.0 and Claude Code 2.1.300. Codex reports hooks and unified execution enabled. Claude documents both ordinary background work and a native Monitor option with availability/lifetime limits. Both document concrete hook control; Codex requires review of new/changed non-managed hook definitions. These are evidence about available primitives, not a tested story loop or a compatibility certification.

The expanded host shortlist has initial OpenRouter evidence: OpenCode and Pi document native support, Hermes documents OpenRouter model configuration, and OpenRouter documents a launcher route for DeepSeek Harness and other hosts. Details and source links are in the host notes. No provider configuration or model call was performed, and no winner has been selected.

The user requested a further pre-review comparison against the previous project's product decisions. [carryover_audit.md](../../research/carryover_audit.md) records the read-only findings and the user's subsequent acceptance of the six product behaviors: constructive Director discussion without automatic story advancement; clarification of incompatible card/world premises; author-oriented card interpretation; reading prose for voice/pacing; applying preferences through writer-managed methods; and work/failure discussion through Director chat and existing host diagnostics. The audit also identifies deliberate changes, including the shared story log and checkpoint-limited Undo, so they are not silently reversed.

## Discussion route and checkpoints

1. Clarify the smallest end-to-end demonstration, including acceptable agent-side setup and interruptions; identify the user's available hosts.
2. Investigate those hosts and the relevant HyperFrames mechanism using primary sources and narrowly scoped, authorized observations. Separate documented support, observed behavior, inference, and unknowns.
3. Discuss waiting and session lifecycle, the minimum shared-file agreement, initial output cadence, and the first image workflow. Keep the choices conversational rather than resolving everything at once.
4. Clarify persistence, latest-interaction correction, card import, and which requirements the short demonstration must exercise versus the later mystery arc.
5. Update the anchored hypothesis, alternatives, and accepted trade-offs. Ask the user explicitly whether it is ready for Goldfish review.
6. Only after readiness approval, run fresh-context Goldfish reviews across the required lenses and write docs/planning/concepts_brief.md. Review findings with the user and revise as needed.
7. Obtain final brief alignment and complete the EGM handoff checkpoint. The user's intended next stage is egm-draft in a fresh session; do not begin formal design or implementation during this brainstorm.

## Current discussion

The ordinary workflow is confirmed. Exceptional interruptions remain open; the user's confirmation does not imply unlimited unattended session operation.

The host-experience question is answered: Claude Code and Codex. Impeccable's wider support is documented in the research note.

Accepted display direction: normal file saves with browser-side reveal of new prose; the writer is aware of the behavior. Established prose is preserved unless the Director authorizes a revision. Authorized edits can update directly, with a change indicator if inexpensive.

Working public-file proposal: one shared story conversation log for both human input and writer prose, with a likely separate Director conversation log. This supplements private world notes rather than replacing them.

Current interaction direction: the prose-production block covers player actions as well as Director submissions, under writer control. Browser reveal animation is separate. Stop is deferred. Undo is a Director action, using Git history with writer-chosen commit times and hook-supported checkpoint enforcement. The user accepts that undo precision follows the available commits; the writer must disclose limitations.

Post-undo behavior is settled: ask for direction in the Director conversation and wait before producing more story prose. Do not automatically regenerate the rejected response.

The first demonstration's image source and placement are settled: supplied character-card PNGs in a cast panel, with generated story imagery deferred. Initial adaptable generation guidance remains a package goal. Accept/Revise is removed. A fresh actual Impeccable comp-led design pass is scheduled after the demonstration has a concrete brief; installed skill and key presence have been checked.

The first demonstration scope is accepted. Claude Code and Codex are required support targets; the additional candidates and OpenRouter requirement are recorded. A host Stop hook cannot be assumed to run after each story exchange inside an ongoing tool-wait loop, and writer-edited hooks may need activation/trust handling.

Restart direction is settled: reopen the workspace with a compatible agent, recover important knowledge from its files, and reopen the interface as needed. Saved host context is optional.

## Anchored hypothesis for readiness review

Package a portable fiction workspace operated by an existing agent, with skills, supported hooks, readable records, an editable browser template, and only the local file-access/waiting helpers needed for play. Use a shared story conversation log and a distinct Director conversation, saved prose with browser-side reveal, and supplied card portraits in a cast panel; the writer manages its own private methods and Git checkpoints, explains Undo limits, and waits for Director guidance after restoration.

Support Claude Code and Codex and provide an existing-host route to user-selected OpenRouter models, comparing the additional host candidates rather than building a provider controller. A fresh compatible session must continue from durable workspace knowledge without needing saved chat context. Start with the accepted short-scene demonstration; keep Stop and generated story imagery deferred, retain the scheduled comp-led Impeccable exploration, and reserve the complete mystery arc for a later demonstration.

The user has now accepted the carry-over behaviors recorded in docs/research/carryover_audit.md. They refine the anchored hypothesis without adding an application controller: constructive Director discussion and imports, clarification of genuine starting conflicts, author-oriented card interpretation, literary use of prior prose, adaptable preference handling, and work/failure discussion through Director chat. The scheduled actual Impeccable comp-led pass remains outstanding.

Readiness for Goldfish review is explicitly confirmed by the user's instruction to review now. This is not an approved concept brief. Host/model execution behavior and the minimum shared-file details remain explicit review questions. Review execution and results will be recorded in the review report; no formal design or application files have been created.

## Goldfish review completed

All six fresh-context BRAINSTORM reviewers completed through the synthesizer, in three concurrent pairs under the session's four-slot limit. No retries or delegation failures occurred. The root read all six raw reports and checked the reviewed inputs. Reported read receipts and context-isolation limits are recorded without claiming access to hidden child tool traces.

- [concepts_brief.md](concepts_brief.md): reviewed working brief in the required EGM format, awaiting discussion and approval.
- [goldfish_review_report.md](../../reviews/goldfish_review_report.md): six statuses, receipts, deduplicated findings, counterarguments, and unresolved alternatives.
- goldfish_reviews (`goldfish_reviews`, kept locally, not published): each reviewer's original report; inputs/brainstorming_notes.md preserves the reviewed primary input before these live-note updates.

No reviewer found a concept-level blocker. The synthesis groups overlapping findings into nine Major concerns and two Nits; these are risks and proposals, not demonstrated implementation defects or newly accepted requirements. The main clusters are shared-log input preservation and instruction timing; coherent coarse Undo across retained Director guidance and pending/running work; and honest host waiting, checkpoint activation, and fresh-context continuation claims.

The user's first post-review resolution extends the prose-writing submission block to player actions, using the same writer-controlled arrangement as Director messages. That resolves ordinary additional submissions during the blocked prose phase, without selecting a universal queue policy or restricting all editing tools. Safe saves, already-submitted inputs, and interrupted/stale blocking signals remain implementation concerns. No public schema, checkpoint-per-response rule, controller, or formal implementation plan was selected by review. The actual comp-led Impeccable exploration remains outstanding.

## Post-review decisions

- 2026-11-03: During prose-response production, the writer can disable player-action submissions as well as Director submissions. Both use the same writer-controlled blocking arrangement. It is the actual writing phase, not subsequent browser animation. This is not an automatic lock during private note-taking or method work.
- 2026-11-03: Undo preserves useful skills and interface improvements by default. The human can include them explicitly in the requested Undo scope. This refines recovery without requiring wholesale workspace rollback or pretending the available history can always separate changes exactly.

Default restoration scope is now settled: withdraw the unwanted story development and associated fictional assumptions while retaining useful method/interface improvements unless the Director requests otherwise. Exact restore mechanics and compatibility of retained improvements with restored files remain later design questions. Further review refinement and the actual comp-led Impeccable exploration remain outstanding.


## Readiness and actual visual exploration

- 2026-11-03: The user's readiness question was assessed against the completed Goldfish review and the two subsequent resolutions. There is no concept-level blocker; detailed input coordination, checkpoint mechanics, recovery assistance, and host observations should remain visible in formal design rather than expanding this brainstorm indefinitely. The final brief still needs user alignment.
- The previously requested actual Impeccable comp-led pass has now started. PRODUCT.md records already-confirmed product truth. docs/designs/impeccable_direction_notes.md records seven candidates, the valid procedural draw, and challenger assessments. The local direction page uses .impeccable/direction-round-1.json; mockups and exact prompt provenance live under .impeccable/mocks/decision/. No application code, formal EGM design, or visual approval follows from opening that page.
- The intended handoff remains egm-draft in a fresh session after alignment. Visual selection is pending and must not be invented from silence.

- Actual Impeccable direction round: five inspected comps now exist with prompt provenance. The browser page offers the recorded candidates and user steering. Selection is pending; no image or direction is approved and no application implementation has begun. See docs/designs/impeccable_direction_notes.md.


## Visual direction selected ? 2026-11-03

The user selected Woven anthology on the actual Impeccable decision page. The retrieved answer is optionId woven, comp-led unchanged, with no steer. The selected reference is .impeccable/mocks/decision/woven.png; direction approval and the original answer are saved with the Impeccable artifacts. docs/planning/concepts_brief.md and PRODUCT.md now carry this choice. Earlier pending/scheduled statements above are historical. This choice completes the brainstorm direction round, not formal design or implementation. Final concept-brief alignment and the intended fresh-session EGM draft handoff remain.


## Fresh-session draft handoff - 2026-11-03

The user requested the handoff prompt for egm-draft in a fresh session. docs/planning/egm_draft_handoff.md preserves the agreed starting scope, selected image, reading order, open design/evidence questions, and EGM section gates. The concept brief now records this requested transition; no formal draft or application implementation was started here.

The user also authorized updating the existing global Impeccable copy. The official updater completed `npx --yes impeccable@4.8.0 update --global --no-hooks --yes`, reporting one skill updated to 4.8.0 and engine 0.1.18 installed. Both the installed skill header and launcher --version were checked and report 4.8.0. Hook manifests were excluded from the update. A pre-update backup is at `a local backup: impeccable-before-4.8.0-20261103-171936/impeccable-4.5.2.zip`, with a copy of the prior skill lock alongside it. The selected mockup and original direction-round provenance remain from Impeccable 4.5.2; no reroll or regeneration accompanied the update.


## Impeccable hook update - 2026-11-03

The user explicitly authorized updating hooks as well. Reran the official `npx --yes impeccable@4.8.0 update --global --yes`; it completed successfully and reported hooks installed. The skill remains global, while the updater created project `.codex/hooks.json` with PostToolUse and Stop entries pointing to the global Impeccable launcher, including commandWindows paths. Parsed the manifest and verified its Windows launcher exists. Impeccable hooks status reports enabled. Native Codex trust/activation remains separate; the fresh session may need `/hooks` approval. This does not install or validate the future story writer's bookkeeping hooks.

A read-only Impeccable doctor check found no hook-wiring deficiency; it mentioned the absent general buildPath default. No general default was added: the user's existing comp-led direction choice remains recorded, and unrelated project configuration was not changed. The handoff now reflects the subsequent hook update, superseding the earlier no-hooks state.
