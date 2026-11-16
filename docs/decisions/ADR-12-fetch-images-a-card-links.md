---
status: accepted
date: 2026-11-16
decision-makers: Project author
---

# ADR-12 — Let the writer fetch images a card links to, through a helper

> In the context of character cards that embed extra images as links to remote files, facing a writer page that forbade fetching any remote asset and a reader that shows only PNG, we decided to add `card-image`, a helper that downloads one link found in an imported card, checks that it is a PNG, JPEG, WebP or GIF image, keeps the original privately and writes a copy without metadata to `public/assets/`, and to let the reader show those four formats, to achieve stories that can use the pictures a card's author meant to go with it, accepting a network fetch the writer starts, three more image formats the helper must check, and pictures that the card author, not the Director, chose.

## Context and Problem Statement

Cards often embed extra images: an expression sheet, a picture per greeting, a map. They do it with Markdown or HTML image links to remote files, since a card is one PNG or JSON file. The writer's imports page said "Never fetch remote assets or run scripts embedded in a card". That line came from the plan for the import helper, which must not reach the network while it unpacks a card nobody has read yet ([design alternatives and plan](../history/design-alternatives-and-plan.md)). Copied onto the writer's page, it became a ban on the writer too. Even with an image downloaded, the reader could not show it: its sanitizer drops remote images, and it serves only PNG files from `public/assets/`, while card images are often JPEG, WebP or GIF.

May the writer use the images a card links to, and how do they reach the reader?

## Considered Options

* Keep the ban.
* Let the writer download images with its own tools and publish them by hand.
* Add a helper that fetches a link from an imported card, checks it, keeps the original privately and publishes a copy without metadata; let the reader show PNG, JPEG, WebP and GIF.

## Decision Outcome

Chosen option: **a helper that fetches a card's link, and a reader that shows four formats**, selected by the project author on 2026-11-16. A helper keeps the checks in one place the way `portrait` does for the card's own picture: the writer cannot publish a file that is not an image, or one that still carries metadata. Downloading by hand would leave each writer to remember those checks.

* **Only the card's own links.** `card-image --source <import folder> --url <url>` refuses a URL that does not appear in that import's `card.json` or one of its variants. It never follows links found inside a downloaded page. The scheme must be `http` or `https`, the download is bounded to 32 MiB with a timeout, and the request names CouldHappen as its user agent.
* **Only images.** The format is read from the bytes, not from the URL or the server's `Content-Type`. PNG, JPEG, WebP and GIF are accepted after a structural check; anything else (SVG, HTML, an archive) is refused.
* **Private original, public copy.** The download is kept as `imports/<sha>/assets/<sha256>.<ext>` and recorded in `imports/<sha>/assets.json` with its URL. The copy in `public/assets/<sha256>.<ext>` has its metadata removed: PNG text and other non-appearance chunks, JPEG application and comment segments, WebP EXIF and XMP chunks, GIF comment and application extensions other than the loop count. Like a portrait, the copy is not shown until the writer refers to it in a story entry or the cast.
* **The reader.** Picture lines, cast portraits and the asset route accept `.png`, `.jpg`, `.webp` and `.gif`. The helper checks each referenced file's structure against its extension before serving it, with the matching `Content-Type`.
* **The writer.** The imports page replaces the ban: never run scripts in a card; fetch only images the card links to, only through `card-image`, and only when the story will use them. A card's images are the author's choice: the writer looks at each before showing it, and asks the Director before showing one that does not fit the story's agreed limits.
* **Still refused.** `import-card` reads local files only and never fetches. Scripts embedded in a card are never run.

### Consequences

* Good, because cards that rely on extra images can be played as their authors meant.
* Good, because every published image has passed the same checks, and the original stays with its import.
* Bad, because the writer starts network requests to hosts a card author chose, which reveals the player's address to those hosts.
* Bad, because three more image formats are parsed, each a place for a malformed file to be refused wrongly or accepted wrongly.

### Confirmation

`tests/test_images.py` checks that each format is recognised from its bytes, that metadata is removed while the picture's data is kept, and that malformed files and other formats are refused. `tests/test_cards.py` checks that `card-image` refuses a URL missing from the card and a non-image download, and keeps the original and the public copy (the network is replaced by a stub). `tests/test_files.py` and the shared picture-line fixture check that the four extensions are accepted and others refused, in Python and in the reader. The imports page, the capability page and the public contract describe the command.
