"""Local connection and cooperative ownership; never a writer supervisor."""
import json
import os
from pathlib import Path
import secrets
import time
import urllib.request
from uuid import uuid4

from .files import Invalid, read_json, write_json, uuid


def identity(root):
    path = Path(root) / 'couldhappen.json'
    config = read_json(path)
    if config.get('schema_version') != 1:
        raise Invalid('Unsupported workspace contract')
    if config.get('workspace_id') is None:
        config['workspace_id'] = str(uuid4())
        write_json(path, config)
    uuid(config['workspace_id'])
    return config


class WorkspaceLock:
    """OS lock prevents concurrency; a crash marker still needs explicit inspection."""
    def __init__(self, root, recover=False):
        folder = Path(root) / '.couldhappen'
        folder.mkdir(exist_ok=True)
        self.path = folder / 'bridge.lock'
        existed = self.path.exists()
        self.file = self.path.open('a+b')
        try:
            self.file.seek(0)
            if os.name == 'nt':
                import msvcrt
                if self.path.stat().st_size == 0:
                    self.file.write(b'0')
                    self.file.flush()
                    self.file.seek(0)
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise Invalid('Another helper owns this workspace') from None
        if existed and not recover:
            self.file.close()
            raise Invalid('Interrupted helper lock: establish former helper stopped, then use --previous-helper-stopped')

    def close(self):
        self.file.close()
        self.path.unlink(missing_ok=True)


def control(root, operation, **payload):
    connection = read_json(Path(root) / '.couldhappen/connection.json')
    request = urllib.request.Request(connection['address'] + '/control',
        data=json.dumps({'operation': operation, **payload}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + connection['secret']})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        with exc:
            error = json.load(exc)
        raise Invalid(error.get('message', str(exc))) from None


def stop(root, timeout=15):
    """Ask the running helper to shut down, then wait until it has released its lock."""
    result = control(root, 'stop')
    lock = Path(root) / '.couldhappen/bridge.lock'
    deadline = time.monotonic() + timeout
    while lock.exists():
        if time.monotonic() > deadline:
            return {'status': 'error', 'message': 'Helper did not release its lock in time; inspect its process'}
        time.sleep(.1)
    result['status'] = 'stopped'
    return result


def eligible(view):
    result = []
    awaiting = view['work']['mode'] == 'awaiting_director'
    for channel in ('story', 'director'):
        if awaiting and channel == 'story':
            continue
        after = not awaiting
        for item in view[channel]:
            if item['id'] == view['work']['director_question_id']:
                after = True
                continue
            if after and item['role'] == 'human' and item['status'] == 'pending':
                result.append({'channel': channel, 'id': item['id']})
    return result


def wait(root, timeout=0):
    start = time.monotonic()
    while True:
        result = control(root, 'wait-view')
        if result.get('entries'):
            return result, 0
        if timeout > 0 and time.monotonic() - start >= timeout:
            return {'status': 'timeout', 'generation': result['generation']}, 3
        time.sleep(.5)


def secret():
    return secrets.token_hex(32)
