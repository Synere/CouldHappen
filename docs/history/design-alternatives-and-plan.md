# Design alternatives and implementation plan (history)

> **History, not current instructions.** These sections were split out of the [approved design](../designs/couldhappen.md) on 2026-11-05 after the first scope was implemented. Text here may describe superseded decisions or completed steps; where it differs from the design, setup, contract, or skill, those win.

## Alternatives Considered

This section draws on [Alternatives Weighed in the concepts brief](planning/concepts_brief.md#alternatives-weighed), the [brainstorming notes](planning/brainstorming_notes.md#alternatives-to-compare-not-decisions-already-made), and the author's subsequent [T1–T15 decisions](planning/technical_plan_decisions.md). The author approved the consolidated Technical Plan on 2026-11-04.

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

The author approved this Detailed Implementation Plan on 2026-11-04. This section is a design for later implementation, not authorization to start application work during this EGM drafting session. Alternatives Considered was approved on 2026-11-04. All paths below are relative to the portable workspace root. Named source/config/test files are the complete planned initial application inventory; existing documentation indexes and historical material remain in place. Generated imports, runtime files, dependencies, and test output are identified separately.

Use the single sequence below. Each step states its files, behavior, reason, and completion evidence. No production files, package installations, app services, active checkpoint hooks, or model sessions have been created by writing this plan.

1. **Establish the portable workspace and explicit operating scope.**

   | File | Action and reason |
   | --- | --- |
   | `README.md` | Extend the existing repository entry point while retaining its design/handoff links: open this directory with an existing agent and ask it to read the writer skill and “set up.” Explain prerequisites, source layout, reduced assurance, and recovery assistance. |
   | `docs/README.md` | Extend the existing documentation index with operational references as those files are implemented; keep canonical design and history locations discoverable. |
   | `START_HERE.md` | Create the stable writer reentry index. Point to the logs, applicable guidance, current writer-managed world records, methods, and recovery state. Initially leave private-world links empty rather than inventing a scene. |
   | `couldhappen.json` | Create project configuration with contract version 1, a workspace UUID initialized once at setup, browser poll interval 1000 ms, and explicit Git checkpoint scope/exclusions. This identifies the workspace without exposing its absolute path to the browser. |
   | `.gitignore` | Create exclusions for `.couldhappen/`, Python caches, `web/node_modules/`, `web/dist/`, `web/test-results/`, `web/playwright-report/`, `.env`/`.env.*`, and temporary save files. Do not ignore story source, imports, or authorable helpers. |
   | `.gitattributes` | Create UTF-8/LF text conventions and mark PNG assets binary, reducing platform-only log diffs. Readers still accept CRLF input. |
   | `docs/public-contract.md` | Create the normative public format, HTTP/control interface, error meanings, state transitions, and compatibility rules defined below. Keep this independent of harness brands. |

   The development directory is the portable package: skills and source stay alongside its story files. A durable story runs in a clean workspace created from the accepted release ZIP; see the accepted amendment below. Installation does not require a global skill installer or another agent runtime. Native discovery is optional; explicitly reading the documented skill entry point is sufficient.

   > **Accepted amendment (2026-11-05), now folded into the design.** The packaging and story-workspace boundary is defined by [Distribution and story workspaces](../designs/distribution-and-workspaces.md), with rationale in [ADR 0001](../decisions/0001-separate-story-workspaces.md) and [ADR 0002](../decisions/0002-publish-clean-release.md). The distribution design's normative-precedence section supersedes the packaging statement above, while the rest of this approved design remains normative for product behavior. The development repository remains upstream; the public artifact is a deterministic release ZIP under MIT; each real story runs in its own fresh Git workspace; the public contract is self-contained for the released runtime.

   Configure checkpoint scope to include the workspace's story and editable operating materials, including newly created writer records. Default to repository-relative `.`. Exclude historical planning/research material under `docs/archive/`, `docs/planning/`, `docs/research/`, `docs/reviews/`, `.research/`, and `goldfish_reviews/`, plus the implementation-planning handoff at `docs/implementation_handoff.md`. These exclusions affect the fiction checkpoint check, not whether those documents may separately be versioned. Review any additional unrelated existing files at setup and record exclusions explicitly; do not silently commit or hide them.

   Private knowledge remains freeform. New private paths are allowed and must be linked from the reentry index when relevant. If a path is outside the actual Git scope, state that limit or expand the scope deliberately before claiming checkpoint coverage.

2. **Write the common writer skill and its focused references.**

   | File | Action and reason |
   | --- | --- |
   | `.agents/skills/couldhappen/SKILL.md` | Create the portable writer entry point with the creative-initiative principle near the beginning, then link only the references needed for the current operation. Explain that the current workspace agent is the writer. |
   | `.agents/skills/couldhappen/references/creative-practice-examples.md` | Adapt the [optional creative practice examples](../designs/creative-practice-examples.md) into a self-contained skill reference. Illustrate useful experimentation, deliberate simplicity, and abandoning an unhelpful method; require no example to be implemented. |
   | `.agents/skills/couldhappen/references/capabilities.md` | Describe required outcomes and how the agent establishes actual tools, permissions, waiting, continuation, and completion enforcement. No brand dispatch or mandatory host adapter. |
   | `.agents/skills/couldhappen/references/setup.md` | Describe prerequisite installation, project commands, safe first setup/reopening, connection verification, and normal human assistance when the host cannot establish a required boundary. |
   | `.agents/skills/couldhappen/references/writing.md` | Cover Story/Director interpretation, meaningful influence, whole-cast authorship, input dispositions, production blocks, normal saves/reveal, and deliberate session closure. |
   | `.agents/skills/couldhappen/references/records-and-imports.md` | Cover durable distinctions, discoverability, natural preferences, PNG/JSON source interpretation, preserving original cards, and public disclosure. No fixed world database. |
   | `.agents/skills/couldhappen/references/recovery.md` | Specify interrupted pauses, coherent Director Undo, retained improvements/guidance, current-session memory, new-direction waiting, and proportionate helper repairs. |
   | `.agents/skills/couldhappen/references/interface.md` | Document authorable Svelte/Python sources, version/style conventions, maintenance/restart commands, and checks. Load this detail when interface/helper maintenance is needed. |
   | `.agents/skills/couldhappen/references/future-images.md` | Explain how to discover actual host/user image capabilities later, preserve source material, and expose only intended public assets. Require no image provider or generated imagery in the first scene. |

   The skill tells the agent what each operation must accomplish, then has it determine the concrete host tool invocation. It can name Python/npm/Git and the project's commands without naming a required harness. Research host details at setup or after relevant changes, not on every exchange.

   Include the creative-initiative paragraph from the authoring section in the main skill itself. Its optional route can say: “For illustrations when choosing or improving a method, see references/creative-practice-examples.md.” Reading that reference is optional, with no startup or per-exchange requirement. Keep Director calibration in ordinary guidance rather than add an initializer framework, creativity settings schema, reflection hook, or innovation workflow.

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

   Validate the public files, establish safe writer ownership, verify browser reads/submissions, establish a working input wait and leave it standing before setup is reported complete, and check native checkpoint activation when available. No automatic checkpoint hook installation silently replaces other hooks or bypasses normal host trust.


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

    Consider the usefulness of the writer's chosen methods within the existing scene observations. Tool count, novelty, or visible self-assessment is not a success criterion; a simple approach that sustains good play and continuity is valid. Do not add required simulations, an invention quota, or an extra reflection stage to demonstrate initiative.

    Completion requires the mechanical checks and actual evidence appropriate to the support claims. An unperformed host/creative observation stays “not run” or “inconclusive”; it is not converted into a pass by source inspection. Fix demonstrated problems and update affected documentation before claiming the initial package works.
