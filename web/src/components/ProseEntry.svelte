<script>
  import { markdown } from '../lib/markdown.js';
  import { reveal } from '../lib/reveal.js';
  /** @type {{entry:import('../lib/session.js').Entry,change?:string,channel:import('../lib/session.js').Channel}} */
  let { entry, change = 'initial', channel } = $props();
  const html = $derived(markdown(entry.body));
  /** @param {HTMLElement} node */
  function animate(node) { return reveal(node, change === 'new' && entry.role === 'writer'); }
</script>

<article class:human={entry.role === 'human'} data-entry-id={entry.id}>
  <div class="entry-rule">
    <i class="lead" aria-hidden="true"></i>
    <span>{entry.role === 'human' ? (channel === 'story' ? 'Your contribution' : 'You · Director') : (channel === 'story' ? 'Writer continuation' : 'Writer · Director')}</span>
    <i class="thread" aria-hidden="true">
      <svg class="knot" viewBox="0 0 34 22" focusable="false" aria-hidden="true">
        <path d="M9 2 17 11 9 20 1 11Z" fill="var(--reading)" stroke="var(--saffron)" stroke-width="2.6" stroke-linejoin="round" />
        <path d="M17 2 25 11 17 20 9 11Z" fill="var(--reading)" stroke="var(--petrol)" stroke-width="2.6" stroke-linejoin="round" />
      </svg>
    </i>
  </div>
  {#if change === 'revised'}<small class="revision">Passage updated</small>{/if}
  {#key entry.body_hash}
    <div class="prose" {@attach animate}>{@html html}</div>
  {/key}
  {#if entry.role === 'human'}<small class="disposition {entry.status}">{entry.status === 'pending' ? 'Saved · awaiting writer handling' : entry.status === 'deferred' ? 'Deferred by writer' : 'Addressed by writer'}</small>{/if}
</article>
