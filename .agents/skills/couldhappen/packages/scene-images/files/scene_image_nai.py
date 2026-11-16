"""Make one scene image with NovelAI Diffusion V5. Usage:
    python tools/scene_image_nai.py PROMPT_FILE                      write one PNG under public/assets/ and print its file name
    python tools/scene_image_nai.py PROMPT_FILE --size landscape     portrait (default), landscape or square
    python tools/scene_image_nai.py PROMPT_FILE --seed 1234          remake with a recorded seed

The NovelAI provider for scene-images, with the same contract as tools/scene_image.py: a prompt file in, a PNG
in public/assets/ out, its file name printed. The key is a persistent API token (it starts with pst-) read from
NOVELAI_TOKEN in the process environment. It is never printed or stored. Only the /ai/ generation endpoint is
called, and only when the Director asked for a picture.

The prompt file holds the base prompt first, written as it should be sent: the people count, objects, action,
framing, place and light as Danbooru tags, a short sentence only where tags cannot say it, and, with two or more
people, one "Character N: ..." action line per person. Then one character field per person in frame, each under
a header line "[Character N]", numbered from 1 and from the viewer's left, holding that person's gender,
appearance and clothing. "[Character N = <cast id>]" fills the field from notes/prompts/cast/<cast id>.txt, the
character's fixed cast block; lines under such a header replace the block's clothing (every line after its
first). "[Character N @ X,Y]" places that person on the canvas, X from 0 (left) to 1 (right), Y from 0
(top) to 1 (bottom); give every character a position or none. Lines starting with # are notes and are not
sent. A line "nsfw: no" here or in notes/style.txt means the Director does not want NSFW pictures, and nsfw goes into the undesired content. After a
picture is made, the seed used is recorded in the prompt file as a "seed: N" line, so the picture can be remade
or varied deliberately with --seed.

Defaults (the Opus free tier, Effort High): model nai-diffusion-5-full, 23 steps, one sample, Normal sizes only
(portrait 832x1216, landscape 1216x832, square 1024x1024), sampler k_euler_ancestral, noise schedule karras,
guidance 7. The Standard quality tags are appended to the base prompt and the Heavy V5 undesired content is
sent. Anything that costs Anlas (another size such as --size 1024x1536, or --steps above 28) is refused unless
--spend-anlas is given, which needs the Director's explicit request each time. --text drops "no text" from the
quality tags and logo from the undesired content, for a picture that needs readable text.

--ref is kept for when V5 takes reference images, and is refused for now: put the character's cast tag block on
their [Character N] field instead.

Optional environment: NOVELAI_IMAGE_URL (default https://image.novelai.net; for a local test server).
The endpoint and the V5 request fields were checked against NovelAI on 2026-11-16; the field names follow the
web client and NovelAI-Image-MCP (MIT, https://github.com/xinvxueyuan/NovelAI-Image-MCP), whose code is not used.
"""
import argparse
import hashlib
import io
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

MODEL = 'nai-diffusion-5-full'
SIZES = {'portrait': (832, 1216), 'landscape': (1216, 832), 'square': (1024, 1024)}  # NovelAI's Normal sizes
STEPS = 23  # Effort High
FREE_STEPS = 28  # the most steps the Opus free tier allows
QUALITY = ', very aesthetic, masterpiece, no text'  # Standard quality tags
HEAVY_UC = ('lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, '
            'very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, '
            'too many watermarks, negative space, blank page')
USER_AGENT = 'couldhappen-scene-image/0.1'  # an honest agent: Cloudflare refuses Python's default one
HEADER = re.compile(r'^\[\s*character\s*(\d+)\s*(?:=\s*([A-Za-z0-9_-]+)\s*)?'
                    r'(?:@\s*([0-9.]+)\s*,\s*([0-9.]+)\s*)?\]$', re.IGNORECASE)
NO_NSFW = re.compile(r'^nsfw\s*:\s*no\s*$', re.IGNORECASE)
SEED = re.compile(r'^seed\s*:\s*\d+\s*$', re.IGNORECASE)


def tidy(lines):
    """Lines as written, without leading, trailing or repeated blank lines."""
    text = re.sub(r'\n{3,}', '\n\n', '\n'.join(line.rstrip() for line in lines))
    return text.strip()


def cast_block(cast_dir, cast_id):
    """A cast block's tag lines: the appearance line first, then the clothing lines."""
    path = Path(cast_dir) / f'{cast_id}.txt'
    try:
        lines = [line for line in path.read_text(encoding='utf-8').splitlines()
                 if line.strip() and not line.strip().startswith('#')]
    except OSError:
        raise ValueError(f'there is no cast block {path}') from None
    if not lines:
        raise ValueError(f'the cast block {path} has no tags')
    return lines


