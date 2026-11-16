"""Check Danbooru tags for NovelAI prompts. Makes no image. Usage:
    python tools/nai_tags.py TAG [TAG ...]            general tags, from NovelAI's tag suggester
    python tools/nai_tags.py --artist NAME [NAME ...] artist tags, from Danbooru's public tag list
    python tools/nai_tags.py --png FILE [FILE ...]    artist tags written into a picture's embedded text

General tags: prints the suggestions NovelAI's V5 model knows that start with the query, with how common each is
in its training data. Counts top out at 10000 (shown as 10000+), which only means "common". Suggestions that do
not start with the query are fuzzy matches and confirm nothing, so they are hidden. No match, or a very low count,
means writing that detail as a sentence instead of a tag. Needs NOVELAI_TOKEN in the process environment; the
token is never printed or stored, and only NovelAI's /ai/ suggest-tags endpoint is called.

Artist tags: NovelAI's suggester does not complete them, so --artist asks Danbooru's public tag API for artist
tags (category 1) that start with each name, most posts first, and prints each the way it goes in a prompt
(artist:name, lowercase, spaces for underscores). "exact" marks the tag that is the name itself. A low post count
means the model may barely know the style. Needs no token and no account.

--png reads a PNG's text chunks, such as the prompt NovelAI stores in its own pictures or a card's embedded
data, and prints the artist: tags it finds. Reads the file only.

Optional environment: NOVELAI_IMAGE_URL (default https://image.novelai.net) and DANBOORU_URL (default
https://danbooru.donmai.us), for a local test server. The suggest-tags endpoint and its reply shape
({"tags": [{"tag", "count", "confidence"}]}) were checked against NovelAI on 2026-11-16; they were found through
NovelAI-Image-MCP (MIT, https://github.com/xinvxueyuan/NovelAI-Image-MCP), whose code is not used.
"""
import json
import os
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
import zlib

MODEL = 'nai-diffusion-5-full'
TOP = 10000  # the suggester's counts stop here
USER_AGENT = 'couldhappen-scene-image/0.1'  # an honest agent: Cloudflare refuses Python's default one
ARTIST_IN_TEXT = re.compile(r'artist:\s*([^,:{}\[\]"\n]+?)\s*(?=,|::|\}|\]|"|\n|$)', re.IGNORECASE)


def normal(text):
    return ' '.join(text.replace('_', ' ').lower().split())


def matches(query, tags):
    """Suggestions that start with the query, most common first."""
    start = normal(query)
    found = [t for t in tags if normal(str(t.get('tag', ''))).startswith(start)]
    return sorted(found, key=lambda t: -(t.get('count') or 0))


def line(tag):
    count = tag.get('count') or 0
    shown = f'{TOP}+' if count >= TOP else str(count)
    confidence = tag.get('confidence')
    confidence = f'{confidence:.2f}' if isinstance(confidence, (int, float)) else '-'
    return f"  {tag.get('tag')!s:40} count {shown:>6}  confidence {confidence}"


def artist_tag(name):
    """A Danbooru artist name the way NovelAI reads it: artist:name, lowercase, spaces for underscores."""
    return 'artist:' + normal(name)


def artist_lines(query, found):
    """Lines for Danbooru's artist tags, the exact name marked."""
    wanted = normal(query.split(':', 1)[1] if query.lower().startswith('artist:') else query)
    out = []
    for tag in found:
        if tag.get('category') != 1:
            continue
        exact = 'exact' if normal(str(tag.get('name', ''))) == wanted else ''
        old = ' deprecated' if tag.get('is_deprecated') else ''
        out.append(f"  {artist_tag(str(tag.get('name'))):40} posts {tag.get('post_count', 0)!s:>6}  {exact}{old}".rstrip())
    return out


