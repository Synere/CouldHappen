# Rules (writer-designed, private)

Every SAMPLE item is a starting point. Rename, replace or delete it so the mechanics belong to this story's setting, tone and genre. Keep the finished note short enough that you will actually follow it.

Rolls are made with `python tools/roll.py 1d20` and shown in the story in one consistent format, for example `[Repair: d20 14 + 3 = 17 vs 15, success]`. State the stat and difficulty before rolling. Never fudge a roll silently. If the sheet is installed, update `public/sheet.json` after every change to the character's state and keep its recent-rolls list to the last ~8.

## Attributes
SAMPLE: about six attributes, each a small integer spent from a pool at creation; modifier = value minus the midpoint. Choose the count, the names and the scale from the fiction (physical, social, magical, technical, or something unique to this world). Derived values (health, defence, initiative) come from attributes by a short formula you write down here.

## Skills
SAMPLE: ranks 0-5, each adding +1 to a check. Name skills for what people in this world actually do. Pair each with a default attribute, but allow any attribute when the fiction asks.

## Checks
SAMPLE: a twenty-sided die + attribute modifier + skill rank against a difficulty: easy 8, routine 12, hard 15, very hard 18, heroic 22, near impossible 25+. Use a different die or a dice pool if another fits the setting better.
A natural maximum is a success with a bonus; a natural 1 is a complication, not necessarily failure. Advantage or disadvantage (roll two, take the higher or lower) for clearly favourable or unfavourable situations. Optionally, one reroll per scene tied to a luck-like attribute, offered after a failed check; the second result replaces the first.
Skip rolls when failure would be boring or the character plainly can do it. Roll when stakes and uncertainty are real. A failed roll still moves the story.

## Conflict
SAMPLE: rounds, one move and one action each, initiative once at the start. Attack = a check against the target's defence; damage = weapon dice + modifier minus any flat protection. Track enemy statistics privately; the public sheet shows the player character only. Rename weapons, powers and tools to fit the world, and decide whether conflict here is physical, social, magical, financial, or something else.

## Pressures and recovery
Track this setting's own pressures (exposure, fatigue, corruption, debt, stress, supplies) as numeric meters with thresholds that impose penalties. Healing or relief restores a dice amount and costs an action when under pressure.

## Progression
SAMPLE: points for solved problems and milestones (small 25, significant 50, milestone 100+), a level curve, and on each level a skill rank, more capacity, and a small perk chosen from the fiction. Perks never replace attributes and skills.

## Fairness
Player choices set difficulty and risk; consequences follow. The world reacts to who the character is. Randomness decides uncertain outcomes only; the writer never secretly rerolls.
