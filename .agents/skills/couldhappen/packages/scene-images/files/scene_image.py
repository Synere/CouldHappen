"""Make one scene image. Usage:
    python tools/scene_image.py PROMPT_FILE                  write one PNG under public/assets/ and print its file name
    python tools/scene_image.py PROMPT_FILE --ref A.png ...  same, but with reference pictures (characters to keep consistent)
    python tools/scene_image.py --models                     list image-capable model ids (free)

Example provider: OpenAI. To use another provider, keep the same contract (prompt file in, PNG out, print the
name) and change the request. The key is read from the process environment and is never printed or stored.
The model is chosen explicitly: list models, pick a cheap one, then set OPENAI_IMAGE_MODEL.

Optional environment: OPENAI_IMAGE_SIZE (default 1024x1024), OPENAI_IMAGE_QUALITY (default low),
OPENAI_BASE_URL (default https://api.openai.com/v1; for a compatible provider or a local test server).

With --ref the request goes to the image-edit endpoint, which takes the pictures as input images, so the
prompt should say which picture is which person ("the first picture is Whisper"). Reference files must be PNG,
JPEG or WebP and are read from disk only, usually public/assets/<portrait>.png."""
import base64
import hashlib
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

LIMIT = 8  # most reference pictures one request may carry


def multipart(fields, files):
    """Encode form fields and (name, filename, bytes, type) files as multipart/form-data."""
    boundary = uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
    for name, filename, data, kind in files:
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f'Content-Type: {kind}\r\n\r\n').encode() + data + b'\r\n'
    out += f'--{boundary}--\r\n'.encode()
    return bytes(out), 'multipart/form-data; boundary=' + boundary


def main(argv):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        sys.exit('OPENAI_API_KEY is not set in this process environment')
    base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    if argv == ['--models']:
        req = urllib.request.Request(base + '/models', headers={'Authorization': 'Bearer ' + key})
        print(sorted(m['id'] for m in json.load(urllib.request.urlopen(req, timeout=60))['data'] if 'image' in m['id'] or 'dall' in m['id']))
        return
    refs = []
    if '--ref' in argv:
        at = argv.index('--ref')
        refs, argv = argv[at + 1:], argv[:at]
        if not refs or len(refs) > LIMIT:
            sys.exit(f'--ref takes 1 to {LIMIT} picture files')
    if len(argv) != 1:
        sys.exit(__doc__)
    model = os.environ.get('OPENAI_IMAGE_MODEL')
    if not model:
        sys.exit('Set OPENAI_IMAGE_MODEL (run with --models to list the choices)')
    prompt = Path(argv[0]).read_text(encoding='utf-8').strip()
    fields = {'model': model, 'prompt': prompt, 'n': 1,
              'size': os.environ.get('OPENAI_IMAGE_SIZE', '1024x1024'),
              'quality': os.environ.get('OPENAI_IMAGE_QUALITY', 'low')}
    if refs:
        files = []
        for ref in refs:
            path = Path(ref)
            kind = mimetypes.guess_type(path.name)[0]
            if kind not in ('image/png', 'image/jpeg', 'image/webp') or not path.is_file():
                sys.exit(f'Reference is not a readable PNG, JPEG or WebP file: {ref}')
            files.append(('image[]', path.name, path.read_bytes(), kind))
        body, kind = multipart(fields, files)
        req = urllib.request.Request(base + '/images/edits', body, {'Content-Type': kind, 'Authorization': 'Bearer ' + key})
    else:
        body = json.dumps(fields).encode()
        req = urllib.request.Request(base + '/images/generations', body,
                                     {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f'Image provider error {e.code}: {e.read().decode(errors="replace")[:400]}')
    png = base64.b64decode(data['data'][0]['b64_json'])
    name = 'scene-' + hashlib.sha256(png).hexdigest()[:16] + '.png'
    out = Path(__file__).resolve().parents[1] / 'public/assets'
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_bytes(png)
    print(name)


if __name__ == '__main__':
    main(sys.argv[1:])
