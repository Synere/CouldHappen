# CouldHappen: a portable fiction workspace for existing agents

> Archived approved draft. Current scope and implementation decisions are in the [approved design](../../designs/couldhappen.md); start a future implementation session with the [handoff](../implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](README.md).

* **Author:** Synere
* **Status:** Archived approved draft; the finalized design is authoritative.
* **Date:** 2026-11-03 (Asia/Manila)
* **Last updated:** 2026-11-04 (Asia/Manila)
* **Starting scope:** [concepts_brief.md](../planning/concepts_brief.md), with the later resolutions in [brainstorming_notes.md](../planning/brainstorming_notes.md).

The author confirmed intake and authorized drafting on 2026-11-03, then approved Overview, The Problem, Goals, and Non-Goals. The author approved the Technical Plan and then Alternatives Considered on 2026-11-04, authorizing the Detailed Implementation Plan. The author approved Detailed Implementation and requested final design reconciliation on 2026-11-04. All drafting sections are now approved. Remaining finalization steps and later validation obligations are listed under Open Questions. Application implementation has not begun.

## Overview

CouldHappen packages a portable story directory that an existing agent can operate as an author and game master. The human opens that directory in a supported host, asks the writer to launch the supplied editable browser interface, and participates in the story. Human actions and prose contributions share a readable story conversation with the writer's prose. A separate Director conversation supports discussion, preferences, imports, revision requests, and Undo.

The writer portrays the cast, develops consequences, and maintains durable knowledge of the world. It can change its working methods and private records, provided a fresh compatible session can find and use the knowledge needed to continue. The host supplies the execution loop, tools, model/account, permissions, and session behavior. The package supplies skills, supported hooks, templates, and small helpers for local browser/file access and waiting. The workspace session operates the directory; invoking a skill does not create another agent runtime.

The browser presents saved writing and records human input. It animates new prose after normal saves, independently of the writer's actual composition work. The selected visual reference is [Woven anthology](../../designs/woven/woven.png): a petrol/teal shell, saffron accents, a pale cool reading surface, serif prose, clear sans controls, restrained interlaced rules, Story/Director navigation, an action composer, and a right-hand cast panel. Its scene, portraits, and biographies are illustrative. Supplied character-card portraits do not need to be restyled.

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

## Technical Plan (Architecture)

The author approved this Technical Plan on 2026-11-04. It combines the author's architecture choices into one workflow; application implementation has not begun. The supporting [technical decision record](../planning/technical_plan_decisions.md) preserves the discussions, comparisons, research, and source links.

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

