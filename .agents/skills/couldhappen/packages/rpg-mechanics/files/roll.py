"""Fair dice for the writer. Usage: python tools/roll.py 1d20 [1d6+2 ...]
Prints one JSON object per expression: {"expr", "dice", "total"}.
Uses the operating system's random source; there is no seed to fudge."""
import json
import random
import re
import sys

rng = random.SystemRandom()
for expr in sys.argv[1:]:
    m = re.fullmatch(r'(\d+)d(\d+)([+-]\d+)?', expr)
    if not m or not 1 <= int(m[1]) <= 100 or not 2 <= int(m[2]) <= 1000:
        sys.exit(f'bad dice: {expr}')
    count, sides, bonus = int(m[1]), int(m[2]), int(m[3] or 0)
    dice = [rng.randint(1, sides) for _ in range(count)]
    print(json.dumps({'expr': expr, 'dice': dice, 'total': sum(dice) + bonus}))
