import importlib.util
import json
import os
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
import zlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
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


ARTISTS = [{'name': 'ningen_mame', 'post_count': 634, 'category': 1, 'is_deprecated': False},
           {'name': 'ningen_(ningen96)', 'post_count': 406, 'category': 1, 'is_deprecated': False},
           {'name': 'ningen_tag', 'post_count': 900, 'category': 0, 'is_deprecated': False}]


class Danbooru(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        seen.append((url.path, query, dict(self.headers)))
        found = ARTISTS if query['search[name_or_alias_matches]'][0].startswith('ningen') else []
        data = json.dumps(found).encode()
        self.send_response(200)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def png_with_text(*chunks):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    out = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
    for kind, body in chunks:
        out += chunk(kind, body)
    return out + chunk(b'IEND', b'')


class Artists(unittest.TestCase):
    def setUp(self):
        self.tags = load()

    def test_artist_lines_show_prompt_form_and_mark_the_exact_name(self):
        shown = self.tags.artist_lines('ningen mame', ARTISTS)
        self.assertEqual(len(shown), 2)
        self.assertRegex(shown[0], r'artist:ningen mame\s+posts\s+634\s+exact$')
        self.assertNotIn('exact', shown[1])
        self.assertIn('artist:ningen (ningen96)', shown[1])

    def test_artist_tags_are_found_in_embedded_text_however_they_are_weighted(self):
        texts = ['1girl, 0.8::artist:ningen_mame::, {artist:Wlop}, artist:ask (askzy), very aesthetic',
                 '{"prompt": "artist:foo bar,\\nsolo", "uc": "artist:ningen_mame"}']
        self.assertEqual(self.tags.artists_in(texts),
                         ['artist:ningen mame', 'artist:wlop', 'artist:ask (askzy)', 'artist:foo bar'])

    def test_png_text_chunks_are_read_plain_compressed_and_international(self):
        data = png_with_text((b'tEXt', b'Description\x00artist:one, 1girl'),
                             (b'zTXt', b'Comment\x00\x00' + zlib.compress(b'{"prompt": "artist:two"}')),
                             (b'iTXt', b'parameters\x00\x00\x00\x00\x00artist:three'))
        self.assertEqual(self.tags.artists_in(self.tags.png_texts(data)), ['artist:one', 'artist:two', 'artist:three'])
        with self.assertRaises(ValueError):
            self.tags.png_texts(b'not a png')

    def test_artist_mode_asks_danbooru_without_a_token(self):
        server = HTTPServer(('127.0.0.1', 0), Danbooru)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        env = {k: v for k, v in os.environ.items() if k != 'NOVELAI_TOKEN'}
        env['DANBOORU_URL'] = f'http://127.0.0.1:{server.server_port}'
        seen.clear()
        done = subprocess.run([sys.executable, '-I', str(SCRIPT), '--artist', 'artist:Ningen_Mame', 'zzqx'],
                              env=env, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        path, query, headers = seen[0]
        self.assertEqual(path, '/tags.json')
        self.assertEqual(query['search[name_or_alias_matches]'], ['ningen_mame*'])
        self.assertEqual(query['search[category]'], ['1'])
        self.assertNotIn('Authorization', headers)
        self.assertIn('artist:ningen mame', done.stdout)
        self.assertNotIn('ningen tag', done.stdout)
        self.assertIn("'zzqx': no Danbooru artist tag starts with this", done.stdout)

    def test_png_mode_prints_the_artist_tags_of_a_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp, 'card.png')
            path.write_bytes(png_with_text((b'tEXt', b'Description\x00artist:one, 1girl')))
            done = subprocess.run([sys.executable, '-I', str(SCRIPT), '--png', str(path)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn('artist:one', done.stdout)


if __name__ == '__main__':
    unittest.main()
