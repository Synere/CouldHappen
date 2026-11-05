# Establish capabilities

Work out what your host actually lets you do. Check the tools you have, their permissions and settings, the help text of the executables you will run, and current documentation when you need it. Do not assume a capability from a model name or a host's brand.

You need to confirm, in practice:

- you can read and write the workspace files;
- you can run the helper (`python -m helpers ...`) and Git;
- you can receive player input through a wait (below);
- a fresh session could continue from the files alone;
- you can stop or account for any work you started, including delegated work, before a recovery.

## Staying reachable

The player types in a browser. Their entries reach you only when a `python -m helpers wait` command returns to you, so you must always have one running when you hand control back. Choose one of these, in order of preference:

1. **Background wait.** If your host can run a command in the background and tell you when it finishes, run `python -u -m helpers wait --root . --timeout 0` that way. Check your shell tool's description to confirm it reports completion. `--timeout 0` means no helper deadline, but the command still finishes: it returns as soon as a human entry is `pending`. Handle the entries, mark them `addressed` or `deferred`, then start a new background wait. (Use `-u` so its output is not buffered.)
2. **Foreground wait with renewal.** If not, run `python -m helpers wait --root . --timeout N` with `N` safely under your tool's time limit (for example 30 seconds under a 45-second limit). Exit code 3 means a quiet timeout, not a failure; start another. This only works while you are active: once your turn ends nothing is waiting, so tell the player that browser messages will need a nudge in chat.
3. **Native monitor.** If your host has its own file or event monitor, you may use it instead.

Record which method you used, how often it renews, and what it costs, so later sessions do not have to rediscover it.

A helper cannot wake a session that your host has already ended. That is a limit on ended sessions only; it is not a reason to skip a background wait while your session is open.

## Completion hooks

Some hosts can run a check when you try to finish and ask you to continue if scoped work is uncommitted. That is extra assurance, and you only have it if you observe a trusted hook actually firing. Without it, these instructions are your only guard. Optional integrations and their versions are in `docs/reference-hosts.md`. You may install missing prerequisites with your ordinary permissions; verify the actual executable afterwards.
