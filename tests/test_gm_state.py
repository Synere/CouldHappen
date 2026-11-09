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

    # ---- phase 4: discovery ------------------------------------------------------------------

    def secret(self, **extra):
        return self.fact('F9', text='The harbourmaster forged the ledger.', known=False, tags=['harbourmaster'], **extra)

    def rev(self, rid='V1', **extra):
        return {'op': 'add', 'kind': 'revelation', 'id': rid, 'fact': 'F9', 'importance': 'required',
                'tags': ['harbourmaster'], **extra}

    def route(self, route, how, rid='V1', **extra):
        return {'op': 'route', 'kind': 'revelation', 'id': rid, 'route': route, 'how': how, **extra}

    def three_routes(self):
        return [self.route('a', 'Mara confesses if pressed'), self.route('b', 'the back pages of the ledger'),
                self.route('c', 'the clerk remembers the ink', where='Harbour office')]

    def test_only_a_hidden_live_fact_can_become_a_revelation(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.fact('F1')]))  # known to the player
        self.commit(self.delta(self.add_entry('a'), [self.rev(fact='F1')]), expect=1)
        self.commit(self.delta(self.add_entry('b'), [self.rev(fact='F404')]), expect=1)
        self.commit(self.delta(self.add_entry('c'), [self.secret(), self.rev(importance='critical')]), expect=1)
        self.commit(self.delta(self.add_entry('d'), [self.secret(), self.rev()]))
        self.commit(self.delta(self.add_entry('e'), [self.rev('V2')]), expect=1)  # already has a live revelation

    def test_required_truth_warns_until_it_has_three_open_routes(self):
        e = self.add_entry()
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            self.secret(), self.rev(), self.route('a', 'Mara confesses')])), encoding='utf-8')
        self.assertIn('V1 is required with 1 open route(s); aim for 3', run(self.root, 'check').stdout)
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            self.secret(), self.rev(), *self.three_routes()])), encoding='utf-8')
        out = run(self.root, 'check').stdout
        self.assertNotIn('aim for', out)
        self.assertEqual(run(self.root, 'commit').returncode, 0)
        hot = run(self.root, 'hot', '--about', 'harbourmaster').stdout
        self.assertIn('V1 [required, hidden, truth F9] routes: a) Mara confesses if pressed; b) the back', hot)
        self.assertIn('[at Harbour office]', hot)
        self.assertIn('F9 [established, HIDDEN from player]', hot)

    def test_blocking_every_route_is_called_a_dead_end(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.secret(), self.rev(), self.route('a', 'Mara confesses')]))
        block = {'op': 'block', 'kind': 'revelation', 'id': 'V1', 'route': 'a'}
        self.commit(self.delta(self.add_entry('a'), [block]), expect=1)  # needs a reason
        self.commit(self.delta(self.add_entry('b'), [{**block, 'reason': 'Mara left the city'}]))
        self.assertIn('NO open route: a dead end', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('c'), [{**block, 'reason': 'again'}]), expect=1)  # already blocked

    def test_clue_then_reveal_flips_what_the_player_knows(self):
        e = self.add_entry()
        self.commit(self.delta(e, [self.secret(), self.rev(), *self.three_routes()]))
        clue = {'op': 'clue', 'kind': 'revelation', 'id': 'V1', 'route': 'b'}
        self.commit(self.delta(self.add_entry('a'), [clue]), expect=1)  # needs a reason
        self.commit(self.delta(self.add_entry('b'), [{**clue, 'reason': 'the player read the back pages'}]))
        self.assertEqual(self.state()['revelations']['V1']['status'], 'partial')
        self.commit(self.delta(self.add_entry('c'), [{'op': 'reveal', 'kind': 'revelation', 'id': 'V1',
                                                      'how': 'Mara confessed', 'route': 'b'}]), expect=0)
        state = self.state()
        self.assertEqual(state['revelations']['V1']['status'], 'revealed')
        self.assertTrue(state['facts']['F9']['known'])
        self.assertNotIn('V1', run(self.root, 'hot', '--about', 'harbourmaster').stdout)
        self.assertNotIn('V1', json.loads(run(self.root, 'state', '--live').stdout)['revelations'])
        self.commit(self.delta(self.add_entry('d'), [{'op': 'reveal', 'kind': 'revelation', 'id': 'V1', 'how': 'twice'}]), expect=1)

    def test_reveal_needs_a_how_and_a_live_truth(self):
        self.commit(self.delta(self.add_entry(), [self.secret(), self.rev(), *self.three_routes()]))
        reveal = {'op': 'reveal', 'kind': 'revelation', 'id': 'V1', 'how': 'Mara confessed'}
        self.commit(self.delta(self.add_entry('a'), [{**reveal, 'how': ''}]), expect=1)
        self.commit(self.delta(self.add_entry('b'), [{**reveal, 'route': 'zz'}]), expect=1)
        self.commit(self.delta(self.add_entry('c'), [{'op': 'replace', 'kind': 'fact', 'id': 'F9', 'new': 'F10',
                                                      'text': 'It was the clerk.', 'reason': 'twist in scene 8'}]))
        self.commit(self.delta(self.add_entry('d'), [reveal]), expect=1)  # F9 is outdated: relink first
        self.assertIn('outdated or discarded: relink', run(self.root, 'hot').stdout)

    def test_relink_discard_and_review(self):
        self.commit(self.delta(self.add_entry(), [self.secret(), self.rev(), *self.three_routes()]))
        self.assertIn('V1 [required, hidden, truth F9] routes open 3, used 0, blocked 0', run(self.root, 'review').stdout)
        self.commit(self.delta(self.add_entry('a'), [{'op': 'update', 'kind': 'revelation', 'id': 'V1',
                                                      'importance': 'optional'}]))
        self.commit(self.delta(self.add_entry('b'), [{'op': 'update', 'kind': 'revelation', 'id': 'V1',
                                                      'fact': 'F1'}]), expect=1)
        self.commit(self.delta(self.add_entry('c'), [{'op': 'discard', 'kind': 'revelation', 'id': 'V1',
                                                      'reason': 'the story moved on'}]))
        self.assertFalse(self.state()['facts']['F9']['known'])
        self.commit(self.delta(self.add_entry('d'), [self.route('d', 'late idea')]), expect=1)

    # ---- phase 5: scenes and pacing ----------------------------------------------------------

    def open_scene(self, sid='s1', **extra):
        return {'op': 'open', 'kind': 'scene', 'id': sid, 'mode': 'social', 'agenda': 'press Mara about the ledger',
                'exit_condition': 'Mara talks or leaves', **extra}

    def close_scene(self, sid='s1'):
        return {'op': 'close', 'kind': 'scene', 'id': sid, 'outcome': 'Mara admitted the debt'}

    def run_scenes(self, modes, serves=None):
        for n, mode in enumerate(modes, 1):
            ops = [self.open_scene(f's{n}', mode=mode, **({'serves': serves} if serves else {}))]
            if n > 1:
                ops.insert(0, self.close_scene(f's{n - 1}'))
            self.commit(self.delta(self.add_entry(f'Scene {n}.'), ops, why=f'scene {n} begins'))

    def test_scene_lifecycle_and_required_fields(self):
        e = self.add_entry()
        for bad in ({'mode': 'brawl'}, {'tension': 9}, {'serves': ['T404']}, {'agenda': ''}):
            self.commit(self.delta(self.add_entry('x'), [self.open_scene(**bad)]), expect=1)
        no_exit = self.open_scene()
        del no_exit['exit_condition']
        self.commit(self.delta(e, [no_exit]), expect=1)
        self.commit(self.delta(e, [self.open_scene(tension=2, participants=['Mara'])]))
        state = self.state()
        self.assertEqual((state['open_scene'], state['situation']['scene'], state['scene_count']), ('s1', 's1', 1))
        self.commit(self.delta(self.add_entry('a'), [self.open_scene('s2')]), expect=1)  # s1 still open
        self.commit(self.delta(self.add_entry('b'), [self.close_scene('s2')]), expect=1)  # not the open one
        self.commit(self.delta(self.add_entry('c'), [{**self.close_scene(), 'outcome': ''}]), expect=1)
        self.commit(self.delta(self.add_entry('d'), [self.close_scene(), self.open_scene('s2')]))
        self.assertEqual(self.state()['scenes']['s1']['status'], 'closed')
        self.assertEqual(self.state()['scene_count'], 2)

    def test_scene_serves_must_name_real_live_things(self):
        self.commit(self.delta(self.add_entry(), [self.thread()]))
        self.commit(self.delta(self.add_entry('a'), [self.open_scene(serves=['T1', 'want'])]))
        self.assertIn('serves: T1, want', run(self.root, 'hot').stdout)

    def test_same_mode_run_and_disconnected_run_are_flagged(self):
        self.run_scenes(['social'] * 4)
        out = run(self.root, 'hot').stdout
        self.assertIn('4 scenes in a row are social', out)
        self.assertIn('3 scenes in a row serve nothing', out)

    def test_variety_and_connection_clear_the_warnings(self):
        self.run_scenes(['social', 'action', 'social', 'discovery'], serves=['want'])
        out = run(self.root, 'hot').stdout
        self.assertNotIn('in a row', out)
        self.assertIn('recent modes: social, action, social, discovery', out)

    def test_resolved_purpose_is_advice_not_an_order(self):
        self.commit(self.delta(self.add_entry(), [self.open_scene()]))
        self.assertNotIn('served its purpose', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('a'), [{'op': 'update', 'kind': 'scene', 'id': 's1', 'resolved': True}]))
        self.assertIn('scene s1 has served its purpose', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('b'), [self.fact()]))  # a warning never blocks later work

    def test_boundary_report_reads_only_and_names_what_is_owed(self):
        self.commit(self.delta(self.add_entry(), [self.thread(due_day=2), {k: v for k, v in self.pressure().items() if k != 'clock_max'}]))
        self.run_scenes(['social', 'social'], serves=['T1'])
        before = (self.root / 'notes/gm/deltas.jsonl').read_text(encoding='utf-8')
        out = run(self.root, 'boundary').stdout
        for expected in ('OPEN scene s2 [social]', 'PACING recent modes: social, social',
                         'not used in the last three scenes: discovery, action', 'NEXT frame a situation'):
            self.assertIn(expected, out)
        self.assertEqual((self.root / 'notes/gm/deltas.jsonl').read_text(encoding='utf-8'), before)

    def test_scene_count_is_not_double_counted_with_a_plain_situation_scene(self):
        self.commit(self.delta(self.add_entry(), [{'op': 'set', 'kind': 'situation', 'fields': {'scene': 's1'}}]))
        self.commit(self.delta(self.add_entry('a'), [self.open_scene()]))
        self.assertEqual(self.state()['scene_count'], 1)

    # ---- layers: switch any phase on or off at any time -------------------------------------

    def test_layers_default_to_all_on_and_continuity_cannot_be_switched_off(self):
        out = run(self.root, 'layers').stdout
        self.assertEqual(out.count('ON'), 5)
        self.assertNotEqual(run(self.root, 'layers', '--off', '1').returncode, 0)
        self.assertNotEqual(run(self.root, 'layers', '--on', '9').returncode, 0)

    def test_a_layer_that_is_off_rejects_its_records_and_hides_its_output(self):
        run(self.root, 'layers', '--off', '2', '3', '4', '5')
        out = run(self.root, 'layers').stdout
        self.assertIn('1 continuity: ON', out)
        self.assertIn('2 memory: off', out)
        for ops in ([self.thread()], [self.pressure()], [self.secret(), self.rev()], [self.open_scene()]):
            self.commit(self.delta(self.add_entry(), ops), expect=1)
        result = run(self.root, 'check')
        self.assertIn('which is off. Switch it on first', result.stdout)
        self.commit(self.delta(self.add_entry('ok'), [self.fact()]))  # continuity still works
        self.assertIn('layers on: 1 continuity', run(self.root, 'hot').stdout)

    def test_switching_a_layer_on_again_restores_what_was_recorded_before(self):
        self.commit(self.delta(self.add_entry(), [self.thread(), self.pressure()]))
        run(self.root, 'layers', '--off', '2', '3')
        hot = run(self.root, 'hot', '--about', 'Mara', 'guild').stdout
        self.assertNotIn('THREADS', hot)
        self.assertNotIn('PRESSURES', hot)
        self.assertEqual(self.state()['threads'], {})
        run(self.root, 'layers', '--on', '2')
        back = run(self.root, 'hot', '--about', 'guild').stdout
        self.assertIn('T1', back)  # layer 2 is on again, with the thread recorded earlier
        self.assertNotIn('PRESSURES', back)  # layer 3 is still off

    def test_a_bad_layers_file_is_reported_not_ignored(self):
        (self.root / 'notes/gm/layers.json').write_text('{"active": [7]}', encoding='utf-8')
        result = run(self.root, 'hot')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('layers.json', result.stderr)

    # ---- feedback from a real campaign ---------------------------------------------------------

    def test_errors_say_what_is_allowed_and_schema_lists_everything(self):
        e = self.add_entry()
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            {'op': 'update', 'kind': 'npc', 'id': 'N1', 'fields': {'want': 'x'}},
            {'op': 'add', 'kind': 'monster', 'id': 'M1'}])), encoding='utf-8')
        out = run(self.root, 'check').stdout
        self.assertIn('"update" is not an op for npc; use one of: set', out)
        self.assertIn('unknown kind "monster"; use one of: contract, situation, fact', out)
        schema = run(self.root, 'schema').stdout
        for expected in ('"id": "auto"', '{"op": "advance", "kind": "pressure"', 'scene (layer 5)', '{"op": "set", "kind": "npc"'):
            self.assertIn(expected, schema)
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            self.fact(mood='x'), self.fact('F2', text='x' * 400)])), encoding='utf-8')
        out = run(self.root, 'check').stdout
        self.assertIn('unknown keys: mood (allowed:', out)
        self.assertIn('at most 300 characters (this one is 400)', out)

    def test_auto_ids_are_assigned_at_commit_and_are_stable(self):
        auto = lambda **kw: self.fact('auto', **kw)  # noqa: E731
        self.commit(self.delta(self.add_entry(), [auto(), auto(text='Second.'), self.thread('auto'),
                                                  self.pressure('auto'), self.open_scene('auto')]))
        state = self.state()
        self.assertEqual(sorted(state['facts']), ['F1', 'F2'])
        self.assertEqual((list(state['threads']), list(state['pressures']), list(state['scenes'])), (['T1'], ['P1'], ['s1']))
        self.commit(self.delta(self.add_entry('b'), [auto(text='Third.')]))
        self.assertIn('F3', self.state()['facts'])
        deltas = (self.root / 'notes/gm/deltas.jsonl').read_text(encoding='utf-8')
        self.assertNotIn('"auto"', deltas)  # the log holds real ids only

    def test_auto_id_also_works_for_a_replacement(self):
        self.commit(self.delta(self.add_entry(), [self.fact()]))
        self.commit(self.delta(self.add_entry('b'), [{'op': 'replace', 'kind': 'fact', 'id': 'F1', 'new': 'auto',
                                                      'text': 'Changed.', 'reason': 'it changed in the story'}]))
        self.assertEqual(self.state()['facts']['F1']['replaced_by'], 'F2')

    def test_a_long_fact_is_called_a_summary_not_a_fact(self):
        e = self.add_entry()
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            self.fact(text='Ash did many things in the scene. ' * 7)])), encoding='utf-8')
        out = run(self.root, 'check').stdout
        self.assertIn('characters. A fact is one lasting truth, not a summary of the turn', out)
        self.assertEqual(run(self.root, 'commit').returncode, 0)  # advice only

    def test_a_pressure_advanced_without_new_next_action_asks_if_it_is_still_true(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        e = self.add_entry('b')
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [self.advance()])), encoding='utf-8')
        self.assertIn('advanced without a new next_action: is "send a bailiff to Mara" still', run(self.root, 'check').stdout)
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(e, [
            self.advance(next_action='the bailiff waits outside')])), encoding='utf-8')
        self.assertNotIn('without a new next_action', run(self.root, 'check').stdout)
        self.commit(self.delta(self.add_entry('c'), [{'op': 'update', 'kind': 'pressure', 'id': 'P1',
                                                      'next_action': 'the guild regroups'}]))
        self.assertEqual(self.state()['pressures']['P1']['next_action'], 'the guild regroups')

    def test_boundary_asks_whether_each_next_action_is_still_true(self):
        self.commit(self.delta(self.add_entry(), [self.pressure()]))
        self.assertIn('STILL TRUE? P1 Harbour guild next: "send a bailiff to Mara"', run(self.root, 'boundary').stdout)

    # ---- truth, belief and open questions ------------------------------------------------------

    def test_a_reveal_needs_an_established_truth_and_a_rumour_is_not_one(self):
        guess = self.secret(status='provisional')
        reveal = {'op': 'reveal', 'kind': 'revelation', 'id': 'V1', 'route': 'a', 'how': 'the harbourmaster admitted it'}
        self.commit(self.delta(self.add_entry(), [guess, self.rev(), self.route('a', 'Mara confesses')]))
        self.commit(self.delta(self.add_entry('a'), [reveal]), expect=1)
        establish = {'op': 'update', 'kind': 'fact', 'id': 'F9', 'status': 'established', 'reason': 'he admitted it'}
        self.commit(self.delta(self.add_entry('b'), [establish, reveal]))
        self.assertTrue(self.state()['facts']['F9']['known'])
        self.commit(self.delta(self.add_entry('c'), [self.fact('F2', status='rumour', known=False),
                                                     self.rev('V2', fact='F2')]), expect=1)

    def test_an_older_log_that_revealed_a_provisional_fact_still_replays(self):
        e = self.add_entry()
        ops = [self.secret(status='provisional'), self.rev(), self.route('a', 'Mara confesses'),
               {'op': 'reveal', 'kind': 'revelation', 'id': 'V1', 'route': 'a', 'how': 'he admitted it'}]
        (self.root / 'notes/gm/deltas.jsonl').write_text(
            json.dumps({'seq': 1, **self.delta(e, ops)}) + '\n', encoding='utf-8', newline='\n')
        result = run(self.root, 'state')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['revelations']['V1']['status'], 'revealed')

    def test_a_provisional_fact_left_known_draws_a_warning(self):
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(self.add_entry(), [
            self.fact(status='provisional')])), encoding='utf-8')
        self.assertIn('F1 is provisional but marked known to the player (the default)', run(self.root, 'check').stdout)
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(self.add_entry('b'), [
            self.fact(status='provisional', known=False)])), encoding='utf-8')
        self.assertNotIn('marked known', run(self.root, 'check').stdout)

    def test_an_open_question_shows_as_undecided(self):
        self.commit(self.delta(self.add_entry(), [
            {'op': 'set', 'kind': 'situation', 'fields': {'day': 1, 'present': ['Mara'], 'scene': 's1'}},
            {'op': 'add', 'kind': 'thread', 'id': 'T1', 'type': 'question', 'tags': ['Mara'],
             'text': 'Will Mara trust the protagonist with what she knows?'}]))
        self.assertIn('T1 [question, open] Will Mara trust the protagonist with what she knows? '
                      '(undecided: let play answer it)', run(self.root, 'hot').stdout)
        self.commit(self.delta(self.add_entry('b'), [{'op': 'resolve', 'kind': 'thread', 'id': 'T1',
                                                      'resolution': 'She told them everything.'}]))
        self.assertEqual(self.state()['threads']['T1']['status'], 'resolved')

    def test_a_clock_can_lose_ground_and_its_stages_say_what_each_step_means(self):
        stages = ['recruited the harbourmaster', 'pressing the merchants', 'replacing the council']
        self.commit(self.delta(self.add_entry(), [self.pressure(stages=stages + ['too many', 'way too many'])]), expect=1)
        self.commit(self.delta(self.add_entry('a'), [self.pressure(stages=stages)]))
        self.commit(self.delta(self.add_entry('b'), [self.advance(steps=2, next_action='lean on the merchants')]))
        hot = run(self.root, 'hot', '--about', 'guild').stdout
        self.assertIn('reached: pressing the merchants | next stage: replacing the council', hot)
        self.commit(self.delta(self.add_entry('c'), [self.advance(steps=-3, basis='action')]), expect=1)
        self.commit(self.delta(self.add_entry('d'), [self.advance(steps=-1, basis='action',
                                                                   reason='the player exposed the harbourmaster')]))
        self.assertEqual(self.state()['pressures']['P1']['clock'], 1)
        self.assertIn('P1 Harbour guild clock 1/4 | reached: recruited the harbourmaster', run(self.root, 'review').stdout)
        no_clock = {k: v for k, v in self.pressure('P2', stages=['one']).items() if k != 'clock_max'}
        (self.root / 'notes/gm/pending.json').write_text(json.dumps(self.delta(self.add_entry('e'), [no_clock])),
                                                          encoding='utf-8')
        self.assertIn('stages need a clock', run(self.root, 'check').stdout)


if __name__ == '__main__':
    unittest.main()
