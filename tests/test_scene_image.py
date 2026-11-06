import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from support import REPO
from test_cards import png

SCRIPT = REPO / '.agents/skills/couldhappen/packages/scene-images/files/scene_image.py'
seen = []


class Provider(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        seen.append((self.path, self.headers['Content-Type'], body))
        reply = json.dumps({'data': [{'b64_json': base64.b64encode(png([])).decode()}]}).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, *args):
        pass


class SceneImage(unittest.TestCase):
    def run_script(self, *args, **extra):
        server = HTTPServer(('127.0.0.1', 0), Provider)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'tools').mkdir()
        (root / 'tools/scene_image.py').write_text(SCRIPT.read_text(encoding='utf-8'), encoding='utf-8')
        (root / 'prompt.txt').write_text('A doorway at dusk.', encoding='utf-8')
        (root / 'ref.png').write_bytes(png([]))
        env = {**os.environ, 'OPENAI_API_KEY': 'test', 'OPENAI_IMAGE_MODEL': 'm',
               'OPENAI_BASE_URL': f'http://127.0.0.1:{server.server_port}/v1', **extra}
        seen.clear()
        done = subprocess.run([sys.executable, '-I', 'tools/scene_image.py', *args], cwd=root, env=env, capture_output=True, text=True)
        return root, done

    def test_generation_uses_environment_size_and_quality(self):
        root, done = self.run_script('prompt.txt', OPENAI_IMAGE_SIZE='1536x1024', OPENAI_IMAGE_QUALITY='medium')
        self.assertEqual(done.returncode, 0, done.stderr)
        path, kind, body = seen[0]
        self.assertEqual(path, '/v1/images/generations')
        sent = json.loads(body)
        self.assertEqual((sent['size'], sent['quality']), ('1536x1024', 'medium'))
        self.assertTrue((root / 'public/assets' / done.stdout.strip()).is_file())

    def test_references_go_to_the_edit_endpoint_as_input_images(self):
        root, done = self.run_script('prompt.txt', '--ref', 'ref.png', 'ref.png')
        self.assertEqual(done.returncode, 0, done.stderr)
        path, kind, body = seen[0]
        self.assertEqual(path, '/v1/images/edits')
        self.assertTrue(kind.startswith('multipart/form-data'))
        self.assertEqual(body.count(b'name="image[]"'), 2)
        self.assertIn(b'A doorway at dusk.', body)

    def test_a_bad_reference_is_refused_before_any_request(self):
        root, done = self.run_script('prompt.txt', '--ref', 'missing.png')
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(seen, [])


if __name__ == '__main__':
    unittest.main()
