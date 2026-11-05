# CouldHappen: a portable fiction workspace for existing agents

* **Author:** Synere
* **Status:** Approved 2026-11-04; implemented; current. Changes since approval are folded into the text below; their rationale is in the [ADRs](../decisions/README.md) and the [progress log](../history/progress-log.md).
* **Date:** 2026-11-03 (Asia/Manila)
* **Last updated:** 2026-11-05 (Asia/Manila)
* **Starting scope:** [concepts_brief.md](../history/planning/concepts_brief.md), with the later resolutions in [brainstorming_notes.md](../history/planning/brainstorming_notes.md).

Drafting approvals (2026-11-03 to 2026-11-04) are recorded in the [history](../history/README.md).

## Overview

CouldHappen is an experiment in what a modern general-purpose coding agent can contribute to interactive fiction and AI roleplaying when given freedom and responsibility to develop its own creative practice as an author/game master.

CouldHappen packages a portable story directory that an existing agent can operate as an author and game master. The human opens that directory in a supported host, asks the writer to launch the supplied editable browser interface, and participates in the story. Human actions and prose contributions share a readable story conversation with the writer's prose. A separate Director conversation supports discussion, preferences, imports, revision requests, and Undo.

The writer portrays the cast, develops consequences, and maintains durable knowledge of the world. It can change its working methods and private records, provided a fresh compatible session can find and use the knowledge needed to continue. The host supplies the execution loop, tools, model/account, permissions, and session behavior. The package supplies skills, supported hooks, templates, and small helpers for local browser/file access and waiting. The workspace session operates the directory; invoking a skill does not create another agent runtime.

The browser presents saved writing and records human input. It animates new prose after normal saves, independently of the writer's actual composition work. The selected visual reference is [Woven anthology](woven/woven.png): a petrol/teal shell, saffron accents, a pale cool reading surface, serif prose, clear sans controls, restrained interlaced rules, Story/Director navigation, an action composer, and a right-hand cast panel. Its scene, portraits, and biographies are illustrative. Supplied character-card portraits do not need to be restyled.

The first demonstration is one short scene from a human world prompt and imported cards, with supplied PNG portraits, several browser exchanges, a Director exchange, an in-scene fresh-session handoff, and honest Git-supported Undo followed by waiting for direction. Claude Code and Codex are required support targets. The selected validation order starts with Codex interactive CLI, then Claude Code interactive CLI; Pi's native OpenRouter route is the selected additional reference configuration for human-selected underlying models. These choices identify configurations to demonstrate. The common writer skill remains harness-agnostic and guides the agent to establish its capabilities and determine the concrete means of carrying out the shared workflow.

## The Problem

A continuing interactive story needs more than the current conversation window. Characters, established events, disclosed claims, private plans, possibilities, and human preferences can outlive a session. If those distinctions live only in the active context, a restart can lose continuity or turn a discarded possibility into an established fact. A transcript helps recover prose and voice, but making the entire growing conversation the primary world record leaves the writer dependent on repeated reconstruction.

The human also needs two understandable ways to participate: contributing within the story and discussing it with the writer as Director. A hypothetical Director discussion must not become a fictional event merely because it was mentioned. An unwanted continuation needs a usable recovery path that accounts for its associated assumptions, while keeping applicable human corrections and useful improvements to the writer's methods.

An application-owned controller could take responsibility for model calls, scheduling, storage, and recovery. That would also duplicate responsibilities already supplied by the existing host. CouldHappen aims to support the retained browser experience through a small directory-based package while leaving creative decisions and session execution with the writer and host.

That smaller boundary still has to work. Shared files can lose overlapping edits or cause old input to be processed again. A reachable browser helper does not prove that the writer is servicing input. Git can restore recorded contents without clearing rejected assumptions from a live context or stopping delegated work. The design must explain the limits of the supported workflow and handle its ordinary cases without spreading a replacement controller across many scripts and hooks.

The available investigations establish source-inspected handoff precedents and user-reported browser interaction in existing agents. They do not demonstrate this package's repeated story loop, waiting overhead, checkpoint enforcement, coherent Undo, OpenRouter pairing, or fresh-context continuation. Those are outcomes to establish before claiming support.

## Goals

1. **Sustain browser play through an existing writer session.** The human can launch the browser from the story workspace, submit an action or prose contribution, read the resulting continuation, and repeat. Human story inputs and writer prose remain in the same readable conversation; Director discussion has a separate log. The supported saving and input-recognition agreement must preserve submissions and distinguish new human input from writer output and revisions. Waiting should happen locally where the host permits it, with actual renewal overhead and interruption limits made clear.

2. **Support believable authorship and meaningful human influence.** One author/game master can portray the whole cast across different worlds and genres. Player contributions can affect what happens and lead to believable consequences. The writer distinguishes established events, disclosed claims, private plans, and possibilities without a prescribed private schema. Hidden explanations may change when the continuation remains consistent with established and disclosed material. Neither an original private plan nor a player's theory automatically settles the truth. The demonstration must be assessed through the resulting fiction as well as the saved records.

