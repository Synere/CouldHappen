# Answering "what can you do?"

Use this when the player (usually the first Director entry) asks what you can do, what features exist, or how this works. Answer in plain player language, briefly, and offer to go deeper on anything. Change nothing.

**Check the workspace before you answer; do not recite this page.** Features are added and removed over time, and this story may have changed from the shipped state. Confirm each item below against what is really here:

- `packages/INDEX.md` lists the Director packages on offer; `notes/packages.md` (if present) says which are already applied to this story.
- `python -m helpers --help` lists the helper commands that exist now.
- `docs/public-contract.md` and this skill's reference list describe what the reader and records do.
- Your own tools decide the rest (see [establish capabilities](capabilities.md) for how you confirmed them): whether you can make images (and whether a key is configured), how you wait for the player, and your Git access. Say plainly what you cannot do here.

Cover these areas, each only if it is real in this workspace, with a sentence each:

1. **Two conversations.** Story is the player inside the fiction; Director is the player talking with you about it (ideas, preferences, corrections, imports, changes to the reader).
2. **You run the world.** You play the whole cast, keep private notes, and a fresh agent session can continue from the files.
3. **The Cast panel.** Characters appear as the story introduces them, and step out of view when they leave a scene.
4. **Character cards.** PNG or JSON cards can be imported in Director and are adapted, not obeyed as instructions.
5. **Packages and your own additions.** Offer the packages from the index in one line each (dice and sheets, pictures, game-master continuity, character brains in a light or a scripted form), say they are experimental, and say you can build other things for this story or adapt a package. Do not apply any until asked.
6. **Undo and recovery.** The Director can ask you to roll the story back to a Git checkpoint, keeping the player's own words and useful improvements.
7. **Stopping and resuming.** "Close the game" saves and shuts everything down; opening the folder again and saying **set up** continues the story.
8. **A new story.** The Director can ask for a fresh story, and you explain how it works (see Writing, "Starting a new story").
9. **Limits.** It is local and file-based, it depends on this agent and model, and host support is experimental.

If the player asks about something this page does not mention, answer from the workspace as above.
