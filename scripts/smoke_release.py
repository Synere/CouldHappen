"""Smoke-test a CouldHappen release ZIP the way a player would set it up.

This is a maintainer tool, not part of the release. It unpacks the ZIP into a
fresh temporary folder outside any Git repository, follows the README's Start
steps (npm ci, validate, helper, Vite, claim, browser snapshot, Git baseline,
checkpoint), confirms a quiet wait times out, and then runs the package's own
test suites. It stops every service it started and never touches a real story.

    python scripts/smoke_release.py release/dist/couldhappen-<version>.zip
    python scripts/smoke_release.py <zip> --keep      # keep the folder to inspect
    python scripts/smoke_release.py <zip> --skip-browser

Exit status is 0 only if every step passed.
"""
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
import zipfile

DEV_ONLY = '<!-- dev-only -->'


class Failed(Exception):
    pass


class Smoke:
    def __init__(self, workspace, python, node, npm):
        self.root = workspace
        self.python, self.node, self.npm = python, node, npm
        self.processes = []
        self.results = []
        self.log = (workspace.parent / 'services.log').open('w', encoding='utf-8')

    def step(self, name, check):
        started = time.monotonic()
        try:
            detail = check() or ''
            self.results.append((True, name, detail))
            print(f'PASS  {name}' + (f' ({detail})' if detail else ''), flush=True)
        except Exception as exc:  # report every failure the same way
            self.results.append((False, name, str(exc)))
            print(f'FAIL  {name}: {exc}', flush=True)
            raise Failed(name) from exc
        finally:
            self.elapsed = time.monotonic() - started

    def run(self, *args, cwd=None, expect=0):
        result = subprocess.run(list(args), cwd=cwd or self.root, capture_output=True, text=True,
                                encoding='utf-8', errors='replace')
        if result.returncode != expect:
            tail = (result.stdout + result.stderr).strip().splitlines()[-8:]
            raise RuntimeError(f'exit {result.returncode} (expected {expect}): ' + ' | '.join(tail))
        return result.stdout

    def helper(self, *args, expect=0):
        return self.run(self.python, '-m', 'helpers', *args, '--root', '.', expect=expect)

    def start(self, args, cwd):
        process = subprocess.Popen(args, cwd=cwd, stdout=self.log, stderr=self.log)
        self.processes.append(process)
        return process

    def stop(self):
        for process in reversed(self.processes):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        self.processes.clear()
        self.log.close()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def fetch_json(url, process, timeout=30):
    deadline = time.monotonic() + timeout
    while True:
        if process.poll() is not None:
            raise RuntimeError(f'service exited with {process.returncode}; see services.log')
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return json.loads(response.read())
        except (OSError, ValueError):
            if time.monotonic() > deadline:
                raise RuntimeError(f'{url} did not answer within {timeout}s')
            time.sleep(0.25)


def inside_git_repo(path):
    result = subprocess.run(['git', '-C', str(path), 'rev-parse', '--show-toplevel'], capture_output=True)
    return result.returncode == 0


