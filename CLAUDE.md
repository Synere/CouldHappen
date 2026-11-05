@AGENTS.md

The most important rule from AGENTS.md: **never push the local `main` branch.** It is the private history. Only `publish` is pushed (a plain `git push` does that), and the `scripts/git-hooks/pre-push` guard must be active (`git config core.hooksPath scripts/git-hooks`).
