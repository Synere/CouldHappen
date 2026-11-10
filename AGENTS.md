# CouldHappen: agent instructions

These instructions are for agents working on CouldHappen itself, the development repository. They are never shipped: the release ZIP forbids `AGENTS.md` and `CLAUDE.md`, and a story workspace has only the writer skill in `.agents/skills/couldhappen/`.

## Everyone

- Start with [README.md](README.md), then the [issues register](docs/issues.md) for open work and next steps, and [docs/plans/](docs/plans/) for work in progress. [ADR-8](docs/decisions/ADR-8-open-work-in-the-register.md) says which document owns which kind of fact: groundwork keeps decisions, open work and plans; the designs, reviews and drift reports are EGM's. The [docs index](docs/README.md) lists the rest.
- **Do not run a story in this repository.** Real stories run in a workspace unpacked from a release ZIP.
- Use the [approved design](docs/designs/couldhappen.md) for requirements; do not restart brainstorming or an overall design review. Preserve the approved architecture, the creative-initiative principle, the Woven direction, and the existing Impeccable hooks in `.codex/`.
- Only an actual host/story observation establishes that something works on a host. Keep it apart from implemented behaviour, automated checks and visual observations ([validation](docs/validation.md#evidence-levels)).
- Do not write the current release version anywhere but `release.manifest.json`, or host status anywhere but [host integrations](docs/reference-hosts.md).
- Markdown that ships in the release is shared with development text. Wrap development-only material in the `dev-only` HTML comment blocks described in [Building a release](docs/setup.md#building-a-release).
- When you add, change, or remove a player-facing capability (a package, a helper command, a reader feature), update the pages the writer reads to answer "what can you do?": `packages/INDEX.md`, the reference list in the skill's `SKILL.md`, and `references/what-this-can-do.md`. `tests/test_skill_docs.py` fails when a package, reference page, or helper command is missing from them.
- Keep LF line endings. Run the checks in [docs/setup.md](docs/setup.md#development-checks) before proposing a change.
- The license is AGPL-3.0-or-later. Contributions are made under it.

**Contributors** follow [CONTRIBUTING.md](CONTRIBUTING.md) and open a pull request against `main` on [github.com/Synere/CouldHappen](https://github.com/Synere/CouldHappen). **The maintainer** commits on the current branch, usually `main`; no new branch is needed for each change. There is one history, and it is public. Commit with a `@users.noreply.github.com` address. Push only when the user asks, and never force-push.

- [docs/decisions/](docs/decisions/README.md) records why things are the way they are, one MADR file per decision, named `ADR-n-short-title.md` and cited as `ADR-n`.
- Record a decision as a new `ADR-n` file before acting on it, with a Y-statement line and a Confirmation section. Never renumber a decision or rewrite an accepted one: supersede it with a new one.
- Cite decisions by ID in code comments and docs. Every cited ID must exist.
- `node scripts/groundwork-check.mjs` checks the docs (links, decision IDs and fields) and runs as the pre-commit hook. After a fresh clone, run `node scripts/groundwork-check.mjs --install-hooks` once.
- [docs/issues.md](docs/issues.md) is the register of open work: one row per item, each with an `ISS-n` ID.
- Open work goes in the register. Write the item's home section first (a heading that starts with its ID, in another file), then its row, and bump Next ID. Never reuse an ID.
- When an item is resolved, move its row to Closed with the date and a one-line resolution, in the same commit as the work.
- Cut work into tickets that are vertical slices: each one changes something that can be seen or tested end to end, and fits in one session. A ticket that waits on another names its ID in the Blocked by cell.
- Asked what to do next, answer with the head of the register's focus order: its earliest line that is open and unblocked. With no focus order, answer with the frontier: the open rows that nothing open blocks.
- `docs/plans/` holds plans (work that waits on someone or runs over phases) and research notes (cited evidence).
- A note in `docs/plans/` carries `type`, `status` and `updated` in its frontmatter and opens with its Purpose. A plan's Purpose says what ends it ("Ends when …"). A completed plan is never reopened: new work starts a new plan.
- Decisions local to one note go in its `## Decision log` table, and the note declares a `dec-prefix`. Outside the note, cite them with that prefix.
- At the start of a session, if no open-work summary was printed for you, run `node scripts/groundwork-check.mjs --summary` and read it before planning work.
