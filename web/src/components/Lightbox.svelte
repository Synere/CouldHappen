<script>
  /** @type {{src:string,alt:string,onclose:()=>void}} */
  let { src, alt, onclose } = $props();
  /** @type {HTMLButtonElement|undefined} */
  let closeButton;
  $effect(() => { closeButton?.focus(); });
  /** @param {KeyboardEvent} event */
  function keydown(event) {
    if (event.key === 'Escape') { event.stopPropagation(); onclose(); }
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions (Escape and the close button are the keyboard routes; the scrim click is a pointer convenience.) -->
<div class="lightbox" role="dialog" aria-modal="true" aria-label={alt || 'Picture'} tabindex="-1" onkeydown={keydown} onclick={event => { if (event.target === event.currentTarget) onclose(); }}>
  <button type="button" class="lightbox-close" bind:this={closeButton} aria-label="Close picture" onclick={onclose}>
    <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false"><path d="M3 3l10 10M13 3L3 13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
  </button>
  <figure>
    <img {src} {alt} />
    {#if alt}<figcaption>{alt}</figcaption>{/if}
  </figure>
</div>
