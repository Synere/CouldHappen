<script>
  import { onDestroy } from 'svelte';
  import { submit, SaveError } from '../lib/api.js';
  /** @type {{channel:import('../lib/session.js').Channel,snapshot:import('../lib/session.js').Snapshot,session:import('../lib/session.js').Session,epoch:number,refresh:()=>void,connected:boolean}} */
  let { channel, snapshot, session, epoch, refresh, connected } = $props();
  let sending = $state(false);
  const controller = new AbortController();
  onDestroy(() => controller.abort());
  const draft = $derived.by(() => { void epoch; return session.drafts[channel]; });
  const pending = $derived.by(() => { void epoch; return session.pending[channel]; });
  const notice = $derived.by(() => { void epoch; return session.notice[channel]; });
  const permission = $derived(snapshot.permissions[channel]);
  const recovery = $derived(snapshot.work.mode === 'awaiting_director' && channel === 'director');
  /** @param {Event} event */
  async function send(event) {
    event?.preventDefault();
    if (sending || !permission.allowed || !connected) return;
    const request = session.begin(channel);
    if (!request) return;
    sending = true;
    try {
      const receipt = await submit(request, controller.signal);
      session.receipt(channel, receipt.id);
    } catch (error) {
      if (!controller.signal.aborted) {
        const uncertain = !(error instanceof SaveError) || error.status >= 500;
        session.failed(channel, uncertain ? 'Save receipt uncertain. Text retained; check the reader or retry the same save.' : (error instanceof Error ? error.message : 'Save failed.'), uncertain);
      }
    } finally { sending = false; refresh(); }
  }
  /** @param {KeyboardEvent} event */
  function keydown(event) {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') send(event);
  }
</script>

<form class="composer" onsubmit={send}>
  <label for="contribution">{channel === 'story' ? 'What do you do?' : 'Your note to the writer'}</label>
  <textarea id="contribution" rows="3" value={draft} oninput={event => session.draft(channel, event.currentTarget.value)} onkeydown={keydown} placeholder={channel === 'story' ? 'An action, a line of dialogue, a contribution…' : 'An idea, preference, question, or direction…'} aria-describedby="save-status"></textarea>
  <div class="composer-foot">
    <p id="save-status" role="status">{!connected ? 'Connection interrupted. Your draft is retained.' : !permission.allowed ? permission.reason : recovery ? 'The story is paused until your direction is interpreted.' : notice || 'Your message is saved before the writer handles it.'}</p>
    <button class="send" type="submit" disabled={sending || !permission.allowed || !connected || (!pending && !draft.trim())}>{sending ? 'Saving…' : pending ? 'Retry same save' : 'Send'}</button>
  </div>
</form>
