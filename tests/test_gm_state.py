"""Tests for the game-master package's state script (a director package, applied only on request)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from uuid import uuid4

from helpers import files
from tests.support import REPO, workspace

SCRIPT = REPO / '.agents/skills/couldhappen/packages/game-master/files/gm_state.py'


def run(root, *args):
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    return subprocess.run([sys.executable, '-I', str(SCRIPT), '--root', str(root), *args],
                          capture_output=True, text=True, encoding='utf-8', env=env)


class GmStateTest(unittest.TestCase):
    def setUp(self):
        self.temp, self.root = workspace()
        self.addCleanup(self.temp.cleanup)
        self.assertEqual(run(self.root, 'init').returncode, 0)

    def add_entry(self, body='The rain fell on the harbour.', channel='story.md', role='writer'):
        eid = str(uuid4())
        path = self.root / 'public' / channel
        text = path.read_text(encoding='utf-8') + '\n' + files.entry(body, role=role, id=eid)
        path.write_text(text, encoding='utf-8', newline='\n')
        return eid

    def delta(self, entry, ops, why='the player opened the ledger'):
        return {'entry': entry, 'why': why, 'ops': ops}

    def commit(self, delta, expect=0):
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(delta), encoding='utf-8')
        check = run(self.root, 'check')
        result = run(self.root, 'commit')
        self.assertEqual(result.returncode, expect, check.stdout + result.stdout + result.stderr)
        return result

    def state(self):
        return json.loads(run(self.root, 'state').stdout)

    def fact(self, fid='F1', **extra):
        return {'op': 'add', 'kind': 'fact', 'id': fid, 'text': 'Mara owes the harbourmaster a debt.',
                'status': 'established', 'source': 'story', 'tags': ['Mara'], **extra}

    def test_commit_and_hot_context(self):
        e = self.add_entry()
        self.commit(self.delta(e, [
            {'op': 'set', 'kind': 'contract', 'fields': {'genre': 'noir', 'tone': 'wry', 'banned_terms': ['gore']}},
            {'op': 'set', 'kind': 'situation', 'fields': {'day': 1, 'location': 'Harbour', 'present': ['Mara'],
                                                           'problem': 'find the ledger', 'scene': 's1'}},
            self.fact(), self.fact('F2', text='Unrelated lighthouse lore.', tags=['lighthouse'])]))
        out = run(self.root, 'hot').stdout
        self.assertIn('F1 [established] Mara owes', out)
        self.assertNotIn('F2', out.split('FACTS')[1].split('(')[0])
        self.assertIn('1 other live facts not shown', out)
        self.assertIn('F2', run(self.root, 'hot', '--about', 'lighthouse').stdout)

    def test_entry_must_exist_and_state_is_untouched_on_failure(self):
        self.commit(self.delta(str(uuid4()), [self.fact()]), expect=1)
        self.assertEqual(self.state()['facts'], {})

    def test_established_text_needs_replace_with_reason(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.fact()]))
        e2 = self.add_entry('A new truth.')
        self.commit(self.delta(e2, [{'op': 'update', 'kind': 'fact', 'id': 'F1', 'text': 'Mara owes nothing.'}]), expect=1)
        self.commit(self.delta(e2, [{'op': 'replace', 'kind': 'fact', 'id': 'F1', 'new': 'F3',
                                     'text': 'Mara repaid the debt.', 'reason': 'she paid it in scene s2'}]))
        facts = self.state()['facts']
        self.assertEqual(facts['F1']['status'], 'outdated')
        self.assertEqual(facts['F3']['replaces'], 'F1')
        self.assertTrue(facts['F3']['tags'] == ['Mara'])

    def test_rumour_is_not_silently_promoted(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.fact(status='rumour')]))
        promote = {'op': 'update', 'kind': 'fact', 'id': 'F1', 'status': 'established'}
        self.commit(self.delta(e, [promote]), expect=1)
        self.commit(self.delta(e, [{**promote, 'reason': 'Mara confirmed it herself'}]))
        self.assertEqual(self.state()['facts']['F1']['status'], 'established')

    def test_status_must_be_explicit_and_keys_known(self):
        e = self.add_entry()
        no_status = self.fact()
        del no_status['status']
        self.commit(self.delta(e, [no_status]), expect=1)
        self.commit(self.delta(e, [self.fact(mood='grim')]), expect=1)
        self.commit({'entry': e, 'ops': [self.fact()]}, expect=1)

    def test_time_does_not_run_backwards_without_flashback(self):
        e = self.add_entry()
        self.commit(self.delta(e, [{'op': 'set', 'kind': 'situation', 'fields': {'day': 5}}]))
        e2 = self.add_entry('Later.')
        self.commit(self.delta(e2, [{'op': 'set', 'kind': 'situation', 'fields': {'day': 3}}]), expect=1)
        self.commit(self.delta(e2, [{'op': 'set', 'kind': 'situation', 'fields': {'day': 3}, 'flashback': True}]))
        self.assertEqual(self.state()['max_day'], 5)

    def test_hidden_facts_cannot_be_hidden_again_once_known_and_banned_terms_are_blocked(self):
        e = self.add_entry()
        self.commit(self.delta(e, [{'op': 'set', 'kind': 'contract', 'fields': {'banned_terms': ['gore']}}]))
        self.commit(self.delta(e, [self.fact(text='A scene of gore.')]), expect=1)
        self.commit(self.delta(e, [self.fact()]))
        self.commit(self.delta(e, [{'op': 'update', 'kind': 'fact', 'id': 'F1', 'known': False}]), expect=1)
        draft = self.root / 'draft.md'
        draft.write_text('There was gore everywhere.', encoding='utf-8')
        self.assertEqual(run(self.root, 'check', '--prose', str(draft)).returncode, 1)

    def test_reconcile_sets_aside_withdrawn_entries_and_dependents(self):
        e1, e2 = self.add_entry('One.'), self.add_entry('Two.')
        self.commit(self.delta(e1, [self.fact()]))
        self.commit(self.delta(e2, [{'op': 'replace', 'kind': 'fact', 'id': 'F1', 'new': 'F2',
                                     'text': 'Changed.', 'reason': 'it changed in two'}]))
        self.assertEqual(run(self.root, 'reconcile').returncode, 0)
        story = self.root / 'public/story.md'
        text = story.read_text(encoding='utf-8')
        story.write_text(text.replace(files.entry('One.', id=e1), ''), encoding='utf-8', newline='\n')
        self.assertEqual(run(self.root, 'reconcile').returncode, 1)
        self.assertIn('no longer in the logs', run(self.root, 'state').stderr)
        done = run(self.root, 'reconcile', '--apply')
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(self.state()['facts'], {})
        withdrawn = (self.root / 'notes/gm/withdrawn.jsonl').read_text(encoding='utf-8').strip().split('\n')
        self.assertEqual(len(withdrawn), 2)


if __name__ == '__main__':
    unittest.main()
