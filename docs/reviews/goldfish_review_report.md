# Goldfish Review Report

> Historical concept review. Current scope and implementation decisions are in the [approved design](../designs/couldhappen.md); start a future implementation session with the [handoff](../history/implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../history/archive/README.md).

**Target:** Reviewed brainstorming-notes snapshot (`goldfish_reviews/inputs/brainstorming_notes.md`, kept locally, not published), lines 1–294. The live [brainstorming notes](../history/planning/brainstorming_notes.md) continue tracking discussion after review.

**Reviewed input SHA-256:** `4E6D24F394032B9AA2846423ABB9885F20334654C76883392589DFEDA664ACF3`. The root agent preserved this byte-identical snapshot before advancing the live notes and independently read all six original reports. This verifies the input/report artifacts, not each child's hidden tool trace.

**Mode:** BRAINSTORM. **Date:** 2026-11-03 (Asia/Manila). **Status:** Six reviews completed; reviewed working synthesis awaiting user iteration. This is concept critique, not a formal design audit, implementation approval, or compatibility certification.

## Reviewer status and reported reading receipts

All six native reviewers completed and wrote their own findings. The synthesizer read all six actual artifacts before compiling this report. All recommendations remain proposals unless independently recorded as accepted in the primary target.

Reading keys below resolve to these project files under `the repository root`:

- **N:** brainstorming_notes.md at review time (`goldfish_reviews/inputs/brainstorming_notes.md`, kept locally, not published), 294 lines.
- **B:** [browser_handoff_research.md](../research/browser_handoff_research.md), 83 lines.
- **H:** [host_compatibility_notes.md](../research/host_compatibility_notes.md), 85 lines.
- **I:** [prior_imagery_findings.md](../research/prior_imagery_findings.md), 41 lines.
- **C:** [carryover_audit.md](../research/carryover_audit.md), 89 lines.

Every persona path was verified in the installed bundle, `EGM plugin 0.1.0: agents/`, before dispatch. Each reviewer reports reading its complete persona and every assigned document in full, supplementing truncated output where necessary. No persona requires an additional document standard in BRAINSTORM mode; REVIEW-only standards were not imposed.

| Reviewer | Installed persona | BRAINSTORM lens | Reported full project reads | Status / original findings |
| --- | --- | --- | --- | --- |
| `egm-design` | `design_critic.md` | Cost, architecture, resource limits | N, B, H | Completed (`goldfish_reviews/design.md`, kept locally, not published): 6 Major |
| `egm-codebase-details` | `codebase_details.md` | Local observability and debugging | N, B, H, C | Completed (`goldfish_reviews/codebase_details.md`, kept locally, not published): 4 Major, 1 Nit |
| `egm-zoom-out` | `zoom_out.md` | YAGNI, reuse, code minimization | N, B, H | Completed (`goldfish_reviews/zoom_out.md`, kept locally, not published): 4 Major, 1 Nit |
| `egm-comprehension` | `comprehension.md` | UX, ergonomics, cognitive overhead | N, I, C | Completed (`goldfish_reviews/comprehension.md`, kept locally, not published): 5 Major, 1 Nit |
| `egm-implementation-readiness` | `implementation_readiness.md` | Migration, compatibility, rollout/rollback | N, H, C | Completed (`goldfish_reviews/implementation_readiness.md`, kept locally, not published): 3 Major, 1 Nit |
| `egm-structural` | `structural.md` | Maintenance, coupling, long-term debt | N, B, H, I | Completed (`goldfish_reviews/structural.md`, kept locally, not published): 5 Major |

The zoom-out reviewer also reports scoped current-project reuse searches and read-only inspection of the cited local Impeccable source snapshot: `CouldHappen/.research/reference-sources/impeccable/crates/context/src/serve_question.rs`, lines 1311–1405, and `skill/reference/live.md`, lines 13–30. It found reference patterns, not an existing story implementation to reuse wholesale. It reports that its first broad text search also returned current-project carryover/imagery excerpts. No reviewer reports reading MightHappen source files during this review.

