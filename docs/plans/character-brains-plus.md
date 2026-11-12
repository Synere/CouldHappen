---
type: plan
status: proposed
updated: 2026-11-13
---

# Character brains plus

**Purpose.** Build `character-brains-plus`, a second brain package with a script and an event log, so a brain is briefed only with what its character could know and keeps its own body, mood, beliefs and plans ([ADR-9](../decisions/ADR-9-character-brains-plus.md)). Ends when ISS-24 to ISS-30 are closed in the [issues register](../issues.md), or when the plan is abandoned.

The findings F1 to F14 are from an external design brief the author keeps outside this repository. The author accepted F1 to F13 on 2026-11-12, F12 as protocol text only, and deferred F14 (answer parser, audit command, cost ledger, built-in selftest). The method-only `character-brains` package stays and took the script-free fixes on 2026-11-12: the F12 text, a `DECIDES` key, and an optional `desire` line. The sections below carry what each ticket needs, so the brief is not required to do the work.

Every ticket edits only `.agents/skills/couldhappen/packages/character-brains-plus/` (the release builds the `.claude` copy), adds tests under `tests/`, and updates `packages/INDEX.md`, the skill's `SKILL.md` and `references/what-this-can-do.md` when a command is added. No public file, helper or reader code changes.

## ISS-24 — Knowledge isolation

F1, F2, F3 and the F12 text. The core every other ticket builds on.

**Done 2026-11-13.** Choices made where the text above left room, for the later tickets to build on: `brief` prints one JSON object like every command and `--text` prints the bare brief; `add` also takes `--age` and `--threads` (the `knows_threads` list, replaced whole); `char`, `world`, `session` and `compress` are the setup events whose `entry` may be null; every command rewrites the views, since a view also follows game-master; besides refusing a scene file, `brief` refuses to emit any text holding an entry id, a fact-shaped id, a game-master id or a file path. Undo was manual until ISS-25 added `reconcile`. New ops go in `VALIDATE` and `FOLD`, new brief sections in `BRIEF_SECTIONS`, new answer keys in `ANSWER_KEYS`.

- The package folder, `PACKAGE.md` and `APPLY.md`, and its row in `packages/INDEX.md` beside the method-only package, saying when to pick which. The two cannot be installed together: plus refuses over method-only brain files unless it migrates them (ISS-25), and the method-only `APPLY.md` refuses when `notes/brains/events.jsonl` exists.
- `files/brains.py`, installed as `tools/brains.py`: stdlib only, same conventions as `gm_state.py` (`--root .`, one JSON object out, exit 0 ok, 1 warning, 2 error). Reads game-master state by replaying `notes/gm/deltas.jsonl` through `gm_state.py`, never by copying it.
- `notes/brains/events.jsonl`, append-only, one object per line: `seq`, `at`, `npc`, `op`, `entry` (the story or Director entry that justifies it, `null` only for setup), `why`, `data`. Each command validates its event before appending.
- Commands: `init`, `add` (identity, look, aliases, card snapshot with `card_at`), `world <fact> --visibility public|witnessed|private|secret [--witnesses]`, `world --audit`, `know` (with `how`, first person, and `confidence`: `certain`, `probable`, `suspects`, `doubts`), `unlearn`, `remember`, `compress`, `session`, `brief`, `view`, `check`.
- Visibility: no record means hidden from every brain. `witnesses` is required for `witnessed`, `private` and `secret`. `check` fails on an unclassified game-master fact. The `known` flag is never read by the builder.
- `brief <npc> --scene FILE [--as ALIAS]`: allowed facts are public ones, ones the npc witnessed, and ones with a `know` event, less `unlearn`, less outdated or discarded facts. Threads only from the npc's `knows_threads` list. At most six episodes by salience then recency. No fact ids, entry ids or file paths in the output. Refuses a scene file with a line starting `FACT ` or a raw entry id. Same state gives a byte-identical brief.
- Views: `notes/brains/<npc id>.md`, starting `<!-- generated from events.jsonl; do not edit -->`, rewritten by each command.
- `files/PROTOCOL.md`, starting from the method-only protocol and rewritten around the script: never hand-assemble a brief; classify each new fact at the end of the turn; and, plainly, that a character played from the file knows too much, so keep scenes with more characters than the budget short. `files/scene-template.md` for the perception-only scene file. `files/brain-template.md` describes the generated view.
- Tests: a 20-fact fixture where the brief holds exactly the public, witnessed and `know` facts; a `known: false` fact stays out unless known, even when the character is tagged and present; another character's secret stays out.

