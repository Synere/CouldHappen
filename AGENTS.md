# CouldHappen development repository: agent instructions

These instructions are for agents working on CouldHappen itself. They are never shipped: the release ZIP forbids `AGENTS.md` and `CLAUDE.md`, and a story workspace has only the writer skill in `.agents/skills/couldhappen/`. Do not run a story here.

Start with [README.md](README.md) and [docs/implementation-progress.md](docs/implementation-progress.md).

## Two histories: never push `main`

This clone holds two unrelated histories ([ADR 0004](docs/decisions/0004-publish-with-fresh-history.md)):

- **`main`** is the private development history. It contains MIT-licensed versions, local evidence, and a personal email. **It must never be pushed anywhere.**
- **`publish`** is the public history. Its root commit is `535dbae`, and it is pushed to `origin` (`github.com/Synere/CouldHappen`) as `main`.

A plain `git push` is configured (`remote.origin.push`) to push `publish` to the public `main`. To publish work from the private `main`:

1. Commit on `main` as usual.
2. `git switch publish`, then `git cherry-pick <commits>` (or `git checkout main -- <paths>` and commit).
3. `git push`, then `git switch main`.

Never `git push origin main`, never `git push --all` or `--mirror`, never force-push, and never use `--no-verify`. Push only when the user asks.

## The guard

`scripts/git-hooks/pre-push` refuses any push that:

- is not built on the public root `535dbae`;
- deletes a remote branch;
- carries a commit whose author or committer email is not a `@users.noreply.github.com` address.

It is installed as `.git/hooks/pre-push`, outside the working tree, so it also runs while `publish` is checked out (that branch does not contain `scripts/`). Before any push, check that `.git/hooks/pre-push` exists and matches `scripts/git-hooks/pre-push`; if not, run `cp scripts/git-hooks/pre-push .git/hooks/pre-push` from `main`. Do not set `core.hooksPath`. If the hook refuses, stop and tell the user. Do not work around it.

## Commit identity

This repository commits as `Synere <61239445+Synere@users.noreply.github.com>` (local `user.email`). Commits made before that setting carry a private email and can only reach `publish` by being recommitted (for example, by a cherry-pick, which keeps the original author, so amend it with `--reset-author`).

## Releases

Build releases from the public history so that `release.json` names a public commit: `python scripts/build_release.py --ref refs/heads/publish`, then `python scripts/smoke_release.py release/dist/couldhappen-<version>.zip`. Full steps: [Building a release](docs/setup.md#building-a-release). Attach the ZIP and its `.sha256` to a GitHub release tagged `v<version>` on the public `main`.
