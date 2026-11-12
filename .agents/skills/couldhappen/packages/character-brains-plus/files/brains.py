"""Character brains plus: each character's brief is built only from what that character could know.

Usage (from the workspace root):  python tools/brains.py <command> [--root .]
  init                                 create notes/brains/events.jsonl (safe to repeat)
  add <npc> [--name N] [--age N] [--look T] [--alias A ...] [--threads T ...] [--baseline FIELD=N ...]
                                       record a character's identity and snapshot their game-master card;
                                       --baseline is the affect they settle back to (valence, energy, ...)
  world <fact> --visibility public|witnessed|private|secret [--witnesses N ...]
                                       classify a game-master fact for the brains
  world --audit                        list game-master facts no brain classification covers yet
  know <npc> <fact> --how "I ..." --confidence certain|probable|suspects|doubts --entry E
                                       the character learned a fact, and how (first person)
  unlearn <npc> <fact> --entry E --why W   the character no longer holds a fact
  remember <npc> --text T [--salience 1-5] --entry E   an episode the character keeps
  compress <npc> --replace SEQ ... --text T [--salience 1-5]   fold episodes into one summary
  session <npc> (--id ID | --end) [--tier persistent|ephemeral]   the kept subagent session
  state <npc> [--set PATH=VALUE ...] --entry E   body, mood, desire, routine (affect.fear=3, body.clothes=...,
                                       desire.limits=..., routine.<slot>=...; an empty value clears); without --set, print it.
                                       Edges to others: people.<cast id|player>.trust|attraction|fear (0-5),
                                       .debt (-5 to 5), .last, .thinks_knows.<fact>=knows|doesnt|unsure
  believe <npc> --text T --truth true|false|unknown --confidence C [--about FACT] [--retire SEQ] --entry E
  believe <npc> --retire SEQ --entry E  what the character believes, true or not (at most 12 held)
  claim <npc> --to player|<npc> --text T --truth true|false|unknown --kind K [--about FACT] --entry E
                                       what they told someone: lie, truth, half-truth, promise, threat, boast, omission
  tick <npc> [--scene-end] --entry E   time passes: each affect level one step toward baseline
                                       (pain and intoxication only with --scene-end)
  want <npc> --text T [--weight 1-5] [--conflict T] [--retire SEQ] --entry E
                                       a standing want (at most 3); --retire SEQ alone drops one
  intent <npc> --text T --horizon now|scene|day|long [--done SEQ | --drop SEQ] --entry E
                                       what they mean to do (at most 3 active); --done/--drop SEQ alone closes one
  veto <npc> --kind leave|refuse|later|other --reason T [--decides T] [--intent SEQ] --entry E
                                       a DECIDES the writer could not honour, and why
  offscreen <npc> --does T [--salience 1-5] --entry E   what the off-screen call said they did (one per boundary)
  settings [--offscreen on|off]        story settings; off-screen calls are off by default
  brief <npc> --scene FILE [--as ALIAS] [--text]   the only way to build a brain's brief
  brief <npc> --offscreen [--scene FILE] [--text]  the off-screen brief at a scene boundary, with their routine
  view [<npc>]                         rewrite the generated views and print one
  check                                validate the log against game-master
  migrate [--entry E]                  move method-only brain files into the log (originals kept in notes/brains/legacy/)
  reconcile [--apply]                  after a Director Undo: set aside events whose entry is gone, and what
                                       depends on them, into notes/brains/withdrawn.jsonl (dry run without --apply)

Every command prints one JSON object. Exit 0 ok, 1 warning, 2 error.

The log notes/brains/events.jsonl is append-only and the only source of truth. Each line is one event:
{"seq", "at", "npc", "op", "entry", "why", "data"}. notes/brains/<npc>.md are generated views.
Game-master state is read by replaying notes/gm/deltas.jsonl through tools/gm_state.py, never copied.
The game-master "known" flag (what the player has seen) is never read here: what a brain may know is
decided only by world classifications and know/unlearn events. Stdlib only; no network.

Extending: a new event op needs a validator in VALIDATE (checks it against the current state before
it is appended) and a folder in FOLD (applies it on replay). A new brief section is a function added
to BRIEF_SECTIONS. A new state field is an entry in STATE_SCHEMA; a per-person or per-item group is a
('keyed', {field: spec}) entry, like body.marks."""
import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VISIBILITY = ('public', 'witnessed', 'private', 'secret')
CONFIDENCE = ('certain', 'probable', 'suspects', 'doubts')
TIERS = ('persistent', 'ephemeral')
CARD_FIELDS = ('want', 'fear', 'secret', 'attitude', 'voice')
TERMINAL_FACT = ('outdated', 'discarded')
SETUP_OPS = ('char', 'world', 'session', 'compress', 'settings')  # the only ops whose entry may be null
MAX_TEXT, MAX_LIST, MAX_EPISODES = 300, 20, 6
SALIENCE = range(1, 6)
GENERATED = '<!-- generated from events.jsonl; do not edit -->'
NOT_BRAINS = ('PROTOCOL.md', 'TEMPLATE.md', 'SCENE.md')  # files in notes/brains/ that are not views
MIGRATED = 'migrated'  # the how of a know event moved from a method-only "## Knows" line (ISS-25)
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
UUID_RE = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'd|I'll|me|my|mine|myself|we|us|our)\b")
PATH_RE = re.compile(r'(?:\b(?:notes|public|tools|imports)/)|(?:\.(?:jsonl|json|py|md)\b)')
AUTO_ID = re.compile(r'\b[A-Z]\d+\b')  # the shape of game-master auto ids: F12, T3, P2, V1
FACT_ID = re.compile(r'\bF\d+\b')
ANSWER_KEYS = ('NOTICES', 'WANTS', 'HIDES', 'SAYS', 'DOES', 'TELL', 'BODY', 'UNSURE', 'REMEMBERS', 'DECIDES')
ANSWER_HELP = {
    'NOTICES': 'the one thing they notice first',
    'WANTS': 'what they want in this moment',
    'HIDES': 'what they will not show',
    'SAYS': 'one to three short lines, in their voice, as they would actually say them, or (nothing)',
    'DOES': 'one physical action',
    'TELL': 'one involuntary detail a careful observer would catch',
    'BODY': 'what their body feels or does that they notice (pain, tiredness, heat, hunger), or (nothing)',
    'UNSURE': 'what they do not know here and would want to, or (nothing)',
    'REMEMBERS': 'one thing from this moment they will keep, in their own words, or (nothing)',
    'DECIDES': 'a lasting intention they form now (to leave, to refuse, to do something later), or (nothing)'}
CONFIDENCE_WORDS = {'certain': '', 'probable': 'probably', 'suspects': 'you suspect this',
                    'doubts': 'you doubt this'}

# ---- body, mood and desire (ISS-26) ----
# A spec is ('text',), ('level', low, high), ('seen',) (who can see a mark), a dict of named fields, or
# ('keyed', spec): items under any id, each with that spec. State paths are dotted: affect.fear, body.marks.burn.
# A ('choice', values) leaf is one of those words. A keyed group may name what its keys must be as a third
# element, checked against the brain's state when a value is set: 'person' (a cast id, or player, never the
# character themself) and 'fact' (a game-master fact the character holds, so they know it exists).
TEXT, LEVEL = ('text',), ('level', 0, 5)
THINKS = ('knows', 'doesnt', 'unsure')
STATE_SCHEMA = {
    'affect': {'mood': TEXT, 'valence': ('level', -3, 3), 'energy': LEVEL, 'pain': LEVEL, 'fear': LEVEL,
               'shame': LEVEL, 'arousal': LEVEL, 'intoxication': LEVEL},
    'body': {'condition': TEXT, 'marks': ('keyed', {'text': TEXT, 'seen_by': ('seen',)}), 'clothes': TEXT,
             'carrying': TEXT, 'capacities': TEXT},
    'desire': {'orientation': TEXT, 'appetite': TEXT, 'wants': TEXT, 'limits': TEXT, 'never_admits': TEXT,
               'shame': TEXT, 'aftercare': TEXT, 'turn_offs': TEXT, 'current': TEXT},
    # ISS-27: what the character makes of each other person. debt above 0 is owed to the character, below 0
    # is what they owe. thinks_knows is what they think that person knows, by fact id.
    'people': ('keyed', {'trust': LEVEL, 'attraction': LEVEL, 'fear': LEVEL, 'debt': ('level', -5, 5),
                         'last': TEXT, 'thinks_knows': ('keyed', ('choice', THINKS), 'fact')}, 'person'),
    # ISS-28: where they are and what they do when the story is elsewhere, by a short slot id
    # (routine.mornings="opens the chandlery"). Only the off-screen brief prints it.
    'routine': ('keyed', TEXT)}
AFFECT_LEVELS = tuple(k for k, spec in STATE_SCHEMA['affect'].items() if spec[0] == 'level')
DEFAULT_BASELINE = {'energy': 3}  # every other affect level settles to 0
BOUNDARY_ONLY = ('pain', 'intoxication')  # these ease only at a scene boundary (tick --scene-end)
LEVEL_WORDS = ('none', 'a little', 'some', 'a lot', 'badly', 'overwhelming')
VALENCE_WORDS = {-3: 'wretched', -2: 'low', -1: 'a little low', 0: 'even', 1: 'a little lifted', 2: 'good',
                 3: 'elated'}
SEEN = {'anyone': 'anyone can see it', 'close': 'only someone close can see it', 'nobody': 'hidden'}
STATE_LABELS = {
    'affect.mood': 'mood', 'body.condition': 'condition', 'body.clothes': 'wearing',
    'body.carrying': 'carrying', 'body.capacities': 'capacities', 'desire.orientation': 'orientation',
    'desire.appetite': 'appetite', 'desire.wants': 'wants', 'desire.limits': 'limits (never crossed, whatever happens)',
    'desire.never_admits': 'would never admit', 'desire.shame': 'ashamed of wanting', 'desire.aftercare': 'after, needs',
    'desire.turn_offs': 'turned off by', 'desire.current': 'right now'}

# ---- beliefs, claims and other minds (ISS-27) ----
TRUTH = ('true', 'false', 'unknown')  # recorded for the writer; the brief never prints it
CLAIM_KINDS = ('lie', 'truth', 'half-truth', 'promise', 'threat', 'boast', 'omission')
KIND_WORDS = {'lie': 'a lie', 'truth': 'the truth', 'half-truth': 'a half-truth', 'promise': 'a promise',
              'threat': 'a threat', 'boast': 'a boast', 'omission': 'kept back'}
KIND_TRUTH = {'lie': 'false', 'truth': 'true'}  # the two kinds whose truth label follows from the kind
PLAYER = 'player'
MAX_BELIEFS, MAX_CLAIMS, MAX_THINKS = 12, 6, 4
MAX_PEOPLE, MAX_PROPOSITIONS = 3, 2  # in the brief: people, and what each is thought to know
THINKS_WORDS = {'knows': 'you think they know', 'doesnt': 'you think they do not know',
                'unsure': 'you are not sure they know'}
THINKS_ORDER = {'doesnt': 0, 'unsure': 1, 'knows': 2}  # what the brief shows first: what they think is safe
EDGE_LABELS = {'trust': 'trust', 'attraction': 'attraction', 'fear': 'fear of them'}
EDGE_WORDS = ('none', 'a little', 'some', 'a lot', 'deeply', 'utterly')  # 0 to 5, as LEVEL_WORDS for affect
DEBT_WORDS = ('nothing', 'a little', 'something', 'a lot', 'a great deal', 'everything')

# ---- agency and life off-screen (ISS-28) ----
# want, intent, veto and offscreen events carry data.scene, game-master's scene_count when they were recorded,
# so drift review (ISS-29) can count vetoes per ten scenes and find intents gone stale.
HORIZONS = ('now', 'scene', 'day', 'long')
HORIZON_WORDS = {'now': 'right now', 'scene': 'before this scene is over', 'day': 'within a day or so',
                 'long': 'in the long run'}
