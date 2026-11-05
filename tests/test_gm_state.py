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

    # ---- phase 2: threads and lifecycle ----------------------------------------------------

    def thread(self, tid='T1', **extra):
        return {'op': 'add', 'kind': 'thread', 'id': tid, 'type': 'promise', 'tags': ['Mara'],
                'text': 'The player promised Mara to return the ledger.', **extra}

    def scene(self, n, day=None):
        fields = {'scene': f's{n}', **({'day': day} if day is not None else {})}
        self.commit(self.delta(self.add_entry(f'Scene {n}.'), [{'op': 'set', 'kind': 'situation', 'fields': fields}]))

    def test_promise_needs_an_outcome_and_a_later_entry(self):
        e1 = self.add_entry('The promise.')
        e2 = self.add_entry('The delivery.')
        self.commit(self.delta(e1, [self.thread()]))
        resolve = {'op': 'resolve', 'kind': 'thread', 'id': 'T1', 'resolution': 'She got the ledger back.'}
        self.commit(self.delta(e1, [{**resolve, 'outcome': 'fulfilled'}], why='same entry'), expect=1)
        self.commit(self.delta(e2, [resolve], why='no outcome given'), expect=1)
        self.commit(self.delta(e1, [{**resolve, 'outcome': 'fulfilled'}], why='an earlier entry again'), expect=1)
        e0 = self.add_entry('Later still.')
        self.commit(self.delta(e0, [{**resolve, 'outcome': 'fulfilled'}]))
        thread = self.state()['threads']['T1']
        self.assertEqual((thread['status'], thread['outcome'], thread['resolved_entry']), ('resolved', 'fulfilled', e0))
        self.assertNotIn('T1', run(self.root, 'hot', '--about', 'Mara').stdout)
        self.assertNotIn('T1', json.loads(run(self.root, 'state', '--live').stdout)['threads'])

    def test_resolution_must_come_after_the_promise_in_the_log(self):
        early, late = self.add_entry('Early.'), self.add_entry('Late.')
        self.commit(self.delta(late, [self.thread()]))
        resolve = {'op': 'resolve', 'kind': 'thread', 'id': 'T1', 'outcome': 'broken', 'resolution': 'She lied.'}
        self.commit(self.delta(early, [resolve]), expect=1)

    def test_overdue_promise_is_flagged_in_the_hot_context(self):
        e = self.add_entry()
        self.commit(self.delta(e, [{'op': 'set', 'kind': 'situation', 'fields': {'day': 5, 'location': 'Dock'}},
                                   self.thread(due_day=6)]))
        self.assertNotIn('OVERDUE', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('Time passes.'),
                               [{'op': 'set', 'kind': 'situation', 'fields': {'day': 8}}]))
        out = run(self.root, 'hot').stdout
        self.assertIn('OVERDUE', out)
        self.assertIn('was due day 6, it is day 8', out)
        self.commit(self.delta(self.add_entry(), [self.thread('T2', due_day=3)]), expect=1)

    def test_untouched_threads_are_flagged_until_touched(self):
        self.commit(self.delta(self.add_entry(), [self.thread(type='mystery', tags=['Mara'])]))
        for n in range(1, 6):
            self.scene(n)
        self.assertIn('untouched for 5 scenes', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('Progress.'), [{'op': 'update', 'kind': 'thread', 'id': 'T1', 'touch': True}]))
        self.assertNotIn('untouched', run(self.root, 'hot').stdout)

    def test_thread_lifecycle_is_enforced(self):
        self.commit(self.delta(self.add_entry(), [self.thread(type='callback')]))
        e = self.add_entry('Next.')
        finish = {'op': 'update', 'kind': 'thread', 'id': 'T1', 'status': 'resolved', 'reason': 'it ended in scene 3'}
        self.commit(self.delta(e, [finish]), expect=1)
        dormant = {'op': 'update', 'kind': 'thread', 'id': 'T1', 'status': 'dormant'}
        self.commit(self.delta(e, [dormant], why='no reason given'), expect=1)
        self.commit(self.delta(e, [{**dormant, 'reason': 'the player left town'}]))
        self.assertNotIn('T1', run(self.root, 'hot').stdout)  # dormant threads leave the hot context
        e2 = self.add_entry('Later.')
        self.commit(self.delta(e2, [{'op': 'update', 'kind': 'thread', 'id': 'T1', 'status': 'discarded',
                                     'reason': 'the idea no longer fits'}]))
        self.commit(self.delta(self.add_entry(), [{'op': 'update', 'kind': 'thread', 'id': 'T1', 'touch': True}]), expect=1)

    def test_provisional_fact_can_be_discarded_and_leaves_the_hot_context(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.fact(status='provisional')]))
        self.assertIn('F1', run(self.root, 'hot', '--about', 'Mara').stdout)
        self.commit(self.delta(self.add_entry('Dropped.'), [{'op': 'update', 'kind': 'fact', 'id': 'F1',
                                                           'status': 'discarded', 'reason': 'never shown, no longer wanted'}]))
        self.assertNotIn('F1', run(self.root, 'hot', '--about', 'Mara').stdout)
        self.assertNotIn('F1', json.loads(run(self.root, 'state', '--live').stdout)['facts'])

    def test_review_lists_what_to_retire_and_changes_nothing(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.fact(status='provisional'), self.fact('F2', status='rumour'),
                                   self.thread(type='mystery')]))
        before = (self.root / 'notes/gm/deltas.jsonl').read_text(encoding='utf-8')
        out = run(self.root, 'review').stdout
        for expected in ('T1 [mystery, open]', 'F1 [provisional]', 'F2 [rumour]', 'REOPEN'):
            self.assertIn(expected, out)
        self.assertEqual((self.root / 'notes/gm/deltas.jsonl').read_text(encoding='utf-8'), before)

    # ---- phase 3: living pressures and cast -------------------------------------------------

    def pressure(self, pid='P1', **extra):
        return {'op': 'add', 'kind': 'pressure', 'id': pid, 'actor': 'Harbour guild', 'goal': 'seize the ledger',
                'next_action': 'send a bailiff to Mara', 'trigger': 'the player is seen with the ledger',
                'consequence': 'Mara is arrested', 'clock_max': 4, 'tags': ['guild'], **extra}

    def advance(self, pid='P1', **extra):
        return {'op': 'advance', 'kind': 'pressure', 'id': pid, 'basis': 'event',
                'reason': 'the player was seen at the pier', **extra}

    def test_pressure_moves_only_with_a_basis_a_reason_and_room_on_the_clock(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        for i, bad in enumerate([{'basis': 'whim'}, {'reason': ''}, {'steps': 5}, {'steps': 'two'}]):
            self.commit(self.delta(self.add_entry(f'try {i}'), [self.advance(**bad)]), expect=1)
        self.commit(self.delta(self.add_entry('ok'), [self.advance(steps=3)]))
        self.assertEqual(self.state()['pressures']['P1']['clock'], 3)
        self.commit(self.delta(self.add_entry('over'), [self.advance(steps=2)]), expect=1)

    def test_offstage_moves_need_evidence_the_protagonist_can_find(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        offscreen = self.advance(basis='offscreen', reason='three days passed in the countryside')
        self.commit(self.delta(self.add_entry('a'), [offscreen]), expect=1)
        self.commit(self.delta(self.add_entry('b'), [{**offscreen, 'evidence': 'guild posters on every door'}]))
        self.assertEqual(self.state()['pressures']['P1']['evidence'], 'guild posters on every door')

    def test_full_clock_warns_and_advancing_everything_at_once_is_flagged(self):
        self.commit(self.delta(self.add_entry(), [self.pressure('P1'), self.pressure('P2'), self.pressure('P3')]))
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(self.add_entry('all'), [
            self.advance('P1', steps=4), self.advance('P2'), self.advance('P3')])), encoding='utf-8')
        out = run(self.root, 'check').stdout
        self.assertIn('3 pressures advance in one delta', out)
        self.assertIn('P1 clock is full', out)
        self.assertEqual(run(self.root, 'commit').returncode, 0)
        self.assertIn('P1 (Harbour guild) clock is full', run(self.root, 'hot').stdout)

    def test_a_world_that_waits_is_flagged_and_a_move_clears_it(self):
        clockless = {k: v for k, v in self.pressure().items() if k != 'clock_max'}
        self.commit(self.delta(self.add_entry(), [clockless]))
        for n in range(1, 6):
            self.scene(n)
        self.assertIn('no pressure has moved in 5 scenes', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('steps'), [self.advance(steps=1)]), expect=1)  # no clock to step
        self.commit(self.delta(self.add_entry('move'), [self.advance()]))
        self.assertNotIn('no pressure has moved', run(self.root, 'hot').stdout)

    def test_pressure_lifecycle_and_resolution(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        sleep = {'op': 'update', 'kind': 'pressure', 'id': 'P1', 'status': 'dormant'}
        self.commit(self.delta(self.add_entry('a'), [sleep]), expect=1)
        self.commit(self.delta(self.add_entry('b'), [{**sleep, 'reason': 'the guild lost interest'}]))
        self.commit(self.delta(self.add_entry('c'), [self.advance()]), expect=1)  # dormant cannot advance
        self.commit(self.delta(self.add_entry('d'), [{'op': 'update', 'kind': 'pressure', 'id': 'P1',
                                                      'status': 'active', 'reason': 'a new bailiff arrived'}]))
        resolve = {'op': 'resolve', 'kind': 'pressure', 'id': 'P1', 'outcome': 'thwarted', 'resolution': 'The ledger burned.'}
        self.commit(self.delta(self.add_entry('e'), [{**resolve, 'outcome': 'won'}]), expect=1)
        self.commit(self.delta(self.add_entry('f'), [resolve]))
        self.commit(self.delta(self.add_entry('g'), [self.advance()]), expect=1)
        self.assertNotIn('P1', json.loads(run(self.root, 'state', '--live').stdout)['pressures'])

    def test_cast_cards_appear_only_for_present_characters_and_need_a_name(self):
        self.commit(self.delta(self.add_entry(), [{'op': 'set', 'kind': 'npc', 'id': 'N1', 'fields': {'want': 'safety'}}]), expect=1)
        self.commit(self.delta(self.add_entry('a'), [
            {'op': 'set', 'kind': 'npc', 'id': 'N1', 'fields': {'name': 'Mara', 'want': 'safety', 'secret': 'she forged the ledger',
                                                                'voice': 'clipped', 'attitude': 'wary'}},
            {'op': 'set', 'kind': 'npc', 'id': 'N2', 'fields': {'name': 'Orsk', 'want': 'coin'}},
            {'op': 'set', 'kind': 'situation', 'fields': {'present': ['Mara']}}]))
        out = run(self.root, 'hot').stdout
        self.assertIn('Mara (N1): want safety | secret she forged the ledger | voice clipped | attitude wary', out)
        self.assertNotIn('Orsk', out)
        self.commit(self.delta(self.add_entry('b'), [{'op': 'set', 'kind': 'npc', 'id': 'N1', 'fields': {'attitude': 'grateful'}}]))
        self.assertIn('attitude grateful', run(self.root, 'hot').stdout)

    def test_review_lists_pressures_to_consider_after_a_time_skip(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        out = run(self.root, 'review').stdout
        self.assertIn('P1 Harbour guild clock 0/4: next "send a bailiff to Mara"', out)


if __name__ == '__main__':
    unittest.main()
