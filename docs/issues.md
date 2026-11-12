# Issues

The single register of open work for CouldHappen: to-dos, pending decisions, open questions, deferred items and
unverified facts, each with a stable `ISS-n` ID. A row is one short line. Its Source links to the item's home
section: a heading that starts with its ID (`## ISS-n — title`) in another file, which holds the reasoning.

- **Next ID: ISS-31.** IDs are never reused. Code comments and commits may cite them.
- **New item:** write its home section first, then add a row here whose Source links to it, and bump Next ID.
- **Resolved item:** move the row to Closed with the date and a one-line resolution, and update its home section.

**Cutting tickets.** Break a spec, a plan or a conversation into tickets that are vertical slices: each cuts a
narrow, complete path through every layer of the code (schema, API, UI, tests), can be shown or checked on its
own, and fits one session. Prefactoring comes first: make the change easy, then make the easy change. Each
ticket names its blocking edges in its Blocked-by cell, the IDs that must close before it can start; one with
none can start now. A wide mechanical refactor runs as expand, migrate, contract: the new form beside the old,
the callers moved over in batches each blocked by the expand, then the old form deleted, blocked by every
batch. Agree the breakdown (title, blocked by, what it delivers) before writing rows; write blockers first, and
each home section before its row. A spec past draft never homes a ticket. Work the frontier: the open rows
whose blockers are all closed.

**Credit.** The ticket method is adapted from `to-tickets` in Matt Pocock's skills (MIT), https://github.com/mattpocock/skills, Copyright (c) 2026 Matt Pocock.

## Current focus

Work order from 2026-11-11. The author's ranking: one `N. ISS-n — why` line per item, in order. The detail stays in each row and its home section.

1. ISS-19 — the two writer-control bugs the drift report found can strand a session after a restart
2. ISS-20 — the remaining drift fixes gate a wider release; ISS-20 to ISS-23 can go in any order
3. ISS-21 — the writer relies on `card.md` holding the whole card
4. ISS-22 — small reader and contract fixes from the same report
5. ISS-23 — the design text catches up with the shipped skill
6. ISS-2 — more hosts widen what the release is known to work on

## To-do