3. **Keep Director discussion constructive and distinct from fiction.** The human can discuss ideas, give natural-language preferences, and direct changes. Ordinary discussion may influence later writing and working methods without automatically advancing fictional time, rewriting established prose, or establishing hypotheticals as events. Explicit instructions may authorize continuation or revision. Applicable preferences and corrections must inform later work, including after a restart or method change. Work explanations and recoverable failures belong in Director discussion, supported by existing host diagnostics.

4. **Continue from durable, discoverable workspace knowledge.** After context loss or a fresh compatible session, the writer can find its current records, relevant previous prose, character knowledge, established/disclosed material, private possibilities, preferences, and retained Director guidance. The writer can reorganize those materials and edit its methods while preserving that discoverability. Observe an actual fresh-context continuation without relying on saved host chat, and check its prose against prior disclosures and applicable human guidance. Files and commits alone do not prove adequate continuity.

5. **Use imported character cards without surrendering authorship.** The Director can import SillyTavern PNG and JSON cards, including during play. Preserve original source material and supplied portraits. Cards establish initial identity by default, while allowing later development and optional stricter adherence. Adapt compatible details autonomously; ask the Director to resolve genuine conflicts with an explicit world premise and retain that resolution. Greetings, examples, scenarios, and roleplay instructions are source material rather than automatic events or higher-priority writer instructions. Import alone must not reveal a character in the public cast.

6. **Provide a readable, editable presentation in the selected direction.** Keep prose central, with distinct Story and Director views and a cast panel using supplied card portraits. Let the writer save normally and the browser animate new prose. Established prose changes require Director authorization, including the standing error-repair permission added on 2026-11-04 below; authorized revisions may appear directly, with a changed-passage indicator if inexpensive. Support the writer's chosen prose-production block across both player-action and Director submissions. Private note or method work does not automatically block input, and reveal animation is separate from composition. Carry Woven anthology into later interface design without treating its illustrative content or every depicted control as an additional feature requirement.

7. **Make writer-chosen Git checkpoints useful and accurately described.** Include prose and relevant story materials in history. Let the writer choose meaningful commit timing, supported by concrete checkpoint checks through reachable, activated host hooks where supported. Establish what those checks actually enforce and when. Do not infer semantic completeness from a clean tree, an existing file, or a commit. The selected policy checks the concrete Git condition at deliberate closure and active supported host completion; actual enforcement remains to be demonstrated.

8. **Recover from unwanted developments without silently resuming them.** Undo is a Director request constrained by available Git checkpoints. Explain which requested changes history can restore, any coarser scope, and any reconstruction needed. Withdraw the unwanted story development and associated fictional assumptions while retaining applicable human corrections/preferences and useful skill/interface improvements by default. The Director may include those improvements in the requested Undo scope. Retained methods must not continue treating rejected fiction as authority. Account for pending inputs, browser/helper state, live context, and delegated work before claiming recovery. After restoration, ask for Director direction and wait; old pending input must not automatically resume the rejected continuation.

9. **Establish support through observed host configurations.** Support Claude Code and Codex and at least one suitable existing-host OpenRouter route with human-selected underlying models. Distinguish documented capabilities from observed behavior on the actual surface/version and model pairing, including wait handling, hook activation, and fresh-session behavior. Pi's native OpenRouter route is the selected additional reference; OpenCode, Hermes, and DeepSeek Harness remain comparison candidates. Model choice does not imply equal reliability across the entire OpenRouter catalog.

10. **Keep the package small and adaptable.** Reuse the host's execution and permissions, and keep credentials in normal host/user configuration outside story records and source control. Establish only the public agreements needed for input, display, cast assets, work state, and convention changes; leave private world records and authoring methods flexible. Retain initial adaptable guidance for future image tools supplied by a host or user, without requiring a provider integration or runtime image generation for the first scene. Host-supported delegation remains optional.

## Non-Goals

