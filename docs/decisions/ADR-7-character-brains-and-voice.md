---
status: accepted
date: 2026-11-11
decision-makers: Project author
consulted:
informed:
---

# ADR-7 — Ship voice as a reference and character brains as a package

> In the context of a player-made package (erotic-sandbox) that bundled about seven methods, facing the choice of adopting it whole or not at all, we decided to take only its dialogue method, as a writer reference, and its character-brain protocol, as a package that requires game-master layers 1 to 4, to achieve reusable parts that work in any setting, accepting that the rest of the package is declined.

## Context and Problem Statement

erotic-sandbox carried a voice method for dialogue, a casting method, a sample social ruleset, a character-brain protocol for subagents, an image method and style prefix, session-zero and story-state templates, and a full reader. About a third duplicated rpg-mechanics, scene-images and game-master. Two passages could not be adopted as written: an instruction to work around an image provider's refusals, and an age band below 18 in an erotic package.

## Considered Options

* Adopt the package whole.
* Split it into several packages.
* Take only the parts that are reusable in any setting, each in the form that fits it.

## Decision Outcome

Chosen option: **take the reusable parts**, selected by the project author on 2026-11-11.

* **Voice** becomes `references/voice.md` in the writer skill. It is craft every story needs, costs nothing, and changes no file, so it is not a package. The skill links it where dialogue is written.
* **Character brains** becomes the `character-brains` package. It requires game-master with layers 1 to 4 on: a brain's sheet is the layer 3 cast card, its open threads come from layer 2, and what it may know is limited by the layer 4 truths. Applying it asks the Director how many characters keep a persistent brain and how many brain calls a turn may make.
* **The reader** is covered by [ADR-6](ADR-6-dark-petrol-reader.md).
* **Declined:** casting (players decide their own cast conventions), the social ruleset (players design stats for their story with rpg-mechanics), the adult image method and style (setting-specific), session zero and story state (game-master already has them).

### Consequences

* Good, because each part arrives in the smallest form that does the job, without duplicating stock packages.
* Good, because brains reuse game-master's records instead of keeping a second sheet.
* Bad, because brains cannot be used without game-master, even in a light story.

### Confirmation

`tests/test_skill_docs.py` passes: the reference is linked from `SKILL.md`, and the package is in `packages/INDEX.md` with its `PACKAGE.md` and `APPLY.md`. Neither shipped file contains the provider workaround or an age below 18.
