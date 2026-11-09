"""Build a deterministic CouldHappen release ZIP from a named commit.

This is a release tool, not part of the portable runtime. It reads tracked files
from the selected commit, applies release.manifest.json, validates required and
forbidden paths, strips development-only blocks, scans text for configured
secret markers, checks relative Markdown links, and writes a reproducible ZIP
plus a SHA-256 sidecar.

Development-only blocks let one tracked file serve both audiences: the release
text is the file with every marked block removed. A block starts and ends with
the manifest's marker lines for that file type (by default
``<!-- dev-only -->`` / ``<!-- /dev-only -->`` in Markdown), each alone on its
line. Configuration whose rules genuinely differ (such as .gitignore) uses a
manifest template instead.

Mirrors ship one tracked folder under a second name. Claude Code discovers
skills only in ``.claude/skills/``, and other hosts read ``.agents/skills/``, so
the manifest's ``mirrors`` map copies every selected file under a source prefix
to the destination prefix. Nothing is tracked under a destination prefix: the
copy exists only in the release, so it cannot drift from its source.
"""
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'release.manifest.json'
LINK = re.compile(r'\]\(([^)]+)\)')
DEFAULT_MARKERS = {
    '*.md': ['<!-- dev-only -->', '<!-- /dev-only -->'],
}


class ReleaseError(Exception):
    pass


def git(*args):
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True)
    if result.returncode:
        raise ReleaseError(result.stderr.decode('utf-8', 'replace').strip() or 'Git failed')
    return result.stdout


def blob(ref, path):
    result = subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:{path}'], capture_output=True)
    if result.returncode:
        raise ReleaseError(f'Missing tracked file at {ref}: {path}')
    return result.stdout


def tracked(ref):
    raw = git('ls-tree', '-r', '--name-only', '-z', ref)
    return sorted(part.decode('utf-8') for part in raw.split(b'\0') if part)


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def selected(ref, manifest, all_paths):
    include = manifest['include']
    exclude = manifest['exclude']
    templates = manifest.get('templates', {})
    files = [path for path in all_paths if matches(path, include) and not matches(path, exclude)]
    for destination in templates:
        if destination not in files:
            files.append(destination)
    for destination, source in manifest.get('mirrors', {}).items():
        stray = [path for path in all_paths if path.startswith(destination)]
        if stray:
            raise ReleaseError(f'Mirror destination {destination} must not be tracked: {stray[0]}')
        files.extend(destination + path[len(source):] for path in list(files) if path.startswith(source))
    return sorted(set(files))


def source_path(path, manifest):
    """Return the tracked path a release path is read from."""
    for destination, source in manifest.get('mirrors', {}).items():
        if path.startswith(destination):
            path = source + path[len(destination):]
            break
    return manifest.get('templates', {}).get(path, path)


def markers_for(path, manifest):
    for pattern, pair in manifest.get('dev_only_markers', DEFAULT_MARKERS).items():
        if fnmatch.fnmatchcase(posixpath.basename(path), pattern) or fnmatch.fnmatchcase(path, pattern):
            return pair
    return None


def strip_dev_only(path, data, manifest):
    """Return data with development-only blocks removed; refuse malformed blocks."""
    pair = markers_for(path, manifest)
    if pair is None:
        return data
    start, end = pair
    text = data.decode('utf-8')
    if start not in text and end not in text:
        return data
    kept, inside, opened = [], False, 0
    for number, line in enumerate(text.split('\n'), 1):
        marker = line.strip()
        if marker == start:
            if inside:
                raise ReleaseError(f'{path}:{number}: nested dev-only block')
            inside, opened = True, number
        elif marker == end:
            if not inside:
                raise ReleaseError(f'{path}:{number}: dev-only end without start')
            inside = False
        elif start in line or end in line:
            raise ReleaseError(f'{path}:{number}: dev-only marker must be alone on its line')
        elif not inside:
            kept.append(line)
    if inside:
        raise ReleaseError(f'{path}:{opened}: unclosed dev-only block')
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(kept)).strip('\n')
    return (result + ('\n' if text.endswith('\n') else '')).encode('utf-8')


def release_contents(ref, manifest, files):
    return {path: strip_dev_only(path, blob(ref, source_path(path, manifest)), manifest) for path in files}


def link_targets(path, text):
    for match in LINK.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(('http://', 'https://', 'mailto:', '#', '<')):
            continue
        target = target.split('#', 1)[0]
        if not target:
            continue
        if target.startswith('/'):
            resolved = target.lstrip('/')
        else:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
        if resolved.startswith('../') or resolved == '..':
            raise ReleaseError(f'{path}: link escapes the release: {match.group(1)}')
        yield resolved, match.group(1)


