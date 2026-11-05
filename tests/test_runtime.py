import contextlib
import io
import json
import os
import threading
import time
import unittest
from unittest.mock import patch

from helpers import __main__ as cli
from helpers import bridge, files, runtime
from support import workspace


class Locks(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)

    def test_exclusive_and_stale_lock_requires_explicit_recovery(self):
        lock = runtime.WorkspaceLock(self.root)
        marker = self.root / '.couldhappen/bridge.lock'
        self.assertTrue(marker.exists())
        with self.assertRaises(files.Invalid) as caught:
            runtime.WorkspaceLock(self.root)
        self.assertIn('Another helper owns', str(caught.exception))
        lock.close()
        self.assertFalse(marker.exists())

        marker.write_bytes(b'stale lock content')
        old = time.time() - 86400
        os.utime(marker, (old, old))
        with self.assertRaises(files.Invalid) as caught:
            runtime.WorkspaceLock(self.root)
        self.assertIn('Interrupted helper lock', str(caught.exception))
        self.assertTrue(marker.exists())
        recovered = runtime.WorkspaceLock(self.root, recover=True)
        recovered.close()
        self.assertFalse(marker.exists())

    def test_generated_secret_is_safe_as_a_cli_value(self):
        value = runtime.secret()
        self.assertTrue(value)
        self.assertFalse(value.startswith('-'))


class Wait(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        self.bridge = bridge.Bridge(self.root, 'http://127.0.0.1:5173')
        self.http = bridge.server(self.bridge)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)

    def test_bounded_timeout_and_closed_helper_error(self):
        with self.assertRaises(files.Invalid):
            runtime.wait(self.root, 0.1)
        runtime.control(self.root, 'claim')
        started = time.monotonic()
        result, code = runtime.wait(self.root, 0.6)
        elapsed = time.monotonic() - started
        self.assertEqual((result['status'], code), ('timeout', 3))
        self.assertIn('generation', result)
        self.assertGreaterEqual(elapsed, 0.5)
        self.assertLess(elapsed, 2.5)

    def test_cli_rejects_negative_timeout_and_missing_helper_as_errors(self):
        with patch('sys.argv', ['helpers', 'wait', '--root', str(self.root), '--timeout', '-1']):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = cli.main()
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['status'], 'error')
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        with patch('sys.argv', ['helpers', 'wait', '--root', str(root), '--timeout', '1']):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = cli.main()
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['status'], 'error')


class Stop(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)

    def start(self):
        thread = threading.Thread(target=bridge.serve, args=(self.root, 'http://127.0.0.1:5173'), daemon=True)
        with contextlib.redirect_stdout(io.StringIO()):
            thread.start()
            deadline = time.monotonic() + 10
            while not (self.root / '.couldhappen/connection.json').exists():
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.05)
            time.sleep(.2)
        return thread

    def test_stop_shuts_down_and_releases_the_lock(self):
        thread = self.start()
        result = runtime.stop(self.root)
        self.assertEqual((result['status'], result['clean'], result['next_start']), ('stopped', True, 'writer claim'))
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertFalse((self.root / '.couldhappen/bridge.lock').exists())
        # After a clean stop, a restart needs no --previous-helper-stopped.
        thread = self.start()
        runtime.stop(self.root)
        thread.join(5)
        self.assertFalse(thread.is_alive())

    def test_stop_while_owned_reports_that_recovery_is_needed(self):
        thread = self.start()
        runtime.control(self.root, 'claim')
        result = runtime.stop(self.root)
        self.assertFalse(result['clean'])
        self.assertEqual(result['next_start'], 'writer recover --previous-writer-stopped')
        thread.join(5)
        self.assertFalse(thread.is_alive())


class Encoding(unittest.TestCase):
    def test_entry_output_is_utf8_on_a_legacy_console(self):
        import subprocess
        import sys
        from support import REPO
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        body = root / 'body.txt'
        body.write_text('A dash — and été.\n', encoding='utf-8')
        env = {**os.environ, 'PYTHONIOENCODING': 'cp1252', 'PYTHONUTF8': '0'}
        result = subprocess.run([sys.executable, '-m', 'helpers', 'entry', '--body-file', str(body)],
                                cwd=REPO, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('—'.encode('utf-8'), result.stdout)