* **A new agent or provider runtime.** Do not add a workspace-owned model controller, SDK execution service, gateway, direct browser-to-model calls, or another orchestrator in place of the existing host. Local file access and waiting helpers remain allowed within the agreed boundary.
* **A prescribed private world database or reasoning archive.** No fixed private schema, transcript-as-world model, saved private model reasoning, or required preference-injection framework. Durable outcomes and discoverability are required; private storage and methods remain the writer's choice.
* **Exact recovery after every interaction.** No required per-response commits, exact selective recovery from every mixed checkpoint, blanket workspace reset, or claim that Git removes material from live context or covers untracked/external assets automatically. Undo does not automatically generate replacement prose.
* **A publication-acceptance or cancellation system.** No Accept/Revise controls or pending/accepted publication workflow. Browser Stop is deferred. Browser reveal is not raw model-token streaming and does not require character-by-character disk writes.
* **All later creative demonstrations at once.** Runtime story image generation, a complete mystery arc, and a full branching-history interface are deferred. The initial scene uses supplied card PNGs. Future image-tool guidance remains in scope.
* **Universal host/model behavior or unattended lifetime guarantees.** No promise of identical hooks across surfaces, automatic activation of edited hooks, idle wake-up after the host stops servicing results, indefinite operation, negligible renewal cost, or universal model compliance.
* **An infrastructure platform around the story directory.** No default container, sandbox service, elaborate permission layer, custom activity dashboard, automatic updater, general migration engine, general native-tool registration system, or mandatory multi-agent writing arrangement is part of the starting scope.
* **Adoption of the earlier project's architecture or visual theme.** MightHappen is optional read-only history. Its controller, publication protocol, SQLite schema, transaction machinery, credentials, framework, pinned host, implementation sequence, and styling do not carry over. The selected Woven image remains the current visual reference.

## Critical User Journeys (CUJs)

### Set up and sustain browser play

* **Given:** The human has opened this portable workspace with a compatible existing agent and loaded its writer guidance.
* **When:** The human asks it to set up, then submits story contributions through the browser.
* **Then:** The agent establishes actual capabilities, prepares the local services, reads saved human entries, writes believable continuations and durable records, and resumes a serviced local input wait. Save receipts remain distinct from handling an instruction.

### Discuss and import through Director

* **Given:** The scene is available and submissions are permitted.
* **When:** The human discusses a preference, asks a question, or imports PNG/JSON character source material.
* **Then:** The writer responds constructively without automatically advancing fiction, retains applicable guidance/source material, asks about genuine starting conflicts, and controls public cast disclosure.

### Coordinate edits and recover an interruption

* **Given:** Browser and writer share the conversations.
* **When:** The writer needs a direct edit or must reopen interrupted work.
* **Then:** The helper's acknowledged pause preserves accepted submissions; the writer rereads before editing and validates before release. Reopening first establishes that former writing stopped and reconciles actual files, rather than clearing an old block on a timer.

### Undo and wait for new direction

* **Given:** The Director rejects a development and available history has been inspected.
* **When:** The writer restores or reconstructs the supported scope.
* **Then:** It withdraws associated assumptions, preserves applicable guidance and useful improvements by default, explains real limits, reconciles consumers/pending input, asks a new Director question, and waits. Old pending input cannot restart the rejected continuation.

### Continue with a fresh context

* **Given:** Several scene exchanges and applicable Director guidance have been saved, and the former writer/delegates have stopped.
* **When:** A genuinely fresh compatible session reenters without the old host transcript or a test-only recap.
* **Then:** It discovers the current records, reconciles work state, and produces fiction consistent with established/disclosed material and applicable preferences. Evaluate the resulting writing as well as the saved files.

## Technical Plan (Architecture)

The author approved this Technical Plan on 2026-11-04. It combines the author's architecture choices into one workflow; the implementation status is in [implementation progress](../implementation-progress.md). The supporting [technical decision record](../history/planning/technical_plan_decisions.md) preserves the discussions, comparisons, research, and source links.

### Selected architecture and ownership

The existing host runs the writer. A small Python loopback HTTP helper connects saved workspace files to a client-side Svelte interface served by Vite. The browser periodically reads public snapshots and submits human messages through that helper. The writer reads and edits the same files with its ordinary tools, using an acknowledged pause before editing either shared conversation.

```text
Human <-> Svelte browser <-> Vite (frontend and local API proxy)
                                      |
                                      v
                             Python file helper
                              |              |
                       public snapshots   human log saves
                              |              |
                              +------+-------+
                                     |
                          Story / Director Markdown,
                           public cast and work state
                                     ^
                                     | ordinary file tools;
                                     | acknowledged edit pause
                           Writer in existing host
                            |        |         |
                        local wait   |    Git checkpoints
                              private knowledge,
                              imports and methods
```

Vite supplies the live interface and frontend HMR. Python supplies bounded file access, submission serialization, writer controls, and local input waiting. Neither component calls a model, owns the writer session, or decides the creative order of work. A helper process cannot wake a host that has stopped servicing its results.

| Decision | Selected behavior |
| --- | --- |
| T1 | Writer-controlled, acknowledged browser-write pauses around direct shared-log edits. |
| T2 | Writer interprets pending Story and Director inputs together. |
| T3 | Continue in the current session after Undo; remember the rejection without retaining its authority as fiction. |
| T4 | Pause and reopen affected components for incompatible public-convention changes. |
| T5–T6 | Markdown entries with stable identities, roles, boundaries, and human-input dispositions in entry metadata. |
| T7 | Checkpoint checks at deliberate closure and active supported host completion, without a per-response commit rule. |
| T8 | Observe a real fresh-context handoff within the first short scene. |
| T9–T10 | Validate Codex interactive CLI first, Claude Code interactive CLI second, and Pi's native OpenRouter route as the additional reference configuration. |
| T11–T12 | Editable Python scripts, including a small loopback HTTP file helper. |
| T13–T14 | Client-side Svelte with Vite and HMR; live Vite plus Python during ordinary play. |
| T15 | Periodic browser reads for saved-data updates. |

