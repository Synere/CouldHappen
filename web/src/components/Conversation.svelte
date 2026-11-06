<script>
  import { onMount, tick } from 'svelte';
  import ProseEntry from './ProseEntry.svelte';
  /** @type {{entries:import('../lib/session.js').Entry[],changes:Record<string,string>,channel:import('../lib/session.js').Channel,session:import('../lib/session.js').Session,assets?:Record<string,string>}} */
  let { entries, changes, channel, session, assets = {} } = $props();
  /** @type {HTMLElement} */
  let scroller;
  let follow = true;
  let ready = false;
  let previous = '';
  onMount(() => {
    scroller.scrollTop = session.anchors[channel] || 0;
    follow = !session.anchors[channel];
    ready = true;
  });
  function remember() {
    if (!ready) return;
    follow = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 80;
    session.anchor(channel, scroller.scrollTop);
  }
  /** @param {boolean} shouldFollow @param {number} top */
  function settle(shouldFollow, top) {
    if (!scroller || !ready) return;
    if (!shouldFollow) { scroller.scrollTop = top; return; }
    scroller.scrollTop = scroller.scrollHeight;
    const articles = /** @type {HTMLElement[]} */ ([...scroller.querySelectorAll('article[data-entry-id]')]);
    if (!articles.length) return;
    const box = scroller.getBoundingClientRect();
    const last = articles[articles.length - 1];
    const lastCut = box.top - last.getBoundingClientRect().top;
    const lastId = last.dataset.entryId || '';
    // A new long passage should be read from its beginning, not its end.
    if (changes?.[lastId] === 'new' && last.offsetHeight > scroller.clientHeight * .6 && lastCut > 0) {
      scroller.scrollTop -= lastCut;
      return;
    }
    // A status banner can change the viewport height; do not slice a nearly
    // complete entry at the top edge. Snap that entry into full view instead.
    const first = articles.find(article => article.getBoundingClientRect().bottom > box.top + 1);
    if (first) {
      const cut = box.top - first.getBoundingClientRect().top;
      if (cut > 0 && cut < 160) scroller.scrollTop -= cut;
    }
  }
  $effect(() => {
    const signature = entries.map(e => e.id + e.body_hash).join();
    if (signature !== previous) {
      previous = signature;
      const top = scroller?.scrollTop || 0;
      const shouldFollow = follow;
      tick().then(() => { settle(shouldFollow, top); requestAnimationFrame(() => settle(shouldFollow, top)); });
    }
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex (The scrollable reading region must be reachable for keyboard scrolling.) -->
<section class="conversation" role="log" aria-live="off" aria-label={channel === 'story' ? 'Story conversation' : 'Director conversation'} tabindex="0" bind:this={scroller} onscroll={remember}>
  {#if entries.length === 0}
    <div class="empty-reader">
      <h2>{channel === 'story' ? 'A story begins with a possibility.' : 'Room to shape the story.'}</h2>
      <p>{channel === 'story' ? 'Share a world, a character, or a first action with your writer. Your conversation will unfold here.' : 'Discuss ideas, preferences, imports, revisions, or Undo with the writer. Discussion does not automatically advance the fiction.'}</p>
    </div>
  {:else}
    {#each entries as entry (entry.id)}<ProseEntry {entry} {channel} {assets} change={changes?.[entry.id] || 'same'} />{/each}
  {/if}
</section>
