# Goldfish Review Report

**Target:** `docs/designs/couldhappen.md` (lines 1-355, whole document), reviewed as a feature specification.

## Reviewer Status

| Reviewer | Status |
| --- | --- |
| `egm-design` | completed |
| `egm-structural` | completed |
| `egm-style` | completed |

No Blockers were found. Findings from the three reviewers are merged and deduplicated below. Line numbers refer to the target.

## Prioritized Findings (Blockers -> Major -> Nits)

### Alternatives are not in the spec - Severity: Major
* **Reviewer Lens:** `egm-design`, `egm-structural`
* **Affected Scope:** `Alternatives and implementation plan`, lines 334-336; decision table, lines 132-144
* **Discrepancy Description**: The section only points to `../history/design-alternatives-and-plan.md`. The T1-T15 table lists selected behaviors, not rejected options. The standard says a spec that shows a single path fails. Many rows in the history file read "Rejected by author (T#)" with no linked issue or discussion. The heading is not "Alternatives Considered".
* **Rationale & Recommendation**: Add a short table of the 6-8 most load-bearing rejections (for example app-owned controller, Vite versus static build, polling versus push) with option, outcome and one concrete reason. Rename the heading. Where the history says "rejected by author", give the technical reason or link the T-decision entry.

### No Risks and Mitigations section; scalability unaddressed - Severity: Major
* **Reviewer Lens:** `egm-design`, `egm-structural`
* **Affected Scope:** scattered at lines 31-33, 196, 204, 206, 222, 237, 239, 267-269, 307
* **Discrepancy Description**: Risks are spread through the text. Several have no mitigation: a missed wait renewal silently stops input (L239); a tool that bypasses the pause can corrupt logs and the doc does not say what the player sees (L222); wait-renewal cost has no budget or "unsupported" threshold (L237). Growth of `story.md` and `director.md`, cost of re-validating the whole log on each poll, snapshot size and Git growth from PNG portraits are not addressed (L196).
* **Rationale & Recommendation**: Add a Risks and Mitigations section as a table: failure mode, effect, mitigation or accepted residual risk, who detects it. State the expected scale and polling cost.

### Security is only partly specified - Severity: Major
* **Reviewer Lens:** `egm-design`
* **Affected Scope:** line 206 (also 65, 253)
* **Discrepancy Description**: Loopback binding and the Vite filesystem allowlist are covered. Not covered: other local processes or web pages reaching loopback (DNS rebinding, cross-origin POST), Host/Origin checks, CSRF or a per-session token on submit and pause/release endpoints, import size limits for untrusted SillyTavern cards (held only in the history file), and how human or card text is kept from being read as a host command by an agent with full permissions.
* **Rationale & Recommendation**: Add a short threat-model paragraph covering these, state that card and human text is data, state the import limits, and name the residual risk.

### Unproven host assumptions have no go/no-go or fallback - Severity: Major
* **Reviewer Lens:** `egm-design`, `egm-style`
* **Affected Scope:** lines 21, 33, 49, 53, 157, 163, 239, 319-330, 340
* **Discrepancy Description**: The design depends on hosts servicing a yielded or background command, but defines no failure case or degraded mode. Several sentences were written before implementation ("outcomes to establish", "remains to be demonstrated", "No compatibility or performance claim is established") and were not updated, while the status says implemented. Observed results are not summarized or linked precisely.
* **Rationale & Recommendation**: State a go/no-go criterion for the wait capability and the degraded mode. Replace each stale sentence with a dated status that links the exact section of `../validation-results.md`, or label the section as acceptance criteria.

### Visual reference contradicts itself - Severity: Major
* **Reviewer Lens:** `egm-structural`, `egm-style`, `egm-design`
* **Affected Scope:** lines 19, 66, 315
* **Discrepancy Description**: Line 19 says ADR-6 replaced the pale surface and `DESIGN.md` is current. Lines 66 and 315 still call the Woven image the current visual reference. Line 19 also describes the superseded look first.
* **Rationale & Recommendation**: Lead with `DESIGN.md` and ADR-6. Point lines 66 and 315 to them. Describe Woven only as the structural or historical reference.

### Approved text mixed with later amendments; status metadata inconsistent - Severity: Major
* **Reviewer Lens:** `egm-structural`, `egm-style`, `egm-design`
* **Affected Scope:** lines 4-6, 19, 47, 55, 102, 175, 253, 271, 305, 309-311, 341
* **Discrepancy Description**: Status says "Approved 2026-11-04; implemented; current" but Date is 2026-11-03, Last updated is 2026-11-06, and amendments (ADR-6, standing permission, `portrait_button`, `card.md`, `checkpoint check`, `armed`, Director packages, session drafts) are folded in mostly undated. A reader cannot tell what the approval covered. Line 341 says no fresh EGM review has run, which contradicts the stamp.
* **Rationale & Recommendation**: Refresh Last updated. Add a short dated revision list, or an ADR link for each folded-in change. Say what the approval covered and when "current" was last checked against the code. Update line 341 to link this review.

### Open Questions section is stale - Severity: Major
* **Reviewer Lens:** `egm-structural`, `egm-design`
* **Affected Scope:** lines 338-341, 343
* **Discrepancy Description**: It lists no real open questions, only pointers. Line 341 is stale. "Additional Resources" is an H3 under it but is a document-level appendix.
* **Rationale & Recommendation**: Retitle to "Status of open work" and link `../issues.md`, or list real open items. Promote Additional Resources to H2 and mark which entries are normative and which are history.

