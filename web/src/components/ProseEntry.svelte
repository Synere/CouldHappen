<script>
  import { markdown, splitBody } from '../lib/markdown.js';
  import { reveal, firstReveal } from '../lib/reveal.js';
  import Lightbox from './Lightbox.svelte';
  /** @type {{entry:import('../lib/session.js').Entry,change?:string,channel:import('../lib/session.js').Channel,assets?:Record<string,string>}} */
  let { entry, change = 'initial', channel, assets = {} } = $props();
  const parts = $derived(splitBody(entry.body));
  const html = $derived(markdown(parts.text));
  const pictures = $derived(parts.pictures.filter(picture => assets[picture.name]));
  /** @type {{src:string,alt:string}|null} */
  let enlarged = $state(null);
  /** @type {HTMLElement|null} */
  let opener = null;
  /** @param {string} name */
  const source = name => '/api/assets/' + encodeURIComponent(name) + '?v=' + assets[name];
  /** @param {{alt:string,name:string}} picture @param {Event} event */
  function enlarge(picture, event) {
    opener = event.currentTarget instanceof HTMLElement ? event.currentTarget : null;
    enlarged = { src: source(picture.name), alt: picture.alt };
  }
  function shrink() { enlarged = null; opener?.focus(); }
  /** @param {HTMLElement} node */
  function animate(node) { return reveal(node, change === 'new' && entry.role === 'writer' && firstReveal(entry.id + ':' + entry.body_hash)); }
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
  {#each pictures as picture (picture.name)}
    <figure class="plate">
      <button type="button" class="plate-open" aria-label={'Enlarge picture' + (picture.alt ? ': ' + picture.alt : '')} onclick={event => enlarge(picture, event)}>
        <img src={source(picture.name)} alt={picture.alt} decoding="async" />
      </button>
      {#if picture.alt}<figcaption>{picture.alt}</figcaption>{/if}
    </figure>
  {/each}
  {#if enlarged}<Lightbox src={enlarged.src} alt={enlarged.alt} onclose={shrink} />{/if}
  {#if entry.role === 'human'}<small class="disposition {entry.status}">{entry.status === 'pending' ? 'Saved · awaiting writer handling' : entry.status === 'deferred' ? 'Deferred by writer' : 'Addressed by writer'}</small>{/if}
</article>
