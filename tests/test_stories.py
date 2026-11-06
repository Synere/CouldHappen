from pathlib import Path
import json
import subprocess
import tempfile
import unittest

from helpers import files, stories
from support import workspace


class NewStory(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        self.out = tempfile.TemporaryDirectory()
        self.addCleanup(self.out.cleanup)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        config = json.loads((self.root / 'couldhappen.json').read_text())
        config['workspace_id'] = '11111111-1111-4111-8111-111111111111'
        (self.root / 'couldhappen.json').write_text(json.dumps(config))
        (self.root / 'tool.py').write_text('print("shipped")\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')
        # Story play afterwards: records, a package, and edits that must not carry over.
        (self.root / 'public/story.md').write_text('# Story\n\nA long tale.\n', encoding='utf-8')
        (self.root / 'tool.py').write_text('print("edited by the writer")\n')
        (self.root / 'notes').mkdir()
        (self.root / 'notes/packages.md').write_text('applied: rpg-mechanics\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'story')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True).stdout

    def test_new_story_is_the_baseline_with_a_null_identity(self):
        dest = Path(self.out.name) / 'next'
        result = stories.new_story(self.root, dest)
        self.assertEqual(result['status'], 'created')
        self.assertEqual((dest / 'tool.py').read_text(), 'print("shipped")\n')
        self.assertEqual((dest / 'public/story.md').read_text(), '# Story\n')
        self.assertFalse((dest / 'notes').exists())
        self.assertFalse((dest / '.git').exists())
        self.assertIsNone(json.loads((dest / 'couldhappen.json').read_text())['workspace_id'])
        files.snapshot(dest)

    def test_refuses_nonempty_nested_and_same_destinations(self):
        busy = Path(self.out.name) / 'busy'
        busy.mkdir()
        (busy / 'x').write_text('x')
        for bad in (busy, self.root, self.root / 'inside'):
            with self.assertRaises(files.Invalid):
                stories.new_story(self.root, bad)
        self.assertFalse((self.root / 'inside').exists())


if __name__ == '__main__':
    unittest.main()
