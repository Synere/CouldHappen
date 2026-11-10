---
type: plan
status: active
updated: 2026-11-11
---

# Wider public release

**Purpose.** The work to finish before CouldHappen is shared more widely than its GitHub releases. Ends when the items below are closed in the [issues register](../issues.md). Publishing itself is automated: a `v<version>` tag runs `.github/workflows/release.yml` ([Building a release](../setup.md#building-a-release)).

## ISS-4 — Drift report

Run `egm-drift-report` over the [design](../designs/couldhappen.md), [distribution design](../designs/distribution-and-workspaces.md), and [public contract](../public-contract.md) before a wider release. The designs are EGM's ([ADR-8](../decisions/ADR-8-open-work-in-the-register.md)), so their findings are resolved there. Earlier reports are in [docs/reviews/](../reviews/README.md).

## ISS-6 — Retake the screenshots

Retake the screenshots in the README and on GitHub for the restyled reader ([ADR-6](../decisions/ADR-6-dark-petrol-reader.md)).

## ISS-17 — EGM design review

The design's Open Questions say a fresh EGM design review of the [approved design](../designs/couldhappen.md) has not run, and that the predecessor reconciliation does not replace it.