def parse(text, cast_dir='notes/prompts/cast'):
    """Split a prompt file into (base prompt, [character fields], nsfw excluded, [positions] or None)."""
    base, characters, casts, centers, no_nsfw = [], [], [], [], False
    current = base
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith('#') or SEED.match(line):
            continue
        if NO_NSFW.match(line):
            no_nsfw = True
            continue
        header = HEADER.match(line)
        if header:
            if int(header.group(1)) != len(characters) + 1:
                raise ValueError('[Character N] headers must be numbered 1, 2, 3 ... in order')
            current = []
            characters.append(current)
            casts.append(header.group(2))
            if header.group(3) is None:
                centers.append(None)
            else:
                try:
                    x, y = float(header.group(3)), float(header.group(4))
                except ValueError:
                    raise ValueError(f'"{line}": a position is two numbers, X,Y') from None
                if not (0 <= x <= 1 and 0 <= y <= 1):
                    raise ValueError(f'"{line}": a position runs from 0 to 1 on each axis')
                centers.append({'x': round(x, 2), 'y': round(y, 2)})
            continue
        current.append(raw)
    fields = []
    for lines, cast_id in zip(characters, casts):
        if cast_id:
            block = cast_block(cast_dir, cast_id)
            lines = block[:1] + (lines if tidy(lines) else block[1:])
        fields.append(tidy(lines))
    base = tidy(base)
    if any(not field for field in fields):
        raise ValueError('a [Character N] header has nothing under it')
    if not base and not fields:
        raise ValueError('the prompt file is empty')
    if any(centers) and not all(centers):
        raise ValueError('give every [Character N] a position (@ X,Y) or none')
    return base, fields, no_nsfw, (centers if any(centers) else None)


def payload(base, characters, *, width, height, steps, seed, no_nsfw=False, text=False, centers=None):
    """The JSON body for POST /ai/generate-image. With centers, each character is placed on the canvas."""
    quality = QUALITY.replace(', no text', '') if text else QUALITY
    base = base.rstrip().rstrip(',').rstrip()
    prompt = (base + quality) if base else quality.lstrip(', ')
    uc = HEAVY_UC.replace(' logo,', '') if text else HEAVY_UC
    uc = ('nsfw, ' + uc) if no_nsfw else uc
    use_coords = bool(centers)
    centers = centers or [{'x': 0.5, 'y': 0.5}] * len(characters)
    pairs = list(zip(characters, centers))
    parameters = {
        'params_version': 4, 'width': width, 'height': height, 'scale': 7, 'sampler': 'k_euler_ancestral',
        'steps': steps, 'n_samples': 1, 'seed': seed, 'ucPresetId': 'heavy', 'qualityPresetId': 'none',
        'autoSmea': False, 'dynamic_thresholding': False, 'controlnet_strength': 1, 'legacy': False,
        'add_original_image': True, 'cfg_rescale': 0, 'noise_schedule': 'karras', 'legacy_v3_extend': False,
        'use_coords': use_coords, 'legacy_uc': False,
        'normalize_reference_strength_multiple': True, 'inpaintImg2ImgStrength': 1,
        'characterPrompts': [{'prompt': c, 'uc': '', 'center': at, 'enabled': True} for c, at in pairs],
        'v4_prompt': {'caption': {'base_caption': prompt,
                                  'char_captions': [{'char_caption': c, 'centers': [at]} for c, at in pairs]},
                      'use_coords': use_coords, 'use_order': True},
        'v4_negative_prompt': {'caption': {'base_caption': uc,
                                           'char_captions': [{'char_caption': '', 'centers': [at]} for _, at in pairs]},
                               'legacy_uc': False},
        'negative_prompt': uc, 'straight_alpha': True, 'tag_hint_qt': 0, 'tag_hint_uc_preset': 2,
        'deliberate_euler_ancestral_bug': False, 'prefer_brownian': True, 'image_format': 'png',
    }
    return {'input': prompt, 'model': MODEL, 'action': 'generate', 'parameters': parameters}