## Execution, isolation, and evidence limits

Four total concurrent slots included the root and synthesizer, leaving two reviewer slots. The six lenses therefore ran in three waves: design + codebase-details; zoom-out + comprehension; implementation-readiness + structural. Each pair ran concurrently. Each later wave received the original target and its explicit supporting list, without earlier reports, synthesis, leading findings, parent conversation, or private reasoning.

Every reviewer was launched through native `collaboration.spawn_agent` with `fork_turns: "none"`, without a model override. Actual native completion messages were received for all six before synthesis. No reviewer needed a retry; none is marked not run. No delegation/tool failure prevented a review. Some document-read outputs were initially truncated; the reviewers' receipts describe supplementary reads. This was not counted as a clean read without their reported recovery.

The available orchestration interface exposes launch arguments, task status, messages, and final reports; it does not expose each child's full tool-call trace. Full-read statements above are **reviewer-reported receipts**, supported by the delivered artifacts, not a claim that the synthesizer independently observed every child read. Fresh turns do not isolate the shared filesystem or prove exclusion of host/project instruction files. No separate instruction-exclusion probe was run. Reviewers were explicitly prohibited from reading each other's reports, hidden chats/memory, or credentials, and report complying. Only their own findings files were authorized writes; inputs and implementation remained read-only.

The installed synthesizer persona, Codex integration, and brainstorm skill were read. The primary target records the user's explicit readiness authorization. Support notes contain earlier statements that review had not yet been approved; those are historical relative to the target's final authorization and this run. Their evidence limits still apply.

The synthesizer compared SHA-256 hashes of N, B, H, I, and C before reviewer dispatch and after writing the synthesis. All five inputs were unchanged. The brief's required title, author/date fields, and five section headings were also checked after writing.

The research establishes inspected browser-handoff precedent and user-reported Claude Code/Codex experience. It does not establish this workspace's repeated loop, hook enforcement, interruption behavior, OpenRouter pairing, or fresh-context literary continuity. No implementation, installation, live provider call, story image generation, or actual Impeccable pass was performed for this review.

## Prioritized findings

No reviewer established a concept-level Blocker. The 27 Major and 4 Nit source findings overlap; the synthesis below groups them into **9 Major concerns and 2 Nits**. These are risks and decision questions, often already acknowledged by the target. Counts are not votes or demonstrated defects. Proposed outcomes below have not become accepted user requirements, schemas, locks, or frameworks through repetition.

### 1. Public log saving can lose or replay human input — Major

**Original attribution:** design §1; codebase-details §2; zoom-out §1; comprehension §5; structural §1. Migration §2 adds compatibility concerns.

**Affected scope:** N, “Shared public conversation logs,” lines 158–173; “Prose display,” lines 142–156; B, lines 55–63.

A browser append and a writer replacement based on an older read can erase one another. Watching file changes alone cannot distinguish new human input, writer prose, an authorized revision, or a partial save. This is a real overlap question even with one human. Retrospective repair would impose costs on both writing and trust.

**Strongest counterargument:** Ordinary turn-taking is slow and cooperative. A readable shared log plus clear guidance may need little machinery. The risk does not prove that shared logs should be abandoned or that all edits must use one native tool.

**Proposal for alignment:** Preserve identifiable human submissions and avoid silent loss under the concurrency actually supported. Define the meaning of a saved entry and how ordinary editing tools observe a small cooperative agreement. Exact identities, save checks, syntax, and conflict handling belong to later design.

**Smaller alternatives:** Cooperative safe-save checks, short exclusive historical-edit intervals, or serialization of particular writes. A one-outstanding-story-input restriction is a reviewer proposal requiring discussion. A separate tiny browser inbox is a comparison option that changes the working shared-log proposal; it was not selected. Append-first authoring is another proposal, not an accepted restriction on editing methods.

### 2. Coarse Undo must reconcile pending inputs and running consumers — Major

**Original attribution:** design §3; codebase-details §3; zoom-out §2; comprehension §§2–3; implementation-readiness §1; structural §2.

