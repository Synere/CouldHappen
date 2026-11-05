# CouldHappen

A portable fiction workspace for an existing agent. The agent is the writer and game master; the browser is your reading and discussion interface. CouldHappen supplies a browser reader with separate Story and Director conversations, a small local helper, durable story knowledge, and Git-supported recovery. No provider SDK or model client is included: your agent owns model calls, tools, permissions, and execution.

<!-- dev-only -->
## Development repository

This is the development and packaging repository, not a story workspace. **Do not run a durable story here.** Real stories run in a clean workspace unpacked from the release ZIP ([ADR 0001](docs/decisions/0001-separate-story-workspaces.md), [ADR 0002](docs/decisions/0002-publish-clean-release.md)). The release README is this file with the development-only blocks removed; see [Building a release](docs/setup.md#building-a-release).

* **Current state and next steps:** [implementation progress](docs/implementation-progress.md).
* **Building and smoke-testing a release:** [Building a release](docs/setup.md#building-a-release).
* **Documentation index:** [docs/README.md](docs/README.md).
* **Design:** [approved design](docs/designs/couldhappen.md), [design system](DESIGN.md), [product context](PRODUCT.md).
* **Evidence:** [validation results](docs/validation-results.md).
* **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md); agents read [AGENTS.md](AGENTS.md).

Source lives in `helpers/` (Python standard library only) and `web/` (Svelte/Vite). Opt-in native checkpoint examples live in `integrations/`. The Impeccable design hooks in `.codex/` are local development configuration: untracked, not published, and not part of the application.
<!-- /dev-only -->

## Start

> **You don't need to run these steps yourself.** Unpack the release, open the folder with your coding agent, and tell it to **set up**. It reads the writer skill, installs what is needed, starts the reader, and tells you when to open the browser. The steps below are what it does, for reference or if you prefer to do it by hand.

Prerequisites: Python 3.11+, Node 24+, npm, Git.

1. Unpack the release into a private or local directory.
2. Install the reader dependencies:

   ```bash
   cd web
   npm ci
   ```

3. Validate the empty workspace from the workspace root:

   ```bash
   python -m helpers validate --root .
   ```

4. Start the helper:

   ```bash
   python -m helpers serve --root . --frontend-origin http://127.0.0.1:5173
   ```

5. In a second terminal, start the reader:

   ```bash
   cd web
   npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
   ```

6. After the helper prints its address and Vite is ready, claim the workspace:

   ```bash
   python -m helpers writer claim --root .
   ```

7. Open <http://127.0.0.1:5173>.

8. Ask your agent to read `.agents/skills/couldhappen/SKILL.md` and **set up**. It should inspect the workspace, leave a standing wait running so your browser messages reach it, and begin when you supply a world prompt or cards. Codex and opencode also find the skill in `.agents/skills/`; Claude Code finds it through `.claude/skills/couldhappen/`. Support for every host is experimental; see [host integrations](docs/reference-hosts.md).

9. After setup/claim, initialize Git in this directory and make the first baseline commit. The initialized workspace UUID belongs in that commit. Then check:

   ```bash
   python -m helpers checkpoint check --root .
   ```

The agent can do all of these steps itself when asked to set up; see [setup](docs/setup.md).

## Stop

When you are done for now, tell your agent to **close the game**, in chat or in the Director tab. It finishes what it was writing, saves a Git checkpoint, closes the workspace, and stops the reader and helper. Next time, open the folder with your agent and tell it to **set up** again; the story continues from where you left off.

## Privacy

Keep this story workspace private unless you deliberately choose to publish it. Story conversations, imports, portraits, private writer records, and Git history are part of the workspace archive. A public remote exposes them. A redacted export is not provided.

Do not add the development repository as a remote or merge its history into a story.

## License

CouldHappen is free software under the GNU Affero General Public License, version 3 or (at your option) any later version (`AGPL-3.0-or-later`). See [LICENSE](LICENSE). If you share a modified copy, including changes your writer agent made to the helper or reader, share it under the same license with its source; if you let other people use a modified copy over a network, offer them its source. The license covers the package source, not your story or imported third-party card material. Bundled fonts retain their OFL notices in `web/fonts/`; npm dependencies retain their own licenses in the installed package tree.

## Documentation

* [Setup](docs/setup.md)
* [Public contract](docs/public-contract.md)
* [Host integrations](docs/reference-hosts.md)
* [Design system](DESIGN.md)
* [Writer reentry](START_HERE.md)
* [Writer skill](.agents/skills/couldhappen/SKILL.md)
