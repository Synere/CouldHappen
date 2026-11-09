"""Game-master continuity state for the writer. Private notes only; nothing here is public.

Usage (from the workspace root):  python tools/gm_state.py <command> [--root .]
  init                       create notes/gm/ (safe to repeat)
  check [--file F] [--prose F]   validate the pending delta (default notes/gm/pending.json);
                             --prose scans a draft for the contract's banned terms
  commit                     validate again, require the cited entry to exist, then append it
  discard                    delete the pending delta
  state [--live]             print the current state as JSON (--live leaves out finished records)
  hot [--about X ...] [--budget N]   print the compact context to read each turn
  schema                     list every kind, op and field (use "id": "auto" for the next free id)
  layers [--on N ...] [--off N ...]   show or switch the five layers (1 continuity is always on)
  boundary                   scene-boundary checklist: is the scene done, pacing, what is owed
  review                     chapter/session report: stale threads, overdue promises, what to retire
  reconcile [--apply]        find deltas whose entry was withdrawn (Director Undo) and set them aside

State is never edited directly. It is the replay of notes/gm/deltas.jsonl, an append-only log in
which every delta cites the story or Director entry that justifies it. Stdlib only; no network.
Kinds: contract, situation, fact (phase 1); thread (phase 2); pressure, npc (phase 3); revelation (phase 4); scene (phase 5). Later phases add handlers in apply_op."""
import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

FACT_STATUS = ('established', 'rumour', 'provisional', 'outdated', 'discarded')
TERMINAL_FACT = ('outdated', 'discarded')
SOURCES = ('story', 'player', 'director', 'card')
TRANSITIONS = {'provisional': {'established', 'rumour', 'outdated', 'discarded'},
               'rumour': {'established', 'outdated'},
               'established': {'outdated'},
               'outdated': set(), 'discarded': set()}
THREAD_TYPES = ('promise', 'mystery', 'consequence', 'relationship', 'callback', 'question')
THREAD_STATUS = ('open', 'active', 'dormant', 'resolved', 'discarded')
THREAD_LIVE = ('open', 'active', 'dormant')
THREAD_MOVES = {'open': {'active', 'dormant', 'discarded'}, 'active': {'dormant'},
                'dormant': {'open', 'active', 'discarded'}}
OUTCOMES = ('fulfilled', 'broken', 'released')
STALE_SCENES = 5
PRESSURE_STATUS = ('active', 'dormant', 'resolved', 'discarded')
PRESSURE_LIVE = ('active', 'dormant')
PRESSURE_MOVES = {'active': {'dormant', 'discarded'}, 'dormant': {'active', 'discarded'}}
BASIS = ('time', 'event', 'action', 'offscreen')
PRESSURE_OUTCOMES = ('achieved', 'thwarted', 'abandoned')
NPC_STATUS = ('active', 'dormant')
REV_LIVE = ('hidden', 'partial')
IMPORTANCE = ('required', 'optional')
GOOD_ROUTES = 3
MODES = ('discovery', 'social', 'action', 'reflection', 'exploration', 'other')
SAME_MODE_RUN, DISCONNECTED_RUN = 4, 3
SCENE_FIELDS = {'mode': str, 'agenda': str, 'exit_condition': str, 'tension': int, 'participants': list,
                'serves': list, 'resolved': bool}
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
ENTRY_START = re.compile(r'^<!-- couldhappen:entry (\{.*\}) -->$')
ENTRY_END = '<!-- couldhappen:end -->'
MAX_TEXT, MAX_LIST, MAX_OPS = 300, 20, 12

CONTRACT_FIELDS = {'genre': str, 'tone': str, 'boundaries': list, 'banned_terms': list,
                   'promises': list, 'wants': list}
SITUATION_FIELDS = {'day': int, 'time': str, 'location': str, 'present': list,
                    'problem': str, 'scene': str}
FACT_FIELDS = {'text': str, 'status': str, 'source': str, 'known': bool, 'tags': list, 'pin': bool}
THREAD_FIELDS = {'type': str, 'text': str, 'status': str, 'due_condition': str, 'due_day': int,
                 'tags': list}
PRESSURE_FIELDS = {'actor': str, 'goal': str, 'next_action': str, 'trigger': str, 'consequence': str,
                   'clock_max': int, 'status': str, 'tags': list, 'stages': list}
NPC_FIELDS = {'name': str, 'want': str, 'fear': str, 'secret': str, 'voice': str, 'attitude': str,
              'status': str, 'tags': list}


def typed(value, kind):
    if kind is int:
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if kind is bool:
        return isinstance(value, bool)
    if kind is list:
        return (isinstance(value, list) and len(value) <= MAX_LIST
                and all(isinstance(v, str) and 0 < len(v) <= MAX_TEXT for v in value))
    return isinstance(value, str) and 0 < len(value) <= MAX_TEXT


def new_state():
    return {'contract': {}, 'situation': {}, 'max_day': 0, 'scene_count': 0, 'facts': {},
            'threads': {}, 'pressures': {}, 'npcs': {}, 'revelations': {}, 'scenes': {},
            'scene_order': [], 'open_scene': None, 'seen': []}


OPS = {'contract': ['set'], 'situation': ['set'], 'fact': ['add', 'update', 'replace'],
       'thread': ['add', 'update', 'resolve'], 'pressure': ['add', 'advance', 'update', 'resolve'],
       'npc': ['set'], 'revelation': ['add', 'route', 'clue', 'block', 'reveal', 'update', 'discard'],
       'scene': ['open', 'update', 'close']}
AUTO_PREFIX = {('fact', 'add'): ('F', 'facts'), ('thread', 'add'): ('T', 'threads'),
               ('pressure', 'add'): ('P', 'pressures'), ('revelation', 'add'): ('V', 'revelations'),
               ('scene', 'open'): ('s', 'scenes'), ('fact', 'replace'): ('F', 'facts')}
LONG_FACT = 180


def resolve_auto(state, delta):
    """Replace "id": "auto" (and "new": "auto" for replace) with the next free id. Returns the ids given."""
    given, taken = [], {}
    for op in delta.get('ops', []) if isinstance(delta, dict) and isinstance(delta.get('ops'), list) else []:
        if not isinstance(op, dict):
            continue
        prefix = AUTO_PREFIX.get((op.get('kind'), op.get('op')))
        key = 'new' if op.get('op') == 'replace' else 'id'
        if prefix and op.get(key) == 'auto':
            letter, coll = prefix
            used = [int(k[len(letter):]) for k in list(state[coll]) + taken.setdefault(coll, [])
                    if k.startswith(letter) and k[len(letter):].isdigit()]
            op[key] = f'{letter}{max(used, default=0) + 1}'
            taken[coll].append(op[key])
            given.append(op[key])
    return given


def schema_text():
    lines = ['Every delta: {"entry": "<uuid of the entry that shows it>", "why": "<what happened>", "ops": [...]}',
             'Give "id": "auto" on a fact, thread, pressure, revelation or scene to get the next free id.',
             f'Texts are at most {MAX_TEXT} characters; lists at most {MAX_LIST} items; at most {MAX_OPS} ops.', '']
    spec = {
        ('contract', 'set'): 'fields: ' + ', '.join(CONTRACT_FIELDS),
        ('situation', 'set'): 'fields: ' + ', '.join(SITUATION_FIELDS) + '; flashback',
        ('fact', 'add'): 'id, ' + ', '.join(FACT_FIELDS) + ' (status, text and source required)',
        ('fact', 'update'): 'id, reason, ' + ', '.join(set(FACT_FIELDS) - {'source'}),
        ('fact', 'replace'): 'id, new, reason, text, ' + ', '.join(set(FACT_FIELDS) - {'status', 'text'}),
        ('thread', 'add'): 'id, ' + ', '.join(THREAD_FIELDS) + f' (type: {"|".join(THREAD_TYPES)})',
        ('thread', 'update'): 'id, reason, touch, ' + ', '.join(set(THREAD_FIELDS) - {'type'}),
        ('thread', 'resolve'): 'id, resolution, outcome (promises: ' + '|'.join(OUTCOMES) + ')',
        ('pressure', 'add'): 'id, ' + ', '.join(PRESSURE_FIELDS) + ' (actor, goal, next_action, trigger required; '
                             'stages need clock_max, at most one per step)',
        ('pressure', 'advance'): f'id, basis ({"|".join(BASIS)}), reason, steps (negative for a setback), evidence, next_action',
        ('pressure', 'update'): 'id, reason, touch, ' + ', '.join(set(PRESSURE_FIELDS) - {'actor', 'clock_max'}),
        ('pressure', 'resolve'): f'id, resolution, outcome ({"|".join(PRESSURE_OUTCOMES)})',
        ('npc', 'set'): 'id, fields: ' + ', '.join(NPC_FIELDS) + ' (name required for a new one; this is also how to update)',
        ('revelation', 'add'): f'id, fact, importance ({"|".join(IMPORTANCE)}), tags',
        ('revelation', 'route'): 'id, route, how, where',
        ('revelation', 'clue'): 'id, route, reason', ('revelation', 'block'): 'id, route, reason',
        ('revelation', 'reveal'): 'id, how, route (its fact must be established)', ('revelation', 'update'): 'id, reason, fact, importance, tags',
        ('revelation', 'discard'): 'id, reason',
        ('scene', 'open'): f'id, mode ({"|".join(MODES)}), agenda, exit_condition, tension 0-5, participants, serves',
        ('scene', 'update'): 'id, resolved, ' + ', '.join(set(SCENE_FIELDS) - {'resolved'}),
        ('scene', 'close'): 'id, outcome'}
    for kind, verbs in OPS.items():
        lines.append(f'{kind} (layer {KIND_LAYER[kind]}):')
        lines += [f'  {{"op": "{v}", "kind": "{kind}", {spec[(kind, v)]}}}' for v in verbs]
    return '\n'.join(lines)


