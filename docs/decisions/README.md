# Architectural decisions

This directory records durable decisions that shape CouldHappen's packaging, workspace, and distribution model using the [Markdown Architectural Decision Records](https://adr.github.io/madr/) (MADR) format.

The [approved design](../designs/couldhappen.md) remains the normative product and implementation specification. ADRs explain **why** a decision was made; the design defines **what must be built and verified**. Do not duplicate a full specification here.

| ADR | Status | Decision |
| --- | --- | --- |
| [0000](0000-use-markdown-architectural-decision-records.md) | Accepted | Use MADR to record durable decisions. |
| [0001](0001-separate-story-workspaces.md) | Accepted | Run every real story in a clean workspace with its own Git history; keep the development repository as upstream. |
| [0002](0002-publish-clean-release.md) | Accepted | Publish a deterministic clean release ZIP rather than the development history; MIT license; private/local story repositories; no v1 updater. The MIT choice is replaced by 0003. |
| [0003](0003-license-agpl.md) | Accepted | License the package under AGPL-3.0-or-later instead of MIT. |
| [0004](0004-publish-with-fresh-history.md) | Accepted | Publish the development repository with a fresh one-commit history; keep evidence folders local. |

For new decisions, copy one of the templates:

* [adr-template.md](adr-template.md) — all sections with explanations.
* [adr-template-minimal.md](adr-template-minimal.md) — mandatory sections with explanations.
* [adr-template-bare.md](adr-template-bare.md) — all sections, empty.
* [adr-template-bare-minimal.md](adr-template-bare-minimal.md) — mandatory sections, empty.

Name the file `NNNN-title-with-dashes.md`, where `NNNN` is the next consecutive number. Keep the title lowercase and use dashes. The `.markdownlint.yml` file holds the MADR lint adjustments.

Intermediate EGM brainstorming, drafts, reviewer reports, and drift reports are process evidence. Keep them in `docs/history/`, `docs/reviews/`, or another explicitly chosen artifact directory; do not place them in `docs/designs/` or this directory as if they were normative requirements.

Status changes to **Accepted** only after the project author approves the decision. Implementation and validation evidence belongs in [implementation progress](../implementation-progress.md) and [validation results](../validation-results.md), not in the ADR.
