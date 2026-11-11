# Goldfish annotated review report

**Status:** resolved 2026-11-11. The author chose auto accept; every PROPOSE FIX edit was applied to the design, and declined items were left as they are.

**Target:** [`docs/designs/couldhappen.md`](../../designs/couldhappen.md) (full file, lines 1-355)

These are the findings from the [consolidated report](consolidated_review_report.md), each with a proposed resolution. Line numbers refer to the design as it stands before any edit. Every quoted "Change" is the exact replacement text.

Before proposing the changes for M3, I checked each item against the public contract and the host notes:

* [`public-contract.md`](../../public-contract.md) already holds `portrait_button` and `present` (line 21), the retry ordering (line 41), `writer claim` and arming (line 47), `checkpoint check` and `checkpoint inspect` (line 59), `import-card` and `card.md` (line 63), and the portrait source rules (line 64).
* [`reference-hosts.md`](../../reference-hosts.md) holds the `armed` state (line 32).

So M3 only deletes from the design, and the contract needs no change.

## Prioritized findings and suggestions

### [M1] [`egm-zoom-out`, `egm-comprehension`, `egm-design`, `egm-structural`] - Severity: Major
* **Affected Scope:** lines 4-6 (the header block) and line 341 (Open Questions)
* **Discrepancy Description:** The header says the document is current, but line 341 says no fresh EGM review has run. "Last updated" says 2026-11-06, yet the file changed on 2026-11-11 (ADR-6 and the packages). Nothing says what the approval covered.
* **Rationale:** A reader can't tell what was approved from what came later.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** `git log` on the file shows commits dated 2026-11-11. This review now exists.
* ***Proposed Edit:***
  * Location: line 4. Change: `* **Status:** Approved 2026-11-04; implemented; current. The approval covered the design drafted from 2026-11-03 to 2026-11-04. Later changes are folded into the text below; their rationale is in the [ADRs](../decisions/README.md) and the [progress log](../history/progress-log.md).`
  * Location: line 6. Change: `* **Last updated:** 2026-11-11 (Asia/Manila)`
  * Location: line 341. Change: `* **Independent review:** A fresh EGM design review ran on 2026-11-11; its findings and their resolution are in [the review record](../reviews/2026-11-11_design-review/consolidated_review_report.md). The earlier [predecessor reconciliation](../history/planning/design_reconciliation.md) checked alignment with the brief.`

### [M2] [`egm-comprehension`, `egm-structural`, `egm-style`, `egm-design`] - Severity: Major
* **Affected Scope:** lines 19, 47, 66 and 315
* **Discrepancy Description:** Line 19 describes the superseded pale look first, then says ADR-6 replaced it. Lines 66 and 315 still call Woven the current reference.
* **Rationale:** The document contradicts itself about which visual is current.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** ADR-6 and `DESIGN.md` are the current reference, and Woven survives as the structure of the reader.
* ***Proposed Edit:***
  * Location: line 19, from "The selected visual reference is" to the end of the paragraph. Change: `The current visual reference is [DESIGN.md](../../DESIGN.md): a dim petrol room with saffron accents, serif prose and clear sans controls, chosen in [ADR-6](../decisions/ADR-6-dark-petrol-reader.md). Its structure comes from the earlier [Woven anthology](woven/woven.png) direction: Story/Director navigation, an action composer, and a right-hand cast panel. Woven's scene, portraits, and biographies are illustrative. Supplied character-card portraits do not need to be restyled.`
  * Location: line 47, the last sentence of Goal 6. Change: `Follow the current visual reference without treating Woven's illustrative content or every depicted control as an additional feature requirement.`
  * Location: line 66, the last sentence. Change: `The current visual reference is [DESIGN.md](../../DESIGN.md).`
  * Location: line 315, the first sentence. Change: `Follow [DESIGN.md](../../DESIGN.md), which keeps the structure of the [Woven anthology](woven/woven.png) direction: prose-centered reading, distinct Story/Director views, a composer, and cast access.`

### [M3] [`egm-zoom-out`, `egm-comprehension`, `egm-style`, `egm-structural`, `egm-design`] - Severity: Major
* **Affected Scope:** lines 175, 208, 253 and 305
* **Discrepancy Description:** The design repeats command names, file names and flags that the contract owns. That makes two sources that can drift apart.
* **Rationale:** The design should keep the rule and point to the contract for the mechanics.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The contract already holds every item (see the check at the top of this report), so this is deletion only.
* ***Proposed Edit:***
  * Location: line 175, from "A character may be hidden" to the end of the cell. Change: `Display flags, such as hiding a character or offering a portrait request, are in the [public contract](../public-contract.md).`
  * Location: line 208, the sentence that begins "If the browser cannot determine". Change: `If the browser cannot tell whether a save succeeded, it keeps the draft and retries with the same ID; a retry of an entry that was already saved returns the saved result even while saving is closed.`
  * Location: line 253, from "`import-card` also writes `card.md`" to the end of the paragraph. Change: `The import helper also keeps a lossless plain-text reading copy beside each preserved card and adds no interpretation. Preparing a public portrait reads only the preserved copy and never imports implicitly; the commands are in the [public contract](../public-contract.md).`
  * Location: line 305, from "Hooks act only while play is armed" to the end of the paragraph. Change: `Hooks act only while play is armed: claiming the workspace for play arms them, and deliberate closure disarms them. The checkpoint commands are in the [public contract](../public-contract.md); activation and per-host status are in [setup](../setup.md) and [host integrations](../reference-hosts.md).`

