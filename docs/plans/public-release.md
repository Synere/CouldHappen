---
type: plan
status: active
updated: 2026-11-11
---

# Wider public release

**Purpose.** The work to finish before CouldHappen is shared more widely than its GitHub releases. Ends when the items below are closed in the [issues register](../issues.md). Publishing itself is automated: a `v<version>` tag runs `.github/workflows/release.yml` ([Building a release](../setup.md#building-a-release)).

## ISS-4 — Drift report

Run `egm-drift-report` over the [design](../designs/couldhappen.md), [distribution design](../designs/distribution-and-workspaces.md), and [public contract](../public-contract.md) before a wider release. The designs are EGM's ([ADR-8](../decisions/ADR-8-open-work-in-the-register.md)), so their findings are resolved there. Earlier reports are in [docs/reviews/](../reviews/README.md).

**Report run 2026-11-11.** The [2026-11-11 drift report](../reviews/2026-11-11_DRIFT_REPORT.md) found no Blocker. Its triage lists eight code fixes (the two most significant: `close` keeps a production block, and `wait` can hang after a restart with a persisted pause) and three document fixes.

**Closed 2026-11-11.** The report has run; its triage was cut into ISS-19 to ISS-23 below, which carry the fixes.

## ISS-19 — Writer controls after close and restart

Drift report triage 1 and 2. `writer close` refuses while a production block is on ("release the block first"), as it already does for the edit pause, so a clean close never persists `production: true`, which later makes `claim` refuse after a restart. `wait-view` refuses when the helper is closing or unowned, even while a pause is persisted, so `wait --timeout 0` exits 2 after a restart instead of hanging. Only an owned pause returns the empty list. Add a test for each, and state closing while blocked in the [public contract](../public-contract.md).

## ISS-20 — Validation names the file

Drift report triage 3 and 4. Every `validate` error names its file: `public/story.md:<line>`, `public/director.md:<line>`, `public/cast.json`, `public/work.json`, with JSON decode errors wrapped the same way. `cast.json` rejects unknown top-level fields, as it already does for character fields.

## ISS-21 — Lossless card copy and portrait guidance

Drift report triage 5 and 6. `cards.readable` includes the V2/V3 envelope fields outside `data`, keeps a lorebook entry's `name` when its `comment` is the title, and keeps falsy text fields; the cases go in `tests/test_cards.py`. When `portrait` finds no preserved `source.png` (a JSON-card import), it returns the contract's guidance rather than a raw OS error.

## ISS-22 — Reader boundary and save wording

Drift report triage 7, 8 and 11. Add `**/START_HERE.md` to `server.fs.deny` in `web/vite.config.js`. The portrait button gives a failed connection as its reason, not "saving is paused". The contract says that the reader settles an uncertain save from the snapshot and does not retry while saving is closed; retry-while-closed stays a helper guarantee for any client.

## ISS-23 — Design text catches up

Drift report triage 9 and 10. The [design](../designs/couldhappen.md) names `voice.md` and `what-this-can-do.md` in the skill row and points at the skill's `references/creative-practice-examples.md` as the one source; `docs/designs/creative-practice-examples.md` is deleted or reduced to a pointer. The [distribution design](../designs/distribution-and-workspaces.md) step 7 says root-absolute link targets are checked against the ZIP root and `<…>` destinations are not checked.

## ISS-6 — Retake the screenshots

Retake the screenshots in the README and on GitHub for the restyled reader ([ADR-6](../decisions/ADR-6-dark-petrol-reader.md)).

**Closed 2026-11-11.** `director.png` and `story-empty.png` were retaken at 1702×892 in the current stock reader, from a temporary copy of the public files of the 0.1.10 D&D story workspace (the story the old shots showed); `director.png` shows the first Director exchange with an empty cast, as it was before any picture was made. `story-cast.png` was taken from the same files in a throwaway copy of the reader with the scene-images theme and the rpg-mechanics sheet panel applied as those packages describe, using that session's own `sheet.json` (its "Blood moon" theme and Ash's stats), with the Gorger left out of the cast so Whisper and the sheet share the frame; the repository's reader was not changed. `director-export.png` shows a reader a player built, not the stock one, so it was kept.

## ISS-17 — EGM design review

The design's Open Questions say a fresh EGM design review of the [approved design](../designs/couldhappen.md) has not run, and that the predecessor reconciliation does not replace it.

**Closed 2026-11-11.** Stages 5 to 8 of an EGM review ran in consolidated mode, every reviewer on Sonnet; Stage 9 was skipped because the design has no implementation plan of its own. No stage found a Blocker. The author auto-accepted the proposed fixes: the status and review line are current, DESIGN.md is named as the one visual reference, command detail the public contract already holds was removed, the standing wait and the three writer controls are defined once, and a single-user Non-Goal was added. The critic's requests for new Alternatives, Risks and threat-model sections were declined. The reports and the resolution record are in [the review folder](../reviews/2026-11-11_design-review/consolidated_review_report.md). ISS-4's drift check now runs against the revised text.
