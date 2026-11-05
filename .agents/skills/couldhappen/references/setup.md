# Setup and reopening

Follow `docs/setup.md` step by step. This page explains what each part protects.

## Before claiming

- Check Python, Node/npm, and Git, and run `npm ci` in `web/`.
- Preserve existing files, configuration, and hooks. Setup never recreates them.
- Validate the public files. Start the helper and Vite, or reuse running ones only after their reported workspace and generation match this workspace. A port that answers is not proof it is the right service.
- Inspect the files and any interrupted controls before `writer claim`. If a previous writer (or work it delegated) may still be running, establish that it has stopped before using `writer recover --previous-writer-stopped`. The flag records your assertion; it does not check. Never take over ownership just because it looks old.
- Keep the frontend origin (address and port) stable, because the reader's drafts are tied to it. If the helper's address changes, restart Vite and check both services again.

## Baseline and checks

- Before the first commit, run `git rev-parse --show-toplevel` and confirm that it is this workspace. If the workspace sits inside another Git repository, stop and tell the player instead of committing into that repository.
- Make the first Git checkpoint from the actual scope and changes. Never sweep unrelated files into it.
- Check separately whether a native completion hook is active and observed (see capabilities).
- Open the reader and confirm that a browser save works and that a wait returns it.

## Finish with a standing wait

Setup is not finished until a wait is running for the player's first entry. Start it (see "Staying reachable" in capabilities) **before** you tell the player setup is done. Otherwise the first message they type in the Story or Director tab sits unread until they prompt you in chat.

## When something cannot be established

Ask your host or the player for help through the ordinary means. Do not invent story assets or account access to complete a check.