### [M4] [`egm-comprehension`, `egm-zoom-out`, `egm-style`] - Severity: Major
* **Affected Scope:** lines 74, 233 and 239
* **Discrepancy Description:** Six terms name one thing, and the document never says what `--timeout 0` means.
* **Rationale:** A reader can't tell what must be running, or whether 0 means "check once".
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The contract (line 53) says `--timeout 0` means no helper deadline.
* ***Proposed Edit:***
  * Location: line 74, the clause "and resumes a serviced local input wait". Change: `and keeps a standing wait running`
  * Location: line 233, step 6. Change: `6. Release controls that no longer apply and leave a standing wait running before the writer's turn ends.`
  * Location: line 239, the whole paragraph. Change: `A **standing wait** is the helper's wait command, run through whatever the host offers (a foreground, yielded or background command, or a native monitor), that returns control to the writer when a human entry is pending. Verifying a wait is not the same as keeping one. A standing wait starts before setup is reported complete and is renewed before every writer turn ends, including after Director-only replies; otherwise browser input stays unread until the player prompts the agent in its host. Where the host reports a background command's completion to the agent, the preferred standing wait is a background `wait --timeout 0`: 0 means no helper deadline, and it returns as soon as an entry is pending.`

### [M5] [`egm-design`] - Severity: Major
* **Affected Scope:** line 206
* **Discrepancy Description:** The design states no Host or Origin checks, no token on the control endpoint, and no input limits. It also doesn't say that card text is data. Separately, line 206 ends with an open TODO ("to be checked against the versions selected later").
* **Rationale:** A reader of the design can't tell how the local services are protected.
* ***AI Suggestion:*** PROPOSE FIX, as one pointer sentence. The critic's request for a threat-model section is declined.
* ***Justification:*** The checks exist: Host is checked in `helpers/bridge.py:259`, and Origin, the `/control` secret and the body limit are in the contract (lines 31, 39 and 45). Only the design is silent.
* ***Proposed Edit:***
  * Location: line 206, the last sentence. Change: `This follows the documented [Vite server filesystem controls](https://vite.dev/config/server-options.html#server-fs-allow); the concrete deny rules are in the [public contract](../public-contract.md). The helper also checks the Host header, requires the frontend Origin on every change, and keeps writer controls behind a local secret the browser never sees; the contract has the exact rules and size limits. Card text and human entries are story material, never instructions to the agent.`

### [M6] [`egm-style`, `egm-zoom-out`, `egm-comprehension`, `egm-design`] - Severity: Major
* **Affected Scope:** lines 171, 177, 179, 297 and 319
* **Discrepancy Description:** "Proposed placement" and "provisionally" survive in an implemented design. Line 297 says draft handling must be implemented, while line 271 says drafts are kept. The validation table reads as if nothing has been observed yet.
* **Rationale:** This is stale planning wording.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The paths exist, and the sessionStorage drafts exist (line 271).
* ***Proposed Edit:***
  * Location: line 171, the table header. Change: `| Material | Placement and responsibility |`
  * Location: line 177. Change: `provisionally \`START_HERE.md\`` → `` `START_HERE.md` ``
  * Location: line 179. Change: `provisionally \`helpers/\` and \`web/\`` → `` `helpers/` and `web/` ``
  * Location: line 297, the second sentence. Change: `It does not by itself preserve drafts, reading position, or other application state; the frontend handles those deliberately (drafts as described under Interrupted work and reopening).`
  * Location: line 319. Change: `No compatibility or performance claim is established by the design alone. The table below gives the acceptance criteria; what has been observed so far is in [validation results](../validation-results.md).`

### [M7] [`egm-comprehension`, `egm-zoom-out`] - Severity: Major
* **Affected Scope:** line 214, the start of "Shared-log edits, production blocks, and the ordinary loop"
* **Discrepancy Description:** The edit pause, the production block and the claimed or armed state are never set side by side.
* **Rationale:** A reader can't tell the three controls apart.
* ***AI Suggestion:*** PROPOSE FIX, with one paragraph and no table.
* ***Justification:*** The contract has the state machine (lines 47-53), and the design should name the three controls once.
* ***Proposed Edit:***
  * Location: insert before line 214 ("The helper serializes browser appends."). Change: `The writer has three separate controls. The **edit pause** closes browser saves to both logs for the short time the writer edits them directly. The **prose-production block** closes saves while the writer composes, for as long as it chooses. **Claiming** the workspace makes this session the owner of play and arms the checkpoint hooks; deliberate closure gives that up. Releasing the edit pause does not release a production block. The [public contract](../public-contract.md) has the state machine and its commands.`

