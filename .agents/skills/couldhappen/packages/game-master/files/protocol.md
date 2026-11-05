# Game-master protocol (private; read at the start of a session and when unsure)

Prepare situations, not scripted plots. Track causes and consequences, not transcripts. The player decides what the protagonist does; the world decides what happens next.

Six questions to answer before you write: What must remain true? What matters to the protagonist? What is happening without them? What must not be forgotten? What could they discover? What makes this moment worth playing?

Phase 1 covers the first (what must remain true) and the start of the second. Phase 2 covers the fourth (what must not be forgotten). Phase 3 covers the third (what is happening without them). Phase 4 covers the fifth (what they could discover). Later phases add the rest here.

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

## Pressures and cast (phase 3): what is happening without the player

A **pressure** is someone who wants something and will act whether or not the player is watching: a faction, an antagonist, a rival, a frightened witness. Give each a `goal`, a `next_action`, a `trigger` (what makes them move) and, if it helps, a `clock_max` (2 to 12 steps toward `consequence`, what happens if nobody stops them).

```json
{"op": "add", "kind": "pressure", "id": "P1", "actor": "Harbour guild", "goal": "seize the ledger",
 "next_action": "send a bailiff to Mara", "trigger": "the player is seen with the ledger",
 "consequence": "Mara is arrested", "clock_max": 4, "tags": ["guild", "Mara"]}
{"op": "advance", "kind": "pressure", "id": "P1", "steps": 1, "basis": "event",
 "reason": "the player was seen at the pier", "next_action": "the bailiff waits outside Mara's door"}
{"op": "advance", "kind": "pressure", "id": "P1", "basis": "offscreen", "steps": 1,
 "reason": "three days passed", "evidence": "guild notices nailed to every door"}
{"op": "resolve", "kind": "pressure", "id": "P1", "outcome": "thwarted", "resolution": "The ledger burned."}
```

- **Advance only what is justified.** `basis` is `time`, `event`, `action` or `offscreen`, always with a reason. Never advance everything on a whim; advancing more than two in one delta draws a warning.
- **Off-screen means observable.** An off-screen move needs `evidence`: the sign the protagonist can later find. If the world moved and nothing shows it, the player cannot feel it.
- **Full clocks come due.** When a clock fills, `hot` warns. Let the consequence land, or resolve the pressure as thwarted with an explanation. Do not leave it hanging.
- **Lifecycle.** `active` ↔ `dormant` (with a reason), then `resolved` (outcome `achieved`, `thwarted` or `abandoned`) or `discarded`. Dormant pressures cannot advance until woken.
- **A waiting world is a warning, not an order.** If no pressure has moved for five scenes, `hot` says so. Ask whether any actor has a reason to act now; if not, say nothing.
- **Time skips.** Before narrating a skip, run `review`: its REFRESH section lists each active pressure, its next action and its trigger. Decide each in turn and leave evidence.
- **Cast cards.** `{"op": "set", "kind": "npc", "id": "N1", "fields": {"name": "Mara", "want": "...", "fear": "...", "secret": "...", "voice": "...", "attitude": "..."}}`. One short phrase per field. A card is shown in `hot` only while the character is in `present`. Use attitude phrases ("wary, but wants help"), never numeric scores. Keep cards for recurring characters; leave walk-ons uncarded. An NPC's `secret` is their own; a truth the player must be able to discover belongs in a revelation (phase 4).

## Revelations (phase 4): what they could discover

A **revelation** is a hidden truth the player can find out, tracked apart from where or how they find it, so a surprising approach never hits a dead end. The truth itself is an ordinary canon fact with `"known": false`; the revelation holds the routes to it.

```json
{"op": "add", "kind": "fact", "id": "F9", "status": "established", "source": "story", "known": false,
 "text": "The harbourmaster forged the ledger.", "tags": ["harbourmaster"]}
{"op": "add", "kind": "revelation", "id": "V1", "fact": "F9", "importance": "required", "tags": ["harbourmaster"]}
{"op": "route", "kind": "revelation", "id": "V1", "route": "a", "how": "Mara confesses if pressed"}
{"op": "route", "kind": "revelation", "id": "V1", "route": "b", "how": "the back pages of the ledger", "where": "Harbour office"}
{"op": "route", "kind": "revelation", "id": "V1", "route": "c", "how": "the clerk remembers the ink"}
{"op": "clue", "kind": "revelation", "id": "V1", "route": "b", "reason": "the player read the back pages"}
{"op": "reveal", "kind": "revelation", "id": "V1", "route": "b", "how": "the player put the pages beside the harbourmaster's own hand"}
```

- **Required vs optional.** `required` means the story cannot go on without the player learning it; give it three open routes of different kinds (a person, a place or object, a consequence of events). `optional` truths need no minimum.
- **Routes are adaptable.** A route is a way the truth could surface, not a scripted scene. When the player does something unexpected, use the nearest route or add one (`route`), as long as it does not contradict established facts. If a route is lost (the informant dies, the place burns), `block` it with a reason and add another.
- **Clues are partial.** `clue` marks a route as used and makes the revelation `partial`: the player has a piece, not the answer. Use it when a route yields something short of the truth.
- **Reveal only on the page.** `reveal` flips the fact to known and needs a `how` that matches what the prose actually shows. Never reveal in a delta for a scene where the player did not learn it.
- **If the truth changes** (twist, rewrite), `replace` the fact, then `update` the revelation's `fact` to the new hidden one, with a reason. A revelation pointing at an outdated fact is flagged.
- **Retire.** `discard` a revelation, with a reason, when the story no longer needs it. The fact stays hidden.
- **Hidden means hidden.** Everything under "WHAT THE PLAYER COULD DISCOVER" is writer-private. Never state it as narrator knowledge before it is revealed; characters may hint, lie, or be wrong.

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
