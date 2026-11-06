from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error
from uuid import uuid4

from helpers import bridge, files, runtime
from support import workspace
from test_cards import png


class Bridge(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        self.bridge = bridge.Bridge(self.root, 'http://127.0.0.1:5173')
        self.http = bridge.server(self.bridge)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)

    def request(self, route, data=None, origin='http://127.0.0.1:5173', extra=None):
        headers = {'Origin': origin, **(extra or {})}
        request = urllib.request.Request(self.bridge.address + route, headers=headers,
            data=json.dumps(data).encode() if data is not None else None)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None

    def payload(self, body='human text'):
        return {'schema_version': 1, 'workspace_id': self.bridge.config['workspace_id'], 'generation': self.bridge.generation,
                'channel': 'story', 'id': str(uuid4()), 'body': body}

    def raw(self, route):
        try:
            response = urllib.request.urlopen(self.bridge.address + route)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, response.read()

    def test_public_asset_route_revalidates_png_and_requires_reference(self):
        runtime.control(self.root, 'claim')
        assets = self.root / 'public/assets'
        assets.mkdir()
        (assets / 'portrait.png').write_bytes(png([]))
        self.assertEqual(self.request('/api/assets/portrait.png')[0], 404)
        files.write_json(self.root / 'public/cast.json', {'schema_version': 1, 'characters': [
            {'id': 'a', 'name': 'A', 'portrait': 'portrait.png'}]})
        self.bridge.refresh()
        self.assertEqual(self.raw('/api/assets/portrait.png'), (200, png([])))
        (assets / 'portrait.png').write_bytes(b'not a PNG')
        self.assertEqual(self.raw('/api/assets/portrait.png')[0], 404)
        self.assertTrue(self.bridge.view()['validation_error'])

    def test_start_closed_retry_conflicts_origin_and_etag(self):
        payload = self.payload()
        self.assertEqual(self.request('/api/entries', payload)[0], 423)
        runtime.control(self.root, 'claim')
        self.assertEqual(self.request('/api/entries', payload)[0], 201)
        # Lost receipt: same immutable request, one persisted entry.
        self.assertEqual(self.request('/api/entries', payload)[0], 200)
        self.assertEqual(len(files.snapshot(self.root)['story']), 1)
        self.assertEqual(self.request('/api/entries', {**payload, 'body': 'different'})[0], 409)
        self.assertEqual(self.request('/api/entries', self.payload(), origin='https://evil.test')[0], 403)
        self.assertEqual(self.request('/control', {'operation': 'claim'})[0], 403)
        self.assertEqual(self.request('/api/entries', self.payload('x' * (files.MAX_BODY+1)))[0], 413)
        view = self.bridge.view()
        self.assertEqual(self.request('/api/snapshot', extra={'If-None-Match': '"'+view['revision']+'"'})[0], 304)
        for path in ('/imports/source.json', '/.couldhappen/connection.json', '/api/assets/%2e%2e/private.png', '/api/assets/%2fetc.png'):
            self.assertEqual(self.request(path)[0], 404)

    def test_retry_of_saved_entry_succeeds_while_saving_is_closed(self):
        runtime.control(self.root, 'claim')
        payload = self.payload()
        self.assertEqual(self.request('/api/entries', payload)[0], 201)
        runtime.control(self.root, 'block', on=True)
        self.assertEqual(self.request('/api/entries', self.payload())[0], 423)
        self.assertEqual(self.request('/api/entries', payload)[0], 200)
        self.assertEqual(self.request('/api/entries', {**payload, 'body': 'different'})[0], 409)
        token = runtime.control(self.root, 'pause')['token']
        self.assertEqual(self.request('/api/entries', payload)[0], 200)
        self.assertEqual(self.request('/api/entries', self.payload())[0], 423)
        self.assertEqual(len(files.snapshot(self.root)['story']), 1)
        runtime.control(self.root, 'release', token=token)

    def test_release_requires_ownership(self):
        runtime.control(self.root, 'claim')
        token = runtime.control(self.root, 'pause')['token']
        runtime.control(self.root, 'invalidate', token=token)
        self.bridge.state['owner'] = False  # ownership lost while the token is still held
        with self.assertRaises(files.Invalid):
            self.bridge.control({'operation': 'release', 'token': token})
        self.assertTrue(self.bridge.state['paused'])

    def test_invalidate_requires_ownership(self):
        runtime.control(self.root, 'claim')
        token = runtime.control(self.root, 'pause')['token']
        self.bridge.state['owner'] = False  # ownership lost while the token is still held
        generation = self.bridge.generation
        with self.assertRaises(files.Invalid):
            self.bridge.control({'operation': 'invalidate', 'token': token})
        self.assertEqual(self.bridge.generation, generation)

    def test_close_refuses_while_paused(self):
        runtime.control(self.root, 'claim')
        token = runtime.control(self.root, 'pause')['token']
        with self.assertRaises(files.Invalid):
            self.bridge.control({'operation': 'close'})
        self.assertTrue(self.bridge.state['owner'])
        self.assertTrue(self.bridge.state['paused'])
        runtime.control(self.root, 'release', token=token)

    def test_close_refuses_invalid_public_records_without_disarming(self):
        runtime.control(self.root, 'claim')
        story = self.root / 'public/story.md'
        story.write_text('# Story\n\npartial', encoding='utf-8')
        with self.assertRaises(files.Invalid):
            self.bridge.control({'operation': 'close'})
        self.assertTrue(self.bridge.state['owner'])
        story.write_text('# Story\n', encoding='utf-8')
        self.bridge.refresh()
        self.assertFalse(self.bridge.error)

    def test_pause_drains_real_accepted_append_and_preserves_both(self):
        runtime.control(self.root, 'claim')
        entered, finish = threading.Event(), threading.Event()
        original = files.atomic
        def blocked_atomic(path, data):
            if str(path).endswith('story.md'):
                entered.set()
                if not finish.wait(5):
                    raise RuntimeError('test barrier timeout')
            original(path, data)
        with ThreadPoolExecutor(2) as pool, patch('helpers.files.atomic', blocked_atomic):
            saving = pool.submit(self.request, '/api/entries', self.payload())
            self.assertTrue(entered.wait(3))
            pausing = pool.submit(runtime.control, self.root, 'pause')
            deadline = time.monotonic()+3
            while not self.bridge.state['paused'] and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertFalse(pausing.done())
            self.assertEqual(self.request('/api/entries', self.payload('later'))[0], 423)
            finish.set()
            self.assertEqual(saving.result()[0], 201)
            token = pausing.result()['token']
        path = self.root / 'public/story.md'
        files.atomic(path, path.read_text(encoding='utf-8') + '\n' + files.entry('writer answer'))
        runtime.control(self.root, 'release', token=token)
        self.assertEqual([e['body'] for e in files.snapshot(self.root)['story']], ['human text', 'writer answer'])

    def test_recovery_wait_partial_save_and_generation(self):
        runtime.control(self.root, 'claim')
        self.request('/api/entries', self.payload('old pending'))
        old = self.payload('retained draft')
        token = runtime.control(self.root, 'pause')['token']
        question = str(uuid4())
        files.atomic(self.root / 'public/director.md', '# Director\n' + files.entry('New direction?', id=question))
        files.write_json(self.root / 'public/work.json', {'schema_version': 1, 'mode': 'awaiting_director', 'director_question_id': question})
        runtime.control(self.root, 'invalidate', token=token)
        runtime.control(self.root, 'release', token=token)
        self.assertEqual(self.request('/api/entries', old)[0], 409)
        self.assertEqual(runtime.control(self.root, 'wait-view')['entries'], [])
        director = {**self.payload('try a different tone'), 'channel': 'director'}
        self.assertEqual(self.request('/api/entries', director)[0], 201)
        self.assertEqual(runtime.control(self.root, 'wait-view')['entries'], [{'channel': 'director', 'id': director['id']}])
        coherent = self.bridge.view()
        files.atomic(self.root / 'public/director.md', '# Director\npartial')
        invalid = self.bridge.view()
        self.assertEqual(invalid['director'], coherent['director'])
        self.assertTrue(invalid['validation_error'])
        self.assertFalse(invalid['permissions']['director']['allowed'])

    def test_restart_requires_explicit_boundary_and_keeps_block(self):
        runtime.control(self.root, 'claim')
        runtime.control(self.root, 'block', on=True)
        restarted = bridge.Bridge(self.root, 'http://127.0.0.1:5173')
        self.assertFalse(restarted.view()['permissions']['director']['allowed'])
        self.assertTrue(restarted.state['production'])
        with self.assertRaises(files.Invalid):
            restarted.control({'operation': 'claim'})
        restarted.address = self.bridge.address
        restarted.control({'operation': 'recover', 'previous_writer_stopped': True})
        self.assertTrue(restarted.view()['permissions']['director']['allowed'])

    def test_save_failure_and_owned_token(self):
        runtime.control(self.root, 'claim')
        story = self.root / 'public/story.md'
        before = story.read_bytes()
        with patch('helpers.files.os.replace', side_effect=OSError('disk unavailable')):
            self.assertEqual(self.request('/api/entries', self.payload())[0], 503)
        self.assertEqual(story.read_bytes(), before)
        self.assertEqual(list(story.parent.glob('.couldhappen-tmp-*')), [])
        token = runtime.control(self.root, 'pause')['token']
        with self.assertRaises(files.Invalid):
            self.bridge.control({'operation': 'release', 'token': 'wrong'})
        runtime.control(self.root, 'block', on=True)
        runtime.control(self.root, 'release', token=token)
        self.assertFalse(self.bridge.view()['permissions']['director']['allowed'])
