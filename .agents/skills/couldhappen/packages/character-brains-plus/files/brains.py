"""Character brains plus: each character's brief is built only from what that character could know.

Usage (from the workspace root):  python tools/brains.py <command> [--root .]
  init                                 create notes/brains/events.jsonl (safe to repeat)
  add <npc> [--name N] [--age N] [--look T] [--alias A ...] [--threads T ...]
                                       record a character's identity and snapshot their game-master card
  world <fact> --visibility public|witnessed|private|secret [--witnesses N ...]
                                       classify a game-master fact for the brains
  world --audit                        list game-master facts no brain classification covers yet
  know <npc> <fact> --how "I ..." --confidence certain|probable|suspects|doubts --entry E
                                       the character learned a fact, and how (first person)
  unlearn <npc> <fact> --entry E --why W   the character no longer holds a fact
  remember <npc> --text T [--salience 1-5] --entry E   an episode the character keeps
  compress <npc> --replace SEQ ... --text T [--salience 1-5]   fold episodes into one summary
  session <npc> (--id ID | --end) [--tier persistent|ephemeral]   the kept subagent session
  brief <npc> --scene FILE [--as ALIAS] [--text]   the only way to build a brain's brief
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
to BRIEF_SECTIONS."""
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
SETUP_OPS = ('char', 'world', 'session', 'compress')  # the only ops whose entry may be null
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
ANSWER_KEYS = ('NOTICES', 'WANTS', 'HIDES', 'SAYS', 'DOES', 'TELL', 'DECIDES')
ANSWER_HELP = {
    'NOTICES': 'the one thing they notice first',
    'WANTS': 'what they want in this moment',
    'HIDES': 'what they will not show',
    'SAYS': 'one to three short lines, in their voice, as they would actually say them, or (nothing)',
    'DOES': 'one physical action',
    'TELL': 'one involuntary detail a careful observer would catch',
    'DECIDES': 'a lasting intention they form now (to leave, to refuse, to do something later), or (none)'}
CONFIDENCE_WORDS = {'certain': '', 'probable': 'probably', 'suspects': 'you suspect this',
                    'doubts': 'you doubt this'}


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
    return {'chars': {}, 'world': {}, 'knows': {}, 'unlearned': {}, 'episodes': {}}


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


VALIDATE = {'char': v_char, 'world': v_world, 'know': v_know, 'unlearn': v_unlearn,
            'remember': v_remember, 'compress': v_compress, 'session': v_session}


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


FOLD = {'char': f_char, 'world': f_world, 'know': f_know, 'unlearn': f_unlearn,
        'remember': f_remember, 'compress': f_compress, 'session': f_session}


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
    if sit.get('location'):
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


def sec_now(b, npc, ctx):
    sit = b.gm_state['situation']
    when = ', '.join(x for x in (f'day {sit["day"]}' if sit.get('day') else '', sit.get('time', ''),
                                 sit.get('location', '')) if x)
    lines = ['NOW'] + ([when] if when else [])
    return lines + ctx['scene']


def sec_answer(b, npc, ctx):
    return ['ANSWER'] + [f'{k}: {ANSWER_HELP[k]}' for k in ANSWER_KEYS]


BRIEF_SECTIONS = [sec_header, sec_who, sec_memory, sec_owed, sec_knows, sec_now, sec_answer]


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


def build_brief(b, npc, scene_file, alias=None):
    need_char(b.state, npc)
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
    ctx = {'as': alias, 'scene': read_scene(scene_file)}
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
    return '\n'.join(out) + '\n'


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
            warns.append(f'{name}: the Desire line is kept only in the legacy copy; this version has no place for it yet')
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


def cmd_brief(args):
    b = Brains(args.root)
    text = build_brief(b, args.npc, args.scene, args.alias)
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
            'view': cmd_view, 'check': cmd_check, 'migrate': cmd_migrate, 'reconcile': cmd_reconcile}


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
    s = cmd('brief', entry=False)
    s.add_argument('--scene', required=True)
    s.add_argument('--as', dest='alias')
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
