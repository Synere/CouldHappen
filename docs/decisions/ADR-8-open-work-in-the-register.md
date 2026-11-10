---
status: accepted
date: 2026-11-11
decision-makers: Project author
consulted:
informed:
---

# ADR-8 — Keep open work in the register and plans, and leave designs and reviews to EGM

- **Refines:** ADR-5

> In the context of a hand-kept implementation-progress note that copied facts from other documents (the release version, host status, next steps) and went stale, facing several documents that each claimed to hold current state, we decided to switch on groundwork's Open work, Plans & research and Session hook layers, retire the progress note into `docs/history/`, and leave designs, reviews and drift reports to EGM, to achieve one checked home for each kind of fact, accepting that the progress note's links now point into history and that groundwork's own Specs, Review and Architecture layers stay off.

## Context and Problem Statement

`docs/implementation-progress.md` held the current state, the next steps and the open gaps. Its release line still named 0.1.7 after 0.1.20 was published, its host summary repeated [host integrations](../reference-hosts.md), and nothing checked any of it. `docs/history/progress-log.md` asked for new dated entries, and the release rows in [validation results](../validation-results.md) stopped at 0.1.7 once `release.yml` started building releases.

The approved designs, the architecture they describe, the concept and packaging reviews, and the drift reports were all written with EGM. groundwork has layers for specs, architecture and reviews too, and defers to EGM where a project already uses it.

Where should current state, open work and plans live, and which system owns what?

## Considered Options

* Keep the progress note and add a check that its release line matches the manifest.
* Retire the progress note: open work in the groundwork register, plans in `docs/plans/`, designs and reviews left with EGM.
* Move everything into groundwork, including specs, architecture and reviews.

## Decision Outcome

Chosen option: **retire the progress note and split ownership**, selected by the project author on 2026-11-11.

| Kind of fact | Home | Kept by |
| --- | --- | --- |
| What is open: to-dos, deferred items, unverified claims | [issues register](../issues.md), `ISS-n` rows | groundwork |
| How work not built yet will be done | notes in `docs/plans/` | groundwork |
| Why a choice was made | `docs/decisions/` | groundwork (ADR-5) |
| What the system must do, and how it is put together | `docs/designs/` | EGM |
| Reviews and drift reports | `docs/reviews/` | EGM |
| What was observed on hosts | [validation results](../validation-results.md) and [host integrations](../reference-hosts.md) | by hand |
| Which release is current | `release.manifest.json` and the GitHub releases page | `release.yml` |

* `docs/implementation-progress.md` moves to `docs/history/implementation-progress.md` and is frozen. Its next steps and open gaps are `ISS-n` rows whose home sections are in the plan and reference notes.
* `docs/history/progress-log.md` is frozen. The git log and the register's Closed rows replace it.
* No document names the current release version except the manifest, so no version check is needed.
* groundwork's Specs, Review and Architecture overview layers stay off. Text in an EGM document changes through EGM or by the author, not as groundwork upkeep.

### Consequences

* Good, because every open item has an ID, a home and a check, and a new session prints the open-work summary.
* Good, because no document repeats the release version or the host status.
* Bad, because links to the progress note from outside the repository break.
* Neutral, because the EGM documents keep their own format and are checked for drift by an EGM drift report, not by groundwork.

### Confirmation

`node scripts/groundwork-check.mjs` passes with the open-work, plans and session-hook layers on. `docs/implementation-progress.md` does not exist, and `.groundwork.json` lists no specs, review or architecture layer.
