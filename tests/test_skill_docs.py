"""Guard the writer skill's index pages against drifting from what ships.

The skill answers "what can you do?" from the workspace, so the pages it reads
(the package index, the reference list, and the helper command mentions) must
change whenever a capability is added or removed.
"""
from pathlib import Path
import re
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / '.agents/skills/couldhappen'


class SkillDocs(unittest.TestCase):
    def test_every_package_is_in_the_index_and_has_its_files(self):
        index = (SKILL / 'packages/INDEX.md').read_text(encoding='utf-8')
        for folder in sorted(p for p in (SKILL / 'packages').iterdir() if p.is_dir()):
            self.assertIn(f'[{folder.name}]({folder.name}/PACKAGE.md)', index, folder.name)
            self.assertTrue((folder / 'PACKAGE.md').is_file(), folder.name)
            self.assertTrue((folder / 'APPLY.md').is_file(), folder.name)
        for name in re.findall(r'\[([\w-]+)\]\(\1/PACKAGE\.md\)', index):
            self.assertTrue((SKILL / 'packages' / name).is_dir(), f'index lists missing package {name}')

    def test_every_reference_is_linked_from_the_skill(self):
        skill = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        for page in sorted((SKILL / 'references').glob('*.md')):
            self.assertIn(f'references/{page.name}', skill, page.name)

    def test_every_helper_command_is_described_in_the_skill_or_contract(self):
        text = '\n'.join(p.read_text(encoding='utf-8') for p in SKILL.rglob('*.md'))
        for name in ('docs/public-contract.md', 'docs/setup.md'):
            text += (REPO / name).read_text(encoding='utf-8')
        out = subprocess.run([sys.executable, '-m', 'helpers', '--help'], cwd=REPO, capture_output=True, text=True).stdout
        commands = re.search(r'\{([^}]+)\}', out).group(1).split(',')
        missing = [c for c in commands if f'helpers {c}' not in text]
        self.assertEqual(missing, [], 'helper commands not described in the skill, contract or setup')

    def test_adapted_nai_pages_keep_their_gpl_notice(self):
        """ADR-10: every page adapted from nai5-prompting keeps its notice, with NOTICE and the GPL text beside it."""
        folder = SKILL / 'packages/scene-images/nai'
        self.assertTrue((folder / 'NOTICE.md').is_file())
        self.assertTrue((folder / 'LICENSE-GPL-3.0.txt').read_text(encoding='utf-8').lstrip().startswith('GNU GENERAL PUBLIC LICENSE'))
        pages = [p for p in sorted(folder.glob('*.md')) if p.name != 'NOTICE.md']
        self.assertTrue(pages)
        for page in pages:
            head = page.read_text(encoding='utf-8').split('\n\n', 1)[0]
            for needed in ('https://github.com/Miint-Sunny/nai5-prompting', 'Copyright (C) 2026 Miint-Sunny',
                           'SPDX-License-Identifier: GPL-3.0-only', 'Modified for CouldHappen on '):
                self.assertIn(needed, head, page.name)
            self.assertIn(f'[{page.name}]({page.name})', (folder / 'NOTICE.md').read_text(encoding='utf-8'), page.name)

    def test_front_matter_values_are_valid_unquoted_yaml(self):
        """A ': ' or ' #' inside an unquoted value breaks YAML parsers that read these headers."""
        pages = [SKILL / 'SKILL.md', *sorted((SKILL / 'packages').glob('*/PACKAGE.md'))]
        for page in pages:
            lines = page.read_text(encoding='utf-8').splitlines()
            self.assertEqual(lines[0], '---', page)
            for number, line in enumerate(lines[1:], 2):
                if line == '---':
                    break
                key, sep, value = line.partition(': ')
                self.assertTrue(sep, f'{page.name}:{number} is not "key: value"')
                value = value.strip()
                if value[:1] in ('"', "'"):
                    continue
                self.assertNotIn(': ', value, f'{page.parent.name}/{page.name}:{number} has an unquoted ": " in {key}')
                self.assertNotIn(' #', value, f'{page.parent.name}/{page.name}:{number} has an unquoted " #" in {key}')
            else:
                self.fail(f'{page} front matter is not closed')


if __name__ == '__main__':
    unittest.main()
