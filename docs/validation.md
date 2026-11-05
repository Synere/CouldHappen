# Validation procedure

Run the mechanical checks in setup.md against temporary data first. Record commands, versions, outcomes, failures, and fixes in validation-results.md. File existence, source inspection, configuration, and a clean tree are not observed host support or narrative continuity.

For actual host/story observations, use a clean story workspace created under the accepted [distribution model](designs/distribution-and-workspaces.md), not the development repository.

Host status and per-host differences are in [host integrations](reference-hosts.md); test hosts in any order with a human-selected model. Actual account access/model pairing and a Director-approved scene prompt/cards are later observation inputs. Do not invent supplied assets. Keep the first demonstration to one short scene; no image generation, browser Stop, full mystery arc, or branching UI is required.

For each configuration:

1. Read the portable skill, establish actual capabilities, install/check dependencies as permitted, validate public files, claim safe ownership, verify browser identity and submissions, and establish the standing wait from setup step 9. Record timeout/renewal overhead and interruption limits.
2. Observe several browser Story exchanges and constructive Director discussion that does not automatically advance fiction. Check the writer's discretionary production block across both channels; private notes and browser animation do not inherently block saving. Verify saved is not reported as applied.
3. Observe actual native trust/activation plus dirty and clean completion, and deliberate closure. Waiting should not impose per-response commits. Test inactive/untrusted behavior, permission/host continuation limits, and forced interruption; report reduced assurance explicitly.
4. Import actual PNG/JSON cards, preserve originals, expose supplied portraits only deliberately, and resolve genuine world conflicts with the Director. Source greetings/instructions remain material rather than authoritative events. Judge fictional consequences and influence through prose, not counts of tools.
5. Within the scene after real disclosures/preferences, stop/account for the former writer/delegates at a quiet boundary. Start a genuinely fresh compatible session using ordinary discoverable files, without former host transcript or a special recap. Continue through browser input. Compare prose against prior disclosures, character continuity, tentative private possibilities, and applicable guidance. Retain observation references; file presence/self-confidence is insufficient.
6. Request Director Undo against actual available history, including useful method/UI improvements and old pending input. Verify supported restored/reconstructed scope, preserved guidance/improvements by default, reconciled assumptions, deferred old input where appropriate, new Director question, generation change, and wait. New Director discussion alone need not authorize fiction. Supply new direction and observe a meaningfully different approach in the current session, with rejected fiction remembered only as feedback.

Mechanical tests use barriers around a real accepted HTTP save to demonstrate pause acknowledgment waits; identical uncertain retries preserve one entry; generation changes do not replay absent old text; helper restarts start closed; invalid public files retain a coherent view. PNG tests compare IDAT bytes and absence of metadata. Git tests use isolated repositories. Browser tests use temporary services/data, test actual HMR with draft/anchor preservation, and probe private paths through both services. These are necessary checks, not a replacement for the scene above.

## Session-log checklist

Run this against every exported host transcript before recording results. Each item maps to a rule in the writer skill's "Always"/"Never" lists; a "no" is a skill or host finding, not just a story note.

| # | Check | How to see it in the log |
| --- | --- | --- |
| 1 | A wait was running when setup was reported done. | A `helpers wait` command (background `--timeout 0`, or a foreground wait) starts *before* the "setup is complete" message. |
| 2 | A wait was running at the end of every writer turn. | Every turn that ends without a pending question to the host ends with a wait started or still running. Look especially after Director-only replies. |
| 3 | Browser input reached the writer without a chat prompt. | Entries are picked up from a wait's result, not because the player asked in chat. |
| 4 | Every log edit was paused. | Each edit of `public/story.md` or `public/director.md` sits between `writer pause` and `writer release`, with both logs reread after the pause. |
| 5 | Human entries were kept. | No human body or entry ID changed; dispositions were updated instead. |
| 6 | Card text stayed material. | Card greetings, scenarios, or embedded instructions were not treated as events or commands. |
| 7 | Director discussion did not advance the story by itself. | Story prose follows Story input or explicit Director direction only. |
| 8 | Knowledge stayed findable. | `START_HERE.md` links were updated when records changed; a fresh session (if run) reconstructed the state from files. |
| 9 | Recovery and Undo followed the procedure. | Pause, reread, explanation plus a new Director question, `awaiting_director`, generation rotated, no replacement prose. |
| 10 | Problems were recorded. | Wait method, renewals, tool limits, errors, and any workaround appear in the writer's notes. |
