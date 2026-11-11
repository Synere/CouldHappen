# Zoom Out Report

**Target:** `docs/designs/couldhappen.md` (lines 1-355), reviewed as a feature specification.

## Reviewer Status

| Reviewer | Status |
| --- | --- |
| `egm-zoom-out` | completed |

## Verdict

Pass. There are no Blockers. The objective and the reason for it are clear (lines 13-33). The design reuses the host's agent loop, tools and permissions. Non-Goals (lines 57-66) reject a new runtime. The helper surface is small (lines 192-202), and the helper modules that exist match the responsibilities the document describes, so no duplicated components were found.

The reviewer read the persona, the standard and the full target. It checked that the linked `woven/` files, the `docs/history/planning/*.md` files and `helpers/*.py` exist. It did not read the optional background documents.

## Blockers

None.

## Major

### 1. Open question about the independent review is out of date - Severity: Major
* **Affected scope:** lines 340-341 (and the status at line 4)
* **Description:** The document is marked approved and implemented, but line 341 says "A fresh EGM design review of this document has not run". This review supersedes that line. A reader cannot tell whether "approved" predates review.
* **Recommendation:** Update the line, or drop it and record the review in the history.

### 2. Status and dates are inconsistent - Severity: Major
* **Affected scope:** lines 4-6, 19, 55, 175, 239, 253, 305, 311
* **Description:** Line 6 says "Last updated 2026-11-06". The text includes later changes: the ADR-6 dark-petrol restyle, Director packages with image generation, the `portrait_button` flag, `card.md`, the `armed` state and `checkpoint inspect`, and background `wait --timeout 0`. The text says changes are "folded in", but does not mark which parts postdate approval, so approved intent and later additions cannot be told apart.
* **Recommendation:** Check the "Last updated" date against the git log for this file. Mark or list the post-approval additions.

### 3. The spec has drifted into implementation detail - Severity: Major
* **Affected scope:** lines 208, 253, 305 (see also 169, 202)
* **Description:** Examples include the `import-card` portrait-path resolution rules, the `armed` field in private control state, the `python -m helpers checkpoint check` and `checkpoint inspect --ref <commit>` commands, the `writer claim`, `recover` and `writer close` verbs, and the retry rule about resolving an existing ID before checking whether saving is open. Lines 169 and 202 say these are bound in `docs/public-contract.md` and `docs/setup.md`, so keeping them here creates two sources of truth that can disagree.
* **Recommendation:** Move the mechanics to the contract and setup docs. Keep only the architectural rules here: hooks act only while play is armed, and retry resolves existing IDs before permission.

## Nits

1. **Planning-era wording remains** (lines 171, 177, 179). "Proposed placement" and "provisionally `START_HERE.md`" and "provisionally `helpers/` and `web/`" read as undecided although the design is implemented. Use the actual paths or link to `docs/setup.md`.
2. **Ambiguous standing wait** (lines 233, 239). Step 6 of the ordinary loop and the "standing wait" paragraph overlap. The preferred background `wait --timeout 0` is host-conditional and appears only as a one-line aside. Fold it into the capability table (line 157) or `docs/reference-hosts.md`, so the main flow states it once.
3. **Heavy cross-linking to history** (lines 7, 102, 165, 336, 343-353). A new reader needs about 10 links to get the full rationale. Trim Additional Resources (345-353) to what a current maintainer needs. The research and carry-over audits are archival.
4. **Pending-input state described redundantly** (lines 138, 184-186, 235, 281). Each restates the pending, addressed and deferred semantics. One authoritative paragraph with pointers would be simpler.
5. **Goal 6 is a very long single item** (line 47). It bundles error-repair permission, the changed-passage indicator, the production block and the Woven carry-over. Split it, or move the repair permission to the Authoring section where it already appears (line 259).
6. **Scope boundary deserves one sentence** (lines 55, 311). Director packages with outside services (image generation) sit close to the Non-Goal of provider integrations (lines 59, 63). Line 311 keeps them optional and approval-gated, which is adequate. One sentence stating that packages are not part of the core contract would remove the doubt.
