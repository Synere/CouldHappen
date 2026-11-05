# Agent-operated setup

Open this workspace with an existing capable agent and ask it to read `.agents/skills/couldhappen/SKILL.md` and **set up**. The agent remains the writer; no provider client is installed. Read [START_HERE](../START_HERE.md) and [public-contract](public-contract.md) on reentry. Preserve existing story, imports, notes, and hooks.

<!-- dev-only -->
> **Development repository.** Do not run a durable story here. Real stories run in a clean workspace created from the release ZIP; for a smoke test, build a release and unpack it outside this repository (see [Distribution and workspaces](designs/distribution-and-workspaces.md)). The release copy of this file is this text with the marked development-only blocks removed by `scripts/build_release.py`.
<!-- /dev-only -->

Target Python 3.11+, Node 24+, npm, and Git. Verify the actual `python --version`, `node --version`, `npm --version`, and `git --version` in the agent's environment; install missing prerequisites through normal permitted mechanisms, then recheck. No pip install is needed.

1. In `web/`, run `npm ci`. The included fonts are self-hosted OFL assets; no font network request is needed during play.
2. At the workspace root, run `python -m helpers validate --root .`. Setup does not recreate existing files.
3. Choose a free loopback frontend port, normally 5173. Run `python -m helpers serve --root . --frontend-origin http://127.0.0.1:5173` through a serviced host tool. On its first start it initializes the workspace UUID in `couldhappen.json`. It prints its actual address, workspace UUID, and generation without the secret. Runtime connection/control/lock files are private and ignored; do not copy secrets into browser configuration.
4. In `web/`, run `npm run dev -- --host 127.0.0.1 --port 5173 --strictPort`. Vite reads the helper connection at startup and proxies only public APIs. For an alternate workspace, set `COULDHAPPEN_ROOT` to its absolute path in Vite's process environment. If Vite fails with a native memory-allocation error, check free memory and retry.
5. Inspect the workspace and establish safe writer ownership. For a clean first setup use `python -m helpers writer claim --root .`. Claim establishes ownership; it does not create the UUID. Open the selected origin and match its snapshot workspace/generation against the helper rather than trusting an occupied port.
6. After claim, initialize Git in the story workspace. Before committing, check that `git rev-parse --show-toplevel` is this workspace and not an enclosing repository; if it is not, stop and tell the player rather than committing into the enclosing repository. Then make the first baseline commit, including the initialized UUID. Do not create a pre-setup baseline commit. Inspect the actual scope and avoid staging unrelated files. Checkpoint commands are read-only; they never commit.
7. Verify a browser save and a serviced `python -m helpers wait --root . --timeout 30`. Exit 3 means quiet timeout, not failure or session liveness.
8. Inspect optional native hook activation separately using [host integrations](reference-hosts.md). The opt-in examples under `integrations/` are not installed automatically.
9. Before reporting that setup is done, start a standing wait for the player's first entry, and leave one running before every later turn ends. Prefer a background or yielded `python -u -m helpers wait --root . --timeout 0` whose completion the host reports back to the agent; it returns as soon as a human entry is `pending`, so mark handled entries `addressed` or `deferred` first. Otherwise renew a bounded foreground wait within the tool's deadline. After handling what it returns, start the next one. Record the method, renewals, and overhead. If the host supports neither, tell the player that browser input needs a nudge in chat.

Use the agent's discovered executable path in place of `python`. Commands accept argument arrays; paths with spaces must be quoted for the actual shell. On Windows, background start commands should retain process IDs and log paths.

## Direct saves and closure

Obtain `python -m helpers writer pause --root .`, keep the returned token locally, then reread BOTH logs. Use `python -m helpers entry --role writer --body-file <utf8-file>` to print an escaped new entry; write/append with ordinary file tools while paused. Preserve IDs and human bodies. Validate, then `python -m helpers writer release --root . --token <token>`.

`writer block --on` and `--off` independently block both submission channels during prose production. Releasing a pause does not clear this block. `writer invalidate --token <token>` under an owned pause rotates generation for recovery/maintenance while preserving edit ownership.

