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
                                                'to do something later), or (nothing)'))
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

    # ---- migration and Undo (ISS-25) ----

    def method_only(self, name='mara.md', npc='mara', **sections):
        body = {'Look': 'Tall, salt-grey hair, a burn on one wrist.',
                'Desire': 'She wants to be wanted, and will never say so.',
                'Knows': f'- F2, from {self.entry}\n- that Juno lies about the ledger\n- F99, from {self.entry}',
                'Memory': ('- She took the player\'s coin and\n  did not count it.\n- The tide office turned her away.\n'
                           '- ' + 'She waited on the quay all night. ' * 12 + '\n'
                           'DIGEST: she trusts the player a little more; she wants the boat back.'),
                'Digest': 'Owes the player now.\nWill not go back to the tide office.', **sections}
        text = (f'# Brain file: Mara\n\nnpc: {npc}\nsession: sess-41\ntier: persistent (since day 2, because ...)\n\n'
                + ''.join(f'## {k}\n\n{v}\n\n' for k, v in body.items() if v is not None))
        brains = self.root / 'notes' / 'brains'
        brains.mkdir(parents=True, exist_ok=True)
        (brains / name).write_text(text, encoding='utf-8', newline='\n')
        return text

    def events(self, name='events.jsonl'):
        path = self.root / 'notes/brains' / name
        return [json.loads(ln) for ln in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []

    def test_migrate_keeps_every_memory_bullet_and_invents_no_know(self):
        self.cast()  # mara and juno are already in the log; migrate a third character
        self.gm([self.fact(1), self.fact(2, known=False),
                 {'op': 'set', 'kind': 'npc', 'id': 'oren', 'fields': {'name': 'Oren Pike', 'want': 'quiet'}}])
        self.brains('world', 'F1', '--visibility', 'public')
        self.brains('world', 'F2', '--visibility', 'secret', '--witnesses', 'juno')
        original = self.method_only('oren.md', 'oren')
        before = len(self.events())
        out = self.brains('migrate', expect=1)
        self.assertEqual((self.root / 'notes/brains/legacy/oren.md').read_text(encoding='utf-8'), original)
        self.assertTrue((self.root / 'notes/brains/oren.md').read_text(encoding='utf-8').startswith('<!-- generated'))
        new = self.events()[before:]
        self.assertEqual([e['op'] for e in new[:2]], ['char', 'session'])
        self.assertEqual(new[0]['data']['look'], 'Tall, salt-grey hair, a burn on one wrist.')
        self.assertEqual(new[1]['data'], {'session': 'sess-41', 'tier': 'persistent'})
        memories = [e['data'] for e in new if e['op'] == 'remember']
        texts = [m['text'] for m in memories]
        self.assertEqual(texts[:2], ["She took the player's coin and did not count it.", 'The tide office turned her away.'])
        long = ' '.join(t for t in texts if t.startswith('She waited'))
        self.assertEqual(long, ('She waited on the quay all night. ' * 12).strip())  # split, nothing lost
        self.assertEqual(texts[-2:], ['she trusts the player a little more; she wants the boat back.',
                                      'Owes the player now. Will not go back to the tide office.'])
        self.assertEqual([m['salience'] for m in memories][-2:], [4, 4])
        self.assertTrue(all(e['entry'] == self.entry for e in new if e['op'] == 'remember'))
        knows = [e for e in new if e['op'] == 'know']
        self.assertEqual([(k['data']['fact'], k['data']['how'], k['entry']) for k in knows], [('F2', 'migrated', self.entry)])
        joined = ' '.join(out['warnings'])
        for needle in ('names no fact id', 'names F99, not a game-master fact', 'Desire line is kept only',
                       'state oren --set desire.limits', 'split into 2 episodes', 'no know event was invented'):
            self.assertIn(needle, joined)
        brief = self.brief('oren')
        self.assertNotIn('DESIRE', brief)  # never guessed into fields; the writer records it with state
        self.assertIn(text(2), brief)
        self.assertNotIn('migrated', brief)
        self.assertEqual(self.brains('check')['ok'], True)
        self.assertEqual(self.brains('migrate', expect=1)['migrated'], [])  # nothing left to move

    def test_migrate_writes_nothing_to_the_log_when_a_file_cannot_move(self):
        self.cast()
        self.method_only('mara.md', 'mara')  # mara already has a brain in the log
        before = (self.root / 'notes/brains/events.jsonl').read_bytes()
        self.assertIn('already has a brain', self.brains('migrate', expect=2)['error'])
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), before)
        self.assertTrue((self.root / 'notes/brains/mara.md').read_text(encoding='utf-8').startswith('# Brain file'))
        self.brains('check', expect=2)  # still refused over the method-only file
        (self.root / 'notes/brains/mara.md').unlink()
        self.method_only('stray.md', 'nobody')
        self.assertIn('no game-master cast card', self.brains('migrate', expect=2)['error'])
        self.assertTrue((self.root / 'notes/brains/legacy/stray.md').exists())  # the copy came first

    def test_migrate_from_a_fresh_story_needs_no_init(self):
        self.gm([{'op': 'set', 'kind': 'npc', 'id': 'mara', 'fields': {'name': 'Mara Venn'}}])
        self.method_only(Knows=None, Desire=None, Digest=None)
        out = self.brains('migrate', expect=1)
        self.assertEqual(out['migrated'][0]['memories'], 4)
        self.assertEqual(out['migrated'][0]['summaries'], 1)
        self.assertEqual(self.brains('view', 'mara')['view'].count('[salience'), 5)

    def test_an_event_citing_a_withdrawn_entry_leaves_the_brief(self):
        self.fixture()
        undone = self.add_entry('The clerk confessed.')
        self.brains('know', 'mara', 'F9', '--how', 'I heard the clerk confess', '--confidence', 'certain',
                    '--entry', undone)
        first = self.brains('remember', 'mara', '--text', 'The clerk wept.', '--entry', undone)['seq']
        second = self.brains('remember', 'mara', '--text', 'Rain all day.', '--entry', self.entry)['seq']
        self.brains('remember', 'mara', '--text', 'Rain again.', '--entry', self.entry)
        self.brains('compress', 'mara', '--replace', str(first), str(second), '--text', 'A wet, sad day.')
        self.brains('unlearn', 'mara', 'F9', '--entry', self.entry, '--why', 'she decided he lied')
        self.brains('know', 'mara', 'F10', '--how', 'I heard it too', '--confidence', 'probable', '--entry', self.entry)
        self.assertNotIn(text(9), self.brief())
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('The clerk confessed.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        self.assertIn('reconcile', self.brief(expect=2)['error'])  # no brief while the log cites what never happened
        log = (self.root / 'notes/brains/events.jsonl').read_bytes()
        dry = self.brains('reconcile', expect=1)
        self.assertEqual([e['op'] for e in dry['set_aside']], ['know', 'remember', 'compress', 'unlearn'])
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), log)  # a dry run changes nothing
        done = self.brains('reconcile', '--apply')
        self.assertTrue(done['applied'])
        self.assertEqual(len(self.events('withdrawn.jsonl')), 4)
        brief = self.brief()
        self.assertNotIn(text(9), brief)
        self.assertNotIn('clerk wept', brief)
        self.assertNotIn('wet, sad day', brief)
        self.assertIn('- Rain all day.\n- Rain again.', brief)  # the episodes compress had folded come back
        self.assertIn(text(10), brief)
        self.assertEqual(self.brains('check')['ok'], True)
        self.assertEqual(self.brains('reconcile')['set_aside'], [])
        used = {e['seq'] for e in self.events() + self.events('withdrawn.jsonl')}
        self.assertNotIn(self.brains('remember', 'mara', '--text', 'Later.', '--entry', self.entry)['seq'], used)

    def test_reconcile_follows_a_fact_game_master_withdrew(self):
        self.cast()
        undone = self.add_entry('A body in the dock.')
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(
            {'entry': undone, 'why': 'the story showed it', 'ops': [self.fact(1)]}), encoding='utf-8')
        self.assertEqual(run(self.root, 'gm_state.py', 'commit').returncode, 0)
        self.brains('world', 'F1', '--visibility', 'public')  # setup event: cites no entry, rests on F1
        self.assertIn(text(1), self.brief())
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('A body in the dock.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        self.assertEqual(run(self.root, 'gm_state.py', 'reconcile', '--apply').returncode, 0)  # game-master first
        out = self.brains('reconcile', '--apply')
        self.assertEqual([(e['op'], 'F1 is no longer a game-master fact' in e['why']) for e in out['set_aside']],
                         [('world', True)])
        self.assertEqual(self.brains('check')['ok'], True)

    # ---- body, mood and desire (ISS-26) ----

    def state(self, *sets, npc='mara', expect=0, entry=None):
        return self.brains('state', npc, '--set', *sets, '--entry', entry or self.entry, expect=expect)

    def block(self, brief, title):
        return brief.split(f'\n\n{title}\n')[1].split('\n\n')[0].split('\n') if f'\n\n{title}\n' in brief else []

    def test_levels_reach_the_brief_as_words_never_numbers(self):
        self.cast()
        self.state('affect.energy=0', 'affect.pain=1', 'affect.fear=2', 'affect.shame=3', 'affect.arousal=4',
                   'affect.intoxication=5', 'affect.valence=-2', 'affect.mood=tense, watching the door')
        lines = self.block(self.brief(), 'HOW THEY ARE')
        self.assertEqual(lines, ['mood: tense, watching the door', 'spirits: low', 'energy: none', 'pain: a little',
                                 'fear: some', 'shame: a lot', 'arousal: badly', 'intoxication: overwhelming'])
        for value, word in ((-3, 'wretched'), (-1, 'a little low'), (1, 'a little lifted'), (2, 'good'), (3, 'elated')):
            self.state(f'affect.valence={value}')
            self.assertIn(f'spirits: {word}', self.block(self.brief(), 'HOW THEY ARE'))
        self.assertNotRegex('\n'.join(self.block(self.brief(), 'HOW THEY ARE')), r'\d')

    def test_empty_fields_are_left_out_and_an_empty_value_clears(self):
        self.cast()
        brief = self.brief()
        self.assertNotIn('HOW THEY ARE', brief)
        self.assertNotIn('DESIRE', brief)
        self.state('affect.fear=0', 'affect.valence=0', 'body.clothes=a wet oilskin', 'desire.wants=to be chosen')
        self.assertEqual(self.block(self.brief(), 'HOW THEY ARE'), ['wearing: a wet oilskin'])  # 0 is an absence
        self.state('body.clothes=', 'desire.wants=')
        brief = self.brief()
        self.assertNotIn('HOW THEY ARE', brief)
        self.assertNotIn('DESIRE', brief)
        self.assertEqual(self.brains('state', 'mara')['state'], {'affect': {'fear': 0, 'valence': 0}})

    def test_body_marks_say_who_can_see_them_and_desire_comes_before_now(self):
        self.cast()
        self.state('body.condition=a cracked rib', 'body.marks.burn=a burn on one wrist',
                   'body.marks.burn.seen_by=anyone', 'body.marks.tattoo=a gull under the left breast',
                   'body.marks.tattoo.seen_by=juno', 'body.marks.bruise=a bruise on the hip',
                   'body.marks.bruise.seen_by=nobody', 'body.carrying=a gutting knife',
                   'body.capacities=cannot lift the left arm', 'desire.orientation=women, mostly',
                   'desire.limits=nothing in front of others', 'desire.never_admits=that she misses Juno',
                   'desire.current=the player, a little')
        brief = self.brief()
        self.assertEqual(self.block(brief, 'HOW THEY ARE'), [
            'condition: a cracked rib',
            'marks: a bruise on the hip (hidden); a burn on one wrist (anyone can see it); '
            'a gull under the left breast (seen by Juno Ash)',
            'carrying: a gutting knife', 'capacities: cannot lift the left arm'])
        self.assertEqual(self.block(brief, 'DESIRE'), [
            'orientation: women, mostly', 'limits (never crossed, whatever happens): nothing in front of others',
            'would never admit: that she misses Juno', 'right now: the player, a little'])
        order = [brief.index(h) for h in ('WHAT THEY KNOW', 'HOW THEY ARE', 'DESIRE', '\n\nNOW\n', 'ANSWER')]
        self.assertEqual(order, sorted(order))
        self.assertEqual(self.brief().encode(), brief.encode())  # same state, same bytes
        self.state('body.marks.bruise=')
        self.assertNotIn('bruise', self.brief())
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertIn('- body.marks.tattoo: a gull under the left breast (seen by Juno Ash)', view)
        self.assertIn('- desire.limits: nothing in front of others', view)

    def test_tick_moves_each_level_one_step_toward_baseline(self):
        self.cast()
        self.brains('add', 'mara', '--baseline', 'valence=1', 'fear=1')
        self.state('affect.valence=-2', 'affect.fear=4', 'affect.energy=0', 'affect.shame=1', 'affect.pain=3',
                   'affect.intoxication=2', 'affect.arousal=0')
        out = self.brains('tick', 'mara', '--entry', self.entry)
        self.assertEqual(out['moved'], {'valence': [-2, -1], 'energy': [0, 1], 'fear': [4, 3], 'shame': [1, 0]})
        affect = self.brains('state', 'mara')['affect']
        self.assertEqual((affect['pain'], affect['intoxication']), (3, 2))  # only at a scene boundary
        out = self.brains('tick', 'mara', '--scene-end', '--entry', self.entry)
        self.assertEqual(out['moved'], {'valence': [-1, 0], 'energy': [1, 2], 'pain': [3, 2], 'fear': [3, 2],
                                        'intoxication': [2, 1]})
        for _ in range(2):
            self.brains('tick', 'mara', '--scene-end', '--entry', self.entry)
        affect = self.brains('state', 'mara')['affect']
        self.assertEqual(affect, {'valence': 1, 'fear': 1, 'energy': 3, 'shame': 0, 'pain': 0, 'intoxication': 0,
                                  'arousal': 0})
        count = len(self.events())
        out = self.brains('tick', 'mara', '--scene-end', '--entry', self.entry, expect=1)
        self.assertEqual(out['moved'], {})
        self.assertEqual(len(self.events()), count)  # nothing to move, nothing recorded
        self.state('affect.pain=2')
        self.assertIn('until a scene boundary (pain', self.brains('tick', 'mara', '--entry', self.entry,
                                                                  expect=1)['warnings'][0])
        self.assertEqual(self.brains('tick', 'mara', '--entry', self.entry + 'x', '--scene-end', expect=2)['ok'], False)

    def test_baseline_is_where_an_unset_level_stands(self):
        self.cast()
        self.brains('add', 'juno', '--baseline', 'valence=-1', 'energy=2')
        self.assertEqual(self.block(self.brief('juno'), 'HOW THEY ARE'), ['spirits: a little low', 'energy: some'])
        self.brains('add', 'juno', '--baseline', 'fear=2')  # a later add keeps the rest of the baseline
        self.assertEqual(self.brains('state', 'juno')['affect'], {'valence': -1, 'energy': 2, 'fear': 2})
        for bad in ('fear=6', 'valence=-4', 'mood=1', 'fear=lots'):
            self.assertIn('baseline', self.brains('add', 'juno', '--baseline', bad, expect=2)['error'])

    def test_state_validates_every_field_before_appending(self):
        self.cast()
        log = (self.root / 'notes/brains/events.jsonl').read_bytes()
        bad = {'affect.fear=6': 'from 0 to 5', 'affect.energy=-1': 'from 0 to 5', 'affect.valence=4': 'from -3 to 3',
               'affect.valence=-4': 'from -3 to 3', 'affect.fear=a lot': 'whole number', 'affect.joy=2': "no 'joy'",
               'mood=calm': "state has no 'mood'", 'affect.mood.tone=x': 'single value',
               'body.marks=a scar': 'holds fields', 'body.marks.burn.seen_by=nobody-here': 'is not cast',
               'body.marks.burn.seen_by=anyone': 'needs its text first', 'desire.limits=' + 'x' * 301: 'at most 300',
               'affect.fear': 'PATH=VALUE'}
        for item, needle in bad.items():
            self.assertIn(needle, self.state(item, expect=2)['error'], item)
        self.assertIn('from 0 to 5', self.state('affect.fear=3', 'affect.pain=9', expect=2)['error'])  # all or nothing
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), log)  # nothing was appended
        self.assertIn('needs --entry', self.brains('state', 'mara', '--set', 'affect.fear=2', expect=2)['error'])
        self.assertIn('no brain yet', self.state('affect.fear=2', npc='nobody', expect=2)['error'])
        ev = self.state('affect.fear=3', 'body.marks.burn=a burn', 'body.marks.burn.seen_by=juno,mara')
        self.assertEqual(self.events()[-1]['data'], {'set': [['affect.fear', 3], ['body.marks.burn.text', 'a burn'],
                                                             ['body.marks.burn.seen_by', ['juno', 'mara']]]})
        self.assertEqual(self.events()[-1]['seq'], ev['seq'])
        self.assertEqual(self.brains('check')['ok'], True)

    def test_reconcile_replays_state_and_tick_without_what_was_undone(self):
        self.cast()
        undone = self.add_entry('The boat capsized.')
        self.state('affect.fear=4', 'body.condition=soaked through', entry=undone)
        self.state('affect.pain=2')
        self.brains('tick', 'mara', '--scene-end', '--entry', self.entry)
        self.assertEqual(self.brains('state', 'mara')['affect'], {'fear': 3, 'pain': 1})
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('The boat capsized.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        done = self.brains('reconcile', '--apply')
        self.assertEqual([e['op'] for e in done['set_aside']], ['state'])
        self.assertEqual(self.brains('state', 'mara')['affect'], {'pain': 1})  # the tick stands, on what is left
        brief = self.brief()
        self.assertNotIn('soaked', brief)
        self.assertEqual(self.block(brief, 'HOW THEY ARE'), ['pain: a little'])

    def test_reconcile_sets_aside_a_mark_seen_by_someone_no_longer_cast(self):
        self.cast()
        undone = self.add_entry('A stranger arrives.')
        self.entry, kept = undone, self.entry
        self.gm([{'op': 'set', 'kind': 'npc', 'id': 'oren', 'fields': {'name': 'Oren'}}])
        self.entry = kept
        self.state('body.marks.scar=a scar', 'body.marks.scar.seen_by=oren')
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('A stranger arrives.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        self.assertEqual(run(self.root, 'gm_state.py', 'reconcile', '--apply').returncode, 0)
        out = self.brains('reconcile', '--apply')
        self.assertEqual([(e['op'], 'oren' in e['why']) for e in out['set_aside']], [('state', True)])
        self.assertNotIn('scar', self.brief())

    # ---- beliefs, claims and other minds (ISS-27) ----

    def believe(self, text, truth='false', confidence='certain', *extra, npc='mara', expect=0):
        return self.brains('believe', npc, '--text', text, '--truth', truth, '--confidence', confidence, *extra,
                           '--entry', self.entry, expect=expect)

    def claim(self, to, text, truth, kind, *extra, npc='mara', expect=0):
        return self.brains('claim', npc, '--to', to, '--text', text, '--truth', truth, '--kind', kind, *extra,
                           '--entry', self.entry, expect=expect)

    def test_a_false_belief_appears_with_no_label(self):
        self.cast()
        self.gm([self.fact(1)])
        self.brains('world', 'F1', '--visibility', 'secret', '--witnesses', 'juno')
        self.believe('The clerk slipped on the wet steps.', 'false', 'certain', '--about', 'F1')
        self.believe('Juno would never sell me out.', 'unknown', 'probable')
        brief = self.brief()
        self.assertEqual(self.block(brief, 'WHAT THEY BELIEVE'),
                         ['- The clerk slipped on the wet steps.', '- Juno would never sell me out. (probably)'])
        self.assertNotIn(text(1), brief)  # the fact it is about stays hidden
        self.assertNotRegex(brief, r'\b(false|unknown|untrue)\b')
        order = [brief.index(h) for h in ('WHAT THEY KNOW', 'WHAT THEY BELIEVE', '\n\nNOW\n')]
        self.assertEqual(order, sorted(order))
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertRegex(view, r'- seq \d+ \[false, certain, about F1\] The clerk slipped')

    def test_at_most_twelve_beliefs_and_retire_frees_a_place(self):
        self.cast()
        seqs = [self.believe(f'Belief number {n}.', 'unknown')['seq'] for n in range(12)]
        log = (self.root / 'notes/brains/events.jsonl').read_bytes()
        self.assertIn('12 beliefs already', self.believe('One too many.', expect=2)['error'])
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), log)
        out = self.believe('A replacement.', 'true', 'doubts', '--retire', str(seqs[0]))
        self.assertEqual(out['active'], 12)
        self.assertEqual(self.brains('believe', 'mara', '--retire', str(seqs[1]), '--entry', self.entry)['active'], 11)
        lines = self.block(self.brief(), 'WHAT THEY BELIEVE')
        self.assertEqual(len(lines), 11)
        self.assertNotIn('- Belief number 0.', lines)
        self.assertEqual(lines[-1], '- A replacement. (you doubt this)')
        self.assertIn('not an active belief', self.brains('believe', 'mara', '--retire', str(seqs[0]),
                                                          '--entry', self.entry, expect=2)['error'])
        self.assertIn('not a game-master fact', self.believe('x', 'true', 'certain', '--about', 'F99', expect=2)['error'])
        self.assertIn('needs --entry', self.brains('believe', 'mara', '--text', 'x', '--truth', 'true',
                                                   '--confidence', 'certain', expect=2)['error'])

    def test_claims_print_six_people_present_first_never_the_truth(self):
        self.cast()
        self.gm([{'op': 'set', 'kind': 'npc', 'id': 'oren', 'fields': {'name': 'Oren Pike'}}])  # not present
        self.claim('oren', 'Oren claim one.', 'true', 'truth')
        self.claim('juno', 'Juno claim one.', 'false', 'lie')
        for n in range(1, 5):
            self.claim('oren', f'Oren claim {n + 1}.', 'unknown', 'boast')
        self.claim('player', 'You will have the boat by Sunday.', 'false', 'promise')
        self.claim('juno', 'that the boat leaks', 'true', 'omission')
        lines = self.block(self.brief(), 'WHAT THEY HAVE TOLD PEOPLE')
        self.assertEqual(lines, [
            '- to Juno Ash, kept back: that the boat leaks',
            '- to the player, a promise: You will have the boat by Sunday.',
            '- to Juno Ash, a lie: Juno claim one.',
            '- to Oren Pike, a boast: Oren claim 5.', '- to Oren Pike, a boast: Oren claim 4.',
            '- to Oren Pike, a boast: Oren claim 3.'])
        self.assertNotRegex('\n'.join(lines), r'\b(true|false|unknown)\b')
        self.assertIn('is false by its kind', self.claim('juno', 'x', 'true', 'lie', expect=2)['error'])
        self.assertIn('is true by its kind', self.claim('juno', 'x', 'false', 'truth', expect=2)['error'])
        self.assertIn('not cast', self.claim('nobody', 'x', 'true', 'boast', expect=2)['error'])
        self.assertIn('themself', self.claim('mara', 'x', 'true', 'boast', expect=2)['error'])

    def test_check_warns_when_a_claim_contradicts_an_earlier_one_to_the_same_person(self):
        self.cast()
        self.gm([self.fact(1), self.fact(2)])
        for n in (1, 2):
            self.brains('world', f'F{n}', '--visibility', 'public')
        first = self.claim('juno', 'I never touched the manifest.', 'false', 'lie', '--about', 'F1')
        self.claim('player', 'I forged it.', 'true', 'truth', '--about', 'F1')  # another listener
        self.claim('juno', 'The tide was early.', 'true', 'truth', '--about', 'F2')  # another fact
        self.claim('juno', 'Maybe I signed it.', 'unknown', 'half-truth', '--about', 'F1')  # unknown never clashes
        self.assertEqual(self.brains('check')['warnings'], [])
        out = self.claim('juno', 'Fine, I forged it.', 'true', 'truth', '--about', 'F1', expect=1)
        self.assertEqual(len(out['warnings']), 1)
        self.assertIn(f'seq {first["seq"]} (lie, false) and seq {out["seq"]} (truth, true)', out['warnings'][0])
        warns = self.brains('check', expect=1)['warnings']
        self.assertEqual(warns, out['warnings'])
        self.assertEqual(self.brief().encode(), self.brief().encode())  # same state, same bytes

    def test_edges_print_in_words_for_three_people_two_propositions_each(self):
        self.cast()
        self.gm([{'op': 'set', 'kind': 'npc', 'id': 'oren', 'fields': {'name': 'Oren Pike'}},
                 {'op': 'set', 'kind': 'npc', 'id': 'tess', 'fields': {'name': 'Tess'}}]
                + [self.fact(n) for n in range(1, 6)])
        for n in range(1, 6):
            self.brains('world', f'F{n}', '--visibility', 'public')
        self.state('people.oren.trust=1')
        self.state('people.juno.trust=4', 'people.juno.attraction=2', 'people.juno.fear=0', 'people.juno.debt=-3',
                   'people.juno.last=she covered for me at the weigh-house', 'people.juno.thinks_knows.F1=knows',
                   'people.juno.thinks_knows.F2=unsure', 'people.juno.thinks_knows.F3=doesnt',
                   'people.juno.thinks_knows.F4=knows')
        self.state('people.tess.debt=2')
        self.state('people.player.fear=1')
        brief = self.brief()
        self.assertEqual(self.block(brief, 'OTHER PEOPLE'), [
            'the player', '  fear of them: a little',
            'Juno Ash', '  trust: deeply; attraction: some; you owe them a lot',
            '  last between you: she covered for me at the weigh-house',
            f'  you think they do not know: {text(3)}', f'  you are not sure they know: {text(2)}',
            'Tess', '  they owe you something'])  # present first, then the latest recorded; Oren is left out
        self.assertNotRegex('\n'.join(self.block(brief, 'OTHER PEOPLE')), r'\d')
        order = [brief.index(h) for h in ('WHAT THEY KNOW', 'OTHER PEOPLE', '\n\nNOW\n')]
        self.assertEqual(order, sorted(order))
        self.assertEqual(self.brief().encode(), brief.encode())  # same state, same bytes
        self.assertIn('at most 4 facts', self.state('people.juno.thinks_knows.F5=knows', expect=2)['error'])
        self.state('people.juno.thinks_knows.F1=', 'people.juno.thinks_knows.F5=knows')  # clear one, then a fifth fits
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertIn('- people.juno.debt: -3', view)
        self.assertIn('- people.juno.thinks_knows.F3: doesnt', view)

    def test_a_thinks_knows_about_a_fact_the_character_cannot_know_is_refused(self):
        self.cast()
        self.gm([self.fact(1), self.fact(2)])
        self.brains('world', 'F1', '--visibility', 'secret', '--witnesses', 'juno')
        self.brains('world', 'F2', '--visibility', 'witnessed', '--witnesses', 'mara')
        log = (self.root / 'notes/brains/events.jsonl').read_bytes()
        self.assertIn('does not know F1 exists', self.state('people.juno.thinks_knows.F1=knows', expect=2)['error'])
        self.assertIn('not a game-master fact', self.state('people.juno.thinks_knows.F9=knows', expect=2)['error'])
        bad = {'people.juno.thinks_knows.F2=maybe': 'one of knows, doesnt, unsure', 'people.juno.trust=6': 'from 0 to 5',
               'people.juno.debt=-6': 'from -5 to 5', 'people.ghost.trust=1': 'is not cast',
               'people.mara.trust=1': 'themself', 'people.juno=x': 'holds fields'}
        for item, needle in bad.items():
            self.assertIn(needle, self.state(item, expect=2)['error'], item)
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), log)
        self.state('people.juno.thinks_knows.F2=doesnt')
        self.assertIn(f'you think they do not know: {text(2)}', self.brief())
        self.brains('unlearn', 'mara', 'F2', '--entry', self.entry, '--why', 'she was made to forget')
        self.assertNotIn(text(2), self.brief())  # an unlearn takes the proposition out of the brief too
        self.assertIn('no longer holds', self.brains('check', expect=1)['warnings'][0])

    def test_reconcile_sets_aside_beliefs_claims_and_edges_with_their_entry(self):
        self.cast()
        undone = self.add_entry('Mara lies to Juno.')
        self.entry, kept = undone, self.entry
        held = self.believe('Juno trusts me.', 'false')
        self.claim('juno', 'The ledger burned.', 'false', 'lie')
        self.state('people.juno.trust=3')
        self.entry = kept
        self.brains('believe', 'mara', '--retire', str(held['seq']), '--entry', kept)  # rests on the undone belief
        self.claim('player', 'I will get you out.', 'true', 'promise')
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('Mara lies to Juno.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        out = self.brains('reconcile', '--apply')
        self.assertEqual([e['op'] for e in out['set_aside']], ['believe', 'claim', 'state', 'believe'])
        self.assertIn('which is set aside', out['set_aside'][-1]['why'])
        brief = self.brief()
        self.assertEqual(self.block(brief, 'WHAT THEY HAVE TOLD PEOPLE'),
                         ['- to the player, a promise: I will get you out.'])
        for gone in ('WHAT THEY BELIEVE', 'OTHER PEOPLE', 'ledger'):
            self.assertNotIn(gone, brief)
        self.assertEqual(self.brains('check')['ok'], True)

    # ---- agency and life off-screen (ISS-28) ----

    def want(self, text, weight, *extra, npc='mara', expect=0):
        return self.brains('want', npc, '--text', text, '--weight', str(weight), *extra, '--entry', self.entry,
                           expect=expect)

    def intent(self, text, horizon, *extra, npc='mara', expect=0):
        return self.brains('intent', npc, '--text', text, '--horizon', horizon, *extra, '--entry', self.entry,
                           expect=expect)

    def next_scene(self, name):
        self.gm([{'op': 'set', 'kind': 'situation', 'fields': {'scene': name}}])

    def test_answer_block_has_body_unsure_remembers_and_decides_all_accepting_nothing(self):
        self.cast()
        answer = self.block(self.brief().rstrip(), 'ANSWER')
        self.assertEqual([ln.split(':')[0] for ln in answer],
                         ['NOTICES', 'WANTS', 'HIDES', 'SAYS', 'DOES', 'TELL', 'BODY', 'UNSURE', 'REMEMBERS', 'DECIDES'])
        for line in answer[6:]:
            self.assertTrue(line.endswith('or (nothing)'), line)

    def test_at_most_three_wants_the_brief_prints_the_top_two_and_retire_frees_a_place(self):
        self.cast()
        light = self.want('A dry bed tonight.', 1)['seq']
        self.want('To clear the debt before the tide office calls it.', 5, '--conflict', 'the debt is owed to Juno')
        self.want('To keep Juno close.', 3)
        log = (self.root / 'notes/brains/events.jsonl').read_bytes()
        self.assertIn('3 standing wants already', self.want('One too many.', 2, expect=2)['error'])
        self.assertEqual((self.root / 'notes/brains/events.jsonl').read_bytes(), log)
        brief = self.brief()
        self.assertEqual(self.block(brief, 'WHAT THEY WANT'), [
            '- To clear the debt before the tide office calls it. (but: the debt is owed to Juno)',
            '- To keep Juno close.'])  # heaviest first; the third is left out and no weight is printed
        order = [brief.index(h) for h in ('WHAT THEY KNOW', 'WHAT THEY WANT', 'WHAT THEY MEAN TO DO', '\n\nNOW\n')
                 if h in brief]
        self.assertEqual(order, sorted(order))
        self.assertEqual(self.brief().encode(), brief.encode())
        self.assertEqual(self.brains('want', 'mara', '--retire', str(light), '--entry', self.entry)['active'], 2)
        self.want('To see the boat finished.', 5)  # equal weight: the newest first
        self.assertEqual(self.block(self.brief(), 'WHAT THEY WANT')[0], '- To see the boat finished.')
        self.assertIn('not a standing want', self.brains('want', 'mara', '--retire', str(light), '--entry', self.entry,
                                                         expect=2)['error'])
        self.assertIn('--weight is 1', self.want('x', 9, expect=2)['error'])
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertRegex(view, r'- seq \d+ \[weight 5, scene 0\] To clear the debt .* \(conflict: the debt is owed')

    def test_at_most_three_intents_by_horizon_and_done_or_drop_closes_one(self):
        self.cast()
        long_ = self.intent('Leave the harbour for good.', 'long')['seq']
        now = self.intent('Get the lantern off the bollard.', 'now')['seq']
        self.intent('Find out who Juno reports to.', 'day')
        self.assertIn('3 active intents already', self.intent('One too many.', 'scene', expect=2)['error'])
        self.assertEqual(self.block(self.brief(), 'WHAT THEY MEAN TO DO'), [
            '- Get the lantern off the bollard. (right now)', '- Find out who Juno reports to. (within a day or so)',
            '- Leave the harbour for good. (in the long run)'])
        self.next_scene('the weigh-house')
        out = self.brains('intent', 'mara', '--done', str(now), '--entry', self.entry)
        self.assertEqual(out['active'], 2)
        self.intent('Lie to the weigh-house clerk.', 'scene', '--drop', str(long_))  # close one and add one at once
        lines = self.block(self.brief(), 'WHAT THEY MEAN TO DO')
        self.assertEqual(lines, ['- Lie to the weigh-house clerk. (before this scene is over)',
                                 '- Find out who Juno reports to. (within a day or so)'])
        self.assertIn('not an active intent', self.brains('intent', 'mara', '--done', str(now), '--entry', self.entry,
                                                          expect=2)['error'])
        self.assertIn('not both', self.brains('intent', 'mara', '--done', '1', '--drop', '2', '--entry', self.entry,
                                              expect=2)['error'])
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertIn(f'- seq {now} [done at seq {out["seq"]}, scene 1] Get the lantern off the bollard.', view)
        self.assertRegex(view, rf'- seq {long_} \[dropped at seq \d+, scene 1\] Leave the harbour')
        events = [json.loads(ln) for ln in (self.root / 'notes/brains/events.jsonl').read_text().splitlines()]
        self.assertEqual({e['data']['scene'] for e in events if e['op'] == 'intent'}, {0, 1})  # for drift review

    def test_veto_records_the_kind_reason_and_scene_and_can_close_an_intent(self):
        self.cast()
        held = self.intent('Walk out before Juno speaks.', 'now')['seq']
        self.next_scene('the pier')
        out = self.brains('veto', 'mara', '--kind', 'leave', '--reason', 'the tide office has the door barred',
                          '--decides', 'I walk out', '--intent', str(held), '--entry', self.entry)
        self.assertEqual(out['vetoes'], 1)
        self.brains('veto', 'mara', '--kind', 'refuse', '--reason', 'the player already paid her', '--entry', self.entry)
        self.assertNotIn('WHAT THEY MEAN TO DO', self.brief())
        self.assertNotIn('barred', self.brief())  # a veto is the writer's record, not the character's
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertIn(f'- seq {out["seq"]} [leave, scene 1] the tide office has the door barred (decided: I walk out)',
                      view)
        self.assertIn(f'- seq {held} [vetoed at seq {out["seq"]}, scene 1] Walk out before Juno speaks.', view)
        ev = json.loads((self.root / 'notes/brains/events.jsonl').read_text().splitlines()[-1])
        self.assertEqual((ev['op'], ev['data']['kind'], ev['data']['scene']), ('veto', 'refuse', 1))
        self.assertIn('needs --entry', self.brains('veto', 'mara', '--kind', 'leave', '--reason', 'x', expect=2)['error'])
        self.assertIn('--reason is required', self.brains('veto', 'mara', '--kind', 'leave', '--reason', ' ',
                                                          '--entry', self.entry, expect=2)['error'])
        self.assertIn('not an active intent', self.brains('veto', 'mara', '--kind', 'later', '--reason', 'x',
                                                          '--intent', str(held), '--entry', self.entry,
                                                          expect=2)['error'])

    def test_routine_is_a_state_field_only_the_offscreen_brief_prints(self):
        self.cast()
        self.state('routine.mornings=opens the chandlery', 'routine.nights=drinks alone at the Gull')
        self.assertIn('at most 6 routine slots', self.state(*[f'routine.r{n}=x' for n in range(7)], expect=2)['error'])
        self.assertNotIn('chandlery', self.brief())
        self.brains('settings', '--offscreen', 'on')
        brief = self.brains('brief', 'mara', '--offscreen', '--text')
        self.assertEqual(self.block(brief, 'THEIR DAYS'),
                         ['- mornings: opens the chandlery', '- nights: drinks alone at the Gull'])
        self.state('routine.nights=')
        self.assertEqual(self.block(self.brains('brief', 'mara', '--offscreen', '--text'), 'THEIR DAYS'),
                         ['- mornings: opens the chandlery'])
        view = (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8')
        self.assertIn('- routine.mornings: opens the chandlery', view)

    def test_offscreen_call_is_off_by_default_and_one_per_boundary(self):
        self.cast()
        self.claim('player', 'You will have the boat by Sunday.', 'false', 'promise')
        self.claim('juno', 'The ledger burned.', 'false', 'lie')
        self.want('To clear the debt.', 4)
        self.intent('Visit the tide office at dawn.', 'day')
        self.assertIn('off-screen calls are off', self.brains('brief', 'mara', '--offscreen', '--text',
                                                              expect=2)['error'])
        self.assertIn('off-screen calls are off', self.brains('offscreen', 'mara', '--does', 'x', '--entry',
                                                              self.entry, expect=2)['error'])
        self.assertIn('give --scene', self.brains('brief', 'mara', '--text', expect=2)['error'])
        self.assertEqual(self.brains('settings', '--offscreen', 'on')['settings'], {'offscreen': True})
        brief = self.brains('brief', 'mara', '--offscreen', '--text')
        self.assertEqual(brief.encode(), self.brains('brief', 'mara', '--offscreen', '--text').encode())
        self.assertIn('You are the mind of Mara Venn, 34, between scenes, away from the player.', brief)
        self.assertNotIn('the harbour', brief)  # the player's scene is not where Mara is
        self.assertEqual(self.block(brief, 'NOW'), [
            'day 2, dusk', 'The story is elsewhere. Nobody is watching you; what you do now happens off the page.'])
        self.assertEqual(self.block(brief.rstrip(), 'ANSWER'), [
            'DOES: what they do with the time, in one or two plain lines',
            'LEAVES: the sign of it someone could find later (a note, a smell, a missing thing, a rumour), or (nothing)',
            'DECIDES: a lasting intention they form (to leave, to refuse, to do something later), or (nothing)',
            'CHANGES: how they are different after it (mood, body, what they want), or (nothing)'])
        self.assertIn('- Visit the tide office at dawn.', '\n'.join(self.block(brief, 'WHAT THEY MEAN TO DO')))
        self.assertEqual(self.block(brief, 'WHAT THEY HAVE TOLD PEOPLE')[0],
                         '- to Juno Ash, a lie: The ledger burned.')  # nobody present off-screen: newest first
        self.scene.write_text('Two days pass in the rain.\n', encoding='utf-8')
        with_scene = self.brains('brief', 'mara', '--offscreen', '--scene', str(self.scene), '--text')
        self.assertTrue(self.block(with_scene, 'NOW')[-1] == 'Two days pass in the rain.')
        out = self.brains('offscreen', 'mara', '--does', 'I sold the spare sail to a stranger.', '--entry', self.entry)
        self.assertEqual(out['scene'], 0)
        self.assertIn('- I sold the spare sail to a stranger.', self.block(self.brief(), 'WHAT THEY REMEMBER'))
        for args in (('brief', 'juno', '--offscreen', '--text'),
                     ('offscreen', 'juno', '--does', 'x', '--entry', self.entry)):
            self.assertIn('mara already had the off-screen call', self.brains(*args, expect=2)['error'])
        self.next_scene('the pier')
        self.brains('offscreen', 'juno', '--does', 'I followed Mara to the pier.', '--entry', self.entry)
        self.assertIn('- scenes 0', (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8'))
        self.brains('settings', '--offscreen', 'off')
        self.assertIn('off-screen calls are off', self.brains('brief', 'mara', '--offscreen', '--text',
                                                              expect=2)['error'])
        self.assertEqual(self.brains('check')['ok'], True)

    def test_reconcile_follows_wants_intents_vetoes_and_offscreen_calls(self):
        self.cast()
        self.brains('settings', '--offscreen', 'on')
        kept_want = self.want('To clear the debt.', 4)['seq']
        undone = self.add_entry('Mara turns on Juno.')
        self.entry, kept = undone, self.entry
        gone_want = self.want('To ruin Juno.', 5)['seq']
        gone_intent = self.intent('Burn the ledger tonight.', 'day')['seq']
        self.brains('offscreen', 'mara', '--does', 'I bought lamp oil.', '--entry', undone)
        self.entry = kept
        self.brains('want', 'mara', '--retire', str(gone_want), '--entry', kept)    # rests on the undone want
        self.brains('veto', 'mara', '--kind', 'later', '--reason', 'the ledger is needed', '--intent', str(gone_intent),
                    '--entry', kept)                                                # closes the undone intent
        self.intent('Ask the clerk about the manifest.', 'scene')
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(files.entry('Mara turns on Juno.', id=undone), ''),
                         encoding='utf-8', newline='\n')
        self.assertIn('Undo?', self.brief(expect=2)['error'])
        out = self.brains('reconcile', '--apply')
        self.assertEqual([e['op'] for e in out['set_aside']], ['want', 'intent', 'offscreen', 'want', 'veto'])
        brief = self.brief()
        self.assertEqual(self.block(brief, 'WHAT THEY WANT'), ['- To clear the debt.'])
        self.assertEqual(self.block(brief, 'WHAT THEY MEAN TO DO'),
                         ['- Ask the clerk about the manifest. (before this scene is over)'])
        self.assertNotIn('lamp oil', brief)
        self.brains('brief', 'juno', '--offscreen', '--text')  # the set-aside call no longer holds the boundary
        self.assertIn(f'seq {kept_want}', (self.root / 'notes/brains/mara.md').read_text(encoding='utf-8'))
        self.assertEqual(self.brains('settings')['settings'], {'offscreen': True})  # setup, never set aside
        self.assertEqual(self.brains('check')['ok'], True)

    def test_reconcile_sets_aside_a_want_that_would_pass_the_cap(self):
        self.cast()
        first = [self.want(f'Want {n}.', 2)['seq'] for n in range(3)][0]
        undone = self.add_entry('Mara gives up on the boat.')
        self.brains('want', 'mara', '--retire', str(first), '--entry', undone)
        self.want('A fourth want, once the first was gone.', 4)
        story = self.root / 'public/story.md'
        story.write_text(story.read_text(encoding='utf-8').replace(
            files.entry('Mara gives up on the boat.', id=undone), ''), encoding='utf-8', newline='\n')
        out = self.brains('reconcile', '--apply')
        self.assertEqual([e['op'] for e in out['set_aside']], ['want', 'want'])
        self.assertIn('more than 3 standing wants', out['set_aside'][1]['why'])
        self.assertEqual(self.brains('check')['ok'], True)

    # ---- drift review (ISS-29) ----

    def scenes(self, n):
        """Move game-master's scene count on by n, one situation op per scene."""
        start = json.loads(run(self.root, 'brains.py', 'review').stdout)['scene']
        self.gm([{'op': 'set', 'kind': 'situation', 'fields': {'scene': f'scene {start + k + 1}'}} for k in range(n)])

    def review(self, *extra, expect=1):
        return self.brains('review', *extra, expect=expect)

    def test_review_reports_card_fields_changed_since_the_snapshot(self):
        self.cast()
        self.assertEqual(self.review(expect=0)['warnings'], [])
        self.gm([{'op': 'set', 'kind': 'npc', 'id': 'mara', 'fields': {'attitude': 'owes the player now'}}])
        out = self.review()
        self.assertEqual(out['characters']['mara']['card_changed'],
                         [{'field': 'attitude', 'snapshot': 'wary of the player', 'now': 'owes the player now'}])
        self.assertEqual(out['characters']['juno']['card_changed'], [])
        self.assertIn('brains.py add mara', out['warnings'][0])
        self.brains('add', 'mara')  # a new snapshot settles it
        self.assertEqual(self.review(expect=0)['characters']['mara']['card_changed'], [])

    def test_review_sets_wants_intents_and_episodes_beside_the_card_with_both_texts(self):
        self.cast()
        self.want('An old want, from before the snapshot.', 2)
        self.brains('add', 'mara')  # the snapshot: what came before it was already weighed
        self.want('To leave the harbour and never pay.', 5)
        self.want('To keep Juno close.', 2)
        self.intent('Sell the boat to the tide office.', 'long')
        self.intent('Get the lantern off the bollard.', 'now')  # a momentary intent is not set beside the card
        self.brains('remember', 'mara', '--text', 'The player stood up for me at the weigh-house.', '--salience', '4',
                    '--entry', self.entry)
        self.brains('remember', 'mara', '--text', 'Rain on the pier.', '--entry', self.entry)  # salience 3: left out
        r = self.review()
        beside = r['characters']['mara']['beside_card']
        self.assertEqual([(c['field'], c['kind'], c['text']) for c in beside], [
            ('want', 'want', 'To leave the harbour and never pay.'), ('want', 'want', 'To keep Juno close.'),
            ('want', 'intent', 'Sell the boat to the tide office.'),
            ('attitude', 'episode', 'The player stood up for me at the weigh-house.')])
        self.assertEqual({c['card'] for c in beside}, {'to clear her debt', 'wary of the player'})
        line = next(w for w in r['warnings'] if 'never pay' in w)
        self.assertIn("card says 'to clear her debt'", line)
        self.assertIn('Judge whether it contradicts', line)  # a candidate, never a verdict
        self.assertEqual(r['characters']['juno']['beside_card'], [])  # nothing recorded for Juno

    def test_review_flags_more_than_two_vetoes_in_ten_scenes(self):
        self.cast()
        for reason in ('the door is barred', 'the player already paid'):
            self.brains('veto', 'mara', '--kind', 'leave', '--reason', reason, '--entry', self.entry)
        self.assertFalse(self.review(expect=0)['characters']['mara']['puppet'])
        self.scenes(9)
        self.brains('veto', 'mara', '--kind', 'refuse', '--reason', 'it would break canon', '--entry', self.entry)
        r = self.review()['characters']['mara']
        self.assertTrue(r['puppet'])
        self.assertEqual([v['scene'] for v in r['vetoes_in_window']], [0, 0, 9])
        self.scenes(1)  # the first two fall out of the window
        r = self.review(expect=0)['characters']['mara']
        self.assertEqual(([v['scene'] for v in r['vetoes_in_window']], r['puppet']), ([9], False))

    def test_review_finds_intents_gone_stale_for_their_horizon(self):
        self.cast()
        for text_, horizon in (('Now.', 'now'), ('This scene.', 'scene'), ('Today.', 'day')):
            self.intent(text_, horizon)
        self.brains('add', 'mara')  # staleness does not wait on the snapshot
        self.assertEqual(self.review(expect=0)['characters']['mara']['stale_intents'], [])

        def stale():
            return [i['horizon'] for i in self.review()['characters']['mara']['stale_intents']]
        self.scenes(1)
        self.assertEqual(stale(), ['now', 'scene'])
        self.scenes(2)
        self.assertEqual(stale(), ['now', 'scene', 'day'])
        day = [e for e in self.events() if e['op'] == 'intent'][-1]['seq']
        self.brains('intent', 'mara', '--drop', str(day), '--text', 'For good.', '--horizon', 'long',
                    '--entry', self.entry)  # recorded at scene 3
        self.scenes(9)
        self.assertEqual(stale(), ['now', 'scene'])
        self.scenes(1)
        self.assertEqual(stale(), ['now', 'scene', 'long'])
        self.assertIn('has stood 10 scene(s)', self.review()['warnings'][-1])

    def test_review_flags_a_persistent_tier_with_no_session(self):
        self.cast()
        self.brains('session', 'mara', '--id', 'sess-1', '--tier', 'persistent')
        self.assertFalse(self.review(expect=0)['characters']['mara']['persistent_without_session'])
        self.brains('session', 'mara', '--end')  # the tier stays persistent
        r = self.review('--npc', 'mara')
        self.assertEqual(list(r['characters']), ['mara'])
        self.assertTrue(r['characters']['mara']['persistent_without_session'])
        self.assertIn('session mara --id', r['warnings'][0])
        self.assertIn('no brain yet', self.review('--npc', 'nobody', expect=2)['error'])

    def test_propose_writes_a_proposal_for_the_writer_and_never_touches_game_master(self):
        self.cast()
        self.want('To leave the harbour and never pay.', 5)
        self.want('To keep Juno close.', 2)
        self.brains('remember', 'mara', '--text', 'The player stood up for me.', '--salience', '5', '--entry', self.entry)
        gm_dir = self.root / 'notes/gm'
        before = {p.name: p.read_bytes() for p in gm_dir.iterdir()}
        self.assertNotIn('pending.json', before)
        out = self.review('--propose')
        self.assertEqual((out['proposal'], out['proposed_ops']), ('notes/brains/card-proposal.json', 1))
        self.assertEqual({p.name: p.read_bytes() for p in gm_dir.iterdir()}, before)  # no pending, no commit
        proposal = json.loads((self.root / 'notes/brains/card-proposal.json').read_text(encoding='utf-8'))
        self.assertEqual(proposal['ops'], [{'op': 'set', 'kind': 'npc', 'id': 'mara',
                                            'fields': {'want': 'To leave the harbour and never pay.'}}])
        self.assertEqual((proposal['entry'], proposal['why']), (None, None))
        self.assertEqual([c['kind'] for c in proposal['evidence']['mara']], ['want', 'want', 'episode'])
        self.assertNotIn('juno', proposal['evidence'])
        self.gm(proposal['ops'])  # the writer merges it into a delta: it is valid as it stands
        self.assertEqual(self.review()['characters']['mara']['card_changed'][0]['field'], 'want')
        self.brains('add', 'mara')
        out = self.review('--propose', expect=0)
        self.assertEqual(out['proposed_ops'], 0)  # rewritten, so the old proposal does not linger
        self.assertEqual(json.loads((self.root / 'notes/brains/card-proposal.json').read_text())['ops'], [])

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
        for key in ('BODY', 'UNSURE', 'REMEMBERS', 'LEAVES', 'CHANGES'):
            self.assertIn(f'{key}: ', protocol, key)
        self.assertIn('Never narrate the off-screen scene.', protocol)
        self.assertIn('Off-screen calls?', (plus / 'APPLY.md').read_text(encoding='utf-8'))
        self.assertIn('**`limits` is authoritative.**', protocol)
        self.assertIn('cut that output', protocol)
        for command in ('init', 'add', 'world', 'know', 'unlearn', 'remember', 'compress', 'session', 'brief',
                        'view', 'check', 'migrate', 'reconcile', 'state', 'tick', 'believe', 'claim', 'want',
                        'intent', 'veto', 'offscreen', 'settings', 'review'):
            self.assertIn(f'brains.py {command}', protocol + (plus / 'APPLY.md').read_text(encoding='utf-8'), command)


if __name__ == '__main__':
    unittest.main()
