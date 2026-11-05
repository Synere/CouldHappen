"""Game-master continuity state for the writer. Private notes only; nothing here is public.

Usage (from the workspace root):  python tools/gm_state.py <command> [--root .]
  init                       create notes/gm/ (safe to repeat)
  check [--file F] [--prose F]   validate the pending delta (default notes/gm/pending.json);
                             --prose scans a draft for the contract's banned terms
  commit                     validate again, require the cited entry to exist, then append it
  discard                    delete the pending delta
  state                      print the current state as JSON
  hot [--about X ...] [--budget N]   print the compact context to read each turn
  reconcile [--apply]        find deltas whose entry was withdrawn (Director Undo) and set them aside

State is never edited directly. It is the replay of notes/gm/deltas.jsonl, an append-only log in
which every delta cites the story or Director entry that justifies it. Stdlib only; no network.
Phase 1 kinds: contract, situation, fact. Later phases add kinds to KINDS-style handlers below."""
import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

FACT_STATUS = ('established', 'rumour', 'provisional', 'outdated')
SOURCES = ('story', 'player', 'director', 'card')
TRANSITIONS = {'provisional': {'established', 'rumour', 'outdated'},
               'rumour': {'established', 'outdated'},
               'established': {'outdated'},
               'outdated': set()}
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
    return {'contract': {}, 'situation': {}, 'max_day': 0, 'facts': {}, 'seen': []}


# ---- applying one delta -------------------------------------------------------------------

def fields_ok(fields, spec, bad):
    if not isinstance(fields, dict) or not fields:
        bad('fields must be a non-empty object')
        return False
    ok = True
    for key, value in fields.items():
        if key not in spec:
            bad(f'unknown field {key}')
            ok = False
        elif not typed(value, spec[key]):
            bad(f'field {key} has the wrong type, is empty, or is too long (max {MAX_TEXT} chars, {MAX_LIST} items)')
            ok = False
    return ok


def keys_ok(op, allowed, bad):
    extra = set(op) - allowed
    if extra:
        bad('unknown keys: ' + ', '.join(sorted(extra)))
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


def apply_op(state, op, errs, warns):
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
        state['situation'].update(op['fields'])
        if day is not None and not flashback:
            state['max_day'] = day
    elif kind == 'fact' and verb == 'add':
        apply_add(state, op, bad, warns)
    elif kind == 'fact' and verb == 'update':
        apply_update(state, op, bad)
    elif kind == 'fact' and verb == 'replace':
        apply_replace(state, op, bad, warns)
    else:
        bad('unknown kind/op')


def fact_id(op, name, bad):
    value = op.get(name)
    if not (isinstance(value, str) and ID_RE.match(value)):
        bad(f'{name} must be an id like F12 (letters, digits, - and _; at most 32 characters)')
        return None
    return value


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
    if fields['status'] not in FACT_STATUS or fields['status'] == 'outdated':
        return bad('status must be established, rumour or provisional (state it explicitly; nothing is assumed true)')
    if fields['source'] not in SOURCES:
        return bad('source must be one of ' + ', '.join(SOURCES))
    fact = {'id': fid, 'known': True, 'tags': [], 'pin': False, **fields}
    state['facts'][fid] = fact
    if not fact['tags'] and not fact['pin']:
        warns.append(f'{fid} has no tags and is not pinned: it will not appear in the hot context. Add tags (names, places).')


def apply_update(state, op, bad):
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
    if fact['status'] == 'outdated':
        return bad(f'{fid} is outdated and cannot change')
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
    fact.update(fields)


def apply_replace(state, op, bad, warns):
    allowed = {'op', 'kind', 'id', 'new', 'reason'} | (set(FACT_FIELDS) - {'status'})
    if not keys_ok(op, allowed, bad):
        return
    old_id, new_id = fact_id(op, 'id', bad), fact_id(op, 'new', bad)
    fields = {k: v for k, v in op.items() if k in FACT_FIELDS}
    if not old_id or not new_id or not fields_ok(fields, FACT_FIELDS, bad):
        return
    old = state['facts'].get(old_id)
    if not old or old['status'] == 'outdated':
        return bad(f'{old_id} must exist and not already be outdated')
    if new_id in state['facts']:
        return bad(f'{new_id} already exists')
    if 'text' not in fields:
        return bad('text is required')
    if not reason_ok(op, bad, f'replacing {old_id}'):
        return
    old['status'], old['replaced_by'] = 'outdated', new_id
    fact = {'id': new_id, 'known': old['known'], 'tags': old['tags'], 'pin': old['pin'],
            'source': 'story', **fields, 'status': 'established', 'replaces': old_id}
    state['facts'][new_id] = fact


def texts_of(delta):
    for op in delta.get('ops', []):
        if not isinstance(op, dict):
            continue
        yield op.get('text')
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


def validate_delta(state, delta, errs, warns, entries=None):
    """Return the new state after applying delta to a copy of state; append problems to errs."""
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
    for op in ops:
        if not isinstance(op, dict):
            errs.append('each operation must be an object')
            continue
        apply_op(new, op, errs, warns)
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
        current, body = None, []
        for line in path.read_text(encoding='utf-8').replace('\r\n', '\n').split('\n'):
            m = ENTRY_START.match(line)
            if m:
                try:
                    meta = json.loads(m.group(1))
                    current = {'role': meta.get('role'), 'body': ''}
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


def replay(deltas):
    state, good, bad = new_state(), [], []
    for delta in deltas:
        errs, warns = [], []
        new = validate_delta(state, delta, errs, warns)
        if errs:
            bad.append((delta, errs))
        else:
            state = new
            good.append(delta)
    return state, good, bad


def load(root):
    _, deltas_path, _, _ = paths(root)
    deltas = read_lines(deltas_path)
    state, _, bad = replay(deltas)
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
    head = ['# GM state (private; cite entry ids in deltas)']
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
    live = [f for f in state['facts'].values() if f['status'] != 'outdated']
    shown = [f for f in live if f['pin'] or any(t.lower() in context for t in f['tags'])]
    # pinned first, then known before hidden, established before uncertain, newest first
    order = {f['id']: i for i, f in enumerate(state['facts'].values())}
    shown.sort(key=lambda f: (not f['pin'], not f['known'], f['status'] != 'established', -order[f['id']]))
    lines, used = [], sum(len(h) + 1 for h in head)
    omitted = 0
    for f in shown:
        label = f['status']
        if f['status'] != 'established':
            label += ': not truth'
        if not f['known']:
            label += ', HIDDEN from player'
        line = f'{f["id"]} [{label}] {f["text"]}'
        if used + len(line) + 1 > budget * 4:
            omitted += 1
            continue
        lines.append(line)
        used += len(line) + 1
    tail = []
    if omitted:
        tail.append(f'({omitted} relevant facts did not fit the {budget}-token budget; ask with --about)')
    hidden = len(live) - len(shown)
    if hidden:
        tail.append(f'({hidden} other live facts not shown; use --about <name> or the state command)')
    return '\n'.join(head + (['FACTS'] + lines if lines else []) + tail)


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
    entries = read_entries(args.root) if commit else None
    new = validate_delta(state, delta, errs, warns, entries)
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
    state, good, bad = replay(kept)
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
    sub.add_parser('state')
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
        print(json.dumps(load(args.root), indent=2, ensure_ascii=False))
    elif args.cmd == 'hot':
        print(hot(load(args.root), args.about, args.budget))
    elif args.cmd == 'reconcile':
        cmd_reconcile(args)


if __name__ == '__main__':
    main()
