---
type: research
status: completed
updated: 2026-11-11
---

# Previous-project carry-over audit

**Purpose.** A record of what was investigated before the design was approved. It is kept as evidence and is not updated.

> Historical research record. Current scope and implementation decisions are in the [approved design](../designs/couldhappen.md); start a future implementation session with the [handoff](../history/implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../history/archive/README.md).

- Date: 2026-11-03 (Asia/Manila)
- Stage: EGM clarification before readiness approval
- Scope: Read-only comparison of MightHappen's creative/product decisions with the new handoff and current brainstorming notes.
- Status: The user has now explicitly accepted the six product behaviors below for CouldHappen, with the clarifications in the following section. Their authority is this new-project conversation, not the earlier approvals.

## User resolution after reading the audit

- Director discussion is constructive back-and-forth and a source of inspiration for both human and writer. It does not automatically advance fiction or establish hypothetical events. It may influence private possibilities and later writing, and update preferences or working methods.
- Imports are Director actions. Compatible adaptation remains autonomous; genuine initial-card/world conflicts ask for Director guidance.
- Card interpretation as source material is accepted.
- Reading previous prose for voice, pacing, and continuity is accepted and reinforces the usefulness of the shared prose/story file.
- Preferences can be conveyed naturally to the agent. It records and applies them, adapting or reorganizing its methods as useful; a fixed injection system is not required.
- Director chat is the main human-facing channel for discussing work and failures. Keep fiction distinct and reuse the host's existing diagnostics. If the host/helper is unavailable, a basic interface status may still be needed; this is an open practical detail, not adoption of a separate dashboard.

The original audit findings below explain the provenance and remain useful historical analysis. Their earlier recommendation labels are superseded by this resolution where applicable.

## Finding

The main creative goals are already represented. A few smaller behaviors deserve explicit treatment, especially Director discussion, character-card adaptation, how the writer reads prose, and what failures look like to the player. These can remain skill guidance and simple interface behavior; none requires importing the old controller.

## Partly covered behaviors worth discussing

### 1. Director discussion does not advance the story by itself

The earlier design allowed out-of-character questions, planning, persistent guidance, and changes to undisclosed plans or working methods. Ordinary discussion did not advance fictional time. Changes to presented fiction required an explicit revision request. Earlier Director behavior (`MightHappen: docs/designs/autonomous-writer-harness.md:129`).

Current notes distinguish Director and story logs and already require explicit instructions to revise established prose. They do not yet explicitly say that merely discussing possibilities does not make them happen in the fiction.

Recommendation: distinguish discussion from an instruction to act. The writer can answer a Director question without producing another story passage, and should not turn a hypothetical into an established event. An explicit Director request to continue or change the story can still authorize that work. This is a behavioral convention, not a new transaction state.

### 2. Genuine conflicts between a card and the world prompt

The earlier project asked the Director before resolving a genuine conflict between imported initial identity and an explicit world premise, while letting the writer adapt compatible details itself. Earlier decision (`MightHappen: docs/planning/brainstorming_notes.md:183`), Earlier starting-world behavior (`MightHappen: docs/designs/autonomous-writer-harness.md:117`).

Current notes preserve initial identity and permit extrapolation, but have not settled what takes precedence when those starting inputs cannot both hold.

Recommendation: let compatible adaptation proceed and ask the Director when satisfying one supplied premise would materially change the other. Save the resolution. This does not require an import acceptance matrix or a clarification server.

### 3. Cards are source material for an author/game master

The earlier import guidance treated scenarios, greetings, example dialogue, and roleplay instructions as source material. They were not automatically governing instructions or established events. Earlier import guidance (`MightHappen: docs/designs/autonomous-writer-harness/character_card_import_contract.md:11`).

Current notes cover initial identity and source preservation. It would help to say explicitly that importing a single-character roleplay card does not turn the writer into only that character or make a supplied example conversation part of the story history.

