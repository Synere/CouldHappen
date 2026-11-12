"""Tests for the character-brains-plus package's brains.py: a brief carries only what its character could know."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from uuid import uuid4

from helpers import files
from tests.support import REPO, workspace

PACKAGES = REPO / '.agents/skills/couldhappen/packages'
BRAINS = PACKAGES / 'character-brains-plus/files/brains.py'
GM = PACKAGES / 'game-master/files/gm_state.py'
NAMES = ('amber', 'basalt', 'cedar', 'dune', 'ember', 'fennel', 'garnet', 'hazel', 'indigo', 'jasper',
         'kelp', 'linen', 'moss', 'nettle', 'onyx', 'pumice', 'quartz', 'rowan', 'slate', 'thistle')


def run(root, script, *args):
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    return subprocess.run([sys.executable, '-I', str(root / 'tools' / script), '--root', str(root), *args],
                          capture_output=True, env=env)


def text(n):
    return f'The {NAMES[n - 1]} truth holds.'


class BrainsTest(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        (self.root / 'tools').mkdir()
        shutil.copy(GM, self.root / 'tools' / 'gm_state.py')
        shutil.copy(BRAINS, self.root / 'tools' / 'brains.py')
        self.assertEqual(run(self.root, 'gm_state.py', 'init').returncode, 0)
        self.entry = self.add_entry()
        self.scene = self.root / 'notes' / 'brains' / 'scene.txt'

    # ---- helpers ----

    def add_entry(self, body='Rain on the harbour.'):
        eid = str(uuid4())
        path = self.root / 'public' / 'story.md'
        path.write_text(path.read_text(encoding='utf-8') + '\n' + files.entry(body, role='writer', id=eid),
                        encoding='utf-8', newline='\n')
        return eid

    def gm(self, ops):
        (self.root / 'notes/gm/pending.json').write_text(
            json.dumps({'entry': self.entry, 'why': 'the story showed it', 'ops': ops}), encoding='utf-8')
        result = run(self.root, 'gm_state.py', 'commit')
        self.assertEqual(result.returncode, 0, result.stdout.decode() + result.stderr.decode())

    def brains(self, *args, expect=0):
        result = run(self.root, 'brains.py', *args)
        out = result.stdout.decode('utf-8')
        self.assertEqual(result.returncode, expect, out + result.stderr.decode())
        return json.loads(out) if out.startswith('{') else out

    def fact(self, n, **extra):
        return {'op': 'add', 'kind': 'fact', 'id': f'F{n}', 'text': text(n), 'status': 'established',
                'source': 'story', 'tags': ['Harbour'], **extra}

    def cast(self):
        self.gm([
            {'op': 'set', 'kind': 'situation', 'fields': {'day': 2, 'time': 'dusk', 'location': 'the harbour',
                                                         'present': ['Mara', 'Juno']}},
            {'op': 'set', 'kind': 'npc', 'id': 'mara', 'fields': {
                'name': 'Mara Venn', 'want': 'to clear her debt', 'fear': 'the tide office',
                'secret': 'she forged the manifest', 'voice': 'clipped, dry, never finishes a joke',
                'attitude': 'wary of the player'}},
            {'op': 'set', 'kind': 'npc', 'id': 'juno', 'fields': {
                'name': 'Juno Ash', 'want': 'the ledger', 'secret': 'she informs for the harbourmaster'}},
            {'op': 'add', 'kind': 'thread', 'id': 'T1', 'type': 'promise', 'text': 'Mara promised the player a boat.'},
            {'op': 'add', 'kind': 'thread', 'id': 'T2', 'type': 'mystery', 'text': 'Who drowned the clerk?'}])
        self.brains('init')
        self.brains('add', 'mara', '--age', '34', '--look', 'tall, salt-grey hair, a burn on one wrist',
                    '--alias', 'Red', '--threads', 'T1')
        self.brains('add', 'juno')

    def fixture(self):
        """Twenty facts, one of every way a fact can reach or miss Mara's brief."""
        self.cast()
        self.gm([self.fact(n, known=(n % 2 == 0)) for n in range(1, 13)])
        self.gm([self.fact(13), self.fact(14, known=False),
                 self.fact(15, known=False, tags=['Mara', 'Harbour']),  # tagged and present, still hidden
                 self.fact(16), self.fact(17), self.fact(18),
                 self.fact(19, status='provisional', known=False), self.fact(20)])
        for n in range(1, 6):
            self.brains('world', f'F{n}', '--visibility', 'public')
        for n in (6, 7, 8):
            self.brains('world', f'F{n}', '--visibility', 'witnessed', '--witnesses', 'mara', 'juno')
        for n in (9, 10, 20):
            self.brains('world', f'F{n}', '--visibility', 'witnessed', '--witnesses', 'juno')
        self.brains('world', 'F11', '--visibility', 'secret', '--witnesses', 'juno')  # Juno's secret
        self.brains('world', 'F12', '--visibility', 'private', '--witnesses', 'mara')
        for n in (13, 14, 15):
            self.brains('world', f'F{n}', '--visibility', 'secret', '--witnesses', 'juno')
        self.brains('world', 'F16', '--visibility', 'private', '--witnesses', 'juno')  # known: true, still out
        self.brains('world', 'F17', '--visibility', 'private', '--witnesses', 'juno')
        self.brains('world', 'F18', '--visibility', 'public')
        self.brains('world', 'F19', '--visibility', 'witnessed', '--witnesses', 'mara')
        self.brains('know', 'mara', 'F13', '--how', 'I read it in the ledger margin', '--confidence', 'certain',
                    '--entry', self.entry)
        self.brains('know', 'mara', 'F14', '--how', 'I heard Juno say it in her sleep', '--confidence', 'suspects',
                    '--entry', self.entry)
        self.brains('know', 'mara', 'F17', '--how', 'I guessed it', '--confidence', 'doubts', '--entry', self.entry)
        self.brains('unlearn', 'mara', 'F17', '--entry', self.entry, '--why', 'the guess was shown wrong')
        self.gm([{'op': 'update', 'kind': 'fact', 'id': 'F18', 'status': 'outdated', 'reason': 'the tide turned'},
                 {'op': 'update', 'kind': 'fact', 'id': 'F19', 'status': 'discarded', 'reason': 'an unused idea'}])

    def brief(self, npc='mara', scene='Juno sets a wet lantern on the bollard.\n', *extra, expect=0):
        self.scene.write_text(scene, encoding='utf-8')
        return self.brains('brief', npc, '--scene', str(self.scene), '--text', *extra, expect=expect)

    def known_texts(self, brief):
        block = brief.split('WHAT THEY KNOW\n')[1].split('\n\n')[0]
        return {re.sub(r' \(.*\)$', '', ln[2:]) for ln in block.split('\n') if ln.startswith('- ')}

    # ---- the brief ----

    def test_twenty_fact_fixture_brief_holds_exactly_public_witnessed_and_known_facts(self):
        self.fixture()
        expected = {text(n) for n in (1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14)}
        self.assertEqual(self.known_texts(self.brief()), expected)
        juno = {text(n) for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 20)}
        self.assertEqual(self.known_texts(self.brief('juno')), juno)
        self.assertEqual(self.brains('check')['ok'], True)

    def test_a_hidden_fact_stays_out_even_when_the_character_is_tagged_and_present(self):
        self.fixture()
        brief = self.brief()
        self.assertNotIn(text(15), brief)
        self.assertNotIn(text(16), brief)  # known to the player, not to Mara
        self.assertIn(text(2), brief)      # known: false is not read either way
        self.brains('know', 'mara', 'F15', '--how', 'I saw the mark on her door', '--confidence', 'probable',
                    '--entry', self.entry)
        self.assertIn(text(15) + ' (probably; how: I saw the mark on her door)', self.brief())

    def test_another_characters_secret_stays_out(self):
        self.fixture()
        self.assertNotIn(text(11), self.brief())
        self.assertNotIn('informs for the harbourmaster', self.brief())
        self.assertIn(text(11) + ' (you keep this secret)', self.brief('juno'))
        self.assertIn('secret: she forged the manifest', self.brief())

    def test_the_known_flag_is_never_read_by_the_builder(self):
        source = BRAINS.read_text(encoding='utf-8')
        self.assertNotRegex(source, r"\[['\"]known['\"]\]|get\(['\"]known['\"]")

    def test_brief_is_byte_identical_and_carries_no_ids_or_paths(self):
        self.fixture()
        first, second = self.brief(), self.brief()
        self.assertEqual(first.encode(), second.encode())
        self.assertNotRegex(first, r'\bF\d+\b|\bT\d+\b|[0-9a-f]{8}-[0-9a-f]{4}|notes/|\.jsonl|\.md\b')
        self.assertIn('You are the mind of Mara Venn, 34, in the harbour.', first)
        self.assertIn('voice: clipped, dry, never finishes a joke', first)
        self.assertIn('look: tall, salt-grey hair, a burn on one wrist', first)
        self.assertIn('NOW\nday 2, dusk, the harbour\nJuno sets a wet lantern on the bollard.', first)
        self.assertTrue(first.rstrip().endswith('DECIDES: a lasting intention they form now (to leave, to refuse, '
                                                'to do something later), or (none)'))
        wrapped = self.brains('brief', 'mara', '--scene', str(self.scene))
        self.assertEqual(wrapped['brief'], first)

    def test_threads_only_from_the_characters_list(self):
        self.fixture()
        brief = self.brief()
        self.assertIn('WHAT IS OWED\n- Mara promised the player a boat.', brief)
        self.assertNotIn('drowned the clerk', brief)
        self.assertNotIn('WHAT IS OWED', self.brief('juno'))

    def test_scene_file_with_a_fact_line_or_entry_id_is_refused(self):
        self.fixture()
        out = self.brief('mara', 'FACT F11 Juno informs.\n', expect=2)
        self.assertIn('game-master fact line', out['error'])
        out = self.brief('mara', f'She remembers {self.entry}.\n', expect=2)
        self.assertIn('entry id', out['error'])
        out = self.brief('mara', 'She reads notes/gm/deltas.jsonl aloud.\n', expect=2)
        self.assertIn('file path', out['error'])

    def test_a_fact_text_holding_an_id_is_refused_rather_than_leaked(self):
        self.cast()
        self.gm([self.fact(1, text='The crate is stamped F7.')])
        self.brains('world', 'F1', '--visibility', 'public')
        self.assertIn('ids F7', self.brief(expect=2)['error'])

    def test_alias_heads_the_brief_only_when_recorded(self):
        self.fixture()
        self.assertIn('You are the mind of Red, who is Mara Venn, 34', self.brief('mara', 'Fog.\n', '--as', 'Red'))
        self.brief('mara', 'Fog.\n', '--as', 'Nobody', expect=2)

    def test_at_most_six_episodes_by_salience_then_recency(self):
        self.cast()
        for n, salience in enumerate((5, 1, 1, 4, 2, 3, 1, 2), 1):
            self.brains('remember', 'mara', '--text', f'Episode {NAMES[n - 1]}.', '--salience', str(salience),
                        '--entry', self.entry)
        block = self.brief().split('WHAT THEY REMEMBER\n')[1].split('\n\n')[0]
        self.assertEqual(block.split('\n'), ['- Episode amber.', '- Episode dune.', '- Episode ember.',
                                             '- Episode fennel.', '- Episode garnet.', '- Episode hazel.'])

    def test_compress_folds_episodes_into_one(self):
        self.cast()
        seqs = [str(self.brains('remember', 'mara', '--text', f'Episode {n}.', '--entry', self.entry)['seq'])
                for n in NAMES[:3]]
        self.brains('compress', 'mara', '--replace', *seqs[:2], '--text', 'A long, bad week.')
        brief = self.brief()
        self.assertIn('- Episode cedar.\n- A long, bad week.', brief)
        self.assertNotIn('Episode amber', brief)
        self.brains('compress', 'mara', '--replace', seqs[0], seqs[2], '--text', 'x', expect=2)

    # ---- validation, views and check ----

    def test_world_needs_witnesses_except_public_and_audit_lists_the_unclassified(self):
        self.cast()
        self.gm([self.fact(1), self.fact(2)])
        self.brains('world', 'F1', '--visibility', 'witnessed', expect=2)
        self.brains('world', 'F1', '--visibility', 'public', '--witnesses', 'mara', expect=2)
        self.brains('world', 'F1', '--visibility', 'secret', '--witnesses', 'nobody', expect=2)
        self.brains('world', 'F9', '--visibility', 'public', expect=2)
        self.brains('world', 'F1', '--visibility', 'public')
        audit = self.brains('world', '--audit', expect=1)
        self.assertEqual([u['fact'] for u in audit['unclassified']], ['F2'])

    def test_check_fails_on_an_unclassified_fact(self):
        self.cast()
        self.gm([self.fact(1)])
        self.assertIn('F1 has no brain visibility', self.brains('check', expect=2)['error'])
        self.assertNotIn(text(1), self.brief())  # no record: hidden from every brain
        self.brains('world', 'F1', '--visibility', 'public')
        self.assertEqual(self.brains('check')['brains'], ['juno', 'mara'])

    def test_know_needs_first_person_an_entry_and_a_live_fact(self):
        self.fixture()
        base = ['know', 'mara', 'F9', '--confidence', 'certain']
        self.brains(*base, '--how', 'She was told by Juno', '--entry', self.entry, expect=2)
        self.brains(*base, '--how', 'I was told by Juno', expect=2)
        self.brains(*base, '--how', 'I was told by Juno', '--entry', str(uuid4()), expect=2)
        self.brains('know', 'mara', 'F18', '--how', 'I saw it', '--confidence', 'certain', '--entry', self.entry,
                    expect=2)
        self.brains('know', 'nobody', 'F9', '--how', 'I saw it', '--confidence', 'certain', '--entry', self.entry,
                    expect=2)

    def test_unlearn_removes_even_a_public_fact_until_known_again(self):
        self.fixture()
        self.brains('unlearn', 'mara', 'F1', '--entry', self.entry, '--why', 'struck on the head')
        self.assertNotIn(text(1), self.brief())
        self.brains('unlearn', 'mara', 'F1', '--entry', self.entry, '--why', 'again', expect=2)
        self.brains('know', 'mara', 'F1', '--how', 'I read it again', '--confidence', 'certain', '--entry', self.entry)
        self.assertIn(text(1), self.brief())

    def test_events_are_appended_with_their_fields_and_views_are_generated(self):
        self.fixture()
        events = [json.loads(ln) for ln in (self.root / 'notes/brains/events.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual([e['seq'] for e in events], list(range(1, len(events) + 1)))
        for e in events:
            self.assertEqual(list(e), ['seq', 'at', 'npc', 'op', 'entry', 'why', 'data'])
        self.assertIsNone(events[0]['entry'])
        self.brains('view')  # the fixture's last change was in game-master
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertTrue(view.startswith('<!-- generated from events.jsonl; do not edit -->\n'))
        self.assertIn('F14 [know, suspects]', view)
        (self.root / 'notes/brains/mara.md').write_text(view + 'hand edit\n', encoding='utf-8')
        self.brains('check')  # every command rewrites the views
        self.assertEqual((self.root / 'notes/brains/mara.md').read_text(encoding='utf-8'), view)
        self.brains('session', 'mara', '--id', 'abc', '--tier', 'persistent')
        self.assertIn('session: abc', (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8'))
        self.assertIn('tier: persistent', self.brains('view', 'mara')['view'])

    def test_refuses_over_method_only_brain_files(self):
        brains = self.root / 'notes' / 'brains'
        brains.mkdir(parents=True)
        (brains / 'mara.md').write_text('# Brain file: Mara\n\nnpc: mara\nsession: none yet\n', encoding='utf-8')
        (brains / 'PROTOCOL.md').write_text('npc: x\n', encoding='utf-8')
        self.assertIn('method-only brain files (mara.md)', self.brains('init', expect=2)['error'])

    def test_needs_game_master(self):
        (self.root / 'tools' / 'gm_state.py').unlink()
        self.assertIn('game-master is not installed', self.brains('init', expect=2)['error'])


class BrainsDocs(unittest.TestCase):
    def test_package_files_and_method_only_refusal(self):
        plus = PACKAGES / 'character-brains-plus'
        for name in ('PACKAGE.md', 'APPLY.md', 'files/brains.py', 'files/PROTOCOL.md', 'files/scene-template.md',
                     'files/brain-template.md'):
            self.assertTrue((plus / name).is_file(), name)
        self.assertIn('notes/brains/events.jsonl', (PACKAGES / 'character-brains/APPLY.md').read_text(encoding='utf-8'))
        protocol = (plus / 'files/PROTOCOL.md').read_text(encoding='utf-8')
        self.assertIn('knows too much', protocol)
        self.assertIn('DECIDES', protocol)
        for command in ('init', 'add', 'world', 'know', 'unlearn', 'remember', 'compress', 'session', 'brief',
                        'view', 'check'):
            self.assertIn(f'brains.py {command}', protocol + (plus / 'APPLY.md').read_text(encoding='utf-8'), command)


if __name__ == '__main__':
    unittest.main()
