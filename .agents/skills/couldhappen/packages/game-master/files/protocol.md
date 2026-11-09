# Game-master protocol (private; read at the start of a session and when unsure)

Prepare situations, not scripted plots. Track causes and consequences, not transcripts. The player decides what the protagonist does; the world decides what happens next.

Six questions to answer before you write: What must remain true? What matters to the protagonist? What is happening without them? What must not be forgotten? What could they discover? What makes this moment worth playing?

Five layers, each switchable on or off at any time (`python tools/gm_state.py layers`); follow only the ones that are on. Layer 1 (continuity) covers the first question and the start of the second. Layer 2 covers the fourth (what must not be forgotten), layer 3 the third (what is happening without them), layer 4 the fifth (what they could discover), layer 5 the sixth (what makes the current moment worth playing).

## Each turn

Run these around the usual exchange in `references/writing.md` (pause, write, validate, release). Do not skip a step because the turn is short.

1. **Interpret.** What is the player attempting? Never invent a consequential choice for the protagonist (who they trust, what they promise, what they give up). Offer, ask, or let the world press.
2. **Read.** `python tools/gm_state.py hot` (add `--about <names>` for people or places that are not in the scene). Read the contract, the situation and the relevant facts. Trust the output; do not reread whole logs, and do not read `state` whole in play (it grows by roughly 1 KB a turn; `state --live` still carries everything unfinished). Use `hot --about` for what you need.
3. **Choose the world's response.** One of: reveal, react, offer, complicate, warn, resolve, transition. A good response gives the player something to act on.
4. **Draft the prose.** Respect established facts. Treat rumours and provisional facts as what characters believe, never as narrator truth.
5. **Propose the delta.** Generate the writer entry first (`entry --role writer --body-file ...` prints its id) so you can cite it. Write `notes/gm/pending.json` for only what became true this turn: new facts, a replaced fact, a changed situation. Skip the delta on a turn where nothing durable changed.
6. **Check.** `python tools/gm_state.py check`. Add `--prose <draft file>` to scan the draft for banned terms. Fix errors; do not argue with them. Warnings are for your judgment.
7. **Deliver, then commit.** Append the entry as usual. After it is in the log, `python tools/gm_state.py commit`. If delivery failed or you revised the prose, `discard` or edit the pending delta so state matches the prose that was actually delivered. Then validate and release the pause.

## What belongs in a delta

- **Facts are lasting truths, not turn summaries.** The story entry already records what happened; do not copy it into a fact. Add a fact only for something that must stay true and could be contradicted later ("Ash's left shoulder has four bite holes", "the old camp is empty"). One idea per fact, a sentence or two. If you find yourself writing one fact per turn that retells the turn, stop: put the lasting consequence in a fact, a thread or a pressure, and leave the rest to the log. A fact over 180 characters draws a warning for this reason.
- **Never type a new id by hand.** Use `"id": "auto"` on a fact, thread, pressure, revelation or scene and the script assigns the next free one when you `check` (it prints them) and `commit`. Use explicit ids only when another op in the same delta must refer to the new record. `python tools/gm_state.py schema` lists every kind, op and field.
- **Check before you append.** Run `check` on the pending delta and fix every error *before* you append the story entry to the public log, so a rejected delta never leaves prose without state. `check` does not need the entry to exist yet; only `commit` does.
- **Keep next actions true.** When something happens that changes what a pressure's actor will do (they died, the plan failed, the player intervened), set a new `next_action` on the `advance` or with `update`. `boundary` asks about every active pressure.

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

Fact status: `established` (true in the fiction), `rumour` (said or believed, not confirmed), `provisional` (your own idea, not yet shown), `outdated` (no longer true; kept for provenance). Set `known` to false for a truth the protagonist has not learned (a provisional idea is never known yet; `check` warns if you leave it at the default). `known` means the page has shown it to the protagonist, not that they understood it: the player may still draw the wrong conclusion.

