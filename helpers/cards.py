"""Bounded PNG/JSON card extraction. Embedded instructions are never executed."""
import base64
import json
from pathlib import Path
import struct
import zlib

from .files import Invalid, atomic, digest, write_json

SOURCE_LIMIT = 32 * 1024 * 1024
META_LIMIT = 8 * 1024 * 1024
SIGNATURE = b'\x89PNG\r\n\x1a\n'
APPEARANCE = {b'IHDR', b'PLTE', b'IDAT', b'IEND', b'tRNS', b'cHRM', b'gAMA', b'iCCP', b'sBIT', b'sRGB', b'bKGD', b'pHYs', b'acTL', b'fcTL', b'fdAT', b'cICP', b'mDCV', b'cLLI'}


def bounded(path):
    path = Path(path)
    with path.open('rb') as stream:
        data = stream.read(SOURCE_LIMIT + 1)
    if len(data) > SOURCE_LIMIT:
        raise Invalid('Source exceeds 32 MiB')
    return data


def chunks(data):
    if not data.startswith(SIGNATURE):
        raise Invalid('Invalid PNG signature')
    result, pos, ended = [], 8, False
    while pos < len(data):
        if pos + 12 > len(data) or ended:
            raise Invalid('Truncated PNG or bytes after IEND')
        size = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        stop = pos + 12 + size
        if stop > len(data) or size > SOURCE_LIMIT or not all(65 <= v <= 90 or 97 <= v <= 122 for v in kind):
            raise Invalid('Invalid PNG chunk length/type')
        content = data[pos+8:pos+8+size]
        if zlib.crc32(kind + content) & 0xffffffff != struct.unpack('>I', data[stop-4:stop])[0]:
            raise Invalid('PNG checksum mismatch')
        if not kind[0] & 32 and kind not in {b'IHDR', b'PLTE', b'IDAT', b'IEND'}:
            raise Invalid('Unsupported critical PNG chunk')
        result.append((kind, content, data[pos:stop]))
        ended = kind == b'IEND'
        pos = stop
    kinds = [k for k, _, _ in result]
    if not ended or not kinds or kinds[0] != b'IHDR' or kinds.count(b'IHDR') != 1 or b'IDAT' not in kinds or kinds.count(b'PLTE') > 1:
        raise Invalid('Invalid critical PNG structure')
    header = result[0][1]
    if len(header) != 13 or not all(struct.unpack('>II', header[:8])) or header[10:12] != b'\0\0' or header[12] not in (0, 1):
        raise Invalid('Unsupported PNG header')
    depth, color = header[8:10]
    depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
    if depth not in depths.get(color, ()) or (color == 3 and b'PLTE' not in kinds):
        raise Invalid('Invalid PNG color structure')
    idats = [i for i, k in enumerate(kinds) if k == b'IDAT']
    if idats != list(range(min(idats), max(idats)+1)) or (b'PLTE' in kinds and kinds.index(b'PLTE') > min(idats)) or result[-1][1]:
        raise Invalid('Invalid PNG chunk order')
    return result


def definition(data):
    if len(data) > META_LIMIT:
        raise Invalid('Decoded card metadata exceeds 8 MiB')
    try:
        card = json.loads(data.decode('utf-8'))
    except (ValueError, UnicodeError):
        raise Invalid('Malformed UTF-8 card JSON') from None
    if not isinstance(card, dict):
        raise Invalid('Card must be an object')
    if card.get('spec') in ('chara_card_v2', 'chara_card_v3'):
        fmt = 'v2' if card['spec'] == 'chara_card_v2' else 'v3'
        if not isinstance(card.get('data'), dict):
            raise Invalid('Card envelope needs data')
        identity = card['data']
    elif 'spec' in card:
        raise Invalid('Unsupported card specification')
    else:
        fmt, identity = 'v1', card
    if not isinstance(identity.get('name'), str) or not identity['name'].strip():
        raise Invalid('Card requires a character name')
    return card, fmt


def _decode(key, value):
    if len(value) > (META_LIMIT + 2) // 3 * 4:
        raise Invalid('Encoded card metadata exceeds limit')
    try:
        decoded = base64.b64decode(value, validate=True)
    except ValueError:
        raise Invalid('Malformed base64 card metadata') from None
    card, fmt = definition(decoded)
    if key == b'ccv3' and fmt != 'v3':
        raise Invalid('ccv3 metadata must contain a V3 definition')
    return card, fmt