# ---- applying one delta -------------------------------------------------------------------

def fields_ok(fields, spec, bad):
    if not isinstance(fields, dict) or not fields:
        bad('fields must be a non-empty object')
        return False
    ok = True
    for key, value in fields.items():
        if key not in spec:
            bad(f'unknown field {key} (allowed: {", ".join(sorted(spec))})')
            ok = False
        elif not typed(value, spec[key]):
            bad(f'field {key} must be ' + why_untyped(value, spec[key]))
            ok = False
    return ok


def why_untyped(value, kind):
    if kind is int:
        return 'a whole number, 0 or more'
    if kind is bool:
        return 'true or false'
    if kind is list:
        if not isinstance(value, list):
            return f'a list of short texts (up to {MAX_LIST} items)'
        return f'a list of {MAX_LIST} or fewer non-empty texts of at most {MAX_TEXT} characters'
    if not isinstance(value, str) or not value:
        return 'a non-empty text'
    return f'at most {MAX_TEXT} characters (this one is {len(value)}); keep one durable idea per record'


def keys_ok(op, allowed, bad):
    extra = set(op) - allowed
    if extra:
        bad('unknown keys: ' + ', '.join(sorted(extra)) + ' (allowed: ' + ', '.join(sorted(allowed)) + ')')
    return not extra


def need(op, name, bad):
    if not op.get(name):
        bad(f'{name} is required')
        return False
    return True


def reason_ok(op, bad, why):
    reason = op.get('reason')
    if not (isinstance(reason, str) and len(reason.strip()) >= 5):
        bad(f'{why} needs a reason (at least 5 characters saying what happened)')
        return False
    return True


def apply_op(state, op, errs, warns, ctx):
    kind, verb = op.get('kind'), op.get('op')

    def bad(msg):
        errs.append(f'{kind}/{verb}: {msg}')

    if kind == 'contract' and verb == 'set':
        if keys_ok(op, {'op', 'kind', 'fields'}, bad) and fields_ok(op.get('fields'), CONTRACT_FIELDS, bad):
            state['contract'].update(op['fields'])
    elif kind == 'situation' and verb == 'set':
        if not (keys_ok(op, {'op', 'kind', 'fields', 'flashback'}, bad)
                and fields_ok(op.get('fields'), SITUATION_FIELDS, bad)):
            return
        flashback = op.get('flashback', False)
        if not isinstance(flashback, bool):
            bad('flashback must be true or false')
            return
        day = op['fields'].get('day')
        if day is not None and not flashback and day < state['max_day']:
            bad(f'day {day} is before day {state["max_day"]}; set flashback: true if this is deliberately in the past')
            return
        scene = op['fields'].get('scene')
        if scene and scene != state['situation'].get('scene') and not flashback:
            state['scene_count'] += 1
        state['situation'].update(op['fields'])
        if day is not None and not flashback:
            state['max_day'] = day
    elif kind == 'fact' and verb == 'add':
        apply_add(state, op, bad, warns)
    elif kind == 'fact' and verb == 'update':
        apply_update(state, op, bad, warns, ctx)
    elif kind == 'fact' and verb == 'replace':
        apply_replace(state, op, bad, warns, ctx)
    elif kind == 'thread' and verb == 'add':
        thread_add(state, op, bad, warns, ctx)
    elif kind == 'thread' and verb == 'update':
        thread_update(state, op, bad)
    elif kind == 'thread' and verb == 'resolve':
        thread_resolve(state, op, bad, ctx)
    elif kind == 'pressure' and verb == 'add':
        pressure_add(state, op, bad, warns, ctx)
    elif kind == 'pressure' and verb == 'advance':
        pressure_advance(state, op, bad, warns)
    elif kind == 'pressure' and verb == 'update':
        pressure_update(state, op, bad)
    elif kind == 'pressure' and verb == 'resolve':
        pressure_resolve(state, op, bad)
    elif kind == 'npc' and verb == 'set':
        npc_set(state, op, bad)
    elif kind == 'revelation' and verb in REV_VERBS:
        REV_VERBS[verb](state, op, bad, ctx)
    elif kind == 'scene' and verb in SCENE_VERBS:
        SCENE_VERBS[verb](state, op, bad, ctx)
    else:
        if kind in OPS:
            bad(f'"{verb}" is not an op for {kind}; use one of: {", ".join(OPS[kind])} (python tools/gm_state.py schema)')
        else:
            bad(f'unknown kind "{kind}"; use one of: {", ".join(OPS)} (python tools/gm_state.py schema)')


def fact_id(op, name, bad):
    value = op.get(name)
    if not (isinstance(value, str) and ID_RE.match(value)):
        bad(f'{name} must be an id like F12 (letters, digits, - and _; at most 32 characters)')
        return None
    return value


PROVISIONAL_KNOWN = ('{fid} is provisional but marked known to the player{default}: an idea not yet shown cannot be '
                     'known. Set known: false; if the protagonist has heard it said, it is a rumour.')


def truth_of(state, fid):
    """The id of the live revelation whose hidden truth is fid, or None. It also sees revelations of a
    switched-off layer 4 (load keeps their links in 'hidden_truths'), so switching the layer off is never a
    way round the rules that protect a hidden truth."""
    for r in state['revelations'].values():
        if r['fact'] == fid and r['status'] in REV_LIVE:
            return r['id']
    return state.get('hidden_truths', {}).get(fid)


def apply_add(state, op, bad, warns):
    if not keys_ok(op, {'op', 'kind', 'id'} | set(FACT_FIELDS), bad):
        return
    fid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in FACT_FIELDS}
    if not fid or not fields_ok(fields, FACT_FIELDS, bad):
        return
    if fid in state['facts']:
        return bad(f'{fid} already exists')
    for name in ('text', 'status', 'source'):
        if name not in fields:
            return bad(f'{name} is required')
    if fields['status'] not in FACT_STATUS or fields['status'] in TERMINAL_FACT:
        return bad('status must be established, rumour or provisional (state it explicitly; nothing is assumed true)')
    if fields['source'] not in SOURCES:
        return bad('source must be one of ' + ', '.join(SOURCES))
    fact = {'id': fid, 'known': True, 'tags': [], 'pin': False, **fields}
    state['facts'][fid] = fact
    if not fact['tags'] and not fact['pin']:
        warns.append(f'{fid} has no tags and is not pinned: it will not appear in the hot context. Add tags (names, places).')
    if fact['status'] == 'provisional' and fact['known']:
        warns.append(PROVISIONAL_KNOWN.format(fid=fid, default='' if 'known' in fields else ' (the default)'))
    if len(fact['text']) > LONG_FACT:
        warns.append(f'{fid} is {len(fact["text"])} characters. A fact is one lasting truth, not a summary of the turn: '
                     'the story already holds what happened. Keep only what must stay true, and split the rest.')


def apply_update(state, op, bad, warns, ctx):
    allowed = {'op', 'kind', 'id', 'reason'} | (set(FACT_FIELDS) - {'source'})
    if not keys_ok(op, allowed, bad):
        return
    fid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in FACT_FIELDS}
    if not fid or not fields_ok(fields, FACT_FIELDS, bad):
        return
    fact = state['facts'].get(fid)
    if not fact:
        return bad(f'{fid} does not exist')
    if fact['status'] in TERMINAL_FACT:
        return bad(f'{fid} is {fact["status"]} and cannot change')
    new_status = fields.get('status')
    if new_status and new_status != fact['status']:
        if new_status not in TRANSITIONS[fact['status']]:
            return bad(f'{fid}: {fact["status"]} cannot become {new_status}')
        if not reason_ok(op, bad, f'{fid} becoming {new_status}'):
            return
    if 'text' in fields and fields['text'] != fact['text']:
        if fact['status'] == 'established':
            return bad(f'{fid} is established; its text cannot be edited. Use replace, with a reason.')
        if not reason_ok(op, bad, f'changing the text of {fid}'):
            return
    if fields.get('known') is False and fact['known']:
        return bad(f'{fid} is already known to the player and cannot become hidden')
    rid = truth_of(state, fid)
    if ctx.get('strict') and rid:
        if fields.get('known') is True and not fact['known']:
            return bad(f'{fid} is the hidden truth of {rid}: use reveal on {rid} (with how) to make it known')
        if new_status == 'rumour':
            return bad(f'{fid} is the hidden truth of {rid}; a truth cannot become a rumour. Discard or relink '
                       f'{rid} first, or add the rumour as its own fact')
    fact.update(fields)
    if fact['status'] == 'provisional' and fact['known'] and fields.get('known') is True:
        warns.append(PROVISIONAL_KNOWN.format(fid=fid, default=''))


