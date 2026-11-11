---
type: research
status: completed
updated: 2026-11-11
---

# Character-card imagery: selected prior-project findings

**Purpose.** A record of what was investigated before the design was approved. It is kept as evidence and is not updated.

> Historical research record. Current scope and implementation decisions are in the [approved design](../designs/couldhappen.md); start a future implementation session with the [handoff](../history/implementation_handoff.md). Document paths were normalized during organization; byte-exact earlier files are preserved in the [archive](../history/archive/README.md).

- Inspected: 2026-11-03 (Asia/Manila)
- Stage: EGM brainstorming, read-only historical investigation
- Scope: The user's request to consult MightHappen for existing card imagery and portrait presentation.
- No files in MightHappen were modified, and no credentials or assets were copied.

## Current-project direction supplied by the user

The first short demonstration uses the PNGs supplied with imported SillyTavern character cards. AI-generated imagery is deferred for that demonstration. PNG and JSON import remain retained goals; a JSON-only card does not by itself supply a portrait.

The initial package should still include adaptable guidance for image-generation capabilities supplied by the host or user, as requested in the original handoff. Deferring generation in the first demonstration does not remove that guidance or make a provider integration necessary.

## What the earlier project selected

- Reuse the original PNG card as the character portrait, preserving it and the source definition separately from the writer's evolving character interpretation. Earlier import scope (`MightHappen: docs/designs/autonomous-writer-harness/character_card_import_contract.md`).
- Put portraits in a cast panel beside continuous prose. This lets one author response portray several characters without assigning the entire response to one portrait or dividing every passage by speaker. The reference also records that the panel consumes width and needs a different treatment on small screens. Placement comparison (`MightHappen: design-references/portrait-placement/README.md`).
- Let the writer choose which names and portraits are player-facing. Importing a card does not automatically reveal the character. Names and images are disclosures that need continuity tracking. Earlier cast behavior (`MightHappen: docs/designs/autonomous-writer-harness/character_card_import_contract.md`).
- Keep the displayed portrait association separable from the preserved source so later images can be used. This is a useful distinction, not a requirement to build a media pipeline now. Earlier import and portrait guidance (`MightHappen: docs/designs/autonomous-writer-harness/character_card_import_contract.md`).

## Visual evidence inspected

Viewed A: cast-panel reference (`MightHappen: design-references/portrait-placement/a-cast-panel.png`). It shows a large continuous story area and player composer, Story/Director navigation, and a right-hand panel with two named portraits. Its mystery text and faces are illustrative. It also includes old Pending/Accept/Revise controls, which are not selected for CouldHappen.

The placement reference was not approval of its styling. A later Impeccable direction selected an aubergine frame, light reading surface, serif prose, and muted-gold emphasis under the name Serial fiction. That later palette and stack were approved for the earlier project, not this one. Earlier UI brief (`MightHappen: docs/designs/autonomous-writer-harness/ui_design_brief.md`).

The earlier brief also called for long-form reading, a collapsible or secondary cast view on narrow screens, mixed portrait art styles, and preserving the reader's position instead of forcing a jump to the latest prose. These are possible starting considerations for the later Impeccable template work, not new-project visual approvals.

The implementation status (`MightHappen: docs/implementation-status.md`) reports that the full demonstrator UI had not started and that the client was a bootstrap. These findings establish historical design intent and a visual reference, not working import/display or recovery behavior.

## Current carry-over and design direction

The user has accepted a cast panel displaying supplied card PNGs and explicitly removed the earlier Accept/Revise controls. Impeccable remains the selected tool, with an actual fresh comp-led design pass requested and allowed later in this brainstorm once the demonstration has a concrete brief. Generated interface mockups are design artifacts; generated story imagery remains deferred.

Proposed supporting behavior remains a prose-first view, writer-managed public cast with free-form private character records, and narrow-screen access that preserves the reading area. No visual theme is selected. The user described the earlier UI as boring, so the prior Serial fiction look is not a target to reproduce.

Do not inherit the old application's cast manifest, transactional publication states, SQLite source storage, recovery matrix, frontend stack, or Serial fiction palette through this imagery decision. We still need a small way for the editable template to discover public names and portrait locations; exact files and format are unselected.

## Current clarification

PNG reuse and cast-panel placement are settled. Visual direction will be developed through the scheduled Impeccable comp-led pass. Public portrait discovery and disclosure behavior still need a small agreement suited to this workspace, without inheriting the old application's machinery.
