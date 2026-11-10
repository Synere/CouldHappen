---
status: accepted
date: 2026-11-11
decision-makers: Project author
consulted:
informed:
---

# ADR-6 — Restyle the stock reader as a dark petrol room

> In the context of a stock reader whose pale petrol page with prose cards read more like a dashboard than a place to read, facing a player-built reader (from the erotic-sandbox package) that played much better in long sessions, we decided to adopt that reader's structure as the stock design, recoloured in dark petrol and saffron, to achieve a quieter reading room that keeps the brand colours, accepting that DESIGN.md's Honest Ground Rule is replaced and the published screenshots are out of date until they are retaken.

## Context and Problem Statement

A player-made package, erotic-sandbox, shipped six full reader files. Its reader has a centred reading column with no prose cards, hairline role rules with small uppercase labels, a drop cap, a quiet topbar and cast rail, and a faint blurred scene picture behind the text. It played much better than the stock reader. Its palette was warm brown and dark, which went against the Honest Ground Rule in [DESIGN.md](../../DESIGN.md) ("no full-bleed dark prose field").

The package replaced whole files, so on a newer release a writer would have to diff before applying, and it also carried the patches from rpg-mechanics and scene-images. Taking the design into the stock reader removes the copying and keeps it current.

## Considered Options

* Keep the stock reader and leave the new look to packages.
* Adopt the new structure and its warm brown palette as the stock design.
* Adopt the new structure in a light petrol palette.
* Adopt the new structure in a dark petrol and saffron palette.

## Decision Outcome

Chosen option: **the new structure in dark petrol and saffron**, selected by the project author on 2026-11-11. It keeps the dim-room feel that made the new reader work, and the colours that identify CouldHappen.

* `web/src/styles.css` takes the structure from the package. The ground is a near-black petrol, prose is pale cool ink, petrol carries structure and saffron marks the event. The Two-Accent Rule stays.
* Colours are variables, so a sheet theme (scene-images) can recolour the whole reader. The variable names (`--petrol`, `--saffron`, ...) stay as role names, so the existing theme mapping still works.
* The stock stylesheet carries the rules for the sheet panel, quick actions and the backdrop layer. They do nothing until rpg-mechanics part 3 or scene-images adds the markup or sets `--backdrop`. The markup and the theme code stay in those packages.
* The scene-images theme step gains an accent sampled from the newest picture. The warm brown palette is kept as an example theme there.
* The role labels are "You" and "Writer", and the two-diamond knot is gone.

### Consequences

* Good, because the stock reader is the one players liked, without a full-file replacement package.
* Good, because the brand colours and the two-accent rule survive.
* Bad, because the screenshots in the README and on GitHub show the old reader until they are retaken.
* Bad, because a story that patched the old stylesheet must reapply its patch against the new one.

### Confirmation

`DESIGN.md` describes the dark petrol reader and no longer carries the Honest Ground Rule. `npm run check`, `npm run build` and the browser tests in `web/` pass. The reader was looked at in a browser at desktop and phone width, with and without a sheet theme and backdrop.
