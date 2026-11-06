# Public contract v1

The current writer owns story interpretation and direct edits. The helper owns serialized browser appends and cooperative edit controls. Neither helper nor frontend calls models or manages sessions. Private organization is freeform. This contract is the normative runtime agreement for the workspace; the upstream design documents provide product and implementation rationale.

`couldhappen.json` has schema_version 1, a workspace UUID that the helper initializes once, when it first starts (claiming does not create it), poll_interval_ms (1000), and checkpoint scope/exclusions. Browser snapshots contain the UUID, never the absolute root or control secret.

## Conversations and public records

`public/story.md` starts `# Story`; `public/director.md` starts `# Director`. Outside entries only blank lines are valid. Entries are UTF-8/LF (CRLF accepted):

```text
<!-- couldhappen:entry {"id":"canonical-UUID","role":"human","status":"pending"} -->
Body, including ordinary paragraphs.
<!-- couldhappen:end -->
```

Writer role omits status. Human status is pending, addressed, or deferred. Canonical UUIDs are unique across both logs and survive revisions. Preserve human role/body when changing disposition. Addressed is not proof of compliance or expiry of guidance. Metadata updates never constitute new input.

Reserve lines beginning `<!-- couldhappen:`. Prefix one backslash to any body line with zero or more backslashes followed by that prefix; decoding removes exactly one. Serialization inserts exactly one newline between body and end marker; parsing removes exactly that separator, preserving the body's own trailing newlines. Normalize CRLF/CR to LF. `entry --body-file` encodes arbitrary text safely; it prints only and does not bypass editing coordination.

`cast.json` contains schema_version 1 and characters: stable nonempty string id, disclosed name, optional description, optional portrait relative to public/assets. Only referenced existing structurally valid PNGs within that resolved root are exposed. No card is required for a character. Import/preparing a portrait does not add cast. An optional top-level `portrait_button` boolean makes the Cast panel offer a "Make portrait" button for each character; pressing it saves one Director entry (`Make a portrait for <name> (cast id <id>).`) and nothing else.

A story or Director entry may attach a picture with a line of its own, `![caption](/api/assets/<name>.png)`, outside code fences. The reader shows it as a figure with the caption under that entry, with a click-to-enlarge view. Each named PNG is checked like a portrait and added to the snapshot `assets`; a missing or invalid one makes the snapshot invalid.

`work.json` contains schema_version 1, mode play or awaiting_director, and director_question_id. Play requires null; awaiting_director requires the UUID of an existing writer entry in Director. The writer establishes that it is a new question and reconciles old pending work. No second disposition map exists.

Malformed entries, duplicates, partial saves, invalid cast references, and incompatible work states close saving. The helper retains its last coherent view and reports a public validation error. Validation is not proof of fictional continuity.

## Browser API

Both services bind loopback. Vite proxies only these routes, with changeOrigin for the helper Host; mutations require the configured frontend Origin. No wildcard CORS. No private filesystem or command endpoint is exposed. Vite itself answers 403 for `/@fs/`, `/control`, any other `/api/` path, and any path with a segment named `imports`, `public`, `.couldhappen`, `.git`, `.env*`, or `START_HERE.md`; its file-serving deny list repeats the same names. A malformed percent-encoded path gets 400.

| Route | Behavior |
| --- | --- |
| GET /api/snapshot | schema/workspace/generation, revision, Story/Director parsed entries and body_hash, cast, asset hashes, work, permissions per channel, validation_error, poll_interval_ms. If-None-Match supports quoted revision ETags and 304. |
| POST /api/entries | Exact fields schema_version, workspace_id, generation, channel (story/director), UUID id, body. Assigns human/pending. 201 only after save; identical canonical ID/channel/body returns 200. Receipt means saved, never applied. |
| GET /api/assets/name.png | Only a referenced resolved public PNG. The path is resolved under the asset root; PNG signature, chunk lengths/CRCs, critical structure, and the 32 MiB read bound are checked before hashing or serving. No traversal, encoded escape, private import, or symlink escape. Asset query hash comes from snapshot content. |

Bodies normalize LF, reject whitespace-only, and have a 256 KiB UTF-8 limit. Total JSON is bounded to accommodate escapes. Stable JSON errors contain code and message: 400 invalid_input, 403 host_denied/origin_denied/control_denied, 404 not_found (unknown route) or asset_denied (a PNG that is unreferenced, missing, or fails validation), 409 stale_generation/id_conflict, 413 body_too_large, or request_too_large (JSON over the bound, or a missing or negative Content-Length), 423 saving_closed, 503 save_failed/control_failed. Failed/uncertain saves retain drafts.

