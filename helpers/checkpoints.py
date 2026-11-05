"""Read-only, workspace-scoped Git evidence. Never stages, commits, or restores."""
from functools import lru_cache
from pathlib import Path, PurePosixPath
import re
import subprocess

from .files import Invalid, read_json

DEFAULT_EXCLUDES = ('.couldhappen/', '.env', '.env.*', 'web/node_modules/', 'web/dist/',
                    'web/test-results/', 'web/playwright-report/')
SPECIAL_EXCLUDES = ('**/__pycache__/**', '**/*.pyc', '**/.couldhappen-tmp-*')


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode:
        raise Invalid(result.stderr.decode('utf-8', 'replace').strip() or 'Git failed')
    return result.stdout


def relative(value):
    if not isinstance(value, str) or '\\' in value or ':' in value or value.startswith('/') or '..' in PurePosixPath(value).parts or value.startswith('-'):
        raise Invalid('Checkpoint paths must be workspace-relative')
    return value.rstrip('/') or '.'


@lru_cache(maxsize=None)
def glob_regex(pattern):
    """Git's FNM_PATHNAME glob: wildcards do not cross '/', with ** rules."""
    parts, index, size = ['^'], 0, len(pattern)
    while index < size:
        char = pattern[index]
        if char == '*':
            end = index
            while end < size and pattern[end] == '*':
                end += 1
            if end - index >= 2:
                if index == 0 and end < size and pattern[end] == '/':
                    parts.append('(?:.*/)?')
                    index = end + 1
                    continue
                if end == size and index > 0 and pattern[index - 1] == '/':
                    parts.append('.*')
                    index = end
                    continue
                if index > 0 and pattern[index - 1] == '/' and end < size and pattern[end] == '/':
                    parts.append('(?:.*/)?')
                    index = end + 1
                    continue
            parts.append('[^/]*')
            index = end
        elif char == '?':
            parts.append('[^/]')
            index += 1
        elif char == '[':
            end = index + 1
            if end < size and pattern[end] in ('!', '^'):
                end += 1
            if end < size and pattern[end] == ']':
                end += 1
            while end < size and pattern[end] != ']':
                end += 1
            if end >= size:
                parts.append(r'\[')
                index += 1
            else:
                stuff = pattern[index + 1:end]
                if stuff.startswith('!'):
                    stuff = '^' + stuff[1:]
                parts.append('(?!/)[' + stuff + ']')
                index = end + 1
        else:
            parts.append(re.escape(char))
            index += 1
    parts.append('$')
    return re.compile(''.join(parts))


def excluded(path, combined, directory):
    pattern = combined + '/**' if directory else combined
    if any(mark in combined for mark in '*?['):
        return bool(glob_regex(pattern).match(path))
    return path == combined or path.startswith(combined + '/')


def plan(root):
    root = Path(root).resolve()
    repo = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    prefix = root.relative_to(repo).as_posix()
    config = read_json(root / 'couldhappen.json')['checkpoint']
    includes = [(PurePosixPath(prefix) / relative(path)).as_posix() for path in config['scope']]
    excludes = [((PurePosixPath(prefix) / relative(path)).as_posix(), path.endswith('/'))
                for path in list(config['exclude']) + list(DEFAULT_EXCLUDES)]
    return root, repo, prefix, includes, excludes


def pathspecs(includes, excludes):
    paths = []
    for combined in includes:
        paths.append(':(top,glob)**' if combined == '.' else ':(top,literal)' + combined)
    for combined, directory in excludes:
        paths.append(':(top,exclude,glob)' + combined + ('/**' if directory else ''))
    paths += [':(top,exclude,glob)' + pattern for pattern in SPECIAL_EXCLUDES]
    return paths


def selected(path, includes, excludes):
    if not any(item == '.' or path == item or path.startswith(item + '/') for item in includes):
        return False
    for combined, directory in excludes:
        if excluded(path, combined, directory):
            return False
    return ('__pycache__' not in PurePosixPath(path).parts and not path.endswith('.pyc')
            and not PurePosixPath(path).name.startswith('.couldhappen-tmp-'))


def scope(root):
    root, repo, prefix, includes, excludes = plan(root)
    return root, repo, pathspecs(includes, excludes)


def check(root):
    try:
        root, repo, paths = scope(root)
        raw = git(repo, 'status', '--porcelain=v1', '-z', '--untracked-files=all', '--', *paths)
        fields = raw.split(b'\0')
        changed, index = [], 0
        while index < len(fields) and fields[index]:
            field = fields[index].decode('utf-8', 'surrogateescape')
            state, name = field[:2], field[3:]
            if state in ('DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU'):
                raise Invalid('Unmerged checkpoint path: ' + name)
            changed.append({'path': name, 'status': state})
            index += 1
            if 'R' in state or 'C' in state:
                changed.append({'path': fields[index].decode('utf-8', 'surrogateescape'), 'status': 'source'})
                index += 1
        return {'status': 'dirty' if changed else 'clean', 'paths': changed}, 1 if changed else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'error', 'message': str(exc)}, 2


def inspect(root, ref):
    try:
        root, repo, prefix, includes, excludes = plan(root)
        commit = git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
        # ls-tree does not support status's exclude/glob pathspec magic, so list
        # the workspace tree and apply the same configured filters in Python.
        args = ['ls-tree', '-r', '--name-only', '-z', commit]
        if prefix != '.':
            args += ['--', ':(top,literal)' + prefix]
        recorded = git(repo, *args).decode().split('\0')
        history = git(repo, 'log', '-8', '--format=%H %s', commit, '--', *pathspecs(includes, excludes)).decode().splitlines()
        return {'status': 'ok', 'commit': commit,
                'paths': [path for path in recorded if path and selected(path, includes, excludes)],
                'history': history}, 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'error', 'message': str(exc)}, 2


def native(root, event):
    """Common command-hook translation; armed play only, no commits."""
    root = Path(root).resolve()
    cwd = event.get('cwd')
    if not isinstance(cwd, str) or not Path(cwd).resolve().is_relative_to(root):
        return {}
    state = root / '.couldhappen/control.json'
    if not state.exists():
        return {}
    try:
        if not read_json(state).get('armed'):
            return {}
        result, code = check(root)
        if code == 1:
            names = ', '.join(p['path'] for p in result['paths'])
            return {'decision': 'block', 'reason': 'CouldHappen play has uncheckpointed changes: ' + names + '. Review the scoped work, finish durable notes, and make a meaningful checkpoint before completion. Do not auto-commit unrelated files.'}
        if code == 2:
            return {'systemMessage': 'CouldHappen checkpoint assurance unavailable: ' + result['message']}
        return {}
    except (OSError, ValueError, TypeError) as exc:
        return {'systemMessage': 'CouldHappen checkpoint assurance unavailable: ' + str(exc)}