def png_from_zip(data):
    """Return the PNG inside NovelAI's ZIP reply."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in archive.namelist():
                image = archive.read(name)
                if image.startswith(b'\x89PNG\r\n\x1a\n'):
                    return image
    except zipfile.BadZipFile:
        raise ValueError('NovelAI did not return a ZIP') from None
    raise ValueError('NovelAI returned a ZIP with no PNG in it')


def size(value):
    if value in SIZES:
        return SIZES[value]
    match = re.fullmatch(r'(\d+)x(\d+)', value)
    if not match:
        raise argparse.ArgumentTypeError('use portrait, landscape, square or WIDTHxHEIGHT')
    width, height = int(match.group(1)), int(match.group(2))
    if width % 64 or height % 64 or not 64 <= width <= 2048 or not 64 <= height <= 2048:
        raise argparse.ArgumentTypeError('width and height must be multiples of 64 between 64 and 2048')
    return width, height


def record_seed(path, seed):
    """Write the seed used into the prompt file as its last line, replacing an older record."""
    lines = [line for line in path.read_text(encoding='utf-8').splitlines() if not SEED.match(line.strip())]
    while lines and not lines[-1].strip():
        lines.pop()
    path.write_text('\n'.join(lines + [f'seed: {seed}']) + '\n', encoding='utf-8')


def main(argv):
    parser = argparse.ArgumentParser(prog='scene_image_nai.py', description=__doc__.split('\n', 1)[0],
                                     usage='%(prog)s PROMPT_FILE [--size SIZE] [--seed N] [--steps N] [--text] [--spend-anlas]')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('--size', type=size, default=SIZES['portrait'])
    parser.add_argument('--steps', type=int, default=STEPS)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--text', action='store_true', help='allow readable text in the picture')
    parser.add_argument('--spend-anlas', action='store_true', help='allow settings beyond the Opus free tier')
    parser.add_argument('--ref', nargs='+', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.ref:
        sys.exit(f'{MODEL} does not take reference images yet. Put each character\'s appearance tags in their '
                 '[Character N] field instead, and leave out --ref.')
    width, height = args.size
    if not 1 <= args.steps <= 50:
        sys.exit('--steps must be between 1 and 50')
    if (width, height) not in SIZES.values() or args.steps > FREE_STEPS:
        if not args.spend_anlas:
            sys.exit(f'{width}x{height} at {args.steps} steps costs Anlas. The free tier is a Normal size '
                     f'(portrait, landscape or square) at {FREE_STEPS} steps or fewer. Add --spend-anlas only '
                     'when the Director has asked for this picture at this setting.')
    if args.seed is not None and not 0 <= args.seed < 2 ** 32:
        sys.exit('--seed must be between 0 and 4294967295')
    try:
        base, characters, no_nsfw, centers = parse(args.prompt_file.read_text(encoding='utf-8'),
                                                   Path(__file__).resolve().parents[1] / 'notes/prompts/cast')
    except (OSError, ValueError) as error:
        sys.exit(f'Cannot use the prompt file: {error}')
    root = Path(__file__).resolve().parents[1]
    style = root / 'notes/style.txt'
    if style.is_file() and any(NO_NSFW.match(line.strip()) for line in style.read_text(encoding='utf-8').splitlines()):
        no_nsfw = True
    token = os.environ.get('NOVELAI_TOKEN')
    if not token:
        sys.exit('NOVELAI_TOKEN is not set in this process environment')
    seed = args.seed if args.seed is not None else random.randint(0, 2 ** 32 - 1)
    body = json.dumps(payload(base, characters, width=width, height=height, steps=args.steps, seed=seed,
                              no_nsfw=no_nsfw, text=args.text, centers=centers)).encode()
    url = os.environ.get('NOVELAI_IMAGE_URL', 'https://image.novelai.net').rstrip('/') + '/ai/generate-image'
    req = urllib.request.Request(url, body, {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token,
                                             'User-Agent': USER_AGENT}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=300) as reply:
            data = reply.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors='replace')[:400].replace(token, '[token]')
        hint = {401: ' (the token was refused: check NOVELAI_TOKEN)',
                402: ' (this needs Anlas or an active subscription)',
                429: ' (too many requests: wait before trying again)'}.get(error.code, '')
        sys.exit(f'NovelAI error {error.code}{hint}: {detail}')
    except urllib.error.URLError as error:
        sys.exit(f'Cannot reach NovelAI: {error.reason}')
    try:
        png = png_from_zip(data)
    except ValueError as error:
        sys.exit(str(error))
    name = 'scene-' + hashlib.sha256(png).hexdigest()[:16] + '.png'
    out = root / 'public/assets'
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_bytes(png)
    record_seed(args.prompt_file, seed)
    print(name)


if __name__ == '__main__':
    main(sys.argv[1:])