def extract_png(data):
    """Read the definition SillyTavern reads, plus any other distinct ones under that key (ADR-11).

    SillyTavern takes the first ccv3 chunk, else the first chara chunk, keywords compared
    without regard to case. Later chunks under the same key that differ are variants: the
    file does not say which one is current, so they are kept for the writer to compare.
    """
    fields = {b'chara': [], b'ccv3': []}
    for kind, content, _ in chunks(data):
        if kind == b'tEXt' and b'\0' in content:
            key, value = content.split(b'\0', 1)
            key = key.lower()
            if key in fields and value not in fields[key]:
                fields[key].append(value)
    key = b'ccv3' if fields[b'ccv3'] else b'chara'
    if not fields[key]:
        raise Invalid('PNG has no supported card metadata')
    card, fmt = _decode(key, fields[key][0])
    warnings = ['V3 preferred over legacy chara metadata'] if fields[b'ccv3'] and fields[b'chara'] else []
    variants = []
    for number, value in enumerate(fields[key][1:], 2):
        try:
            variants.append((number, *_decode(key, value)))
        except Invalid as error:
            warnings.append(f'Card definition {number} skipped: {error}')
    if len(fields[key]) > 1:
        warnings.append(f'PNG holds {len(fields[key])} different {key.decode()} card definitions; card.json is '
                        'the first, which SillyTavern reads, and the others are kept as variants')
    return card, fmt, warnings, variants


def differing_fields(card, other):
    """Top-level card fields (under data for V2/V3) whose values differ, sorted."""
    a = card.get('data') if isinstance(card.get('data'), dict) else card
    b = other.get('data') if isinstance(other.get('data'), dict) else other
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


TEXT_FIELDS = ('description', 'personality', 'scenario', 'system_prompt', 'post_history_instructions',
               'first_mes', 'mes_example', 'creator_notes')


def _text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=1)


def readable(card):
    """A lossless plain-text reading copy of a card (every field, every lorebook entry, verbatim).

    It adds no interpretation and prescribes nothing; it only spares the writer from reading
    hundreds of kilobytes of escaped JSON. card.json remains the source of truth.
    """
    data = card.get('data') if card.get('spec') in ('chara_card_v2', 'chara_card_v3') else card
    used = set(TEXT_FIELDS) | {'name', 'alternate_greetings', 'character_book'}
    out = [f"# {data['name']}\n"]
    for key in TEXT_FIELDS:
        if data.get(key):
            out.append(f'## {key}\n\n{_text(data[key])}\n')
    prompt = (data.get('extensions') or {}).get('depth_prompt') or {}
    if prompt.get('prompt'):
        out.append(f"## depth_prompt (role {prompt.get('role')}, depth {prompt.get('depth')})\n\n{prompt['prompt']}\n")
    for number, greeting in enumerate(data.get('alternate_greetings') or [], 1):
        out.append(f'## alternate_greeting {number}\n\n{_text(greeting)}\n')
    book = data.get('character_book') or {}
    entries = book.get('entries') or []
    entries = list(entries.values()) if isinstance(entries, dict) else entries
    if book:
        meta = {k: v for k, v in book.items() if k != 'entries'}
        out.append(f'## lorebook ({len(entries)} entries)\n\n{json.dumps(meta, ensure_ascii=False)}\n')
    for number, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            out.append(f'### lorebook entry {number}\n\n{_text(entry)}\n')
            continue
        title = entry.get('comment') or entry.get('name') or f'entry {number}'
        flags = {k: v for k, v in entry.items() if k not in ('content', 'comment', 'name')}
        out.append(f"### lorebook: {title}\n\n{json.dumps(flags, ensure_ascii=False)}\n\n{_text(entry.get('content', ''))}\n")
    rest = {k: v for k, v in data.items() if k not in used}
    if rest:
        out.append(f'## other fields\n\n{json.dumps(rest, ensure_ascii=False, indent=1)}\n')
    return '\n'.join(out)


def import_card(root, source):
    source = Path(source).resolve()
    data = bounded(source)
    suffix = source.suffix.lower()
    if suffix == '.png':
        card, fmt, warnings, extra = extract_png(data)
    elif suffix == '.json':
        card, fmt = definition(data)
        warnings, extra = [], []
    else:
        raise Invalid('Only local PNG and JSON cards are supported; no archives or remote assets')
    sha = digest(data)
    folder = Path(root) / 'imports' / sha
    target = folder / ('source' + suffix)
    if target.exists() and target.read_bytes() != data:
        raise Invalid('Existing content-addressed source differs')
    atomic(target, data)
    write_json(folder / 'card.json', card)
    atomic(folder / 'card.md', readable(card).encode('utf-8'))
    variants = []
    for number, other, _ in extra:
        write_json(folder / f'card.{number}.json', other)
        atomic(folder / f'card.{number}.md', readable(other).encode('utf-8'))
        variants.append({'card_file': f'card.{number}.json', 'readable_file': f'card.{number}.md',
                         'differs': differing_fields(card, other)})
    receipt = {'source_sha256': sha, 'format': fmt, 'result': 'extracted', 'warnings': warnings,
               'source_name': source.name, 'source_file': target.name, 'readable_file': 'card.md',
               'variants': variants}
    write_json(folder / 'import.json', receipt)
    return {'path': str(folder), 'source_path': str(target), **receipt}


