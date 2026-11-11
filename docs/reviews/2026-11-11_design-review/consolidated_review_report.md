# Consolidated EGM design review: CouldHappen design

* **Issue:** ISS-17, a fresh EGM design review of the approved design
* **Date:** 2026-11-11
* **Target:** [`docs/designs/couldhappen.md`](../../designs/couldhappen.md), lines 1-355, reviewed as a feature spec
* **Mode:** consolidated report (the uninterrupted flow). Every reviewer ran on Sonnet, at the author's request.
* **Context given to reviewers:** the repository files the design links to. Two Vite documentation URLs were left out.
* **Stage reports:** [zoom out](zoom_out_report.md) (Stage 5), [comprehension](comprehension_report.md) (Stage 6), [critic](critic_report.md) (Stage 7), [intermediate zoom out](intermediate_zoom_out_report.md) (Stage 8)
* **Stage 9 (implementation readiness) did not run.** The design has no implementation-plan section. Line 336 only points to [the finished plan in history](../../history/design-alternatives-and-plan.md), and a finished plan has nothing to check for readiness.

## Verdict

Pass, with changes. No stage found a Blocker. Both zoom-out stages call the design simple and in scope: it adds no runtime, and the helper surface matches the code. The problems are in the document, not the architecture:

* It says it is current, but parts of it are stale.
* It contradicts itself about the visual reference.
* It repeats command-level detail that the public contract already owns.
* It uses some terms without defining them.

Stage 8 warns against adopting the critic's "add a section" fixes wholesale. On a shipped design, more text means more to drift. This report follows that warning: items that would only grow the document are listed as declined, each with its reason.

## Checked against the code

The critic called security "only partly specified" (no Host/Origin checks, no tokens, no import limits). The code and the contract already handle this:

* `helpers/bridge.py:259` checks the Host header.
* [The public contract](../../public-contract.md) requires the configured frontend Origin on mutations. It puts a bearer secret on `/control` and refuses browser Origin there. It also sets a 256 KiB body limit with `413` errors.

The gap is that the design doesn't mention any of this. See item M5.

The contract also settles the comprehension test's `wait --timeout 0` question: 0 means "no helper deadline". Here too, only the design's wording is unclear (item M4).

## Action items

### 🔴 Blocker

None.

### 🟡 Major

| ID | Action | Lines |
| --- | --- | --- |
| M1 | **Make the status true.** Replace line 341 ("a fresh EGM design review … has not run") with a link to this review. Update "Last updated" at line 6. Say in one line what the 2026-11-04 approval covered, and that later changes are recorded in the ADRs and the progress log. | 4-6, 341 |
| M2 | **Name one visual reference.** Lead with ADR-6 and `DESIGN.md` as the current reference. Describe Woven as the structural origin (layout, Story/Director views, composer, cast panel), not as the current look. Fix lines 66 and 315 to match. | 19, 66, 315 |
| M3 | **Move command detail to the documents that own it.** The `writer claim`, `recover` and `close` verbs; the `armed` field; `checkpoint check` and `checkpoint inspect`; the portrait path rules for `import-card`; `card.md`; the retry ordering; and the `portrait_button` and `present: false` flags all belong in the contract or setup docs. Check each against the contract first. If it is already there, delete it from the design. If not, add it to the contract, then delete it here. Keep only the architectural rule in the design. | 175, 208, 253, 305 |
| M4 | **Define the standing wait once.** Six terms name one idea: "local wait", "standing wait", "serviced command wait", "yielded command", "native monitor/event" and "background `wait --timeout 0`". Define it once near line 237, as a command that returns when input is pending and is kept running before each turn ends. Delete the alternates, and say that `--timeout 0` means no helper deadline. | 37, 157, 233, 237-239 |
| M5 | **Add one sentence on local security.** The sentence should point to the contract for its Host and Origin checks, the `/control` secret and the body limit. Add that card and human text is data, never instructions to the agent. Don't add a threat-model section. | 206 |
| M6 | **Remove planning-era wording.** "Proposed placement" and "provisionally" no longer apply. Close the open TODO at line 206 ("to be checked against the versions selected later"). Make line 297 (drafts must be handled deliberately) agree with line 271 (drafts are preserved). In the validation section, label the table as acceptance criteria and link the matching section of [validation results](../../validation-results.md). | 171-179, 206, 271, 297, 319-330 |
| M7 | **Say what controls the writer has, in one place.** The edit pause, the prose-production block and the claimed/armed state share vocabulary, and a reader cannot tell them apart. Add one short paragraph naming the three, saying what each blocks, and linking the contract's state machine. Don't add a table. | 214-224, 305 |

### 🟢 Nit

