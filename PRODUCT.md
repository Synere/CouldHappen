# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A local human who plays a fictional character and also acts as Director, discussing ideas and preferences with an existing writer agent. The interface supports sustained reading, creative participation, and constructive out-of-character discussion.

## Product Purpose

CouldHappen is an experiment in what a modern general-purpose coding agent can contribute to interactive fiction and AI roleplaying when given freedom and responsibility to develop its own creative practice as an author/game master. It supplies a portable fiction workspace operated through project skills, hooks, files, and small local helpers. The browser is the human's play interface. Success means useful, believable fiction with meaningful player influence and durable knowledge that a fresh agent context can recover from the workspace.

## Operating Context

The human opens the story directory in a compatible existing agent and asks it to start. The agent launches an editable local browser interface, reads human entries from shared files, maintains its private materials, writes prose, and waits locally for more input. The story conversation contains player input and writer prose; Director discussion uses a distinct log. The host supplies model calls, tools, permissions, and session behavior.

Claude Code and Codex are required targets. The approved validation order is Codex interactive CLI, then Claude Code interactive CLI, with Pi's native OpenRouter route as the additional reference for human-selected models. Other capable harnesses remain eligible through the common capability checklist; named-host setup examples stay separate from the core skill. Actual compatibility is not yet demonstrated.

The player can ask the loaded writer agent to “set up.” The agent establishes its actual capabilities, checks or installs prerequisites as permitted, installs project dependencies, starts/reuses the local services, and verifies the intended workspace.

## Capabilities and Constraints

- One author/game master can portray the entire cast. Different worlds and genres must remain possible.
- Creative initiative is part of the main writer role. The writer can develop useful methods, mechanics, tools, or interface changes using its actual capabilities, while remaining responsible for fiction, Director authority, player influence, recoverability, and interoperability. Optional examples illustrate possibilities; deliberate simplicity is valid, with no required system, tool quota, reflection schedule, or initializer.
- The initial demonstration is one short scene with a human world prompt, PNG/JSON character-card imports, several story exchanges, a Director exchange, an in-scene fresh-context handoff, and checkpoint-limited Undo.
- Existing card PNGs appear in a cast panel. Import is a Director action and does not automatically reveal a character. No runtime story image generation is required for the first scene.
- Story reading is the primary activity. Director discussion is constructive and can inspire later writing without automatically advancing the fiction.
- The writer saves prose normally; the browser animates new prose. Established prose changes require Director authorization, including standing permission to quietly repair small understood technical/mechanical failures across code, affected records, and prose. Material failures or uncertain consequences are explained in Director discussion. Ordinary creative revisions remain Director-guided. Authorized changes can update directly, with a change indicator if inexpensive.
- The writer controls a prose-production block covering player-action and Director submissions. This concerns actual writing, separately from animation. Browser Stop is deferred. There are no Accept/Revise controls or pending/accepted publication workflow.
- Undo is a Director instruction. The writer explains available Git recovery, retains applicable human corrections and useful skill/interface improvements by default, restores the supported scope, and asks for direction before writing again. Improvements can be included in Undo explicitly. Exact per-interaction rollback is not guaranteed.
- Notes, preferences, and disclosed/established knowledge must survive context loss. The writer can reorganize its records, skills, scripts, and methods. Saved host chat context is optional.
- Work/failure explanations belong in Director discussion and existing host diagnostics. A basic helper error or reopen indication may still be needed; no custom activity dashboard is required.
- Trusted local use with normal host permissions. Credentials stay in host/user configuration and outside story records and source control.
- The browser template and supplied helper source are editable by the player and agent. The approved stack is a small Python loopback file helper and client-side Svelte/Vite interface, normally served live with HMR. Periodic browser reads pick up saved data; the agent's input wait is separate.

## Brand Commitments

CouldHappen is the working project name. The user accepted cast-panel placement and requested a fresh visual direction because the earlier project's interface felt boring. No prior palette, typography, or visual theme is binding. The user selected Woven anthology in the actual Impeccable direction round: petrol/teal shell, saffron accents, pale cool reading surface, serif prose, sans controls, and restrained interlaced rules. Reference: .impeccable/mocks/decision/woven.png. This is visual-direction approval; scene content and portraits remain illustrative. Avoid making one permanent genre the template's identity. On 2026-11-11 the reader was restyled as a dim petrol room (centred column, hairline rules, a backdrop layer) that keeps the petrol and saffron accents but drops the pale reading surface ([ADR-6](docs/decisions/ADR-6-dark-petrol-reader.md)); [DESIGN.md](DESIGN.md) describes the current design.

## Evidence on Hand

The predecessor docs/history/planning/concepts_brief.md and docs/history/planning/brainstorming_notes.md record the brainstorm scope and history. The approved [design](docs/designs/couldhappen.md), [technical decisions](docs/history/planning/technical_plan_decisions.md), and [predecessor reconciliation](docs/history/planning/design_reconciliation.md) record the later architecture and standing author instructions. The final design is saved at `docs/designs/couldhappen.md`; [implementation handoff](docs/history/implementation_handoff.md) and [documentation index](docs/README.md) explain the current layout. docs/reviews/goldfish_review_report.md contains six completed concept reviews, not runtime certification. docs/research/prior_imagery_findings.md links read-only historical placement references; their illustrative story text and portraits are not supplied character-card assets. No real scene or card library has been provided in this workspace. Any mockup example fiction or portraits must be identified as illustrative.

## Product Principles

- Preserve readable prose and meaningful human influence.
- Keep story participation and Director discussion understandable and distinct.
- Reuse the existing agent's execution and methods rather than build a controller.
- Treat durable workspace knowledge as the basis of continuity.
- Encourage resourceful initiative and deliberate simplicity; judge methods by their contribution to the fiction, player experience, and continuity.
- Explain recovery and status according to what the system actually knows.
