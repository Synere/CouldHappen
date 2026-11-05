from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from helpers import checkpoints, files
from support import workspace


class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture baseline')
        self.branch = self.git('rev-parse', '--abbrev-ref', 'HEAD').decode().strip()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True).stdout

    def test_all_dirty_states_exclusions_and_history(self):
        self.assertEqual(checkpoints.check(self.root)[1], 0)
        (self.root / 'public/story.md').write_text('# Story\n\n', encoding='utf-8')
        self.git('add', 'public/story.md')
        (self.root / 'public/director.md').write_text('# Director\n\n', encoding='utf-8')
        (self.root / 'public/cast.json').unlink()
        (self.root / 'private.md').write_text('world note', encoding='utf-8')
        (self.root / '.env').write_text('SECRET=fixture', encoding='utf-8')
        (self.root / 'docs/history').mkdir(parents=True)
        (self.root / 'docs/history/history.md').write_text('history', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({p['path'] for p in result['paths']}, {'public/story.md', 'public/director.md', 'public/cast.json', 'private.md'})
        result, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, result)
        self.assertIn('public/story.md', result['paths'])
        self.assertEqual(checkpoints.inspect(self.root, '--bad')[1], 2)
        with patch('helpers.checkpoints.subprocess.run', side_effect=FileNotFoundError('no git')):
            self.assertEqual(checkpoints.check(self.root)[1], 2)

    def test_inspect_applies_the_same_exclusions_as_check(self):
        (self.root / 'docs/history').mkdir(parents=True)
        (self.root / 'docs/history/history.md').write_text('history', encoding='utf-8')
        (self.root / 'docs/history/handoff.md').write_text('handoff', encoding='utf-8')
        (self.root / 'private.md').write_text('world note', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'add included and excluded files')
        self.assertEqual(checkpoints.check(self.root)[1], 0)
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        paths = set(inspected['paths'])
        self.assertIn('private.md', paths)
        self.assertIn('public/story.md', paths)
        self.assertNotIn('docs/history/history.md', paths)
        self.assertNotIn('docs/history/handoff.md', paths)
        # A commit touching only excluded paths is not checkpoint history.
        (self.root / 'docs/history/only.md').write_text('only', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'excluded only')
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        self.assertNotIn('excluded only', '\n'.join(inspected['history']))
        # Dirty excluded paths do not make the checkpoint dirty.
        (self.root / 'docs/history/history.md').write_text('changed', encoding='utf-8')
        (self.root / 'docs/history/handoff.md').write_text('changed', encoding='utf-8')
        (self.root / 'private.md').write_text('changed', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({p['path'] for p in result['paths']}, {'private.md'})

    def test_gitignore_and_checkpoint_exclusions_are_independent(self):
        (self.root / '.couldhappen').mkdir()
        (self.root / '.couldhappen/control.json').write_text('{}', encoding='utf-8')
        (self.root / 'docs/history').mkdir(parents=True)
        (self.root / 'docs/history/history.md').write_text('history', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 0, result)

    def test_default_exclusions_apply_to_check_and_inspect(self):
        names = ('web/node_modules/pkg/index.js', '__pycache__/x.pyc', 'web/.couldhappen-tmp-x',
                 '.couldhappen/control.json')
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('excluded', encoding='utf-8')
        self.git('add', '-f', *names)
        self.git('commit', '-qm', 'default excluded files')
        self.assertEqual(checkpoints.check(self.root)[1], 0)
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        for name in names:
            self.assertNotIn(name, inspected['paths'])
        for name in names:
            (self.root / name).write_text('changed', encoding='utf-8')
        self.assertEqual(checkpoints.check(self.root)[1], 0)

    def test_rename_and_deletion_statuses(self):
        (self.root / 'private.md').write_text('note', encoding='utf-8')
        self.git('add', 'private.md')
        self.git('commit', '-qm', 'private')
        self.git('mv', 'private.md', 'moved.md')
        (self.root / 'public/cast.json').unlink()
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({(p['path'], p['status']) for p in result['paths']},
                         {('moved.md', 'R '), ('private.md', 'source'), ('public/cast.json', ' D')})
        self.git('add', 'public/cast.json')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({(p['path'], p['status']) for p in result['paths']},
                         {('moved.md', 'R '), ('private.md', 'source'), ('public/cast.json', 'D ')})

    def test_unmerged_state_is_an_error_not_clean(self):
        conflict = self.root / 'conflict.txt'
        conflict.write_text('base\n', encoding='utf-8')
        self.git('add', 'conflict.txt')
        self.git('commit', '-qm', 'conflict base')
        self.git('checkout', '-qb', 'side')
        conflict.write_text('side\n', encoding='utf-8')
        self.git('add', 'conflict.txt')
        self.git('commit', '-qm', 'side change')
        self.git('checkout', '-q', self.branch)
        conflict.write_text('main\n', encoding='utf-8')
        self.git('add', 'conflict.txt')
        self.git('commit', '-qm', 'main change')
        merge = subprocess.run(['git', '-C', str(self.root), 'merge', 'side'], capture_output=True)
        self.assertNotEqual(merge.returncode, 0)
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unmerged', result['message'])

    def test_git_glob_semantics_do_not_cross_directory_boundaries(self):
        cases = [
            ('private/*.md', False, 'private/a.md', True),
            ('private/*.md', False, 'private/nested/kept.md', False),
            ('private/*', False, 'private/nested/kept.md', False),
            ('private/**', False, 'private/nested/kept.md', True),
            ('private/**/*.md', False, 'private/a.md', True),
            ('private/**/*.md', False, 'private/nested/kept.md', True),
            ('**/kept.md', False, 'private/nested/kept.md', True),
            ('*.md', False, 'root.md', True),
            ('*.md', False, 'nested/root.md', False),
            ('private[!x]kept.md', False, 'private/kept.md', False),
            ('private[!x]kept.md', False, 'privateakept.md', True),
            ('private[!x]kept.md', False, 'privatexkept.md', False),
            ('private[^x]kept.md', False, 'private/kept.md', False),
            ('private[^x]kept.md', False, 'privateakept.md', True),
            ('private[^x]kept.md', False, 'privatexkept.md', False),
            ('private', False, 'private/nested/kept.md', True),
            ('docs/planning', True, 'docs/planning/x.md', True),
        ]
        for pattern, directory, path, expected in cases:
            with self.subTest(pattern=pattern, path=path):
                self.assertEqual(checkpoints.excluded(path, pattern, directory), expected)

    def test_inspect_and_check_agree_on_glob_exclusions(self):
        config = files.read_json(self.root / 'couldhappen.json')
        config['checkpoint']['exclude'].append('private/*.md')
        files.write_json(self.root / 'couldhappen.json', config)
        (self.root / 'private/nested').mkdir(parents=True)
        (self.root / 'private/a.md').write_text('a', encoding='utf-8')
        (self.root / 'private/nested/kept.md').write_text('kept', encoding='utf-8')
        (self.root / 'private/notes.txt').write_text('notes', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'glob exclusion fixture')
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        self.assertIn('private/nested/kept.md', inspected['paths'])
        self.assertIn('private/notes.txt', inspected['paths'])
        self.assertNotIn('private/a.md', inspected['paths'])
        for name in ('private/a.md', 'private/nested/kept.md', 'private/notes.txt'):
            (self.root / name).write_text('changed', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({p['path'] for p in result['paths']},
                         {'private/nested/kept.md', 'private/notes.txt'})

    def test_inspect_and_check_agree_on_bracket_exclusions(self):
        config = files.read_json(self.root / 'couldhappen.json')
        config['checkpoint']['exclude'].append('private[!x]kept.md')
        files.write_json(self.root / 'couldhappen.json', config)
        (self.root / 'private').mkdir()
        (self.root / 'private/kept.md').write_text('kept', encoding='utf-8')
        (self.root / 'privateakept.md').write_text('matched', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'bracket exclusion fixture')
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        self.assertIn('private/kept.md', inspected['paths'])
        self.assertNotIn('privateakept.md', inspected['paths'])
        for name in ('private/kept.md', 'privateakept.md'):
            (self.root / name).write_text('changed', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1)
        self.assertEqual({p['path'] for p in result['paths']}, {'private/kept.md'})

    def test_inspect_and_check_agree_on_caret_negated_brackets(self):
        config = files.read_json(self.root / 'couldhappen.json')
        config['checkpoint']['exclude'].append('private[^x]kept.md')
        files.write_json(self.root / 'couldhappen.json', config)
        names = ('private/kept.md', 'privateakept.md', 'privatexkept.md')
        (self.root / 'private').mkdir()
        for name in names:
            (self.root / name).write_text('original', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'caret bracket fixture')
        inspected, code = checkpoints.inspect(self.root, 'HEAD')
        self.assertEqual(code, 0, inspected)
        self.assertIn('private/kept.md', inspected['paths'])
        self.assertIn('privatexkept.md', inspected['paths'])
        self.assertNotIn('privateakept.md', inspected['paths'])
        for name in names:
            (self.root / name).write_text('changed', encoding='utf-8')
        result, code = checkpoints.check(self.root)
        self.assertEqual(code, 1, result)
        self.assertEqual({p['path'] for p in result['paths']},
                         {'private/kept.md', 'privatexkept.md'})

    def test_nested_workspace_does_not_include_parent(self):
        nested = self.root / 'nested'
        nested.mkdir()
        files.write_json(nested / 'couldhappen.json', files.read_json(self.root / 'couldhappen.json'))
        (self.root / 'outside.md').write_text('unrelated', encoding='utf-8')
        result, code = checkpoints.check(nested)
        self.assertEqual(code, 1)
        self.assertEqual([p['path'] for p in result['paths']], ['nested/couldhappen.json'])

    def test_nested_workspace_inspect_ignores_parent_history_and_paths(self):
        nested = self.root / 'nested'
        nested.mkdir()
        files.write_json(nested / 'couldhappen.json', files.read_json(self.root / 'couldhappen.json'))
        (nested / 'private.md').write_text('nested note', encoding='utf-8')
        (self.root / 'outside.md').write_text('unrelated', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'nested workspace')
        self.assertEqual(checkpoints.check(nested)[1], 0)
        inspected, code = checkpoints.inspect(nested, 'HEAD')
        self.assertEqual(code, 0, inspected)
        self.assertEqual(set(inspected['paths']), {'nested/couldhappen.json', 'nested/private.md'})
        self.assertNotIn('fixture baseline', '\n'.join(inspected['history']))
