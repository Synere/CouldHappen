---
status: accepted
date: 2026-11-11
decision-makers: Project author
consulted:
informed:
---

# ADR-5 — Check the docs with groundwork and name decisions ADR-n

- **Refines:** ADR-0

> In the context of a repository whose decisions, links and agent instructions are kept by hand, facing dead links and unchecked decision records, we decided to adopt groundwork's Core and Decisions layers and rename the decision files to `ADR-n-title.md`, to achieve checks that every agent and person passes through at commit, accepting that the five existing records changed their file names and citation form.

## Context and Problem Statement

[ADR-0](ADR-0-use-markdown-architectural-decision-records.md) chose MADR with files named `NNNN-title-with-dashes.md` and cited as "ADR 0004". Nothing checked that a cited decision exists, that a link resolves, or that a decision has its status and Confirmation. Two dead heading links had already accumulated in `docs/history/`.

groundwork checks links, decision IDs, citations and decision fields from a pre-commit hook. Its decision ID grammar needs a prefix, so files named by a bare number cannot be read: every number in every file would count as a citation.

## Considered Options

* Adopt groundwork's Core layer only and leave the decision records unchecked.
* Rename the records to `ADR-n-title.md`, cite them as `ADR-n`, and adopt the Decisions layer in its files form.
* Keep the records as they are and start a second, single-file log for new decisions.

## Decision Outcome

Chosen option: **rename and adopt the files form**, selected by the project author on 2026-11-11. One place holds every decision, and all of it is checked.

* `docs/decisions/000N-title.md` became `docs/decisions/ADR-N-title.md`, with the heading `# ADR-N — Title`. Every link and citation in the repository was rewritten. IDs keep their numbers: 0004 is ADR-4.
* The MADR templates moved to `docs/templates/adr/`, outside the decisions folder, so they are not read as decisions.
* `.groundwork.json` sets the layers, the decisions folder, the ID grammar and a grandfathering line at ADR-4: the five older records only warn about missing Y-statements or Confirmations. A new decision errors without them.
* The Core brief is the approved [design](../designs/couldhappen.md); no separate brief was written.
* `node scripts/groundwork-check.mjs` runs from `.githooks/pre-commit` (`core.hooksPath = .githooks`). None of these files ships in the release ZIP.

This refines ADR-0's naming rule; the choice of MADR stands.

### Consequences

* Good, because a dead link, a citation of a missing decision, or an incomplete new decision fails the commit.
* Good, because every decision stays in one folder in one format.
* Bad, because paths to the five old records changed. Anything outside the repository that linked to them by path breaks.
* Neutral, because a fresh clone has to run `node scripts/groundwork-check.mjs --install-hooks` once (the repository has no `package.json` to do it).

### Confirmation

`node scripts/groundwork-check.mjs` passes with no errors. The pre-commit hook runs it. `docs/decisions/` holds only `ADR-n-*.md` files, the index and the lint configuration.