### "Proposed" and "provisionally" wording in an implemented design - Severity: Major
* **Reviewer Lens:** `egm-style`
* **Affected Scope:** lines 171-180, 206, 297
* **Discrepancy Description**: The placement table says "Proposed placement" and "provisionally `START_HERE.md`". Line 206 says configuration is "to be checked against the versions selected later" (an unclosed TODO). Line 297 says draft preservation must be implemented deliberately, but line 271 says drafts are preserved.
* **Rationale & Recommendation**: Use the actual paths and versions, or say the names are open and where the decision is recorded. Align line 297 with line 271.

### Command-level detail sits in a high-level spec - Severity: Major
* **Reviewer Lens:** `egm-style`, `egm-structural`, `egm-design`
* **Affected Scope:** lines 169, 253, 305
* **Discrepancy Description**: Line 169 defers concrete files to `../setup.md` and `../public-contract.md`, yet line 305 packs a policy, a rule and several CLI commands into one paragraph, and line 253 describes `card.md` and `import-card` behavior.
* **Rationale & Recommendation**: Move the command and file specifics to `../setup.md`, `../reference-hosts.md` and `../public-contract.md`. Keep the requirement here.

### Overview paragraphs are dense - Severity: Major
* **Reviewer Lens:** `egm-style`
* **Affected Scope:** lines 13-21
* **Discrepancy Description**: Three long abstract paragraphs; line 17 lists seven nouns in one sentence; line 21 mixes the demonstration scenario with support targets.
* **Rationale & Recommendation**: Split them, and put the current visual reference first.

### Subjective or untestable wording - Severity: Nit
* **Reviewer Lens:** `egm-style`
* **Affected Scope:** lines 13, 31, 37, 39, 41, 74, 247-251, 258-261
* **Discrepancy Description**: "believable", "meaningful" (lines 39, 49, 146, 247, 301), "honest", "constructive", "ordinary" (about 20 uses), "proportionate corrections", "small understood error" and "fixed quietly" are undefined. "Quietly" conflicts with the transparency stance at lines 41 and 261. Line 261 hedges on rollback versus Undo. RFC-style keywords are used inconsistently.
* **Rationale & Recommendation**: Replace adjectives with the concrete behavior or the assessment method. Define the threshold for a quiet fix and what must be recorded. Say what the writer must do for rollback versus Undo. Use MUST and SHOULD consistently where a requirement is meant.

### Imperative skill text inside the spec - Severity: Nit
* **Reviewer Lens:** `egm-structural`, `egm-style`
* **Affected Scope:** lines 245-251
* **Discrepancy Description**: "Take initiative..." addresses the writer directly and reads as prompt text.
* **Rationale & Recommendation**: Frame it as a requirement ("The skill must contain a principle that...") or link to the skill file.

### Decision IDs T1-T15 unexplained and merged - Severity: Nit
* **Reviewer Lens:** `egm-structural`, `egm-style`
* **Affected Scope:** lines 132-144
* **Discrepancy Description**: IDs are defined only in `../history/planning/technical_plan_decisions.md`. Rows are merged (T5-T6, T9-T10, T11-T12, T13-T14), so single decisions cannot be cited. "Selected behavior" entries are labels.
* **Rationale & Recommendation**: Label the column, link the record per ID, and avoid ranges.

### Goals, CUJs and validation rows repeat each other and are hard to trace - Severity: Nit
* **Reviewer Lens:** `egm-structural`, `egm-style`, `egm-design`
* **Affected Scope:** lines 35-55, 68-98, 321-330
* **Discrepancy Description**: Undo, fresh context and checkpoints recur across all three. Goals 6, 7, 8 and 10 bundle five or more requirements each. CUJ "Then" clauses are wordy (line 74 has seven verbs; line 86 is ambiguous). The validation table has evidence criteria but no thresholds (renewal overhead, poll latency, what counts as "several" exchanges).
* **Rationale & Recommendation**: Number sub-requirements, link CUJs and validation rows to Goal numbers, rewrite CUJ outcomes as numbered observable results, and add targets or state that none are claimed.

### Heading names and structure - Severity: Nit
* **Reviewer Lens:** `egm-structural`
* **Affected Scope:** lines 23, 100, 241-261
* **Discrepancy Description**: "The Problem" and "Technical Plan (Architecture)" differ from the standard's names. Only one H4 exists; sibling topics at lines 241-261 have no headings.
* **Rationale & Recommendation**: Align names with the standard and add headings for the sub-topics.

### Misc wording and duplication - Severity: Nit
* **Reviewer Lens:** `egm-style`
* **Affected Scope:** lines 19, 55, 102, 150, 165, 207, 222, 233, 253, 307, 336, 355
* **Discrepancy Description**: Line 102 repeats the approval claim from line 4. Lines 150 and 165 make the same point. Goal 10 (line 55) is tense-confused about Director image generation versus the core non-goal. Line 233 "Clear controls" is ambiguous. Line 222 would sit better next to step 4 of line 219. Lines 207 and 307 name no inspection step or document. Line 336 second clause belongs in the Status line. The footer "Drafted with EGM" next to line 341 is confusing. Line 53 has no reader decision attached.
* **Rationale & Recommendation**: Delete duplicates, rephrase Goal 10, say "Release controls", name the inspection step and the document (`../reference-hosts.md`), and clarify "drafted with" versus "reviewed by".

## Not verified

The style reviewer did not open linked files, so claims about `validation-results.md`, `reference-hosts.md`, the ADRs and the `armed` field and CLI names at line 305 are unchecked. The structural reviewer confirmed the relative links it checked resolve.
