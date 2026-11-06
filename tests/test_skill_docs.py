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


if __name__ == '__main__':
    unittest.main()
