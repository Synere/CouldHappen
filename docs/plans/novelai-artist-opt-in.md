---
type: plan
status: completed
updated: 2026-11-16
---

# NovelAI artist tags: opt-in, checked against real pictures

**Purpose.** Make artist tags something the writer offers only when there is a reason, and check its picks against the artist's real work instead of its memory. Follows the completed [artist tags plan](novelai-artist-tags.md). Ends when ISS-41 is closed in the [issues register](../issues.md).

## ISS-41 — Artist tags by default off, with sample pictures

Raised by the author on 2026-11-16 after ISS-39: a story should use no artist by default, and the writer's memory of what an artist's work looks like is unreliable. Decisions from the author (2026-11-16):

- **Default:** no artist tags. The writer offers them only when the Director asks for a style, or when the card PNG's embedded prompt names artists (`--png`). Even then it offers, never applies.
- **Sample pictures:** `nai_tags.py --artist NAME --samples DIR` saves each exact artist's top-scored Danbooru pictures (`order:score`) as 360-pixel previews, so the writer can compare them with the reference before naming the artist. Every content rating is included and the samples are sorted by Danbooru score, as the author asked: some good artists draw only adult work, and only the style matters. Previews are fetched only from Danbooru's own hosts.
- **Free test portraits** stay the final check, since NovelAI's reading of a tag can differ from the artist's own pictures.

Facts checked on 2026-11-16: `GET /posts.json?tags=<name> order:score` answers without an account, and each post's `media_asset.variants` holds a `360x360` preview on `cdn.donmai.us`.

Done when the helper's offline tests pass and the guide pages say artist tags are off by default.

**Closed 2026-11-16, not yet observed in a story.** `--samples` with an offline test, and a live run that saved four `ningen mame` previews, which opened as images. The core page's "Choosing artist tags", APPLY, PACKAGE and the reverse page now make artist tags opt-in.