The writer owns authorship, world records, preferences, public disclosures, and meaningful Git checkpoints. The host owns model/provider configuration, execution, permissions, session continuation, and any delegation. Credentials stay in normal host/user configuration outside story records and source control.

### Capability-driven skill and reference integrations

The main skill and its capability-routing reference describe operations and required outcomes. They ask the agent to establish how its actual tools can accomplish them. They do not branch by harness brand, require a known-host writer adapter, or infer abilities from the selected model's recollection.

| Capability | What setup or validation must establish |
| --- | --- |
| Read and follow workspace guidance | The current session reads the public agreement and discoverable writer reentry instructions. Native skill discovery is optional. |
| Share and edit workspace files | Browser/helper and writer use the same directory; direct edits follow the acknowledged pause. |
| Execute helpers and Git | Commands or equivalent tools can launch/reuse the local services, obtain results, control pauses, and inspect actual history. |
| Receive input and continue | At least one serviced command wait, yielded command, or native monitor/event returns control to the active writer for several real exchanges. |
| Reenter from durable files | A fresh session can find current knowledge and continue without the previous host transcript. |
| Establish recovery boundaries | The writer can stop or account for work that might overwrite a restore, using normal host controls and human assistance where necessary. |

The agent inspects exposed tools, settings, local help, and current documentation as needed at setup/reentry or after environmental changes. It does not repeat capability research on every story exchange. Missing Python, Node/npm, or Git can be resolved through installation where ordinary permissions permit; verify the actual executable is available to the agent afterward.

A native completion hook adds a separate capability: a reachable, activated host event must execute the Git check and be able to request continuation when relevant work remains uncheckpointed. A passive notification or Markdown instruction alone cannot enforce that boundary. A harness without this capability may still support ordinary play with guidance-only checkpoint assurance. Reference integrations must demonstrate the stronger assurance they claim.

