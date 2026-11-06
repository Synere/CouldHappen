import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { request as httpRequest } from 'node:http';
import { resolve, relative } from 'node:path';
import { randomUUID } from 'node:crypto';

const root = process.env.COULDHAPPEN_TEST_ROOT;
const python = process.env.COULDHAPPEN_TEST_PYTHON;
const repo = resolve(import.meta.dirname, '../..');
const origin = new URL(process.env.COULDHAPPEN_TEST_URL);
function rawGet(path) {
  return new Promise((resolvePromise, reject) => {
    const request = httpRequest({ host: origin.hostname, port: origin.port, path, method: 'GET' }, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { body += chunk; });
      response.on('end', () => resolvePromise({ status: response.statusCode, text: body }));
    });
    request.on('error', reject);
    request.end();
  });
}
function command(...args) { return JSON.parse(execFileSync(python, ['-m', 'helpers', ...args, '--root', root], { cwd: repo, encoding: 'utf8' })); }
function edit(channel, body) {
  const token = command('writer', 'pause').token;
  const path = resolve(root, 'public', `${channel}.md`);
  const id = randomUUID();
  writeFileSync(path, readFileSync(path, 'utf8') + `\n<!-- couldhappen:entry {"id":"${id}","role":"writer"} -->\n${body}\n<!-- couldhappen:end -->\n`);
  command('writer', 'release', '--token', token);
  return id;
}