**Affected scope:** N, “Git checkpoints and Undo,” lines 193–219, and input recognition at 168–173; H, lines 69–75.

A correct Git restore can leave a stale helper cursor, queued story entry, browser copy, production signal, or running writer. Old input may appear new, or a late save may restore withdrawn material. The latest rejection and preferences may be newer than the checkpoint. These failures are separate from the user's accepted limitation on restoration precision.

**Strongest counterargument:** Undo is a Director conversation carried out by the writer. Ordinary Git inspection, a quiet boundary, retained guidance, and a reload may suffice. No exact interaction rollback engine is justified.

**Proposal for alignment:** Retained Director guidance, an understandable restore result, and the accepted wait for new Director direction must survive the actual restore. Previously queued story input must not bypass that wait. Re-establish the restored view for relevant consumers before claiming the operation complete. Explain which prose, notes, assets, uncommitted changes, or unrelated improvements the chosen history can actually recover; distinguish reconstruction from historical restoration.

**Smaller alternative:** Assisted writer-led restoration at a quiet boundary, preserving the relevant Director discussion and reloading/relaunching the helper if needed. A fresh compatible session is a fallback to evaluate if rejected material keeps influencing the live session. No mandatory session reset, per-response commit, browser Stop, branching UI, or automatic transaction journal is selected.

### 3. Browser availability can misrepresent writer availability — Major

**Original attribution:** codebase-details §1; comprehension §1; design §2; structural, proportionality discussion.

**Affected scope:** N, lines 79–80, 175–191, 231–238; H, lines 39–55 and 79–80; C, lines 65–71.

A healthy helper does not prove the host is servicing input. A saved response can still animate after the writer has moved on. A stale writer-declared block may persist after interruption. An unanswered entry should not force the human to guess whether to resubmit.

**Strongest counterargument:** The existing host is already visible and supplies useful diagnostics. Adding presence inference or a supervisor could be less reliable than directing the human back to that host.

**Proposal for alignment:** Use status that states what its source actually knows, retain unanswered saved input, and give an understandable return-to-host/reopen action. Distinguish local persistence, helper reachability, last declared writer activity, and unknown writer state. Avoid implying immediate interruption or automatic recovery.

**Smaller alternative:** Save/error acknowledgment, a last-reported status, and plain instructions to inspect or resume the existing host. No heartbeat model calls, custom dashboard, timeout-based claim of failure, or automatic retry controller follows. Exact stale-block clearing remains open.

### 4. Separate conversations need understandable instruction timing — Major

**Original attribution:** comprehension §2; design §1; codebase-details §2; zoom-out §2.

**Affected scope:** N, lines 160–173, 179–191, 199–201; C, lines 25–31.

A Director preference or Undo instruction can arrive while prose is being composed or while saved prose animates. Submission alone cannot establish that the writer read it or that it changes the in-flight passage. Additional ordinary story submissions during production are explicitly unsettled.

**Strongest counterargument:** Natural discussion and a useful check before continuation may handle this without a scheduler or cross-log transactions.

**Proposal for alignment:** Clarify when a received instruction is acknowledged and what it affects, preserving the writer's discretion to block Director submissions. Decide what happens to additional player input during an in-flight reply. Open Director input must not imply immediate interruption. The current review does not choose a mandatory lock or queue policy.

**Smaller alternative:** Boundary-based reading and acknowledgment guidance plus one explanatory browser sentence. One outstanding player submission is a possible narrowing, not an accepted decision. A mandatory Director block would contradict the recorded writer discretion.

### 5. A successful live scene cannot establish fresh-context continuation — Major

**Original attribution:** design §5; codebase-details §4; zoom-out §3; comprehension §4; structural §5; implementation-readiness §2.

**Affected scope:** N, lines 65–72, 102–106, 223–229; H, lines 69–83.

The live context can supply missing facts while apparently durable notes go untested. After the writer reorganizes records, a fresh session may follow stale instructions or reconstruct the world from the whole growing transcript. That would miss the required workspace-knowledge outcome and increase reading cost.

