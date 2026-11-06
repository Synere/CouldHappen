"""Narrow loopback HTTP bridge with draining, acknowledged edit pauses."""
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from . import files, runtime


class Failure(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


class Bridge:
    def __init__(self, root, origin):
        self.root = Path(root).resolve()
        parsed = urlsplit(origin)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost') or parsed.path not in ('', '/') or not parsed.port:
            raise files.Invalid('Frontend origin must be an explicit loopback HTTP port')
        self.origin = origin.rstrip('/')
        self.config = runtime.identity(self.root)
        self.generation = str(uuid4())
        self.secret = runtime.secret()
        self.condition = threading.Condition(threading.RLock())
        self.write_lock = threading.Lock()
        self.accepted = 0
        self.closing = True
        self.valid = None
        self.error = None
        path = self.root / '.couldhappen/control.json'
        self.state = files.read_json(path) if path.exists() else {'owner': False, 'paused': False, 'production': False, 'armed': False}
        self.interrupted = bool(self.state['owner'] or self.state['paused'] or self.state['production'])
        self.token = None
        self.httpd = None
        self.refresh()
        self.persist()

    def persist(self):
        files.write_json(self.root / '.couldhappen/control.json', self.state)

    def refresh(self):
        try:
            self.valid = files.snapshot(self.root)
            self.error = None
        except (OSError, ValueError, TypeError, KeyError) as exc:
            # Absolute paths and private diagnostics do not cross to the browser.
            self.error = 'Saved public records are invalid; writer inspection required.'
            self.diagnostic = str(exc)

    def permission(self, channel):
        if self.error:
            return self.error
        if self.closing or not self.state['owner']:
            return 'Writer ownership must be established before saving.'
        if self.state['paused']:
            return 'Saving paused for writer edits.'
        if self.state['production']:
            return 'Saving paused while the writer composes.'
        if self.valid and self.valid['work']['mode'] == 'awaiting_director' and channel == 'story':
            return 'Awaiting Director direction.'
        return None

    def view(self):
        with self.condition:
            if not self.state['paused']:
                with self.write_lock:
                    self.refresh()
            result = copy.deepcopy(self.valid) if self.valid else {
                'story': [], 'director': [], 'cast': {'schema_version': 1, 'characters': []}, 'assets': {},
                'work': {'schema_version': 1, 'mode': 'play', 'director_question_id': None}}
            result.update(schema_version=1, workspace_id=self.config['workspace_id'], generation=self.generation,
                          poll_interval_ms=self.config['poll_interval_ms'], validation_error=self.error)
            result['permissions'] = {ch: {'allowed': self.permission(ch) is None, 'reason': self.permission(ch)} for ch in ('story', 'director')}
            result['revision'] = files.digest(json.dumps(result, sort_keys=True))
            return result

    def submit(self, payload):
        try:
            if set(payload) != {'schema_version', 'workspace_id', 'generation', 'channel', 'id', 'body'}:
                raise files.Invalid('Unsupported submission fields')
            files.uuid(payload['id'])
            if payload['channel'] not in ('story', 'director') or not isinstance(payload['body'], str):
                raise files.Invalid('Invalid channel or body')
            body = files.normalize(payload['body'])
            if not body.strip():
                raise files.Invalid('Write something before saving.')
            if len(body.encode()) > files.MAX_BODY:
                raise Failure(413, 'body_too_large', 'Message exceeds 256 KiB; your draft is retained.')
        except (files.Invalid, TypeError, KeyError) as exc:
            raise Failure(400, 'invalid_input', str(exc)) from None
        with self.condition:
            if payload['schema_version'] != 1 or payload['workspace_id'] != self.config['workspace_id'] or payload['generation'] != self.generation:
                raise Failure(409, 'stale_generation', 'Workspace changed. Reread before deliberately submitting your retained draft.')
            # A retry of an already-saved entry succeeds even while saving is closed.
            existing = self.existing(payload, body)
            if existing:
                return existing, 200
            reason = self.permission(payload['channel'])
            if reason:
                raise Failure(423, 'saving_closed', reason)
            self.accepted += 1
        try:
            with self.write_lock:
                try:
                    view = files.snapshot(self.root)
                    for ch in ('story', 'director'):
                        for item in view[ch]:
                            if item['id'] == payload['id']:
                                if ch != payload['channel'] or item['role'] != 'human' or item['body'] != body:
                                    raise Failure(409, 'id_conflict', 'This request ID already belongs to different text or a different channel.')
                                return {'id': item['id'], 'status': 'saved'}, 200
                    path = self.root / f'public/{payload["channel"]}.md'
                    text = files.normalize(path.read_text(encoding='utf-8'))
                    files.atomic(path, text.rstrip('\n') + '\n\n' + files.entry(body, 'human', payload['id']))
                    self.valid = files.snapshot(self.root)
                    return {'id': payload['id'], 'status': 'saved'}, 201
                except Failure:
                    raise
                except (OSError, ValueError, TypeError, KeyError):
                    self.error = 'Public save failed; writer inspection required. Your draft is retained.'
                    raise Failure(503, 'save_failed', self.error) from None
        finally:
            with self.condition:
                self.accepted -= 1
                self.condition.notify_all()

    def existing(self, payload, body):
        try:
            view = files.snapshot(self.root)  # writes replace files atomically, so no write lock
        except (OSError, ValueError, TypeError, KeyError):
            return None  # permission() reports the invalid state
        for ch in ('story', 'director'):
            for item in view[ch]:
                if item['id'] == payload['id']:
                    if ch != payload['channel'] or item['role'] != 'human' or item['body'] != body:
                        raise Failure(409, 'id_conflict', 'This request ID already belongs to different text or a different channel.')
                    return {'id': item['id'], 'status': 'saved'}
        return None

    def control(self, data):
        op = data.get('operation')
        with self.condition:
            if op == 'pause':
                if not self.state['owner'] or self.closing:
                    raise files.Invalid('Claim safe writer ownership first')
                if self.state['paused']:
                    raise files.Invalid('Already paused; inspect interrupted ownership rather than replacing its token')
                self.state['paused'] = True
                self.persist()
                while self.accepted:
                    self.condition.wait()
                self.token = runtime.secret()
                return {'token': self.token, 'status': 'paused'}
            if op == 'release':
                if not self.state['owner'] or self.closing:
                    raise files.Invalid('Claim safe writer ownership first')
                if not self.token or data.get('token') != self.token:
                    raise files.Invalid('Matching edit-owner token required')
                self.refresh()
                if self.error:
                    raise files.Invalid(self.diagnostic)
                self.state['paused'] = False
                self.token = None
            elif op in ('claim', 'recover'):
                if op == 'claim' and (self.interrupted or self.state['owner']):
                    raise files.Invalid('Existing ownership requires explicit recovery after the former writer stopped')
                if op == 'recover' and not data.get('previous_writer_stopped'):
                    raise files.Invalid('Establish the former writer/delegates stopped, then assert --previous-writer-stopped')
                self.closing = True
                while self.accepted:
                    self.condition.wait()
                self.refresh()
                if self.error:
                    raise files.Invalid(self.diagnostic)
                self.state.update(owner=True, paused=False, production=False, armed=True)
                self.token = None
                self.closing = False
                self.interrupted = False
                if op == 'recover':
                    self.generation = str(uuid4())
                    self.publish_connection()
            elif op == 'block':
                if not self.state['owner'] or self.closing:
                    raise files.Invalid('Claim safe writer ownership first')
                self.state['production'] = bool(data['on'])
            elif op == 'invalidate':
                if not self.state['owner'] or self.closing:
                    raise files.Invalid('Claim safe writer ownership first')
                if not self.token or data.get('token') != self.token:
                    raise files.Invalid('Invalidation requires the owned pause token')
                self.generation = str(uuid4())
                self.publish_connection()
            elif op == 'close':
                from .checkpoints import check
                if self.state['paused']:
                    raise files.Invalid('Release the edit pause before closing')
                self.closing = True
                while self.accepted:
                    self.condition.wait()
                self.refresh()
                if self.error:
                    self.closing = False
                    raise files.Invalid(self.diagnostic)
                result, code = check(self.root)
                if code:
                    self.closing = False
                    return result
                self.state.update(owner=False, armed=False)
            elif op == 'stop':
                # Drain accepted saves, then shut down after this response is sent.
                self.closing = True
                while self.accepted:
                    self.condition.wait()
                self.persist()
                if self.httpd:
                    threading.Thread(target=self.httpd.shutdown, daemon=True).start()
                owned = bool(self.state['owner'] or self.state['paused'] or self.state['production'])
                return {'status': 'stopping', 'clean': not owned,
                        'next_start': 'writer recover --previous-writer-stopped' if owned else 'writer claim'}
            elif op == 'wait-view':
                if self.state['paused']:
                    return {'generation': self.generation, 'entries': []}
                view = self.view()
                if self.error or self.closing or not self.state['owner']:
                    raise files.Invalid('Invalid or unowned workspace requires recovery before waiting')
                return {'generation': self.generation, 'entries': runtime.eligible(view)}
            else:
                raise files.Invalid('Unknown writer control')
            self.persist()
            return {'status': 'ok', 'generation': self.generation}

    def publish_connection(self):
        files.write_json(self.root / '.couldhappen/connection.json', {
            'address': self.address, 'workspace_id': self.config['workspace_id'],
            'generation': self.generation, 'secret': self.secret, 'frontend_origin': self.origin})


def server(bridge, port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, value=None, headers=None):
            body = b'' if value is None else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            for key, val in (headers or {}).items():
                self.send_header(key, val)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(body)

        def check_host(self):
            if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
                raise Failure(403, 'host_denied', 'Loopback Host required')

        def do_GET(self):
            try:
                self.check_host()
                path = unquote(urlsplit(self.path).path)
                if path == '/api/snapshot':
                    view = bridge.view()
                    tag = '"' + view['revision'] + '"'
                    return self.respond(304 if self.headers.get('If-None-Match') == tag else 200,
                                        None if self.headers.get('If-None-Match') == tag else view, {'ETag': tag})
                if path.startswith('/api/assets/'):
                    relative = path[len('/api/assets/'):]
                    view = bridge.view()
                    if relative not in view['assets']:
                        raise files.Invalid('Asset is not publicly referenced')
                    data = files.public_asset(bridge.root, relative)
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self.respond(404, {'code': 'not_found', 'message': 'Unknown public route'})
            except Failure as exc:
                self.respond(exc.status, {'code': exc.code, 'message': exc.message})
            except (OSError, ValueError):
                self.respond(404, {'code': 'asset_denied', 'message': 'Public asset unavailable'})

        def do_POST(self):
            try:
                self.check_host()
                route = urlsplit(self.path).path
                if route == '/control':
                    if self.headers.get('Authorization') != 'Bearer ' + bridge.secret or self.headers.get('Origin'):
                        raise Failure(403, 'control_denied', 'Writer authorization required')
                elif route == '/api/entries':
                    if self.headers.get('Origin') != bridge.origin:
                        raise Failure(403, 'origin_denied', 'Expected frontend Origin required')
                else:
                    raise Failure(404, 'not_found', 'Unknown route')
                length = int(self.headers.get('Content-Length', '-1'))
                if length < 0 or length > files.MAX_BODY * 6 + 4096:
                    raise Failure(413, 'request_too_large', 'Request exceeds the bounded JSON limit')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise files.Invalid('Expected JSON object')
                if route == '/control':
                    return self.respond(200, bridge.control(data))
                value, status = bridge.submit(data)
                self.respond(status, value)
            except Failure as exc:
                self.respond(exc.status, {'code': exc.code, 'message': exc.message})
            except (ValueError, KeyError, TypeError) as exc:
                self.respond(400, {'code': 'invalid_input', 'message': str(exc)})
            except OSError:
                self.respond(503, {'code': 'control_failed', 'message': 'Local operation failed; inspect host diagnostics'})

    httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    httpd.daemon_threads = True
    bridge.httpd = httpd
    bridge.address = f'http://127.0.0.1:{httpd.server_port}'
    bridge.publish_connection()
    return httpd


def serve(root, origin, previous_helper_stopped=False):
    lock = runtime.WorkspaceLock(root, previous_helper_stopped)
    httpd = None
    try:
        old = Path(root) / '.couldhappen/connection.json'
        port = urlsplit(files.read_json(old)['address']).port if old.exists() else 0
        bridge = Bridge(root, origin)
        try:
            httpd = server(bridge, port)
        except OSError:
            httpd = server(bridge)
        print(json.dumps({'address': bridge.address, 'workspace_id': bridge.config['workspace_id'], 'generation': bridge.generation}), flush=True)
        httpd.serve_forever()
    finally:
        if httpd:
            httpd.server_close()
        lock.close()