test('reader, drafts, saved inputs, blocked/uncertain receipts, refresh, sanitization and revision', async ({ page }) => {
  await page.goto('/');
  const draft = page.locator('textarea');
  await expect(page.getByRole('heading', { name: 'The story', exact: true })).toBeVisible();
  await draft.fill('A retained Story draft');
  await page.getByRole('button', { name: 'Director', exact: true }).click();
  await draft.fill('A Director preference');
  await page.reload();
  await page.getByRole('button', { name: 'Director', exact: true }).click();
  await expect(draft).toHaveValue('A Director preference');
  await page.getByRole('button', { name: 'Story', exact: true }).click();
  await expect(draft).toHaveValue('A retained Story draft');
  command('writer', 'block', '--on');
  await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeDisabled();
  await expect(draft).toHaveValue('A retained Story draft');
  command('writer', 'block', '--off');
  await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeEnabled();
  let original;
  await page.route('**/api/entries', async route => {
    original = route.request().postDataJSON();
    // The backend persists the request but the browser never receives its receipt.
    await route.fetch();
    await route.abort('failed');
  }, { times: 1 });
  await page.getByRole('button', { name: 'Send', exact: true }).click();
  await expect(draft).toHaveValue('');
  const saved = JSON.parse(readFileSync(resolve(root, '.couldhappen/connection.json'), 'utf8'));
  const snapshot = await (await page.request.get('/api/snapshot')).json();
  expect(snapshot.story.filter(entry => entry.id === original.id)).toHaveLength(1);
  const id = edit('story', '**Safe prose** <script>window.__injected=1</script><img src="https://example.invalid/x" onerror="window.__injected=2"><svg onload="window.__injected=3"></svg><a href="javascript:alert(1)">unsafe</a>');
  const prose = page.locator(`[data-entry-id="${id}"]`);
  await expect(prose.locator('strong')).toHaveText('Safe prose');
  await expect(prose.locator('.prose img, .prose script, .prose svg')).toHaveCount(0);
  expect(await page.evaluate(() => window.__injected)).toBeUndefined();
  const revisionToken = command('writer', 'pause').token;
  const storyPath = resolve(root, 'public/story.md');
  writeFileSync(storyPath, readFileSync(storyPath, 'utf8').replace('**Safe prose**', '**Revised prose**'));
  command('writer', 'release', '--token', revisionToken);
  await expect(prose.locator('strong')).toHaveText('Revised prose');
  await expect(prose.getByText('Passage updated')).toBeVisible();
  // A failed save with no append remains uncertain until a generation resync.
  await draft.fill('Uncertain absent message');
  await page.route('**/api/entries', route => route.abort('failed'), { times: 1 });
  await page.getByRole('button', { name: 'Send', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Retry same save' })).toBeVisible();
  const uncertainToken = command('writer', 'pause').token;
  command('writer', 'invalidate', '--token', uncertainToken);
  command('writer', 'release', '--token', uncertainToken);
  await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeVisible();
  await expect(draft).toHaveValue('Uncertain absent message');
  const noReplay = await (await page.request.get('/api/snapshot')).json();
  expect(noReplay.story.filter(e => e.body === 'Uncertain absent message')).toHaveLength(0);
  await draft.fill('Draft across generation');
  const token = command('writer', 'pause').token;
  command('writer', 'invalidate', '--token', token);
  command('writer', 'release', '--token', token);
  await expect(draft).toHaveValue('Draft across generation');
  const privatePaths = ['/control', '/imports/source.json', '/.couldhappen/connection.json', '/@fs/' + root.replaceAll('\\', '/') + '/private.md', '/@fs/' + root.replaceAll('\\', '/') + '/imports/source.json', '/@fs/' + root.replaceAll('\\', '/') + '/START_HERE.md', '/@fs/' + root.replaceAll('\\', '/') + '/public/story.md', '/public/%2e%2e/private.md', '/imports/%2e%2e/private.md', '/api/assets/%2e%2e/private.md'];
  for (const path of privatePaths) {
    const response = await rawGet(path);
    expect(response.status, path).toBeGreaterThanOrEqual(400);
    expect(response.text).not.toContain('PRIVATE_BOUNDARY_FIXTURE');
    expect(response.text).not.toContain(saved.secret);
  }
  const traversal = await rawGet('/src/%2e%2e/%2e%2e/private.md');
  expect(traversal.text).not.toContain('PRIVATE_BOUNDARY_FIXTURE');
  expect(traversal.text).not.toContain(saved.secret);
});

test('Vite refuses accidental private source imports', async ({ page }) => {
  const probe = resolve(repo, 'web/src/private-import-probe.js');
  const privateFile = resolve(root, 'private.md');
  expect(readFileSync(privateFile, 'utf8')).toContain('PRIVATE_BOUNDARY_FIXTURE');
  const privateSource = relative(resolve(repo, 'web/src'), privateFile).replaceAll('\\', '/');
  writeFileSync(probe, `import secret from '${privateSource}?raw';\nexport default secret;\n`);
  try {
    await page.goto('/');
    const served = await page.request.get('/src/private-import-probe.js');
    expect(await served.text()).not.toContain('PRIVATE_BOUNDARY_FIXTURE');
    const result = await page.evaluate(async () => {
      try {
        await import('/src/private-import-probe.js');
        return 'loaded';
      } catch {
        return 'blocked';
      }
    });
    expect(result).toBe('blocked');
  } finally {
    rmSync(probe, { force: true });
  }
});

test('reading position, keyboard, narrow cast, recovery waiting, reduced motion and screenshots', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  const scroller = page.locator('.conversation');
  await expect(scroller).toBeVisible();
  await scroller.evaluate(element => { element.scrollTop = 250; element.dispatchEvent(new Event('scroll')); });
  await page.locator('textarea').fill('Draft survives reader updates');
  edit('story', 'A new synthetic passage that must not move an earlier reading position.');
  await page.waitForTimeout(1200);
  expect(await scroller.evaluate(element => element.scrollTop)).toBeCloseTo(250, 0);
  await page.reload();
  await expect(page.locator('textarea')).toHaveValue('Draft survives reader updates');
  await expect.poll(() => scroller.evaluate(element => element.scrollTop)).toBe(250);
  // Actual compatible source edit exercises Vite HMR; always restore source bytes.
  const css = resolve(repo, 'web/src/styles.css');
  const originalCss = readFileSync(css);
  try {
    writeFileSync(css, Buffer.concat([originalCss, Buffer.from('\n:root { --hmr-observation: observed; }\n')]));
    await expect.poll(() => page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--hmr-observation').trim())).toBe('observed');
    await expect(page.locator('textarea')).toHaveValue('Draft survives reader updates');
    expect(await scroller.evaluate(element => element.scrollTop)).toBe(250);
  } finally { writeFileSync(css, originalCss); }
  await scroller.evaluate(element => { element.scrollTop = 0; });
  await page.screenshot({ path: resolve(repo, '.impeccable/review/desktop.png'), fullPage: true });
  const question = edit('director', 'Recovery fixture: what direction should we take now?');
  const token = command('writer', 'pause').token;
  writeFileSync(resolve(root, 'public/work.json'), JSON.stringify({ schema_version: 1, mode: 'awaiting_director', director_question_id: question }));
  command('writer', 'invalidate', '--token', token);
  command('writer', 'release', '--token', token);
  await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeDisabled();
  expect(command('writer', 'pause').token).toBeTruthy();
  command('writer', 'recover', '--previous-writer-stopped');
  // Recovery changes the generation; reread before submitting so the test does
  // not race the next poll with a stale generation.
  await page.reload();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('button', { name: 'Director', exact: true }).click();
  await page.locator('textarea').fill('New Director guidance');
  await expect(page.getByRole('button', { name: 'Send', exact: true })).toBeEnabled();
  await page.locator('textarea').press('Control+Enter');
  await expect(page.locator('textarea')).toHaveValue('');
  await page.getByRole('button', { name: 'Cast', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Character without portrait' })).toBeVisible();
  await page.getByRole('button', { name: 'Close cast' }).click();
  await page.getByRole('button', { name: 'Cast', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Close cast' })).toBeFocused();
  expect(await page.evaluate(() => /** @type {HTMLElement} */ (document.querySelector('.topbar')).inert)).toBe(true);
  await expect(page.locator('#cast-panel')).toHaveAttribute('role', 'dialog');
  await expect(page.locator('#cast-panel')).toHaveAttribute('aria-modal', 'true');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: 'Close cast' })).toBeHidden();
  expect(await page.evaluate(() => /** @type {HTMLElement} */ (document.querySelector('.topbar')).inert)).toBe(false);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.screenshot({ path: resolve(repo, '.impeccable/review/mobile.png'), fullPage: true });
  const modeToken = command('writer', 'pause').token;
  writeFileSync(resolve(root, 'public/work.json'), JSON.stringify({ schema_version: 1, mode: 'play', director_question_id: null }));
  command('writer', 'release', '--token', modeToken);
});

test('a story picture enlarges and cast members can ask for a portrait', async ({ page }) => {
  await page.goto('/');
  const figure = page.locator('figure.plate').last();
  await expect(figure.locator('figcaption')).toHaveText('A synthetic lit doorway');
  await figure.getByRole('button').click();
  const dialog = page.getByRole('dialog', { name: /doorway/i });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('button', { name: /close/i })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(figure.getByRole('button')).toBeFocused();
  const toggle = page.getByRole('button', { name: 'Cast', exact: true });
  if (await toggle.isVisible()) await toggle.click();
  const ask =page.getByRole('button', { name: /portrait for Character without portrait/i });
  await expect(ask).toBeEnabled();
  await expect(page.getByRole('heading', { name: 'Character who left' })).toHaveCount(0);
  await ask.click();
  await expect(page.getByRole('status').filter({ hasText: 'Requested' })).toBeVisible();
  expect(readFileSync(resolve(root, 'public/director.md'), 'utf8')).toContain('Make a portrait for Character without portrait (cast id no-portrait).');
});

test('first setup empty states remain useful and do not invent a scene', async ({ page }) => {
  const token = command('writer', 'pause').token;
  writeFileSync(resolve(root, 'public/story.md'), '# Story\n');
  writeFileSync(resolve(root, 'public/director.md'), '# Director\n');
  writeFileSync(resolve(root, 'public/cast.json'), JSON.stringify({ schema_version: 1, characters: [] }));
  writeFileSync(resolve(root, 'public/work.json'), JSON.stringify({ schema_version: 1, mode: 'play', director_question_id: null }));
  command('writer', 'invalidate', '--token', token);
  command('writer', 'release', '--token', token);
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await expect(page.getByText('A story begins with a possibility.')).toBeVisible();
  await expect(page.getByText('People will appear here as the story reveals them.')).toBeVisible();
  await page.screenshot({ path: resolve(repo, '.impeccable/review/empty.png'), fullPage: true });
});
