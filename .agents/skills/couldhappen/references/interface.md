# Editable interface

The helper and the reader are editable source. Read `web/README.md` and `docs/public-contract.md` before changing them, and follow any installed UI or Svelte skills that apply.

- **Reader changes** (Svelte/Vite) reload live through hot module replacement. Visual changes that keep the file formats need no migration. Preserve drafts, the reading position, focus, reduced-motion behavior, and supplied portraits.
- **Helper changes** (Python) usually need a deliberate helper restart: `python -m helpers stop --root .`, then `serve` again. A stopped helper releases its lock, so the restart needs no `--previous-helper-stopped`. If you held ownership, the stop reports `clean: false`; reclaim with `writer recover --previous-writer-stopped` (you are the previous writer and you know you stopped). Restart Vite if the helper's address changed, and start a new wait.
- **Incompatible changes** to public file formats or interfaces: pause, inspect, update every consumer and the contract, rotate the generation with `writer invalidate` under your token, validate, then reopen or restart what changed. Stale writes must be refused, and both services checked afterwards.

Run the Python, unit, browser, check, and build commands listed in `docs/setup.md`.

Out of scope here: a runtime image provider for the player, a model client, an activity supervisor, or a publication workflow.
