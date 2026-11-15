import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from support import REPO
from test_cards import png

SCRIPT = REPO / '.agents/skills/couldhappen/packages/scene-images/files/scene_image_nai.py'
TOKEN = 'pst-test-token-never-printed'
seen = []
reply = {}


def zipped(*files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, data in files:
            archive.writestr(name, data)
    return buffer.getvalue()


def load():
    spec = importlib.util.spec_from_file_location('scene_image_nai', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NovelAI(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        seen.append((self.path, dict(self.headers), json.loads(body)))
        status, data = reply.get('status', 200), reply.get('data', zipped(('image_0.png', png([]))))
        self.send_response(status)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class Payload(unittest.TestCase):
    def setUp(self):
        self.nai = load()

    def test_prompt_file_splits_into_base_and_numbered_character_fields(self):
        base, characters, no_nsfw, centers = self.nai.parse(
            '# a note\n2girls, indoors, window, soft lighting,\nThe girl on the left hands a cup to the other.\n\n\n\n'
            'Character 1: girl, source#giving, smile,\nCharacter 2: girl, target#giving,\n'
            '[Character 1]\ngirl, long hair,\nwhite shirt,\n[character 2]\ngirl, short hair,\nseed: 9\n')
        self.assertEqual(base, '2girls, indoors, window, soft lighting,\nThe girl on the left hands a cup to the other.\n\n'
                               'Character 1: girl, source#giving, smile,\nCharacter 2: girl, target#giving,')
        self.assertEqual(characters, ['girl, long hair,\nwhite shirt,', 'girl, short hair,'])
        self.assertFalse(no_nsfw)

    def test_positions_place_every_character_or_none(self):
        text = '1girl, 1boy,\n[Character 1 @ 0.25,0.6]\ngirl,\n[Character 2 @ 0.75, 0.5]\nboy,\n'
        base, characters, _, centers = self.nai.parse(text)
        self.assertEqual(centers, [{'x': 0.25, 'y': 0.6}, {'x': 0.75, 'y': 0.5}])
        sent = self.nai.payload(base, characters, width=1216, height=832, steps=23, seed=1, centers=centers)
        p = sent['parameters']
        self.assertTrue(p['use_coords'] and p['v4_prompt']['use_coords'])
        self.assertEqual(p['characterPrompts'][1]['center'], {'x': 0.75, 'y': 0.5})
        self.assertEqual(p['v4_prompt']['caption']['char_captions'][0]['centers'], [{'x': 0.25, 'y': 0.6}])
        self.assertIsNone(self.nai.parse('1girl,\n[Character 1]\ngirl,\n')[3])
        self.assertFalse(self.nai.payload('1girl', ['girl'], width=832, height=1216, steps=23, seed=1)['parameters']['use_coords'])
        for bad in ('1girl, 1boy,\n[Character 1 @ 0.2,0.5]\ngirl,\n[Character 2]\nboy,\n',
                    '1girl,\n[Character 1 @ 1.5,0.5]\ngirl,\n'):
            with self.assertRaises(ValueError, msg=bad):
                self.nai.parse(bad)

    def test_a_cast_header_can_carry_a_position(self):
        with tempfile.TemporaryDirectory() as cast:
            Path(cast, 'brann.txt').write_text('boy, beard,\nleather apron,\n', encoding='utf-8')
            _, characters, _, centers = self.nai.parse('1boy,\n[Character 1 = brann @ 0.5,0.5]\n', cast)
            self.assertEqual((characters, centers), (['boy, beard,\nleather apron,'], [{'x': 0.5, 'y': 0.5}]))

    def test_character_headers_out_of_order_or_empty_are_refused(self):
        for text in ('1girl\n[Character 2]\ngirl\n', '1girl\n[Character 1]\n[Character 2]\ngirl\n'):
            with self.assertRaises(ValueError, msg=text):
                self.nai.parse(text)

    def test_a_cast_header_fills_the_field_from_the_cast_block(self):
        with tempfile.TemporaryDirectory() as cast:
            Path(cast, 'whisper.txt').write_text(
                '# Whisper. Chosen: grey eyes.\ngirl, long hair, grey hair, braid, grey eyes,\ndark green cloak, boots,\n',
                encoding='utf-8')
            text = '2girls, indoors,\n[Character 1 = whisper]\n[Character 2 = whisper]\nwhite dress,\n'
            base, characters, _, _ = self.nai.parse(text, cast)
            self.assertEqual(characters[0], 'girl, long hair, grey hair, braid, grey eyes,\ndark green cloak, boots,')
            self.assertEqual(characters[1], 'girl, long hair, grey hair, braid, grey eyes,\nwhite dress,')
            with self.assertRaises(ValueError):
                self.nai.parse('1girl\n[Character 1 = nobody]\n', cast)

    def test_defaults_are_the_free_tier_at_effort_high(self):
        sent = self.nai.payload('1girl, indoors,', ['girl, red hair'], width=832, height=1216, steps=23, seed=7)
        p = sent['parameters']
        self.assertEqual(sent['model'], 'nai-diffusion-5-full')
        self.assertEqual(sent['action'], 'generate')
        self.assertEqual((p['width'], p['height'], p['steps'], p['n_samples'], p['scale']), (832, 1216, 23, 1, 5))
        self.assertEqual((p['sampler'], p['noise_schedule'], p['image_format']), ('k_euler_ancestral', 'karras', 'png'))
        self.assertEqual(sent['input'], '1girl, indoors, very aesthetic, masterpiece, no text')
        self.assertEqual(p['v4_prompt']['caption']['base_caption'], sent['input'])
        self.assertEqual((p['qualityPresetId'], p['ucPresetId']), ('none', 'heavy'))
        self.assertTrue(p['negative_prompt'].startswith('lowres, artistic error'))
        self.assertNotIn('nsfw', p['negative_prompt'])
        self.assertEqual(p['v4_negative_prompt']['caption']['base_caption'], p['negative_prompt'])
        self.assertEqual(p['characterPrompts'][0]['prompt'], 'girl, red hair')
        self.assertEqual(p['v4_prompt']['caption']['char_captions'][0]['char_caption'], 'girl, red hair')
        self.assertEqual(len(p['v4_negative_prompt']['caption']['char_captions']), 1)
        self.assertEqual(p['seed'], 7)

    def test_nsfw_goes_into_the_uc_only_when_excluded_and_text_drops_no_text(self):
        sent = self.nai.payload('1girl', [], width=832, height=1216, steps=23, seed=1, no_nsfw=True, text=True)
        self.assertTrue(sent['parameters']['negative_prompt'].startswith('nsfw, lowres'))
        self.assertEqual(sent['input'], '1girl, very aesthetic, masterpiece')
        self.assertNotIn('logo', sent['parameters']['negative_prompt'])

    def test_zip_reading_takes_the_png_and_refuses_anything_else(self):
        self.assertEqual(self.nai.png_from_zip(zipped(('readme.txt', b'x'), ('image_0.png', png([])))), png([]))
        with self.assertRaises(ValueError):
            self.nai.png_from_zip(zipped(('image_0.png', b'not a png')))
        with self.assertRaises(ValueError):
            self.nai.png_from_zip(b'{"error": "not a zip"}')


class Script(unittest.TestCase):
    def run_script(self, *args, prompt='1girl, solo, window,\n[Character 1]\ngirl, black hair,\n', style=None, token=TOKEN, cast=None):
        server = HTTPServer(('127.0.0.1', 0), NovelAI)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'tools').mkdir()
        (root / 'notes/prompts').mkdir(parents=True)
        (root / 'tools/scene_image_nai.py').write_text(SCRIPT.read_text(encoding='utf-8'), encoding='utf-8')
        (root / 'notes/prompts/1.txt').write_text(prompt, encoding='utf-8')
        if cast is not None:
            (root / 'notes/prompts/cast').mkdir()
            (root / 'notes/prompts/cast/whisper.txt').write_text(cast, encoding='utf-8')
        if style is not None:
            (root / 'notes/style.txt').write_text(style, encoding='utf-8')
        env = {k: v for k, v in os.environ.items() if k != 'NOVELAI_TOKEN'}
        env['NOVELAI_IMAGE_URL'] = f'http://127.0.0.1:{server.server_port}'
        if token:
            env['NOVELAI_TOKEN'] = token
        seen.clear()
        done = subprocess.run([sys.executable, '-I', 'tools/scene_image_nai.py', 'notes/prompts/1.txt', *args],
                              cwd=root, env=env, capture_output=True, text=True)
        self.assertNotIn(TOKEN, done.stdout + done.stderr)
        return root, done

    def setUp(self):
        reply.clear()

    def test_one_png_lands_in_public_assets_and_the_seed_is_recorded(self):
        root, done = self.run_script('--size', 'landscape')
        self.assertEqual(done.returncode, 0, done.stderr)
        path, headers, sent = seen[0]
        self.assertEqual(path, '/ai/generate-image')
        self.assertEqual(headers['Authorization'], 'Bearer ' + TOKEN)
        self.assertTrue(headers['User-Agent'].startswith('couldhappen-scene-image/'))
        self.assertEqual((sent['parameters']['width'], sent['parameters']['height']), (1216, 832))
        name = done.stdout.strip()
        self.assertRegex(name, r'^scene-[0-9a-f]{16}\.png$')
        self.assertEqual((root / 'public/assets' / name).read_bytes(), png([]))
        prompt = (root / 'notes/prompts/1.txt').read_text(encoding='utf-8')
        self.assertTrue(prompt.endswith(f"seed: {sent['parameters']['seed']}\n"), prompt)

    def test_the_script_reads_cast_blocks_from_the_workspace(self):
        root, done = self.run_script(prompt='1girl, solo,\n[Character 1 = whisper]\n', cast='girl, grey hair, braid,\ngreen cloak,\n')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(seen[0][2]['parameters']['characterPrompts'][0]['prompt'], 'girl, grey hair, braid,\ngreen cloak,')

    def test_a_recorded_seed_is_replaced_and_reused_on_request(self):
        root, done = self.run_script('--seed', '42', prompt='1girl\nseed: 5\n')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(seen[0][2]['parameters']['seed'], 42)
        self.assertEqual((root / 'notes/prompts/1.txt').read_text(encoding='utf-8'), '1girl\nseed: 42\n')

    def test_the_director_choice_in_style_adds_nsfw_to_the_uc(self):
        root, done = self.run_script(style='painterly, soft light\nnsfw: no\n')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(seen[0][2]['parameters']['negative_prompt'].startswith('nsfw, '))
        self.assertNotIn('nsfw', seen[0][2]['input'])

    def test_settings_that_cost_anlas_are_refused_without_the_flag(self):
        for args in (['--size', '1024x1536'], ['--steps', '29']):
            root, done = self.run_script(*args)
            self.assertNotEqual(done.returncode, 0, args)
            self.assertIn('--spend-anlas', done.stderr)
            self.assertEqual(seen, [])
        root, done = self.run_script('--size', '1024x1536', '--steps', '28', '--spend-anlas')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(seen[0][2]['parameters']['height'], 1536)

    def test_ref_is_refused_with_a_clear_message_before_any_request(self):
        root, done = self.run_script('--ref', 'public/assets/portrait-a.png')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('does not take reference images', done.stderr)
        self.assertEqual(seen, [])

    def test_a_missing_token_stops_before_any_request(self):
        root, done = self.run_script(token=None)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('NOVELAI_TOKEN', done.stderr)
        self.assertEqual(seen, [])

    def test_a_refusal_reports_the_status_without_the_token_and_writes_nothing(self):
        reply.update(status=401, data=b'{"message": "Unauthorized ' + TOKEN.encode() + b'"}')
        root, done = self.run_script()
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('NovelAI error 401', done.stderr)
        self.assertFalse((root / 'public/assets').exists())
        self.assertNotIn('seed:', (root / 'notes/prompts/1.txt').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