def smoke(zip_path, base, args):
    workspace = base / 'workspace'
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(workspace)
    s = Smoke(workspace, args.python, args.node, args.npm)
    config = lambda: json.loads((workspace / 'couldhappen.json').read_text(encoding='utf-8'))
    try:
        s.step('outside any Git repository', lambda: (_ for _ in ()).throw(RuntimeError('folder is inside a repository'))
               if inside_git_repo(workspace) else None)
        s.step('release metadata', lambda: 'version ' + json.loads((workspace / 'release.json').read_text())['version'])
        s.step('workspace UUID starts null', lambda: None if config()['workspace_id'] is None else
               (_ for _ in ()).throw(RuntimeError('UUID already set')))

        def no_dev_text():
            hits = [str(p.relative_to(workspace)) for p in workspace.rglob('*.md')
                    if 'node_modules' not in p.parts and DEV_ONLY in p.read_text(encoding='utf-8')]
            if hits:
                raise RuntimeError('dev-only marker in ' + ', '.join(hits))
        s.step('no development-only text shipped', no_dev_text)

        # Player setup, following the README's Start steps.
        s.step('npm ci', lambda: s.run(s.npm, 'ci', '--no-audit', '--no-fund', cwd=workspace / 'web') and None)
        s.step('validate', lambda: s.helper('validate') and None)
        origin = f'http://127.0.0.1:{free_port()}'

        def start_helper():
            helper = s.start([s.python, '-m', 'helpers', 'serve', '--root', '.', '--frontend-origin', origin], workspace)
            connection = workspace / '.couldhappen/connection.json'
            deadline = time.monotonic() + 15
            while not connection.exists():
                if helper.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('helper did not publish its connection; see services.log')
                time.sleep(0.1)
            address = json.loads(connection.read_text(encoding='utf-8'))['address']
            fetch_json(address + '/api/snapshot', helper)
            return address
        s.step('start helper', start_helper)
        s.step('writer claim', lambda: s.helper('writer', 'claim') and None)
        s.step('helper start set the workspace UUID', lambda: config()['workspace_id'] or
               (_ for _ in ()).throw(RuntimeError('UUID still null')))

        def start_reader():
            vite = s.start([s.node, str(workspace / 'web/node_modules/vite/bin/vite.js'), '--host', '127.0.0.1',
                            '--port', origin.rsplit(':', 1)[1], '--strictPort'], workspace / 'web')
            snapshot = fetch_json(origin + '/api/snapshot', vite)
            if snapshot.get('workspace_id') != config()['workspace_id']:
                raise RuntimeError('reader snapshot belongs to a different workspace')
            return origin
        s.step('start reader and match its snapshot', start_reader)
        s.step('quiet wait times out (exit 3)', lambda: s.helper('wait', '--timeout', '2', expect=3) and None)

        def baseline():
            identity = ['-c', 'user.name=CouldHappen smoke test', '-c', 'user.email=smoke@example.invalid']
            s.run('git', 'init', '-q')
            top = Path(s.run('git', 'rev-parse', '--show-toplevel').strip()).resolve()
            if top != workspace.resolve():
                raise RuntimeError(f'Git top level is {top}')
            s.run('git', 'add', '-A')
            s.run('git', *identity, 'commit', '-q', '-m', 'Baseline')
            count = s.run('git', 'rev-list', '--count', 'HEAD').strip()
            if count != '1':
                raise RuntimeError(f'{count} commits, expected 1')
        s.step('Git baseline commit', baseline)
        s.step('checkpoint clean', lambda: None if json.loads(s.helper('checkpoint', 'check'))['status'] == 'clean'
               else (_ for _ in ()).throw(RuntimeError('checkpoint not clean')))
        s.stop()

        # The package's own checks.
        s.step('Python tests', lambda: s.run(s.python, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py')
               and None)
        s.step('reader check', lambda: s.run(s.npm, 'run', 'check', cwd=workspace / 'web') and None)
        s.step('reader unit tests', lambda: s.run(s.npm, 'run', 'test:unit', cwd=workspace / 'web') and None)
        s.step('reader build', lambda: s.run(s.npm, 'run', 'build', cwd=workspace / 'web') and None)
        if not args.skip_browser:
            s.step('Chromium browser tests', lambda: s.run(s.python, 'tests/run_browser.py', '--python', s.python,
                                                            '--node', s.node) and None)
    except Failed:
        pass
    finally:
        if s.processes or not s.log.closed:
            s.stop()
    failed = [name for ok, name, _ in s.results if not ok]
    print()
    print(f'{len(s.results) - len(failed)} passed, {len(failed)} failed' + (f': {failed[0]}' if failed else ''))
    return 1 if failed else 0


def remove_tree(path):
    """Delete the temporary folder, including Git's read-only object files on Windows."""
    def retry(function, target, _):
        os.chmod(target, 0o700)
        function(target)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def main():
    parser = argparse.ArgumentParser(description='Smoke-test a CouldHappen release ZIP as a player would set it up')
    parser.add_argument('zip', help='Path to couldhappen-<version>.zip')
    parser.add_argument('--keep', action='store_true', help='Keep the unpacked workspace and print its path')
    parser.add_argument('--skip-browser', action='store_true', help='Skip the Chromium tests')
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--node', default=shutil.which('node'))
    parser.add_argument('--npm', default=shutil.which('npm'))
    args = parser.parse_args()
    if not args.node or not args.npm:
        parser.error('node and npm must be on PATH (or pass --node/--npm)')
    zip_path = Path(args.zip).resolve()
    base = Path(tempfile.mkdtemp(prefix='couldhappen-smoke-'))
    try:
        if inside_git_repo(base):
            print(f'Temporary folder {base} is inside a Git repository; set TMP to a folder outside one.')
            return 2
        return smoke(zip_path, base, args)
    finally:
        if args.keep:
            print(f'Workspace kept at {base / "workspace"}')
        else:
            remove_tree(base)


if __name__ == '__main__':
    sys.exit(main())
