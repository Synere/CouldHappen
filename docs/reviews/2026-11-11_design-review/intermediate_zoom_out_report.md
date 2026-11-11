# Intermediate Zoom Out Report (Stage 8)

**Target:** `docs/designs/couldhappen.md` (lines 1-355)

## Reviewer Status

| Reviewer | Status |
| --- | --- |
| `egm-zoom-out` | completed |

Earlier reports considered: [zoom_out_report.md](zoom_out_report.md), [comprehension_report.md](comprehension_report.md), [critic_report.md](critic_report.md).

## Verdict

Pass, no Blockers. The design stays simple and in scope. The risk now is the review round itself: several earlier recommendations would make the document bigger without making the product simpler. No duplicated components found, and no new components are proposed.

## Blocker

None.

## Major

### 1. Do not adopt the critic's "add sections" fixes wholesale (lines 334-341, 206, 239, 319-330)
The critic asks for an Alternatives table, a Risks and Mitigations section, a threat model, a go/no-go criterion with a degraded mode for waiting, scale targets, and numbered CUJ thresholds. This is a shipped, approved design. Adding all of it lengthens the spec and invites drift against `public-contract.md`, `setup.md` and `validation-results.md`, which is the problem the first zoom out reported and ISS-4 checks for.
- Alternatives: keep the pointer at line 336, rename the heading, do not copy the table in.
- Risks: no new section. Lines 237 and 64 already state the limits. At most, one "Known limits" pointer to `docs/plans/known-limitations.md` (ISS-9 to ISS-12).
- Scale and polling thresholds: reject. A single-user local story with a one-second poll has no proven bottleneck.
- Go/no-go for waiting: reject as a new design item. Line 163 gives the degraded mode (ordinary play, guidance-only assurance); line 239 gives the failure case. The real gap is observation, tracked as ISS-13 to ISS-15.

### 2. Security hardening: keep to a few sentences (line 206)
Only one critic addition earns a place: an Origin/Host check (or token) on the pause, release and submit endpoints, as part of the loopback story at line 206.
- Check `helpers/bridge.py` and the public contract first. If it exists, document it in the contract and add one line here. If not, open an issue rather than a design section.
- Import size limits belong in the contract or card importer.
- "Card text is data, not commands" is already implied by lines 45 and 253.

### 3. Fix metadata first (lines 6, 19, 55, 66, 315, 341)
- Line 341 says a fresh EGM review has not run. Replace with a link to this review set, or delete.
- Line 6 "Last updated" is wrong.
- Line 19 says DESIGN.md is current while lines 66 and 315 still call Woven current. State once that ADR-6 and DESIGN.md are authoritative and Woven is structural history (Overview and Goal 10).
All three earlier reports agree. This makes the document smaller and clearer.

### 4. Shrink by deletion, but do not leave duplicates (lines 169, 202, 208, 253, 305)
Moving command names, the `armed` field, `card.md`, retry ordering and the `portrait_button` / `present:false` flags to `public-contract.md` and `setup.md` is right. Check the contract first: if the item is already there, delete it here; if not, add it there. Never paraphrase the same rule in both places. Keep only the architectural rules here: hooks act only while play is armed, and retry resolves an existing ID before checking permission.

## Nit

1. Control-state glossary (comprehension finding 2): do not add a table to the design. Link the contract from lines 214-224 and 305, or add it there.
2. Wait vocabulary (lines 157, 233, 239): six terms for one idea. Define once at line 237 ("a command that returns when input is pending, kept running before each turn ends") and delete the alternates. Resolve `--timeout 0` with half a sentence or move it to the contract.
3. Stale wording: remove "Proposed placement" and "provisionally" (lines 171, 177, 179). Close the TODO at line 206. Align line 297 (drafts implemented deliberately) with line 271 (drafts preserved).
4. T1-T15 table (lines 132-144): add one sentence saying where the IDs are defined; do not split merged rows.
5. Late features (Director packages line 311, `portrait_button`): one sentence saying packages are optional extras outside the core contract. No new CUJs or diagram entries.
6. Creative-initiative text (lines 245-251): reword the second-person paragraph as a requirement on the skill, or link the skill file.
7. Subjective wording ("believable", "meaningful"): leave, except reconcile "fixed quietly" (line 259) with the transparency stance at lines 41 and 261.
8. MightHappen (line 66): add a short gloss.
9. Pi: state once whether it is required or only the selected reference route; gloss "Impeccable".
10. Resources list (lines 343-353): trim to maintainer-relevant links or mark entries as history.
11. Validation table (lines 319-330): note that it is acceptance criteria and link `docs/validation-results.md`; add no thresholds.

## Missed by the earlier zoom out

- Issue order: `docs/issues.md` ranks ISS-17 (this review) before ISS-4 (drift check). Fixes change the design text, so run the drift check after they land, and close ISS-17 with a link to this review set.
- Dev-repo versus story workspace (line 293): stated in one clause and correctly short. Do not expand.
- Single-user local assumption is never stated outright. One sentence in Non-Goals (one human, one writer, one machine) would pre-empt the scale and security demands.

## Summary

Act on: status and date drift, the visual-reference contradiction, stale "provisional" wording, and command-level detail that belongs in the contract. Defer the Alternatives table, Risks section, scale targets and go/no-go criteria. Add only a short Origin/Host-check note, after confirming the code.
