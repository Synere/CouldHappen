import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from support import REPO


class ReleaseBuild(unittest.TestCase):
    def build(self, out):
        result = subprocess.run(
            [sys.executable, str(REPO / 'scripts' / 'build_release.py'),
             '--ref', 'HEAD', '--out', str(out), '--allow-dirty'],
            cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_release_is_deterministic_clean_and_self_describing(self):
        with tempfile.TemporaryDirectory() as folder:
            first = self.build(Path(folder) / 'one.zip')
            second = self.build(Path(folder) / 'two.zip')
            one = Path(first['path']).read_bytes()
            two = Path(second['path']).read_bytes()
            self.assertEqual(one, two)
            self.assertEqual(first['sha256'], second['sha256'])
            self.assertTrue((Path(first['path']).with_name('one.zip.sha256')).is_file())
            with zipfile.ZipFile(first['path']) as archive:
                names = set(archive.namelist())
                required = {
                    'README.md', 'START_HERE.md', 'couldhappen.json', 'DESIGN.md', 'LICENSE', '.gitignore',
                    'docs/README.md', 'docs/setup.md', 'docs/public-contract.md', 'docs/reference-hosts.md',
                    'web/README.md', 'web/package.json', 'helpers/__main__.py',
                    '.agents/skills/couldhappen/SKILL.md', 'public/story.md', 'public/director.md',
                    'public/cast.json', 'public/work.json', 'release.json',
                }
                self.assertTrue(required <= names)
                ignores = archive.read('.gitignore').decode()
                self.assertIn('.impeccable/', ignores)
                self.assertIn('.DS_Store', ignores)
                self.assertIn('npm ci', archive.read('README.md').decode())
                for name in names:
                    if name.endswith('.md'):
                        text = archive.read(name).decode()
                        self.assertNotIn('dev-only', text, name)
                        self.assertNotIn('Development repository', text, name)
                self.assertNotIn('implementation-progress', archive.read('README.md').decode())
                self.assertIn('standing wait', archive.read('docs/setup.md').decode())
                self.assertNotIn('Building a release', archive.read('docs/setup.md').decode())
                skill, mirror = '.agents/skills/couldhappen/', '.claude/skills/couldhappen/'
                shipped = {name[len(skill):] for name in names if name.startswith(skill)}
                mirrored = {name[len(mirror):] for name in names if name.startswith(mirror)}
                self.assertIn('SKILL.md', shipped)
                self.assertEqual(shipped, mirrored, 'Claude Code copy of the skill differs from .agents/')
                for name in shipped:
                    self.assertEqual(archive.read(skill + name), archive.read(mirror + name), name)
                self.assertFalse(any(name.startswith(('.claude/agents/', '.claude/skills/impeccable/'))
                                     or name.startswith('.claude/settings') for name in names))
                for forbidden in ('.git', '.impeccable', 'docs/history', 'docs/research', 'docs/reviews',
                                  'docs/decisions', 'docs/designs', 'PRODUCT.md', 'release/README.md',
                                  'scripts/build_release.py', 'tests/test_release.py', 'AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md'):
                    self.assertFalse(any(name == forbidden or name.startswith(forbidden + '/') for name in names), forbidden)
                config = json.loads(archive.read('couldhappen.json'))
                self.assertIsNone(config['workspace_id'])
                self.assertEqual(config['schema_version'], 1)
                self.assertEqual(config['checkpoint']['exclude'], [])
                self.assertEqual(archive.read('public/story.md').decode(), '# Story\n')
                self.assertEqual(archive.read('public/director.md').decode(), '# Director\n')
                self.assertEqual(json.loads(archive.read('public/cast.json'))['characters'], [])
                work = json.loads(archive.read('public/work.json'))
                self.assertEqual((work['mode'], work['director_question_id']), ('play', None))
                metadata = json.loads(archive.read('release.json'))
                self.assertEqual(metadata['version'], json.loads((REPO / 'release.manifest.json').read_text())['version'])
                self.assertEqual(metadata['contract_version'], 1)
                self.assertEqual(metadata['source_commit'], subprocess.check_output(
                    ['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip())
                self.assertEqual(metadata['file_count'], len(names))
                self.assertIn('manifest_sha256', metadata)

    def test_list_matches_build_and_has_no_dev_artifacts(self):
        result = subprocess.run(
            [sys.executable, str(REPO / 'scripts' / 'build_release.py'), '--ref', 'HEAD', '--list'],
            cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        listed = json.loads(result.stdout)
        self.assertGreater(listed['count'], 20)
        self.assertIn('README.md', listed['files'])
        self.assertNotIn('PRODUCT.md', listed['files'])
        self.assertNotIn('docs/decisions/ADR-1-separate-story-workspaces.md', listed['files'])

    def test_version_lives_only_in_the_manifest(self):
        for name in ('web/package.json', 'web/package-lock.json'):
            data = json.loads((REPO / name).read_text(encoding='utf-8'))
            self.assertNotIn('version', data, name)
            self.assertNotIn('version', data.get('packages', {}).get('', {}), name)


class VerifyArchive(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(REPO / 'scripts'))
        import build_release
        self.module = build_release
        self.manifest = {'templates': {'public/story.md': 'release/public/story.md'}}
        self.good = {'couldhappen.json': b'{"workspace_id": null}', 'public/story.md': b'# Story\n'}

    def check(self, written, contents=None, config=None):
        contents = contents or self.good
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'x.zip'
            with zipfile.ZipFile(out, 'w') as archive:
                for name, data in written.items():
                    archive.writestr(name, data)
            self.module.verify_archive(out, sorted(contents), contents, self.manifest, 'HEAD')

    def test_good_archive_passes_and_bad_ones_are_refused(self):
        self.check(self.good)
        with self.assertRaises(self.module.ReleaseError):  # missing file
            self.check({'couldhappen.json': self.good['couldhappen.json']})
        bad = {**self.good, 'couldhappen.json': b'{"workspace_id": "abc"}'}
        with self.assertRaises(self.module.ReleaseError):  # workspace id set
            self.check(bad, bad)
        bad = {**self.good, 'public/story.md': b'# Story\n\nsecret\n'}
        with self.assertRaises(self.module.ReleaseError):  # not the empty template
            self.check(bad, bad)


class Mirrors(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(REPO / 'scripts'))
        import build_release
        self.module = build_release
        self.manifest = {'include': ['s/**', 'x.md'], 'exclude': ['**/*.pyc'], 'mirrors': {'m/': 's/'}}

    def test_mirror_copies_selected_source_files_and_reads_from_the_source(self):
        files = self.module.selected('HEAD', self.manifest, ['s/SKILL.md', 's/a/b.py', 's/a/b.pyc', 'x.md'])
        self.assertEqual(files, ['m/SKILL.md', 'm/a/b.py', 's/SKILL.md', 's/a/b.py', 'x.md'])
        self.assertEqual(self.module.source_path('m/a/b.py', self.manifest), 's/a/b.py')
        self.assertEqual(self.module.source_path('x.md', self.manifest), 'x.md')

    def test_a_mirrored_file_ships_its_source_template(self):
        manifest = {**self.manifest, 'templates': {'s/c.json': 'release/c.json'}}
        self.assertEqual(self.module.source_path('m/c.json', manifest), 'release/c.json')
        self.assertEqual(self.module.source_path('s/c.json', manifest), 'release/c.json')

    def test_the_real_manifest_ships_nested_package_files_in_both_copies(self):
        manifest = json.loads((REPO / 'release.manifest.json').read_text(encoding='utf-8'))
        source = '.agents/skills/couldhappen/packages/p/files/defaults.json'
        files = self.module.selected('HEAD', manifest, [source])
        mirrored = '.claude/skills/couldhappen/packages/p/files/defaults.json'
        self.assertTrue({mirrored, source} <= set(files), files)
        self.assertFalse(self.module.matches(mirrored, manifest['forbidden']))
        self.assertTrue(self.module.matches('.claude/settings.local.json', manifest['forbidden']))

    def test_a_tracked_file_under_the_mirror_destination_is_refused(self):
        with self.assertRaises(self.module.ReleaseError):
            self.module.selected('HEAD', self.manifest, ['s/SKILL.md', 'm/SKILL.md'])


class DevOnlyBlocks(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(REPO / 'scripts'))
        import build_release
        self.module = build_release
        self.strip = lambda text, path='x.md': build_release.strip_dev_only(path, text.encode(), {}).decode()

    def test_blocks_are_removed_and_text_is_a_subset(self):
        text = 'A\n\n<!-- dev-only -->\nsecret dev note\n<!-- /dev-only -->\n\nB\n'
        self.assertEqual(self.strip(text), 'A\n\nB\n')
        self.assertEqual(self.strip('<!-- dev-only -->\nx\n<!-- /dev-only -->\n# Title\n'), '# Title\n')
        self.assertEqual(self.strip('no markers\n'), 'no markers\n')
        self.assertEqual(self.strip('A\n\n<!-- dev-only -->\nx\n<!-- /dev-only -->\n'), 'A\n')
        self.assertEqual(self.strip('<!-- dev-only -->\nkept\n', 'x.json'), '<!-- dev-only -->\nkept\n')

    def test_malformed_blocks_are_refused(self):
        for text in ('<!-- dev-only -->\nx\n', 'x\n<!-- /dev-only -->\n',
                     '<!-- dev-only -->\n<!-- dev-only -->\n<!-- /dev-only -->\n<!-- /dev-only -->\n',
                     'inline <!-- dev-only --> marker\n'):
            with self.subTest(text=text), self.assertRaises(self.module.ReleaseError):
                self.strip(text)


class DevelopmentLinks(unittest.TestCase):
    EVIDENCE = ('.research/', 'goldfish_reviews/', '.impeccable/')

    def test_relative_markdown_links_resolve_in_the_repository(self):
        import posixpath
        import re
        tracked = set(subprocess.check_output(['git', '-C', str(REPO), 'ls-files'], text=True).split('\n'))
        folders = {posixpath.dirname(path) for path in tracked}
        while '' not in folders:
            folders |= {posixpath.dirname(folder) for folder in folders}
        broken = []
        for name in sorted(tracked):
            if not name.endswith('.md') or name.startswith(self.EVIDENCE):
                continue
            text = re.sub(r'`[^`\n]*`', '', (REPO / name).read_text(encoding='utf-8'))  # code spans are not links
            for target in re.findall(r'\]\(([^)\s]+)\)', text):
                if target.startswith(('http://', 'https://', 'mailto:', '#', '<', '/')) or re.match(r'[A-Za-z]:[/\\]', target):
                    continue  # external, including absolute paths to other local projects
                path = target.split('#', 1)[0]
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), path)).rstrip('/')
                if resolved not in tracked and resolved not in folders:
                    broken.append(f'{name}: {target}')
        self.assertEqual(broken, [])


if __name__ == '__main__':
    unittest.main()