def png_texts(data):
    """The text of a PNG's tEXt, zTXt and iTXt chunks."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('not a PNG file')
    texts, at = [], 8
    while at + 8 <= len(data):
        length, kind = struct.unpack('>I4s', data[at:at + 8])
        body = data[at + 8:at + 8 + length]
        at += 12 + length
        try:
            if kind == b'tEXt':
                texts.append(body.split(b'\0', 1)[1].decode('latin-1'))
            elif kind == b'zTXt':
                texts.append(zlib.decompress(body.split(b'\0', 1)[1][1:]).decode('latin-1'))
            elif kind == b'iTXt':
                rest = body.split(b'\0', 1)[1]
                compressed, rest = rest[0], rest[2:]
                text = rest.split(b'\0', 2)[2]
                texts.append((zlib.decompress(text) if compressed else text).decode('utf-8'))
        except (IndexError, zlib.error, UnicodeDecodeError):
            continue
        if kind == b'IEND':
            break
    return texts


def positive(text):
    """The prompt part of a text: for NovelAI's JSON metadata, the prompt fields only, never the undesired content."""
    try:
        data = json.loads(text)
    except ValueError:
        return text
    if not isinstance(data, dict):
        return text
    parts = [data.get('prompt')]
    caption = (data.get('v4_prompt') or {}).get('caption') or {}
    parts.append(caption.get('base_caption'))
    parts += [c.get('char_caption') for c in caption.get('char_captions') or [] if isinstance(c, dict)]
    return '\n'.join(p for p in parts if isinstance(p, str))


def artists_in(texts):
    """artist: tags found in the texts' prompts, in order, without repeats."""
    found = []
    for text in texts:
        for name in ARTIST_IN_TEXT.findall(positive(text)):
            tag = artist_tag(name)
            if tag != 'artist:' and tag not in found:
                found.append(tag)
    return found


def get(url, headers):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as reply:
        return json.loads(reply.read())


def check_pngs(paths):
    for path in paths:
        try:
            with open(path, 'rb') as handle:
                found = artists_in(png_texts(handle.read()))
        except (OSError, ValueError) as error:
            print(f'{path}: {error}')
            continue
        print(f'{path}: ' + (', '.join(found) if found else 'no artist: tags in its embedded text'))


def check_artists(names):
    base = os.environ.get('DANBOORU_URL', 'https://danbooru.donmai.us').rstrip('/')
    failed = False
    for query in names:
        name = normal(query.split(':', 1)[1] if query.lower().startswith('artist:') else query).replace(' ', '_')
        url = base + '/tags.json?' + urllib.parse.urlencode({
            'search[name_or_alias_matches]': name + '*', 'search[category]': 1, 'search[hide_empty]': 'true',
            'search[order]': 'count', 'limit': 10})
        try:
            found = get(url, {'User-Agent': USER_AGENT, 'Accept': 'application/json'})
        except urllib.error.HTTPError as error:
            print(f'{query!r}: Danbooru error {error.code}')
            failed = True
            continue
        except urllib.error.URLError as error:
            sys.exit(f'Cannot reach Danbooru: {error.reason}')
        shown = artist_lines(query, found if isinstance(found, list) else [])
        if not shown:
            print(f'{query!r}: no Danbooru artist tag starts with this')
            continue
        print(f'{query!r}:')
        print('\n'.join(shown))
    return failed


def check_tags(queries):
    token = os.environ.get('NOVELAI_TOKEN')
    if not token:
        sys.exit('NOVELAI_TOKEN is not set in this process environment')
    base = os.environ.get('NOVELAI_IMAGE_URL', 'https://image.novelai.net').rstrip('/')
    failed = False
    for query in queries:
        url = base + '/ai/generate-image/suggest-tags?' + urllib.parse.urlencode(
            {'model': MODEL, 'prompt': query, 'lang': 'en'})
        try:
            tags = get(url, {'Authorization': 'Bearer ' + token, 'User-Agent': USER_AGENT}).get('tags', [])
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors='replace')[:200].replace(token, '[token]')
            print(f'{query!r}: NovelAI error {error.code}: {detail}')
            failed = True
            continue
        except urllib.error.URLError as error:
            sys.exit(f'Cannot reach NovelAI: {error.reason}')
        found = matches(query, tags)
        if not found:
            print(f'{query!r}: no tag starts with this; describe it in a sentence instead')
            continue
        print(f'{query!r}:')
        for tag in found:
            print(line(tag))
    return failed


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        sys.exit(__doc__)
    if argv[0] == '--png':
        check_pngs(argv[1:] or sys.exit('--png takes one or more PNG files'))
        return
    if argv[0] == '--artist':
        failed = check_artists(argv[1:] or sys.exit('--artist takes one or more names'))
    else:
        failed = check_tags(argv)
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
