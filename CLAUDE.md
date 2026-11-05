@AGENTS.md

The most important rule from AGENTS.md: **never push the local `main` branch.** It is the private history. Only `publish` is pushed (a plain `git push` does that), and the pre-push guard must be installed at `.git/hooks/pre-push` (copied from `scripts/git-hooks/pre-push`).
