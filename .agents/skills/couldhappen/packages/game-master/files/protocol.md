# Game-master protocol (private; read at the start of a session and when unsure)

Prepare situations, not scripted plots. Track causes and consequences, not transcripts. The player decides what the protagonist does; the world decides what happens next.

Six questions to answer before you write: What must remain true? What matters to the protagonist? What is happening without them? What must not be forgotten? What could they discover? What makes this moment worth playing?

Phase 1 covers the first (what must remain true) and the start of the second. Phase 2 covers the fourth (what must not be forgotten). Later phases add the rest here.

## Each turn

Run these around the usual exchange in `references/writing.md` (pause, write, validate, release). Do not skip a step because the turn is short.

1. **Interpret.** What is the player attempting? Never invent a consequential choice for the protagonist (who they trust, what they promise, what they give up). Offer, ask, or let the world press.
2. **Read.** `python tools/gm_state.py hot` (add `--about <names>` for people or places that are not in the scene). Read the contract, the situation and the relevant facts. Trust the output; do not reread whole logs.
3. **Choose the world's response.** One of: reveal, react, offer, complicate, warn, resolve, transition. A good response gives the player something to act on.
4. **Draft the prose.** Respect established facts. Treat rumours and provisional facts as what characters believe, never as narrator truth.
5. **Propose the delta.** Generate the writer entry first (`entry --role writer --body-file ...` prints its id) so you can cite it. Write `notes/gm/pending.json` for only what became true this turn: new facts, a replaced fact, a changed situation. Skip the delta on a turn where nothing durable changed.
6. **Check.** `python tools/gm_state.py check`. Add `--prose <draft file>` to scan the draft for banned terms. Fix errors; do not argue with them. Warnings are for your judgment.
7. **Deliver, then commit.** Append the entry as usual. After it is in the log, `python tools/gm_state.py commit`. If delivery failed or you revised the prose, `discard` or edit the pending delta so state matches the prose that was actually delivered. Then validate and release the pause.

## What belongs in a delta

- `entry`: the id of the entry that shows it happening (yours, or the Director's for something they told you).
- `why`: one line naming the event or player action. No state change without one.
- `ops`: at most 12, each short. Facts are one sentence. Tag every fact with the names and places it concerns, or it will never come back into your hot context. Pin only what must stay in view.

```json
{"entry": "<uuid>", "why": "Mara admitted the debt when the player showed the ledger",
 "ops": [
  {"op": "add", "kind": "fact", "id": "F7", "status": "established", "source": "story",
   "text": "Mara owes the harbourmaster a debt of nine silver.", "tags": ["Mara", "harbourmaster"]},
  {"op": "set", "kind": "situation", "fields": {"day": 2, "time": "dusk", "location": "Harbour office",
   "present": ["Mara"], "problem": "Mara wants the ledger back", "scene": "s4"}}
 ]}
```

Fact status: `established` (true in the fiction), `rumour` (said or believed, not confirmed), `provisional` (your own idea, not yet shown), `outdated` (no longer true; kept for provenance). Set `known` to false for a truth the protagonist has not learned.

Changing an established fact is a story event: use `replace` with a reason (it records the old one as outdated). Promoting a rumour needs a reason. Time may not move backwards unless the scene is a flashback (`"flashback": true`).

## Threads (phase 2): what must not be forgotten

A thread is an obligation the story has taken on. Types: `promise` (someone said they would), `mystery` (a question the player wants answered), `consequence` (something the player did that the world will answer), `relationship` (a bond that is changing), `callback` (a detail worth echoing later). Open one only when it will change what you write; skip incidental detail.

```json
{"op": "add", "kind": "thread", "id": "T3", "type": "promise", "due_day": 6, "tags": ["Mara"],
 "text": "The player promised Mara the ledger back before the tide turns."}
{"op": "update", "kind": "thread", "id": "T3", "touch": true}
{"op": "resolve", "kind": "thread", "id": "T3", "outcome": "fulfilled", "resolution": "Returned at the pier."}
```

- **Lifecycle.** `open` (noted) → `active` (in play) ↔ `dormant` (parked, out of the hot context) → `resolved` (finished: keep a one-line `resolution`, which leaves the hot context) or `discarded` (unused preparation, with a reason). Resolved and discarded are final.
- **Promises** end with an `outcome`: `fulfilled`, `broken` or `released`, in an entry that comes after the one that made the promise. Never mark one fulfilled without the scene that shows it.
- **Use `touch: true`** whenever a thread genuinely advanced in a scene, even if nothing else about it changed.
- **Warnings are advice.** An overdue promise or a thread untouched for five scenes shows as `WARN` at the top of `hot`. You decide what the fiction needs: pay it off, complicate it, let it lapse with a consequence, or park it. A warning never forces an event.
- **Retire on purpose.** At a scene or chapter boundary run `python tools/gm_state.py review` (Review, Retire, Refresh, Reopen). Park, resolve or discard what has run its course, and discard provisional facts you never used (`"status": "discarded"`, with a reason).
- **Consequences first.** Promises and consequences stay in the hot context even when their tags do not match the scene, because those are the ones a good game master never lets slip.

## Self-checks the script cannot do

Before you deliver, ask yourself:

- Does the prose contradict anything established in the hot context?
- Did I decide something consequential for the protagonist?
- Did I let a rumour or a character's belief read as narrator fact?
- Does my delta describe what the final prose actually shows, no more and no less?
- Does anything cross the contract's boundaries?

## After an Undo

Run `python tools/gm_state.py reconcile`, then `--apply`. It sets aside every change that cited a withdrawn entry, and any later change that depended on one, and keeps a private copy in `notes/gm/withdrawn.jsonl`. Facts whose prose still stands but whose delta was set aside must be restated in a new delta.

## Do not track

Complete transcripts, every NPC's biography, every possible future scene, a full world simulation, arbitrary numeric relationship scores. If a record will not change what you write, leave it out.
