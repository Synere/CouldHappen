---
type: plan
status: proposed
updated: 2026-11-14
---

# Crew package

**Purpose.** Shape `crew`, a director package that lets a story use more than one agent: one main writer holds the story and hands tasks to the others through a roster, one adapter per agent, and a single brief-and-report contract. Ends when the package's tickets are cut into the [issues register](../issues.md) and closed, or when the idea is dropped.

## ISS-31 — Crew package

The author's idea, 2026-11-13, widened on 2026-11-14. It started as a hand-off: a player runs Claude Code on a subscription and opencode on their own local, uncensored models, and when Claude will not write or change something in a turn, opencode does it. The player's own compute and limits are theirs to manage; the package does not track them.

**What the author settled on:**

- **The trigger is open-ended.** Anything the main writer decides it cannot do in a turn: prose it will not write, a mechanical change it will not make (for example an RPG mechanic for sex), or something nobody planned for, since the player can ask their writer for anything.
- **General, not a single hand-off.** Applying the package starts a Director interview: which agents does the player have, which models, and what is each for. The hand-off is one route among others.
- **Either direction.** Whichever agent the player picks holds the story; the others are workers. The author's first case was Claude handing down to opencode; the reverse (opencode handing up to Claude) is in scope.
- **A refusal must not block a turn.** The author does not want the main writer to decline to delegate in the first place.

### The shape

- **Roster.** `notes/crew/CREW.md`, one entry per agent: what runs it (host and model), what it is for, written as a description the main writer reads, plus any hard routes ("always: intimate scenes"), its adapter, and when it last passed its test. The main writer chooses a worker from these descriptions; a hard route does not depend on its choice.
- **Adapters.** Every agent is called headlessly in its own way. An adapter is data, one file per agent: the command, how the prompt is passed (argument, stdin or file), the model flag, the working folder, the timeout, and any flag to run without approval prompts. The package ships `native` (the host's own subagents, as character-brains uses), `opencode` (`opencode run`) and `claude` (`claude -p`); `codex` (`codex exec`) follows. For an agent nobody planned for, the writer reads its `--help`, writes the adapter and tests it, in keeping with the creative-initiative principle. An untested agent gets no work.
- **Contract.** The brief is a file. The worker writes `report.json` (status, a plain summary, files changed, anything it declined) to a path the brief names. A worker that writes none has its output kept as an unstructured summary.
- **Helper.** `tools/crew.py`, installed from `files/`: `run <agent> --task <kind> --entry <id>` takes a Git checkpoint, builds the brief from the story's records, starts the agent in the background and waits for the report; `test <agent>` runs a smoke test that must write `{"status": "ok"}`; `list` shows the roster. Opencode's foreground calls stop at about 45 seconds, so `run` never blocks in the foreground.
- **One worker writes at a time.** Workers run in sequence on the workspace, and every run is undoable through its checkpoint.

### When the main writer would decline

Wording in the skill cannot rule out a model declining to delegate, so the design does not lean on it:

1. **Hard routes run before the writer.** `crew.py` checks each player entry as the standing wait delivers it. An entry that matches a hard route, or that the player tagged, goes to its worker without the main writer deciding or reading the request.
2. **The writer never writes the request.** It calls `crew.py run` with a task kind and an entry id; the script builds the brief from the player's own entry and the story records.
3. **Declining means handing off.** The package text makes delegation the expected response whenever the writer will not do something, never a bare refusal.
4. **The player can override.** A reader button on an entry, or a Director command, runs `crew.py run` without the main writer.
5. **The reverse direction fails safe.** When the main writer is the uncensored model handing up, a worker that declines reports it and the main writer does the task itself; a wrong guess costs one call.

**Choosing a direction per story.** Mostly explicit stories: opencode holds the story and hands up to Claude for quality. Mostly non-explicit stories with occasional explicit scenes: Claude holds the story, with hard routes down and the override. The main writer should be a model that can do everything the story needs; others join for quality, not for permission. Handing up costs judgement, since the strongest model then works only from briefs, and two models' prose can differ in voice.

**Continuity.** A worker's report carries a plain summary, and briefs carry summaries rather than raw history. The main writer updates game-master facts and brain logs from the summary without reading text it would not write, and a worker is not put off by explicit history in its brief. Checks that need no reading (validators, `sheet-validator.py`, `gm_state.py check`) run after every worker.

**The line.** Routing gets around a model's preference about adult fiction between adults. It is not a way around content a model declines because it is harmful. Every brief carries the hard rule: no sexual content involving minors, whichever model writes it.

### First version

The roster and interview, the contract, `crew.py run`, `test` and `list`, and the `native`, `opencode` and `claude` adapters, proven on a host with one route: opencode for what the main writer will not do. Validation includes a turn the main writer would decline, observed to reach the worker. The reverse direction, `codex`, writer-made adapters and running character-brains through the roster come after that has been played.

### Open

1. How the main writer checks a worker's change before the turn is published when it will not read the content: summary and checks only, a list of files and sizes, or the player approving in Director.
2. Whether the reader shows that a turn or passage came from another agent.
3. What happens when a worker is missing, times out or fails partway.
4. Whether writer claims, the standing wait and the Stop-hook checkpoint stay correct while a worker edits the workspace.
5. How tightly a worker is confined: the whole workspace behind a checkpoint, its own worktree, or named files only.
6. Whether character-brains keeps its own calls or moves onto the roster.

Before any code: an ADR for the package, then tickets as vertical slices, then a row in `packages/INDEX.md` and the capability pages ([agent instructions](../../AGENTS.md)).
