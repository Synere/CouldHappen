// Opt-in Pi 1.5.0 example. Set absolute interpreter/workspace paths during setup.
import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

export default function (pi: ExtensionAPI) {
  const root = process.env.COULDHAPPEN_ROOT;
  const python = process.env.COULDHAPPEN_PYTHON || 'python';
  let lastDirty = '';
  pi.on('agent_start', async () => { /* Do not gate temporary waits. */ });
  pi.on('agent_before_settle', async (event, ctx) => {
    if (!root || resolve(ctx.cwd) !== resolve(root)) return;
    let state;
    try { state = JSON.parse(readFileSync(resolve(root, '.couldhappen/control.json'), 'utf8')); }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') ctx.ui.notify('CouldHappen checkpoint assurance unavailable: ' + String(error), 'warning');
      return;
    }
    if (!state.armed) return;
    let result;
    try {
      let output: string;
      try { output = execFileSync(python, ['-m', 'helpers', 'checkpoint', 'check', '--root', root], { cwd: root, encoding: 'utf8' }); }
      catch (error) { output = String((error as { stdout?: string }).stdout || ''); }
      result = JSON.parse(output);
    } catch (error) {
      ctx.ui.notify('CouldHappen checkpoint assurance unavailable: ' + String(error), 'warning');
      return;
    }
    if (result.status === 'clean') { lastDirty = ''; return; }
    if (result.status !== 'dirty') { ctx.ui.notify('CouldHappen checkpoint assurance unavailable: ' + result.message, 'warning'); return; }
    const fingerprint = JSON.stringify(result.paths);
    if (fingerprint === lastDirty || !event.context.canContinue) {
      ctx.ui.notify('CouldHappen remains uncheckpointed; continuation unavailable or made no status progress. Inspect Git permissions and checkpoint explicitly.', 'warning');
      return;
    }
    lastDirty = fingerprint;
    return { entries: [...event.entries, {
      type: 'custom_message', customType: 'couldhappen-checkpoint', display: false,
      content: 'CouldHappen play is uncheckpointed: ' + fingerprint + '. Review scoped work, finish durable notes, and make a meaningful checkpoint. Do not auto-commit unrelated files.'
    }], continue: true };
  });
  pi.on('agent_settled', async () => { lastDirty = ''; });
}
