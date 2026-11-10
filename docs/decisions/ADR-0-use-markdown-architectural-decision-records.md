---
status: accepted
date: 2026-11-05
decision-makers: Project author
consulted:
informed:
---

# ADR-0 — Use Markdown Architectural Decision Records

> In the context of a project that needs a durable record of why structural choices were made, facing a choice between running every decision through a full EGM design cycle and keeping no record at all, we decided to record decisions as MADR 4.0.0 files in `docs/decisions/`, to achieve explicit assumptions, consequences and a Confirmation target kept apart from the approved design, accepting that the project maintains two durable document types.

## Context and Problem Statement

CouldHappen needs a durable place to record packaging and workspace decisions without turning every decision into a full EGM design cycle. The approved design remains the normative product specification, but the project also needs to preserve why structural choices were made, the alternatives considered, and how compliance will be confirmed.

Which format and structure should these records follow?

## Considered Options

* [MADR](https://adr.github.io/madr/) 4.0.0 — Markdown Architectural Decision Records
* [Michael Nygard's template](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
* [Sustainable Architectural Decisions](https://www.infoq.com/articles/sustainable-architectural-design-decisions) — Y-Statements
* Other templates listed at <https://github.com/joelparkerhenderson/architecture_decision_record>
* Formless — no conventions for file format or structure

## Decision Outcome

Chosen option: "MADR 4.0.0", because it makes assumptions and consequences explicit, is lightweight enough for packaging decisions, includes a Confirmation section, and keeps decisions separate from the approved design specification.

The official MADR setup is used:

* decisions live in `docs/decisions/`;
* new files use `NNNN-title-with-dashes.md`;
* the MADR templates and lint configuration are retained locally;
* EGM design documents remain normative, while ADRs record rationale and alternatives.

### Consequences

* Good, because the project can record structural decisions without duplicating the design.
* Good, because the Confirmation section gives drift and acceptance checks a clear target.
* Neutral, because ADRs are a project convention, not an EGM requirement.
* Bad, because the project now maintains two durable document types: normative designs and decision records.

### Confirmation

A new structural decision is recorded using the local MADR template, linked from the [decision index](README.md), and reviewed for status and consequences. The [approved design](../designs/couldhappen.md) remains the reference for implementation requirements.

## More Information

* [MADR](https://adr.github.io/madr/)
* [Decision index](README.md)
* [Approved design](../designs/couldhappen.md)
