---
status: accepted
date: 2026-11-16
decision-makers: Project author
---

# ADR-11 — Import every card variant and read the one SillyTavern reads

> In the context of `import-card` reading character cards from PNG files, facing real Chub downloads that carry two different `chara` chunks, which the helper refused as "Conflicting card definitions", we decided to import the card anyway: `card.json` and `card.md` hold the definition SillyTavern reads (the first `ccv3` chunk, else the first `chara` chunk), and every other distinct definition under that key is kept beside it as `card.2.json`, `card.2.md` and so on, listed in the receipt with the fields that differ, to achieve imports that work on cards as they are found and lose none of what the file holds, accepting that the helper's default may be the stale copy and that the writer must compare the variants and ask the Director when it matters.

## Context and Problem Statement

The design asked `import-card` to fail with an explicit error on "conflicting card definitions" ([design alternatives and plan](../history/design-alternatives-and-plan.md)). On 2026-11-16 a scratch import of four cards downloaded from Chub (`main_<slug>_spec_v2.png`) failed on all four: each PNG holds two `tEXt` chunks named `chara`, and they differ. In all four the first chunk is Chub's current export (version `main`, a Chub id, the linked lorebook), and the second is an older definition left over from the image the creator uploaded. Descriptions and first messages match; tags, creator notes, greetings and lorebooks differ. In one card the second chunk has no lorebook at all, where the first has six entries.

Nothing in a PNG says which definition is current. The order depends on the last tool that wrote the file: Chub seems to put its export first, while a tool that appends would put the newest last. A refusal leaves the writer with no way forward and no message saying what to do. How should the helper treat a PNG that carries more than one definition?

## Considered Options

* Keep refusing.
* Read the last chunk, as the most recently appended.
* Read the chunk SillyTavern reads, and keep every other definition as a variant for the writer.

## Decision Outcome

Chosen option: **read the chunk SillyTavern reads, and keep the rest as variants**, selected by the project author on 2026-11-16. The helper cannot know which definition the Director means, so it does not judge; it picks the same default as the program most cards are written for, keeps the others, and says so. SillyTavern's `src/character-card-parser.js` `read` takes the first `ccv3` chunk if there is one, otherwise the first `chara` chunk, comparing keywords without regard to case. Reading the last chunk would have dropped a whole lorebook from one of the four Chub cards.

* **The default.** The key is `ccv3` if any chunk has it, else `chara`, with keywords matched without regard to case. `card.json` and `card.md` hold the first chunk under that key. A legacy `chara` beside a `ccv3` is still not imported, with the warning it had before.
* **The variants.** Each later chunk under the same key whose content differs from every earlier one is decoded and written as `card.<n>.json` and `card.<n>.md`, numbered from 2 in file order. An identical repeat is not a variant. A variant that cannot be decoded is skipped with a warning; only the default must decode.
* **The receipt.** `import.json` and the printed receipt gain `variants`: one object per variant with `card_file`, `readable_file` and `differs`, the top-level card fields (under `data` for V2 and V3) whose values differ from the default. A warning says how many definitions the PNG holds and that `card.json` is the one SillyTavern reads. The helper reports differences as facts and does not rank the variants.
* **The writer.** The skill's imports page tells the writer that a card with variants holds more than one version, to compare them, and to ask the Director which one they meant when the differences matter. The answer goes in the story notes.

### Consequences

* Good, because cards downloaded from Chub import, and nothing the file holds is lost.
* Good, because the default matches what the Director sees when the same card is loaded in SillyTavern.
* Bad, because the default may be the stale definition, as it would be after a tool that appends; the writer has to notice the variants.
* Bad, because the import folder and the receipt grow for these cards.

### Confirmation

`tests/test_cards.py` imports a PNG with two different `chara` chunks and checks that `card.json` holds the first, `card.2.json` and `card.2.md` hold the second, and the receipt lists the variant and the fields that differ; that an identical repeat makes no variant; that a `ccv3` chunk still wins over `chara`; and that an undecodable variant is skipped with a warning while an undecodable default still fails. The skill's imports page and the [public contract](../public-contract.md) describe the variants.
