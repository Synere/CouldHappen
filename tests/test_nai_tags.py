import importlib.util
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from support import REPO

SCRIPT = REPO / '.agents/skills/couldhappen/packages/scene-images/files/nai_tags.py'
TOKEN = 'pst-test-token-never-printed'
seen = []
SUGGESTIONS = {
    'upper bo': [{'tag': 'boingo', 'count': 120, 'confidence': 0.7123456},
                 {'tag': 'upper body', 'count': 10000, 'confidence': 0.0},
                 {'tag': 'bo staff', 'count': 900, 'confidence': 0.65}],
    'socks rolled': [{'tag': 'socks rolled down', 'count': 28, 'confidence': 0.0}],
    'zzqx': [{'tag': 'zebra', 'count': 3000, 'confidence': 0.61}],
}


def load():
    spec = importlib.util.spec_from_file_location('nai_tags', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Suggester(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        seen.append((url.path, query, dict(self.headers)))
        data = json.dumps({'tags': SUGGESTIONS.get(query['prompt'][0], [])}).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class Filtering(unittest.TestCase):
    def setUp(self):
        self.tags = load()

    def test_only_suggestions_that_start_with_the_query_count(self):
        found = self.tags.matches('upper bo', SUGGESTIONS['upper bo'])
        self.assertEqual([t['tag'] for t in found], ['upper body'])
        self.assertEqual(self.tags.matches('Upper_Bo', SUGGESTIONS['upper bo'])[0]['tag'], 'upper body')

    def test_counts_cap_and_confidence_is_rounded(self):
        self.assertIn('10000+', self.tags.line({'tag': 'upper body', 'count': 10000, 'confidence': 0.0}))
        shown = self.tags.line({'tag': 'boingo', 'count': 120, 'confidence': 0.7123456})
        self.assertIn('0.71', shown)
        self.assertNotIn('0.7123', shown)


class Script(unittest.TestCase):
    def test_queries_v5_and_prints_only_confirmed_tags(self):
        server = HTTPServer(('127.0.0.1', 0), Suggester)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        env = {**os.environ, 'NOVELAI_TOKEN': TOKEN, 'NOVELAI_IMAGE_URL': f'http://127.0.0.1:{server.server_port}'}
        seen.clear()
        done = subprocess.run([sys.executable, '-I', str(SCRIPT), 'upper bo', 'socks rolled', 'zzqx'],
                              env=env, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn(TOKEN, done.stdout + done.stderr)
        path, query, headers = seen[0]
        self.assertEqual(path, '/ai/generate-image/suggest-tags')
        self.assertEqual(query['model'], ['nai-diffusion-5-full'])
        self.assertEqual(headers['Authorization'], 'Bearer ' + TOKEN)
        self.assertIn('upper body', done.stdout)
        self.assertNotIn('boingo', done.stdout)
        self.assertRegex(done.stdout, r'socks rolled down\s+count\s+28')
        self.assertIn("'zzqx': no tag starts with this", done.stdout)

    def test_a_missing_token_stops_before_any_request(self):
        env = {k: v for k, v in os.environ.items() if k != 'NOVELAI_TOKEN'}
        done = subprocess.run([sys.executable, '-I', str(SCRIPT), 'socks'], env=env, capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('NOVELAI_TOKEN', done.stderr)


if __name__ == '__main__':
    unittest.main()
