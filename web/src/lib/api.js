export class SaveError extends Error {
  /** @param {string} message @param {string} code @param {number} status */
  constructor(message, code, status) { super(message); this.code = code; this.status = status; }
}

/** @param {import('./session.js').Submission} payload @param {AbortSignal} signal */
export async function submit(payload, signal) {
  const response = await fetch('/api/entries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal });
  const data = await response.json();
  if (!response.ok) throw new SaveError(data.message || 'Save failed; draft retained.', data.code, response.status);
  return data;
}

/** Serial reads; abort on cleanup and never apply an older read after a newer one.
 * @param {(snapshot:import('./session.js').Snapshot)=>void} onSnapshot
 * @param {(message:string)=>void} onError */
export function poll(onSnapshot, onError) {
  let closed = false, etag = '', running = false, again = false, delay = 1000;
  /** @type {ReturnType<typeof setTimeout>|undefined} */
  let timer;
  const controller = new AbortController();
  async function refresh() {
    if (closed) return;
    clearTimeout(timer);
    if (running) { again = true; return; }
    running = true;
    try {
      const response = await fetch('/api/snapshot', { headers: etag ? { 'If-None-Match': etag } : {}, signal: controller.signal });
      if (!response.ok && response.status !== 304) throw new Error('Reader connection failed. Your draft is retained.');
      if (response.status !== 304) {
        const data = await response.json();
        if (!closed) { onSnapshot(data); etag = response.headers.get('ETag') || ''; delay = Math.max(250, Number(data.poll_interval_ms) || 1000); }
      }
      if (!closed) onError('');
    } catch (error) { if (!closed) onError(error instanceof Error ? error.message : 'Reader connection failed.'); }
    finally {
      running = false;
      if (!closed) { timer = setTimeout(refresh, again ? 0 : delay); again = false; }
    }
  }
  refresh();
  return { refresh, close() { closed = true; controller.abort(); clearTimeout(timer); } };
}