## ISS-25 — Migration and Undo

F13, and moving a story from the method-only package.

**Done 2026-11-13.** Choices made where the text above left room: `migrate` takes `--entry` for the `remember` events it writes and defaults to the last story entry; a `## Knows` line keeps its own entry when it names one, and is skipped with a warning when that entry is gone; a `DIGEST:` line under `## Memory` also becomes a salience-4 summary, other memory items are salience 3, and a memory over 300 characters is split at sentence ends, never cut; `## Desire`, `## Sheet` and unknown sections stay in the legacy copy only, with a warning (ISS-26 owns the desire field); migrate stages every event before it writes the log once, then deletes each original, whose copy is in `legacy/`. A migrated `know` has `how: "migrated"`, which the brief never prints. `reconcile` mirrors game-master's: an event is set aside when its entry is gone, or when what is left no longer supports it (its character, its fact or thread in game-master, the fact an `unlearn` removed, the episodes a `compress` folded), and a fact gone outdated since is not a reason. `brief` refuses while any event cites a missing entry. A new seq is one past every seq in the log and in `withdrawn.jsonl`, and a view whose brain was set aside is deleted.

- `migrate`: reads a method-only brain file (`session`, `tier`, `## Look`, `## Desire`, `## Knows`, `## Memory`, `## Digest`, and a `## Sheet` if present), copies it to `notes/brains/legacy/` first, writes `char`, `session` and `remember` events, and turns the digest into a salience-4 summary. It never invents a `know` event and warns that fact ids must be added by the writer. `## Knows` lines that name a fact id become `know` events with `how: "migrated"`.
- `reconcile [--apply]`: sets aside every event whose entry is withdrawn or missing, and any event that depends on one, into `notes/brains/withdrawn.jsonl`. The protocol's Undo steps run `gm_state.py reconcile` first, then this.
- Tests: a method-only file keeps every memory bullet; an event citing a withdrawn entry leaves the brief.

## ISS-26 — Body, mood and desire

F7 and F8.

**Done 2026-11-13.** Choices made where the text above left room: a state path is dotted (`affect.fear`, `body.marks.burn.seen_by`) and every field is declared in `STATE_SCHEMA`, where a per-person group is a `('keyed', {...})` entry like `body.marks`, ready for ISS-27's edges and ISS-28's `routine`; `state` events hold an ordered list of `[path, value]` pairs, an empty value clears, and one bad pair refuses the whole event. Body fields and every desire field are short texts (`appetite` too); a mark has a text and a `seen_by` of `anyone`, `close`, `nobody` or cast ids, and `reconcile` sets aside a mark seen by someone no longer cast. `add --baseline` sets levels only (not `mood`), merged with any earlier baseline; a level with no baseline settles to 0, energy to 3, and a level that was never set and has no baseline is absent. `tick` is its own op, recomputed on replay, so after a reconcile it eases what is left; a tick with nothing to move records nothing. In the brief, valence reads as `spirits` (wretched, low, a little low, a little lifted, good, elated), a level at 0 is left out except energy, the body and affect go in a HOW THEY ARE section after WHAT THEY KNOW, and DESIRE follows it, before NOW. `migrate` still leaves a `## Desire` line in the legacy copy, now with a warning saying how to record it with `state`, since splitting it by guesswork could lose a limit.