def apply_replace(state, op, bad, warns, ctx):
    allowed = {'op', 'kind', 'id', 'new', 'reason'} | (set(FACT_FIELDS) - {'status'})
    if not keys_ok(op, allowed, bad):
        return
    old_id, new_id = fact_id(op, 'id', bad), fact_id(op, 'new', bad)
    fields = {k: v for k, v in op.items() if k in FACT_FIELDS}
    if not old_id or not new_id or not fields_ok(fields, FACT_FIELDS, bad):
        return
    old = state['facts'].get(old_id)
    if not old or old['status'] in TERMINAL_FACT:
        return bad(f'{old_id} must exist and not already be outdated or discarded')
    if new_id in state['facts']:
        return bad(f'{new_id} already exists')
    if 'text' not in fields:
        return bad('text is required')
    if not reason_ok(op, bad, f'replacing {old_id}'):
        return
    if ctx.get('strict') and 'known' in fields and fields['known'] != old['known']:
        if old['known']:
            return bad(f'{old_id} is known to the player; its replacement cannot be hidden')
        rid = truth_of(state, old_id)
        if rid:
            return bad(f'{old_id} is the hidden truth of {rid}: replace it hidden and relink {rid}, '
                       'then reveal it when the page shows it')
    old['status'], old['replaced_by'] = 'outdated', new_id
    fact = {'id': new_id, 'known': old['known'], 'tags': old['tags'], 'pin': old['pin'],
            'source': 'story', **fields, 'status': 'established', 'replaces': old_id}
    state['facts'][new_id] = fact


def later(entries, first, second):
    """True unless both entries are in the same log and `second` does not come after `first`."""
    a, b = (entries or {}).get(first), (entries or {}).get(second)
    if a and b and a['channel'] == b['channel']:
        return b['pos'] > a['pos']
    return True


def thread_add(state, op, bad, warns, ctx):
    if not keys_ok(op, {'op', 'kind', 'id'} | set(THREAD_FIELDS), bad):
        return
    tid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in THREAD_FIELDS}
    if not tid or not fields_ok(fields, THREAD_FIELDS, bad):
        return
    if tid in state['threads']:
        return bad(f'{tid} already exists')
    for name in ('type', 'text'):
        if name not in fields:
            return bad(f'{name} is required')
    if fields['type'] not in THREAD_TYPES:
        return bad('type must be one of ' + ', '.join(THREAD_TYPES))
    if fields.setdefault('status', 'open') not in ('open', 'active'):
        return bad('a new thread starts open or active')
    if fields.get('due_day', state['max_day']) < state['max_day']:
        return bad(f'due_day {fields["due_day"]} is already past (it is day {state["max_day"]})')
    state['threads'][tid] = {'id': tid, 'due_condition': '', 'due_day': None, 'tags': [], **fields,
                             'origin': ctx['entry'], 'touched': state['scene_count'],
                             'resolution': None, 'outcome': None}
    if not state['threads'][tid]['tags']:
        warns.append(f'{tid} has no tags: it will show in the hot context only while overdue or if it is a '
                     'promise or consequence.')


def thread_update(state, op, bad):
    allowed = {'op', 'kind', 'id', 'reason', 'touch'} | (set(THREAD_FIELDS) - {'type'})
    if not keys_ok(op, allowed, bad):
        return
    tid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in THREAD_FIELDS}
    touch = op.get('touch', False)
    if not tid or (fields and not fields_ok(fields, THREAD_FIELDS, bad)):
        return
    if not isinstance(touch, bool):
        return bad('touch must be true or false')
    if not fields and not touch:
        return bad('nothing to change; use touch: true to record that the thread advanced')
    thread = state['threads'].get(tid)
    if not thread:
        return bad(f'{tid} does not exist')
    if thread['status'] not in THREAD_LIVE:
        return bad(f'{tid} is {thread["status"]} and cannot change')
    new_status = fields.pop('status', None)
    if new_status and new_status != thread['status']:
        if new_status not in THREAD_MOVES[thread['status']]:
            return bad(f'{tid}: {thread["status"]} cannot become {new_status}'
                       + ('; use resolve to finish a thread' if new_status == 'resolved' else ''))
        if not reason_ok(op, bad, f'{tid} becoming {new_status}'):
            return
        thread['status'] = new_status
    if fields.get('due_day', state['max_day']) < state['max_day']:
        return bad(f'due_day {fields["due_day"]} is already past (it is day {state["max_day"]})')
    thread.update(fields)
    thread['touched'] = state['scene_count']


def thread_resolve(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'resolution', 'outcome'}, bad):
        return
    tid = fact_id(op, 'id', bad)
    thread = state['threads'].get(tid) if tid else None
    if not thread:
        return bad(f'{tid} does not exist')
    if thread['status'] not in THREAD_LIVE:
        return bad(f'{tid} is already {thread["status"]}')
    resolution, outcome = op.get('resolution'), op.get('outcome')
    if not (typed(resolution, str) and len(resolution.strip()) >= 5):
        return bad('resolution must say what happened (at least 5 characters)')
    if thread['type'] == 'promise':
        if outcome not in OUTCOMES:
            return bad('a promise needs an outcome: ' + ', '.join(OUTCOMES))
        if ctx['entry'] == thread['origin']:
            return bad('a promise cannot be resolved in the same entry that made it')
        if not later(ctx.get('entries'), thread['origin'], ctx['entry']):
            return bad('the cited entry must come after the one that made the promise')
    elif outcome is not None:
        return bad('outcome is only for promises')
    thread.update(status='resolved', resolution=resolution, outcome=outcome, resolved_entry=ctx['entry'],
                  touched=state['scene_count'])


def pressure_add(state, op, bad, warns, ctx):
    if not keys_ok(op, {'op', 'kind', 'id'} | set(PRESSURE_FIELDS), bad):
        return
    pid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in PRESSURE_FIELDS}
    if not pid or not fields_ok(fields, PRESSURE_FIELDS, bad):
        return
    if pid in state['pressures']:
        return bad(f'{pid} already exists')
    for name in ('actor', 'goal', 'next_action', 'trigger'):
        if name not in fields:
            return bad(f'{name} is required (who, what they want, what they do next, what makes them move)')
    if fields.setdefault('status', 'active') not in PRESSURE_LIVE:
        return bad('a new pressure starts active or dormant')
    if 'clock_max' in fields and not 2 <= fields['clock_max'] <= 12:
        return bad('clock_max must be between 2 and 12')
    if not stages_ok(fields.get('stages'), fields.get('clock_max'), bad):
        return
    state['pressures'][pid] = {'id': pid, 'consequence': '', 'clock_max': None, 'tags': [], 'stages': [], **fields,
                               'clock': 0, 'origin': ctx['entry'], 'last_moved': state['scene_count'],
                               'evidence': None, 'resolution': None, 'outcome': None}
    if not state['pressures'][pid]['tags']:
        warns.append(f'{pid} has no tags: it will show in full only when its clock is full.')


def stages_ok(stages, clock_max, bad):
    """Stage n says what the clock reaching n means; there is at most one per step."""
    if stages and not clock_max:
        bad('stages need a clock: set clock_max, one stage per step at most')
        return False
    if stages and len(stages) > clock_max:
        bad(f'{len(stages)} stages for a clock of {clock_max}: at most one stage per step')
        return False
    return True


def stage_note(p):
    """' | reached: ... | next stage: ...' for a pressure with stages, else ''."""
    stages, clock = p.get('stages') or [], p['clock']
    parts = []
    if 0 < clock <= len(stages):
        parts.append(f'reached: {stages[clock - 1]}')
    if clock < len(stages):
        parts.append(f'next stage: {stages[clock]}')
    return ''.join(' | ' + x for x in parts)


def live_pressure(state, op, bad, name='id'):
    pid = fact_id(op, name, bad)
    pressure = state['pressures'].get(pid) if pid else None
    if not pressure:
        bad(f'{pid} does not exist')
    elif pressure['status'] not in PRESSURE_LIVE:
        bad(f'{pid} is {pressure["status"]} and cannot change')
        return None
    return pressure


