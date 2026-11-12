# Architectural decisions

This directory records durable decisions that shape CouldHappen's packaging, workspace, and distribution model using the [Markdown Architectural Decision Records](https://adr.github.io/madr/) (MADR) format.

The [approved design](../designs/couldhappen.md) remains the normative product and implementation specification. ADRs explain **why** a decision was made; the design defines **what must be built and verified**. Do not duplicate a full specification here.

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-0](ADR-0-use-markdown-architectural-decision-records.md) | Accepted | Use MADR to record durable decisions. |
| [ADR-1](ADR-1-separate-story-workspaces.md) | Accepted | Run every real story in a clean workspace with its own Git history; keep the development repository as upstream. |
| [ADR-2](ADR-2-publish-clean-release.md) | Accepted | Publish a deterministic clean release ZIP rather than the development history; MIT license; private/local story repositories; no v1 updater. The MIT choice is replaced by ADR-3. |
| [ADR-3](ADR-3-license-agpl.md) | Accepted | License the package under AGPL-3.0-or-later instead of MIT. |
| [ADR-4](ADR-4-publish-with-fresh-history.md) | Accepted | Publish the development repository with a fresh one-commit history; keep evidence folders local. |
| [ADR-5](ADR-5-adopt-groundwork-checks.md) | Accepted | Check the docs with groundwork; name decisions `ADR-n-title.md` and cite them as `ADR-n`. |
| [ADR-6](ADR-6-dark-petrol-reader.md) | Accepted | Restyle the stock reader as a dark petrol room with a centred column, hairline rules and a backdrop layer. |
| [ADR-7](ADR-7-character-brains-and-voice.md) | Accepted | Ship the voice method as a writer reference and character brains as a package that requires game-master layers 1 to 4. |
| [ADR-8](ADR-8-open-work-in-the-register.md) | Accepted | Keep open work in the groundwork register and plans, retire the progress note, and leave designs, reviews and drift reports to EGM. |
| [ADR-9](ADR-9-character-brains-plus.md) | Accepted | Keep method-only character-brains and add character-brains-plus, whose stdlib script and event log brief only what visibility classes and `know` events allow. |

For new decisions, copy one of the templates:

* [adr-template.md](../templates/adr/adr-template.md) — all sections with explanations.
* [adr-template-minimal.md](../templates/adr/adr-template-minimal.md) — mandatory sections with explanations.
* [adr-template-bare.md](../templates/adr/adr-template-bare.md) — all sections, empty.
* [adr-template-bare-minimal.md](../templates/adr/adr-template-bare-minimal.md) — mandatory sections, empty.

Name the file `ADR-n-title-with-dashes.md`, where `n` is the next consecutive number with no leading zeros, and start it with the heading `# ADR-n — Title`. Keep the title lowercase and use dashes. Cite a decision as `ADR-n`. Besides the MADR sections, a new decision needs a Y-statement line (`> In the context of …, facing …, we decided … to achieve …, accepting …`) and a Confirmation section; `node scripts/groundwork-check.mjs` enforces both ([ADR-5](ADR-5-adopt-groundwork-checks.md)). The `.markdownlint.yml` file holds the MADR lint adjustments.

Intermediate EGM brainstorming, drafts, reviewer reports, and drift reports are process evidence. Keep them in `docs/history/`, `docs/reviews/`, or another explicitly chosen artifact directory; do not place them in `docs/designs/` or this directory as if they were normative requirements.

Status changes to **Accepted** only after the project author approves the decision. Validation evidence belongs in [validation results](../validation-results.md), and open work in the [issues register](../issues.md), not in the ADR ([ADR-8](ADR-8-open-work-in-the-register.md)).