WEIGHTS = range(1, 6)  # how much a standing want matters; ranks wants, never printed
MAX_WANTS, MAX_INTENTS, BRIEF_WANTS, MAX_ROUTINE = 3, 3, 2, 6
INTENT_OUTCOMES = ('done', 'dropped')  # a veto closes an intent as 'vetoed'
VETO_KINDS = ('leave', 'refuse', 'later', 'other')  # what the DECIDES the writer could not honour named
OFFSCREEN_ANSWER_KEYS = ('DOES', 'LEAVES', 'DECIDES', 'CHANGES')
OFFSCREEN_ANSWER_HELP = {
    'DOES': 'what they do with the time, in one or two plain lines',
    'LEAVES': 'the sign of it someone could find later (a note, a smell, a missing thing, a rumour), or (nothing)',
    'DECIDES': 'a lasting intention they form (to leave, to refuse, to do something later), or (nothing)',
    'CHANGES': 'how they are different after it (mood, body, what they want), or (nothing)'}
SETTINGS = {'offscreen': False}  # off-screen calls are off until the Director turns them on at apply


class Fail(Exception):
    """An error that ends the command with exit 2."""


# ---- game-master, by replay ------------------------------------------------------------------

def gm_module(root):
    """tools/gm_state.py in the workspace; beside this script; or, in the development repo, the package copy."""
    here = Path(__file__).resolve().parent
    for path in (Path(root) / 'tools' / 'gm_state.py', here / 'gm_state.py',
                 here.parent.parent / 'game-master' / 'files' / 'gm_state.py'):
        if path.is_file():
            spec = importlib.util.spec_from_file_location('gm_state', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise Fail('game-master is not installed (no tools/gm_state.py). Apply the game-master package first.')


def gm_load(gm, root):
    """Game-master state, replayed from notes/gm/deltas.jsonl by gm_state.py itself."""
    if not gm.paths(root)[1].exists():
        raise Fail('notes/gm/deltas.jsonl is missing. Run: python tools/gm_state.py init')
    try:
        state = gm.load(root)
    except SystemExit as exc:
        raise Fail(f'game-master state does not load: {exc}')
    if not {1, 3}.issubset(state['layers']):
        raise Fail('character brains need game-master layer 3 (cast cards). '
                   'Run: python tools/gm_state.py layers --on 2 3 4')
    return state


def gm_seq(gm, root):
    return max((d.get('seq') or 0 for d in gm.read_lines(gm.paths(root)[1])), default=0)


# ---- the log ---------------------------------------------------------------------------------

def brains_dir(root):
    return Path(root) / 'notes' / 'brains'


def events_path(root):
    return brains_dir(root) / 'events.jsonl'


def withdrawn_path(root):
    return brains_dir(root) / 'withdrawn.jsonl'


def method_only_files(root):
    """Brain files from the method-only package: hand-written, with an "npc:" line and no generated header."""
    out = []
    for path in sorted(brains_dir(root).glob('*.md')):
        if path.name in NOT_BRAINS:
            continue
        text = path.read_text(encoding='utf-8')
        if not text.startswith(GENERATED) and re.search(r'^npc: ', text, re.M):
            out.append(path.name)
    return out


def new_state():
    # touched: npc -> person -> the seq of the last state event about them, to rank people in the brief
    # wants and intents: npc -> seq -> the active one; closed: npc -> intents completed, dropped or vetoed
    return {'chars': {}, 'world': {}, 'knows': {}, 'unlearned': {}, 'episodes': {}, 'states': {},
            'beliefs': {}, 'claims': {}, 'touched': {}, 'wants': {}, 'intents': {}, 'closed': {}, 'vetoes': {},
            'offscreen': {}, 'settings': dict(SETTINGS)}


def text_ok(value):
    return isinstance(value, str) and 0 < len(value.strip()) and len(value) <= MAX_TEXT


def need_char(state, npc):
    if npc not in state['chars']:
        raise Fail(f'{npc} has no brain yet. Run: python tools/brains.py add {npc}')


def need_fact(gm_state, fid, live=True):
    fact = gm_state['facts'].get(fid)
    if not fact:
        raise Fail(f'{fid} is not a game-master fact')
    if live and fact['status'] in TERMINAL_FACT:
        raise Fail(f'{fid} is {fact["status"]}: a brain cannot learn it')
    return fact


def allowed_facts(state, gm_state, npc):
    """Fact id -> how the character holds it, in game-master order. The game-master "known" flag is never read."""
    out = {}
    knows, gone = state['knows'].get(npc, {}), state['unlearned'].get(npc, set())
    for fid, fact in gm_state['facts'].items():
        if fact['status'] in TERMINAL_FACT or fid in gone:
            continue
        world = state['world'].get(fid)
        seen = world and (world['visibility'] == 'public' or npc in world['witnesses'])
        if fid in knows:
            out[fid] = dict(knows[fid], source='know', secret=bool(seen and world['visibility'] == 'secret'))
        elif seen:
            out[fid] = {'source': world['visibility'], 'confidence': 'certain', 'how': None,
                        'secret': world['visibility'] == 'secret'}
    return out


def live_episodes(state, npc):
    return sorted(state['episodes'].get(npc, {}).values(), key=lambda e: e['seq'])


# Validators: (state, gm_state, event) -> list of warnings; raise Fail on an error. They run before an append.

def v_char(state, gm_state, ev):
    d = ev['data']
    card = gm_state['npcs'].get(ev['npc'])
    if not card:
        raise Fail(f'{ev["npc"]} has no game-master cast card. Add one first (kind npc, op set).')
    if not text_ok(d.get('name', '')):
        raise Fail('name must be a non-empty text')
    for key in ('look',):
        if key in d and not text_ok(d[key]):
            raise Fail(f'{key} must be a text of at most {MAX_TEXT} characters')
    if 'age' in d and not (isinstance(d['age'], int) and 0 <= d['age'] < 1000):
        raise Fail('age must be a whole number')
    for key in ('aliases', 'knows_threads'):
        if len(d.get(key, [])) > MAX_LIST or not all(text_ok(a) for a in d.get(key, [])):
            raise Fail(f'{key}: at most {MAX_LIST} short texts')
    for tid in d.get('knows_threads', []):
        if tid not in gm_state['threads']:
            raise Fail(f'{tid} is not a game-master thread (is layer 2 on?)')
    for field, value in d.get('baseline', {}).items():
        if field not in AFFECT_LEVELS:
            raise Fail(f'baseline {field}: a baseline is set for ' + ', '.join(AFFECT_LEVELS))
        check_value(STATE_SCHEMA['affect'][field], value, f'baseline {field}', state, gm_state)
    return []


def v_world(state, gm_state, ev):
    d = ev['data']
    need_fact(gm_state, d['fact'], live=False)
    if d['visibility'] not in VISIBILITY:
        raise Fail('visibility must be one of ' + ', '.join(VISIBILITY))
    if d['visibility'] == 'public' and d['witnesses']:
        raise Fail('a public fact has no witnesses: every brain may know it')
    if d['visibility'] != 'public' and not d['witnesses']:
        raise Fail(f'a {d["visibility"]} fact needs --witnesses: the characters who know it')
    unknown = [w for w in d['witnesses'] if w not in state['chars'] and w not in gm_state['npcs']]
    if unknown:
        raise Fail('witnesses must be cast ids: ' + ', '.join(unknown) + ' is not')
    return []


def v_know(state, gm_state, ev):
    d = ev['data']
    need_char(state, ev['npc'])
    need_fact(gm_state, d['fact'])
    if not text_ok(d.get('how', '')):
        raise Fail('--how is required: how the character learned it, in their own words')
    if d.get('migrated') and d['how'] == MIGRATED:
        pass  # moved from a method-only file, which never said how
    elif not FIRST_PERSON.search(d['how']):
        raise Fail('--how is written in the first person, as the character would say it ("I overheard ...")')
    if d['confidence'] not in CONFIDENCE:
        raise Fail('confidence must be one of ' + ', '.join(CONFIDENCE))
    return []


def v_unlearn(state, gm_state, ev):
    need_char(state, ev['npc'])
    fid = ev['data']['fact']
    need_fact(gm_state, fid, live=False)
    if fid not in allowed_facts(state, gm_state, ev['npc']):
        raise Fail(f'{ev["npc"]} does not hold {fid}; nothing to unlearn')
    return []


def v_remember(state, gm_state, ev):
    need_char(state, ev['npc'])
    if not text_ok(ev['data'].get('text', '')):
        raise Fail(f'--text must be a non-empty text of at most {MAX_TEXT} characters')
    if ev['data']['salience'] not in SALIENCE:
        raise Fail('salience is 1 (passing) to 5 (unforgettable)')
    return []


def v_compress(state, gm_state, ev):
    v_remember(state, gm_state, ev)
    have = state['episodes'].get(ev['npc'], {})
    replace = ev['data']['replaces']
    if len(replace) < 2:
        raise Fail('compress folds two or more episodes into one: give their seq numbers with --replace')
    missing = [str(s) for s in replace if s not in have]
    if missing:
        raise Fail(f'not live episodes of {ev["npc"]}: seq ' + ', '.join(missing) + ' (see python tools/brains.py view)')
    return []


def v_session(state, gm_state, ev):
    need_char(state, ev['npc'])
    d = ev['data']
    if d['session'] is not None and not text_ok(d['session']):
        raise Fail('--id must be a short text')
    if d.get('tier') is not None and d['tier'] not in TIERS:
        raise Fail('tier must be persistent or ephemeral')
    return []


def state_spec(path):
    """(parts, spec) for a dotted state path, or Fail naming what the path may hold."""
    parts, spec = path.split('.'), STATE_SCHEMA
    for i, part in enumerate(parts):
        if isinstance(spec, dict):
            if part not in spec:
                where = '.'.join(parts[:i]) or 'state'
                raise Fail(f'{path}: {where} has no {part!r}; it holds ' + ', '.join(spec))
            spec = spec[part]
        elif spec[0] == 'keyed':
            if not ID_RE.match(part):
                raise Fail(f'{path}: {part!r} is not a short id (letters, digits, - and _)')
            spec = spec[1]
        else:
            raise Fail(f'{path}: {".".join(parts[:i])} is a single value')
    return parts, spec


def keyed_ids(path):
    """(kind, key) for each key in a valid path whose group says what its keys must be ('person', 'fact')."""
    out, spec = [], STATE_SCHEMA
    for part in path.split('.'):
        if isinstance(spec, dict):
            spec = spec[part]
        else:
            if len(spec) > 2:
                out.append((spec[2], part))
            spec = spec[1]
    return out


def check_key(kind, key, path, npc, state, gm_state):
    """Fail unless a key fits what its group holds: a person, or a fact the character knows exists."""
    if kind == 'person':
        if key == npc:
            raise Fail(f'{path}: a character\'s edges are to other people, not to themself')
        if key != PLAYER and key not in state['chars'] and key not in gm_state['npcs']:
            raise Fail(f'{path}: {key} is not cast; a person is a cast id or {PLAYER}')
    elif kind == 'fact':
        if key not in gm_state['facts']:
            raise Fail(f'{path}: {key} is not a game-master fact')
        if key not in allowed_facts(state, gm_state, npc):
            raise Fail(f'{path}: {npc} does not know {key} exists, so cannot think anything about who knows it. '
                       f'Record know first if they learned it.')


def check_value(spec, value, path, state, gm_state):
    """Fail unless value fits a leaf spec."""
    if spec == TEXT:
        if not text_ok(value):
            raise Fail(f'{path} must be a text of at most {MAX_TEXT} characters')
    elif isinstance(spec, tuple) and spec[0] == 'choice':
        if value not in spec[1]:
            raise Fail(f'{path} is one of {", ".join(spec[1])}')
    elif isinstance(spec, tuple) and spec[0] == 'level':
        if not (isinstance(value, int) and not isinstance(value, bool) and spec[1] <= value <= spec[2]):
            raise Fail(f'{path} is a whole number from {spec[1]} to {spec[2]}')
    elif spec == ('seen',):
        if isinstance(value, list):
            lost = [w for w in value if not isinstance(w, str) or (w not in state['chars'] and w not in gm_state['npcs'])]
            if not value or lost:
                raise Fail(f'{path}: cast ids, or one of {", ".join(SEEN)}'
                           + (f'; {", ".join(map(str, lost))} is not cast' if lost else ''))
        elif value not in SEEN:
            raise Fail(f'{path} is one of {", ".join(SEEN)}, or the cast ids of who can see it')
    else:
        raise Fail(f'{path} holds fields; set one of them ({path}.<field>=...)')


def v_state(state, gm_state, ev):
    need_char(state, ev['npc'])
    pairs = ev['data'].get('set')
    if not isinstance(pairs, list) or not pairs:
        raise Fail('give at least one --set PATH=VALUE')
    for pair in pairs:
        if not (isinstance(pair, list) and len(pair) == 2 and isinstance(pair[0], str)):
            raise Fail('state data is a list of [path, value] pairs')
        path, value = pair
        _, spec = state_spec(path)
        if value is not None:  # clearing needs no check: what it names may be long gone
            for kind, key in keyed_ids(path):
                check_key(kind, key, path, ev['npc'], state, gm_state)
            check_value(spec, value, path, state, gm_state)
    trial = {'states': {ev['npc']: json.loads(json.dumps(state['states'].get(ev['npc'], {})))}}
    f_state(trial, ev)
    tree = trial['states'][ev['npc']]
    marks = tree.get('body', {}).get('marks', {})
    if len(marks) > MAX_LIST:
        raise Fail(f'at most {MAX_LIST} marks')
    bare = [m for m, mark in marks.items() if 'text' not in mark]
    if bare:
        raise Fail(f'a mark needs its text first: --set body.marks.{bare[0]}="..."')
    if len(tree.get('routine', {})) > MAX_ROUTINE:
        raise Fail(f'at most {MAX_ROUTINE} routine slots; clear one with --set routine.<slot>=')
    people = tree.get('people', {})
    if len(people) > MAX_LIST:
        raise Fail(f'at most {MAX_LIST} people; clear one with --set people.<id>=')
    for pid, edge in people.items():
        if len(edge.get('thinks_knows', {})) > MAX_THINKS:
            raise Fail(f'people.{pid}.thinks_knows: at most {MAX_THINKS} facts; clear one first '
                       f'(--set people.{pid}.thinks_knows.<fact>=)')
    return []


def v_believe(state, gm_state, ev):
    need_char(state, ev['npc'])
    d, active = ev['data'], state['beliefs'].get(ev['npc'], {})
    if 'retire' not in d and 'text' not in d:
        raise Fail('give the belief (--text, --truth, --confidence), or --retire SEQ, or both to replace one')
    if 'retire' in d and d['retire'] not in active:
        raise Fail(f'seq {d["retire"]} is not an active belief of {ev["npc"]} (see python tools/brains.py view)')
    if 'text' in d:
        if not text_ok(d['text']):
            raise Fail(f'--text must be a non-empty text of at most {MAX_TEXT} characters')
        if d.get('truth') not in TRUTH:
            raise Fail('--truth is one of ' + ', '.join(TRUTH) + ': whether the belief is so (the brief never says)')
        if d.get('confidence') not in CONFIDENCE:
            raise Fail('--confidence is one of ' + ', '.join(CONFIDENCE))
        if d.get('about') is not None:
            need_fact(gm_state, d['about'], live=False)
        if len(active) - ('retire' in d) >= MAX_BELIEFS:
            raise Fail(f'{ev["npc"]} holds {MAX_BELIEFS} beliefs already, the most a brain keeps. '
                       'Retire one first, or replace it: believe ... --retire SEQ')
    return []


def contradiction(earlier, later):
    """Whether a later claim contradicts an earlier one, by a fixed rule.

    Two claims contradict when the same character told the same person something about the same game-master
    fact (--about), and one claim is labelled true and the other false. A claim with no about, or labelled
    unknown, never contradicts: the script does not read the texts."""
    return (earlier['to'] == later['to'] and earlier.get('about') is not None
            and earlier.get('about') == later.get('about')
            and {earlier['truth'], later['truth']} == {'true', 'false'})


def contradiction_warning(npc, earlier, later):
    return (f'{npc} told {later["to"]} contradicting things about {later["about"]}: seq {earlier["seq"]} '
            f'({earlier["kind"]}, {earlier["truth"]}) and seq {later["seq"]} ({later["kind"]}, {later["truth"]}). '
            f'{later["to"]} may notice.')


def v_claim(state, gm_state, ev):
    need_char(state, ev['npc'])
    d = ev['data']
    to = d.get('to')
    if to == ev['npc']:
        raise Fail('--to is someone else: a character does not make claims to themself')
    if to != PLAYER and to not in state['chars'] and to not in gm_state['npcs']:
        raise Fail(f'--to is {PLAYER} or a cast id; {to} is not cast')
    if not text_ok(d.get('text', '')):
        raise Fail(f'--text must be a non-empty text of at most {MAX_TEXT} characters')
    if d.get('kind') not in CLAIM_KINDS:
        raise Fail('--kind is one of ' + ', '.join(CLAIM_KINDS))
    if d.get('truth') not in TRUTH:
        raise Fail('--truth is one of ' + ', '.join(TRUTH))
    if d['kind'] in KIND_TRUTH and d['truth'] != KIND_TRUTH[d['kind']]:
        raise Fail(f'a {d["kind"]} is {KIND_TRUTH[d["kind"]]} by its kind; use half-truth or another kind')
    if d.get('about') is not None:
        need_fact(gm_state, d['about'], live=False)
    later = dict(d, seq=ev['seq'])
    return [contradiction_warning(ev['npc'], c, later) for c in state['claims'].get(ev['npc'], [])
            if contradiction(c, later)]


def v_tick(state, gm_state, ev):
    need_char(state, ev['npc'])
    if not isinstance(ev['data'].get('boundary'), bool):
        raise Fail('tick data needs boundary: true or false')
    return []


def need_scene(ev):
    if not (isinstance(ev['data'].get('scene'), int) and not isinstance(ev['data']['scene'], bool)):
        raise Fail(f'{ev["op"]} data needs scene: game-master\'s scene count when it was recorded')


def v_want(state, gm_state, ev):
    need_char(state, ev['npc'])
    need_scene(ev)
    d, active = ev['data'], state['wants'].get(ev['npc'], {})
    if 'retire' not in d and 'text' not in d:
        raise Fail('give the want (--text, --weight), or --retire SEQ, or both to replace one')
    if 'retire' in d and d['retire'] not in active:
        raise Fail(f'seq {d["retire"]} is not a standing want of {ev["npc"]} (see python tools/brains.py view)')
    if 'text' in d:
        if not text_ok(d['text']):
            raise Fail(f'--text must be a non-empty text of at most {MAX_TEXT} characters')
        if d.get('weight') not in WEIGHTS:
            raise Fail('--weight is 1 (a passing want) to 5 (what their life turns on)')
        if 'conflict' in d and not text_ok(d['conflict']):
            raise Fail(f'--conflict must be a text of at most {MAX_TEXT} characters')
        if len(active) - ('retire' in d) >= MAX_WANTS:
            raise Fail(f'{ev["npc"]} has {MAX_WANTS} standing wants already, the most a brain keeps. '
                       'Retire one first, or replace it: want ... --retire SEQ')
    return []


def v_intent(state, gm_state, ev):
    need_char(state, ev['npc'])
    need_scene(ev)
    d, active = ev['data'], state['intents'].get(ev['npc'], {})
    if 'close' not in d and 'text' not in d:
        raise Fail('give the intent (--text, --horizon), or --done SEQ or --drop SEQ, or both')
    if 'close' in d:
        if d['close'] not in active:
            raise Fail(f'seq {d["close"]} is not an active intent of {ev["npc"]} (see python tools/brains.py view)')
        if d.get('outcome') not in INTENT_OUTCOMES:
            raise Fail('an intent closes as ' + ' or '.join(INTENT_OUTCOMES))
    if 'text' in d:
        if not text_ok(d['text']):
            raise Fail(f'--text must be a non-empty text of at most {MAX_TEXT} characters')
        if d.get('horizon') not in HORIZONS:
            raise Fail('--horizon is one of ' + ', '.join(HORIZONS))
        if len(active) - ('close' in d) >= MAX_INTENTS:
            raise Fail(f'{ev["npc"]} has {MAX_INTENTS} active intents already. Close one first '
                       '(intent ... --done SEQ or --drop SEQ), or give it with the new --text')
    return []


def v_veto(state, gm_state, ev):
    need_char(state, ev['npc'])
    need_scene(ev)
    d = ev['data']
    if d.get('kind') not in VETO_KINDS:
        raise Fail('--kind is one of ' + ', '.join(VETO_KINDS) + ': what the decision you could not honour named')
    if not text_ok(d.get('reason', '')):
        raise Fail(f'--reason is required: why the story could not honour it (at most {MAX_TEXT} characters)')
    if 'decides' in d and not text_ok(d['decides']):
        raise Fail(f'--decides must be a text of at most {MAX_TEXT} characters')
    if 'intent' in d and d['intent'] not in state['intents'].get(ev['npc'], {}):
        raise Fail(f'seq {d["intent"]} is not an active intent of {ev["npc"]}')
    return []


def offscreen_at(state, scene):
    """The character who already had the off-screen call at this scene boundary, or None."""
    for npc in sorted(state['offscreen']):
        if any(o['scene'] == scene for o in state['offscreen'][npc]):
            return npc
    return None


def v_offscreen(state, gm_state, ev):
    need_char(state, ev['npc'])
    need_scene(ev)
    if not state['settings']['offscreen']:
        raise Fail('off-screen calls are off for this story. The Director turns them on: '
                   'python tools/brains.py settings --offscreen on')
    had = offscreen_at(state, ev['data']['scene'])
    if had:
        raise Fail(f'{had} already had the off-screen call at this scene boundary; one per boundary')
    v_remember(state, gm_state, ev)
    return []


def v_settings(state, gm_state, ev):
    d = ev['data']
    if not d or any(k not in SETTINGS or not isinstance(v, bool) for k, v in d.items()):
        raise Fail('settings: ' + ', '.join(f'{k} on|off' for k in SETTINGS))
    return []


VALIDATE = {'char': v_char, 'world': v_world, 'know': v_know, 'unlearn': v_unlearn,
            'remember': v_remember, 'compress': v_compress, 'session': v_session, 'state': v_state,
            'tick': v_tick, 'believe': v_believe, 'claim': v_claim, 'want': v_want, 'intent': v_intent,
            'veto': v_veto, 'offscreen': v_offscreen, 'settings': v_settings}


# Folders: (state, event) -> None. They apply an already-validated event on replay and never consult game-master.

def f_char(state, ev):
    char = state['chars'].setdefault(ev['npc'], {'aliases': [], 'knows_threads': [], 'session': None,
                                                 'tier': 'ephemeral'})
    char.update(ev['data'])


def f_world(state, ev):
    d = ev['data']
    state['world'][d['fact']] = {'visibility': d['visibility'], 'witnesses': list(d['witnesses']), 'seq': ev['seq']}


def f_know(state, ev):
    d = ev['data']
    state['knows'].setdefault(ev['npc'], {})[d['fact']] = {
        'how': d['how'], 'confidence': d['confidence'], 'entry': ev['entry'], 'seq': ev['seq']}
    state['unlearned'].setdefault(ev['npc'], set()).discard(d['fact'])


def f_unlearn(state, ev):
    fid = ev['data']['fact']
    state['knows'].get(ev['npc'], {}).pop(fid, None)
    state['unlearned'].setdefault(ev['npc'], set()).add(fid)


def f_remember(state, ev):
    state['episodes'].setdefault(ev['npc'], {})[ev['seq']] = {
        'seq': ev['seq'], 'text': ev['data']['text'], 'salience': ev['data']['salience'], 'entry': ev['entry']}


def f_compress(state, ev):
    eps = state['episodes'].setdefault(ev['npc'], {})
    for seq in ev['data']['replaces']:
        eps.pop(seq, None)
    f_remember(state, ev)


def f_session(state, ev):
    char = state['chars'][ev['npc']]
    char['session'] = ev['data']['session']
    if ev['data'].get('tier'):
        char['tier'] = ev['data']['tier']


def put(tree, parts, value):
    """Set a dotted path in a nested dict; None clears it, and any group left empty goes too."""
    if len(parts) == 1:
        if value is None:
            tree.pop(parts[0], None)
        else:
            tree[parts[0]] = value
        return
    child = tree.setdefault(parts[0], {})
    put(child, parts[1:], value)
    if not child:
        tree.pop(parts[0])


def f_state(state, ev):
    tree = state['states'].setdefault(ev['npc'], {})
    for path, value in ev['data']['set']:
        parts = path.split('.')
        put(tree, parts, value)
        if parts[0] == 'people' and len(parts) > 1:
            state.setdefault('touched', {}).setdefault(ev['npc'], {})[parts[1]] = ev['seq']


def current_affect(state, npc):
    """Affect level -> value: what was set, else the baseline set at add. A level never given is absent."""
    set_now = state['states'].get(npc, {}).get('affect', {})
    return {**state['chars'].get(npc, {}).get('baseline', {}),
            **{k: v for k, v in set_now.items() if k in AFFECT_LEVELS}}


def baseline_of(state, npc, field):
    return state['chars'].get(npc, {}).get('baseline', {}).get(field, DEFAULT_BASELINE.get(field, 0))


def tick_moves(state, npc, boundary):
    """Affect level -> (from, to): one step toward baseline; pain and intoxication only at a boundary."""
    moves = {}
    affect = current_affect(state, npc)
    for field in AFFECT_LEVELS:
        if field not in affect:
            continue
        value, target = affect[field], baseline_of(state, npc, field)
        if value != target and (boundary or field not in BOUNDARY_ONLY):
            moves[field] = (value, value + (1 if target > value else -1))
    return moves


def f_tick(state, ev):
    """Recomputed on replay, so after a reconcile a tick eases what is left, not what was set aside."""
    moves = tick_moves(state, ev['npc'], ev['data']['boundary'])
    tree = state['states'].setdefault(ev['npc'], {})
    for field, (_, new) in moves.items():
        put(tree, ['affect', field], new)


def f_believe(state, ev):
    d, beliefs = ev['data'], state['beliefs'].setdefault(ev['npc'], {})
    if 'retire' in d:
        beliefs.pop(d['retire'], None)
    if 'text' in d:
        beliefs[ev['seq']] = {'seq': ev['seq'], 'text': d['text'], 'truth': d['truth'],
                              'confidence': d['confidence'], 'about': d.get('about'), 'entry': ev['entry']}


def f_claim(state, ev):
    d = ev['data']
    state['claims'].setdefault(ev['npc'], []).append({
        'seq': ev['seq'], 'to': d['to'], 'text': d['text'], 'truth': d['truth'], 'kind': d['kind'],
        'about': d.get('about'), 'entry': ev['entry']})


def f_want(state, ev):
    d, wants = ev['data'], state['wants'].setdefault(ev['npc'], {})
    if 'retire' in d:
        wants.pop(d['retire'], None)
    if 'text' in d:
        wants[ev['seq']] = {'seq': ev['seq'], 'text': d['text'], 'weight': d['weight'],
                            'conflict': d.get('conflict'), 'scene': d['scene'], 'entry': ev['entry']}


def close_intent(state, npc, seq, outcome, ev):
    intent = state['intents'].get(npc, {}).pop(seq, None)
    if intent:
        state['closed'].setdefault(npc, []).append(
            dict(intent, outcome=outcome, closed_seq=ev['seq'], closed_scene=ev['data']['scene']))


def f_intent(state, ev):
    d = ev['data']
    if 'close' in d:
        close_intent(state, ev['npc'], d['close'], d['outcome'], ev)
    if 'text' in d:
        state['intents'].setdefault(ev['npc'], {})[ev['seq']] = {
            'seq': ev['seq'], 'text': d['text'], 'horizon': d['horizon'], 'scene': d['scene'], 'entry': ev['entry']}


def f_veto(state, ev):
    d = ev['data']
    if 'intent' in d:
        close_intent(state, ev['npc'], d['intent'], 'vetoed', ev)
    state['vetoes'].setdefault(ev['npc'], []).append({
        'seq': ev['seq'], 'kind': d['kind'], 'reason': d['reason'], 'decides': d.get('decides'),
        'intent': d.get('intent'), 'scene': d['scene'], 'entry': ev['entry']})


def f_offscreen(state, ev):
    """What a character did off-screen: kept as one of their episodes, and as the call made at that boundary."""
    state['offscreen'].setdefault(ev['npc'], []).append({'seq': ev['seq'], 'scene': ev['data']['scene']})
    f_remember(state, ev)


def f_settings(state, ev):
    state['settings'].update(ev['data'])


FOLD = {'char': f_char, 'world': f_world, 'know': f_know, 'unlearn': f_unlearn,
        'remember': f_remember, 'compress': f_compress, 'session': f_session, 'state': f_state,
        'tick': f_tick, 'believe': f_believe, 'claim': f_claim, 'want': f_want, 'intent': f_intent,
        'veto': f_veto, 'offscreen': f_offscreen, 'settings': f_settings}


def replay(events):
    state = new_state()
    for ev in events:
        fold = FOLD.get(ev.get('op'))
        if not fold:
            raise Fail(f'events.jsonl seq {ev.get("seq")}: unknown op {ev.get("op")!r}')
        fold(state, ev)
    return state


class Brains:
    """One command's view of the workspace: the brain log, its replayed state, and game-master's state."""

    def __init__(self, root, need_log=True, migrating=False):
        self.root = root
        self.gm = gm_module(root)
        self.gm_state = gm_load(self.gm, root)
        stale = method_only_files(root)
        if stale and not migrating:
            raise Fail('notes/brains/ holds method-only brain files (' + ', '.join(stale) + '). The two brain '
                       'packages cannot run together; move those files into the log first, or keep the method-only package.')
        if need_log and not events_path(root).exists():
            raise Fail('notes/brains/events.jsonl is missing. Run: python tools/brains.py init')
        self.events = self.gm.read_lines(events_path(root)) if events_path(root).exists() else []
        self.state = replay(self.events)
        if not migrating:  # a view could overwrite a method-only file before migrate has copied it
            write_views(self)  # views also follow game-master, so every command rewrites them

    def next_seq(self):
        """One past every seq used, set-aside events included, so a seq is never reused."""
        used = self.events + self.gm.read_lines(withdrawn_path(self.root))
        return max((e.get('seq') or 0 for e in used), default=0) + 1

    def append(self, npc, op, data, entry=None, why=None):
        ev, warns = self.stage(npc, op, data, entry, why)
        self.save()
        return ev, warns

    def save(self):
        self.gm.write_text(events_path(self.root), self.gm.dump_lines(self.events))
        write_views(self)

    def stage(self, npc, op, data, entry=None, why=None):
        """Validate an event and apply it in memory; save() writes it."""
        if entry is None and op not in SETUP_OPS:
            raise Fail(f'{op} needs --entry: the story or Director entry that shows it')
        if entry is not None and entry not in self.gm.read_entries(self.root):
            raise Fail(f'entry {entry} is not in public/story.md or public/director.md')
        if npc is not None and not ID_RE.match(npc):
            raise Fail('a character id is letters, digits, - and _ (their game-master cast id)')
        ev = {'seq': self.next_seq(),
              'at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'npc': npc, 'op': op, 'entry': entry, 'why': why or f'{op} {npc or data.get("fact")}', 'data': data}
        if not text_ok(ev['why']):
            raise Fail(f'--why must be a text of at most {MAX_TEXT} characters')
        warns = VALIDATE[op](self.state, self.gm_state, ev)
        self.events.append(ev)
        FOLD[op](self.state, ev)
        return ev, warns


# ---- the brief -------------------------------------------------------------------------------
# A section is (b, npc, ctx) -> list of lines (empty to leave it out). Later tickets add sections here.

def sec_header(b, npc, ctx):
    char, sit = b.state['chars'][npc], b.gm_state['situation']
    who = ctx['as'] or char['name']
    parts = [who + (f', who is {char["name"]}' if ctx['as'] else '')]
    if char.get('age') is not None:
        parts.append(str(char['age']))
    if ctx.get('offscreen'):  # the situation's place is the player's scene, not where this character is now
        parts.append('between scenes, away from the player')
    elif sit.get('location'):
        parts.append('in ' + sit['location'])
    return [f'You are the mind of {", ".join(parts)}. Return only the block below.',
            'You know nothing beyond what this brief says. You may lie, withhold, misread, or refuse.']


def sec_who(b, npc, ctx):
    char, card = b.state['chars'][npc], b.gm_state['npcs'].get(npc, {})
    lines = [f'{k}: {card[k]}' for k in CARD_FIELDS[:4] if card.get(k)]
    if char.get('look'):
        lines.append('look: ' + char['look'])
    if card.get('voice'):
        lines.append('voice: ' + card['voice'])
    others = [a for a in char.get('aliases', []) if a != ctx['as']]
    if others:
        lines.append('also called: ' + ', '.join(others))
    return ['WHO THEY ARE'] + lines


def sec_memory(b, npc, ctx):
    eps = live_episodes(b.state, npc)
    keep = {e['seq'] for e in sorted(eps, key=lambda e: (-e['salience'], -e['seq']))[:MAX_EPISODES]}
    lines = ['- ' + e['text'] for e in eps if e['seq'] in keep]
    return ['WHAT THEY REMEMBER'] + lines if lines else []


def sec_owed(b, npc, ctx):
    threads = b.gm_state['threads']
    lines = ['- ' + threads[t]['text'] for t in b.state['chars'][npc].get('knows_threads', [])
             if t in threads and threads[t]['status'] in ('open', 'active', 'dormant')]
    return ['WHAT IS OWED'] + lines if lines else []


def sec_knows(b, npc, ctx):
    lines = []
    for fid, held in allowed_facts(b.state, b.gm_state, npc).items():
        fact = b.gm_state['facts'][fid]
        notes = [w for w in (CONFIDENCE_WORDS[held['confidence']],
                             'a rumour' if fact['status'] == 'rumour' else '',
                             'you keep this secret' if held['secret'] else '') if w]
        if held.get('how') and held['how'] != MIGRATED:
            notes.append('how: ' + held['how'])
        lines.append('- ' + fact['text'] + (f' ({"; ".join(notes)})' if notes else ''))
    return ['WHAT THEY KNOW'] + lines + ['They know nothing else about the world.']


def cast_name(b, cid):
    return (b.state['chars'].get(cid) or b.gm_state['npcs'].get(cid) or {}).get('name') or cid


def state_line(path, value):
    """One brief line for a state value, in words, never numbers; None when there is nothing to say."""
    field = path.split('.')[-1]
    if path == 'affect.valence':
        return None if value == 0 else 'spirits: ' + VALENCE_WORDS[value]
    if path.startswith('affect.') and field in AFFECT_LEVELS:
        # energy at 0 is exhaustion and is said; any other level at 0 is an absence, left out
        return None if value == 0 and field != 'energy' else f'{field}: {LEVEL_WORDS[value]}'
    return f'{STATE_LABELS[path]}: {value}'


def mark_text(b, mark):
    seen = mark.get('seen_by')
    if seen is None:
        return mark['text']
    who = SEEN[seen] if isinstance(seen, str) else 'seen by ' + ', '.join(cast_name(b, c) for c in seen)
    return f'{mark["text"]} ({who})'


def state_lines(b, npc, group):
    values = dict(b.state['states'].get(npc, {}).get(group, {}))
    if group == 'affect':
        values.update(current_affect(b.state, npc))
    lines = []
    for field in STATE_SCHEMA[group]:  # schema order, so the same state gives the same brief
        if field not in values:
            continue
        if group == 'body' and field == 'marks':
            lines.append('marks: ' + '; '.join(mark_text(b, values[field][m]) for m in sorted(values[field])))
        else:
            line = state_line(f'{group}.{field}', values[field])
            if line:
                lines.append(line)
    return lines


def sec_body(b, npc, ctx):
    lines = state_lines(b, npc, 'affect') + state_lines(b, npc, 'body')
    return ['HOW THEY ARE'] + lines if lines else []


def sec_desire(b, npc, ctx):
    lines = state_lines(b, npc, 'desire')
    return ['DESIRE'] + lines if lines else []


def sec_believes(b, npc, ctx):
    """Active beliefs, oldest first, with how sure they are. Never the truth label, never the about fact."""
    lines = []
    for seq in sorted(b.state['beliefs'].get(npc, {})):
        belief = b.state['beliefs'][npc][seq]
        word = CONFIDENCE_WORDS[belief['confidence']]
        lines.append('- ' + belief['text'] + (f' ({word})' if word else ''))
    return ['WHAT THEY BELIEVE'] + lines if lines else []


def present_ids(b, ctx=None):
    """Cast ids on stage now: game-master's situation.present, matched by id, name or alias, case-insensitively.
    The player counts as present: every brain call is part of a scene played with them. Off-screen, nobody is."""
    if ctx and ctx.get('offscreen'):
        return set()
    here = {p.strip().lower() for p in b.gm_state['situation'].get('present', []) if isinstance(p, str)}
    out = {PLAYER}
    for cid in sorted(set(b.state['chars']) | set(b.gm_state['npcs'])):
        char, card = b.state['chars'].get(cid, {}), b.gm_state['npcs'].get(cid, {})
        names = [cid, char.get('name'), card.get('name'), *char.get('aliases', [])]
        if any(n and n.lower() in here for n in names):
            out.add(cid)
    return out


def person_name(b, pid):
    return 'the player' if pid == PLAYER else cast_name(b, pid)


def edge_lines(b, npc, pid, edge, held):
    """The brief lines for one person: levels in words, the last thing between them, two propositions."""
    # a level at 0 is an absence and is left out, as in HOW THEY ARE
    parts = [f'{EDGE_LABELS[f]}: {EDGE_WORDS[edge[f]]}' for f in EDGE_LABELS if edge.get(f)]
    debt = edge.get('debt', 0)
    if debt:
        parts.append(f'they owe you {DEBT_WORDS[debt]}' if debt > 0 else f'you owe them {DEBT_WORDS[-debt]}')
    lines = ['  ' + '; '.join(parts)] if parts else []
    if edge.get('last'):
        lines.append('  last between you: ' + edge['last'])
    # only facts the character holds now: an unlearn after the edge was set takes the proposition out too
    order = list(b.gm_state['facts'])
    thinks = sorted(((fid, w) for fid, w in edge.get('thinks_knows', {}).items() if fid in held),
                    key=lambda p: (THINKS_ORDER[p[1]], order.index(p[0])))[:MAX_PROPOSITIONS]
    lines += [f'  {THINKS_WORDS[w]}: {b.gm_state["facts"][fid]["text"]}' for fid, w in thinks]
    return [person_name(b, pid)] + lines if lines else []


def sec_others(b, npc, ctx):
    """At most three people: those present first, then the most recently recorded, then by id."""
    people = b.state['states'].get(npc, {}).get('people', {})
    here, touched = present_ids(b, ctx), b.state['touched'].get(npc, {})
    held = allowed_facts(b.state, b.gm_state, npc)
    lines, shown = [], 0
    for pid in sorted(people, key=lambda p: (p not in here, -touched.get(p, 0), p)):
        more = edge_lines(b, npc, pid, people[pid], held)
        if more and shown < MAX_PEOPLE:
            lines += more
            shown += 1
    return ['OTHER PEOPLE'] + lines if lines else []


def sec_claims(b, npc, ctx):
    """Six claims at most: to people present first, newest first within each. The kind is said (the character
    knows when they lied); the truth label is not."""
    here = present_ids(b, ctx)
    claims = sorted(b.state['claims'].get(npc, []), key=lambda c: (c['to'] not in here, -c['seq']))[:MAX_CLAIMS]
    lines = [f'- to {person_name(b, c["to"])}, {KIND_WORDS[c["kind"]]}: {c["text"]}' for c in claims]
    return ['WHAT THEY HAVE TOLD PEOPLE'] + lines if lines else []


def top_wants(b, npc):
    """The standing wants the brief carries: heaviest first, then newest."""
    wants = b.state['wants'].get(npc, {}).values()
    return sorted(wants, key=lambda w: (-w['weight'], -w['seq']))[:BRIEF_WANTS]


def sec_wants(b, npc, ctx):
    """The top two standing wants, each with what pulls against it. The weight ranks them and is never printed."""
    lines = ['- ' + w['text'] + (f' (but: {w["conflict"]})' if w.get('conflict') else '') for w in top_wants(b, npc)]
    return ['WHAT THEY WANT'] + lines if lines else []


def active_intents(b, npc):
    """Active intents, nearest horizon first, then oldest."""
    return sorted(b.state['intents'].get(npc, {}).values(), key=lambda i: (HORIZONS.index(i['horizon']), i['seq']))


def sec_intents(b, npc, ctx):
    lines = [f'- {i["text"]} ({HORIZON_WORDS[i["horizon"]]})' for i in active_intents(b, npc)]
    return ['WHAT THEY MEAN TO DO'] + lines if lines else []


def sec_routine(b, npc, ctx):
    """Only off-screen: where the character's time goes when the story is elsewhere, in recorded order."""
    routine = b.state['states'].get(npc, {}).get('routine', {})
    if not ctx.get('offscreen') or not routine:
        return []
    return ['THEIR DAYS'] + [f'- {slot}: {routine[slot]}' for slot in routine]


def sec_now(b, npc, ctx):
    sit = b.gm_state['situation']
    place = '' if ctx.get('offscreen') else sit.get('location', '')
    when = ', '.join(x for x in (f'day {sit["day"]}' if sit.get('day') else '', sit.get('time', ''), place) if x)
    lines = ['NOW'] + ([when] if when else [])
    if ctx.get('offscreen'):
        lines.append('The story is elsewhere. Nobody is watching you; what you do now happens off the page.')
    return lines + ctx['scene']


def sec_answer(b, npc, ctx):
    keys, help_ = ((OFFSCREEN_ANSWER_KEYS, OFFSCREEN_ANSWER_HELP) if ctx.get('offscreen')
                   else (ANSWER_KEYS, ANSWER_HELP))
    return ['ANSWER'] + [f'{k}: {help_[k]}' for k in keys]


BRIEF_SECTIONS = [sec_header, sec_who, sec_memory, sec_owed, sec_knows, sec_believes, sec_body, sec_desire,
                  sec_others, sec_claims, sec_wants, sec_intents, sec_routine, sec_now, sec_answer]


def read_scene(path):
    """The perception-only scene file, less template comments. Refuses game-master lines and entry ids."""
    p = Path(path)
    if not p.is_file():
        raise Fail(f'no scene file at {path}')
    text = re.sub(r'<!--.*?-->', '', p.read_text(encoding='utf-8').replace('\r\n', '\n'), flags=re.S)
    lines = [ln.rstrip() for ln in text.split('\n')]
    for n, line in enumerate(lines, 1):
        if line.startswith('FACT '):
            raise Fail(f'scene file line {n} is a game-master fact line. Describe only what the character perceives.')
        if UUID_RE.search(line):
            raise Fail(f'scene file line {n} holds an entry id. Describe only what the character perceives.')
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    if not lines:
        raise Fail('the scene file is empty')
    return lines


def leaks(b, text):
    """Ids and paths that must never reach a brain, found in the finished brief."""
    found = []
    if UUID_RE.search(text):
        found.append('an entry id')
    # Game-master's own ids that look like ids (F12, T3), plus any fact-shaped id. Custom ids that are plain
    # words ("harbour") cannot be told from prose, so they are not searched for.
    ids = {i for coll in ('facts', 'threads', 'pressures', 'revelations') for i in b.gm_state.get(coll, {})
           if AUTO_ID.fullmatch(i)}
    hits = sorted(set(FACT_ID.findall(text)) | (set(AUTO_ID.findall(text)) & ids))
    if hits:
        found.append('ids ' + ', '.join(hits))
    if PATH_RE.search(text):
        found.append('a file path')
    return found


def build_brief(b, npc, scene_file, alias=None, offscreen=False):
    need_char(b.state, npc)
    if offscreen:
        if not b.state['settings']['offscreen']:
            raise Fail('off-screen calls are off for this story; they are asked about at apply. The Director turns '
                       'them on: python tools/brains.py settings --offscreen on')
        had = offscreen_at(b.state, b.gm_state['scene_count'])
        if had:
            raise Fail(f'{had} already had the off-screen call at this scene boundary; one per boundary')
    elif scene_file is None:
        raise Fail('give --scene: the perception-only scene file (only an off-screen brief may go without one)')
    gone = withdrawn_entries(b)
    if gone:
        raise Fail(f'{len(gone)} brain event(s) cite entries no longer in the logs (Undo?), so the brief could carry '
                   'what never happened. Run: python tools/gm_state.py reconcile --apply, then '
                   'python tools/brains.py reconcile --apply')
    if npc not in b.gm_state['npcs']:
        raise Fail(f'{npc} has no game-master cast card')
    char = b.state['chars'][npc]
    if alias is not None and alias not in char.get('aliases', []):
        raise Fail(f'{alias!r} is not one of {npc}\'s aliases; add it with: python tools/brains.py add {npc} --alias ...')
    ctx = {'as': alias, 'scene': read_scene(scene_file) if scene_file else [], 'offscreen': offscreen}
    blocks = [lines for lines in (sec(b, npc, ctx) for sec in BRIEF_SECTIONS) if lines]
    text = '\n\n'.join('\n'.join(lines) for lines in blocks) + '\n'
    found = leaks(b, text)
    if found:
        raise Fail('the brief would carry ' + ' and '.join(found) + '. Reword the fact, memory or scene text '
                   'that holds it; a brain sees only what the character perceives.')
    return text


# ---- generated views -------------------------------------------------------------------------

def render_view(b, npc):
    char, card = b.state['chars'][npc], b.gm_state['npcs'].get(npc, {})
    out = [GENERATED, f'# Brain: {char["name"]} ({npc})', '',
           f'tier: {char.get("tier")}  ', f'session: {char.get("session") or "none"}  ',
           f'age: {char.get("age", "not set")}  ', f'look: {char.get("look", "not set")}  ',
           'aliases: ' + (', '.join(char.get('aliases', [])) or 'none') + '  ',
           'threads: ' + (', '.join(char.get('knows_threads', [])) or 'none'), '',
           f'## Card snapshot (game-master seq {char.get("card_at")})', '']
    snap = char.get('card', {})
    out += [f'- {k}: {snap.get(k, "-")}' + ('' if snap.get(k) == card.get(k) else '  (changed since)')
            for k in CARD_FIELDS]
    out += ['', '## Knows', '']
    held = allowed_facts(b.state, b.gm_state, npc)
    out += [f'- {fid} [{h["source"]}, {h["confidence"]}] {b.gm_state["facts"][fid]["text"]}'
            + (f' (how: {h["how"]}; entry {h["entry"]})' if h.get('how') else '') for fid, h in held.items()] or ['- nothing']
    out += ['', '## Episodes', '']
    out += [f'- seq {e["seq"]} [salience {e["salience"]}] {e["text"]}' for e in live_episodes(b.state, npc)] or ['- none']
    out += ['', '## State', '']
    tree, affect = b.state['states'].get(npc, {}), current_affect(b.state, npc)
    rows = []
    for field in AFFECT_LEVELS:
        if field in affect:
            words = (VALENCE_WORDS if field == 'valence' else LEVEL_WORDS)[affect[field]]
            rows.append(f'- affect.{field}: {affect[field]} ({words}; baseline {baseline_of(b.state, npc, field)})')
    for group in STATE_SCHEMA:
        for field, value in tree.get(group, {}).items():
            if group == 'affect' and field in AFFECT_LEVELS:
                continue
            if group == 'body' and field == 'marks':
                rows += [f'- body.marks.{m}: {mark_text(b, value[m])}' for m in sorted(value)]
            else:
                rows += [f'- {path}: {v}' for path, v in flatten(value, f'{group}.{field}')]
    out += rows or ['- nothing set']
    out += ['', '## Beliefs', '']
    out += [f'- seq {s["seq"]} [{s["truth"]}, {s["confidence"]}' + (f', about {s["about"]}' if s['about'] else '')
            + f'] {s["text"]}' for _, s in sorted(b.state['beliefs'].get(npc, {}).items())] or ['- none']
    out += ['', '## Claims', '']
    out += [f'- seq {c["seq"]} to {c["to"]} [{c["kind"]}, {c["truth"]}' + (f', about {c["about"]}' if c['about'] else '')
            + f'] {c["text"]}' for c in b.state['claims'].get(npc, [])] or ['- none']
    out += ['', '## Wants', '']
    out += [f'- seq {w["seq"]} [weight {w["weight"]}, scene {w["scene"]}] {w["text"]}'
            + (f' (conflict: {w["conflict"]})' if w.get('conflict') else '')
            for _, w in sorted(b.state['wants'].get(npc, {}).items())] or ['- none']
    out += ['', '## Intents', '']
    out += [f'- seq {i["seq"]} [{i["horizon"]}, scene {i["scene"]}] {i["text"]}' for i in active_intents(b, npc)]
    out += [f'- seq {i["seq"]} [{i["outcome"]} at seq {i["closed_seq"]}, scene {i["closed_scene"]}] {i["text"]}'
            for i in b.state['closed'].get(npc, [])]
    if out[-1] == '':
        out.append('- none')
    out += ['', '## Vetoes', '']
    out += [f'- seq {v["seq"]} [{v["kind"]}, scene {v["scene"]}] {v["reason"]}'
            + (f' (decided: {v["decides"]})' if v.get('decides') else '') for v in b.state['vetoes'].get(npc, [])
            ] or ['- none']
    calls = b.state['offscreen'].get(npc, [])
    out += ['', '## Off-screen calls', '', '- scenes ' + ', '.join(str(o['scene']) for o in calls) if calls else '- none']
    return '\n'.join(out) + '\n'


def flatten(value, prefix):
    """(dotted path, leaf value) pairs of a state subtree, in recorded order."""
    if not isinstance(value, dict):
        return [(prefix, value)]
    return [pair for key, sub in value.items() for pair in flatten(sub, f'{prefix}.{key}')]


def write_views(b):
    for npc in sorted(b.state['chars']):
        b.gm.write_text(brains_dir(b.root) / f'{npc}.md', render_view(b, npc))
    for path in brains_dir(b.root).glob('*.md'):  # a brain set aside by reconcile leaves no stale view
        if path.stem not in b.state['chars'] and path.read_text(encoding='utf-8').startswith(GENERATED):
            path.unlink()


# ---- check -----------------------------------------------------------------------------------

def unclassified(b):
    return [fid for fid, f in b.gm_state['facts'].items()
            if f['status'] not in TERMINAL_FACT and fid not in b.state['world']]


def run_check(b):
    errs, warns = [], []
    seqs = [e.get('seq') for e in b.events]
    if seqs != sorted(set(seqs)):
        errs.append('events.jsonl seq numbers are not strictly increasing; the log was edited by hand')
    for ev in b.events:
        missing = [k for k in ('seq', 'at', 'npc', 'op', 'entry', 'why', 'data') if k not in ev]
        if missing:
            errs.append(f'seq {ev.get("seq")}: missing ' + ', '.join(missing))
        elif ev['entry'] is None and ev['op'] not in SETUP_OPS:
            errs.append(f'seq {ev["seq"]}: {ev["op"]} cites no entry')
    for fid in unclassified(b):
        errs.append(f'{fid} has no brain visibility; until it does, every brain is blind to it. '
                    f'Run: python tools/brains.py world {fid} --visibility ...')
    for npc in sorted(b.state['chars']):
        if npc not in b.gm_state['npcs']:
            errs.append(f'{npc} has a brain but no game-master cast card')
    entries = b.gm.read_entries(b.root)
    for ev in b.events:
        if ev.get('entry') and ev['entry'] not in entries:
            warns.append(f'seq {ev["seq"]} ({ev["op"]} {ev.get("npc")}) cites entry {ev["entry"]}, no longer in the logs '
                         '(Undo?). Run: python tools/brains.py reconcile')
    for npc in sorted(b.state['chars']):
        held = allowed_facts(b.state, b.gm_state, npc)
        for fid in b.state['knows'].get(npc, {}):
            fact = b.gm_state['facts'].get(fid, {})
            new = fact.get('replaced_by')
            if new and new not in held:
                warns.append(f'{npc} knew {fid}, which {new} replaced; they do not hold {new}. Record know if they learned it.')
    for fid, w in b.state['world'].items():
        if fid not in b.gm_state['facts']:
            warns.append(f'{fid} is classified but is no longer a game-master fact')
    for npc in sorted(b.state['claims']):
        claims = b.state['claims'][npc]
        warns += [contradiction_warning(npc, a, c) for i, c in enumerate(claims) for a in claims[:i]
                  if contradiction(a, c)]
    for npc in sorted(b.state['states']):
        held = allowed_facts(b.state, b.gm_state, npc)
        for pid, edge in b.state['states'][npc].get('people', {}).items():
            for fid in edge.get('thinks_knows', {}):
                if fid not in held:
                    warns.append(f'{npc} thinks about whether {pid} knows {fid}, which {npc} no longer holds; the '
                                 f'brief leaves it out. Clear it: state {npc} --set people.{pid}.thinks_knows.{fid}=')
    return errs, warns


# ---- reconcile (ISS-25) ----------------------------------------------------------------------

def withdrawn_entries(b):
    """Events that cite an entry no longer in the public logs: a Director Undo took it back."""
    entries = b.gm.read_entries(b.root)
    return [ev for ev in b.events if ev.get('entry') and ev['entry'] not in entries]


def holds(state, npc, fid):
    """Whether the character held a fact before an unlearn; outdated or discarded facts count, as they did then."""
    world = state['world'].get(fid)
    seen = world and (world['visibility'] == 'public' or npc in world['witnesses'])
    return fid in state['knows'].get(npc, {}) or bool(seen and fid not in state['unlearned'].get(npc, set()))


def dependency(state, gm_state, ev):
    """Why an event cannot stand on what is left (the kept events before it, and game-master now), or None.

    Like game-master's reconcile, only what a withdrawal can break is rechecked: a fact that has since
    become outdated does not set aside the know event recorded while it was live."""
    op, npc, d = ev.get('op'), ev.get('npc'), ev.get('data') or {}
    if op == 'char':
        if npc not in gm_state['npcs']:
            return f'{npc} no longer has a game-master cast card'
        lost = [t for t in d.get('knows_threads', []) if t not in gm_state['threads']]
        return 'threads ' + ', '.join(lost) + ' are no longer in game-master' if lost else None
    if op == 'settings':
        return None
    if op != 'world' and npc not in state['chars']:
        return f'{npc} has no brain once the events it rests on are set aside'
    fid = d.get('fact')
    if op in ('world', 'know', 'unlearn') and fid not in gm_state['facts']:
        return f'{fid} is no longer a game-master fact'
    if op == 'world':
        lost = [w for w in d.get('witnesses', []) if w not in state['chars'] and w not in gm_state['npcs']]
        if lost:
            return 'witnesses ' + ', '.join(lost) + ' are no longer cast'
    if op == 'unlearn' and not holds(state, npc, fid):
        return f'{npc} no longer held {fid} to unlearn'
    def cast(w):
        return w in state['chars'] or w in gm_state['npcs']

    if op == 'state':
        for path, value in d.get('set', []):
            if path.endswith('.seen_by') and isinstance(value, list):
                lost = [w for w in value if not cast(w)]
                if lost:
                    return f'{path} names {", ".join(lost)}, no longer cast'
            parts = path.split('.')
            if value is None or parts[0] != 'people' or len(parts) < 2:
                continue
            if parts[1] != PLAYER and not cast(parts[1]):
                return f'{path} is about {parts[1]}, no longer cast'
            if len(parts) > 3 and parts[2] == 'thinks_knows':
                if parts[3] not in gm_state['facts']:
                    return f'{path}: {parts[3]} is no longer a game-master fact'
                if not holds(state, npc, parts[3]):
                    return f'{path}: {npc} no longer holds {parts[3]}'
    if op in ('believe', 'claim') and d.get('about') is not None and d['about'] not in gm_state['facts']:
        return f'it is about {d["about"]}, no longer a game-master fact'
    if op == 'believe' and 'retire' in d and d['retire'] not in state['beliefs'].get(npc, {}):
        return f'it retired the belief at seq {d["retire"]}, which is set aside'
    if op == 'claim' and d.get('to') != PLAYER and not cast(d.get('to')):
        return f'it was said to {d.get("to")}, no longer cast'
    # ISS-28: closing what is set aside, or a fourth want or intent once a retire or close it relied on is gone
    if op == 'want':
        wants = state['wants'].get(npc, {})
        if 'retire' in d and d['retire'] not in wants:
            return f'it retired the want at seq {d["retire"]}, which is set aside'
        if 'text' in d and len(wants) - ('retire' in d) >= MAX_WANTS:
            return f'{npc} would hold more than {MAX_WANTS} standing wants'
    if op in ('intent', 'veto'):
        intents, seq = state['intents'].get(npc, {}), d.get('close', d.get('intent'))
        if seq is not None and seq not in intents:
            return f'it closed the intent at seq {seq}, which is set aside'
        if op == 'intent' and 'text' in d and len(intents) - ('close' in d) >= MAX_INTENTS:
            return f'{npc} would hold more than {MAX_INTENTS} active intents'
    if op == 'believe' and 'text' in d and len(state['beliefs'].get(npc, {})) - ('retire' in d) >= MAX_BELIEFS:
        return f'{npc} would hold more than {MAX_BELIEFS} beliefs'
    if op == 'compress':
        live = state['episodes'].get(npc, {})
        lost = [str(q) for q in d.get('replaces', []) if q not in live]
        if lost:
            return 'it folded episodes that are set aside (seq ' + ', '.join(lost) + ')'
    return None


def plan_reconcile(b):
    """(kept events, [(event, why it is set aside)]), in log order."""
    entries = b.gm.read_entries(b.root)
    state, kept, aside = new_state(), [], []
    for ev in b.events:
        if ev.get('entry') and ev['entry'] not in entries:
            aside.append((ev, f'entry {ev["entry"]} is no longer in the logs'))
            continue
        why = dependency(state, b.gm_state, ev)
        if why:
            aside.append((ev, 'depends on what was set aside: ' + why))
            continue
        FOLD[ev['op']](state, ev)
        kept.append(ev)
    return kept, aside


# ---- migrate (ISS-25) ------------------------------------------------------------------------

# Guidance lines of the method-only brain template; a file copied from it may still hold them.
TEMPLATE_LINES = {
    'Frame, colouring and one recurring physical detail, in one line. A brain will reach for the body; '
    'give it the right one.',
    'Optional, one line, written plainly: what they want sexually or physically, what they refuse, what they would '
    'never admit. Leave it out when it does not belong in the story. Their limits are authoritative: cut anything a '
    'brain writes that crosses them.',
    'Fact ids this character has learned, with the entry where they learned it. Only these hidden truths '
    '(facts with `"known": false`) may enter their brief.',
    'What they did, what they learned, what they will not forget. Newest last.',
    'Written every third turn the brain is called, or at a scene\'s end. See the protocol\'s "Memory".'}
KNOWN_SECTIONS = ('Look', 'Desire', 'Knows', 'Memory', 'Digest', 'Sheet')
BULLET = re.compile(r'^(?:[-*+]|\d+[.)])\s+')


def parse_method_only(text):
    """A method-only brain file: its name, header fields (npc, session, tier) and sections (title -> lines)."""
    out = {'name': None, 'fields': {}, 'sections': {}}
    current = None
    for line in text.replace('\r\n', '\n').split('\n'):
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m:
            current = out['sections'].setdefault(m.group(1), [])
        elif current is not None:
            current.append(line)
        elif re.match(r'^#\s+Brain file:', line):
            out['name'] = line.split(':', 1)[1].strip()
        else:
            m = re.match(r'^(npc|session|tier):\s*(.*?)\s*$', line)
            if m:
                out['fields'][m.group(1)] = m.group(2)
    return out


def items(lines):
    """Bullets and paragraphs, one text each; a wrapped line joins the item above it. Template guidance is dropped."""
    out, joinable = [], False
    for line in lines:
        s = line.strip()
        if not s or s in TEMPLATE_LINES or s.startswith('<!--'):
            joinable = False
            continue
        if BULLET.match(s):
            out.append(BULLET.sub('', s))
        elif joinable and not s.startswith('DIGEST:'):  # a digest pasted under Memory is its own item
            out[-1] += ' ' + s
        else:
            out.append(s)
        joinable = True
    return out


def chunks(text, size=MAX_TEXT):
    """Split a text into pieces of at most size characters, at sentence ends, then at spaces."""
    text = ' '.join(text.split())
    if len(text) <= size:
        return [text]
    pieces = []
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        pieces += [sentence] if len(sentence) <= size else [w[i:i + size] for w in sentence.split()
                                                            for i in range(0, len(w), size)]
    out = ['']
    for piece in pieces:
        if out[-1] and len(out[-1]) + 1 + len(piece) > size:
            out.append('')
        out[-1] = (out[-1] + ' ' + piece).strip()
    return out


def default_entry(b):
    story = [eid for eid, e in b.gm.read_entries(b.root).items() if e.get('channel') == 'story.md']
    if not story:
        raise Fail('public/story.md has no entry for the migrated memories to cite; give --entry')
    return story[-1]


def migrate_file(b, path, entry, entries):
    """Stage one method-only file's events; return (summary, warnings)."""
    src = parse_method_only(path.read_text(encoding='utf-8'))
    npc, name, secs, warns = src['fields'].get('npc', ''), path.name, src['sections'], []
    if npc in b.state['chars']:
        raise Fail(f'{name}: {npc} already has a brain in events.jsonl; move the file aside by hand')
    card = b.gm_state['npcs'].get(npc, {})
    title = src['name'] if src['name'] and '<' not in src['name'] else None
    data = {'name': title or card.get('name') or npc,
            'card': {k: card[k] for k in CARD_FIELDS if card.get(k)}, 'card_at': gm_seq(b.gm, b.root)}
    look = ' '.join(items(secs.get('Look', [])))
    if look:
        if len(look) > MAX_TEXT:
            warns.append(f'{name}: the look was cut to {MAX_TEXT} characters; the whole of it is in the legacy copy')
            look = look[:MAX_TEXT]
        data['look'] = look
    why = f'migrated from {name}'
    b.stage(npc, 'char', data, None, why)
    tier = (src['fields'].get('tier', '').split() or ['ephemeral'])[0].lower()
    if tier not in TIERS:
        warns.append(f'{name}: tier {src["fields"]["tier"]!r} is not persistent or ephemeral; recorded as ephemeral')
        tier = 'ephemeral'
    session = src['fields'].get('session', '').split()
    session = None if not session or session[0].lower() in ('none', 'new') else session[0]
    b.stage(npc, 'session', {'session': session, 'tier': tier}, None, why)

    memories = []
    for text in items(secs.get('Memory', [])):
        digest = re.match(r'^DIGEST:\s*', text)
        memories.append((text[digest.end():] if digest else text, 4 if digest else 3))
    digest = ' '.join(items(secs.get('Digest', [])))
    if digest:
        memories.append((digest, 4))  # the digest becomes one summary, ranked above a plain memory
    count = {3: 0, 4: 0}
    for text, salience in memories:
        parts = chunks(text)
        if len(parts) > 1:
            warns.append(f'{name}: a memory longer than {MAX_TEXT} characters was split into {len(parts)} episodes')
        found = leaks(b, text)
        if found:
            warns.append(f'{name}: the memory "{text[:60]}" holds ' + ' and '.join(found) + '; a brief is refused '
                         'until it is folded into reworded text with compress')
        for part in parts:
            b.stage(npc, 'remember', {'text': part, 'salience': salience}, entry, why)
            count[salience] += 1

    knows = []
    for line in items(secs.get('Knows', [])):
        if re.search(r'<[^>]+>', line):
            continue  # the template's placeholder bullet
        cited = UUID_RE.search(line)
        words = re.findall(r'[A-Za-z][A-Za-z0-9_-]*', UUID_RE.sub(' ', line))
        fids = [w for w in dict.fromkeys(words) if w in b.gm_state['facts']]
        if not fids:
            odd = FACT_ID.findall(line)
            warns.append(f'{name}: Knows line "{line}" ' + (f'names {", ".join(odd)}, not a game-master fact' if odd
                         else 'names no fact id') + f'; if {npc} knows it, record it with know')
            continue
        at = cited.group(0) if cited else entry
        if at not in entries:
            warns.append(f'{name}: Knows line "{line}" cites entry {at}, no longer in the logs; not moved')
            continue
        for fid in fids:
            status = b.gm_state['facts'][fid]['status']
            if status in TERMINAL_FACT:
                warns.append(f'{name}: {fid} is {status}; not moved')
            elif fid not in b.state['knows'].get(npc, {}):
                b.stage(npc, 'know', {'fact': fid, 'how': MIGRATED, 'confidence': 'certain', 'migrated': True},
                        at, why)
                knows.append(fid)
    for title in secs:
        if not items(secs[title]):
            continue
        if title == 'Desire':
            warns.append(f'{name}: the Desire line is kept only in the legacy copy, never split by guesswork. Record '
                         f'it with python tools/brains.py state {npc} --set desire.limits=... desire.wants=... '
                         '--entry E, limits first')
        elif title == 'Sheet':
            warns.append(f'{name}: the Sheet is kept only in the legacy copy; remember what of it the character keeps')
        elif title not in KNOWN_SECTIONS:
            warns.append(f'{name}: section "{title}" is kept only in the legacy copy')
    return {'npc': npc, 'file': f'notes/brains/{name}', 'legacy': f'notes/brains/legacy/{name}',
            'memories': count[3], 'summaries': count[4], 'knows': knows}, warns


# ---- commands --------------------------------------------------------------------------------

def cmd_init(args):
    if method_only_files(args.root):
        Brains(args.root, need_log=False)  # raises with the explanation
    gm = gm_module(args.root)
    gm_load(gm, args.root)
    path = events_path(args.root)
    if not path.exists():
        gm.write_text(path, '')
    return {'ready': 'notes/brains/events.jsonl'}, []


def cmd_add(args):
    b = Brains(args.root)
    card = b.gm_state['npcs'].get(args.npc)
    if not card:
        raise Fail(f'{args.npc} has no game-master cast card. Add one first (kind npc, op set).')
    old = b.state['chars'].get(args.npc, {})
    data = {'name': args.name or old.get('name') or card.get('name'),
            'card': {k: card[k] for k in CARD_FIELDS if card.get(k)}, 'card_at': gm_seq(b.gm, args.root)}
    if args.age is not None:
        data['age'] = args.age
    if args.look:
        data['look'] = args.look
    if args.alias:
        data['aliases'] = sorted(set(old.get('aliases', [])) | set(args.alias))
    if args.threads is not None:
        data['knows_threads'] = args.threads
    if args.baseline:
        data['baseline'] = dict(old.get('baseline', {}))
        for item in args.baseline:
            field, _, raw = item.partition('=')
            data['baseline'][field] = parse_level(raw, f'baseline {field}')
    ev, warns = b.append(args.npc, 'char', data, args.entry, args.why or f'brain for {args.npc}')
    return {'seq': ev['seq'], 'npc': args.npc}, warns


def cmd_world(args):
    b = Brains(args.root)
    if args.audit:
        missing = unclassified(b)
        return {'unclassified': [{'fact': f, 'text': b.gm_state['facts'][f]['text']} for f in missing],
                'classified': {f: {k: w[k] for k in ('visibility', 'witnesses')} for f, w in sorted(b.state['world'].items())}
                }, [f'{f} is unclassified' for f in missing]
    if not args.fact or not args.visibility:
        raise Fail('give a fact and --visibility, or --audit')
    data = {'fact': args.fact, 'visibility': args.visibility, 'witnesses': sorted(set(args.witnesses))}
    ev, warns = b.append(None, 'world', data, args.entry, args.why or f'{args.fact} is {args.visibility}')
    return {'seq': ev['seq'], 'fact': args.fact, 'visibility': args.visibility}, warns


def cmd_know(args):
    b = Brains(args.root)
    data = {'fact': args.fact, 'how': args.how, 'confidence': args.confidence}
    ev, warns = b.append(args.npc, 'know', data, args.entry, args.why or f'{args.npc} learned {args.fact}')
    return {'seq': ev['seq']}, warns


def cmd_unlearn(args):
    b = Brains(args.root)
    ev, warns = b.append(args.npc, 'unlearn', {'fact': args.fact}, args.entry, args.why)
    return {'seq': ev['seq']}, warns


def cmd_remember(args):
    b = Brains(args.root)
    ev, warns = b.append(args.npc, 'remember', {'text': args.text, 'salience': args.salience},
                         args.entry, args.why or f'{args.npc} remembers')
    return {'seq': ev['seq']}, warns


def cmd_compress(args):
    b = Brains(args.root)
    data = {'text': args.text, 'salience': args.salience, 'replaces': sorted(set(args.replace))}
    ev, warns = b.append(args.npc, 'compress', data, args.entry, args.why or f'compressed {len(data["replaces"])} episodes')
    return {'seq': ev['seq']}, warns


def cmd_session(args):
    b = Brains(args.root)
    if bool(args.id) == bool(args.end):
        raise Fail('give --id for a new or resumed session, or --end')
    ev, warns = b.append(args.npc, 'session', {'session': None if args.end else args.id, 'tier': args.tier},
                         args.entry, args.why or ('session ended' if args.end else 'session started'))
    return {'seq': ev['seq']}, warns


def parse_level(raw, path):
    try:
        return int(raw)
    except ValueError:
        raise Fail(f'{path} is a whole number, not {raw!r}')


def parse_set(item):
    """PATH=VALUE as [path, value]: an empty value clears; a mark's own path sets its text."""
    path, eq, raw = item.partition('=')
    if not eq:
        raise Fail(f'--set {item!r}: write PATH=VALUE, for example affect.fear=3 (an empty value clears)')
    parts, spec = state_spec(path)
    raw = raw.strip()
    if not raw:
        return [path, None]
    if isinstance(spec, dict) and 'text' in spec:
        parts, spec = parts + ['text'], spec['text']
    path = '.'.join(parts)
    if isinstance(spec, tuple) and spec[0] == 'level':
        return [path, parse_level(raw, path)]
    if spec == ('seen',):
        return [path, raw if raw in SEEN else sorted({w.strip() for w in raw.split(',') if w.strip()})]
    return [path, raw]


def cmd_state(args):
    b = Brains(args.root)
    need_char(b.state, args.npc)
    if not args.set:
        return {'npc': args.npc, 'state': b.state['states'].get(args.npc, {}),
                'affect': current_affect(b.state, args.npc),
                'baseline': {f: baseline_of(b.state, args.npc, f) for f in AFFECT_LEVELS}}, []
    pairs = [parse_set(item) for group in args.set for item in group]
    ev, warns = b.append(args.npc, 'state', {'set': pairs}, args.entry, args.why or f'{args.npc} state changed')
    return {'seq': ev['seq'], 'state': b.state['states'].get(args.npc, {})}, warns


def cmd_tick(args):
    b = Brains(args.root)
    need_char(b.state, args.npc)
    moves = tick_moves(b.state, args.npc, args.scene_end)
    if not moves:
        held = [f for f in BOUNDARY_ONLY if f in tick_moves(b.state, args.npc, True)]
        return {'moved': {}}, [f'{args.npc}: nothing to move toward baseline'
                               + (f' until a scene boundary ({", ".join(held)}: tick --scene-end)' if held else '')
                               + '; nothing recorded']
    ev, warns = b.append(args.npc, 'tick', {'boundary': args.scene_end}, args.entry,
                         args.why or ('the scene ended' if args.scene_end else 'time passed'))
    return {'seq': ev['seq'], 'moved': {f: list(m) for f, m in moves.items()}}, warns


def cmd_believe(args):
    b = Brains(args.root)
    data = {}
    if args.retire is not None:
        data['retire'] = args.retire
    if args.text is not None:
        data.update(text=args.text, truth=args.truth, confidence=args.confidence)
        if args.about:
            data['about'] = args.about
    elif args.truth or args.confidence or args.about:
        raise Fail('--truth, --confidence and --about go with a new belief\'s --text')
    ev, warns = b.append(args.npc, 'believe', data, args.entry,
                         args.why or (f'{args.npc} came to believe something' if 'text' in data
                                      else f'{args.npc} no longer believes seq {args.retire}'))
    return {'seq': ev['seq'], 'active': len(b.state['beliefs'].get(args.npc, {}))}, warns


def cmd_claim(args):
    b = Brains(args.root)
    data = {'to': args.to, 'text': args.text, 'truth': args.truth, 'kind': args.kind}
    if args.about:
        data['about'] = args.about
    ev, warns = b.append(args.npc, 'claim', data, args.entry, args.why or f'{args.npc} told {args.to} something')
    return {'seq': ev['seq']}, warns


def cmd_want(args):
    b = Brains(args.root)
    data = {'scene': b.gm_state['scene_count']}
    if args.retire is not None:
        data['retire'] = args.retire
    if args.text is not None:
        data.update(text=args.text, weight=args.weight)
        if args.conflict:
            data['conflict'] = args.conflict
    elif args.conflict:
        raise Fail('--weight and --conflict go with a new want\'s --text')
    ev, warns = b.append(args.npc, 'want', data, args.entry,
                         args.why or (f'{args.npc} wants something' if 'text' in data
                                      else f'{args.npc} no longer wants seq {args.retire}'))
    return {'seq': ev['seq'], 'active': len(b.state['wants'].get(args.npc, {}))}, warns


def cmd_intent(args):
    b = Brains(args.root)
    if args.done is not None and args.drop is not None:
        raise Fail('give --done or --drop, not both')
    data = {'scene': b.gm_state['scene_count']}
    closing = args.done if args.done is not None else args.drop
    if closing is not None:
        data.update(close=closing, outcome='done' if args.done is not None else 'dropped')
    if args.text is not None:
        data.update(text=args.text, horizon=args.horizon)
    elif args.horizon:
        raise Fail('--horizon goes with a new intent\'s --text')
    ev, warns = b.append(args.npc, 'intent', data, args.entry,
                         args.why or (f'{args.npc} means to do something' if 'text' in data
                                      else f'{args.npc} intent seq {closing} {data["outcome"]}'))
    return {'seq': ev['seq'], 'active': len(b.state['intents'].get(args.npc, {}))}, warns


def cmd_veto(args):
    b = Brains(args.root)
    data = {'kind': args.kind, 'reason': args.reason, 'scene': b.gm_state['scene_count']}
    if args.decides:
        data['decides'] = args.decides
    if args.intent is not None:
        data['intent'] = args.intent
    ev, warns = b.append(args.npc, 'veto', data, args.entry, args.why or f'a decision of {args.npc} was not honoured')
    return {'seq': ev['seq'], 'vetoes': len(b.state['vetoes'][args.npc])}, warns


def cmd_offscreen(args):
    b = Brains(args.root)
    data = {'text': args.does, 'salience': args.salience, 'scene': b.gm_state['scene_count']}
    ev, warns = b.append(args.npc, 'offscreen', data, args.entry, args.why or f'{args.npc} off-screen')
    return {'seq': ev['seq'], 'scene': data['scene']}, warns


def cmd_settings(args):
    b = Brains(args.root)
    if args.offscreen is None:
        return {'settings': b.state['settings']}, []
    ev, warns = b.append(None, 'settings', {'offscreen': args.offscreen == 'on'}, args.entry,
                         args.why or f'off-screen calls {args.offscreen}')
    return {'seq': ev['seq'], 'settings': b.state['settings']}, warns


def cmd_brief(args):
    b = Brains(args.root)
    text = build_brief(b, args.npc, args.scene, args.alias, args.offscreen)
    if args.text:
        sys.stdout.write(text)
        return None, []
    return {'npc': args.npc, 'brief': text}, []


def cmd_view(args):
    b = Brains(args.root)
    write_views(b)
    if args.npc:
        need_char(b.state, args.npc)
        return {'path': f'notes/brains/{args.npc}.md', 'view': render_view(b, args.npc)}, []
    return {'views': [f'notes/brains/{n}.md' for n in sorted(b.state['chars'])]}, []


def cmd_check(args):
    b = Brains(args.root)
    errs, warns = run_check(b)
    if errs:
        raise Fail('; '.join(errs) + ('; warnings: ' + '; '.join(warns) if warns else ''))
    return {'events': len(b.events), 'brains': sorted(b.state['chars'])}, warns


def cmd_migrate(args):
    names = method_only_files(args.root)
    if not names:
        return {'migrated': []}, ['notes/brains/ holds no method-only brain files; nothing to migrate']
    b = Brains(args.root, need_log=False, migrating=True)
    entries = b.gm.read_entries(args.root)
    entry = args.entry or default_entry(b)
    if entry not in entries:
        raise Fail(f'entry {entry} is not in public/story.md or public/director.md')
    paths = [brains_dir(args.root) / n for n in names]
    npcs = [parse_method_only(p.read_text(encoding='utf-8'))['fields'].get('npc', '') for p in paths]
    twice = sorted({n for n in npcs if npcs.count(n) > 1})
    if twice:
        raise Fail('more than one method-only file is for ' + ', '.join(twice) + '; merge them by hand first')
    legacy = brains_dir(args.root) / 'legacy'
    for path in paths:  # the copies come first, so nothing is lost whatever happens next
        dest = legacy / path.name
        if dest.exists() and dest.read_bytes() != path.read_bytes():
            raise Fail(f'notes/brains/legacy/{path.name} already exists and differs; move one of them aside by hand')
        legacy.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
    done, warns = [], []
    for path in paths:
        summary, more = migrate_file(b, path, entry, entries)
        done.append(summary)
        warns += more
    b.save()  # one write, once every file staged cleanly; a view replaces the file named after its npc
    for path in paths:
        if path.exists() and not path.read_text(encoding='utf-8').startswith(GENERATED):
            path.unlink()  # its copy is in legacy/; left here it would block every command
    for s in done:
        warns.append(f'{s["npc"]}: no know event was invented. Record with know each fact they hold that the old '
                     'file did not list by id, and classify facts with world --audit')
    return {'migrated': done, 'entry': entry}, warns


def cmd_reconcile(args):
    b = Brains(args.root)
    kept, aside = plan_reconcile(b)
    listed = [{'seq': ev['seq'], 'op': ev['op'], 'npc': ev.get('npc'), 'why': why} for ev, why in aside]
    if not aside:
        return {'set_aside': [], 'applied': False, 'remaining': len(kept)}, []
    if not args.apply:
        return {'set_aside': listed, 'applied': False, 'remaining': len(kept)}, [
            f'{len(aside)} event(s) to set aside. Run again with --apply (they are kept in notes/brains/withdrawn.jsonl).']
    old = b.gm.read_lines(withdrawn_path(args.root))
    b.gm.write_text(withdrawn_path(args.root), b.gm.dump_lines(old + [ev for ev, _ in aside]))
    b.events, b.state = kept, replay(kept)
    b.save()
    return {'set_aside': listed, 'applied': True, 'remaining': len(kept)}, []


COMMANDS = {'init': cmd_init, 'add': cmd_add, 'world': cmd_world, 'know': cmd_know, 'unlearn': cmd_unlearn,
            'remember': cmd_remember, 'compress': cmd_compress, 'session': cmd_session, 'brief': cmd_brief,
            'view': cmd_view, 'check': cmd_check, 'migrate': cmd_migrate, 'reconcile': cmd_reconcile,
            'state': cmd_state, 'tick': cmd_tick, 'believe': cmd_believe, 'claim': cmd_claim, 'want': cmd_want,
            'intent': cmd_intent, 'veto': cmd_veto, 'offscreen': cmd_offscreen, 'settings': cmd_settings}


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('--root', default='.')
    sub = p.add_subparsers(dest='cmd', required=True)

    def cmd(name, npc=True, entry=True):
        s = sub.add_parser(name)
        if npc:
            s.add_argument('npc')
        if entry:
            s.add_argument('--entry', help='id of the story or Director entry that shows it')
            s.add_argument('--why')
        return s

    cmd('init', npc=False, entry=False)
    s = cmd('add')
    s.add_argument('--name')
    s.add_argument('--age', type=int)
    s.add_argument('--look')
    s.add_argument('--alias', nargs='*', default=[])
    s.add_argument('--threads', nargs='*', help='the game-master thread ids this character knows (replaces the list)')
    s.add_argument('--baseline', nargs='*', default=[], metavar='FIELD=N',
                   help='affect levels they settle back to: ' + ', '.join(AFFECT_LEVELS))
    s = cmd('world', npc=False)
    s.add_argument('fact', nargs='?')
    s.add_argument('--visibility', choices=VISIBILITY)
    s.add_argument('--witnesses', nargs='*', default=[])
    s.add_argument('--audit', action='store_true')
    s = cmd('know')
    s.add_argument('fact')
    s.add_argument('--how', required=True)
    s.add_argument('--confidence', required=True, choices=CONFIDENCE)
    s = cmd('unlearn')
    s.add_argument('fact')
    s = cmd('remember')
    s.add_argument('--text', required=True)
    s.add_argument('--salience', type=int, default=3)
    s = cmd('compress')
    s.add_argument('--replace', nargs='+', type=int, required=True)
    s.add_argument('--text', required=True)
    s.add_argument('--salience', type=int, default=4)
    s = cmd('session')
    s.add_argument('--id')
    s.add_argument('--end', action='store_true')
    s.add_argument('--tier', choices=TIERS)
    s = cmd('state')
    s.add_argument('--set', nargs='+', action='append', metavar='PATH=VALUE',
                   help='affect.<level>=N, affect.mood=..., body.<field>=..., body.marks.<id>=... and '
                        'body.marks.<id>.seen_by=anyone|close|nobody|<cast ids>, desire.<field>=..., '
                        'people.<cast id|player>.trust|attraction|fear=N (0-5), .debt=N (-5 to 5), .last=..., '
                        '.thinks_knows.<fact>=knows|doesnt|unsure')
    s = cmd('believe')
    s.add_argument('--text', help='the belief, as the character holds it')
    s.add_argument('--truth', choices=TRUTH, help='whether it is so; for you, never printed in the brief')
    s.add_argument('--confidence', choices=CONFIDENCE)
    s.add_argument('--about', help='the game-master fact it concerns, if any')
    s.add_argument('--retire', type=int, metavar='SEQ', help='a belief they no longer hold (with --text, replaces it)')
    s = cmd('claim')
    s.add_argument('--to', required=True, help=f'{PLAYER} or the cast id of who was told')
    s.add_argument('--text', required=True, help='what they said, or for an omission what they kept back')
    s.add_argument('--truth', required=True, choices=TRUTH)
    s.add_argument('--kind', required=True, choices=CLAIM_KINDS)
    s.add_argument('--about', help='the game-master fact it concerns; claims about the same fact are compared')
    s = cmd('tick')
    s.add_argument('--scene-end', action='store_true', help='a scene boundary: pain and intoxication ease too')
    s = cmd('want')
    s.add_argument('--text', help='a standing want, as the character holds it')
    s.add_argument('--weight', type=int, default=3, help='1 (passing) to 5 (what their life turns on); ranks wants')
    s.add_argument('--conflict', help='what pulls against it, if anything')
    s.add_argument('--retire', type=int, metavar='SEQ', help='a want they no longer hold (with --text, replaces it)')
    s = cmd('intent')
    s.add_argument('--text', help='what they mean to do')
    s.add_argument('--horizon', choices=HORIZONS, help='now, scene (before it ends), day, or long')
    s.add_argument('--done', type=int, metavar='SEQ', help='an intent they carried out')
    s.add_argument('--drop', type=int, metavar='SEQ', help='an intent they let go')
    s = cmd('veto')
    s.add_argument('--kind', required=True, choices=VETO_KINDS, help='what the DECIDES you could not honour named')
    s.add_argument('--reason', required=True, help='why the story could not honour it')
    s.add_argument('--decides', help='the decision itself, as the brain gave it')
    s.add_argument('--intent', type=int, metavar='SEQ', help='an active intent this veto closes')
    s = cmd('offscreen')
    s.add_argument('--does', required=True, help='what they did off-screen (the DOES line); kept as an episode')
    s.add_argument('--salience', type=int, default=2)
    s = cmd('settings', npc=False)
    s.add_argument('--offscreen', choices=('on', 'off'), help='off-screen calls at scene boundaries (off by default)')
    s = cmd('brief', entry=False)
    s.add_argument('--scene', help='the perception-only scene file (optional with --offscreen)')
    s.add_argument('--as', dest='alias')
    s.add_argument('--offscreen', action='store_true',
                   help='the off-screen call at a scene boundary: adds their routine, answers DOES/LEAVES/DECIDES/CHANGES')
    s.add_argument('--text', action='store_true', help='print the brief alone, not wrapped in JSON')
    s = sub.add_parser('view')
    s.add_argument('npc', nargs='?')
    cmd('check', npc=False, entry=False)
    s = cmd('migrate', npc=False, entry=False)
    s.add_argument('--entry', help='the entry the migrated memories cite (default: the last story entry)')
    s = cmd('reconcile', npc=False, entry=False)
    s.add_argument('--apply', action='store_true', help='set the events aside; without it, only list them')
    return p


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    args = parser().parse_args()
    try:
        result, warns = COMMANDS[args.cmd](args)
    except Fail as exc:
        print(json.dumps({'ok': False, 'command': args.cmd, 'error': str(exc)}, ensure_ascii=False))
        sys.exit(2)
    if result is None:  # brief --text already wrote the brief
        sys.exit(0)
    print(json.dumps({'ok': True, 'command': args.cmd, **result, 'warnings': warns}, ensure_ascii=False))
    sys.exit(1 if warns else 0)


if __name__ == '__main__':
    main()