def pressure_advance(state, op, bad, warns):
    if not keys_ok(op, {'op', 'kind', 'id', 'steps', 'basis', 'evidence', 'reason', 'next_action'}, bad):
        return
    pressure = live_pressure(state, op, bad)
    if not pressure:
        return
    if pressure['status'] != 'active':
        return bad(f'{pressure["id"]} is dormant; wake it first (update status: active, with a reason)')
    basis = op.get('basis')
    if basis not in BASIS:
        return bad('basis must say why it moves: ' + ', '.join(BASIS))
    if not reason_ok(op, bad, f'advancing {pressure["id"]}'):
        return
    evidence = op.get('evidence')
    if basis == 'offscreen' and not (typed(evidence, str) and len(evidence.strip()) >= 5):
        return bad('an off-screen move needs evidence: what the protagonist could later observe')
    if evidence is not None and not typed(evidence, str):
        return bad('evidence must be a short text')
    steps = op.get('steps', 1 if pressure['clock_max'] else 0)
    if not (isinstance(steps, int) and not isinstance(steps, bool)):
        return bad('steps must be a whole number (negative for a setback)')
    if steps and not pressure['clock_max']:
        return bad(f'{pressure["id"]} has no clock; omit steps')
    if pressure['clock_max'] and pressure['clock'] + steps > pressure['clock_max']:
        return bad(f'{pressure["id"]} clock is {pressure["clock"]}/{pressure["clock_max"]}; {steps} more step(s) would overflow it')
    if pressure['clock'] + steps < 0:
        return bad(f'{pressure["id"]} clock is {pressure["clock"]}/{pressure["clock_max"]}; it cannot lose {-steps} step(s)')
    if 'next_action' in op:
        if not typed(op['next_action'], str):
            return bad('next_action must be a short text')
        pressure['next_action'] = op['next_action']
    if 'next_action' not in op and steps >= 0:
        warns.append(f'{pressure["id"]} advanced without a new next_action: is "{pressure["next_action"]}" still what '
                     'this actor will do, given what just happened?')
    pressure['clock'] += steps
    pressure['last_moved'] = state['scene_count']
    if evidence:
        pressure['evidence'] = evidence
    if pressure['clock_max'] and pressure['clock'] == pressure['clock_max']:
        warns.append(f'{pressure["id"]} clock is full: let the consequence land, or resolve it as thwarted.')


def pressure_update(state, op, bad):
    allowed = {'op', 'kind', 'id', 'reason', 'touch'} | (set(PRESSURE_FIELDS) - {'actor', 'clock_max'})
    if not keys_ok(op, allowed, bad):
        return
    fields = {k: v for k, v in op.items() if k in PRESSURE_FIELDS}
    touch = op.get('touch', False)
    if fields and not fields_ok(fields, PRESSURE_FIELDS, bad):
        return
    if not isinstance(touch, bool):
        return bad('touch must be true or false')
    if not fields and not touch:
        return bad('nothing to change')
    pressure = live_pressure(state, op, bad)
    if not pressure:
        return
    if 'stages' in fields and not stages_ok(fields['stages'], pressure['clock_max'], bad):
        return
    new_status = fields.pop('status', None)
    if new_status and new_status != pressure['status']:
        if new_status not in PRESSURE_MOVES[pressure['status']]:
            return bad(f'{pressure["id"]}: {pressure["status"]} cannot become {new_status}'
                       + ('; use resolve to finish one' if new_status == 'resolved' else ''))
        if not reason_ok(op, bad, f'{pressure["id"]} becoming {new_status}'):
            return
        pressure['status'] = new_status
    pressure.update(fields)
    if touch and pressure['status'] == 'active':
        pressure['last_moved'] = state['scene_count']


def pressure_resolve(state, op, bad):
    if not keys_ok(op, {'op', 'kind', 'id', 'resolution', 'outcome'}, bad):
        return
    pressure = live_pressure(state, op, bad)
    if not pressure:
        return
    resolution = op.get('resolution')
    if not (typed(resolution, str) and len(resolution.strip()) >= 5):
        return bad('resolution must say what happened (at least 5 characters)')
    if op.get('outcome') not in PRESSURE_OUTCOMES:
        return bad('outcome must be one of ' + ', '.join(PRESSURE_OUTCOMES))
    pressure.update(status='resolved', resolution=resolution, outcome=op['outcome'])


def npc_set(state, op, bad):
    if not keys_ok(op, {'op', 'kind', 'id', 'fields'}, bad):
        return
    nid = fact_id(op, 'id', bad)
    fields = op.get('fields')
    if not nid or not fields_ok(fields, NPC_FIELDS, bad):
        return
    if fields.get('status', 'active') not in NPC_STATUS:
        return bad('status must be active or dormant')
    npc = state['npcs'].get(nid)
    if not npc:
        if 'name' not in fields:
            return bad(f'{nid} is new: name is required')
        npc = state['npcs'][nid] = {'id': nid, 'status': 'active', 'tags': []}
    npc.update(fields)


def rev_get(state, op, bad):
    rid = fact_id(op, 'id', bad)
    rev = state['revelations'].get(rid) if rid else None
    if not rev:
        bad(f'{rid} does not exist')
    elif rev['status'] not in REV_LIVE:
        bad(f'{rid} is {rev["status"]} and cannot change')
        return None
    return rev


def rev_route_of(rev, op, bad, statuses):
    route = rev['routes'].get(op.get('route'))
    if not route:
        bad(f'{rev["id"]} has no route {op.get("route")}')
    elif route['status'] not in statuses:
        bad(f'route {route["id"]} is {route["status"]}')
        return None
    return route


def rev_add(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'fact', 'importance', 'tags'}, bad):
        return
    rid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in ('fact', 'importance', 'tags')}
    if not rid or not fields_ok(fields, {'fact': str, 'importance': str, 'tags': list}, bad):
        return
    if rid in state['revelations']:
        return bad(f'{rid} already exists')
    for name in ('fact', 'importance'):
        if name not in fields:
            return bad(f'{name} is required')
    if fields['importance'] not in IMPORTANCE:
        return bad('importance must be required or optional')
    fact = state['facts'].get(fields['fact'])
    if not fact or fact['status'] in TERMINAL_FACT:
        return bad(f'fact {fields["fact"]} must exist and not be outdated or discarded')
    if ctx.get('strict') and fact['status'] == 'rumour':
        return bad(f'{fact["id"]} is a rumour, which is what someone believes. Make the truth behind it its own '
                   'fact (established or provisional) and point the revelation at that')
    if fact['known']:
        return bad('the player already knows that fact; only a hidden truth (known: false) can be a revelation')
    if any(r['fact'] == fields['fact'] and r['status'] in REV_LIVE for r in state['revelations'].values()):
        return bad(f'{fields["fact"]} already has a live revelation')
    state['revelations'][rid] = {'id': rid, 'tags': [], **fields, 'status': 'hidden', 'routes': {},
                                 'origin': ctx['entry'], 'revealed_entry': None, 'reveal_how': None}


def rev_route(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'route', 'how', 'where'}, bad):
        return
    rev = rev_get(state, op, bad)
    route = fact_id(op, 'route', bad)
    if not rev or not route:
        return
    if route in rev['routes']:
        return bad(f'route {route} already exists')
    for name, kind in (('how', str), ('where', str)):
        if name in op and not typed(op[name], kind):
            return bad(f'{name} must be a short text')
    if 'how' not in op:
        return bad('how is required: the way the player could find this out')
    rev['routes'][route] = {'id': route, 'how': op['how'], 'where': op.get('where', ''), 'status': 'open'}


def rev_clue(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'route', 'reason'}, bad):
        return
    rev = rev_get(state, op, bad)
    route = rev and rev_route_of(rev, op, bad, ('open',))
    if route and reason_ok(op, bad, f'marking route {route["id"]} used'):
        route['status'] = 'used'
        rev['status'] = 'partial'


def rev_block(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'route', 'reason'}, bad):
        return
    rev = rev_get(state, op, bad)
    route = rev and rev_route_of(rev, op, bad, ('open',))
    if route and reason_ok(op, bad, f'blocking route {route["id"]}'):
        route['status'] = 'blocked'


def rev_reveal(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'how', 'route'}, bad):
        return
    rev = rev_get(state, op, bad)
    if not rev:
        return
    if not (typed(op.get('how'), str) and len(op['how'].strip()) >= 5):
        return bad('how must say how the protagonist learned it (at least 5 characters)')
    fact = state['facts'].get(rev['fact'])
    if not fact or fact['status'] in TERMINAL_FACT:
        return bad(f'its fact {rev["fact"]} is outdated or discarded; relink the revelation first')
    if ctx.get('strict') and fact['status'] != 'established':
        return bad(f'its fact {fact["id"]} is {fact["status"]}, not established. A reveal shows a truth: establish it '
                   'first in this delta (fact update, status established, with a reason), or relink the revelation')
    if 'route' in op:
        route = rev_route_of(rev, op, bad, ('open', 'used'))
        if not route:
            return
        route['status'] = 'used'
    fact['known'] = True
    rev.update(status='revealed', revealed_entry=ctx['entry'], reveal_how=op['how'])