| ID | Action | Lines |
| --- | --- | --- |
| N1 | Say where the T1-T15 IDs are defined: link [the technical decision record](../../history/planning/technical_plan_decisions.md) in one sentence. Keep the merged rows. | 132-144 |
| N2 | State once whether Pi is required or only the selected OpenRouter route. Gloss Impeccable, MightHappen and SillyTavern cards in a few words each. | 21, 45, 53, 66, 165 |
| N3 | Reword the creative-initiative paragraph as a requirement on the skill ("the skill opens with a principle that…"), or quote it as skill text. It is written in the second person to the agent, but it sits inside the design. | 245-251 |
| N4 | Add one sentence saying Director packages are optional extras outside the core contract. That clears up the apparent conflict with the provider non-goal and with Goal 10's image-generation clause. | 55, 59, 63, 311 |
| N5 | Make "fixed quietly" (line 259) agree with the transparency stance. Say what a quiet fix must still record. | 41, 259, 261 |
| N6 | State the single-user, local assumption in Non-Goals: one human, one writer, one machine. That answers the scale and multi-user questions without a new section. | 57-66 |
| N7 | Rename the `## Alternatives and implementation plan` heading so it says it points to history. Promote Additional Resources to H2 and mark which entries are history. Trim the archival research links. | 334-353 |
| N8 | Small duplicates: line 102 repeats the approval claim; lines 150 and 165 make the same point; Goal 6 bundles four requirements. Write "Release controls" for "Clear controls" at line 233. | 47, 102, 150, 165, 233 |

### Declined, with reasons

| Finding | Source | Why not |
| --- | --- | --- |
| Add an Alternatives table to the spec | critic | The alternatives are recorded in history, and copying them here creates a second source that can drift. N7 renames the pointer instead. |
| Add a Risks and Mitigations section | critic | Lines 64 and 237 already state the limits. Known limitations are tracked as ISS-9 to ISS-12 in [known limitations](../../plans/known-limitations.md). |
| Scale targets and polling thresholds | critic | One local user with a one-second poll has no proven bottleneck. N6 states the assumption instead. |
| Go/no-go criterion and degraded mode for waiting | critic | Line 163 already gives the degraded mode: ordinary play with guidance-only checkpoint assurance. What's missing is observation on real hosts, tracked as ISS-13 to ISS-15. |
| Threat-model section | critic | The checks exist in code and contract; M5 adds a pointer. |
| Number every Goal sub-requirement and trace CUJs to Goals | critic | This would grow the shipped design for little gain. ISS-4's drift check covers whether the document matches the code. |
| Replace subjective words ("believable", "meaningful") throughout | critic | These describe creative judgment, which the design leaves to the writer on purpose. Only "fixed quietly" conflicts with another rule (N5). |
| Rename "The Problem" and "Technical Plan" to the standard's headings | critic | It's cosmetic, and other documents link to these headings. |
| Add Director packages to the CUJs and the diagram | comprehension | They are optional extras; N4's one sentence is enough. |

## Order of work

The register ranks ISS-17 before ISS-4. The fixes above change the design text, so the drift check (ISS-4) should run after they land. Otherwise it reports against text that is about to change.

## Traceability matrix

| Action | Zoom out (S5) | Comprehension (S6) | Critic (S7) | Intermediate zoom out (S8) |
| --- | --- | --- | --- | --- |
| M1 | Major 1, Major 2 | 12 | Approved text mixed with amendments; Open Questions stale | Major 3 |
| M2 | — | 1 | Visual reference contradicts itself; Overview dense | Major 3 |
| M3 | Major 3 | 2, 8 | Command-level detail | Major 4 |
| M4 | Nit 2 | 3 | Misc wording ("Clear controls") | Nit 2 |
| M5 | — | — | Security partly specified | Major 2 |
| M6 | Nit 1 | 10 | "Proposed" and "provisionally" wording; unproven host assumptions (stale sentences) | Nit 3, Nit 11 |
| M7 | Nit 4 | 2 | — | Nit 1 |
| N1 | — | 4 | Decision IDs T1-T15 | Nit 4 |
| N2 | — | 7, 9, 13 | — | Nit 8, Nit 9 |
| N3 | — | 9 | Imperative skill text | Nit 6 |
| N4 | Nit 6 | 8 | Misc wording (Goal 10) | Nit 5 |
| N5 | — | — | Subjective wording ("quietly") | Nit 7 |
| N6 | — | — | No Risks section (scalability) | Missed: single-user assumption |
| N7 | Nit 3 | — | Alternatives not in spec; Open Questions stale; heading names | Major 1, Nit 10 |
| N8 | Nit 5 | 11 | Goals/CUJs repeat; misc wording | — |
| Declined | — | 5, 6, 8 (partly) | Alternatives table, Risks, scale, go/no-go, threat model, numbering, subjective words, heading names | Major 1, Major 2 |

Comprehension findings 5 (entry format) and 6 (who commits and when) are left to the contract and to Goal 7. The design points to the contract for the entry syntax, which is the right home for it. The writer chooses commit timing on purpose, and the hook covers the completion boundary.

## Not verified

The style reviewer and the comprehension reviewer did not open linked files. This report checked only the security claim and the `--timeout 0` meaning against the code and the contract. M3's list of what the contract already holds still has to be checked item by item when the fixes are made.
