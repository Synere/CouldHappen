"""Version-one public records. All conversation authority lives in Markdown."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import UUID, uuid4

PREFIX = '<!-- couldhappen:'
END = '<!-- couldhappen:end -->'
START = '<!-- couldhappen:entry '
MAX_BODY = 256 * 1024


class Invalid(ValueError):
    pass


def normalize(body):
    return body.replace('\r\n', '\n').replace('\r', '\n')


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


def uuid(value):
    try:
        if str(UUID(value)) != value:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise Invalid('Expected canonical UUID') from None
    return value


def entry(body, role='writer', id=None, status=None):
    body = normalize(body)
    meta = {'id': uuid(id or str(uuid4())), 'role': role}
    if role == 'human':
        meta['status'] = status or 'pending'
    validate_meta(meta)
    escaped = '\n'.join('\\' + line if re.match(r'^\\*<!-- couldhappen:', line) else line
                        for line in body.split('\n'))
    return START + json.dumps(meta, separators=(',', ':')) + ' -->\n' + escaped + '\n' + END + '\n'


def validate_meta(meta):
    if not isinstance(meta, dict) or set(meta) != ({'id', 'role', 'status'} if meta.get('role') == 'human' else {'id', 'role'}):
        raise Invalid('Unsupported entry metadata')
    uuid(meta['id'])
    if meta['role'] not in ('human', 'writer'):
        raise Invalid('Invalid role')
    if meta['role'] == 'human' and meta['status'] not in ('pending', 'addressed', 'deferred'):
        raise Invalid('Invalid human disposition')


def parse(text, channel):
    lines = normalize(text).split('\n')
    if not lines or lines[0] != '# ' + channel.title():
        raise Invalid(f'{channel}:1: expected channel title')
    entries, i = [], 1
    while i < len(lines):
        if not lines[i]:
            i += 1
            continue
        at = i + 1
        try:
            line = lines[i]
            if not line.startswith(START) or not line.endswith(' -->'):
                raise Invalid('Expected entry boundary')
            meta = json.loads(line[len(START):-4])
            validate_meta(meta)
            i += 1
            body = []
            while i < len(lines) and lines[i] != END:
                line = lines[i]
                if line.startswith(PREFIX):
                    raise Invalid('Unescaped reserved marker or incomplete entry')
                if re.match(r'^\\+<!-- couldhappen:', line):
                    line = line[1:]
                body.append(line)
                i += 1
            if i == len(lines) or not body:
                raise Invalid('Missing end marker or separator newline')
            # split lines plus join removes exactly the delimiter separator.
            decoded = '\n'.join(body)
            entries.append({**meta, 'body': decoded, 'body_hash': digest(decoded)})
            i += 1
        except (Invalid, ValueError, TypeError, KeyError) as exc:
            raise Invalid(f'{channel}:{at}: {exc}') from None
    return entries


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.couldhappen-tmp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data if isinstance(data, bytes) else data.encode('utf-8'))
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def asset_path(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or relative.startswith('/') or '..' in relative.split('/'):
        raise Invalid('Invalid public portrait path')
    base = (Path(root) / 'public/assets').resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or path.suffix.lower() != '.png' or not path.is_file():
        raise Invalid('Missing or escaped public PNG')
    return path


def public_asset(root, relative):
    """Read a referenced public PNG only after path and critical-structure checks."""
    path = asset_path(root, relative)
    from .cards import SOURCE_LIMIT, chunks
    if path.stat().st_size > SOURCE_LIMIT:
        raise Invalid('Public portrait exceeds 32 MiB')
    data = path.read_bytes()
    try:
        chunks(data)
    except Invalid as exc:
        raise Invalid(f'Public portrait is not a valid PNG: {exc}') from None
    return data


PICTURE = re.compile(r'^!\[[^\]\n]{0,200}\]\(/api/assets/([A-Za-z0-9][A-Za-z0-9._-]{0,120}\.png)\)\s*$')


def pictures(body):
    """Names of the pictures attached to a passage: lines of the form ![caption](/api/assets/name.png) outside code fences."""
    names, fenced = [], False
    for line in body.split('\n'):
        if re.match(r'^\s*(```|~~~)', line):
            fenced = not fenced
        match = None if fenced else PICTURE.match(line)
        if match:
            names.append(match.group(1))
    return names


def snapshot(root):
    root = Path(root)
    logs, ids = {}, set()
    for channel in ('story', 'director'):
        logs[channel] = parse((root / f'public/{channel}.md').read_text(encoding='utf-8'), channel)
        for item in logs[channel]:
            if item['id'] in ids:
                raise Invalid(f'{channel}: duplicate ID {item["id"]}')
            ids.add(item['id'])
    cast = read_json(root / 'public/cast.json')
    if not isinstance(cast, dict) or cast.get('schema_version') != 1 or not isinstance(cast.get('characters'), list):
        raise Invalid('Unsupported cast format')
    cast_ids, assets = set(), {}
    for character in cast['characters']:
        if not isinstance(character, dict) or set(character) - {'id', 'name', 'description', 'portrait', 'present'}:
            raise Invalid('Invalid disclosed cast fields')
        cid = character.get('id')
        if not isinstance(cid, str) or not cid or cid in cast_ids or not isinstance(character.get('name'), str) or not character['name'].strip():
            raise Invalid('Invalid or duplicate cast identity')
        cast_ids.add(cid)
        if 'description' in character and not isinstance(character['description'], str):
            raise Invalid('Invalid cast description')
        if 'present' in character and not isinstance(character['present'], bool):
            raise Invalid('Invalid cast present flag')
        if character.get('portrait') is not None:
            assets[character['portrait']] = digest(public_asset(root, character['portrait']))
    if 'portrait_button' in cast and not isinstance(cast['portrait_button'], bool):
        raise Invalid('Invalid portrait_button')
    for channel in ('story', 'director'):
        for item in logs[channel]:
            for name in pictures(item['body']):
                if name not in assets:
                    try:
                        assets[name] = digest(public_asset(root, name))
                    except Invalid:
                        raise Invalid(f'{channel}: entry {item["id"]} attaches a missing or invalid picture ({name})') from None
    work = read_json(root / 'public/work.json')
    if not isinstance(work, dict) or set(work) != {'schema_version', 'mode', 'director_question_id'} or work['schema_version'] != 1 or work['mode'] not in ('play', 'awaiting_director'):
        raise Invalid('Unsupported work format')
    question = work['director_question_id']
    if work['mode'] == 'awaiting_director':
        uuid(question)
        if not any(e['id'] == question and e['role'] == 'writer' for e in logs['director']):
            raise Invalid('Recovery requires an existing writer Director question')
    elif question is not None:
        raise Invalid('Play mode must have no recovery question')
    return {**logs, 'cast': cast, 'assets': assets, 'work': work}
