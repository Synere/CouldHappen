import test from 'node:test';
import assert from 'node:assert/strict';
import { Session } from '../src/lib/session.js';

const storage = () => { const data = new Map(); return { getItem: key => data.get(key), setItem: (key, value) => data.set(key, value) }; };
const snapshot = (generation = 'one', story = [], director = []) => ({ workspace_id: 'workspace', generation, story, director });
const entry = (id, body, role = 'writer') => ({ id, body, body_hash: body, role });

test('initial/new/revised recognition; metadata does not replay and recovery renders directly', () => {
  const session = new Session(storage());
  assert.equal(session.receive(snapshot('one', [entry('1', 'old')])).story['1'], 'initial');
  assert.equal(session.receive(snapshot('one', [entry('1', 'old'), entry('2', 'new')])).story['2'], 'new');
  assert.equal(session.receive(snapshot('one', [entry('1', 'revised'), entry('2', 'new')])).story['1'], 'revised');
  assert.equal(session.receive(snapshot('one', [entry('1', 'revised'), entry('2', 'new')])).story['2'], 'same');
  assert.equal(session.receive(snapshot('two', [entry('1', 'restored')])).story['1'], 'initial');
});

test('immutable uncertain retry and newer typed draft survive receipt and refresh', () => {
  const saved = storage();
  let session = new Session(saved);
  session.receive(snapshot());
  session.draft('story', 'first');
  const request = session.begin('story', 'request');
  session.draft('story', 'newer typing');
  assert.equal(session.begin('story', 'another'), request);
  assert.equal(request.body, 'first');
  assert.ok(Object.isFrozen(request));
  session = new Session(saved);
  session.receive(snapshot());
  assert.equal(session.pending.story.id, 'request');
  session.receive(snapshot('one', [entry('request', 'first', 'human')]));
  assert.equal(session.pending.story, null);
  assert.equal(session.drafts.story, 'newer typing');
});

test('generation changes never replay missing uncertain input; channel drafts and anchors persist', () => {
  const saved = storage();
  let session = new Session(saved);
  session.receive(snapshot());
  session.draft('story', 'withdrawn');
  session.draft('director', 'preference');
  session.anchor('story', 120);
  session.begin('story', 'request');
  session = new Session(saved);
  session.receive(snapshot('two'));
  assert.equal(session.pending.story, null);
  assert.equal(session.drafts.story, 'withdrawn');
  assert.equal(session.drafts.director, 'preference');
  assert.equal(session.anchors.story, 120);
  assert.match(session.notice.story, /deliberately send/);
});

test('closed saves retain draft; only exact confirmed body clears', () => {
  const session = new Session(storage());
  session.receive(snapshot());
  session.draft('story', 'keep');
  session.begin('story', 'id');
  session.failed('story', 'paused', false);
  assert.equal(session.drafts.story, 'keep');
  assert.equal(session.pending.story, null);
  session.begin('story', 'id2');
  session.receipt('story', 'wrong');
  assert.ok(session.pending.story);
  session.receipt('story', 'id2');
  assert.equal(session.drafts.story, '');
});

import { splitBody } from '../src/lib/markdown.js';

test('splitBody lifts standalone picture lines and ignores code fences', () => {
  const { text, pictures } = splitBody('Before.\n\n![A doorway](/api/assets/scene-1.png)\n\nAfter.\n\n```\n![x](/api/assets/no.png)\n```');
  assert.deepEqual(pictures, [{ alt: 'A doorway', name: 'scene-1.png' }]);
  assert.ok(!text.includes('scene-1.png'));
  assert.ok(text.includes('/api/assets/no.png'));
});

import { firstReveal } from '../src/lib/reveal.js';

test('a passage version is revealed once, so switching channels does not replay typing', () => {
  assert.equal(firstReveal('a:1'), true);
  assert.equal(firstReveal('a:1'), false);
  assert.equal(firstReveal('a:2'), true);
});
