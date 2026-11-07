# CouldHappen: agent instructions

These instructions are for agents working on CouldHappen itself, the development repository. They are never shipped: the release ZIP forbids `AGENTS.md` and `CLAUDE.md`, and a story workspace has only the writer skill in `.agents/skills/couldhappen/`.

## Everyone

- Start with [README.md](README.md), then [docs/implementation-progress.md](docs/implementation-progress.md) for the current state and next steps. The [docs index](docs/README.md) lists the rest.
- **Do not run a story in this repository.** Real stories run in a workspace unpacked from a release ZIP.
- Markdown that ships in the release is shared with development text. Wrap development-only material in the `dev-only` HTML comment blocks described in [Building a release](docs/setup.md#building-a-release).
- When you add, change, or remove a player-facing capability (a package, a helper command, a reader feature), update the pages the writer reads to answer "what can you do?": `packages/INDEX.md`, the reference list in the skill's `SKILL.md`, and `references/what-this-can-do.md`. `tests/test_skill_docs.py` fails when a package, reference page, or helper command is missing from them.
- Keep LF line endings. Run the checks in [docs/setup.md](docs/setup.md#development-checks) before proposing a change.
- The license is AGPL-3.0-or-later. Contributions are made under it.

**Contributors and the maintainer** follow [CONTRIBUTING.md](CONTRIBUTING.md): work on a branch and open a pull request against `main` on [github.com/Synere/CouldHappen](https://github.com/Synere/CouldHappen). There is one history, and it is public. Commit with a `@users.noreply.github.com` address. Push only when the user asks, and never force-push.