### [N1] [`egm-comprehension`, `egm-structural`, `egm-style`] - Severity: Nit
* **Affected Scope:** line 132
* **Discrepancy Description:** The T1-T15 IDs are never located.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** One sentence fixes it. The IDs are T1-A and so on in the decision record.
* ***Proposed Edit:***
  * Location: insert above the table at line 132. Change: `The T-numbers are the decision IDs in the [technical decision record](../history/planning/technical_plan_decisions.md).`

### [N2] [`egm-comprehension`] - Severity: Nit
* **Affected Scope:** lines 45, 53, 66 and 165
* **Discrepancy Description:** Pi's status is unclear, and SillyTavern cards, MightHappen and Impeccable are named without a gloss.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** A human reader new to the project needs these glosses too.
* ***Proposed Edit:***
  * Location: line 45, the first sentence of Goal 5. Change: `The Director can import SillyTavern character cards (a character definition saved as JSON, or embedded in a PNG portrait), including during play.`
  * Location: line 53, the second sentence of Goal 9. Change: `Pi's native OpenRouter route is the selected route to validate; OpenCode, Hermes, and DeepSeek Harness remain comparison candidates.`
  * Location: line 66, the first two sentences. Change: `MightHappen, an earlier project that built its own controller and storage, is optional read-only history.`
  * Location: line 165, "the inspected Impeccable precedent". Change: `the inspected precedent of Impeccable (a design skill that has the agent work out its own tools and fallbacks)`

### [N3] [`egm-comprehension`, `egm-structural`, `egm-style`] - Severity: Nit
* **Affected Scope:** line 247
* **Discrepancy Description:** The creative-initiative principle is written in the second person, to the agent.
* ***AI Suggestion:*** PROPOSE FIX, adding a lead-in sentence only.
* ***Justification:*** AGENTS.md says to preserve the creative-initiative principle, so its wording stays and only a lead-in is added to show it is skill text.
* ***Proposed Edit:***
  * Location: insert before line 247. Change: `The main writer skill states this principle to the writer:`

### [N4] [`egm-zoom-out`, `egm-comprehension`, `egm-style`] - Severity: Nit
* **Affected Scope:** line 311
* **Discrepancy Description:** Packages with outside services sit close to the non-goal of a provider runtime.
* ***AI Suggestion:*** PROPOSE FIX
* ***Proposed Edit:***
  * Location: add at the end of line 311. Change: ` Packages sit outside the core contract: the core calls no model or provider, with or without them.`

### [N5] [`egm-style`] - Severity: Nit
* **Affected Scope:** line 259
* **Discrepancy Description:** "Fixed quietly" conflicts with the transparency stance.
* ***AI Suggestion:*** PROPOSE FIX
* ***Proposed Edit:***
  * Location: line 259, "can be fixed quietly across". Change: `can be fixed without stopping play to ask, across`

### [N6] [`egm-zoom-out` (Stage 8)] - Severity: Nit
* **Affected Scope:** Non-Goals, lines 57-66
* **Discrepancy Description:** The single-user, local assumption is never stated.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Loopback-only binding (line 206) already implies it. Stating it answers the scale and multi-user questions.
* ***Proposed Edit:***
  * Location: a new bullet after line 64. Change: `* **More than one player or machine.** A story has one human, one active writer session, and one local machine. There is no multi-user, networked, or hosted mode.`

### [N7] [`egm-structural`, `egm-zoom-out`] - Severity: Nit
* **Affected Scope:** lines 334 and 343
* **Discrepancy Description:** The heading is unclear, and Additional Resources sits under Open Questions.
* ***AI Suggestion:*** PROPOSE FIX for the H2 promotion only. DECLINE renaming the heading and trimming the list.
* ***Justification:*** `docs/history/implementation_handoff.md:13` links `#alternatives-and-implementation-plan`, so renaming breaks that link. The history links are kept on purpose.
* ***Proposed Edit:***
  * Location: line 343. Change: `### Additional Resources` → `## Additional Resources`

### [N8] [`egm-style`, `egm-zoom-out`] - Severity: Nit
* **Affected Scope:** lines 47, 102, 150 and 165
* **Discrepancy Description:** Small duplicates, and Goal 6 is long.
* ***AI Suggestion:*** DECLINE. The "Clear controls" part is fixed under M4.
* ***Justification:*** This is cosmetic, and splitting Goal 6 would renumber requirements that other documents cite.

### Declined critic and comprehension items

The table under "Declined, with reasons" in the [consolidated report](consolidated_review_report.md) stands as written: the Alternatives table, a Risks section, scale targets, a go/no-go criterion, a threat model, numbered sub-requirements, subjective wording, heading renames, and packages in the CUJs. Comprehension findings 5 and 6 are left to the contract and to Goal 7.

## Counts

7 Major and 6 Nit are proposed for fixing; N7 is partly declined. N8 and 9 other items are declined. None is contested or escalated.