Related earlier choices were importing additional cards during play through Director input and not revealing a character merely because its card was imported. Earlier mid-play import decision (`MightHappen: docs/planning/brainstorming_notes.md:177`). Public cast selection is already discussed in docs/research/prior_imagery_findings.md; import timing is not fully settled in this brainstorm.

### 4. Existing prose is a writing resource

The earlier writing guidance had the writer consult the manuscript for voice, pacing, and continuation, choosing relevant portions without loading the whole thing every turn. Earlier prose guidance (`MightHappen: docs/designs/autonomous-writer-harness.md:111`).

The new shared story log is an intentional difference from the old prose-only manuscript. It already supports a readable log and preserves player contributions. Do not undo that choice or require a second canonical manuscript merely to match the old design.

Recommendation: retain the outcome that the writer can find and read prior fiction for literary continuity. Distinguishable entries or a derived reading/export view might help later, but no extra file or schema is selected here.

### 5. Preferences must be reused, not merely stored

The earlier project used Director guidance for creativity/card adherence and required important guidance to persist and reach later writing. Earlier preference decision (`MightHappen: docs/planning/brainstorming_notes.md:187`), Earlier Director behavior (`MightHappen: docs/designs/autonomous-writer-harness.md:129`).

Current notes already require durable preferences and fresh-context continuation. What remains implicit is the writer's responsibility to consult applicable preferences during normal writing, including after it reorganizes its methods.

Recommendation: make that a starter-skill responsibility. Host-supported reminders may help; the old automatic injection/publication integration is not a carry-over requirement.

### 6. Useful visibility into failures and work

The earlier project wanted tools, usage, elapsed work, and errors inspectable separately from fiction. It also distinguished missing prose from a successful story response. Earlier observability goal (`MightHappen: docs/designs/autonomous-writer-harness.md:35`), Earlier missing-prose behavior (`MightHappen: docs/designs/autonomous-writer-harness.md:113`).

The new notes retain cost/responsiveness concerns and expose some writing status, but have not settled the minimum visibility when the agent or helper fails, an input remains unanswered, or a task takes a long time.

Recommendation: keep story prose distinct from work commentary and show actionable status when the interface knows delivery failed. Reuse the host's existing logs and usage display where useful. This does not select a custom activity dashboard, exact token accounting, an automatic retry controller, or the old numeric timing limits.

## Already carried or intentionally changed

- Creative authorship, one writer portraying many characters, believable consequences, adaptable private explanations, meaningful player influence, and disclosure tracking are already explicit.
- A complete mystery arc remains a later demonstration. The accepted initial scope is a short scene.
- Fresh-context continuation and survival of changing working methods are already goals. The earlier evaluation also proposed checking the actual player-visible exchanges rather than accepting the writer's notes as proof of continuity. Preserve that evaluation question; no new evidence database follows from it. Earlier evaluation goals (`MightHappen: docs/designs/autonomous-writer-harness.md:29`).
- Exact latest-turn rollback has deliberately been replaced by honest recovery from available writer-chosen checkpoints, followed by waiting for Director guidance.
- Accept/Revise, pending/accepted publication states, browser Stop, and raw token streaming are removed or deferred by current decisions.
- The shared story log deliberately differs from the prior prose-only manuscript.
- Existing card PNGs and cast-panel placement carry over; the old visual theme does not. A fresh actual comp-led Impeccable pass remains scheduled.
- Skills and hooks remain editable, with activation dependent on the chosen host. This is already recorded and is not solved merely by saving their source.
- The earlier project did not establish a universal foreshadowing rule or guarantee that every player theory makes permanent investigative progress. Do not add either as a historical requirement. Meaningful influence and believability remain current requirements. Earlier mystery policy (`MightHappen: docs/planning/concepts_brief.md:21`).

## Assessment before Goldfish review

The user has resolved ordinary Director discussion, starting-input conflicts, and the other listed behaviors as above. Their implementation details remain open for later design and should not block concept critique by themselves.

No architecture-changing omission was found that by itself justifies reinstating the earlier application. The accepted behaviors come from the user's explicit response to this audit. Readiness remains pending explicit confirmation; no Goldfish agents have been launched.