| ID | Item | Area | Blocked by / phase | Source |
| --- | --- | --- | --- | --- |
| ISS-2 | Test more hosts, any order: Codex CLI, Claude Code (with skill discovery), Pi with OpenRouter | hosts | — | [host validation](plans/host-validation.md#iss-2--more-hosts) |
| ISS-19 | `close` refuses while blocked; `wait` errors on an unowned or closing helper even while a pause is persisted | helpers | — | [public release](plans/public-release.md#iss-19--writer-controls-after-close-and-restart) |
| ISS-20 | `validate` names the file for every error; `cast.json` rejects unknown top-level fields | helpers | — | [public release](plans/public-release.md#iss-20--validation-names-the-file) |
| ISS-21 | Lossless `card.md` (envelope, lorebook names, falsy fields); `portrait` guidance for a JSON-card import | helpers | — | [public release](plans/public-release.md#iss-21--lossless-card-copy-and-portrait-guidance) |
| ISS-22 | Vite denies `START_HERE.md`; portrait button names a lost connection; contract says how the reader settles uncertain saves | web | — | [public release](plans/public-release.md#iss-22--reader-boundary-and-save-wording) |
| ISS-23 | Design names `voice.md` and `what-this-can-do.md` and keeps one creative-practice file; link-check wording | docs | — | [public release](plans/public-release.md#iss-23--design-text-catches-up) |
| ISS-24 | character-brains-plus package and script core: fact visibility classes, `know` with how and confidence, the brief builder, generated views | packages | — | [character-brains-plus](plans/character-brains-plus.md#iss-24--knowledge-isolation) |
| ISS-25 | character-brains-plus: migrate method-only brain files into the log; `reconcile` after a Director Undo | packages | ISS-24 | [character-brains-plus](plans/character-brains-plus.md#iss-25--migration-and-undo) |
| ISS-26 | character-brains-plus: body, mood and desire state, `tick` decay, words not numbers in the brief | packages | ISS-24 | [character-brains-plus](plans/character-brains-plus.md#iss-26--body-mood-and-desire) |
| ISS-27 | character-brains-plus: beliefs, claims with a contradiction warning, what each thinks others know | packages | ISS-24 | [character-brains-plus](plans/character-brains-plus.md#iss-27--beliefs-claims-and-other-minds) |
| ISS-28 | character-brains-plus: the `BODY`, `UNSURE` and `REMEMBERS` answer keys, wants, intents, vetoes, the off-screen call | packages | ISS-24 | [character-brains-plus](plans/character-brains-plus.md#iss-28--agency-and-life-off-screen) |
| ISS-29 | character-brains-plus: `review` for card drift, with a proposal for game-master | packages | ISS-24, ISS-28 | [character-brains-plus](plans/character-brains-plus.md#iss-29--drift-review) |
| ISS-30 | Both brain packages: no desire for a character under 18 or with no age (for opencode) | packages | ISS-26 | [character-brains-plus](plans/character-brains-plus.md#iss-30--age-gate-on-desire) |

## Decisions pending

| ID | Decision | Area | Options / leaning | Source |
| --- | --- | --- | --- | --- |

## Open questions

| ID | Question | Area | Who can answer | Source |
| --- | --- | --- | --- | --- |

## Deferred / backlog

| ID | Item | Area | Revisit when | Source |
| --- | --- | --- | --- | --- |
| ISS-8 | Writing-style director package: a distilled style guide, a per-turn re-read, a style lint, and preset import as data | packages | idea, not started | [plan](plans/writing-style-package.md#iss-8--writing-style-package) |
| ISS-9 | Literal comp pixel gates: `.impeccable/build/state.json` stays at `spec`; no pixel pass claimed | reader | the author explicitly downgrades comp authority | [known limitations](plans/known-limitations.md#iss-9--literal-comp-pixel-gates) |
| ISS-10 | Dependency audit: two low dev-tooling findings (`deepmerge` under `@sveltejs/vite-plugin-svelte`) | web | an upstream patch lands, or a deliberate override is chosen | [known limitations](plans/known-limitations.md#iss-10--dependency-audit) |
| ISS-11 | Native assurance: checkpoint examples are off by default; a clean tree does not prove the world record complete | checkpoints | native checkpoint hooks are activated or observed on a host | [known limitations](plans/known-limitations.md#iss-11--native-assurance) |
| ISS-12 | Portrait framing: revisit the 4:3 contain treatment with the Director | reader | a real portrait library shows problems with it | [known limitations](plans/known-limitations.md#iss-12--portrait-framing) |
| ISS-18 | Writer-listening status: the reader cannot show whether the writer has a wait running | reader | the next round of reader work is chosen | [prior-art findings](research/browser-ui-prior-art-findings.md#iss-18--writer-listening-status) |

## Unverified

| ID | Claim | Area | How to verify | Source |
| --- | --- | --- | --- | --- |
| ISS-13 | Native checkpoint hooks are reached and trusted on a host | hosts | observe in a release workspace session | [host validation](plans/host-validation.md#iss-13--native-checkpoint-hooks) |
| ISS-14 | The writer closes the game when the player asks | hosts | observe in a release workspace session | [host validation](plans/host-validation.md#iss-14--closing-the-game-on-request) |
| ISS-15 | The skill's wait check works after a host restart | hosts | restart the host mid-session and observe | [host validation](plans/host-validation.md#iss-15--wait-check-after-a-host-restart) |
| ISS-16 | The voice reference works on a host | skill | observe in a release workspace session | [host validation](plans/host-validation.md#iss-16--voice-reference-on-a-host) |

## Closed

| ID | Item | Closed | Resolution |
| --- | --- | --- | --- |
| ISS-7 | Try character-brains on a host with subagents, with game-master layers 1 to 4 | 2026-11-12 | The author is playing a live 0.1.22 story with it on Claude Code with Opus, all game-master layers on, and reports it works well |
| ISS-4 | Run `egm-drift-report` over the design, distribution design and public contract | 2026-11-11 | 13 drifts, no Blocker ([report](reviews/2026-11-11_DRIFT_REPORT.md)); the fixes are ISS-19 to ISS-23 |
| ISS-1 | Re-test the fixes on a host | 2026-11-11 | The author observed the standing wait starting after setup and `portrait` working in several later sessions |
| ISS-3 | Fresh-context continuation | 2026-11-11 | The author continued the fiction after a fresh-context restart on Claude Code and opencode |
| ISS-17 | Run a fresh EGM design review of the approved design | 2026-11-11 | Stages 5-8 ran on Sonnet with no Blockers; 7 Major and 6 Nit fixes were applied to the design and the rest declined with reasons ([review record](reviews/2026-11-11_design-review/consolidated_review_report.md)) |
| ISS-6 | Retake the README screenshots | 2026-11-11 | Director and empty Story shots retaken in the restyled reader, the Story shot with that session's package theme and sheet applied to a throwaway copy; the director-export shot shows a player-built reader and was kept |
| ISS-5 | Publish by the ADR-4 checklist | 2026-11-11 | Done on 2026-11-05: v0.1.7 was published from the fresh history; releases since are built from tags by `release.yml` |