def rev_update(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'fact', 'importance', 'tags', 'reason'}, bad):
        return
    rev = rev_get(state, op, bad)
    fields = {k: v for k, v in op.items() if k in ('fact', 'importance', 'tags')}
    if not rev:
        return
    if not fields:
        return bad('give at least one of fact, importance, tags')
    if not fields_ok(fields, {'fact': str, 'importance': str, 'tags': list}, bad):
        return
    if fields.get('importance', 'required') not in IMPORTANCE:
        return bad('importance must be required or optional')
    if 'fact' in fields:
        fact = state['facts'].get(fields['fact'])
        if not fact or fact['status'] in TERMINAL_FACT or fact['known']:
            return bad('the new fact must exist, be live, and still be hidden from the player')
        if ctx.get('strict') and fact['status'] == 'rumour':
            return bad(f'{fact["id"]} is a rumour; a revelation points at the truth, not at a belief')
        if ctx.get('strict') and truth_of(state, fact['id']) not in (None, rev['id']):
            return bad(f'{fact["id"]} already has a live revelation ({truth_of(state, fact["id"])})')
        if not reason_ok(op, bad, f'relinking {rev["id"]}'):
            return
    rev.update(fields)


def rev_discard(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'reason'}, bad):
        return
    rev = rev_get(state, op, bad)
    if rev and reason_ok(op, bad, f'discarding {rev["id"]}'):
        rev['status'] = 'discarded'


REV_VERBS = {'add': rev_add, 'route': rev_route, 'clue': rev_clue, 'block': rev_block,
             'reveal': rev_reveal, 'update': rev_update, 'discard': rev_discard}


def rev_warnings(state, only=None):
    """Soft rules: a required mystery should stay discoverable."""
    out = []
    for r in state['revelations'].values():
        if r['status'] not in REV_LIVE or (only is not None and r['id'] not in only):
            continue
        fact = state['facts'].get(r['fact'])
        if not fact or fact['status'] in TERMINAL_FACT:
            out.append(f'{r["id"]} points at {r["fact"]}, which is outdated or discarded: relink or discard it.')
        elif fact['status'] == 'rumour':
            out.append(f'{r["id"]} points at {r["fact"]}, a rumour: a revelation needs a truth. Relink it to a fact, '
                       'or discard it.')
        elif fact['known']:
            first = '' if fact['status'] == 'established' else 'establish it (fact update, with a reason), then '
            out.append(f'{r["id"]}: the player already knows {r["fact"]}; {first}mark it revealed (reveal) or discard it.')
        viable = sum(1 for x in r['routes'].values() if x['status'] == 'open')
        if r['importance'] == 'required':
            if viable == 0:
                out.append(f'{r["id"]} is required and has NO open route: a dead end. Add a route or reveal it.')
            elif viable < GOOD_ROUTES:
                out.append(f'{r["id"]} is required with {viable} open route(s); aim for {GOOD_ROUTES}.')
    return out


def serves_ok(state, serves, bad):
    live = {**{k: v for k, v in state['threads'].items() if v['status'] in THREAD_LIVE},
            **{k: v for k, v in state['pressures'].items() if v['status'] in PRESSURE_LIVE},
            **{k: v for k, v in state['revelations'].items() if v['status'] in REV_LIVE}}
    for item in serves:
        if item != 'want' and item not in live:
            bad(f'serves: "{item}" must be "want" or the id of a live thread, pressure or revelation')
            return False
    return True


def scene_check_fields(state, fields, bad):
    if not fields_ok(fields, SCENE_FIELDS, bad):
        return False
    if 'mode' in fields and fields['mode'] not in MODES:
        bad('mode must be one of ' + ', '.join(MODES))
        return False
    if fields.get('tension', 0) > 5:
        bad('tension is 0 to 5')
        return False
    return serves_ok(state, fields.get('serves', []), bad)


