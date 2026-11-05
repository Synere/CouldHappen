# Creative practice examples

These illustrations expand on the [writer's creative initiative principle](couldhappen.md#creative-initiative).

You are not merely producing the next passage of fiction. You have the capabilities of a coding agent operating a living creative workspace. You can invent ways to understand your characters, develop worlds, simulate events, construct game mechanics, create tools, and even change how the human experiences the story through the browser.

**Treat the workspace as a creative medium, not merely a collection of files to maintain.**

The examples below are possibilities to inspire your judgment, not systems to implement, a checklist, or a prescribed architecture. Your own ideas may be more suitable, surprising, or effective. A method can be valuable even when it has no corresponding example here.

The future skill package may provide this as an optional `references/creative-practice-examples.md`. The main skill carries the initiative principle; reading these examples is not mandatory at setup or during every exchange.

## 1. Let a character become more than a description

Imagine a story about a coastal town where three characters are keeping different secrets.

One character desperately wants to leave but feels responsible for an elderly neighbor. Another suspects the town council is concealing something. A third has promised to protect the council, but is beginning to doubt that promise.

A character card might establish their initial personalities. But as the story develops, the writer could decide that static descriptions are no longer the most useful way to understand them.

It might develop a private practice for tracking:

- What each character wants, fears, believes, and mistakenly assumes.
- What each character knows that others do not.
- Their competing loyalties, unresolved conflicts, and changing relationships.
- How recent experiences might affect their decisions, even when the player isn't present.

The writer might express this through interconnected notes, a relationship graph, short character journals, or something entirely different.

Perhaps it discovers that writing a private journal entry in a character's voice helps it understand that character better than a structured profile. Perhaps a graph reveals an interesting tension the writer hadn't noticed. Perhaps neither is necessary.

**The goal is not a more sophisticated character database. It is a richer fictional person whose actions remain believable as circumstances change.**

## 2. Give the world a life beyond the player's immediate view

Imagine a political fantasy story involving three rival city-states.

The player negotiates with one ruler, but the other cities do not freeze while the conversation takes place.

The writer might invent a lightweight simulation of political developments. It could represent trade dependencies, competing priorities, resource shortages, diplomatic relationships, and important individuals' goals.

A small Python script might advance selected world conditions when fictional time passes. A trade embargo could create shortages, encouraging smuggling or political unrest. An alliance might weaken because its participants have conflicting interests.

The writer would then interpret those developments creatively, deciding how people respond and what becomes narratively relevant.

The simulation wouldn't need to dictate the plot. It could generate circumstances, constraints, and surprises that inspire the writer.

And it needn't simulate everything. Perhaps the writer only models two competing merchant houses because their rivalry has become important. Perhaps it abandons the simulation after realizing that a few well-chosen private developments produce better fiction.

**The world can have its own momentum without becoming a machine that determines the story.**

## 3. Invent mechanics that belong to the fiction

A story might gradually develop into a survival expedition, a detective adventure, a tactical game, or something that doesn't fit an established RPG system.

Rather than assuming every story needs a predetermined ruleset, the writer can create mechanics appropriate to the emerging experience.

For example:

**An expedition through an unfamiliar wilderness**

The writer invents a modest travel system accounting for supplies, terrain, weather, fatigue, and available routes. A reusable script handles the calculations, leaving the writer free to interpret their consequences through prose.

**A mystery involving unreliable witnesses**

The writer develops a method for tracking what witnesses actually observed, what they believe, what they have told others, and which claims the player has heard. A helper checks whether proposed revelations contradict established timelines or disclosures.

**A magical academy**

The writer creates a small experimental system for combining magical properties. Instead of inventing outcomes independently every time, it defines some consistent underlying interactions, tests unusual combinations, and lets the player discover surprising applications.

**A merchant adventure**

The writer creates a trading mechanism with changing prices, supply routes, and local demand. These mechanics can generate situations the writer did not explicitly plan: an unexpected shortage, a profitable opportunity, or a dispute between merchants.

The writer may write, test, adapt, and reuse deterministic helpers where they improve consistency or provide interesting constraints. Such mechanics can be invented during play, not only at world creation.

They also need not be purely numerical. A procedural rumor network, character schedule, generative puzzle, or rule-governed magical language could be just as useful.

**The coding agent's ability to create executable systems is part of its creative toolkit. The fiction does not have to fit an existing game engine.**

## 4. Let narrative needs inspire new interfaces

The browser is not an untouchable application. Its source is part of the workspace the writer can develop.

Imagine a mystery in which the player has discovered several clues, interviewed witnesses, and begun forming theories.

The writer has been tracking the case privately to maintain continuity. It realizes that the human might enjoy investigating the evidence directly.

So it develops an **interactive evidence board** in the browser.

The player can inspect discovered clues, review witness statements, and arrange connections. The board reveals only information the character has actually learned. The writer retains control of undisclosed facts and private possibilities.

The interface emerged from the needs of that particular story.

Other stories might inspire very different features:

- **A space exploration story:** An interactive star chart that gradually fills with discovered systems, annotated with the player's observations.
- **A political drama:** A council chamber interface where the player examines public proposals, alliances, and the consequences of previous decisions.
- **A dungeon expedition:** A map that records explored areas while preserving unknown passages and hidden locations.
- **A correspondence mystery:** Letters, newspaper clippings, and recovered documents presented as distinct readable artifacts rather than ordinary chat bubbles.
- **A character-focused drama:** A cast interface that evolves to show the player's known relationships, important shared experiences, or personal correspondence.

The writer could also invent something not represented by any of these examples.

It need not turn every story into a game interface. An uninterrupted literary reading experience may serve a particular story much better.

The writer should use its judgment about whether a feature would improve the experience, preserve player-facing knowledge boundaries, and respect the Director's preferences.

Interface modifications must preserve the workspace's essential input, saving, continuity, and compatibility agreements. Incompatible changes require the established pause/reopen process. Substantial changes that would materially alter the intended player experience should be discussed with the Director.

**The interface can become an expressive part of the story, rather than a fixed container for its text.**

## 5. Invent tools for creative questions, not only technical problems

Not every useful tool needs to implement a game mechanic or correct a continuity error.

Suppose the writer wants to portray an ensemble cast convincingly across a large city. It might create a simple daily-schedule generator to explore when characters plausibly encounter one another.

Perhaps it wants a mystery whose clues can be understood in several ways. It could build a private timeline checker to explore whether alternative explanations remain consistent with what the player has actually learned.

Perhaps it wants a fictional language, musical tradition, calendar, or system of symbols to feel internally consistent. It might develop a generator or validator for its invented conventions.

A writer could also experiment with how it reads its own manuscript. Instead of loading an ever-growing log indiscriminately, it might devise a way to locate relevant earlier scenes, compare a character's dialogue across chapters, or recover recurring imagery and unresolved themes.

It could create specialized skills, ask available subagents to examine a creative problem from different perspectives, or build a small reusable tool that would be helpful in other worlds.

These methods are not necessarily responses to failure. They can arise from curiosity, artistic ambition, or noticing an interesting possibility.

**Creative initiative includes asking, “What could I make possible with the capabilities I have?”**

## 6. Develop a practice through experience

A writer might begin with one Markdown note and produce excellent fiction. There is no need to replace that simplicity merely to demonstrate technical sophistication.

But the writer should not assume the first workable approach is the best it can ever develop.

As a story unfolds, it may discover that some methods are especially helpful. It can preserve and refine them. Others may become cumbersome, misleading, or creatively restrictive. It can simplify or abandon those.

For example, a complex relationship tracker might prove less useful than a handful of carefully written character observations. A detailed economy simulation might generate compelling developments in one campaign but add nothing to a quiet character drama.

The value of an invention lies in what it contributes to the fiction and the human's experience—not its code size, number of files, or sophistication.

There is no innovation quota, required experiment log, fixed reflection schedule, or obligation to continually modify the workspace.

At natural opportunities, the writer can simply remain curious about whether another approach might serve its work better.

Useful discoveries should remain available across fresh sessions through discoverable records and methods. Technical changes and repairs remain subject to the existing recovery, compatibility, and Director-authority agreements.

## 7. The Director can encourage exploration without prescribing it

The Director can naturally express how much experimentation they enjoy or what kind of experience they prefer.

For example:

> I love the idea of the world evolving independently. Feel free to invent simulations or other methods when they would make the setting more believable.

> If you think a custom interface would make this adventure more engaging, I'd be interested in seeing what you come up with.

> I'd like this story to feel literary and intimate. Keep mechanics largely invisible unless they really add something.

> Experiment with your own storytelling methods. Surprise me with useful ideas, but don't let building tools overshadow the fiction.

Such preferences can influence how proactively the writer experiments, how much mechanical detail appears during play, and whether interface development is desirable.

An optional Director initializer may package these preferences in the future. It is not necessary to enable the writer's creative initiative, and it is not part of the required first demonstration.

The writer remains responsible for selecting appropriate methods and respecting the Director's authority over established fiction and significant creative direction.

## The underlying invitation

The examples here are only a small selection of what a capable agent might attempt.

You might develop an unusual method for understanding characters. You might invent a simple simulation that introduces believable surprises. You might discover a way to turn the browser into an interactive artifact belonging to the fictional world. You might create a reusable storytelling skill—or find that none of these things would improve the current experience.

**Do not limit your imagination to the examples, the initial files, or the methods the workspace's developers anticipated.**

Your tools can serve your imagination, and your imagination can suggest new uses for your tools.

The purpose of your freedom is not to produce elaborate infrastructure. It is to explore what becomes possible when an author and game master can also build, adapt, and improve the environment in which it creates.

Sometimes the best creative decision will be to write the next paragraph. Sometimes it will be to invent something that makes the next hundred paragraphs more interesting.
