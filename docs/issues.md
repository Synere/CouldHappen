# Issues

The single register of open work for CouldHappen: to-dos, pending decisions, open questions, deferred items and
unverified facts, each with a stable `ISS-n` ID. A row is one short line. Its Source links to the item's home
section: a heading that starts with its ID (`## ISS-n — title`) in another file, which holds the reasoning.

- **Next ID: ISS-18.** IDs are never reused. Code comments and commits may cite them.
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

## To-do

| ID | Item | Area | Blocked by / phase | Source |
| --- | --- | --- | --- | --- |
| ISS-1 | Re-test the fixes on a host: standing wait starts after setup with no chat prompt; `portrait` accepts the original card path | hosts | — | [host validation](plans/host-validation.md#iss-1--re-test-the-fixes) |
| ISS-2 | Test more hosts, any order: Codex CLI, Claude Code (with skill discovery), Pi with OpenRouter | hosts | — | [host validation](plans/host-validation.md#iss-2--more-hosts) |
| ISS-3 | Fresh-context continuation: after reentry from files alone, continue the fiction through browser input | hosts | — | [host validation](plans/host-validation.md#iss-3--fresh-context-continuation) |
| ISS-4 | Run `egm-drift-report` over the design, distribution design and public contract before a wider release | docs | — | [public release](plans/public-release.md#iss-4--drift-report) |
| ISS-6 | Retake the README and GitHub screenshots for the restyled reader | docs | — | [public release](plans/public-release.md#iss-6--retake-the-screenshots) |
| ISS-7 | Try character-brains on a host with subagents, with game-master layers 1 to 4 | packages | — | [host validation](plans/host-validation.md#iss-7--try-character-brains) |
| ISS-17 | Run a fresh EGM design review of the approved design | docs | — | [public release](plans/public-release.md#iss-17--egm-design-review) |

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
| ISS-5 | Publish by the ADR-4 checklist | 2026-11-11 | Done on 2026-11-05: v0.1.7 was published from the fresh history; releases since are built from tags by `release.yml` |
