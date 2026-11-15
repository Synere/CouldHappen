"""Check Danbooru tags with NovelAI's tag suggester. Makes no image. Usage:
    python tools/nai_tags.py TAG [TAG ...]       for example: python tools/nai_tags.py "loose socks" "upper bo"

For each query, prints the suggestions NovelAI's V5 model knows that start with the query, with how common each
is in its training data. Counts top out at 10000 (shown as 10000+), which only means "common". Suggestions that do
not start with the query are fuzzy matches and confirm nothing, so they are hidden. No match, or a very low count,
means writing that detail as a sentence instead of a tag.

The token is NOVELAI_TOKEN in the process environment, never printed or stored. Only NovelAI's /ai/ suggest-tags
endpoint is called. Optional environment: NOVELAI_IMAGE_URL (default https://image.novelai.net; for a local test
server). The endpoint and its reply shape ({"tags": [{"tag", "count", "confidence"}]}) were checked against
NovelAI on 2026-11-16; they were found through NovelAI-Image-MCP (MIT,
https://github.com/xinvxueyuan/NovelAI-Image-MCP), whose code is not used.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MODEL = 'nai-diffusion-5-full'
TOP = 10000  # the suggester's counts stop here
USER_AGENT = 'couldhappen-scene-image/0.1'  # an honest agent: Cloudflare refuses Python's default one


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


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        sys.exit(__doc__)
    token = os.environ.get('NOVELAI_TOKEN')
    if not token:
        sys.exit('NOVELAI_TOKEN is not set in this process environment')
    base = os.environ.get('NOVELAI_IMAGE_URL', 'https://image.novelai.net').rstrip('/')
    failed = False
    for query in argv:
        url = base + '/ai/generate-image/suggest-tags?' + urllib.parse.urlencode(
            {'model': MODEL, 'prompt': query, 'lang': 'en'})
        req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token, 'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as reply:
                tags = json.loads(reply.read()).get('tags', [])
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
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
