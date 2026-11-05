# Contributing to CouldHappen

Thanks for your interest. CouldHappen is a portable interactive-fiction workspace in which your own coding agent is the writer and game master. This repository is where the package is developed; players use the release ZIP instead (see the [README](README.md)).

## Ways to help

- **Play-test reports** are the most useful contribution right now. Every host is experimental. Unpack a [release](https://github.com/Synere/CouldHappen/releases), tell your agent to **set up**, play a while, then open an issue. Include:
  - the host and version (opencode, Codex CLI, Claude Code, Pi, or another);
  - the model;
  - the operating system;
  - what worked and what did not.

  Things worth watching: did the agent keep listening for browser messages? Did it respect your Director directions? Did **close the game** work?
- **Bug reports:** open an issue with steps to reproduce and the helper's or reader's output. Leave out story text you would rather keep private.
- **Pull requests:** for fixes, tests, documentation, and host integrations. For a larger change, open an issue first so we can agree on the approach.

## Working on the code

Prerequisites: Python 3.11+, Node 24+, npm, and Git. The helper (`helpers/`) uses only the Python standard library; the reader (`web/`) is Svelte with Vite.

```bash
cd web
npm ci
```

Before opening a pull request, run the [development checks](docs/setup.md#development-checks) from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

And in `web/`:

```bash
npm run check
npm run test:unit
npm run build
```

If you change the reader, also run the browser tests (`python tests/run_browser.py`).

## Ground rules

- **Never run a real story in this repository, and never commit one.** That covers story logs, imported character cards, portraits, and API keys. Stories belong in a workspace unpacked from a release.
- **The release is built from these files.** Markdown that ships is the development text with its `dev-only` blocks removed. Wrap anything meant only for developers in those blocks; see [Building a release](docs/setup.md#building-a-release).
- **Keep the public contract in step.** If you change a file format, a helper command, or the browser API, update [docs/public-contract.md](docs/public-contract.md) in the same pull request.
- **Design changes** go through the [approved design](docs/designs/couldhappen.md) and, for lasting decisions, a new [decision record](docs/decisions/README.md).
- Keep LF line endings and the existing code style. Add or update tests for behavior you change.

## Using an AI agent

You are welcome to work with a coding agent. Point it at [AGENTS.md](AGENTS.md) (Claude Code reads `CLAUDE.md`, which includes it). You are responsible for what it submits, so read the diff before you open a pull request.

## License

CouldHappen is licensed under AGPL-3.0-or-later (see [LICENSE](LICENSE)). By contributing, you agree that your contribution is licensed under the same terms. There is no separate contributor agreement.
