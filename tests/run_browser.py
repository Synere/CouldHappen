"""Isolated services and synthetic public data. Never starts a model or play session."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helpers import files, runtime
from test_cards import png
from support import EMPTY_CONFIG

REPO = Path(__file__).resolve().parents[1]


def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def await_url(url, process):
    deadline = time.monotonic()+30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('Test service exited before readiness')
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(.1)
    raise RuntimeError('Test service readiness timeout')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--node', default=shutil.which('node'))
    args = parser.parse_args()
    processes = []
    with tempfile.TemporaryDirectory(prefix='couldhappen-browser-') as folder:
        root = Path(folder)
        (root / 'public/assets').mkdir(parents=True)
        files.write_json(root / 'couldhappen.json', EMPTY_CONFIG)
        story = '# Story\n\n'
        for n in range(18):
            story += files.entry(f'Synthetic browser fixture, passage {n+1}.\n\nThe door stands open beside the river. This text tests sustained reading and is not a supplied scene. ' * 3)
        files.atomic(root / 'public/story.md', story)
        files.atomic(root / 'public/director.md', '# Director\n')
        files.write_json(root / 'public/work.json', {'schema_version': 1, 'mode': 'play', 'director_question_id': None})
        files.atomic(root / 'public/assets/fixture.png', png([]))
        files.write_json(root / 'public/cast.json', {'schema_version': 1, 'characters': [
            {'id': 'fixture', 'name': 'Synthetic cast fixture', 'description': 'A test image; no real card was supplied.', 'portrait': 'fixture.png'},
            {'id': 'no-portrait', 'name': 'Character without portrait'}]})
        files.atomic(root / 'private.md', 'PRIVATE_BOUNDARY_FIXTURE')
        origin = f'http://127.0.0.1:{port()}'
        env = {**os.environ, 'COULDHAPPEN_ROOT': str(root), 'COULDHAPPEN_TEST_ROOT': str(root),
               'COULDHAPPEN_TEST_URL': origin, 'COULDHAPPEN_TEST_PYTHON': args.python}
        output = REPO / 'web/test-results'
        output.mkdir(exist_ok=True)
        # Playwright clears test-results on startup. Keep the open Windows log
        # outside that directory so cleanup cannot stall on a sharing violation.
        with (root / 'services.log').open('w', encoding='utf-8') as log:
            try:
                helper = subprocess.Popen([args.python, '-m', 'helpers', 'serve', '--root', str(root), '--frontend-origin', origin], cwd=REPO, stdout=log, stderr=log)
                processes.append(helper)
                deadline = time.monotonic()+10
                while not (root / '.couldhappen/connection.json').exists():
                    if time.monotonic() > deadline or helper.poll() is not None:
                        raise RuntimeError('Helper connection unavailable')
                    time.sleep(.1)
                await_url(files.read_json(root / '.couldhappen/connection.json')['address']+'/api/snapshot', helper)
                runtime.control(root, 'claim')
                vite = subprocess.Popen([args.node, str(REPO / 'web/node_modules/vite/bin/vite.js'), '--host', '127.0.0.1', '--port', origin.rsplit(':', 1)[1], '--strictPort'], cwd=REPO / 'web', env=env, stdout=log, stderr=log)
                processes.append(vite)
                await_url(origin, vite)
                return subprocess.run([args.node, str(REPO / 'web/node_modules/@playwright/test/cli.js'), 'test'], cwd=REPO / 'web', env=env).returncode
            finally:
                for process in reversed(processes):
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == '__main__':
    sys.exit(main())