Concrete hook configurations, native extensions, provider setup, and observed version-specific behavior belong in separate setup/validation materials. The core skill stays capability-driven when tested on Codex, Claude Code, and Pi. The [decision record](../history/planning/technical_plan_decisions.md#impeccable-precedent-for-capability-driven-guidance) records the inspected Impeccable precedent and the limits of that analogy. This is guidance interpreted by the existing agent, not an executable capability router or replacement agent loop.

### Workspace materials and public agreement

The package adds instructions, templates, helper source, frontend source, dependency manifests/lockfiles, and reference setup/validation materials. The working layout below identifies architectural responsibilities; concrete files and commands are in [setup](../setup.md) and the [public contract](../public-contract.md).

| Material | Proposed placement and responsibility |
| --- | --- |
| Portable skill and references | A skill package describing setup, capability assessment, writing, persistence, imports, browser agreement, recovery, and future image-tool adaptation. Host examples stay separate from the common workflow. |
| Story and Director conversations | `public/story.md` and `public/director.md`, each the authoritative conversation for that channel. Story includes both human contributions and writer prose. |
| Public cast and portraits | `public/cast.json` and `public/assets/`, containing only information intentionally disclosed for display. No preapproved cast list is required. |
| Public work state | A small `public/work.json` describing the public-convention version and durable modes such as awaiting new Director direction after Undo. It contains no second per-input disposition ledger. |
| Durable writer reentry index | A stable entry point, provisionally `START_HERE.md`, pointing to the current world records, methods, relevant prose, preferences, and recovery instructions. Private record organization remains freeform. |
| Imports and private working material | Preserved original cards/portraits and writer-managed knowledge/methods outside the browser-served area. Import source is distinct from public disclosure. |
| Supplied editable source | Python helper scripts and an isolated frontend directory, provisionally `helpers/` and `web/`. Source and relevant manifests belong in Git. |
| Transient local runtime material | A Git-excluded runtime directory for process connection details and interrupted-control recovery. It is not a canonical inbox, world database, or source of per-input processing truth. |

The public agreement covers entry parsing, cast display, writer controls, snapshots, submission receipts, compatibility, and recovery modes. It does not prescribe private character/world schemas, a preference database, or the writer's reasoning.

Each Markdown entry needs a stable ID, an author role, explicit boundaries, and ordinary unescaped prose. Human entries additionally carry `pending`, `addressed`, or `deferred` metadata. Existing IDs remain stable through authorized revisions. Processing metadata changes preserve the original human message body and do not create new input or replay reveal animation. Exact delimiter syntax is in the [public contract](../public-contract.md); parser fixtures are in `tests/`.

A successful browser save creates a pending human entry. It does not establish that the writer has read or applied it. Addressed means the writer reports handling the submission; it does not expire an ongoing preference or prove successful compliance. Deferred entries remain discoverable but do not repeatedly wake the writer as new work.

Readers reject malformed boundaries, duplicate IDs, or incompatible conventions rather than interpreting them as new input. During an acknowledged direct-edit interval, the browser retains the last coherent conversation view and displays the current saving permission. Releasing the interval validates and refreshes the saved view. This is save coordination, with no separate publication-acceptance step.

### Python helper, browser access, and periodic reads

The supplied helper is ordinary editable Python source, initially favoring standard-library primitives. It provides a narrow interface:

| Operation | Responsibility |
| --- | --- |
| Read public snapshot/revision | Return valid public conversations, cast references, and known work/control state. An unchanged revision avoids resending/rerendering the whole conversation. |
| Submit a human entry | Validate the channel, request identity, current permission, and public compatibility; serialize the append; acknowledge only after the log save succeeds. |
| Pause/release shared-log writes | Give the writer the acknowledged edit interval described below. Browser submission calls cannot release it. |
| Report writer controls | Expose the writer's prose-production block and known maintenance/recovery state without inferring liveness. |
| Wait for input | Check canonical logs locally and return relevant pending human entries through an actually serviced host tool. |

Endpoint names and command payloads are bound in the [public contract](../public-contract.md). The interface stays small: no general workspace file browser, arbitrary command endpoint, model client, creative scheduler, or event-history service.

The browser polls for the current public revision/snapshot, initially using an adjustable interval of about one second while active. It applies changes by stable entry identity. Timer throttling and service interruptions can delay updates; actual submission permission is enforced by Python even if the display is stale. Returning to the page or reconnecting triggers a fresh read. Polls and unchanged local checks do not themselves require model calls.

Use the live Vite origin with a narrow API proxy to Python, keeping normal browser requests on one local origin. Both servers bind to loopback. Python serves only approved public data/assets and constrains resolved paths to those locations. The frontend root and Vite filesystem allowance must also exclude private story records and preserved source imports; Python's allowlist alone would not constrain a separate dev server. This follows the documented [Vite server filesystem controls](https://vite.dev/config/server-options.html#server-fs-allow), with concrete configuration to be checked against the versions selected later.

A browser submission carries a client-generated entry/request ID that is reused on an uncertain retry. The helper checks the canonical log: the same ID and body return the existing saved result; a conflicting reuse is rejected. This prevents ordinary retry duplicates without a separate input ledger. If the browser cannot determine whether a save succeeded, it keeps the draft and reuses the same request ID; the helper resolves an existing ID and body before it checks whether saving is open, so a retry of an already-saved entry returns the saved result even while saving is closed. A rejected or paused save also keeps the draft. Process crashes and filesystem failures still require inspection rather than an exactly-once processing claim.

A helper generation/compatibility value accompanies browser writes. Restart, recovery, or an incompatible public change invalidates stale requests; the browser rereads current state and preserves its unsaved draft rather than silently replaying it. This is a stale-write check, not a session supervisor.

### Shared-log edits, production blocks, and the ordinary loop

The helper serializes browser appends. The writer follows this direct-edit agreement:

1. Ask the helper to pause browser writes to both shared logs.
2. The helper stops accepting new appends, finishes already-accepted saves, and acknowledges the pause.
3. Reread both current logs after that acknowledgment. Account for any submission saved just before the pause.
4. Edit the shared logs with ordinary tools, retaining entry identities and original human bodies when changing processing metadata. Keep other writers/delegates from overlapping these edits.
5. Validate the resulting public records and release the pause. The helper refreshes the snapshot and permits submissions according to the remaining writer/recovery controls.

Disabling controls in the browser is only presentation. The helper's permission check and acknowledgment prevent the stale-copy overwrite race. The agreement remains cooperative: an unrelated tool that bypasses it can still corrupt or overwrite a log.

The writer separately chooses when to engage a prose-production block. It applies to both Story and Director submissions and can cover composition beyond the short file-edit interval. Private notes, method changes, or ordinary planning do not automatically engage it. Releasing the edit pause does not clear an independently active production block. Reveal animation is also independent; animated prose can continue after writing has finished.

An ordinary exchange is:

1. The human submits through Story or Director. The helper saves the entry and returns a persistence receipt.
2. The active writer's local wait returns through its host tool. The writer reads pending entries from both logs and relevant durable context.
3. The writer interprets those inputs together. There is no cross-log FIFO rule, one-outstanding-input rule, or automatic Director-priority scheduler. Explain consequential conflicts or deferrals.
4. Ordinary Director discussion receives a constructive response without automatically advancing fiction. Explicit direction may authorize advancement or revision. The writer chooses an appropriate continuation for Story input.
5. Save prose, update input dispositions under the edit agreement, and maintain durable knowledge. Public cast changes reflect intended disclosures.
6. Clear controls that no longer apply and leave a standing local wait running before the writer's turn ends.

Saving prose and updating dispositions are not one indivisible transaction. On interruption, inspect actual prose, metadata, and records before deciding what remains pending. A writer save, revision, cast update, or file timestamp alone is not a new human input.

The wait mechanism stays separate from browser polling. It can locally check files or use an actually available monitor/event mechanism. Yielded command sessions must keep being serviced. Tool deadlines may require renewals and model/tool cycles; record observed overhead and limits instead of promising free, indefinite waiting or idle wake-up after session completion.

Verifying a wait is not the same as keeping one. A standing wait starts before setup is reported complete and is renewed before every writer turn ends, including after Director-only replies; otherwise browser input stays unread until the player prompts the agent in its host. Where the host reports a background command's completion to the agent, a background `wait --timeout 0` is the preferred standing wait; it returns as soon as an entry is pending.

### Authoring, imports, private records, and helper repair

The writer portrays the whole cast and may create new characters freely. A card, portrait, or preexisting public cast entry is not required. A cast entry is a display reference created when disclosure is appropriate, not permission to invent a character.

#### Creative initiative

Take initiative in shaping a creative practice and working environment that serve this story and player. Use your available capabilities to develop useful methods and tools, respecting host permissions and Director preferences. Notice weaknesses and opportunities; reconsider your methods when experience warrants it, and retain useful discoveries across sessions. Simple methods are valid when they serve the work; improvements should earn their complexity. Natural milestones may offer opportunities for reflection, with no fixed schedule or requirement to create tools. Judge methods by their contribution to the fiction, player experience, and continuity. Honor established fiction, Director authority, meaningful player influence, recoverability, and the shared workspace agreement.

Place this principle near the beginning of the main writer skill so that resourceful initiative is part of its baseline role. The initial workspace is adaptable; the writer chooses methods for outcomes rather than following a prescribed creative architecture. [Creative practice examples](creative-practice-examples.md) are optional illustrations to consult when useful. They introduce no mandatory mechanic, tool, simulation, reflection report, or first-scene requirement.

An optional Director initializer may express preferences about experimentation, mechanics, or proactivity. Ordinary Director discussion already supports those preferences, so the initial package needs no dedicated initializer mechanism. Initiative applies without an initializer. Assessment should consider how the chosen approach serves fiction, player experience, and continuity; a simple effective method is a valid result.

Director imports accept SillyTavern PNG and JSON cards, including during play. Preserve original source and supplied portraits outside the public served area. Use cards as initial identity material, adapt compatible details, and ask about genuine conflicts with an explicit world premise. Greetings, examples, scenarios, and embedded roleplay instructions do not become established events or higher-priority writer instructions. Import alone does not reveal a character. `import-card` reports the preserved source path; public portrait preparation accepts that preserved file, its import folder, or the original card file once an identical import exists, always reads the preserved copy, and never imports implicitly.

The writer's durable records must distinguish established events, disclosed claims, private plans, and possibilities in whatever organization it finds useful. Maintain a discoverable reentry index when that organization changes. Preserve applicable Director corrections/preferences and enough current knowledge for a fresh session to continue. The old host transcript may help but cannot be required. Do not save private reasoning as a project requirement.

Writer-created skills/helpers can fail and be repaired. The supplied Python helper is also editable source in Git. Keep the file bridge small where practical and put independent mechanics in separate helpers as a complexity preference, not an immutable boundary. Additional helpers may use another appropriate language.

The author gives standing permission for proportionate corrections caused by identified technical/mechanical failures. A small understood error can be fixed quietly across code, mechanical results, dependent records, and affected prose, then play can continue. Judge significance by effects on play; a rounding bug can still have consequential fictional effects. Ordinary creative revisions remain Director-guided.

For larger failures, explain the actual correction/rollback and any reconstruction or uncertainty. Git may help restore tools or records; it does not guarantee an exact repair. If coherent consequences cannot be established, ask the Director. Withdrawing substantial story development requires recovery reconciliation and new direction before replacing it. Technical rollback alone need not behave like a Director-requested Undo.

### Interrupted work and reopening

A reachable page/helper proves availability of that component, not that the writer is reading input. Show concrete known conditions such as saved, paused, awaiting Director direction, or connection failure. Do not label a submission “applied” from a receipt or infer writer activity from a timer.

An interrupted writer may leave an edit pause or prose block active. Do not clear either merely because it is old. Reopening establishes that the former writer and relevant delegated work have stopped, inspects the latest logs and partial work, validates the public records, and reconciles pending dispositions before releasing controls. Use normal host controls and human assistance where needed to establish that boundary.

A restarted helper begins with submissions closed until the writer reestablishes safe ownership and current conventions. Persist enough local control information to diagnose an interrupted pause; helper restart must not automatically override it. If durable public records indicate post-Undo waiting, restart retains that meaning rather than treating all pending entries as fresh authorization.

The browser preserves unsent drafts for the life of the tab (session storage) through ordinary refresh/reconnect and frontend maintenance, scoped to the current workspace and channel; a new tab starts without them. Stored drafts are unsent text, not a second canonical conversation. After a generation or convention change, show the current state and require a deliberate submission rather than automatic replay.

### Director Undo

Undo is a writer-led recovery procedure using actual available history, normally in the same host session:

1. Read the Director request and inspect checkpoints, current changes, and the requested scope. Explain coarser restoration or reconstruction honestly. Do not describe an untracked/external asset as restored by Git without evidence.
2. Establish a quiet boundary: obtain the acknowledged browser-write pause and account for active writer/delegated work that could overwrite recovery. If necessary, use normal host controls with human assistance before proceeding.
3. Restore or reconstruct the requested fiction and associated assumptions. Retain applicable corrections/preferences and useful skill/interface improvements by default unless the Director includes them in scope. Inspect mixed files/commits rather than blindly resetting the entire directory.
4. Reconcile retained methods and private records so that rejected events, disclosures, and explanations are no longer current authority. Remembering the attempted approach as feedback remains useful.
5. Reconcile pending inputs and public conventions. Preserve human input and applicable guidance; mark old unresolved inputs as deferred where appropriate, retaining their original bodies. They cannot automatically resume the rejected continuation.
6. Refresh the helper/browser generation and valid view. Append a recovery explanation and a new Director question. Record a durable awaiting-direction mode identifying that question.
7. Release the edit pause so new Director messages can be saved. Wait for Director input following the recovery question; earlier pending entries do not satisfy this wait. Story continuation remains suspended until the writer has interpreted new direction that authorizes it.

Use the Director log's entry identity/order to identify new feedback after the recovery question; no global event journal is needed. The writer interprets the response rather than a helper attempting to classify its natural-language intent.

The current session rereads the restored records and treats the withdrawn attempt as rejected fiction. Its memory of that attempt can guide a different approach, but it cannot count as something the player's character experienced or learned. Use a fresh compatible session if needed/requested; a context restart neither repairs bad records nor stops an old writer by itself.

### Public changes and agent-managed setup

Routine public content changes—new prose, authorized revisions, cast additions, or portrait references—use the current agreement. They do not require a maintenance migration. Incompatible entry syntax, public fields, or helper/frontend interfaces require a deliberate pause and reopening of affected components. Update the agreement, validate any affected records, restart/reload what is necessary, and reject stale writes before resuming. No general migration framework is required.

The player should be able to ask the agent to “set up.” The agent reads the skill and project manifests, checks/installs prerequisites as permitted, installs frontend dependencies, and starts or reuses the Python helper and live Vite server. It verifies the intended workspace and actual service addresses, opens the playing interface, establishes ownership and a standing input wait, and checks available hook activation. Existing story material is preserved. A durable story runs in its own clean workspace created from the release ZIP, never in the development repository; [Distribution and story workspaces](distribution-and-workspaces.md) is the packaging contract.

[Setup](../setup.md) specifies reproducible dependency commands and supported versions. Python remains a project dependency, Node/npm supports Vite, and Git supports checkpoints. Instructions may name these concrete project requirements while remaining agnostic about the host tools used to install/run them.

Vite HMR supports frontend source edits without a separate production build on every change. It does not guarantee preservation of drafts, reading position, or all application state; implement that handling deliberately. Python source changes normally need a deliberate helper restart at the recovery/maintenance boundary. A static frontend build remains useful for validation/distribution, not the selected ordinary playing mode. Current [Vite HMR documentation](https://vite.dev/guide/features.html#hot-module-replacement) describes the live development mechanism.

### Checkpoints and host completion

The writer chooses meaningful checkpoints, including deliberate closure of a play stretch. An active supported host-completion hook runs a concrete Git-scope check and requests continuation when relevant changes remain uncheckpointed. The writer then reviews the changes, completes needed durable notes, and makes an appropriate checkpoint. A dirty-tree check can establish recorded changes, not the semantic completeness of the world record.

Checkpoint scope includes relevant conversations, world/method records, imported source/portraits, editable helper/frontend source, and dependency manifests. Exclude process state, caches, dependencies, generated local runtime files, and credentials. Check the actual repository scope and staged/current contents; do not sweep unrelated files into commits.

The policy does not force a commit after every browser exchange or at a timer interval. A host turn may contain several exchanges while a local wait remains active. Reference validation must exercise the actual completion boundary during waits/monitors and distinguish real completion from temporary waiting. Hook trust, reachability, and activation must be observed after setup or edits; writing a config file alone does not establish enforcement. Hooks act only while play is armed (`writer claim` or `recover` arms it; `writer close` disarms it, recorded as `armed` in the private control state). `python -m helpers checkpoint check` reports `clean`, `dirty`, or `error` for the configured scope, and `checkpoint inspect --ref <commit>` lists what a commit recorded; see [setup](../setup.md) and [host integrations](../reference-hosts.md) for activation and per-host status.

Forced termination, crash, unsupported boundaries, or inactive/untrusted hooks can bypass the check. Document reduced assurance where appropriate. The supplied host examples and actual tested versions must establish how Codex CLI, Claude Code CLI, and Pi provide the required behavior. Existing design-visualization hooks are separate and are not evidence of story checkpoint enforcement.

### Presentation and validation boundary

Carry the selected [Woven anthology](woven/woven.png) into later interface work: prose-centered reading, distinct Story/Director views, a composer, and cast access. Preserve supplied card portrait treatment. Cover narrow screens, keyboard/focus use, reduced motion, readable contrast, stable reading position, unsent drafts, rejected/uncertain saves, interrupted controls, and recovery waiting. No mockup regeneration or runtime image generation is required for the first scene.

New saved writer entries may animate; existing-ID authorized revisions update directly, optionally with an inexpensive changed-passage indicator. Do not replay all prose after every poll, refresh, metadata update, or Undo. Respect readers who have scrolled away from the latest entry. Reveal state does not determine submission permission.

No compatibility or performance claim is established by the design alone. The implementation must demonstrate:

| Observation | Required evidence |
| --- | --- |
| Ordinary play | Several real browser exchanges in the same active writer session, including Director discussion that does not automatically advance fiction. |
| Save coordination | An accepted in-flight submission survives an edit pause; stale writes and uncertain retries do not silently duplicate or lose input. |
| Interrupted work | Pauses/partial work survive interruption honestly; reopening requires establishing a safe boundary and does not blindly replay pending input. |
| Undo | Actual available checkpoint scope, retained guidance/improvements, reconciled assumptions/pending input, and waiting for new Director direction. |
| Live frontend work | HMR, refresh/reconnect, drafts, reading position, stable entry identities, and recovery views work without a build per ordinary edit. |
| Checkpoint assurance | The actual trusted hook executes at the supported boundary and requests corrective continuation when needed; waiting does not accidentally impose per-response commits. |
| Fresh-context continuation | After several scene exchanges and applicable Director guidance, stop the old writer/delegates and start a genuinely fresh session. It uses only discoverable workspace material, without an old transcript or a special recap, and produces fiction consistent with prior disclosures and preferences. |
| Reference support | Record observed surface/version/model details for Codex CLI, then Claude Code CLI, plus Pi/OpenRouter; distinguish untested routes and renewal costs from observed results. |

The first creative demonstration remains one short scene using a human world prompt and supplied cards/PNG portraits. Evaluate the writing and continuity as well as the tools. Passing a parser test, creating files, or making a commit cannot establish that the writer did a good job of preserving the story.

## Alternatives and implementation plan

The alternatives the author considered (and why each was selected or rejected) and the ordered implementation plan used to build the first scope are preserved in [design alternatives and implementation plan](../history/design-alternatives-and-plan.md). The plan is complete; the text above describes the current design.

## Open Questions

* **Observation:** What has and has not been observed on real hosts is recorded only in [validation results](../validation-results.md); open next steps are in [implementation progress](../implementation-progress.md).
* **Independent review:** A fresh EGM design review of this document has not run. The [predecessor reconciliation](../history/planning/design_reconciliation.md) checked alignment with the brief and does not replace that review.

### Additional Resources

* [Creative practice examples](creative-practice-examples.md) — optional illustrations for the planned writer skill
* [Documentation index](../README.md) and [history](../history/README.md), including the original implementation handoff
* [Completed EGM drafting handoff](../history/planning/egm_draft_handoff.md)
* [Concept brief](../history/planning/concepts_brief.md) and [decision history](../history/planning/brainstorming_notes.md)
* [Technical decision record](../history/planning/technical_plan_decisions.md) and [final predecessor reconciliation](../history/planning/design_reconciliation.md)
* [Goldfish concept review](../reviews/goldfish_review_report.md) — risks and proposals, not runtime certification
* [Browser handoff research](../research/browser_handoff_research.md) and [host compatibility findings](../research/host_compatibility_notes.md)
* [Selected visual direction and provenance](impeccable_direction_notes.md), [selection record](woven/direction-selection.json), and [product context](../../PRODUCT.md)
* [Accepted creative carry-over](../research/carryover_audit.md) and [portrait findings](../research/prior_imagery_findings.md)

*Drafted with EGM*
