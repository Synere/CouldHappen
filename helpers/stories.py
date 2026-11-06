"""Start a new story workspace from the baseline commit of an existing one."""
import io
from pathlib import Path
import subprocess
import tarfile

from .files import Invalid, read_json, snapshot, write_json


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode:
        raise Invalid(result.stderr.decode('utf-8', 'replace').strip() or 'Git failed')
    return result.stdout


def new_story(root, destination):
    """Extract the root commit of this workspace into a new folder with no story state.

    The root commit is the clean release plus the workspace identity (setup's first
    baseline commit), so the new story gets the shipped code and writer skill without
    this story's records, imports, packages, or edits. It has no Git history yet and a
    null workspace identity: setup initializes both.
    """
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination == root or root in destination.parents or destination in root.parents:
        raise Invalid('The new story folder must be a separate folder, not inside or around this one')
    if destination.exists() and any(destination.iterdir()):
        raise Invalid('The new story folder already exists and is not empty')
    roots = git(root, 'rev-list', '--max-parents=0', 'HEAD').decode().split()
    if len(roots) != 1:
        raise Invalid('Expected one baseline commit in this workspace; found %d' % len(roots))
    baseline = roots[0]
    archive = git(root, 'archive', '--format=tar', baseline)
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            target = (destination / member.name).resolve()
            if destination != target and destination not in target.parents:
                raise Invalid('Unsafe path in baseline: %s' % member.name)
        tar.extractall(destination, filter='data')
    config_path = destination / 'couldhappen.json'
    config = read_json(config_path)
    config['workspace_id'] = None
    write_json(config_path, config)
    snapshot(destination)
    return {'status': 'created', 'path': str(destination), 'baseline': baseline}