Concrete hook configurations, native extensions, provider setup, and observed version-specific behavior belong in separate setup/validation materials. The core skill stays capability-driven when tested on Codex, Claude Code, and Pi. The [decision record](../planning/technical_plan_decisions.md#impeccable-precedent-for-capability-driven-guidance) records the inspected Impeccable precedent and the limits of that analogy. This is guidance interpreted by the existing agent, not an executable capability router or replacement agent loop.

### Workspace materials and public agreement

The package adds instructions, templates, helper source, frontend source, dependency manifests/lockfiles, and reference setup/validation materials. The working layout below identifies architectural responsibilities; the later Detailed Implementation section will enumerate every concrete file and command.

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

Each Markdown entry needs a stable ID, an author role, explicit boundaries, and ordinary unescaped prose. Human entries additionally carry `pending`, `addressed`, or `deferred` metadata. Existing IDs remain stable through authorized revisions. Processing metadata changes preserve the original human message body and do not create new input or replay reveal animation. Exact delimiter syntax and parser fixtures belong in the detailed plan.

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

Endpoint names and command payloads will be bound in the detailed plan. The interface stays small: no general workspace file browser, arbitrary command endpoint, model client, creative scheduler, or event-history service.

The browser polls for the current public revision/snapshot, initially using an adjustable interval of about one second while active. It applies changes by stable entry identity. Timer throttling and service interruptions can delay updates; actual submission permission is enforced by Python even if the display is stale. Returning to the page or reconnecting triggers a fresh read. Polls and unchanged local checks do not themselves require model calls.

Use the live Vite origin with a narrow API proxy to Python, keeping normal browser requests on one local origin. Both servers bind to loopback. Python serves only approved public data/assets and constrains resolved paths to those locations. The frontend root and Vite filesystem allowance must also exclude private story records and preserved source imports; Python's allowlist alone would not constrain a separate dev server. This follows the documented [Vite server filesystem controls](https://vite.dev/config/server-options.html#server-fs-allow), with concrete configuration to be checked against the versions selected later.

A browser submission carries a client-generated entry/request ID that is reused on an uncertain retry. The helper checks the canonical log: the same ID and body return the existing saved result; a conflicting reuse is rejected. This prevents ordinary retry duplicates without a separate input ledger. If the browser cannot determine whether a save succeeded, it keeps the draft and resolves the existing ID before offering another submission. A rejected or paused save also keeps the draft. Process crashes and filesystem failures still require inspection rather than an exactly-once processing claim.

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
6. Clear controls that no longer apply and resume an appropriate local wait.

Saving prose and updating dispositions are not one indivisible transaction. On interruption, inspect actual prose, metadata, and records before deciding what remains pending. A writer save, revision, cast update, or file timestamp alone is not a new human input.

The wait mechanism stays separate from browser polling. It can locally check files or use an actually available monitor/event mechanism. Yielded command sessions must keep being serviced. Tool deadlines may require renewals and model/tool cycles; record observed overhead and limits instead of promising free, indefinite waiting or idle wake-up after session completion.

### Authoring, imports, private records, and helper repair

The writer portrays the whole cast and may create new characters freely. A card, portrait, or preexisting public cast entry is not required. A cast entry is a display reference created when disclosure is appropriate, not permission to invent a character.

Director imports accept SillyTavern PNG and JSON cards, including during play. Preserve original source and supplied portraits outside the public served area. Use cards as initial identity material, adapt compatible details, and ask about genuine conflicts with an explicit world premise. Greetings, examples, scenarios, and embedded roleplay instructions do not become established events or higher-priority writer instructions. Import alone does not reveal a character.

The writer's durable records must distinguish established events, disclosed claims, private plans, and possibilities in whatever organization it finds useful. Maintain a discoverable reentry index when that organization changes. Preserve applicable Director corrections/preferences and enough current knowledge for a fresh session to continue. The old host transcript may help but cannot be required. Do not save private reasoning as a project requirement.

Writer-created skills/helpers can fail and be repaired. The supplied Python helper is also editable source in Git. Keep the file bridge small where practical and put independent mechanics in separate helpers as a complexity preference, not an immutable boundary. Additional helpers may use another appropriate language.

The author gives standing permission for proportionate corrections caused by identified technical/mechanical failures. A small understood error can be fixed quietly across code, mechanical results, dependent records, and affected prose, then play can continue. Judge significance by effects on play; a rounding bug can still have consequential fictional effects. Ordinary creative revisions remain Director-guided.

For larger failures, explain the actual correction/rollback and any reconstruction or uncertainty. Git may help restore tools or records; it does not guarantee an exact repair. If coherent consequences cannot be established, ask the Director. Withdrawing substantial story development requires recovery reconciliation and new direction before replacing it. Technical rollback alone need not behave like a Director-requested Undo.

### Interrupted work and reopening

A reachable page/helper proves availability of that component, not that the writer is reading input. Show concrete known conditions such as saved, paused, awaiting Director direction, or connection failure. Do not label a submission “applied” from a receipt or infer writer activity from a timer.

An interrupted writer may leave an edit pause or prose block active. Do not clear either merely because it is old. Reopening establishes that the former writer and relevant delegated work have stopped, inspects the latest logs and partial work, validates the public records, and reconciles pending dispositions before releasing controls. Use normal host controls and human assistance where needed to establish that boundary.

A restarted helper begins with submissions closed until the writer reestablishes safe ownership and current conventions. Persist enough local control information to diagnose an interrupted pause; helper restart must not automatically override it. If durable public records indicate post-Undo waiting, restart retains that meaning rather than treating all pending entries as fresh authorization.

The browser preserves unsent drafts through ordinary refresh/reconnect and frontend maintenance, scoped to the current workspace and channel. Stored drafts are unsent text, not a second canonical conversation. After a generation or convention change, show the current state and require a deliberate submission rather than automatic replay.

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

The player should be able to ask the agent to “set up.” The agent reads the skill and project manifests, checks/installs prerequisites as permitted, installs frontend dependencies, and starts or reuses the Python helper and live Vite server. It verifies the intended workspace and actual service addresses, opens the playing interface, establishes ownership/input waiting, and checks available hook activation. Existing story material is preserved.

The later implementation plan will specify reproducible dependency commands and supported versions. Python remains a project dependency, Node/npm supports Vite, and Git supports checkpoints. Instructions may name these concrete project requirements while remaining agnostic about the host tools used to install/run them.

Vite HMR supports frontend source edits without a separate production build on every change. It does not guarantee preservation of drafts, reading position, or all application state; implement that handling deliberately. Python source changes normally need a deliberate helper restart at the recovery/maintenance boundary. A static frontend build remains useful for validation/distribution, not the selected ordinary playing mode. Current [Vite HMR documentation](https://vite.dev/guide/features.html#hot-module-replacement) describes the live development mechanism.

### Checkpoints and host completion

The writer chooses meaningful checkpoints, including deliberate closure of a play stretch. An active supported host-completion hook runs a concrete Git-scope check and requests continuation when relevant changes remain uncheckpointed. The writer then reviews the changes, completes needed durable notes, and makes an appropriate checkpoint. A dirty-tree check can establish recorded changes, not the semantic completeness of the world record.

Checkpoint scope includes relevant conversations, world/method records, imported source/portraits, editable helper/frontend source, and dependency manifests. Exclude process state, caches, dependencies, generated local runtime files, and credentials. Check the actual repository scope and staged/current contents; do not sweep unrelated files into commits.

The policy does not force a commit after every browser exchange or at a timer interval. A host turn may contain several exchanges while a local wait remains active. Reference validation must exercise the actual completion boundary during waits/monitors and distinguish real completion from temporary waiting. Hook trust, reachability, and activation must be observed after setup or edits; writing a config file alone does not establish enforcement.

Forced termination, crash, unsupported boundaries, or inactive/untrusted hooks can bypass the check. Document reduced assurance where appropriate. The supplied host examples and actual tested versions must establish how Codex CLI, Claude Code CLI, and Pi provide the required behavior. Existing design-visualization hooks are separate and are not evidence of story checkpoint enforcement.

### Presentation and validation boundary

Carry the selected [Woven anthology](../../designs/woven/woven.png) into later interface work: prose-centered reading, distinct Story/Director views, a composer, and cast access. Preserve supplied card portrait treatment. Cover narrow screens, keyboard/focus use, reduced motion, readable contrast, stable reading position, unsent drafts, rejected/uncertain saves, interrupted controls, and recovery waiting. No mockup regeneration or runtime image generation is required for the first scene.

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

## Alternatives Considered

This section draws on [Alternatives Weighed in the concepts brief](../planning/concepts_brief.md#alternatives-weighed), the [brainstorming notes](../planning/brainstorming_notes.md#alternatives-to-compare-not-decisions-already-made), and the author's subsequent [T1–T15 decisions](../planning/technical_plan_decisions.md). The author approved the consolidated Technical Plan on 2026-11-04.

“Rejected by author” below means rejected for the stated role in this initial design, not a claim that the approach cannot work elsewhere. Options only investigated or deferred are identified separately. The reasons describe project fit and accepted trade-offs; they are not performance or compatibility findings from a running implementation.

### Ownership and browser access

| Alternative | Standing and reason | Cost retained by the selected approach |
| --- | --- | --- |
| A workspace-owned SDK/controller or direct browser-to-model execution | **Rejected by author:** The existing host is to own model calls, execution, permissions, and session behavior. A controller would add provider/session responsibility and maintenance to obtain more explicit control of continuation or cancellation. | The package depends on a host that actually services input waits. It cannot manufacture missing continuation facilities or promise immediate interruption. |
| Existing host UI as the only playing interface | **Not adopted as a substitute:** This is a useful lower-code baseline from the brief, but does not provide the retained editable browser reader and cast-panel experience. The brief did not record a standalone rejection of all play through a host UI. | The browser adds source, dependencies, local services, public conventions, and failure states that must earn their complexity. The host UI remains available for ordinary setup/diagnostics and assistance. |
| Direct browser directory/file access without a local HTTP helper | **Rejected by author (T12):** Select the small editable Python bridge instead of making browser-specific directory permissions and file-access behavior part of the ordinary workflow. The bridge centralizes browser saves, public reads, and the acknowledged edit pause. | A local process must be started/reopened and its served paths constrained. Removing browser filesystem permissions does not remove process lifecycle work. |
| Adopt Impeccable's Live/decision-page implementation wholesale | **Not adopted as a dependency:** The brief treats these as inspected precedents. Their design-specific payloads, binaries, journals, and lifecycle assumptions do not automatically fit story play. Reuse the understood capability/wait patterns rather than import an unrelated execution package. | CouldHappen must implement and validate its own small file agreement and lifecycle. Precedent is not evidence that this story loop already works. |
| Dispatch the core writer skill by harness brand or require a known-host writer adapter | **Rejected by author:** The skill must let the agent establish its actual capabilities and determine how to perform shared operations. Brand branches would narrow portability and could assume tools absent from the actual session. | Capability assessment and honest fallbacks remain necessary. Native completion enforcement still needs concrete activated host wiring, documented separately. |

HyperFrames' inspected Studio path is likewise a limited handoff precedent, not an adopted runtime. Historical MightHappen approvals do not adopt its controller, database, publication protocol, or recovery machinery here.

### Shared conversations and input handling

| Alternative | Standing and reason | Cost retained by the selected approach |
| --- | --- | --- |
| Require final writer updates to pass through a serialized helper update API | **Rejected by author (T1):** Keep ordinary direct log editing, with the writer controlling when the browser may save. The helper instead acknowledges a pause after draining already-accepted saves, then the writer rereads and edits. | Both submission channels pause during the interval. Safety depends on cooperating writers; interrupted ownership must be resolved before reopening. |
| Process both logs in a mandatory global save order | **Rejected by author (T2):** Let the writer interpret related Story and Director inputs together. Strict ordering can put a later correction behind an earlier queued action and requires an additional cross-log ordering convention. | The writer's ordering is less predictable and can misjudge intent. It must explain consequential deferrals/conflicts and ask when context cannot resolve them. |
| Always process Director entries before Story entries | **Rejected by author (T2):** A fixed priority rule is unnecessary when the writer can interpret pending inputs together. Sustained Director discussion could otherwise indefinitely defer story actions. | Saving Director guidance is not an immediate interrupt or proof it affected an in-flight passage. Ordinary discussion still does not authorize advancing fiction. |
| JSON Lines conversations with Markdown bodies stored as strings | **Rejected by author (T5):** Markdown entries keep multiline prose comfortable to read and edit in ordinary files and Git. Small entry metadata supplies identity, role, and boundaries. | The chosen format needs explicit delimiters, escaping, and validation. Markdown alone does not distinguish complete entries or prevent malformed metadata. |
| A separate per-input disposition file keyed by message IDs | **Rejected by author (T6):** Keep pending/addressed/deferred metadata with each human entry, reducing independent authorities that can disagree after a restore. | Updating dispositions requires the shared-log edit pause. Prose and disposition saves can still be interrupted separately and need inspection. |
| A separate inbox or a universal one-outstanding-input limit | **Not adopted:** The shared conversations remain authoritative. A separate inbox changes that arrangement; a universal limit would extend blocking beyond the writer-controlled prose phase and short edit intervals. Neither was selected as a blanket simplification. | The writer must reconcile several pending entries when they exist. The helper cannot avoid that responsibility by silently dropping, merging, or scheduling them. |

The writer-controlled prose-production block and the acknowledged file-edit pause solve different problems. Neither is tied to browser reveal animation, and private note/method work does not automatically block submissions.

### Recovery, compatibility, and checkpoint assurance

| Alternative | Standing and reason | Cost retained by the selected approach |
| --- | --- | --- |
| Require a fresh session after every Director Undo | **Rejected by author (T3):** Continuing in the current session preserves useful knowledge of what the player disliked and why a different approach may be needed. Withdraw the attempted development's fictional authority while retaining the rejection as feedback. | The writer can accidentally reuse rejected facts. It must reread restored records and reconcile assumptions; a fresh session remains a fallback, not a cure for bad saved knowledge. |
| Live changeover between incompatible public conventions | **Rejected by author (T4):** Pause and reopen affected components rather than maintain multiple active representations and conversion logic. Ordinary cast additions, prose changes, and private-method changes do not become migrations. | Play pauses for incompatible changes. Stale clients must be refused, drafts preserved, and interrupted maintenance completed or reverted before writes reopen. |
| An enforced checkpoint-age/span limit during continuous play | **Rejected by author (T7):** Keep meaningful commit timing with the writer, checking at deliberate closure and actual supported host completion. An interval adds bookkeeping and another constraint during play. | Several exchanges can remain uncheckpointed. Crashes/forced termination can bypass the selected checks, and coarse history can limit Undo precision. |
| Put fresh-context validation only in a companion test after the scene | **Rejected by author (T8):** Observe the handoff within the short scene so actual disclosures and Director guidance test the writer's ongoing recordkeeping rather than relying on the old live context. | The demonstration includes a planned session transition. Separate ordinary-loop failures from restart failures when reporting the observation. |
| An automatic recovery supervisor or a blanket workspace reset | **Not adopted:** The approved recovery procedure uses writer judgment, a quiet boundary, and normal host assistance where needed. A reset can erase applicable guidance and useful method/UI improvements, while a supervisor adds ownership of running work that belongs to the host. | Mixed commits may require reconstruction. The writer must establish that relevant old work stopped, explain real limits, reconcile pending input, and wait for new Director direction. |

Exact rollback of every interaction is outside the promise. Required per-response commits would impose a different granularity policy and still would not prove semantic completeness or erase live context. Retained improvements must be inspected for rejected fictional assumptions; keeping a helper file does not make everything inside it valid.

### Helper runtime and frontend workflow

| Alternative | Standing and reason | Cost retained by the selected approach |
| --- | --- | --- |
| JavaScript/Node.js for the supplied shared helpers | **Rejected by author as the default (T11):** Prefer editable Python scripts, initially using the standard library. The author accepts agent-assisted runtime installation and wants helpers the writer can understand and adapt. This is not a finding that models universally write Python more reliably. | Svelte/Vite still requires Node/npm, so this design uses two runtimes. Python installation, invocation, and availability must also be verified. Additional writer helpers may use another suitable language. |
| Distribute only a self-contained helper executable | **Rejected by author as the starting package (T11):** Avoid platform build/release maintenance and keep supplied helper source directly editable without rebuilding an executable for each change. | Python must be available. A binary could simplify setup on supported targets, but would introduce a different packaging/release obligation. |
| Alpine with browser-ready HTML/JavaScript | **Rejected by author for the frontend (T13):** The author selected Svelte/Vite for localized component edits, checking feedback, HMR, and their own Svelte experience. Alpine's smaller setup remains a valid counterargument; it does not supply the selected compiler/component workflow. | Svelte adds frontend tooling and reactivity conventions. The writer needs pinned guidance and checks rather than assuming every familiar-looking example fits the project. |
| Preact components with HTM or a Vite/JSX workflow | **Rejected by author for the frontend (T13):** Reusable components are viable, but the selected Svelte workflow better matches the author's experience and desired writer-maintenance feedback. No general claim of better model accuracy decides this choice. | Preact's ordinary JavaScript and possible no-build route are benefits forgone. Svelte still requires deliberate subscription, state, and browser verification. |
| Build frontend assets for Python to serve during ordinary play | **Rejected by author as the default serving mode (T14):** Keep the playing interface connected to live Vite so writer source edits can appear through HMR without rebuilding and switching back to a distribution. A static build remains useful for checks/distribution. | Ordinary play requires both Vite and Python. A failed transform or stopped dev server can interrupt the interface, and HMR does not automatically preserve drafts or reading position. |
| Server-sent change notifications for saved-data display | **Rejected by author (T15):** Prefer short periodic reads over a persistent connection with reconnect/cleanup behavior. Public files remain authoritative and snapshots update by entry identity. | The browser makes repeated local requests and notices changes on a later check. This does not select how the agent's separate input wait returns control or imply a model call per poll. |
| Character-by-character copying of composed prose onto disk | **Rejected by author for reveal animation:** Normal saves plus browser-side reveal achieve the intended effect without a disk write for every character. Copying staged text does not reduce its prior composition time. | Animation is presentation after a save, not raw model-token streaming. New entries and existing-ID authorized revisions need different display behavior. |

A lightweight interface does not by itself imply no compiler. The chosen workflow accepts agent-managed dependency/service setup and keeps the authorable sources available. An installation obstacle is not automatically a reason to reject a compatible harness.

### Reference hosts and OpenRouter route

| Alternative | Standing and reason | Cost retained by the selected approach |
| --- | --- | --- |
| Reuse Codex through Ori for the OpenRouter reference | **Rejected by author for this reference role (T10):** Prefer Pi's native provider route and an additional practical portability reference rather than adding a provider launcher around Codex. The author's expectation of broader usefulness is a preference, not a measured popularity or compatibility result. | Pi adds a third host surface and native completion integration to validate. Ori may still work; it is simply not an adopted dependency. |
| Select OpenCode as the initial native OpenRouter reference | **Not selected (T10):** Pi is the adopted reference. The recorded OpenCode investigation had not established the required completion-enforcement path; native provider/skill support alone did not settle the full lifecycle. | Pi's actual versions, wait behavior, extension activation, and chosen model pairing must still be tested. The comparison does not prove OpenCode cannot satisfy the requirements. |
| Promise every investigated OpenRouter host | **Not adopted:** OpenCode, Hermes, and DeepSeek Harness remain comparison candidates rather than additional required integrations. Observations about one surface do not certify another. | The initial evidence covers a narrower set of configurations. Other users' agents remain eligible through the common capability checklist, with assurance stated according to observed behavior. |

T9 selects validation on Codex interactive CLI first and Claude Code interactive CLI second. Claude Code remains a required support target, rather than a rejected host. The current IDE surface is not certified by a CLI test. Pi/OpenRouter is an additional reference pairing, not a prerequisite or brand branch in the portable core skill.

### Deferred scope

The author deferred runtime story image generation, browser Stop, a complete mystery arc, and a full branching-history interface. The first scene uses preserved card PNG portraits; adaptable instructions for future host/user image tools remain in scope. Deferral is not a technical rejection of those features.

Accept/Revise controls and a publication-acceptance workflow remain outside this design. Undo reports the restoration and waits for direction; it does not automatically generate a replacement passage. Routine understood helper failures can still be repaired under the standing permission, with proportionate mechanical/prose reconciliation and disclosure of larger failures.

## Detailed Implementation

The author approved this Detailed Implementation Plan on 2026-11-04. This section is a design for later implementation, not authorization to start application work during this EGM drafting session. Alternatives Considered was approved on 2026-11-04. All paths below are relative to the portable workspace root. Named source/config/test files are the complete planned initial inventory; generated imports, runtime files, dependencies, and test output are identified separately.

Use the single sequence below. Each step states its files, behavior, reason, and completion evidence. No production files, package installations, app services, active checkpoint hooks, or model sessions have been created by writing this plan.

1. **Establish the portable workspace and explicit operating scope.**

   | File | Action and reason |
   | --- | --- |
   | `README.md` | Create a short entry point: open this directory with an existing agent and ask it to read the writer skill and “set up.” Explain prerequisites, source layout, reduced assurance, and recovery assistance. |
   | `START_HERE.md` | Create the stable writer reentry index. Point to the logs, applicable guidance, current writer-managed world records, methods, and recovery state. Initially leave private-world links empty rather than inventing a scene. |
   | `couldhappen.json` | Create project configuration with contract version 1, a workspace UUID initialized once at setup, browser poll interval 1000 ms, and explicit Git checkpoint scope/exclusions. This identifies the workspace without exposing its absolute path to the browser. |
   | `.gitignore` | Create exclusions for `.couldhappen/`, Python caches, `web/node_modules/`, `web/dist/`, `web/test-results/`, `web/playwright-report/`, `.env`/`.env.*`, and temporary save files. Do not ignore story source, imports, or authorable helpers. |
   | `.gitattributes` | Create UTF-8/LF text conventions and mark PNG assets binary, reducing platform-only log diffs. Readers still accept CRLF input. |
   | `docs/public-contract.md` | Create the normative public format, HTTP/control interface, error meanings, state transitions, and compatibility rules defined below. Keep this independent of harness brands. |

   The directory itself is the initial distributable workspace: skills and source stay alongside its story files. Installation does not require a global skill installer or another agent runtime. Native discovery is optional; explicitly reading the documented skill entry point is sufficient.

   Configure checkpoint scope to include the workspace's story and editable operating materials, including newly created writer records. Default to repository-relative `.`, with explicit exclusions for unrelated planning artifacts already present here: `docs/designs/couldhappen.md`, `docs/planning/technical_plan_decisions.md`, `docs/planning/design_reconciliation.md`, `docs/planning/concepts_brief.md`, `docs/planning/brainstorming_notes.md`, `docs/planning/egm_draft_handoff.md`, `docs/reviews/goldfish_review_report.md`, `goldfish_reviews/`, `docs/research/browser_handoff_research.md`, `docs/research/host_compatibility_notes.md`, `docs/designs/impeccable_direction_notes.md`, `docs/research/carryover_audit.md`, and `docs/research/prior_imagery_findings.md`. These exclusions affect the fiction checkpoint check, not whether those documents may separately be versioned. Review any additional unrelated existing files at setup and record exclusions explicitly; do not silently commit or hide them.

   Private knowledge remains freeform. New private paths are allowed and must be linked from the reentry index when relevant. If a path is outside the actual Git scope, state that limit or expand the scope deliberately before claiming checkpoint coverage.

2. **Write the common writer skill and its focused references.**

   | File | Action and reason |
   | --- | --- |
   | `.agents/skills/couldhappen/SKILL.md` | Create the portable writer entry point and link only the references needed for the current operation. Explain that the current workspace agent is the writer. |
   | `.agents/skills/couldhappen/references/capabilities.md` | Describe required outcomes and how the agent establishes actual tools, permissions, waiting, continuation, and completion enforcement. No brand dispatch or mandatory host adapter. |
   | `.agents/skills/couldhappen/references/setup.md` | Describe prerequisite installation, project commands, safe first setup/reopening, connection verification, and normal human assistance when the host cannot establish a required boundary. |
   | `.agents/skills/couldhappen/references/writing.md` | Cover Story/Director interpretation, meaningful influence, whole-cast authorship, input dispositions, production blocks, normal saves/reveal, and deliberate session closure. |
   | `.agents/skills/couldhappen/references/records-and-imports.md` | Cover durable distinctions, discoverability, natural preferences, PNG/JSON source interpretation, preserving original cards, and public disclosure. No fixed world database. |
   | `.agents/skills/couldhappen/references/recovery.md` | Specify interrupted pauses, coherent Director Undo, retained improvements/guidance, current-session memory, new-direction waiting, and proportionate helper repairs. |
   | `.agents/skills/couldhappen/references/interface.md` | Document authorable Svelte/Python sources, version/style conventions, maintenance/restart commands, and checks. Load this detail when interface/helper maintenance is needed. |
   | `.agents/skills/couldhappen/references/future-images.md` | Explain how to discover actual host/user image capabilities later, preserve source material, and expose only intended public assets. Require no image provider or generated imagery in the first scene. |

   The skill tells the agent what each operation must accomplish, then has it determine the concrete host tool invocation. It can name Python/npm/Git and the project's commands without naming a required harness. Research host details at setup or after relevant changes, not on every exchange.

   Make the creative behavior explicit: a new character needs no card or portrait; ordinary Director discussion does not advance fiction; embedded card instructions do not override writer guidance; original human message bodies are preserved; addressed preferences may remain applicable. Include the standing permission for quiet, proportionate technical/mechanical repairs across code, records, and affected prose. Substantial withdrawal of fiction still requires recovery and new direction.

3. **Implement the shared file formats and validation primitives.**

   | File | Action and reason |
   | --- | --- |
   | `public/story.md` | Create an empty canonical Story conversation with the title `# Story`. Do not insert illustrative scene events. |
   | `public/director.md` | Create the separate canonical Director conversation with the title `# Director`. |
   | `public/cast.json` | Create version-1 public cast data with an empty characters array. |
   | `public/work.json` | Create version-1 durable work state: mode `play`, with no recovery question. |
   | `helpers/__init__.py` | Create the small internal Python package; no pip installation is required. |
   | `helpers/files.py` | Implement entry encoding/parsing, public validation, stable IDs/body hashes, atomic helper saves, and public snapshot construction. Keep story interpretation outside this module. |

   **Conversation format.** Store UTF-8 text, normalized to LF by supplied writers. After the channel title, each entry has this shape; this is a format illustration, not implementation code:

   ```text
   <!-- couldhappen:entry {"id":"<UUID>","role":"human","status":"pending"} -->
   The original human contribution, with normal prose paragraphs.
   <!-- couldhappen:end -->
   ```

   Writer entries use `role: "writer"` and omit status. Human status is exactly `pending`, `addressed`, or `deferred`. IDs are UUIDs, unique across both logs. Keep IDs through authorized revisions; never replace a human entry's role/body merely to mark it handled. Unknown required formats or conflicting IDs invalidate the view rather than become input.

   Reserve lines beginning with `<!-- couldhappen:`. Encode body lines consisting of zero or more leading backslashes followed by that prefix by adding one leading backslash; decode exactly one on reading. This also preserves literal backslashes. A supplied entry-format command performs this escaping for arbitrary human text. The parser uses explicit boundaries, not a loose search for comments or file timestamps.

   Serialization adds exactly one separator newline before the end marker; remove exactly that separator when decoding, preserving the body's own trailing newlines. Preserve body content after the documented LF normalization. Reject empty/whitespace-only submitted bodies. Outside entries allow only the channel title and blank lines. Report malformed entries with channel and line number.

   **Other public files.** `cast.json` has `schema_version: 1` and `characters`, each with a stable `id`, disclosed `name`, optional disclosed `description`, and optional relative `portrait` under `public/assets/`. A missing portrait is valid. `work.json` has `schema_version: 1`, `mode: "play" | "awaiting_director"`, and `director_question_id: null | UUID`. Awaiting-direction mode requires an existing writer question in the Director log. No per-input status map is added.

   Helper saves write a temporary file in the target directory, flush it, and replace the target before acknowledging success. Detect replacement errors and retain the previous valid view. Direct writer tools may save differently inside the acknowledged pause; no atomic transaction across prose, dispositions, private notes, and Git is promised.

4. **Implement the loopback bridge and explicit writer controls.**

   | File | Action and reason |
   | --- | --- |
   | `helpers/runtime.py` | Manage workspace identity, connection/control files, exclusive helper ownership, generation IDs, and interrupted-control recovery. Store no model credentials. |
   | `helpers/bridge.py` | Implement the bounded HTTP service, serialized submissions, acknowledged pauses, current valid snapshots, and loopback writer-control endpoint. |
   | `helpers/__main__.py` | Expose one documented CLI for validation, serving, controls, waiting, imports, and checkpoint inspection/checking. |

   The helper binds `127.0.0.1`. Prefer its previously recorded free port on reopen; otherwise bind an available port and publish the actual address. An exclusive workspace lock prevents accidentally starting a second helper. A stale lock is not cleared on age or PID alone: recovery first establishes that the former service/writer stopped.

   Generate `.couldhappen/connection.json` for the address, workspace/generation IDs, and a random local writer-control secret; `.couldhappen/control.json` for persisted pause/production/ownership state; and `.couldhappen/bridge.lock` for exclusive ownership. These are runtime outputs, Git-excluded, and never browser-served. Runtime state is not authoritative input bookkeeping. Generate a new helper generation on restart and on explicit recovery invalidation.

   Start closed. A writer must inspect the current files and establish safe ownership before opening submissions. Persist interrupted blocks so restart cannot silently override them. Do not use a timeout to claim that an old writer is gone.

   | Browser endpoint | Contract |
   | --- | --- |
   | `GET /api/snapshot` | Return contract/workspace/generation IDs, revision, parsed Story/Director entries with body hashes, public cast/asset revisions, durable mode, and known submission permissions/reasons. Support `If-None-Match` with 304 for an unchanged revision. |
   | `POST /api/entries` | Accept `schema_version`, `workspace_id`, `generation`, `channel`, client UUID `id`, and `body`. The server assigns human role/pending status. Return 201 after a new successful save, or 200 for an identical already-saved entry. |
   | `GET /api/assets/<relative-name>` | Serve only referenced, validated public PNG assets. Resolve the path under the asset root and refuse traversal/symlink escape. |

   Use bounded JSON requests, initially at most 256 KiB of UTF-8 body text, with a clear 413 result and retained draft when exceeded. Reject an ID reused with a different body/channel with 409. A stale generation/contract returns 409; a closed edit/production/recovery permission returns 423; malformed input returns 400; a save failure returns 503 without a success receipt. Include a stable error code and user-readable explanation. A validation failure keeps the last coherent browser view, adds an explicit saved-file validation error to its public status, and closes new saves until inspected. Snapshot revisions include generation and permission/error changes as well as public content; cache asset URLs by content hash.

   Check identical retry IDs against the canonical valid conversations under the save lock. A normal uncertain retry reuses the same ID/body; it does not create a second message. After a generation change, the browser first rereads the snapshot: an absent old ID is not permission to replay it, especially after Undo. Keep that text as a draft requiring deliberate submission.

   Give the writer CLI a separate `/control` request path protected by the runtime secret. Vite does not proxy it, and it is not part of the browser interface. Validate the actual local Host and expected frontend Origin for browser mutations; allow no wildcard CORS or arbitrary-command/file endpoint.

   **Pause acknowledgment.** Under a state lock, a pause first closes acceptance to new browser writes. Already-accepted requests finish through a separate serialized file-write lock; acknowledgment waits for their count to reach zero. Then return an opaque edit-owner token. While paused, expose current controls but keep the last coherent conversation snapshot. The writer rereads both files only after acknowledgment. Release requires the matching token and successful validation of both logs/cast/work state; it refreshes the snapshot before acceptance reopens. A production block remains independent.

   Expose these CLI operations, using the agent's established interpreter in place of `python`:

   | Command | Meaning |
   | --- | --- |
   | `python -m helpers validate --root .` | Validate all public records; JSON diagnostics and exit 0/2 for valid/invalid. |
   | `python -m helpers entry --role writer --body-file <path>` | Print a correctly encoded new entry; do not write a conversation or bypass the pause. |
   | `python -m helpers serve --root . --frontend-origin <origin>` | Run the bridge in the foreground, printing connection details without the control secret. The host may manage this process using its own tools. |
   | `python -m helpers writer claim --root .` | Establish initial ownership after checks. If interrupted ownership exists, require explicit recovery after establishing the former writer stopped. |
   | `python -m helpers writer pause --root .` | Obtain the acknowledged edit token. |
   | `python -m helpers writer release --root . --token <token>` | Validate, refresh, and release that edit interval. |
   | `python -m helpers writer block --root . --on` / `--off` | Set/clear the writer's separate prose-production block. |
   | `python -m helpers writer recover --root . --previous-writer-stopped` | Record the caller's established recovery boundary, validate actual files, rotate generation, and clear abandoned ownership explicitly. The flag is an assertion by the cooperating agent, not automatic proof. |
   | `python -m helpers writer invalidate --root .` | Rotate the generation under an owned pause for Undo or incompatible maintenance. |
   | `python -m helpers writer close --root .` | Run the scoped checkpoint check and close normal-play ownership only when it passes; do not commit or invent a checkpoint. |

   Keep secrets/tokens out of durable story notes and ordinary browser snapshots. A successful claim/recover cannot itself authorize story advancement.


5. **Implement local waiting without a second message authority.**

   Add waiting behavior to `helpers/runtime.py` and its commands to `helpers/__main__.py`; the bridge's accepted snapshots remain derived from canonical logs.

   `python -m helpers wait --root . --timeout 0` waits locally until eligible pending human entries exist. Zero means no helper-imposed deadline; a positive timeout is available when an actual host tool requires bounded waits. Check locally about every 500 ms, emit no repeated unchanged output, and return one JSON result containing channel/ID references and current generation. Exit 0 for input, 3 for a quiet timeout, and 2 for invalid/recovery-required state. The writer then rereads current records; a wait result is not a reservation or proof that the input was handled.

   In ordinary mode inspect pending human entries in both logs; return their references without prescribing cross-log order. Deferred and addressed entries do not wake the wait. Writer saves, metadata-only changes, and cast edits do not count as new human input. While an edit pause is held, wait for a coherent released view rather than parse a partial writer save.

   In `awaiting_director` mode, return only pending human Director entries following the recorded question in that log. Earlier pending entries and Story entries cannot satisfy recovery waiting. Story submission is closed with an understandable “Awaiting Director direction” reason; Director submission can reopen after the edit/production blocks clear.

   The core skill has the agent choose a supported foreground wait, serviced yielded command, or available native monitor. It must continue servicing results/renewals and record real timeout overhead. No local file marker proves that the agent is still alive, and a detached wait cannot revive an ended session.

6. **Implement imports and public portrait extraction.**

   | File | Action and reason |
   | --- | --- |
   | `helpers/cards.py` | Read PNG/JSON cards, preserve originals, extract metadata, prepare private normalized source material, and export a public portrait without embedded card text. |
   | `imports/README.md` | Explain content-addressed private imports, original preservation, supported formats, diagnostics, and why importing does not publish a character. |

   Expose `python -m helpers import-card --root . --source <path>`. Accept flat V1 JSON and V2/V3 JSON envelopes; for PNG read CRC-validated chunks and the base64 UTF-8 JSON in `chara` or `ccv3` tEXt metadata, preferring valid V3 when both are present. If preferred metadata is malformed, report it rather than silently treating a different character definition as equivalent. Preserve unknown card fields in private extracted JSON. Do not fetch remote assets, execute card scripts, replace system instructions, or establish a greeting as a story event.

   Store generated outputs at `imports/<source-sha256>/source.png` or `source.json`, `card.json`, and `import.json` containing source hash, detected format, extraction result/warnings, and local provenance. Repeat imports reuse identical content without overwriting different source bytes. JSON cards without a portrait remain valid. Unsupported archives/remote asset schemes receive an explicit diagnostic; CHARX is not promised by the PNG/JSON scope.

   Add `python -m helpers portrait --root . --source <imported-source.png>`. Export `public/assets/<portrait-sha256>.png` only when the writer deliberately requests public portrait preparation. Preserve image/appearance chunks, including image data, palette/transparency and color information; remove text/EXIF/private ancillary metadata. Validate chunk lengths/checksums and reject unsupported critical structure rather than emit a corrupt image. Preserve the original bytes privately. Creating that asset still does not add a cast entry: the writer makes the disclosure decision.

   Use bounded reads/decompression and explicit errors for truncated PNG, invalid base64/JSON, missing metadata, and conflicting card definitions. Start with a 32 MiB source limit and an 8 MiB decoded metadata limit; a rejected import retains the source path for the writer to handle without claiming success.

   The [V2 specification](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md), [V3 embedding specification](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md#embedding-methods), and [SillyTavern's own parser](https://github.com/SillyTavern/SillyTavern/blob/release/src/character-card-parser.js) are format evidence. CouldHappen imports source material; it does not adopt those applications' prompt-execution semantics.

7. **Build the source-retaining Svelte/Vite reader.**

   | File | Action and reason |
   | --- | --- |
   | `web/package.json` | Create exact dependency pins and named development/check/test/build scripts. |
   | `web/package-lock.json` | Generate and retain the resolved dependency lock during implementation, so later setup uses `npm ci`. |
   | `web/index.html` | Create the browser entry document with language, viewport, title, and mount point. |
   | `web/vite.config.js` | Configure the Svelte plugin, loopback/strict frontend port, isolated frontend root, narrow API proxy, and explicit filesystem boundaries. Read only necessary connection fields on the server side. |
   | `web/svelte.config.js` | Make the modern Svelte compiler convention explicit; enable no experimental async mode or additional backend. |
   | `web/jsconfig.json` | Enable JavaScript/JSDoc checking through the Svelte checker and exclude generated/dependency files. |
   | `web/src/main.js` | Mount the client-side app and load shared styles. |
   | `web/src/App.svelte` | Compose the selected shell, Story/Director navigation, reader, composer, status messages, and responsive cast access. |
   | `web/src/components/Conversation.svelte` | Render entries keyed by stable ID and preserve reading anchors across updates and authorized revisions. |
   | `web/src/components/ProseEntry.svelte` | Render sanitized Markdown and manage per-entry reveal without replaying existing prose. |
   | `web/src/components/Composer.svelte` | Keep separate channel drafts and implement submission/uncertain-save behavior without confusing saved with applied. |
   | `web/src/components/CastPanel.svelte` | Display only disclosed cast data, handle absent portraits, and provide usable narrow-screen access. |
   | `web/src/lib/api.js` | Implement bounded snapshot polling, conditional reads, POST receipts/errors, visibility refresh, and cancellation/cleanup. |
   | `web/src/lib/session.js` | Hold current view state, workspace/channel drafts, in-flight request identity, reading anchors, and generation changes. Keep transport state separate from input dispositions. |
   | `web/src/lib/markdown.js` | Convert Markdown with Marked and sanitize the resulting HTML with DOMPurify under a restricted prose policy. |
   | `web/src/lib/reveal.js` | Animate safe rendered text nodes for genuinely new writer entries; cancel/finish appropriately on revision, recovery, unmount, and reduced-motion settings. |
   | `web/src/styles.css` | Define Woven colors, spacing, typography, focus treatment, responsive layout, and reduced-motion behavior. |
   | `web/README.md` | Map authorable components, state ownership, source/dev/build modes, dependency pins, and maintenance checks for future writer edits. |

   Implement Svelte 5 runes and modern event attributes. Use derived values for derived state, immutable/raw snapshots when appropriate, keyed entry loops, and explicit timer/listener cleanup. Keep normal writing independent of UI tooling. Actual later interface implementation follows the installed relevant UI/Svelte skills and the retained Woven selection; this plan does not reroll or regenerate the visual reference.

   Poll about once per second without overlapping requests. Read immediately after a save, visibility return, or reconnect. A late response from an older request/generation cannot replace a newer view. Cancel work on unmount/HMR. A first snapshot renders existing prose immediately; subsequent new writer IDs may animate. A body change under an existing ID renders as an authorized revision, not a new response. Generation changes resynchronize immediately and do not replay restored history.

   Persist unsent drafts, immutable in-flight ID/body, and reading anchors in browser session storage keyed by workspace/channel; session storage keeps separate tabs independent while surviving same-tab reloads. Do not store private world material. Clear only the exact body confirmed saved; preserve any newer typing. While a receipt is uncertain, resolve the original ID from a fresh snapshot or retry that identical payload only within the same generation. Never turn a restored-away message into an automatic resubmission.

   Render Markdown only through the sanitizer. Allow prose paragraphs, emphasis, lists, quotes, code, and ordinary safe links; exclude scripts, embedded controls, SVG/MathML, and automatic remote images. Public portraits use the dedicated asset route. Marked explicitly requires output sanitization; see [Marked's documentation](https://github.com/markedjs/marked#usage) and [DOMPurify](https://github.com/cure53/DOMPurify).

   Keep animation separate from composer permission. Do not insert unfinished raw HTML while revealing characters. Preserve the reader's position when they are reading earlier text; only follow the bottom when already near it. Honor reduced motion, keyboard navigation, visible focus, and live-status announcements without reading every animated character aloud.

8. **Make setup reproducible and agent-operated.**

   | File | Action and reason |
   | --- | --- |
   | `docs/setup.md` | Document exact project commands, prerequisite checks/install paths, service lifecycle, workspace verification, and safe reopening. Keep host-specific examples elsewhere. |

   Target Python 3.11+ using standard-library APIs and Node 24+ for the selected frontend dependency set. These are implementation targets, not claims that every newer runtime has been tested. The current machine reports Python 3.14.2, Node 25.6.0, npm 11.8.0, and Git 2.53.0.windows.1. Reference validation records the actual runtime used.

   Pin these direct frontend packages from the registry metadata checked on 2026-11-04:

   | Package | Exact initial version | Role |
   | --- | --- | --- |
   | `svelte` | 5.57.3 | UI components/compiler. |
   | `vite` | 8.3.5 | Live frontend and optional build. |
   | `@sveltejs/vite-plugin-svelte` | 7.3.1 | Svelte/Vite integration. |
   | `svelte-check` | 4.7.8 | Component, JavaScript, CSS, and accessibility diagnostics. |
   | `typescript` | 6.0.3 | Checker dependency for JavaScript/JSDoc; do not introduce TypeScript application syntax just to use the checker. |
   | `marked` | 18.1.3 | Markdown conversion. |
   | `dompurify` | 3.4.17 | Browser HTML sanitization. |
   | `@playwright/test` | 1.64.1 | Development-only browser verification. |

   Check direct/transitive compatibility when generating the lockfile. The checked Svelte plugin accepts the selected Svelte/Vite versions; the checked Svelte checker accepts TypeScript 5/6, so latest TypeScript 7 is deliberately not selected. Metadata sources are the official npm registry package records, for example [Svelte](https://registry.npmjs.org/svelte/5.57.3), [Vite integration](https://registry.npmjs.org/@sveltejs/vite-plugin-svelte/7.3.1), and [checker peers](https://registry.npmjs.org/svelte-check/4.7.8). No dependencies were installed during design.

   Set package scripts to `dev` (Vite), `check` (svelte-check using jsconfig), `test:unit` (Node's built-in test runner), `test:browser` (Playwright), and `build` (Vite build). Do not add SvelteKit, Tailwind, a database, or a provider SDK.

   For first source implementation, generate `web/package-lock.json` from exact direct pins; ordinary player setup thereafter runs `npm ci` in `web/`. It does not recreate a project from a floating scaffold. The agent checks the actual Python/Node/npm/Git invocations and installs missing prerequisites when permitted, then verifies them in its own command environment.

   Setup chooses and remembers an available frontend origin, normally `http://127.0.0.1:5173`, starts the Python helper with that allowed origin, then starts `npm run dev -- --host 127.0.0.1 --port <chosen-port> --strictPort`. Vite reads the helper address from the private connection file at startup and proxies only `/api/snapshot`, `/api/entries`, and `/api/assets/`. Its source root/allowance excludes private records, imports, runtime files, and the surrounding project. Explicitly block those private paths from Vite's file serving even if a frontend source import accidentally references them; verify this against the selected Vite version. Do not put control secrets into browser-facing Vite environment variables.

   Reuse a service only after matching its workspace/generation, not merely finding an occupied port. If a helper restart changes its address, restart Vite deliberately so its proxy points to the actual new service. Keep the frontend origin stable where possible for browser draft continuity. If it must change, help preserve/copy drafts from the old tab before claiming continuity across origins.

   If no repository exists, initialize Git at the workspace root using normal local identity/configuration. If an existing repository contains the workspace, constrain operations to this workspace and its configured paths rather than treating the entire parent repository as story scope. Establish an appropriate initial baseline checkpoint through writer review; do not sweep unrelated files into it.

   Validate the public files, establish safe writer ownership, verify browser reads/submissions, establish a working input wait, and check native checkpoint activation when available. No automatic checkpoint hook installation silently replaces other hooks or bypasses normal host trust.


9. **Provide opt-in native checkpoint examples around one Git check.**

   | File | Action and reason |
   | --- | --- |
   | `helpers/checkpoints.py` | Implement neutral scoped Git status/checkpoint inspection with JSON results. Do not stage, commit, or restore files automatically. |
   | `integrations/codex/hooks.example.json` | Provide a Stop command-hook fragment invoking the Codex wrapper with the established Python/root paths. |
   | `integrations/codex/stop.py` | Read the native event, call the shared check, and translate dirty/clean/error outcomes into Codex's actual hook output. |
   | `integrations/claude/settings.example.json` | Provide the equivalent Claude Code Stop fragment, separately from the core skill. |
   | `integrations/claude/stop.py` | Translate the common check for Claude Code and handle documented paused/background work only when established in the actual version. |
   | `integrations/pi/checkpoint.ts` | Provide a small Pi extension calling the same check at the final actionable settlement boundary. It owns no writing loop. |
   | `docs/reference-hosts.md` | Record concrete setup, trust/activation, provider configuration, supported wait examples, and version-specific limitations for the three references. |

   Add `python -m helpers checkpoint check --root .`: resolve the actual repository, use NUL-delimited Git status with the configured scope/exclusions, and include staged, unstaged, deleted, and untracked relevant paths. Return exit 0/JSON `clean`, exit 1/JSON `dirty` with paths, or exit 2/JSON `error` with the actual failure. A missing repository, unmerged state, or inaccessible Git is not a clean checkpoint.

   Add `python -m helpers checkpoint inspect --root . --ref <commit>` to resolve a real commit and describe recorded paths/history for writer-led recovery. Invoke Git with argument arrays and validated repository-relative paths, not interpolated shell commands. Private filenames may be returned to the writer but are not browser snapshot content.

   Writer claim arms the checkpoint integration for managed play in that workspace; unrelated design/development sessions are not automatically gated. Deliberate closure checks before disarming. Native wrappers act only in the intended workspace/armed play scope. They request further work on the concrete dirty result, never create an automatic “meaningful” commit, and allow completion when clean. Errors are explicitly reported as unavailable assurance and require attention, rather than being mislabeled as clean. Do not bypass trust or host continuation limits. On check errors, Codex/Claude wrappers emit a common warning system message instead of a clean result; Pi reports the failure through its available UI/log mechanism. Preserve the failure in validation evidence.

   | Reference | Concrete wiring and acceptance target |
   | --- | --- |
   | Codex interactive CLI | Start with the locally identified 0.165.0 surface, verifying behavior before claiming support. Use `hooks.Stop[].hooks[]` command configuration. Exit 0 with `{"decision":"block","reason":"…"}` for dirty work, or `{}` when clean. Review exact hook definitions through normal trust. Another hook's `continue:false` can prevent continuation. |
   | Claude Code interactive CLI | Start with locally identified 2.1.300 using a demonstrated shell wait; do not assume a newer native Monitor is present. Use `hooks.Stop[].hooks[]` command configuration and the corresponding block/reason output. Validate whether actual Stop payloads expose background work; never infer “temporarily waiting” from a local stale marker alone. |
   | Pi/OpenRouter | Target published `@earendil-works/pi-coding-agent@1.5.0`. Its package documentation/types contain `agent_before_settle`; on dirty work append an extension-authored checkpoint instruction to the proposed entries and return `continue:true`. Use neither low-level `agent_end` nor notification-only `agent_settled` as the enforcement gate. |

   Use `stop_hook_active` as diagnostic context, not an unconditional instruction to skip unresolved dirty work. A dirty condition must actually be actionable with the established Git permissions. Report hook errors, inactive trust, aborts, or host limits as reduced assurance. Do not start an unconditional extension continuation loop.

   Source references: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code Stop](https://code.claude.com/docs/en/hooks#stop), and [Pi extension boundaries](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md). Pi's published-package source was inspected without installing/running it. The versions above identify validation targets, not successful runtime observations.

   During later authorized reference setup, merge rather than replace existing configuration. Planned activation targets are `.codex/hooks.json` (modify the existing file while preserving Impeccable entries), `.claude/settings.json` (create/merge the checkpoint fragment), and `.pi/extensions/couldhappen-checkpoint.ts` (copy the supplied extension). Do not activate these while merely implementing the package or drafting this design. Resolve command paths/quoting for the actual host; configuration examples do not contain account keys.

   Pi provider/model setup stays in normal user/host configuration. The human selects the OpenRouter model; record that actual pairing in validation. No key is copied into the story directory and no provider client is added to the package.

10. **Bind interruption, Undo, and incompatible maintenance to the same controls.**

    Complete the behavior in the already-listed `helpers/runtime.py`, `helpers/bridge.py`, `docs/public-contract.md`, and writer recovery/interface references.

    Recovery first closes browser saving and establishes that relevant former writer/delegated work cannot overwrite restoration. Inspect actual Git history/current changes before choosing paths. Restore/reconstruct the requested fiction and assumptions while preserving applicable Director guidance and useful improvements by default. Explain mixed-commit limits. No blanket reset, automatic branch rewrite, session supervisor, or automatic replacement prose is added.

    Under the acknowledged edit token, reconcile logs and private records, retain human bodies, and defer old unresolved inputs where appropriate. Append the recovery explanation and a new writer Director question. Set `work.json` to `awaiting_director` with that question ID. Rotate the browser generation, validate, and release; invalidating browser generations does not invalidate the current owned edit token. Enable Director saving while Story waits for new interpreted direction.

    A fresh helper/reentry validates the question pointer and preserves this mode. If the pointer or files are inconsistent, remain closed and report recovery required. New Director discussion may be answered without advancing fiction; only direction interpreted as authorizing continuation clears the durable mode. Remember the rejected approach as feedback in the current session, never as a restored fictional fact.

    Incompatible format/interface changes use the same close/inspect/update/validate/reopen boundary. Update contract consumers together and refuse stale writes. A private method change, cast addition, or ordinary visual edit does not automatically become such a migration. Python edits normally require restart; Vite HMR handles compatible frontend source updates. Verify both actual running services after restart.

    Quiet, understood technical repairs may continue after correcting their mechanical/prose consequences under the standing permission. Material failures or uncertain consequences are explained through Director discussion. Withdrawal of substantial fiction follows the new-direction recovery boundary.

11. **Add tests for actual failure boundaries and run the required checks.**

    | File | Action and reason |
    | --- | --- |
    | `tests/fixtures/public-v1.json` | Create shared representative entry/body/state cases, including reserved marker text, trailing newlines, duplicates, and malformed formats. No real/private story data. |
    | `tests/test_files.py` | Verify format round trips, exact body preservation after LF normalization, cross-log IDs, partial saves, and invalid work/question/cast references. |
    | `tests/test_bridge.py` | Exercise real loopback requests, in-flight save/pause overlap, duplicate/uncertain retries, stale generations, permissions, startup closure, and public/private path boundaries. |
    | `tests/test_cards.py` | Build small independent PNG fixtures in temporary storage and verify V1/V2/V3 extraction, original preservation, malformed data limits, and portrait metadata removal with image-data preservation. |
    | `tests/test_checkpoints.py` | Use isolated temporary Git repositories to verify staged/unstaged/untracked/deleted paths, scope exclusions, real commit inspection, and Git failures without changing this repository. |
    | `tests/test_integrations.py` | Verify native payload/output translation for clean/dirty/error cases and inactive play scope. These are adapter tests, not proof a host ran a hook. |
    | `tests/run_browser.py` | Start an isolated public-data workspace, owned helper and Vite processes, run browser checks, and clean up only those processes/temp data. Accept discovered Python/Node paths. |
    | `web/tests/session.test.js` | Use Node's test runner for revision/generation transitions, immutable retry payloads, newer typed drafts, and initial/new/revised entry recognition. |
    | `web/tests/browser.spec.js` | Test actual reader/composer/cast behavior, save failures/retries, Markdown sanitization, refresh, draft/anchor preservation, recovery waiting, keyboard/narrow-screen access, and reduced motion. |
    | `web/playwright.config.js` | Configure Chromium against the temporary test services, with output limited to ignored test-result/report paths. |

    Race tests use barriers around a real accepted save: request a pause while that save is in progress, prove acknowledgment waits for it, prove a later submission is refused, then reread/edit/release and verify both entries survive. Do not substitute a button-disabled assertion for backend saving evidence.

    Simulate a dropped receipt after the append, then retry the same ID/body and verify one human entry. Exercise a generation change after an uncertain save and prove the browser does not replay text automatically. Test that a blocked save retains the draft, helper restart begins closed, invalid partial records retain a previous valid view, and an old pending Story message cannot satisfy post-Undo waiting.

    For portraits, assert that image-data chunks remain unchanged while embedded card text is absent from the public output; an unchanged visible filename is insufficient. For public access, try traversal/encoded paths and private imports/runtime paths through both Python routes and Vite's file serving.

    Run these checks during implementation, not now:

    | Check | Command/observation |
    | --- | --- |
    | Python behavior | `python -m unittest discover -s tests -p "test_*.py"`. |
    | Frontend diagnostics | In `web/`, `npm run check`; resolve compiler, accessibility, and JavaScript issues. |
    | Pure frontend behavior | In `web/`, `npm run test:unit`. |
    | Browser integration | Install the pinned Playwright Chromium for development verification, then `python tests/run_browser.py`, which invokes the pinned browser suite against temporary services. |
    | Build viability | In `web/`, `npm run build`; this validates distribution output without changing ordinary live-serving mode. |
    | Svelte-specific review | Run the installed Svelte autofixer on authored components before finalizing them, following the applicable skill. This is a development check, not a player prerequisite. |
    | Live HMR and reader inspection | With a draft and earlier reading position present, make a compatible frontend edit, verify the live result, and inspect narrow/wide screens, focus, portrait treatment, and motion. Use actual browser evidence; compiler success alone is insufficient. |

    Browser fixtures use temporary conversation/import/runtime data, not the user's actual story. The launcher passes the temporary workspace to Vite server configuration without serving that directory wholesale. Resolve child executables and pass argument arrays; do not construct commands from story text. If a browser dependency is missing, the agent installs it as a development prerequisite rather than asking the player to operate a test harness.

12. **Demonstrate the creative loop and publish honest support evidence.**

    | File | Action and reason |
    | --- | --- |
    | `docs/validation.md` | Create the repeatable host/scene/recovery procedure, observable success criteria, and distinction between mechanical checks and narrative continuity. |
    | `docs/validation-results.md` | Create the evidence record with initially “not run” results. Later record actual dates, versions, surfaces, models, waits/renewals, trust/activation, failures, and limitations. |
    | `docs/demo-session.md` | Record the Director-approved scene prompt and source-card references when supplied, plus observation references; do not invent supplied cards or a special restart recap. |
    | `README.md`, `docs/setup.md`, `docs/reference-hosts.md`, `web/README.md` | Update the already-listed operating documentation to match observed commands/limitations rather than advertise untested behavior. |

    Validate Codex interactive CLI first, then Claude Code interactive CLI, then Pi's native OpenRouter pairing, using the same capability-driven skill and public agreement. Keep the actual underlying model human-selected. If an actual surface lacks the necessary event/tools, record the failure or guidance-only assurance and revise the example; do not silently claim another surface's success.

    For each demonstrated configuration, observe several real browser exchanges, constructive Director discussion, normal writer-controlled blocks, wait pickup and renewal limits, and at least one deliberate closure plus native dirty/clean completion check. Verify that ordinary waits do not impose commits after every story response. Record inactive/untrusted-hook behavior and that forced interruption can bypass checks. Existing Impeccable hooks do not count as checkpoint evidence.

    Use the short scene's real disclosures and applicable Director guidance for the fresh-session observation. At a quiet boundary stop the prior writer/delegates, preserve its files as maintained, and start a genuinely fresh compatible session without the former transcript or a test-only recap. Continue through ordinary browser input. Assess the resulting fiction for remembered established/disclosed material, character continuity, private possibilities remaining tentative, and retained preferences. File existence or the new writer's own confidence is insufficient evidence.

    Exercise a Director Undo against actual available history, including a case with retained method/interface improvements and old pending input. Verify the reported scope, reconciled assumptions/public view, preserved guidance, new question, and wait. Then give new Director feedback and observe an appropriately different approach in the current session. Distinguish reconstruction from exact restoration.

    Real scene assets/account access are inputs to this later observation, not invented requirements to satisfy during drafting. Generated files include `imports/<hash>/source.*`, `card.json`, `import.json`, `public/assets/<hash>.png`, writer-chosen private notes/helpers, the two conversation logs, cast/work records, runtime controls, dependency/build caches, and ignored test output. Their concrete data-dependent names cannot be known before play; the importer/control commands above bind their locations and ownership.

    Completion requires the mechanical checks and actual evidence appropriate to the support claims. An unperformed host/creative observation stays “not run” or “inconclusive”; it is not converted into a pass by source inspection. Fix demonstrated problems and update affected documentation before claiming the initial package works.

## Open Questions

All drafting sections are approved as of 2026-11-04. The [predecessor reconciliation](../planning/design_reconciliation.md) found no unresolved contradictions with the brief as amended by explicit author decisions. The final save location remains to be selected; implementation and runtime observations are separate future work.

* **Final destination:** No existing design directory was found. The proposed final location is `docs/designs/couldhappen.md`, pending the required destination choice. Rebase relative resource links for the selected location.
* **Later validation inputs:** Actual scene prompt/cards, host account access, and human-selected model pairings are needed for the specified demonstrations.
* **Unobserved behavior:** Hook trust/execution, repeated waits and renewal costs, runtime/browser compatibility, coherent Undo, and fresh-context writing remain validation obligations. Source and package inspection do not establish passes.
* **Independent review:** Recommend a fresh EGM design review after final saving. This reconciliation checks predecessor alignment and does not replace that review.

### Additional Resources

* [Fresh-session handoff](../planning/egm_draft_handoff.md)
* [Concept brief](../planning/concepts_brief.md) and [decision history](../planning/brainstorming_notes.md)
* [Technical decision record](../planning/technical_plan_decisions.md) and [final predecessor reconciliation](../planning/design_reconciliation.md)
* [Goldfish concept review](../../reviews/goldfish_review_report.md) — risks and proposals, not runtime certification
* [Browser handoff research](../../research/browser_handoff_research.md) and [host compatibility findings](../../research/host_compatibility_notes.md)
* [Selected visual direction and provenance](../../designs/impeccable_direction_notes.md), [selection record](../../designs/woven/direction-selection.json), and [product context](../../../PRODUCT.md)
* [Accepted creative carry-over](../../research/carryover_audit.md) and [portrait findings](../../research/prior_imagery_findings.md)

*Drafted with EGM*