def validate(files, manifest, contents):
    missing = [path for path in manifest.get('required', []) if path not in files]
    if missing:
        raise ReleaseError('Missing required release paths: ' + ', '.join(missing))
    for path in files:
        if matches(path, manifest.get('forbidden', [])):
            raise ReleaseError(f'Forbidden release path selected: {path}')
    allow_prefixes = tuple(manifest.get('content_pattern_allow_paths', []))
    patterns = manifest.get('content_patterns', [])
    for path, data in contents.items():
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern in text:
                if pattern == 'PRIVATE_BOUNDARY_FIXTURE' and path.startswith(allow_prefixes):
                    continue
                raise ReleaseError(f'Private/secret marker {pattern!r} found in {path}')
        if path.endswith('.md'):
            for target, original in link_targets(path, text):
                if target not in files:
                    raise ReleaseError(f'{path}: relative link target missing in release: {original}')
    if 'release.json' in files:
        raise ReleaseError('release.json is generated by the builder and must not be selected')


def verify_archive(out, names, contents, manifest, ref):
    """Reopen the written ZIP and check it against the plan."""
    with zipfile.ZipFile(out) as archive:
        if archive.testzip() is not None:
            raise ReleaseError('Written ZIP is corrupt')
        if sorted(archive.namelist()) != names:
            raise ReleaseError('Written ZIP file list differs from the plan')
        for name in names:
            if archive.read(name) != contents[name]:
                raise ReleaseError(f'Written ZIP content differs from the plan: {name}')
        config = json.loads(archive.read('couldhappen.json'))
        if config.get('workspace_id') is not None:
            raise ReleaseError('Release couldhappen.json must have workspace_id null')
        for name, source in manifest.get('templates', {}).items():
            if name.startswith('public/') and archive.read(name) != blob(ref, source):
                raise ReleaseError(f'Public file is not the empty template: {name}')


def build(ref, out, allow_dirty=False, manifest_path=MANIFEST):
    if not allow_dirty:
        dirty = git('status', '--porcelain')
        if dirty.strip():
            raise ReleaseError('Working tree is dirty; commit or use --allow-dirty for a non-release build')
    manifest_data = blob(ref, manifest_path)
    manifest = json.loads(manifest_data)
    if manifest.get('schema_version') != 1:
        raise ReleaseError('Unsupported release manifest schema')
    version = str(manifest['version'])
    files = selected(ref, manifest, tracked(ref))
    contents = release_contents(ref, manifest, files)
    validate(files, manifest, contents)
    commit = git('rev-parse', ref).decode().strip()
    date = git('show', '-s', '--format=%cI', ref).decode().strip()
    metadata = {
        'schema_version': 1,
        'name': manifest['name'],
        'version': version,
        'contract_version': manifest['contract_version'],
        'source_commit': commit,
        'source_date': date,
        'manifest_sha256': hashlib.sha256(manifest_data).hexdigest(),
        'file_count': len(files) + 1,
    }
    contents['release.json'] = (json.dumps(metadata, indent=2, sort_keys=True) + '\n').encode('utf-8')
    out = Path(out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    names = sorted(contents)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, contents[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    verify_archive(out, names, contents, manifest, ref)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    sidecar = out.with_name(out.name + '.sha256')
    sidecar.write_text(f'{digest}  {out.name}\n', encoding='utf-8', newline='\n')
    return {'status': 'built', 'path': str(out), 'sha256': digest, 'file_count': len(names),
            'source_commit': commit, 'version': version, 'files': names}


def main():
    parser = argparse.ArgumentParser(description='Build a deterministic CouldHappen release ZIP')
    parser.add_argument('--ref', default='HEAD', help='Git commit/ref to build from')
    parser.add_argument('--out', help='Output ZIP (default: release/dist/couldhappen-<version>.zip)')
    parser.add_argument('--manifest', default=MANIFEST, help='Manifest path (must be tracked at ref)')
    parser.add_argument('--allow-dirty', action='store_true', help='Development-only: allow a dirty worktree')
    parser.add_argument('--list', action='store_true', help='Print the selected file list and exit')
    args = parser.parse_args()
    try:
        manifest = json.loads(blob(args.ref, args.manifest))
        version = str(manifest['version'])
        out = args.out or f'release/dist/couldhappen-{version}.zip'
        if args.list:
            files = selected(args.ref, manifest, tracked(args.ref))
            validate(files, manifest, release_contents(args.ref, manifest, files))
            print(json.dumps({'files': files, 'count': len(files)}, indent=2))
            return 0
        result = build(args.ref, out, args.allow_dirty, args.manifest)
        print(json.dumps(result, indent=2))
        return 0
    except (ReleaseError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