The helper resolves an existing request ID and body against both canonical logs before it checks whether saving is open, so a retry of an already-saved entry returns 200 even while saving is paused, blocked, or awaiting Director direction; a conflicting reuse returns 409 id_conflict. A new ID still needs saving to be open. Reuse the same immutable payload after uncertain receipt only in the same generation. A generation change requires a fresh snapshot; an absent old ID is never permission for automatic replay, and the browser retains the text for deliberate submission. The browser keeps unsent drafts for the life of its tab (session storage). A new generation or permission/error/content change changes revision.

## Writer controls

The loopback `/control` POST requires the private runtime bearer secret and refuses browser Origin. The CLI reads that secret locally. Vite never proxies this route. Runtime files under .couldhappen are not durable story authorities.

The state machine starts closed, even on restart. `writer claim` validates public state and arms checkpoint scope for play; existing interrupted ownership requires `writer recover --previous-writer-stopped`. This assertion records a boundary established through actual host tools; no age/PID check proves safety. A separate OS lock prevents concurrent helpers. Interrupted lock recovery uses serve --previous-helper-stopped only after that boundary has been established.

`writer pause` first closes new acceptance under the state lock, drains already accepted serialized saves, then acknowledges with an opaque token. Only after acknowledgment reread both logs. While paused, snapshots retain coherent conversation content. Direct edits use ordinary tools. `writer release --token` requires current ownership (not closing), the matching token, and successful full validation, refreshes the snapshot, then reopens according to remaining controls. `writer block --on/--off` independently controls both channels during prose production. Reveal and private work do not control permissions.

`writer invalidate --token` rotates generation under an owned pause; the token remains valid. `writer recover --previous-writer-stopped` drains saving, validates, rotates generation, and explicitly clears abandoned edit/production controls while claiming safe ownership. It does not clear awaiting_director. `writer close` closes acceptance, drains accepted saves, validates the public records, checks Git, and disarms only on a valid, clean result. It never commits. `stop` (control operation `stop`; CLI `python -m helpers stop`) drains accepted saves, persists controls, and shuts the helper down so it releases its OS lock; it reports whether ownership was still held, in which case the next start needs `writer recover`.

The control operations are `claim`, `recover`, `pause`, `release`, `block` (with on/off), `invalidate`, `close`, `stop`, and `wait-view`. `wait-view` is the read-only operation behind `wait`: it returns the generation and the eligible pending references, an empty list while paused, and refuses an invalid or unowned workspace. Use `wait --timeout 0` for no helper deadline, or a positive host-compatible timeout. It locally checks about every 500 ms, returning pending channel/ID references with generation (exit 0), quiet timeout (3), or recovery/error (2). While paused it waits for release. In recovery it returns only pending human Director entries following the question; old Story/Director input cannot authorize replacement fiction. The active agent must service waits/renewals and keep one standing (setup step 9); a helper never wakes an idle agent.

## Other commands

All commands print one JSON object. Exit 0 is success, 1 is a dirty checkpoint, 2 is an error (`{"status":"error","message":...}`), and 3 is a quiet wait timeout.

* `checkpoint check` is read-only. It reports `clean` (exit 0) or `dirty` (exit 1) with the changed `paths` inside the configured scope and exclusions, or `error` (exit 2), including for unmerged paths. `checkpoint inspect --ref <commit>` reports `ok` with the commit, the paths it recorded within the same scope, and recent history for that scope, or `error`. Neither command commits.
* `import-card --source <png-or-json>` reads a local card (no archives or remote assets), stores a content-addressed copy under `imports/<sha256>/`, and prints the receipt: `path`, `source_path`, `source_sha256`, `format`, `result`, `warnings`, `source_name`, `source_file`, and `readable_file` (`card.md`, a lossless plain-text copy of every field and lorebook entry). Imports are private; they never add cast.
* `portrait --source <png>` writes a portrait PNG (the card's appearance chunks only) to `public/assets/` from an already imported card: the source is the preserved `imports/<sha256>/source.png`, its folder, or the original card file once `import-card` has imported it. It never imports implicitly. It prints `portrait` (the filename to put in `cast.json`), `sha256`, `disclosed` (false until the writer discloses the character), and `source_path`. A source that is not an imported PNG card returns `error` with guidance to run `import-card` first.

## Recovery and compatibility

Under an acknowledged pause, stop/account for relevant work, inspect real history, reconcile requested fiction and assumptions, preserve applicable guidance and useful improvements by default, defer old unresolved inputs as appropriate, append explanation plus a new Director question, set awaiting_director, rotate generation, validate, release. Only Director saving reopens; the writer interprets new direction before clearing the mode. Invalid pointers remain closed. There is no automatic Git reset, replacement passage, intent classifier, or exact per-turn Undo promise.

Incompatible format/interface changes update this contract and all consumers within the same pause/reopen boundary. Ordinary content, cast, private-method, and visual changes do not require migration. Python edits normally require restart; Vite handles compatible HMR. Verify both actual services afterward. Helper atomic saves write/flush/replace before receipt; no cross-file transaction or protection from uncooperative writers is promised.
