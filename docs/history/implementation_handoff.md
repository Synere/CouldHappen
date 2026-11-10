# CouldHappen implementation handoff

> Application implementation began after this original handoff. For open work and the next-session entry point, read the [issues register](../issues.md) and [AGENTS.md](../../AGENTS.md). The state statements below preserve the design-to-implementation handoff as it existed before application work.

* **Date:** 2026-11-04 (Asia/Manila)
* **State:** All design sections approved; predecessor reconciliation complete; final destination saved; focused creative-initiative amendment approved and applied.
* **Authoritative design:** [CouldHappen](../designs/couldhappen.md).
* **Implementation state:** Not started. This handoff and the documentation organization are documentation work.

## Read in this order

1. [Product context](../../PRODUCT.md) and the design's [Overview](../designs/couldhappen.md#overview), [Goals](../designs/couldhappen.md#goals), and [Non-Goals](../designs/couldhappen.md#non-goals).
2. Read the design's [creative-initiative principle](../designs/couldhappen.md#creative-initiative), then its [Technical Plan](../designs/couldhappen.md#technical-plan-architecture), then its [Detailed Implementation](../designs/couldhappen.md#alternatives-and-implementation-plan). The latter contains the ordered 12-step file inventory, public formats, commands, package pins, host examples, and validation obligations.
3. [Predecessor reconciliation](planning/design_reconciliation.md) for retained requirements, explicit changes, and additions. Use the [technical decision record](planning/technical_plan_decisions.md) only when the rationale for a settled choice matters.
4. [Visual direction/provenance](../designs/impeccable_direction_notes.md), the actual [selected Woven PNG](../designs/woven/woven.png), and [selection record](../designs/woven/direction-selection.json) before frontend work.
5. [Documentation index](../README.md) for targeted research and historical evidence. The [completed EGM draft handoff](planning/egm_draft_handoff.md) is history; it is not an instruction to restart drafting.

## Decisions to carry into implementation

* The existing agent owns model calls, tools, permissions, sessions, and optional delegation. The package supplies editable files, skill guidance, and small local helpers.
* The main writer skill establishes creative initiative as part of its baseline role, with freedom of method and responsibility for outcomes. Deliberate simplicity is valid; there is no required mechanic, innovation quota, or reflection schedule. The [examples reference](../designs/creative-practice-examples.md) is optional and should become the planned skill's `references/creative-practice-examples.md`, linked only as useful guidance. Director preferences can calibrate the experience through ordinary conversation; a separate initializer is not required.
* The core skill is harness-agnostic and asks the agent to establish actual capabilities. Named-host setup/hook examples remain separate.
* Use editable Python helpers and a client-side Svelte/Vite interface, ordinarily running live with HMR. The browser periodically reads saved snapshots; the agent's serviced local input wait is separate.
* Human and writer entries share Story Markdown; Director has its own log. IDs, roles, boundaries, and human pending/addressed/deferred metadata are public conventions. Private world records stay freeform.
* Direct log edits use a writer-requested, acknowledged browser-write pause. Prose-production blocking is separate and also writer-controlled.
* Undo normally continues in the current session, retaining rejection as feedback while withdrawing its fictional authority. Reconcile pending/running work, preserve applicable guidance and useful improvements by default, ask a new Director question, and wait.
* Small understood mechanical failures may be repaired quietly across helper code, mechanics, records, and affected prose. Material failures/uncertainty are explained; this does not authorize arbitrary creative rewriting.
* Checkpoints are meaningful writer choices, checked at deliberate closure and actual supported host completion. No interval or per-response commit policy is selected.
* Validate Codex interactive CLI first, then Claude Code interactive CLI, plus Pi's native OpenRouter route with a human-selected model. These are targets, not compatibility certifications.
* Use supplied card PNG portraits for the short scene and include a real fresh-context handoff. Story image generation, browser Stop, full mystery arc, and branching-history UI remain deferred.

## Start an authorized implementation task

Follow the design's implementation sequence. Inspect the current tree before creating files: the root README, documentation indexes, final design, and this handoff now exist. Extend them rather than replacing them with a blank scaffold. Operational helper/frontend files, manifests, logs, and writer skill described in the plan have not been created.

Preserve the documentation layout and links. The final plan's checkpoint exclusions cover the historical documentation groups. Keep `PRODUCT.md` at the root for the existing visual-tool context.

Use the exact planned dependency versions as a checked baseline and generate the lockfile during implementation. Metadata/version observations dated 2026-11-04 are not evidence that dependencies were installed or builds passed. If actual compatibility checks fail, explain and correct the concrete issue rather than blindly switching everything to latest.

Existing `.codex/hooks.json` contains Impeccable design hooks. Preserve it. Future fiction checkpoint examples are separate and must be merged/activated only in their intended reference-play setup, with ordinary host trust. Merely writing a configuration does not establish activation.

Actual later UI work follows the applicable installed skills and existing authorizations. The selected Woven image is preserved; the recorded later comp-led composition stage is not discharged by finalizing this design.

## Evidence still needed

No application story loop, native checkpoint enforcement, OpenRouter pairing, Undo, browser suite, or fresh-context continuation has been demonstrated. The prior Goldfish artifacts are concept reviews. A fresh EGM review of the overall design remains a separate recommendation and has not run. The author-approved initiative amendment needs no additional review gate or restarted brainstorming cycle.

Actual scene prompt/cards and account/model access are later validation inputs. Use synthetic temporary fixtures for mechanical tests without pretending they are supplied scene assets. Assess resulting fiction and preferences after a genuinely fresh session, not just file existence.

## Reference conventions and immediate next step

Treat non-link file paths as relative to the workspace root; resolve Markdown links relative to their containing document. The approved design is authoritative, while historical notes and reviewed inputs describe earlier decisions or observations. When an authorized implementation task starts, begin at step 1 of the design's Detailed Implementation sequence; the application files are still unimplemented.

The former-root-path table in the documentation index is the lookup for historical filenames. It does not recreate deleted paths. Old chat/IDE references to removed forwarding files can no longer open directly; use the canonical locations recorded in that table.

## Provenance and path compatibility

The [documentation index](../README.md) maps former root names to canonical documents. The forwarding files have been removed; use the canonical links. [Archive notes](archive/README.md) identify the byte-exact pre-organization ZIP and original reviewed-input hash.

The review files retain their `goldfish_reviews/` locations with document references normalized; byte-exact originals remain in the ZIP. Captured sources under `.research/reference-sources/` and visual provenance under `.impeccable/` remain unchanged. Historical line numbers and SHA receipts identify the original observations, not the current normalized copies, and do not override the approved design.