def preserved_source(root, source):
    """Resolve a portrait source to its preserved imports/<sha>/source.png.

    Accepts the preserved file itself, its import folder, or the original card
    file when an identical import already exists. Never imports implicitly.
    """
    imports = root / 'imports'
    if source.is_dir() and source.is_relative_to(imports):
        source = source / 'source.png'
    if source.is_relative_to(imports):
        if source.name != 'source.png':
            raise Invalid('Portrait source must be a preserved imported source.png')
        return source
    if source.suffix.lower() != '.png' or not source.is_file():
        raise Invalid('Portrait source must be a PNG card imported with import-card, '
                      'or its preserved imports/<sha>/source.png')
    preserved = imports / digest(bounded(source)) / 'source.png'
    if not preserved.is_file():
        raise Invalid(f'{source.name} has not been imported; run import-card on it first, '
                      'then rerun portrait')
    return preserved


def portrait(root, source):
    root = Path(root).resolve()
    source = preserved_source(root, Path(source).resolve())
    data = bounded(source)
    if source.parent.name != digest(data):
        raise Invalid('Imported source hash differs')
    cleaned = SIGNATURE + b''.join(raw for kind, _, raw in chunks(data) if kind in APPEARANCE)
    name = digest(cleaned) + '.png'
    atomic(root / 'public/assets' / name, cleaned)
    return {'portrait': name, 'sha256': digest(cleaned), 'disclosed': False, 'source_path': str(source)}


USER_AGENT = 'CouldHappen card-image (+https://github.com/Synere/CouldHappen)'


def import_folder(root, source):
    """An import folder from itself, a file in it, or the original card once it is imported."""
    imports = (root / 'imports').resolve()
    source = Path(source).resolve()
    if source.is_relative_to(imports):
        folder = imports / source.relative_to(imports).parts[0] if source != imports else None
    elif source.is_file():
        folder = imports / digest(bounded(source))
    else:
        folder = None
    if folder is None or not (folder / 'card.json').is_file():
        raise Invalid('Source must be an imported card, its import folder, or a file in it; '
                      'run import-card on the card first')
    return folder


def card_image(root, source, url, fetch=None):
    """Fetch one image a card links to, keep it privately and publish a copy without metadata (ADR-12).

    Only a URL that appears in the import's card.json or one of its variants is fetched; the
    format comes from the bytes. The public copy is not disclosed until an entry or the cast
    refers to it.
    """
    from urllib.parse import urlsplit
    from . import images
    root = Path(root).resolve()
    folder = import_folder(root, source)
    if urlsplit(url).scheme not in ('http', 'https'):
        raise Invalid('Only http and https links can be fetched')
    texts = [json.dumps(json.loads(p.read_text(encoding='utf-8')), ensure_ascii=False)
             for p in sorted(folder.glob('card*.json'))]
    if not any(url in text for text in texts):
        raise Invalid('That URL does not appear in this card; only links the card itself holds are fetched')
    data = (fetch or _download)(url)
    if len(data) > SOURCE_LIMIT:
        raise Invalid('Download exceeds 32 MiB')
    ext, cleaned = images.clean(data)
    private = folder / 'assets' / f'{digest(data)}.{ext}'
    atomic(private, data)
    name = f'{digest(cleaned)}.{ext}'
    atomic(root / 'public/assets' / name, cleaned)
    log = folder / 'assets.json'
    records = json.loads(log.read_text(encoding='utf-8')) if log.is_file() else []
    record = {'url': url, 'file': f'assets/{private.name}', 'format': ext, 'picture': name}
    if record not in records:
        records.append(record)
    write_json(log, records)
    return {'picture': name, 'format': ext, 'disclosed': False, 'private_path': str(private), 'url': url}


def _download(url):
    from urllib.error import URLError
    from urllib.request import Request, urlopen
    from urllib.parse import urlsplit
    try:
        with urlopen(Request(url, headers={'User-Agent': USER_AGENT}), timeout=30) as response:
            if urlsplit(response.geturl()).scheme not in ('http', 'https'):
                raise Invalid('Link redirected away from http or https')
            return response.read(SOURCE_LIMIT + 1)
    except (URLError, TimeoutError, OSError) as exc:
        raise Invalid(f'Could not fetch the image: {getattr(exc, "reason", exc)}') from None
