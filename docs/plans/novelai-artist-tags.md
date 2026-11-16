---
type: plan
status: completed
updated: 2026-11-16
---

# NovelAI artist tags

**Purpose.** Let the writer give a story's NovelAI pictures an art style through Danbooru artist tags in `notes/style.txt`, matched by default to the story's reference image. Follows the completed [NovelAI images plan](novelai-images.md). Ends when ISS-39 is closed in the [issues register](../issues.md), or when the idea is abandoned.

## ISS-39 — Artist tags in the NovelAI style block

Raised by the author on 2026-11-16. Until now the guide only kept artist tags the Director gave, word for word. Decisions from the author (2026-11-16):

- **Who picks:** the writer proposes and the Director chooses. By default the writer tries to match the art style of the story's reference image, usually the imported card's PNG or an image embedded in the card.
- **Checking:** NovelAI's tag suggester does not complete artist tags. `nai_tags.py --artist` asks Danbooru's public tag API for artist tags (category 1) instead, with an honest user agent and no account.

Facts checked on 2026-11-16:

- **Syntax:** NovelAI writes artist tags as `artist:<name>`, lowercase, with spaces instead of underscores ([V4 curated preview notes](https://journal.novelai.net/release-novelai-anime-diffusion-v4-curated-preview-en-ca4b0b11e671/), [V4.5 full release](https://journal.novelai.net/novelai-diffusion-v4-5-full-release-678318c86205/)). The notes say the tag is strong and can be weakened.
- **Danbooru API:** `GET https://danbooru.donmai.us/tags.json?search[name_or_alias_matches]=<name>*&search[category]=1&search[hide_empty]=true&search[order]=count` answers without an account and returns `name`, `post_count`, `category` and `is_deprecated`.

Delivers:

- **`nai_tags.py --artist NAME ...`:** artist tags from Danbooru, the exact match marked, each shown as it goes in a prompt (`artist:ningen mame`) with its post count.
- **`nai_tags.py --png FILE`:** any `artist:` tags in a PNG's embedded text, such as the prompt NovelAI stores in its own pictures, as first candidates.
- **The core page:** how to propose, check, try and record artist tags. The writer never claims a reference was drawn by a given artist.
- **Reverse page:** an embedded prompt's artist tags are style candidates.
- **APPLY:** a pointer to the core page.

Done when the helper's offline tests pass and a style proposal from a card portrait has been tried in a story.

**Closed 2026-11-16, not yet observed in a story.** `nai_tags.py --artist` and `--png`, with offline tests; `--artist` was also tried against Danbooru itself (`ningen mame` 634 posts, `wlop` 403, both exact) and `--png` on a NovelAI picture from the ISS-38 check, which correctly reported no artist tags (its prompt had none). The core page's "Choosing artist tags", and pointers in the danbooru and reverse pages, APPLY and PACKAGE. A style proposal from a card portrait has not been tried in a story yet.