def scene_open(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id'} | (set(SCENE_FIELDS) - {'resolved'}), bad):
        return
    sid = fact_id(op, 'id', bad)
    fields = {k: v for k, v in op.items() if k in SCENE_FIELDS}
    if not sid or not scene_check_fields(state, fields, bad):
        return
    if sid in state['scenes']:
        return bad(f'{sid} already exists')
    if state['open_scene']:
        return bad(f'scene {state["open_scene"]} is still open; close it first (in the same delta is fine)')
    for name in ('mode', 'agenda', 'exit_condition'):
        if name not in fields:
            return bad(f'{name} is required (what kind of scene, what it is for, what ends it)')
    state['scenes'][sid] = {'id': sid, 'participants': [], 'serves': [], 'tension': None, **fields,
                            'resolved': False, 'status': 'open', 'origin': ctx['entry'], 'outcome': None}
    state['scene_order'].append(sid)
    state['open_scene'] = sid
    if state['situation'].get('scene') != sid:
        state['scene_count'] += 1
    state['situation']['scene'] = sid


def scene_update(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id'} | set(SCENE_FIELDS), bad):
        return
    fields = {k: v for k, v in op.items() if k in SCENE_FIELDS}
    if op.get('id') != state['open_scene']:
        return bad(f'{op.get("id")} is not the open scene ({state["open_scene"] or "none open"})')
    if not fields:
        return bad('nothing to change')
    if scene_check_fields(state, fields, bad):
        state['scenes'][op['id']].update(fields)


def scene_close(state, op, bad, ctx):
    if not keys_ok(op, {'op', 'kind', 'id', 'outcome'}, bad):
        return
    if op.get('id') != state['open_scene']:
        return bad(f'{op.get("id")} is not the open scene ({state["open_scene"] or "none open"})')
    if not (typed(op.get('outcome'), str) and len(op['outcome'].strip()) >= 5):
        return bad('outcome must say what changed (at least 5 characters)')
    scene = state['scenes'][op['id']]
    scene.update(status='closed', outcome=op['outcome'], closed_entry=ctx['entry'])
    state['open_scene'] = None


SCENE_VERBS = {'open': scene_open, 'update': scene_update, 'close': scene_close}


def scene_warnings(state):
    """Soft rules: pacing and purpose. They never force an event."""
    out, order = [], [state['scenes'][s] for s in state['scene_order']]
    now = state['scenes'].get(state['open_scene'])
    if now and now['resolved']:
        out.append(f'scene {now["id"]} has served its purpose: end it, or give it a new reason to continue '
                   '(not while the player is happily engaged).')
    recent = order[-SAME_MODE_RUN:]
    if len(recent) == SAME_MODE_RUN and len({s['mode'] for s in recent}) == 1:
        out.append(f'{SAME_MODE_RUN} scenes in a row are {recent[0]["mode"]}: vary the next unless the story needs it.')
    recent = order[-DISCONNECTED_RUN:]
    if len(recent) == DISCONNECTED_RUN and not any(s['serves'] for s in recent):
        out.append(f'{DISCONNECTED_RUN} scenes in a row serve nothing the protagonist wants or any open thread, '
                   'pressure or revelation: reconnect the next one.')
    return out


def boundary(state):
    """Scene-boundary checklist. Reads only; changes nothing."""
    out = ['# Scene boundary (private)']
    now = state['scenes'].get(state['open_scene'])
    if now:
        out.append(f'OPEN scene {now["id"]} [{now["mode"]}] agenda: {now["agenda"]} | exit: {now["exit_condition"]}'
                   + (' | PURPOSE RESOLVED' if now['resolved'] else ''))
        out.append('  Is the exit condition met? If so, close it with an outcome. If the player is engaged, keep going.')
    else:
        out.append('no scene open: open the next one (agenda, exit condition, what it serves).')
    modes = [state['scenes'][s]['mode'] for s in state['scene_order']][-6:]
    out.append('PACING recent modes: ' + (', '.join(modes) or 'none') + '; tension: '
               + (', '.join(str(state['scenes'][s]['tension']) for s in state['scene_order'][-6:]
                            if state['scenes'][s]['tension'] is not None) or 'not set'))
    unused = [m for m in MODES[:-1] if m not in modes[-3:]]
    if modes:
        out.append('  not used in the last three scenes: ' + ', '.join(unused))
    owed = thread_warnings(state) + pressure_warnings(state) + rev_warnings(state) + scene_warnings(state)
    out += ['WARN ' + w for w in owed]
    for p in state['pressures'].values():
        if p['status'] == 'active':
            out.append(f'STILL TRUE? {p["id"]} {p["actor"]} next: "{p["next_action"]}". If this scene changed it '
                       '(someone died, a plan failed), update next_action.')
    out.append('CHECK threads you advanced (touch them); pressures whose trigger was met (advance with a basis); '
               'relationships that changed (update the cast card).')
    out.append('NEXT frame a situation already in motion that needs a decision. Do not decide the player\'s response.')
    return '\n'.join(out)


def texts_of(delta):
    for op in delta.get('ops', []):
        if not isinstance(op, dict):
            continue
        yield op.get('text')
        yield op.get('resolution')
        yield op.get('due_condition')
        yield op.get('goal')
        yield op.get('agenda')
        yield op.get('exit_condition')
        yield op.get('how')
        yield op.get('where')
        yield op.get('next_action')
        yield op.get('consequence')
        fields = op.get('fields')
        if isinstance(fields, dict):
            for key, value in fields.items():
                if key != 'banned_terms':
                    yield from (value if isinstance(value, list) else [value])


def banned_in(state, text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    return [t for t in state['contract'].get('banned_terms', []) if t.lower() in text]


def delta_hash(delta):
    core = {k: delta[k] for k in ('entry', 'why', 'ops') if k in delta}
    return hashlib.sha1(json.dumps(core, sort_keys=True).encode('utf-8')).hexdigest()[:12]


def validate_delta(state, delta, errs, warns, entries=None, strict=False):
    """Return the new state after applying delta to a copy of state; append problems to errs.

    strict adds rules introduced after deltas were first committed. A new delta is checked with them;
    replaying the log is not, so an older campaign keeps replaying (reconcile rechecks deltas after a withdrawal)."""
    if not isinstance(delta, dict):
        errs.append('delta must be an object')
        return state
    extra = set(delta) - {'delta', 'entry', 'why', 'ops', 'seq'}
    if extra:
        errs.append('unknown delta keys: ' + ', '.join(sorted(extra)))
    if not (isinstance(delta.get('entry'), str) and UUID_RE.match(delta['entry'])):
        errs.append('entry must be the UUID of the story or Director entry that justifies this change')
    elif entries is not None and delta['entry'] not in entries:
        errs.append(f'entry {delta["entry"]} is not in public/story.md or public/director.md yet')
    why = delta.get('why')
    if not (isinstance(why, str) and 5 <= len(why.strip()) <= 240):
        errs.append('why must say, in 5 to 240 characters, which event or player action supports this change')
    ops = delta.get('ops')
    if not (isinstance(ops, list) and 1 <= len(ops) <= MAX_OPS):
        errs.append(f'ops must be a list of 1 to {MAX_OPS} operations')
        return state
    if delta.get('delta', delta_hash(delta)) in state['seen']:
        errs.append('this delta was already committed')
    new = copy.deepcopy(state)
    ctx = {'entry': delta.get('entry'), 'entries': entries, 'strict': strict}
    for op in ops:
        if not isinstance(op, dict):
            errs.append('each operation must be an object')
            continue
        apply_op(new, op, errs, warns, ctx)
    moves = sum(1 for op in ops if isinstance(op, dict) and op.get('kind') == 'pressure' and op.get('op') == 'advance')
    touched = {op.get('id') for op in ops if isinstance(op, dict) and op.get('kind') == 'revelation'}
    facts = {op.get('id') for op in ops if isinstance(op, dict) and op.get('kind') == 'fact'}
    touched |= {r['id'] for r in new['revelations'].values() if r['fact'] in facts}
    if touched:
        warns.extend(rev_warnings(new, touched))
    if any(isinstance(op, dict) and op.get('kind') == 'scene' for op in ops):
        warns.extend(scene_warnings(new))
    if moves > 2:
        warns.append(f'{moves} pressures advance in one delta. Advance only what this turn justifies, not everything.')
    for text in texts_of(delta):
        for term in banned_in(new, text):
            errs.append(f'contains the banned term "{term}" (see the contract)')
    new['seen'].append(delta.get('delta') or delta_hash(delta))
    return new


# ---- files ----------------------------------------------------------------------------------

def paths(root):
    base = Path(root) / 'notes' / 'gm'
    return base, base / 'deltas.jsonl', base / 'pending.json', base / 'withdrawn.jsonl'


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.gm-tmp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
            out.write(text)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_lines(path):
    if not Path(path).exists():
        return []
    out = []
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').split('\n'), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                sys.exit(f'{path}:{n}: not valid JSON. Fix or remove that line.')
    return out


def dump_lines(items):
    return ''.join(json.dumps(i, ensure_ascii=False, separators=(',', ':')) + '\n' for i in items)


def read_entries(root):
    """Map entry id -> {'role', 'body'} from both public logs."""
    entries = {}
    for name in ('story.md', 'director.md'):
        path = Path(root) / 'public' / name
        if not path.exists():
            continue
        current, body, pos = None, [], 0
        for line in path.read_text(encoding='utf-8').replace('\r\n', '\n').split('\n'):
            m = ENTRY_START.match(line)
            if m:
                try:
                    meta = json.loads(m.group(1))
                    pos += 1
                    current = {'role': meta.get('role'), 'body': '', 'channel': name, 'pos': pos}
                    entries[meta['id']] = current
                    body = []
                except (ValueError, KeyError):
                    current = None
            elif line == ENTRY_END and current is not None:
                current['body'] = '\n'.join(body)
                current = None
            elif current is not None:
                body.append(line)
    return entries


def replay(deltas, strict_after=None, lenient=()):
    """Rebuild state from committed deltas. Deltas whose seq is above strict_after are held to the current
    rules, except those whose seq is in lenient."""
    state, good, bad = new_state(), [], []
    for delta in deltas:
        errs, warns = [], []
        seq = delta.get('seq') or 0
        strict = strict_after is not None and seq > strict_after and seq not in lenient
        new = validate_delta(state, delta, errs, warns, strict=strict)
        if errs:
            bad.append((delta, errs))
        else:
            state = new
            good.append(delta)
    return state, good, bad


KIND_LAYER = {'contract': 1, 'situation': 1, 'fact': 1, 'thread': 2, 'pressure': 3, 'npc': 3,
              'revelation': 4, 'scene': 5}
LAYER_KEYS = {2: ['threads'], 3: ['pressures', 'npcs'], 4: ['revelations'], 5: ['scenes']}
LAYER_NAMES = {1: 'continuity', 2: 'memory', 3: 'living world', 4: 'discovery', 5: 'pacing'}


def layers_path(root):
    return paths(root)[0] / 'layers.json'


def read_layers(root):
    """The layers that are switched on. With no layers.json, all five are (older installs)."""
    path = layers_path(root)
    if not path.exists():
        return {1, 2, 3, 4, 5}
    try:
        active = set(json.loads(path.read_text(encoding='utf-8'))['active'])
        if not active <= set(LAYER_NAMES):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        sys.exit(f'{path}: expected {{"active": [1, 2, ...]}} with numbers from 1 to 5.')
    return active | {1}


def load(root):
    _, deltas_path, _, _ = paths(root)
    deltas = read_lines(deltas_path)
    state, _, bad = replay(deltas)
    active = read_layers(root)
    state['layers'] = sorted(active)
    if 4 not in active:  # a switched-off layer 4 still protects its hidden truths (see truth_of)
        state['hidden_truths'] = {r['fact']: r['id'] for r in state['revelations'].values() if r['status'] in REV_LIVE}
    for layer, keys in LAYER_KEYS.items():  # a layer that is off is invisible; its records stay in the log
        if layer not in active:
            for key in keys:
                state[key] = {}
            if layer == 5:
                state['scene_order'], state['open_scene'] = [], None
    entries = read_entries(root)
    gone = [d for d in deltas if d.get('entry') not in entries]
    if gone:
        print(f'WARN {len(gone)} committed delta(s) cite entries no longer in the logs (Undo?). '
              'Run: python tools/gm_state.py reconcile --apply', file=sys.stderr)
    if bad:
        sys.exit('The committed deltas do not replay cleanly (seq '
                 + ', '.join(str(d.get('seq', '?')) for d, _ in bad)
                 + '). Run: python tools/gm_state.py reconcile')
    return state


# ---- hot context ----------------------------------------------------------------------------

def hot(state, about, budget):
    c, s = state['contract'], state['situation']
    head = ['# GM state (private; cite entry ids in deltas) | layers on: '
            + ', '.join(f'{n} {LAYER_NAMES[n]}' for n in state.get('layers', sorted(LAYER_NAMES)))]
    if c:
        parts = [f'{k}: {v if isinstance(v, str) else "; ".join(v)}' for k, v in c.items()
                 if v and k != 'banned_terms']
        head.append('CONTRACT ' + ' | '.join(parts))
        if c.get('banned_terms'):
            head.append('NEVER USE: ' + ', '.join(c['banned_terms']))
    else:
        head.append('CONTRACT: not set. Run session zero with the Director.')
    if s:
        head.append(f'NOW day {s.get("day", "?")}, {s.get("time", "?")} | {s.get("location", "?")} | '
                    f'present: {", ".join(s.get("present", [])) or "?"} | scene {s.get("scene", "?")}')
        if s.get('problem'):
            head.append('PROBLEM ' + s['problem'])
    context = ' '.join([s.get('location', ''), s.get('problem', ''), s.get('scene', ''),
                        ' '.join(s.get('present', [])), *about]).lower()
    used = [sum(len(h) + 1 for h in head) + 320]  # reserve room for section headers and the footer
    omitted = {'threads': 0, 'facts': 0}

    def fit(line, group):
        if used[0] + len(line) + 1 > budget * 4:
            omitted[group] += 1
            return False
        used[0] += len(line) + 1
        return True

    warnings = [w for w in thread_warnings(state) + pressure_warnings(state) + rev_warnings(state)
                + scene_warnings(state) if fit('WARN ' + w, 'threads')]
    scene = state['scenes'].get(state['open_scene'])
    if scene:
        recent = ', '.join(state['scenes'][s]['mode'] for s in state['scene_order'][-4:])
        line = (f'SCENE {scene["id"]} [{scene["mode"]}'
                + (f', tension {scene["tension"]}' if scene['tension'] is not None else '')
                + f'] agenda: {scene["agenda"]} | ends when: {scene["exit_condition"]}'
                + (f' | serves: {", ".join(scene["serves"])}' if scene['serves'] else ' | serves: nothing yet')
                + f' | recent modes: {recent}')
        if fit(line, 'threads'):
            head.append(line)
    # threads: overdue first, then due soonest, promises and consequences, then tag-relevant
    day = state['situation'].get('day', state['max_day'])
    live_threads = [t for t in state['threads'].values() if t['status'] in THREAD_LIVE]

    def thread_rank(t):
        overdue = t['due_day'] is not None and t['due_day'] < day
        return (not overdue, t['due_day'] if t['due_day'] is not None else 10 ** 9,
                t['type'] not in ('promise', 'consequence'))

    def thread_shown(t):
        relevant = any(x.lower() in context for x in t['tags'])
        overdue = t['due_day'] is not None and t['due_day'] < day
        urgent = t['status'] != 'dormant' and (t['due_day'] is not None or t['type'] in ('promise', 'consequence'))
        return overdue or urgent or relevant
    thread_lines = []
    for t in sorted(filter(thread_shown, live_threads), key=thread_rank):
        due = ''
        if t['due_day'] is not None:
            due = f', due day {t["due_day"]}' + (' OVERDUE' if t['due_day'] < day else '')
        if t['due_condition']:
            due += f', due when: {t["due_condition"]}'
        line = f'{t["id"]} [{t["type"]}, {t["status"]}{due}] {t["text"]}'
        if t['type'] == 'question':
            line += ' (undecided: let play answer it)'
        if fit(line, 'threads'):
            thread_lines.append(line)
    present = {p.lower() for p in state['situation'].get('present', [])}
    npc_lines = []
    for n in state['npcs'].values():
        if n['status'] == 'active' and (n.get('name', '').lower() in present
                                         or any(t.lower() in present for t in n['tags'])):
            parts = [f'{k} {n[k]}' for k in ('want', 'fear', 'secret', 'voice', 'attitude') if n.get(k)]
            line = f'{n["name"]} ({n["id"]}): ' + ' | '.join(parts)
            if fit(line, 'threads'):
                npc_lines.append(line)
    pressure_lines, running = [], []
    for p in state['pressures'].values():
        if p['status'] != 'active':
            continue
        full = p['clock_max'] and p['clock'] >= p['clock_max']
        if full or any(t.lower() in context for t in p['tags']):
            clock = f', clock {p["clock"]}/{p["clock_max"]}' if p['clock_max'] else ''
            line = (f'{p["id"]} [{p["actor"]}{clock}] goal: {p["goal"]}{stage_note(p)} | next: {p["next_action"]} | '
                    f'moves when: {p["trigger"]}' + (f' | if unopposed: {p["consequence"]}' if p['consequence'] else ''))
            if fit(line, 'threads'):
                pressure_lines.append(line)
        else:
            running.append(f'{p["id"]} {p["actor"]}')
    if running:
        line = 'also running: ' + '; '.join(running)
        if fit(line, 'threads'):
            pressure_lines.append(line)
    rev_lines, other_revs = [], []
    for r in state['revelations'].values():
        if r['status'] not in REV_LIVE:
            continue
        open_routes = [x for x in r['routes'].values() if x['status'] == 'open']
        if any(t.lower() in context for t in r['tags']) or (r['importance'] == 'required' and r['status'] == 'partial'):
            routes = '; '.join(f'{x["id"]}) {x["how"]}' + (f' [at {x["where"]}]' if x['where'] else '')
                               for x in open_routes) or 'NO OPEN ROUTE'
            line = f'{r["id"]} [{r["importance"]}, {r["status"]}, truth {r["fact"]}] routes: {routes}'
            if fit(line, 'threads'):
                rev_lines.append(line)
        else:
            other_revs.append(r['id'])
    if other_revs and fit('also hidden: ' + ', '.join(other_revs), 'threads'):
        rev_lines.append('also hidden: ' + ', '.join(other_revs))
    live = [f for f in state['facts'].values() if f['status'] not in TERMINAL_FACT]
    shown = [f for f in live if f['pin'] or any(t.lower() in context for t in f['tags'])]
    # pinned first, then known before hidden, established before uncertain, newest first
    order = {f['id']: i for i, f in enumerate(state['facts'].values())}
    shown.sort(key=lambda f: (not f['pin'], not f['known'], f['status'] != 'established', -order[f['id']]))
    lines = []
    for f in shown:
        label = f['status']
        if f['status'] != 'established':
            label += ': not truth'
        if not f['known']:
            label += ', HIDDEN from player'
        line = f'{f["id"]} [{label}] {f["text"]}'
        if fit(line, 'facts'):
            lines.append(line)
    tail = []
    if omitted['facts'] or omitted['threads']:
        tail.append(f'({omitted["threads"]} threads/warnings and {omitted["facts"]} facts did not fit the '
                    f'{budget}-token budget; ask with --about or run review)')
    hidden = len(live) - len(shown)
    if hidden:
        tail.append(f'({hidden} other live facts not shown; use --about <name> or the state command)')
    return '\n'.join(head + ['WARN ' + w for w in warnings] + (['THREADS'] + thread_lines if thread_lines else [])
                     + (['CAST HERE'] + npc_lines if npc_lines else [])
                     + (['PRESSURES (the world moves without the player)'] + pressure_lines if pressure_lines else [])
                     + (['WHAT THE PLAYER COULD DISCOVER (hidden truths and their routes)'] + rev_lines if rev_lines else [])
                     + (['FACTS'] + lines if lines else []) + tail)


def thread_warnings(state):
    """Soft rules only: they inform your judgment and never force an event."""
    day = state['situation'].get('day', state['max_day'])
    out, stale = [], []
    for t in state['threads'].values():
        if t['status'] not in THREAD_LIVE:
            continue
        if t['due_day'] is not None and t['due_day'] < day:
            out.append(f'{t["id"]} ({t["type"]}) was due day {t["due_day"]}, it is day {day}: '
                       'fulfil, break, release or explain it.')
        quiet = state['scene_count'] - t['touched']
        if t['status'] != 'dormant' and quiet >= STALE_SCENES:
            stale.append((t, quiet))
    if len(stale) > 2:  # a pile of identical warnings costs context and gets ignored
        out.append(f'{len(stale)} threads untouched for {STALE_SCENES}+ scenes ({", ".join(t["id"] for t, _ in stale)}): '
                   'advance, park or resolve them (run review).')
    else:
        out += [f'{t["id"]} ({t["type"]}) untouched for {q} scenes: advance it, make it dormant, or resolve it.'
                for t, q in stale]
    return out


def pressure_warnings(state):
    """Soft rules only."""
    out, active = [], [p for p in state['pressures'].values() if p['status'] == 'active']
    for p in active:
        if p['clock_max'] and p['clock'] >= p['clock_max']:
            out.append(f'{p["id"]} ({p["actor"]}) clock is full: let the consequence land, or resolve it as thwarted.')
    if active:
        quiet = state['scene_count'] - max(p['last_moved'] for p in active)
        if quiet >= STALE_SCENES:
            out.append(f'no pressure has moved in {quiet} scenes: has the world been waiting for the player? '
                       'Consider whether any actor has a reason to act (see review).')
    return out


def review(state):
    """Scene/chapter boundary report: Review, Retire, Refresh, Reopen. Reads only; changes nothing."""
    out = ['# Review (private)', 'REVIEW what changed and what is still owed']
    threads = [t for t in state['threads'].values() if t['status'] in THREAD_LIVE]
    out += [f'  {t["id"]} [{t["type"]}, {t["status"]}] {t["text"]}' for t in threads] or ['  no live threads']
    warns = thread_warnings(state) + pressure_warnings(state) + rev_warnings(state)
    out += ['  WARN ' + w for w in warns]
    out.append('RETIRE candidates (propose each as a delta with a reason; nothing here is automatic)')
    stale = [t for t in threads if t['status'] != 'dormant' and state['scene_count'] - t['touched'] >= STALE_SCENES]
    out += [f'  {t["id"]}: make dormant, or resolve if it has already ended' for t in stale]
    out += [f'  {f["id"]} [provisional]: show it in play and establish it, or discard it'
            for f in state['facts'].values() if f['status'] == 'provisional']
    out += [f'  {f["id"]} [rumour]: confirm, disprove (outdated), or leave it a rumour on purpose'
            for f in state['facts'].values() if f['status'] == 'rumour']
    done = [t for t in state['threads'].values() if t['status'] == 'resolved']
    out.append(f'  {len(done)} resolved thread(s) are kept as summaries and left out of the hot context.')
    out.append('DISCOVERY what the player has yet to learn (keep each required truth reachable by several routes)')
    for r in state['revelations'].values():
        if r['status'] in REV_LIVE:
            counts = {s: sum(1 for x in r['routes'].values() if x['status'] == s) for s in ('open', 'used', 'blocked')}
            out.append(f'  {r["id"]} [{r["importance"]}, {r["status"]}, truth {r["fact"]}] routes open {counts["open"]}, '
                       f'used {counts["used"]}, blocked {counts["blocked"]}')
    if not any(r['status'] in REV_LIVE for r in state['revelations'].values()):
        out.append('  no hidden truths are being tracked')
    out.append('REFRESH what the world is doing (advance only what time, events or the player justify; '
               'after a time skip, decide each actor in turn and leave evidence the protagonist can find)')
    for p in state['pressures'].values():
        if p['status'] == 'active':
            clock = f' clock {p["clock"]}/{p["clock_max"]}' if p['clock_max'] else ''
            out.append(f'  {p["id"]} {p["actor"]}{clock}{stage_note(p)}: next "{p["next_action"]}" when "{p["trigger"]}"')
    if not any(p['status'] == 'active' for p in state['pressures'].values()):
        out.append('  no active pressures: who wants something the player is not giving them?')
    out += ['REOPEN plan a strong next opening: a situation already in motion, not a recap of what happened']
    return '\n'.join(out)


# ---- commands -------------------------------------------------------------------------------

def report(errs, warns):
    for e in errs:
        print('ERROR ' + e)
    for w in warns:
        print('WARN  ' + w)


def load_pending(root, file=None):
    path = Path(file) if file else paths(root)[2]
    if not path.exists():
        sys.exit(f'No pending delta at {path}.')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        sys.exit(f'{path}: not valid JSON ({exc}).')


def cmd_check(args, commit=False):
    state = load(args.root)
    delta = load_pending(args.root, getattr(args, 'file', None))
    errs, warns = [], []
    given = resolve_auto(state, delta)
    if given:
        print('ids assigned: ' + ', '.join(given))
    for op in delta.get('ops', []) if isinstance(delta, dict) and isinstance(delta.get('ops'), list) else []:
        layer = KIND_LAYER.get(op.get('kind')) if isinstance(op, dict) else None
        if layer and layer not in state['layers']:
            errs.append(f'{op["kind"]} belongs to layer {layer} ({LAYER_NAMES[layer]}), which is off. '
                        f'Switch it on first: python tools/gm_state.py layers --on {layer}')
    entries = read_entries(args.root) if commit else None
    new = validate_delta(state, delta, errs, warns, entries, strict=True)
    prose = getattr(args, 'prose', None)
    if prose:
        for term in banned_in(new, Path(prose).read_text(encoding='utf-8')):
            errs.append(f'draft prose contains the banned term "{term}"')
    if commit and not errs:
        body = entries[delta['entry']]['body']
        warns += [f'the cited entry contains the banned term "{t}"' for t in banned_in(new, body)]
    report(errs, warns)
    if errs:
        sys.exit(1)
    if not commit:
        print('ok: the delta is valid')
        return
    _, deltas_path, pending_path, _ = paths(args.root)
    deltas = read_lines(deltas_path)
    delta = {'seq': len(deltas) + 1, 'delta': delta.get('delta') or delta_hash(delta),
             **{k: delta[k] for k in ('entry', 'why', 'ops')}}
    write_text(deltas_path, dump_lines(deltas + [delta]))
    if pending_path.exists() and not getattr(args, 'file', None):
        pending_path.unlink()
    print(f'committed seq {delta["seq"]}')


def cmd_reconcile(args):
    _, deltas_path, _, withdrawn_path = paths(args.root)
    deltas, entries = read_lines(deltas_path), read_entries(args.root)
    missing = [d for d in deltas if d.get('entry') not in entries]
    kept = [d for d in deltas if d.get('entry') in entries]
    # After a withdrawal, later deltas are rechecked with today's rules, since what they relied on may be gone.
    # A delta that broke those rules even with nothing withdrawn (an older log) keeps the rules it was written under:
    # failing them now says nothing about the withdrawal.
    cut = min((d.get('seq') or 0) for d in missing) if missing else None
    lenient = {d.get('seq') or 0 for d, _ in replay(deltas, cut)[2]} if missing else set()
    state, good, bad = replay(kept, cut, lenient)
    for d in missing:
        print(f'WITHDRAWN seq {d.get("seq")}: entry {d.get("entry")} is no longer in the logs ({d.get("why")})')
    for d, errs in bad:
        print(f'DEPENDENT seq {d.get("seq")}: depended on withdrawn state ({"; ".join(errs)}). '
              f'Its prose still stands; restate its facts as a new delta.')
    if not missing and not bad:
        print('ok: every delta cites an existing entry and replays cleanly')
        return
    if args.apply:
        set_aside = missing + [d for d, _ in bad]
        write_text(withdrawn_path, dump_lines(read_lines(withdrawn_path) + set_aside))
        write_text(deltas_path, dump_lines(good))
        print(f'set aside {len(set_aside)} delta(s) in {withdrawn_path.name}; {len(good)} remain')
    else:
        print('Run again with --apply to set these aside (a private copy is kept in withdrawn.jsonl).')
        sys.exit(1)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--root', default='.')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init')
    p = sub.add_parser('check')
    p.add_argument('--file')
    p.add_argument('--prose')
    sub.add_parser('commit')
    sub.add_parser('discard')
    p = sub.add_parser('state')
    p.add_argument('--live', action='store_true')
    sub.add_parser('review')
    sub.add_parser('boundary')
    sub.add_parser('schema')
    p = sub.add_parser('layers')
    p.add_argument('--on', nargs='*', type=int, default=[])
    p.add_argument('--off', nargs='*', type=int, default=[])
    p = sub.add_parser('hot')
    p.add_argument('--about', nargs='*', default=[])
    p.add_argument('--budget', type=int, default=1000)
    p = sub.add_parser('reconcile')
    p.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    base, deltas_path, pending_path, withdrawn_path = paths(args.root)
    if args.cmd == 'init':
        for path in (deltas_path, withdrawn_path):
            if not path.exists():
                write_text(path, '')
        print(f'ready: {base}')
    elif args.cmd == 'check':
        cmd_check(args)
    elif args.cmd == 'commit':
        cmd_check(args, commit=True)
    elif args.cmd == 'discard':
        pending_path.unlink(missing_ok=True)
        print('discarded')
    elif args.cmd == 'state':
        state = load(args.root)
        if args.live:
            state['facts'] = {k: v for k, v in state['facts'].items() if v['status'] not in TERMINAL_FACT}
            state['threads'] = {k: v for k, v in state['threads'].items() if v['status'] in THREAD_LIVE}
            state['pressures'] = {k: v for k, v in state['pressures'].items() if v['status'] in PRESSURE_LIVE}
            state['revelations'] = {k: v for k, v in state['revelations'].items() if v['status'] in REV_LIVE}
            keep = set(state['scene_order'][-8:])
            state['scenes'] = {k: v for k, v in state['scenes'].items() if k in keep}
        print(json.dumps(state, indent=2, ensure_ascii=False))
    elif args.cmd == 'review':
        print(review(load(args.root)))
    elif args.cmd == 'boundary':
        print(boundary(load(args.root)))
    elif args.cmd == 'schema':
        print(schema_text())
    elif args.cmd == 'layers':
        active = read_layers(args.root)
        bad_numbers = [n for n in args.on + args.off if n not in LAYER_NAMES]
        if bad_numbers or 1 in args.off:
            sys.exit('Layers are numbered 1 to 5, and layer 1 (continuity) is the foundation and stays on.')
        if args.on or args.off:
            active = (active | set(args.on)) - set(args.off)
            write_text(layers_path(args.root), json.dumps({'active': sorted(active)}) + '\n')
        for n, name in LAYER_NAMES.items():
            print(f'{n} {name}: {"ON" if n in active else "off"}')
    elif args.cmd == 'hot':
        print(hot(load(args.root), args.about, args.budget))
    elif args.cmd == 'reconcile':
        cmd_reconcile(args)


if __name__ == '__main__':
    main()