Changing an established fact is a story event: use `replace` with a reason (it records the old one as outdated). Promoting a rumour needs a reason. Time may not move backwards unless the scene is a flashback (`"flashback": true`).

## Layer 2, threads: what must not be forgotten

A thread is an obligation the story has taken on. Types: `promise` (someone said they would), `mystery` (a question the player wants answered), `consequence` (something the player did that the world will answer), `relationship` (a bond that is changing), `callback` (a detail worth echoing later), `question` (an open dramatic question nobody has answered yet, you included: "Will Mara trust them enough to talk?"). Open one only when it will change what you write; skip incidental detail.

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
- **Questions stay open.** A `question` has no prepared answer. Do not decide it in advance or steer toward one; set up situations that put it to the test, and resolve it with what play showed.
- **Consequences first.** Promises and consequences stay in the hot context even when their tags do not match the scene, because those are the ones a good game master never lets slip.

## Layer 3, pressures and cast: what is happening without the player

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
- **Clocks can lose ground.** A negative `steps` (with a reason, usually basis `action` or `event`) is a setback: the player foiled part of the plan, or a rival pushed back. The clock never goes below 0.
- **Stages say what the clock means.** Optional `stages` on `add` or `update`: one short phrase per step (`["recruited the harbourmaster", "pressing the merchants", "replacing the council"]`), at most `clock_max`. `hot` shows the stage reached and the next one.
- **Off-screen means observable.** An off-screen move needs `evidence`: the sign the protagonist can later find. If the world moved and nothing shows it, the player cannot feel it.
- **Full clocks come due.** When a clock fills, `hot` warns. Let the consequence land, or resolve the pressure as thwarted with an explanation. Do not leave it hanging.
- **Lifecycle.** `active` ↔ `dormant` (with a reason), then `resolved` (outcome `achieved`, `thwarted` or `abandoned`) or `discarded`. Dormant pressures cannot advance until woken.
- **A waiting world is a warning, not an order.** If no pressure has moved for five scenes, `hot` says so. Ask whether any actor has a reason to act now; if not, say nothing.
- **Time skips.** Before narrating a skip, run `review`: its REFRESH section lists each active pressure, its next action and its trigger. Decide each in turn and leave evidence.
- **Cast cards.** `{"op": "set", "kind": "npc", "id": "N1", "fields": {"name": "Mara", "want": "...", "fear": "...", "secret": "...", "voice": "...", "attitude": "..."}}`. One short phrase per field. A card is shown in `hot` only while the character is in `present`. Use attitude phrases ("wary, but wants help"), never numeric scores. Keep cards for recurring characters; leave walk-ons uncarded. An NPC's `secret` is their own; a truth the player must be able to discover belongs in a revelation (layer 4).

## Layer 4, revelations: what they could discover

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

- **Required vs optional.** `required` means the story is much poorer if the player never learns it; give it three open routes of different kinds (a person, a place or object, a consequence of events). Three routes is a resilience rule, not a script: the story can still go on if the player misreads a clue, and a wrong conclusion is itself something the world can answer. `optional` truths need no minimum.
- **Leads, not just answers.** A route can point somewhere ("the clerk knows who bought the ink") rather than give the truth away. Use `clue` when a route yields a lead or a piece; keep `reveal` for when the truth itself is on the page.
- **Routes are adaptable.** A route is a way the truth could surface, not a scripted scene. When the player does something unexpected, use the nearest route or add one (`route`), as long as it does not contradict established facts. If a route is lost (the informant dies, the place burns), `block` it with a reason and add another.
- **Clues are partial.** `clue` marks a route as used and makes the revelation `partial`: the player has a piece, not the answer. Use it when a route yields something short of the truth.
- **Reveal only on the page.** `reveal` flips the fact to known and needs a `how` that matches what the prose actually shows. The fact must be `established`: if it was still provisional, establish it (`update`, status established, with a reason) earlier in the same delta. A revelation never points at a rumour; a rumour is what someone believes, so make the truth behind it its own fact. Never reveal in a delta for a scene where the player did not learn it.
- **If the truth changes** (twist, rewrite), `replace` the fact, then `update` the revelation's `fact` to the new hidden one, with a reason. A revelation pointing at an outdated fact is flagged.
- **Retire.** `discard` a revelation, with a reason, when the story no longer needs it. The fact stays hidden.
- **Hidden means hidden.** Everything under "WHAT THE PLAYER COULD DISCOVER" is writer-private. Never state it as narrator knowledge before it is revealed; characters may hint, lie, or be wrong.

