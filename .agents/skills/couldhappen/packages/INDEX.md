# Director packages

A **director package** is a reusable setup: a prompt, with optional helper scripts, that a Director can hand to the writer so that a story gets a capability without the writer designing it from nothing. Packages are never required for play and never applied by themselves.

Each package is a folder here: `PACKAGE.md` (what it is, what it touches, what it costs), `APPLY.md` (the instructions you follow to apply it), and optional `files/`. How to use them is in [the skill](../SKILL.md#director-packages). How to make and share one is in [AUTHORING.md](AUTHORING.md).

## Available

| Package | Offers | A player might say |
| --- | --- | --- |
| [rpg-mechanics](rpg-mechanics/PACKAGE.md) | Fair visible dice, a private rules note designed for this setting, and an optional character sheet panel in the reader. | "I want stats", "add an RPG system", "make the rolls real", "track my health and gear" |
| [scene-images](scene-images/PACKAGE.md) | Pictures inside the story turn they belong to, checked against the scene before they are kept, a "Picture scene" button, a "Make portrait" button per cast member, portraits reused as references so characters stay consistent, and an optional colour theme. Needs an image provider key. | "I want pictures", "generate scene images", "can the story have art" |
| [game-master](game-master/PACKAGE.md) | Runs the story like an expert tabletop game master: a private contract, checkable canon facts and current situation, and every change validated and tied to the entry that caused it. Five layers the Director can switch on or off at any time: continuity, memory, living world, discovery, pacing. | "keep the story consistent", "make the world feel alive", "remember my choices", "run it like a real GM" |
| [character-brains](character-brains/PACKAGE.md) | Recurring characters get their own subagent brain that sees only what that character perceives, so they keep their own minds, secrets and voices. The Director chooses how many are tracked at once. Needs game-master with layers 1 to 4 and a host that can run subagents. | "make the characters think for themselves", "NPCs should not know everything", "give them their own minds" |
| [character-brains-plus](character-brains-plus/PACKAGE.md) | The same brains, but a script builds every brief from a log of what each character has seen, been told and kept, so a character cannot be briefed with what they could not know, and keeps each character's body, mood and desire, beliefs, lies and promises, what they think of each other, and what they want and mean to do between scenes, with an optional off-screen life at scene boundaries. Pick it over character-brains for stories built on secrets and lies; pick the method-only package for light stories or to skip the per-turn bookkeeping. The two cannot be installed together. Needs game-master with layers 1 to 4, Python, and a host that can run subagents. | "NPCs keep knowing things they shouldn't", "make secrets airtight", "track who knows what" |

## Packages made for this workspace

Packages the Director has asked you to create from this story's own setup are added below, one line each, newest last. Keep this list current.

