---
status: accepted
date: 2026-11-16
decision-makers: Project author
---

# ADR-10 — Bundle pages adapted from nai5-prompting under GPL-3.0-only

> In the context of the NovelAI provider for scene-images, whose prompt guide is adapted from Miint-Sunny's nai5-prompting (GPL-3.0-only), facing a release licensed AGPL-3.0-or-later that would carry third-party GPL text, we decided to ship the adapted pages as a separately licensed GPL-3.0-only folder, `packages/scene-images/nai/`, combined with the AGPL work under GPLv3 §13 and AGPLv3 §13, each page keeping the source's copyright line, licence identifier, source link and a modification notice, with the source's NOTICE and the GPL-3.0 text beside them, to achieve a guide that keeps nai5-prompting's tested rules while honouring its licence, accepting that one folder of the release is under a different licence from the rest and that every page there must keep its notice.

## Context and Problem Statement

The [NovelAI images plan](../plans/novelai-images.md) (ISS-32) adds a NovelAI provider to the `scene-images` package and a guide that turns the story's prose into Danbooru tags. The rules in that guide come from [nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting) v1.2.8, Copyright (C) 2026 Miint-Sunny, licensed GPL-3.0-only. Its plan table names the exact source sections. CouldHappen is AGPL-3.0-or-later ([ADR-3](ADR-3-license-agpl.md)) and ships as a release ZIP that includes everything under `.agents/skills/couldhappen/` ([ADR-2](ADR-2-publish-clean-release.md)). Can the release carry pages adapted from GPL-3.0-only text, and what must travel with them?

## Considered Options

* Bundle the adapted pages in their own GPL-3.0-only folder, combined under §13 of both licences.
* Write the guide from scratch from NovelAI's own docs, with nothing adapted.
* Bundle nothing and tell the Director to install nai5-prompting themselves.

## Decision Outcome

Chosen option: **bundle the adapted pages in their own GPL-3.0-only folder**, selected by the project author on 2026-11-16 in the plan. GPLv3 §13 lets a GPLv3 work be combined with an AGPLv3 work into a single combined work, and AGPLv3 §13 says the same from the other side. CouldHappen's "or later" lets the combination take AGPL version 3. Each part keeps its own licence: the adapted pages stay GPL-3.0-only, and the network clause of AGPLv3 §13 covers the combination. Writing from scratch would lose rules the source has already tested against V5, and leaving it out would make every Director install a 500 KB skill for a few pages' worth of rules.

* **One folder.** Every adapted page lives in `.agents/skills/couldhappen/packages/scene-images/nai/`. Nothing outside that folder is adapted from nai5-prompting; CouldHappen's own text, the provider script and the tag helper stay AGPL-3.0-or-later.
* **Each page's notice.** Every page in the folder opens with a quoted notice block that keeps the source's copyright line (`Copyright (C) 2026 Miint-Sunny`), `SPDX-License-Identifier: GPL-3.0-only`, the source link, and a statement that the page was modified for CouldHappen, with the date and what changed. That statement is the "prominent notice" GPLv3 §5(a) asks of a modified version. A modified page is GPL-3.0-only as a whole (§5(c)), our additions included.
* **What sits beside them.** `nai/NOTICE.md` carries the source's project notice (copyright, author, source, licence, warranty disclaimer) and says which source sections each page adapts. `nai/LICENSE-GPL-3.0.txt` is the GPL-3.0 text copied unchanged from the source.
* **Left out.** Nothing from the source's `background.md` is adapted, so its separate MIT notice for Fanfic-background-assistant does not apply. If a later page takes from it, that page carries the MIT notice too.
* **How the release carries them.** The release manifest already includes `.agents/skills/couldhappen/**`, so the folder ships as it is, and the `.claude/skills/` mirror copies it. The repository README's licence section names the folder and its licence.
* **NovelAI-Image-MCP.** The provider script and the tag helper take only facts from it (endpoint names, the response shape), no code. They credit it (MIT) in a comment.

### Consequences

* Good, because the guide keeps rules and examples the source tested against V5.
* Good, because the licence boundary is a folder, easy to check and to keep.
* Bad, because one folder of the release is GPL-3.0-only while the rest is AGPL-3.0-or-later, and anyone reusing that folder alone must follow GPL-3.0-only.
* Bad, because every page added to the folder must carry the notice, and an edit to a page should update its modification line.

### Confirmation

`tests/test_skill_docs.py` checks that every Markdown page in `packages/scene-images/nai/` other than `NOTICE.md` opens with the notice block (the copyright line, the SPDX identifier, the source link and a modification statement), and that `NOTICE.md` and `LICENSE-GPL-3.0.txt` are in the folder. The README's licence section names the folder.