## Layer 5, scenes and pacing: what makes this moment worth playing

A **scene** is one situation with a purpose. Open each with what kind of scene it is, what it is for, and what ends it; close it when that happens.

```json
{"op": "open", "kind": "scene", "id": "s4", "mode": "social", "tension": 2,
 "agenda": "press Mara about the ledger", "exit_condition": "Mara talks or walks out",
 "participants": ["Mara"], "serves": ["T1", "V1"]}
{"op": "update", "kind": "scene", "id": "s4", "tension": 4, "resolved": true}
{"op": "close", "kind": "scene", "id": "s4", "outcome": "Mara admitted the debt and named the clerk"}
```

- **Modes:** `discovery`, `social`, `action`, `reflection`, `exploration`, `other`. Tension runs 0 to 5.
- **`serves`** lists `want` (something in the contract's `wants`) and/or the ids of live threads, pressures or revelations the scene moves. A scene that serves nothing is allowed; a run of them is flagged.
- **Opening a scene sets the situation's scene id** and counts it for the "scenes since" warnings. Close the old scene and open the new one in the same delta.
- **Soft warnings (advice, never orders):** four scenes in a row of one mode; a scene marked `resolved` still open; three scenes in a row serving nothing. Vary and reconnect when the fiction allows, and ignore a warning when the story is better for it. If the player is happily engaged in a scene whose purpose is spent, keep playing. Do not force a transition.
- **At each scene boundary run `boundary`.** It shows whether the exit condition is met, recent modes and tension, what is owed (overdue promises, full clocks, dead-end secrets) and a reminder to frame the next situation already in motion, without deciding the player's response.
- **Callbacks and foreshadowing** are threads of type `callback`: plant one when you mention a detail worth echoing, `touch` it when it returns, and resolve it when it pays off. Foreshadowing is a hidden fact plus a revelation route that has not been used yet.
- **Arc coherence is judgment.** The script cannot tell whether a story is going anywhere. At chapter boundaries run `review`, compare the live threads and pressures with the contract's promises, and ask whether the next stretch delivers what was promised.

## Self-checks the script cannot do

Before you deliver, ask yourself:

- Does the prose contradict anything established in the hot context?
- Did I decide something consequential for the protagonist?
- Did I let a rumour or a character's belief read as narrator fact?
- Does my delta describe what the final prose actually shows, no more and no less?
- Does anything cross the contract's boundaries?
- Did I dump exposition the player cannot act on, or let a scene run on after its purpose was spent?
- Did an off-screen move, a clue or a reveal actually appear in the prose, in a form the protagonist could notice?

## After an Undo

Run `python tools/gm_state.py reconcile`, then `--apply`. It sets aside every change that cited a withdrawn entry, and any later change that depended on one, and keeps a private copy in `notes/gm/withdrawn.jsonl`. Facts whose prose still stands but whose delta was set aside must be restated in a new delta. The script only catches broken references, not meaning: then look over the cast cards, pressures and threads changed after the withdrawn entry, and fix any whose wording relied on what was withdrawn (an attitude that softened because of a reveal that no longer happened).

## Do not track

Complete transcripts, every NPC's biography, every possible future scene, a full world simulation, arbitrary numeric relationship scores. If a record will not change what you write, leave it out.