**Strongest counterargument:** A maintained starting note and writer-chosen index can be enough. A fixed database, record schema, retrieval service, or automatic preference injection would constrain methods without proving continuity.

**Proposal for alignment:** Preserve a discoverable reentry route after reorganization. Observe a genuinely fresh continuation before claiming that capability, checking resulting fiction against established/disclosed material and retained Director guidance. File or commit existence is insufficient.

**Smaller alternative:** A short start-here pointer to writer-managed notes and selected previous prose; one separate early fresh-session observation using the accepted scene, an applicable preference/correction, and a disclosure boundary. Whether this observation belongs inside or beside the first scene remains open. No larger mystery arc or exhaustive model benchmark is required now.

### 6. Checkpoint enforcement depends on an active, reachable host boundary — Major

**Original attribution:** design §4; implementation-readiness §3; structural §§3–4; zoom-out §5.

**Affected scope:** N, lines 69–71, 197–211; H, lines 39–49, 57–63, 77–83.

A host Stop hook may not run during several story exchanges in an ongoing tool-wait loop. A changed or restored hook file may await host trust and be inactive. A dirty-tree check before every wait could silently replace writer-chosen commit granularity with a commit-per-response policy.

**Strongest counterargument:** A small concrete check at a useful supported boundary can suffice. The source notes already acknowledge these limits; no general enforcement framework is implied.

**Proposal for alignment:** Define the intended checkpoint assurance and investigate a reachable host/surface boundary without promising semantic completeness or precise interaction snapshots. Reopening and hook edits must respect normal activation/trust behavior. A fallback must be described honestly rather than called enforced support.

**Smaller alternative:** Thin host guidance and a stable mechanical check, with activation/reopen instructions. A close/pause boundary or limited helper check is worth comparing. Neither is selected; the writer continues to choose meaningful commit times.

### 7. Editable infrastructure can invalidate its own interoperability and recovery — Major

**Original attribution:** implementation-readiness §2; structural §3; comprehension §4; zoom-out §5.

**Affected scope:** N, lines 65–69, 77, 128, 215–238; H, lines 47–49; I, lines 35–41.

Private note reorganization and changes to public log interpretation have different effects. An old browser/helper may remain active after a format change or restore. Restoring story files may also revert useful helper code or trust definitions. A directory can remain editable while its components quietly disagree.

**Strongest counterargument:** One trusted writer can update a small set of materials and restart helpers. General self-migration, semantic versioning, or an immutable core would be premature.

**Proposal for alignment:** Keep the current public agreement and knowledge entry points discoverable, and account for relevant running readers and infrastructure changes during customization or recovery. This constrains interoperability outcomes, not the writer's private schema or choice of authoring tools.

**Smaller alternatives:** A short workspace map and deliberate maintenance/reopen boundaries for public-convention changes; inspect relevant Git differences before restoration. Some reviewers favor a stable public convention during play. That staging proposal remains unresolved and does not prohibit ordinary private-method or presentation changes.

### 8. Host comparisons can grow into unintended integration ownership — Major

**Original attribution:** design §6; zoom-out §4; structural §4; implementation-readiness §3; codebase-details, assumptions.

**Affected scope:** N, lines 13–17, 40, 97–100, 288–290; H, lines 15–33, 65–85.

Host brand, CLI/desktop surface, version, hook trust, launcher/provider route, and model behavior are distinct variables. Six candidates should not become six promised integrations or an exhaustive test platform. The smallest OpenRouter route may overlap a required host; a native third-host route might still be simpler than a launcher.

**Strongest counterargument:** Shared files and a helper may leave little host-specific code. Claude Code/Codex and an existing-host OpenRouter route are accepted requirements and cannot be removed in the name of minimalism.

**Proposal for alignment:** Retain required support, compare actual setup and lifecycle costs, name the configurations for which evidence exists, and keep candidates distinct from supported routes. Model choice does not imply equal reliability across the catalog. Host/model/credential/session ownership stays with the existing host.

**Smaller alternative:** One common public agreement/helper with concise required-host guidance, plus one suitable existing OpenRouter route. Investigate other candidates when they offer an observed advantage. No provider controller, generalized adapter registry, or universal capability checker is selected.

