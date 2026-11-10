---
status: accepted
date: 2026-11-05
decision-makers: Project author
consulted:
informed:
---

# ADR-3 — License the package under AGPL-3.0-or-later

> In the context of publishing a package that agents modify during play, facing the risk of a closed, hosted version of a modified copy, we decided to license it under AGPL-3.0-or-later instead of MIT, to achieve modified copies that stay free with their source when they are shared or offered over a network, accepting that releases 0.1.0 to 0.1.6 keep their MIT terms and that outside contributions are AGPL.

## Context and Problem Statement

[ADR-2](ADR-2-publish-clean-release.md) chose MIT. Before the first public GitHub release, the author reconsidered. CouldHappen invites agents to modify its own helper and reader during play, and the misuse most worth preventing is a closed, hosted version of a modified copy. Which license should the package carry when it is published?

## Considered Options

* Keep MIT.
* AGPL-3.0-only.
* AGPL-3.0-or-later.

## Decision Outcome

Chosen option: **AGPL-3.0-or-later**, selected by the project author on 2026-11-05. Modified copies that are shared, or offered to other people over a network, must stay free with their source. "Or later" lets the package follow future versions of the license.

### Consequences

* `LICENSE` holds the unmodified AGPL-3.0 text, so GitHub detects it. `web/package.json` declares `AGPL-3.0-or-later`, and the README explains what it means for players.
* The license covers the package source, not a player's story or imported third-party card material.
* Agent modifications to the helper or reader are derivative work. Private use needs nothing; sharing them, including in Director prompts or packs that carry code, is under the same license.
* Releases 0.1.0 to 0.1.6 were MIT, and copies already made keep those terms. The project had a single author, so relicensing needed no other consent.
* Future outside contributions will be AGPL. If the author may later want to dual-license, contributors would need to sign a contributor agreement first.
* npm dependencies use permissive licenses compatible with AGPL. Bundled fonts keep their OFL notices.

### Confirmation

`LICENSE` holds the unmodified AGPL-3.0 text and GitHub detects it as AGPL-3.0. `web/package.json` declares `AGPL-3.0-or-later`, and the README's license section says what it means for players.
