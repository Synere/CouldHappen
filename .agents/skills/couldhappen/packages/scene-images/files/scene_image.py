"""Make one scene image. Usage:
    python tools/scene_image.py PROMPT_FILE      write one PNG under public/assets/ and print its file name
    python tools/scene_image.py --models         list image-capable model ids (free)

Example provider: OpenAI. To use another provider, keep the same contract (prompt file in, PNG out, print the
name) and change the request. The key is read from the process environment and is never printed or stored.
The model is chosen explicitly: list models, pick a cheap one, then set OPENAI_IMAGE_MODEL."""
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

key = os.environ.get('OPENAI_API_KEY')
if not key:
    sys.exit('OPENAI_API_KEY is not set in this process environment')
if len(sys.argv) != 2:
    sys.exit(__doc__)
if sys.argv[1] == '--models':
    req = urllib.request.Request('https://api.openai.com/v1/models', headers={'Authorization': 'Bearer ' + key})
    print(sorted(m['id'] for m in json.load(urllib.request.urlopen(req, timeout=60))['data'] if 'image' in m['id'] or 'dall' in m['id']))
    sys.exit()
model = os.environ.get('OPENAI_IMAGE_MODEL')
if not model:
    sys.exit('Set OPENAI_IMAGE_MODEL (run with --models to list the choices)')
prompt = Path(sys.argv[1]).read_text(encoding='utf-8').strip()
body = json.dumps({'model': model, 'prompt': prompt, 'size': '1024x1024', 'quality': 'low', 'n': 1}).encode()
req = urllib.request.Request('https://api.openai.com/v1/images/generations', body,
                             {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
try:
    data = json.load(urllib.request.urlopen(req, timeout=180))
except urllib.error.HTTPError as e:
    sys.exit(f'Image provider error {e.code}: {e.read().decode(errors="replace")[:400]}')
png = base64.b64decode(data['data'][0]['b64_json'])
name = 'scene-' + hashlib.sha256(png).hexdigest()[:16] + '.png'
out = Path(__file__).resolve().parents[1] / 'public/assets'
out.mkdir(exist_ok=True)
(out / name).write_bytes(png)
print(name)