- `state <npc> --set path=value`: `affect` (mood text; `valence` -3 to 3; `energy`, `pain`, `fear`, `shame`, `arousal`, `intoxication` 0 to 5), `body` (`condition`, `marks` with who can see them, `clothes`, `carrying`, `capacities`) and `desire` (`orientation`, `appetite`, `wants`, `limits`, `never_admits`, `shame`, `aftercare`, `turn_offs`, `current`). A `baseline` set at `add`.
- `tick <npc>`: each affect field one step toward baseline; `pain` and `intoxication` only at a scene boundary.
- The brief prints words, never numbers (0 none, 1 a little, 2 some, 3 a lot, 4 badly, 5 overwhelming), omits empty fields, and puts `desire` before `NOW`. The protocol says `limits` is authoritative and the writer cuts output that crosses it.
- No age gate in this ticket; that is ISS-30.

## ISS-27 — Beliefs, claims and other minds

F4, F5 and F6.

**Done 2026-11-13.** Choices made where the text above left room: a belief is keyed by its seq, `--retire SEQ` drops one and, given with `--text`, replaces it in one event; `--about` names any game-master fact (the brief prints neither it nor the truth label) and beliefs appear in a WHAT THEY BELIEVE section after WHAT THEY KNOW. A claim takes an optional `--about`; a `lie` must be `false` and a `truth` `true`. Two claims contradict when the same character told the same person something about the same `about` fact, one `true` and one `false`; `unknown` or no `about` never contradicts, and both `claim` and `check` warn. The brief picks six claims by listener present, then newest, so a present listener's older claim beats an absent one's newer; the player always counts as present, and a cast member is present when their id, name or alias is in game-master's `situation.present`. Edges are a `people` group in `STATE_SCHEMA` (`('keyed', spec, 'person')`, with `thinks_knows` a `('keyed', ('choice', ...), 'fact')` group); a keyed group's third element names what its keys must be, checked when a value is set. People are ranked present first, then by the last state event about them; propositions show `doesnt`, then `unsure`, then `knows`, and only facts the character still holds, so an unlearn takes one out of the brief (`check` warns). Edge levels read none, a little, some, a lot, deeply, utterly, and debt nothing to everything. `reconcile` sets aside a retire of a set-aside belief, a claim to or edge about someone no longer cast, and anything about a fact game-master no longer has.

- `believe`: text, a `truth` label (`true`, `false`, `unknown`) the brief never prints, `confidence`, optional `about`, `--retire`. At most 12 active.
- `claim --to player|N2`: text, `truth`, `kind` (`lie`, `truth`, `half-truth`, `promise`, `threat`, `boast`, `omission`). `check` warns when a claim contradicts an earlier one to the same person. The brief prints the last six, people present first.
- Edges in `state`: per person `trust`, `attraction`, `fear` 0 to 5, `debt` -5 to 5, `last`, and `thinks_knows` (up to four facts, each `knows`, `doesnt` or `unsure`), only about facts the character knows exist. The brief prints at most three people, two propositions each.
- Tests: a false belief appears with no label; a `thinks_knows` about a fact the character cannot know is refused.

## ISS-28 — Agency and life off-screen

F10 and F11.

