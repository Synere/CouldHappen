<script>
  /** @type {{cast:{characters:import('../lib/session.js').Character[],portrait_button?:boolean},assets:Record<string,string>,open?:boolean,onclose?:()=>void,canRequest?:boolean,notes?:Record<string,string>,onrequest?:(character:import('../lib/session.js').Character)=>void}} */
  let { cast, assets, open = false, onclose = () => {}, canRequest = false, notes = {}, onrequest = () => {} } = $props();
  /** @type {HTMLButtonElement|undefined} */
  let closeButton;
  $effect(() => { if (open) closeButton?.focus(); });
  /** @param {Event} event */
  function loaded(event) {
    const image = event.currentTarget;
    if (image instanceof HTMLImageElement) image.parentElement?.classList.add('loaded');
  }
  /** @param {Event} event */
  function failed(event) {
    const image = event.currentTarget;
    if (image instanceof HTMLImageElement) image.hidden = true;
  }
</script>

<aside class:open class="cast" id="cast-panel" aria-label="Disclosed cast" role={open ? 'dialog' : 'complementary'} aria-modal={open ? 'true' : undefined}>
  <div class="cast-frame">
    <div class="cast-head">
      <h2>Cast</h2>
      <button type="button" class="cast-close" bind:this={closeButton} aria-label="Close cast" onclick={onclose}>
        <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false"><path d="M3 3l10 10M13 3L3 13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
      </button>
    </div>
    {#if cast.characters.length === 0}<p class="empty-cast">People will appear here as the story reveals them.</p>{/if}
    {#each cast.characters as character (character.id)}
      <section class="character">
        {#if character.portrait}
          {#key character.portrait}
            <div class="portrait-frame">
              <span class="portrait-fallback" aria-hidden="true">{character.name.trim().slice(0, 1).toUpperCase()}</span>
              <img src={'/api/assets/' + character.portrait.split('/').map(encodeURIComponent).join('/') + '?v=' + assets[character.portrait]} alt={'Portrait of ' + character.name} decoding="async" onload={loaded} onerror={failed} />
            </div>
          {/key}
        {/if}
        <h3>{character.name}</h3>
        {#if character.description}<p>{character.description}</p>{/if}
        {#if cast.portrait_button && character.id !== 'scene'}
          <div class="portrait-ask">
            <button type="button" class="ask" disabled={!canRequest || notes[character.id] === 'Saving…'} aria-describedby={'ask-note-' + character.id} onclick={() => onrequest(character)}>{character.portrait ? 'New portrait' : 'Make portrait'}<span class="visually-hidden"> for {character.name}</span></button>
            <small id={'ask-note-' + character.id} role="status">{notes[character.id] || (canRequest ? '' : 'Unavailable while saving is paused.')}</small>
          </div>
        {/if}
      </section>
    {/each}
  </div>
</aside>
