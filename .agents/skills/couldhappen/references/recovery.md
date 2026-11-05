# Interruption and Undo

## Starting any recovery

**If you already own the workspace** (for example, the Director asks for Undo during play):

1. Run `python -m helpers writer pause --root .` and keep the token.
2. Make sure earlier writer work, including anything you delegated, can no longer write to the workspace. Use your host's actual controls, and ask for help if you cannot tell. A stale marker or a fresh session is not proof that old work stopped.
3. Reread both logs, any partial work, your records, and the actual Git history and current changes.

**If you are reopening after an interruption** (the last session did not end with `writer close`), you do not own the workspace yet, and a restarted helper always begins closed. Inspect the files and the interrupted controls first, establish that the previous writer has stopped (step 2), validate, then run `python -m helpers writer recover --root . --previous-writer-stopped`. That gives you ownership and rotates the generation; it does not clear `awaiting_director`. Then pause as above before editing. After a clean close, `writer claim` is enough.

If `public/work.json` is `awaiting_director` but its `director_question_id` does not point to an existing writer entry in Director, the workspace stays closed until you repair it.

## Director Undo

When the Director asks to undo story development:

1. **Explain the scope.** Say what history is available, and which parts you can restore exactly versus reconstruct.
2. **Restore the fiction.** Return the requested story and its assumptions. By default keep applicable Director guidance and useful method or interface improvements. Inspect mixed commits rather than resetting wholesale; never rewrite Git branches.
3. **Reconcile.** Withdrawn *writer* entries leave the public logs; keep a verbatim private copy (for example under your notes) so the history is not lost. Human entries stay in the logs with their original bodies and IDs; mark old unresolved ones `deferred` where appropriate. Update your private knowledge so the withdrawn fiction has no current authority. In this session, remember the rejection as feedback, not as something that happened in the story.
4. **Ask for direction.** Append an explanation and a **new** writer question in Director. Set `public/work.json` to `awaiting_director` with that question's ID. Under the same pause, run `writer invalidate --token <token>` to rotate the browser generation; your token stays valid. Validate, then release.
5. **Wait for the answer.** Story stays closed while Director can save. Start a wait; in this mode it returns only Director entries that come after your question. Interpret the reply; discussion alone need not authorize continuing. Clear `awaiting_director` only when new direction authorizes it.

Never generate replacement prose automatically.

## Mechanical failures

For a small, understood mechanical failure, use the standing repair permission in proportion: fix the code, results, records, and affected prose quietly, and continue. A material failure, or one you are unsure about, belongs in Director discussion. Withdrawing substantial fiction uses the Undo procedure above.
