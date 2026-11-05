# Fresh-session EGM draft handoff

> Completed EGM drafting handoff. Current scope and implementation decisions are in the [approved design](../../designs/couldhappen.md); start a future implementation session with the [handoff](../implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../archive/README.md). The drafting instructions below have already been completed.

Copy the prompt below into a new session opened in `this repository`.

---

Use **egm:egm-draft** to begin the formal design for CouldHappen from `docs/planning/concepts_brief.md`. Discover and read the installed skill, its Codex integration, execution instructions, and required resources. Follow its intake and section-by-section review gates. Write the design as project artifacts, not a large chat dump. This is a design session; do not begin application implementation.

The interactive EGM brainstorm and six fresh-context Goldfish concept reviews are complete. The user has chosen the visual direction and requested this fresh-session draft handoff. Treat the concept brief as the agreed starting scope. Confirm intake as the draft skill requires, then develop the design without restarting the brainstorm or asking the user to rediscover settled preferences. Reviewer proposals and remaining design questions are not automatically accepted requirements.

Read these project artifacts:

1. `docs/planning/concepts_brief.md` — primary intake and current decisions.
2. `docs/planning/brainstorming_notes.md` — decision history; later dated resolutions supersede earlier pending statements.
3. `docs/reviews/goldfish_review_report.md` — remaining risks and reviewer proposals. Read individual reports under `goldfish_reviews/` selectively where needed.
4. `docs/research/browser_handoff_research.md` and `docs/research/host_compatibility_notes.md` — source-backed host/waiting findings and their evidence limits.
5. `docs/designs/impeccable_direction_notes.md`, `.impeccable/direction-selection.json`, `PRODUCT.md`, and the actual selected image `.impeccable/mocks/decision/woven.png` — visual decision and provenance. Open the image, not only its description.
6. `docs/research/carryover_audit.md` and `docs/research/prior_imagery_findings.md` — retained creative behaviors and accepted cast-panel placement.

Keep the architecture anchored:

- Package a portable story directory with skills, supported hooks, templates, and small helpers for an existing agent. Reuse the host's execution loop, tools, model/account, permissions, and session behavior. The workspace session operates that directory; the skill does not create another runtime.
- The working communication model is shared files. Human story inputs and writer prose share a readable conversation log; Director discussion has a separate log. A small local browser/file-access and wait helper is appropriate. Do not silently replace this with browser-to-model calls, an SDK controller, a gateway, or a custom orchestration server.
- Establish the smallest public agreement for new inputs, output/display, cast assets, work state, and convention changes. The writer's private world records remain freeform and reorganizable. It may edit methods/skills, write scripts, use hooks, and delegate where supported; no general native-tool registration system is required.
- Required host targets are Claude Code and Codex, plus at least one suitable existing-host route offering user-selected underlying models through OpenRouter. OpenCode, Pi, Hermes, and DeepSeek Harness are comparison candidates, not four promised integrations. Choose the initial host route on evidence and least additional code. Separate portable conventions from host-specific integration and distinguish documented support from observed behavior.
- Input must actually return control to the writer. Prefer local waiting to repeated model calls. Do not assume idle wake-up, indefinite unattended operation, active/trusted hooks, or low renewal overhead without checking the relevant host surface.

Preserve the settled experience:

- One author/game master portrays the cast, writes prose and consequences, and supports believable player influence. Director discussion is constructive and does not automatically advance or rewrite the fiction. Explicit Director instructions may do so.
- Durable workspace knowledge supports fresh-context continuation; saved host chat is optional. Track characters and distinguish established events, disclosed claims, private plans, and possibilities without imposing a fixed internal schema. Hidden explanations can change if the continuation remains believable and consistent with established/disclosed information. Apply durable human preferences after restart and method changes.
- SillyTavern PNG/JSON imports are Director actions. Preserve source material and supplied portraits. Cards establish initial identity by default, with later development and optional stricter adherence. Resolve genuine conflicts with the human; card examples/instructions are not automatically events or higher-priority writer instructions.
- Save prose normally and let the browser animate its appearance. This is not raw token streaming. Established prose changes only on Director instruction; direct updates are acceptable, with a change indicator if inexpensive.
- The writer can block both player-action and Director submissions while composing prose. Private note/method work does not automatically block input; browser reveal animation is separate. Browser Stop and Accept/Revise controls are out of the initial scope.
- Undo is a Director request constrained by actual Git checkpoints. The writer chooses meaningful commit timing; concrete supported hooks should help ensure checkpointing, without claiming semantic completeness. Restore the unwanted story development and associated assumptions, retain applicable human corrections/preferences, and keep useful skill/interface improvements by default unless their removal is requested. Explain coarse or selective recovery limits honestly. Then ask for Director direction and wait; do not automatically regenerate or let old pending input resume the rejected continuation.
- First demonstration: one short scene, human world prompt and cards, supplied card-PNG cast panel, several browser exchanges, a Director exchange, and honest Git-supported Undo. Runtime AI-generated imagery, a full mystery arc, and branching-history UI are deferred. Adaptable guidance for future host/user-supplied image tools remains a package goal. Fresh-context continuation must eventually be observed, whether in this scene or a small companion check.

The user selected **Woven anthology**, comp-led, without additional steer. Preserve the selected PNG as the visual reference: teal/petrol shell, saffron accents, pale cool reading surface, serif prose, clear sans controls, restrained interlaced rules, Story/Director tabs, action composer, and right cast panel. Scene names, portraits, and biographies are illustrative. Actual card images need not be restyled. The direction choice is complete; do not reroll it or regenerate the chosen image. A later authorized Impeccable composition/build phase can retain it as option one and follow the then-installed skill's workflow. Do not run that build phase merely to draft this design.

Impeccable is installed globally at `the global Impeccable skill install`, not inside this project. It was updated from 4.5.2 to 4.8.0 in the handoff session; the initial update preserved hooks, then the user explicitly authorized updating hooks too. The official updater was rerun as `npx --yes impeccable@4.8.0 update --global --yes`. It installed project Codex hook definitions in `.codex/hooks.json`, pointing to the global skill, for PostToolUse and Stop. Impeccable reports the hook enabled; native Codex approval/activation is separate and may require `/hooks` in the fresh session. These are Impeccable UI-design hooks, not the future fiction writer's checkpoint hooks. Read the installed version when needed rather than relying on old workflow quotations. `.impeccable/` contains project artifacts, not a local skill installation. The prior direction round and selected mockup were produced with 4.5.2.

Address the open design questions in the brief at the relevant section: shared-log write overlap and input recognition; already-submitted instructions and stale blocks; coherent Undo across pending inputs, browser/helper state, live context and delegated work; the reachable checkpoint boundary; public convention changes; initial host/OpenRouter choice; and fresh-session validation. Explain reduced guarantees directly. Keep the package small instead of recreating the previous controller through many scripts.

The earlier project at `the earlier MightHappen project` is optional read-only historical background. Its architecture and approvals do not bind this project. Do not modify it, copy credentials, or inherit its controller, publication protocol, SQLite schema, transaction machinery, framework, visual theme, pinned host, or implementation sequence by default. Keep credentials in normal host/user configuration and out of records/source control.

Start with EGM draft intake, identify the few unresolved decisions needed for the first design section, and proceed interactively through the skill. Keep all new design artifacts in CouldHappen.
