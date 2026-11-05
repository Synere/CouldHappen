/** @typedef {'story'|'director'} Channel */
/** @typedef {{schema_version:number,workspace_id:string,generation:string,channel:Channel,id:string,body:string}} Submission */
/** @typedef {{id:string,role:'human'|'writer',status?:string,body:string,body_hash:string}} Entry */
/** @typedef {{id:string,name:string,description?:string,portrait?:string}} Character */
/** @typedef {{schema_version:number,workspace_id:string,generation:string,revision:string,poll_interval_ms:number,story:Entry[],director:Entry[],cast:{schema_version:number,characters:Character[]},assets:Record<string,string>,work:{mode:string,director_question_id:string|null},permissions:Record<Channel,{allowed:boolean,reason:string|null}>,validation_error:string|null}} Snapshot */
/** @typedef {Record<Channel,Record<string,string>>} Changes */

export class Session {
  /** @param {Pick<Storage, 'getItem'|'setItem'>} storage */
  constructor(storage) {
    this.storage = storage;
    this.workspace = '';
    /** @type {Snapshot|null} */
    this.snapshot = null;
    this.drafts = { story: '', director: '' };
    /** @type {Record<Channel, Submission|null>} */
    this.pending = { story: null, director: null };
    this.notice = { story: '', director: '' };
    this.anchors = { story: 0, director: 0 };
    this.notify = () => {};
  }
  key() { return `couldhappen:v1:${this.workspace}`; }
  persist() {
    if (!this.workspace) return;
    try { this.storage.setItem(this.key(), JSON.stringify({ drafts: this.drafts, pending: this.pending, anchors: this.anchors })); }
    catch { this.notice.story = this.notice.director = 'Draft storage unavailable. Keep this tab open or copy your text before refreshing.'; }
    this.notify();
  }
  /** @param {Channel} channel @param {string} text */
  draft(channel, text) { this.drafts[channel] = text; this.persist(); }
  /** @param {Channel} channel @param {number} top */
  anchor(channel, top) { this.anchors[channel] = top; this.persist(); }
  /** @param {Snapshot} next */
  receive(next) {
    if (this.workspace !== next.workspace_id) {
      this.workspace = next.workspace_id;
      try {
        const saved = JSON.parse(this.storage.getItem(this.key()) || '{}');
        for (const channel of /** @type {Channel[]} */ (['story', 'director'])) {
          this.drafts[channel] = typeof saved.drafts?.[channel] === 'string' ? saved.drafts[channel] : '';
          this.pending[channel] = saved.pending?.[channel] || null;
          this.anchors[channel] = Number(saved.anchors?.[channel]) || 0;
        }
      } catch { /* A bad local draft never replaces canonical records. */ }
    }
    const changedGeneration = this.snapshot && this.snapshot.generation !== next.generation;
    const previous = this.snapshot;
    /** @type {Changes} */
    const changes = { story: {}, director: {} };
    for (const channel of /** @type {Channel[]} */ (['story', 'director'])) {
      const before = new Map((previous?.[channel] || []).map(e => [e.id, e.body_hash]));
      changes[channel] = Object.fromEntries(next[channel].map(e => [e.id,
        !previous || changedGeneration ? 'initial' : !before.has(e.id) ? 'new' : before.get(e.id) !== e.body_hash ? 'revised' : 'same']));
      const pending = this.pending[channel];
      if (pending) {
        const saved = next[channel].find(e => e.id === pending.id);
        if (saved?.role === 'human' && saved.body === pending.body) this.receipt(channel, pending.id, false);
        else if (pending.generation !== next.generation || pending.workspace_id !== next.workspace_id) {
          this.pending[channel] = null;
          this.notice[channel] = 'Workspace changed. Your draft is retained; review it and deliberately send when ready.';
        } else if (saved) {
          this.pending[channel] = null;
          this.notice[channel] = 'Request identity conflicts with saved text. Review your retained draft before sending.';
        }
      }
    }
    this.snapshot = next;
    this.persist();
    return changes;
  }
  /** @param {Channel} channel @param {string} id */
  begin(channel, id = crypto.randomUUID()) {
    if (this.pending[channel]) return this.pending[channel];
    if (!this.snapshot || !this.drafts[channel].trim()) return null;
    const request = Object.freeze({ schema_version: 1, workspace_id: this.workspace,
      generation: this.snapshot.generation, channel, id, body: this.drafts[channel].replace(/\r\n?/g, '\n') });
    this.pending[channel] = request;
    this.notice[channel] = '';
    this.persist();
    return request;
  }
  /** @param {Channel} channel @param {string} id */
  receipt(channel, id, persist = true) {
    const pending = this.pending[channel];
    if (!pending || pending.id !== id) return;
    if (this.drafts[channel].replace(/\r\n?/g, '\n') === pending.body) this.drafts[channel] = '';
    this.pending[channel] = null;
    this.notice[channel] = 'Saved. The writer has not necessarily handled it yet.';
    if (persist) this.persist();
  }
  /** @param {Channel} channel @param {string} message @param {boolean} uncertain */
  failed(channel, message, uncertain) {
    if (!uncertain) this.pending[channel] = null;
    this.notice[channel] = message;
    this.persist();
  }
}