**Done 2026-11-13.** Choices made where the text above left room: the answer block is `NOTICES`, `WANTS`, `HIDES`, `SAYS`, `DOES`, `TELL`, `BODY`, `UNSURE`, `REMEMBERS`, `DECIDES`, and the last four end "or (nothing)" (`DECIDES` said "(none)" before). A want is keyed by its seq like a belief, with a `--weight` 1 to 5 that ranks it and is never printed; the brief's WHAT THEY WANT gives the top two by weight, then newest, each with its conflict as "(but: ...)". An intent's horizon orders WHAT THEY MEAN TO DO (now, scene, day, long, then oldest); `--done SEQ` or `--drop SEQ` closes one, and with `--text` closes one and adds one in a single event. `veto --kind` is `leave`, `refuse`, `later` or `other`, with `--reason`, an optional `--decides` and `--intent SEQ`, which closes that intent as `vetoed`; the brief never shows a veto. Every `want`, `intent`, `veto` and `offscreen` event stores `data.scene`, game-master's `scene_count` when recorded, and closed intents keep `closed_seq` and `closed_scene`, for ISS-29's ten-scene veto count and stale intents. `routine` is a `('keyed', TEXT)` state group of at most six slots, printed as THEIR DAYS only in the off-screen brief. The off-screen setting is a `settings` setup event (`settings --offscreen on|off`, off by default). `brief --offscreen` (scene file optional) places the character "between scenes, away from the player", counts nobody as present (so claims and people rank by recency), drops the place from NOW, and asks `DOES`, `LEAVES`, `DECIDES`, `CHANGES`; `offscreen <npc> --does ... --entry E` records `DOES` as an episode (salience 2) and uses up that boundary, so a second brief or record at the same `scene_count` is refused. `reconcile` sets aside a retire or close of a set-aside want or intent, a veto closing one, and a want, intent or belief that would pass its cap once a retire it relied on is gone (the belief case was a gap in ISS-27).

- Answer block gains `BODY`, `UNSURE` and `REMEMBERS` beside the `DECIDES` key it inherits, all accepting `(nothing)`. `DECIDES` may name leaving, refusing or a later act; the writer honours it or records `veto <npc> --kind --reason`. `REMEMBERS` becomes a `remember` event.
- `want` (at most three standing wants with a weight, optional conflict line) and `intent` (horizon `now`, `scene`, `day`, `long`; at most three active). The brief prints the top two wants and the active intents.
- Off-screen call at a scene boundary, off by default and asked at apply: one per boundary, outside the turn budget. It answers `DOES`, `LEAVES`, `DECIDES`, `CHANGES`. `LEAVES` goes to game-master as evidence; the scene is never narrated directly. `routine` in `state` feeds it.

## ISS-29 — Drift review

F9.

**Done 2026-11-13.** Choices made where the text above left room: the script does not read meaning, so `review` never claims a contradiction; it sets beside the card every candidate recorded since the last card snapshot (the latest `char` event, kept as `snapshot_seq`): each standing want and each `day` or `long` intent beside the card's `want`, and each `remember` or `offscreen` episode of salience 4 or more (at most six, so a `compress` summary is not one) beside its `attitude`, both texts shown, for the writer to judge. Taking a new snapshot with `add` is how the writer marks them weighed. Card fields changed since `card_at` are found by comparing the snapshot with the card now, and are fixed by a new snapshot, not a delta. An active intent is stale once game-master's scene count is 1 past its recorded scene for `now` and `scene`, 3 for `day` and 10 for `long` (`STALE_AFTER`). The veto window counts vetoes whose scene is within the last ten (`scene > scene_count - 10`). Each finding is a warning, so `review` exits 1 when there is something to look at. `--propose` rewrites `notes/brains/card-proposal.json` on every run with `entry` and `why` left null, `ops` that are game-master `npc` `set` ops (a `want` only, the heaviest standing want since the snapshot when it differs from the card; an attitude is never proposed) and the candidates under `evidence`; it never writes under `notes/gm/`.

- `review [--npc] [--propose]`: per character, card fields changed in game-master since `card_at`; episodes, wants or intents that contradict the card's `want` or `attitude`, with both texts; more than two vetoes in ten scenes; intents gone stale; a persistent tier with no session.
- `--propose` writes `notes/brains/card-proposal.json` for the writer to merge into a game-master delta. It never writes `notes/gm/pending.json` and never commits.
- The protocol runs it at each chapter boundary and every ten scenes.

## ISS-30 — Age gate on desire

In character-brains-plus, `check` and `state` refuse a `desire` field for a character whose `age` is missing or under 18, and `brief` omits the block for them. In method-only character-brains, the protocol and template say the `desire` line is written only for a character the story has established as 18 or older, and the brief leaves it out otherwise. The author will hand this to opencode once ISS-26 lands.