### 9. Local waiting does not establish negligible idle cost — Major

**Original attribution:** design §2 (Major); codebase-details §5 (Nit); zoom-out §4, host assumptions.

**Affected scope:** N, lines 120–124; B, lines 22–26 and 38–42; H, lines 53–55 and 79–80.

Filesystem polling can be local while bounded wait returns still require model-serviced renewal. The cost that matters is host/model activity over reading and idle periods, not the number of local file checks. Normal-save animation does not reduce composition latency.

**Strongest counterargument and severity disagreement:** The design reviewer treats idle overhead as Major; the debugging reviewer treats it as a Nit requiring observation before instrumentation. Existing long-lived tools or event delivery may already make it minor. The synthesis keeps it Major because it could change the ordinary browser experience, without asserting that the cost is currently high.

**Smaller proposal:** One quiet existing-host wait, ordinary host usage observations, and an honest exceptional-expiration/resume path. No inherited numerical budgets, provider metering, watchdog model, or custom session daemon is justified by this review.

### 10. Reading states need attention in the scheduled visual pass — Nit

**Original attribution:** comprehension §6; I, historical reading considerations and current direction.

**Affected scope:** N, lines 148–156 and 191; I, lines 17, 27, 33–41.

Animation can delay reading already-saved prose; replacement/Undo can move the viewport; a cast panel can consume narrow-screen reading space. These are design questions within the accepted direction, not grounds to remove the PNG cast panel or import earlier styling.

**Counterargument and smaller proposal:** Keep the agreed browser reveal and assess immediate-reveal convenience, reduced motion, reading-position preservation, revision display, and narrow-screen cast access in the actual comp-led Impeccable pass. These are reviewer proposals. No visual theme, framework, elaborate diff viewer, or media pipeline is selected. No Accept/Revise or browser Stop is added.

### 11. Future template updating need not be automatic — Nit

**Original attribution:** implementation-readiness §4; zoom-out §5.

**Affected scope:** N, lines 65–69, 77, 288–290.

A future blind template replacement could erase local methods or mismatch code and records. There is no installed base or accepted updater requirement now.

**Counterargument and smaller proposal:** A copy-once template with later explicit Git review/merge may be enough. Defer update tooling until an actual update scenario needs it. This proposal has not become a delivery decision.

## Disagreements, alternatives, and decisions still open

The reviewers share concerns but do not demonstrate one best mechanism. Preserve these differences:

- **Concurrent input:** append-first cooperation, a short edit interval, safe-save conflict checks, serialized story acceptance, and a separate inbox are alternatives. A one-outstanding-player-input rule may shrink the implementation but changes the available interaction. It is not selected. Director blocking remains the writer's choice.
- **Recovery assistance:** several reviewers favor manual quiet-boundary Undo/reload; others stress inspectable input identity and retained state. These can coexist, but the acceptable human assistance and queued-input disposition require alignment. Automatic coordination is not accepted.
- **Public convention changes:** migration and maintenance favor deliberate maintenance/reopen boundaries; writer editability remains accepted. No rule has yet divided ordinary customization from incompatible changes or chosen a stable-core policy.
- **Evidence staging:** all relevant lenses favor an early fresh-context observation. The accepted scene stays intact; placing restart inside it or in a companion check remains unresolved.
- **Host route:** thin shared guidance is favored, but no first host, version/surface, OpenRouter integration, launcher, or model has won. The review supplies no executed comparison.
- **Cost priority:** idle overhead is Major to design and Nit to debugging. Observe before choosing instrumentation or session machinery.

Accepted user choices are preserved in [concepts_brief.md](../history/planning/concepts_brief.md), separate from these proposals. The next discussion can address ordinary additional player submissions during an in-flight reply, which affects the concurrency and instruction-timing questions without choosing a schema prematurely. The actual comp-led Impeccable exploration remains scheduled and outstanding. User approval of the working brief and the later EGM handoff are still required; formal drafting and implementation have not started.
