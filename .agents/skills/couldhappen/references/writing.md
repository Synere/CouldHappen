# Writing and closing

## Each exchange

All commands below run from the workspace root as `python -m helpers <command> --root .`.

1. **Read.** When a wait returns, read the pending Story and Director entries together, with your durable notes. Neither channel goes first by rule. If entries conflict, or you choose to defer one, say so.
2. **Decide what the input asks for.** Director discussion shapes ideas, preferences, and imports; it does not establish hypotheticals or move story time forward. Explicit Director direction can authorize continuing or revising the story. A Story entry is the player acting in the fiction.
3. **Optionally block.** If you want both channels closed while you write, run `writer block --on` first. Private note work does not need a block.
4. **Pause and reread.** Run `writer pause`, keep its token, then reread both logs; something may have arrived since you last looked.
5. **Write.** Put your prose in a UTF-8 file and run `entry --role writer --body-file <file>` to print a correctly encoded entry; append it with ordinary file tools. Mark every human entry you handled `addressed` or `deferred`; a wait returns immediately while any stays `pending`. Keep human bodies and all IDs unchanged. `pending`, `addressed`, and `deferred` describe how you handled an entry, not whether a preference still applies.
6. **Validate and release.** Run `validate`, then `writer release --token <token>`. Clear the production block separately (`writer block --off`) when you are done with it.
7. **Update your notes** and the `START_HERE.md` links, so a fresh session can continue.
8. **Start a new wait before your turn ends**, including after a Director-only reply or a question (SKILL.md, Always 1). This is the step most easily forgotten.

Portray the whole cast, keep consequences believable, and let the player's contributions matter.

A save is publication: the reader shows it immediately, and there is no Accept/Revise stage. New writer prose may animate in; a revision keeps its ID and updates in place.

## After an interruption

Inspect the actual prose and dispositions in the files before redoing anything. Do not blindly repeat an action that may already have happened.

## Checkpoints

Choose meaningful Git checkpoints yourself; no timer or per-response commit is required. Completion hooks add assurance where a host supports them; forced interruption can bypass them.

## Closing the game

Close when the player asks you to stop for now, in chat or in a Director entry ("close the game", "let's stop here", "quit", "end the session"). Closing leaves the workspace so that the next session starts with a plain `writer claim` and no recovery. Do these in order:

1. **Answer a Director request first.** If the request came in Director, reply there briefly under a pause (for example, that you are closing and the story is saved) and mark it `addressed`, so the browser shows the answer.
2. **Finish what is in progress.** Do not leave a half-written passage or delegated work running. If you hold a pause, validate and release it. If a production block is on, run `writer block --off`.
3. **Settle the remaining entries.** Handle or deliberately `defer` every pending human entry, and say in Director which ones you deferred.
4. **Stop the standing wait.** Stop the background wait through your host's control, or end the process you started. This is the one time a turn may end with no wait running (Always 1 and Never 1); the player has asked you to stop listening.
5. **Leave notes for the next session.** Record where the story stands, open threads, and anything a fresh session needs, linked from `START_HERE.md` (Always 6).
6. **Checkpoint.** Run `python -m helpers checkpoint check --root .`, review the actual changes, and commit them with a meaningful message. Never sweep unrelated files in.
7. **Close.** Run `python -m helpers writer close --root .`. It stops the browser from saving, drains saves already accepted, validates the public records, and checks Git. It never commits. If it refuses (a record is invalid, the tree is dirty, or a save arrived at the last moment), fix the cause, commit again, and retry.
8. **Stop the services you started.** Stop the helper with `python -m helpers stop --root .`; it drains saves, shuts down, and releases its lock, and its `clean` field says whether the next start can use a plain `writer claim`. Then stop Vite through your host's control or the process ID from setup. Do not stop processes you did not start.
9. **Tell the player.** Say that the game is closed, name the checkpoint commit, and explain how to come back: open the folder with the agent and say **set up** (or "continue the story"). Mention any entries you deferred.

On the next setup, `writer claim` works directly after a clean close. `writer recover --previous-writer-stopped` is only for a session that ended without `writer close`.

## Starting a new story

Use this when the Director asks for another story, a fresh start, or "the same setup without the packages". A story workspace is one folder, one story: never reuse this folder or this session for it. A new agent session is needed because this one carries this story's context. Do these in order, and do not run the command until the player has answered.

1. **Explain first, in Director, and mark the entry `addressed`.** Say what will happen: a new sibling folder is created from this workspace's clean baseline (the shipped reader, helper and skill), with no story, cast, imports, notes, Git history, or packages from this story, so anything the Director wants (dice, pictures, game-master, cards) is asked for again in the new story's Director tab. This story stays here untouched, and can be reopened later by opening this folder with an agent and saying **set up**. Ask what to call the folder (suggest a sibling of this one) and whether to go ahead. Wait for a clear yes in a later entry.
2. **Create the folder.** Run `python -m helpers new-story --root . --destination <new folder>`. It refuses a folder that exists and is not empty, or one inside this workspace. Report the path it returns.
3. **Close this game** with the procedure above ("Closing the game"), so this wait, helper and reader are stopped and their ports are free. It is the one time a turn may end with no wait running.
4. **Tell the player what to do next:** open the new folder in a new agent session (not this one), tell it to **set up**, and give its Director its first instructions, including any packages.

Never set up, write in, or import anything into the new folder from this session.
