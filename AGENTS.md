# CouldHappen: agent instructions

These instructions are for agents working on CouldHappen itself, the development repository. They are never shipped: the release ZIP forbids `AGENTS.md` and `CLAUDE.md`, and a story workspace has only the writer skill in `.agents/skills/couldhappen/`.

## Everyone

- Start with [README.md](README.md), then [docs/implementation-progress.md](docs/implementation-progress.md) for the current state and next steps. The [docs index](docs/README.md) lists the rest.
- **Do not run a story in this repository.** Real stories run in a workspace unpacked from a release ZIP.
- Markdown that ships in the release is shared with development text. Wrap development-only material in the `dev-only` HTML comment blocks described in [Building a release](docs/setup.md#building-a-release).
- Keep LF line endings. Run the checks in [docs/setup.md](docs/setup.md#development-checks) before proposing a change.
- The license is AGPL-3.0-or-later. Contributions are made under it.

**Contributors:** follow [CONTRIBUTING.md](CONTRIBUTING.md): work on a branch of your own fork and open a pull request against `main` on [github.com/Synere/CouldHappen](https://github.com/Synere/CouldHappen). Nothing below applies to you; your clone has one ordinary history.

## Maintainer's local clone only

This section applies only to the maintainer's own clone, which holds the private development history. You are in that clone if `git branch` lists both `main` and `publish`, and `git merge-base --is-ancestor 535dbae main` fails. In any other clone, skip this section.

There, the clone holds two unrelated histories ([ADR 0004](docs/decisions/0004-publish-with-fresh-history.md)):

- **`main`** is the private development history. It contains MIT-licensed versions, local evidence, and a personal email. **It must never be pushed anywhere.**
- **`publish`** is the public history. Its root commit is `535dbae`, and it is pushed to `origin` as GitHub's `main`.

A plain `git push` is configured (`remote.origin.push`) to push `publish` to the public `main`. To publish work:

1. Commit on `main` as usual.
2. `git switch publish`, then `git cherry-pick <commits>`.
3. `git push`, then `git switch main`.

Never `git push origin main`, never `git push --all` or `--mirror`, never force-push, and never use `--no-verify`. Push only when the user asks.

The guard script `scripts/git-hooks/pre-push` refuses any push that:

- is not built on the public root `535dbae`;
- deletes a remote branch;
- carries a commit whose author or committer email is not a `@users.noreply.github.com` address.

It is installed as `.git/hooks/pre-push`, so it also runs while `publish` is checked out. Before any push, check that `.git/hooks/pre-push` matches `scripts/git-hooks/pre-push`; if not, run `cp scripts/git-hooks/pre-push .git/hooks/pre-push` from `main`. Do not set `core.hooksPath`. If the hook refuses, stop and tell the user; do not work around it.

The clone commits as `Synere <61239445+Synere@users.noreply.github.com>` (local `user.email`). A cherry-pick keeps the original author, so commits made before that setting need `--reset-author` before they can be pushed.

Build releases from the public history, so `release.json` names a public commit: `python scripts/build_release.py --ref refs/heads/publish`, then `python scripts/smoke_release.py release/dist/couldhappen-<version>.zip`. Do not attach it by hand: the GitHub Action `.github/workflows/release.yml` does that. After the release commits are on the public `main`, push the tag (`git tag v<version> <commit on publish>`, then `git push origin v<version>`). The Action checks that the tag matches `release.manifest.json` and is on the public `main`, runs the tests, builds, smoke-tests, and creates the GitHub release with the ZIP and `.sha256`. Run it by hand from the Actions tab for a dry run that uploads the ZIP as an artifact and releases nothing.