When the player asks to close the game, follow "Closing the game" in the skill's writing reference: answer any Director request, finish or release in-progress work, settle pending entries, stop the standing wait, leave notes, inspect `python -m helpers checkpoint check --root .` and make a meaningful writer-chosen checkpoint, then run `python -m helpers writer close --root .`, and finally stop the Vite and helper processes it started. Close drains saves, validates public records, and refuses invalid/dirty/error results; it never commits. After a clean close the next setup uses `writer claim`, not recovery. No per-exchange or timer policy is imposed.

## Safe reopening

A helper restart always begins closed. Establish through actual host controls that old writer/delegated work has stopped. Inspect partial logs/notes and persisted pause/production controls. For an interrupted OS lock, establish the old helper stopped before using `serve ... --previous-helper-stopped`; OS locking still refuses a live second helper. Neither age nor a PID alone authorizes recovery.

After validation use `writer recover --previous-writer-stopped`. This records your established boundary, rotates generation, and clears abandoned edit/production controls. It does not clear durable awaiting_director state. If files are invalid, recover fails closed: repair them under the already closed boundary and retry. If the helper address changed, restart Vite and verify both services. Keep the frontend origin stable; drafts are origin/workspace/channel scoped in same-tab session storage.

For Director Undo, follow the skill recovery reference: inspect actual available history, restore/reconstruct only supported scope, retain applicable guidance/useful improvements by default, reconcile pending input and private assumptions, append explanation and a new Director question, set awaiting_director, invalidate generation, validate/release, and wait for interpreted new direction. `checkpoint inspect --ref <commit>` describes recorded history; no blanket restore command is supplied.

Python source edits normally require a deliberate helper restart: `python -m helpers stop --root .` drains saves, shuts the helper down, and releases its lock, so `serve` starts again without `--previous-helper-stopped`. Avoid stopping helpers by matching process names. A host restart ends background waits; check one is running at the start of every turn that a wait did not start. Compatible frontend changes use Vite HMR. Incompatible public changes update all consumers under pause/reopen. No production build is required for ordinary saves.

## Development checks

At the workspace root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

In `web/`:

```bash
npm run check
npm run test:unit
npm run build
```

For browser verification install the pinned Chromium once, then run the browser runner from the workspace root:

```bash
npx playwright install chromium
python tests/run_browser.py
```

The browser runner creates temporary synthetic data, starts only its own services, and terminates only those child processes; optional `--python` and `--node` select discovered executables. Do not run it against a real story workspace. It never claims native-host or narrative validation.

<!-- dev-only -->
In the development repository, also run the installed Svelte autofixer on every authored component, and record results in [validation results](validation-results.md).

## Building a release

1. Commit everything; the builder refuses a dirty tree.
2. Bump `"version"` in `release.manifest.json` and commit. It is the only place the version lives; `web/package.json` is private and carries none.
3. Run the checks above.
4. Preview the file list with `python scripts/build_release.py --ref HEAD --list`.
5. Build with `python scripts/build_release.py --ref HEAD`. It writes `release/dist/couldhappen-<version>.zip` and a `.sha256` sidecar.
6. Smoke-test it: `python scripts/smoke_release.py release/dist/couldhappen-<version>.zip`. It unpacks the ZIP into a temporary folder outside any repository, follows the README's player setup (npm ci, validate, helper, reader, claim, snapshot match, Git baseline, clean checkpoint, quiet wait), then runs the package's own test suites, and stops everything it started. Add `--keep` to inspect the folder afterwards or `--skip-browser` to skip Chromium. Players never need this; it exists so a broken ZIP is caught before it is shared. It covers items 1 to 8 of the [confirmation checklist](designs/distribution-and-workspaces.md#confirmation-checklist); items 9 and 10 need a real session.

Release text comes from the tracked files themselves. In Markdown, wrap development-only material between an opening and a closing `dev-only` HTML comment, each alone on its line (the exact markers are in `scripts/build_release.py`); the builder removes those blocks and then checks that every remaining relative link resolves inside the release. Only data files whose content must differ (`couldhappen.json`, the empty `public/` files, `.gitignore`) use templates under `release/`.
<!-- /dev-only -->
