# CouldHappen final design reconciliation

* **Author:** Synere
* **Date:** 2026-11-04 (Asia/Manila)
* **Scope:** EGM predecessor-context reconciliation after approval of Detailed Implementation.
* **Result:** No unresolved contradictions with the predecessor brief as amended by the author's explicit later decisions. Final destination confirmed as `docs/designs/couldhappen.md`.

## Contradictions

No unresolved contradiction requires another author decision.

One settled requirement was explicitly expanded during drafting:

| Earlier requirement | Approved draft | Authority and limits |
| --- | --- | --- |
| The [concept brief](concepts_brief.md#analysis) says: “Established prose changes only on Director instruction.” | The [authoring policy](../../designs/couldhappen.md#authoring-imports-private-records-and-helper-repair) says: “The author gives standing permission for proportionate corrections caused by identified technical/mechanical failures.” | The author explicitly allowed quiet correction of small understood helper failures, including affected mechanics and prose, then approved the Technical Plan and Detailed Implementation. This is standing Director authorization, not permission for arbitrary creative rewriting. Material consequences/uncertainty are explained; substantial withdrawal of fiction requires reconciliation and new direction. |

This is an authorized change, not a reason to silently restore the older rule or ask for the same permission again. The same clarification is carried into the current product context.

## Sources and authority

Re-read the [concept brief](concepts_brief.md) and [brainstorming notes](brainstorming_notes.md), applying later dated resolutions over earlier pending statements. Compared their requirements with the unchanged approved [design draft](../../designs/couldhappen.md). Cross-checked accepted [carry-over behaviors](../../research/carryover_audit.md), [product context](../../../PRODUCT.md), and [visual provenance](../../designs/impeccable_direction_notes.md). Checked the scope and evidence limits of the [concept reviews](../../reviews/goldfish_review_report.md), [browser research](../../research/browser_handoff_research.md), [host notes](../../research/host_compatibility_notes.md), and [portrait findings](../../research/prior_imagery_findings.md).

The [draft handoff](egm_draft_handoff.md) defines a design-only session. Historical approvals in MightHappen are not authority for this project. The [technical decision record](technical_plan_decisions.md) preserves the drafting choices and source research; the author's subsequent section approvals establish the current design.

This reconciliation compares requirements and recorded decisions. It is not an independent Goldfish design review, a runtime compatibility test, or evidence that the writer maintains adequate narrative knowledge.

## Retained requirements

| Predecessor requirement | Where the approved design carries it |
| --- | --- |
| Existing agent owns execution/model/tools/permissions. | Technical Plan ownership boundaries and capability-driven skill; Python handles local files/controls/waiting only. No workspace model client or session supervisor. |
| Shared human/writer Story log and separate Director discussion. | Canonical Markdown logs and role/entry metadata. No separate inbox, second manuscript, or publication-acceptance ledger. |
| Writer authors the whole cast and supports believable influence. | Goals, writing reference, free character creation, and evaluation of actual resulting fiction. Cards/portraits are not prerequisites for inventing characters. |
| Ordinary Director discussion does not advance fiction. | Writing loop and recovery guidance distinguish conversation, preferences, hypothetical ideas, and explicit permission to continue/revise. |
| Durable, discoverable world knowledge; free private organization. | Stable reentry index and writer-managed records; fresh-context observation uses the files without old host chat or a special test recap. No mandatory world schema or reasoning archive. |
| Imported sources/portraits preserved; cards interpreted as source material. | Private originals and extracted records; explicit conflict clarification; public portrait preparation/disclosure separated from import. Removing public PNG metadata does not replace or restyle the preserved original. |
| Normal saves, browser reveal, writer-controlled prose block. | Saved-entry presentation, separate production/edit controls, and reduced-motion/reading-position handling. Private note work and reveal animation do not automatically block submissions. |
| Meaningful writer-chosen Git checkpoints and honest Undo. | Deliberate-close/supported-completion check, actual history inspection, retained guidance/improvements, quiet boundary, assumption/input reconciliation, and waiting for new Director direction. No per-response checkpoint mandate or exact-restore promise. |
| Claude Code, Codex, and an existing OpenRouter route. | Codex CLI then Claude Code CLI, plus Pi/OpenRouter. Core guidance remains capability-based; reference setup and observed support are separate. |
| Selected Woven direction and limited first demonstration. | Woven image/provenance preserved; supplied card PNGs, short scene, Director and Undo. Generated story images, browser Stop, full mystery arc, and branching UI remain deferred. Future image-tool guidance stays in scope. |
| No unsupported evidence claims. | Native hook activation, real waiting/renewals, coherent Undo, fresh-context fiction, and model/surface compatibility remain later observations. Documentation, package inspection, a running helper, or a clean tree are not substituted for those outcomes. |

The selected direction remains the approved original comp. The predecessor's later comp-led composition stage—original selected image plus two same-direction organizational variations when that stage is authorized—remains governed by the handoff/visual record and applicable installed UI workflow. This reconciliation does not run or discharge that stage.

## Resolutions of questions already raised by the brief

These are recorded answers to open predecessor questions, rather than contradictions:

| Open question | Approved resolution |
| --- | --- |
| How can browser saves coexist with ordinary writer edits? | T1: close browser acceptance, finish accepted saves, acknowledge, then reread/edit/release. Cooperative editing and interrupted-pause recovery are explicit limits. |
| How should already-saved inputs be ordered? | T2: interpret both logs together using writer judgment; explain consequential conflicts/deferrals. |
| How should input identity and handled state work? | T5–T6: stable Markdown entry IDs/roles/boundaries, with pending/addressed/deferred on human entries. A save receipt does not mean applied. |
| What does Undo do to live context and pending work? | T3: continue in the current session, remembering rejection as feedback. Establish a quiet boundary, reconcile files/assumptions/input, and wait behind a new Director question. |
| How can public conventions evolve? | T4: pause/reopen affected components for incompatible changes. Ordinary cast/private-method changes do not require a migration. |
| What checkpoint boundary should be enforced? | T7: deliberate closure and reachable active host completion; no interval during continuous play. Missing/inactive/error cases have explicitly reduced assurance. |
| Where should fresh-context continuation be observed? | T8: within the short scene after real exchanges and applicable Director guidance. |
| Which surfaces and OpenRouter route should be demonstrated? | T9–T10: Codex interactive CLI, then Claude Code interactive CLI, plus Pi's native OpenRouter route. Other investigated routes are not declared impossible or automatically supported. |

## Material additions made during drafting

The brief deliberately left runtime, transport, frontend, public formats, and implementation sequencing open. The rows below identify architectural/interface/dependency commitments added by the draft. They have been covered by explicit decisions or approval of the completed design sections; none requires fresh permission merely because it was absent from the brief.

| Addition | Architectural/interface/dependency effect | Recorded approval |
| --- | --- | --- |
| Strict capability-driven core skill | Agent establishes actual capabilities; harness-brand examples and native hook wiring stay in separate reference materials. | Explicit author clarification inspired by Impeccable, then Technical Plan approval. |
| Agent-managed setup and prerequisite installation | Setup can install/check Python, Node/npm, and Git as permitted, install locked frontend dependencies, and start/reuse the actual local services. | Explicit author instructions about “set up” and installation, then Technical Plan/Detailed Implementation approval. |
| Editable Python loopback helper | Standard-library-oriented source provides file access, controls, and waiting; additional writer helpers may use other languages. | T11–T12 and section approvals. |
| Svelte/Vite live frontend | Node/npm and two local serving processes during ordinary play; retained source, HMR, optional build checks, and deliberate draft/anchor handling. | T13–T14 and section approvals. |
| Periodic browser snapshot reads | Roughly one-second active polling with revision checks; separate from the agent's local input wait. | T15 and section approvals. |
| Concrete public file/control contract | Entry delimiters/escaping, stable UUIDs, cast/work JSON, acknowledged edit tokens, startup closure, durable post-Undo question, and compatible-generation checks. | Approved Technical Plan and Detailed Implementation. |
| Concrete HTTP and retry contract | Narrow snapshot/submission/asset routes, identical-ID retry handling, retained uncertain drafts, explicit errors, and a 256 KiB submitted-body limit. | Detailed Implementation approval. |
| Bounded private import/public portrait handling | V1/V2/V3 PNG/JSON source handling, content-addressed originals, public PNG metadata removal, 32 MiB source and 8 MiB decoded-metadata limits. | Detailed Implementation approval, preserving the brief's source/portrait/disclosure requirements. |
| Browser Markdown conversion and sanitization | Marked 18.1.3 and DOMPurify 3.4.17; restricted rendered content rather than executing card/prose HTML. | Detailed Implementation approval. |
| Reproducible frontend/checking/testing dependencies | Svelte 5.57.3, Vite 8.3.5, plugin 7.3.1, svelte-check 4.7.8, TypeScript 6.0.3 for checking, and Playwright 1.64.1, with a generated lockfile during implementation. | Detailed Implementation approval. Runtime/version compatibility still needs the planned checks. |
| Narrow local exposure and draft persistence | Loopback servers, restricted public asset/source access, separate writer control secret, and same-tab workspace/channel session-storage drafts. | Technical Plan and Detailed Implementation approval. These are local interoperability controls, not a new account system or general permission platform. |
| Concrete reference hooks, checkpoint scope, file inventory, and tests | Separate native wrappers/extensions invoke one scoped check; explicit operating sources, planning/runtime exclusions, temporary-data tests, and observed creative/host validation. | Detailed Implementation approval. Active installation and runtime observations remain future implementation/validation work. |

## Documentation reconciliation and remaining work

Apply only documentation corrections already determined by author decisions:

* Record Detailed Implementation approval and completion of predecessor reconciliation.
* Replace stale “checkpoint boundary remains to be decided” wording with the selected closure/completion policy.
* Replace stale Pi-candidate wording with the selected Pi/OpenRouter reference, retaining other routes as comparisons.
* Update the current product context with the approved stack, setup model, in-scene fresh-context observation, and standing repair permission.
* Preserve the predecessor brief/brainstorm/research files as historical inputs rather than rewriting them to conceal later choices.

No application files, installations, active checkpoint wiring, model calls, or creative demonstrations are part of these documentation edits. Actual scene prompt/cards and account/model access are later validation inputs.

No existing design directory or sitemap was found before finalization. The author selected `docs/designs/couldhappen.md` and authorized documentation organization. The final design is saved there with relative links adjusted for the new layout. A documentation index, implementation handoff, and design sitemap identify the authoritative files. The author subsequently requested removal of the root forwarding notes; references now use canonical document locations. A byte-exact pre-organization archive preserves the prior artifacts and review provenance.

After final saving, recommend an independent EGM design review of the final document. Approval and this reconciliation do not substitute for that review or authorize application implementation.

## Approved post-finalization initiative clarification — 2026-11-04

The author clarified CouldHappen's purpose as an experiment in the creative practice of an empowered general-purpose coding agent, then explicitly authorized applying the proposal to the documentation. Existing design permission to develop private methods, helpers, and the UI is retained; the new emphasis makes useful initiative part of the main writer role.

The [creative-initiative principle](../../designs/couldhappen.md#creative-initiative) belongs in the main skill. [Optional examples](../../designs/creative-practice-examples.md) are planned for `references/creative-practice-examples.md`; they illustrate useful experimentation, deliberate simplicity, and discarding an unhelpful approach. They are not a feature checklist or prescribed architecture. Director preferences may calibrate the experience through ordinary conversation, without a new initializer mechanism.

The author accepted a focused wording amendment with a consistency check. No new EGM cycle or review prerequisite is introduced for this amendment. Architecture, public authority/interoperability boundaries, recoverability, and first-demonstration scope are retained. Evaluate chosen methods by their contribution to fiction, player experience, and continuity; neither artifact counts nor mandatory reflection reports establish success. Historical brief, review, draft, and ZIP artifacts remain historical records.
