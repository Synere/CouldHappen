# CouldHappen documentation

Start with [setup](setup.md), then read the [public contract](public-contract.md) and the optional [host integrations](reference-hosts.md). The [design system](../DESIGN.md) records the reader's visual rules, and [START_HERE](../START_HERE.md) is the writer's reentry index.

The writer skill is at [.agents/skills/couldhappen/SKILL.md](../.agents/skills/couldhappen/SKILL.md).

Keep the workspace private unless you deliberately choose to publish the story. Imports, portraits, private records, and Git history are part of the story archive.

<!-- dev-only -->
## Development documentation

Each fact has one home; other documents link to it rather than restating it.

| Kind of fact | Home |
| --- | --- |
| What the writer agent does | [Writer skill](../.agents/skills/couldhappen/SKILL.md) and its references |
| What the helper and files guarantee | [Public contract](public-contract.md) |
| Setup and release steps | [Setup](setup.md) |
| Per-host differences and status | [Host integrations](reference-hosts.md) |
| What was observed, and when | [Validation results](validation-results.md), using the [validation procedure](validation.md) |
| Current state and next steps | [Implementation progress](implementation-progress.md) |
| Requirements and architecture | [Approved design](designs/couldhappen.md) and [distribution and workspaces](designs/distribution-and-workspaces.md) |
| Why a decision was made | [Architectural decisions](decisions/README.md) |
| Visual system | [DESIGN.md](../DESIGN.md), [product context](../PRODUCT.md), [reader surface direction](designs/woven/reader-surface-direction.md) |

Supporting material:

| Group | Documents and role |
| --- | --- |
| Creative initiative | [Core principle](designs/couldhappen.md#creative-initiative) and [optional practice examples](designs/creative-practice-examples.md). Examples are possibilities, not required systems. |
| Visual provenance | [Direction record](designs/impeccable_direction_notes.md), [design sitemap](designs/SITEMAP.md), and the [selected Woven reference](designs/woven/woven.png). |
| Research | [Browser handoff](research/browser_handoff_research.md), [host capabilities](research/host_compatibility_notes.md), [accepted carry-over](research/carryover_audit.md), and [portrait findings](research/prior_imagery_findings.md). Source inspection, not observed operation. |
| Reviews | [Concept-review synthesis](reviews/goldfish_review_report.md), the [packaging review](reviews/2026-11-05_packaging-goldfish-review.md) and its [resolution](reviews/2026-11-05_packaging-resolution.md), and the [review index](reviews/README.md). |
| History | [docs/history/](history/README.md): planning notes, the original implementation handoff, the design's alternatives and implementation plan, the progress log, and archives. Not current instructions. |

Release copies of Markdown files are these files with their `dev-only` blocks removed; see [Building a release](setup.md#building-a-release). Captured upstream sources (`.research/`), original review inputs (`goldfish_reviews/`), and visual artifacts (`.impeccable/`) are evidence, not operating instructions.
<!-- /dev-only -->
