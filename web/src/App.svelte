<script>
  import { onMount, tick } from 'svelte';
  import { poll, submit, SaveError } from './lib/api.js';
  import { Session } from './lib/session.js';
  import Conversation from './components/Conversation.svelte';
  import Composer from './components/Composer.svelte';
  import CastPanel from './components/CastPanel.svelte';
  /** @type {import('./lib/session.js').Snapshot|null} */
  let snapshot = $state.raw(null);
  /** @type {import('./lib/session.js').Changes} */
  let changes = $state.raw({story: {}, director: {}});
  /** @type {import('./lib/session.js').Channel} */
  let channel = $state('story');
  let castOpen = $state(false);
  /** @type {HTMLButtonElement|undefined} */
  let castToggle;
  let error = $state('');
  let epoch = $state(0);
  const session = new Session(sessionStorage);
  session.notify = () => { epoch += 1; };
  /** @type {ReturnType<typeof poll>|undefined} */
  let transport;
  function refresh() { transport?.refresh(); }
  /** @type {Record<string,string>} */
  let portraitNotes = $state({});
  /** One click saves one Director request; it never retries by itself, so a doubtful receipt is left for the player to check.
   * @param {import('./lib/session.js').Character} character */
  async function requestPortrait(character) {
    if (!snapshot || portraitNotes[character.id] === 'Saving…') return;
    portraitNotes = { ...portraitNotes, [character.id]: 'Saving…' };
    try {
      await submit({ schema_version: 1, workspace_id: snapshot.workspace_id, generation: snapshot.generation, channel: 'director',
        id: crypto.randomUUID(), body: `Make a portrait for ${character.name} (cast id ${character.id}).` }, new AbortController().signal);
      portraitNotes = { ...portraitNotes, [character.id]: 'Requested. Your writer will answer in Director.' };
    } catch (failure) {
      const uncertain = !(failure instanceof SaveError) || failure.status >= 500;
      portraitNotes = { ...portraitNotes, [character.id]: uncertain ? 'Not sure it saved. Check the Director channel before asking again.' : (failure instanceof Error ? failure.message : 'Could not save the request.') };
    } finally { refresh(); }
  }
  function closeCast() { castOpen = false; tick().then(() => castToggle?.focus()); }
  onMount(() => {
    transport = poll(next => { changes = session.receive(next); snapshot = next; }, message => { error = message; });
    return () => transport?.close();
  });
</script>

<svelte:window ononline={refresh} onfocus={refresh} onkeydown={(event) => { if (event.key === 'Escape' && castOpen) closeCast(); }} />
<svelte:document onvisibilitychange={() => { if (!document.hidden) refresh(); }} />
<a class="skip-link" href="#reader" inert={castOpen}>Skip to conversation</a>
<header class="topbar" inert={castOpen}>
  <h1>CouldHappen</h1>
  <nav aria-label="Conversation">
    <button type="button" class:active={channel === 'story'} aria-current={channel === 'story' ? 'page' : undefined} onclick={() => { channel = 'story'; }}>Story</button>
    <button type="button" class:active={channel === 'director'} aria-current={channel === 'director' ? 'page' : undefined} onclick={() => { channel = 'director'; }}>Director</button>
  </nav>
  <button type="button" class="cast-toggle" bind:this={castToggle} aria-expanded={castOpen} aria-controls="cast-panel" onclick={() => { castOpen = !castOpen; }}>Cast</button>
</header>
{#if snapshot}
  <div class="workspace">
    <main id="reader" tabindex="-1" inert={castOpen}>
      <div class="reading-heading"><h2>{channel === 'story' ? 'The story' : 'Director'}</h2><p>{channel === 'story' ? 'A conversation with your writer' : 'Ideas, preferences, and direction'}</p></div>
      {#if error || snapshot.validation_error}<p class="connection-error" role="alert">{error || snapshot.validation_error}</p>{/if}
      {#if snapshot.work.mode === 'awaiting_director'}<p class="recovery-status" role="status">{channel === 'director' ? 'Awaiting your direction. Add a note below; the story stays paused until the writer interprets it.' : 'Awaiting Director direction. Open Director to discuss the next approach before the story continues.'}</p>{/if}
      {#key channel}
        <div class="reader-scroll">
          <Conversation entries={snapshot[channel]} changes={changes[channel]} {channel} {session} assets={snapshot.assets} />
          <div class="scroll-fade" aria-hidden="true"></div>
        </div>
        <Composer {channel} {snapshot} {session} {epoch} {refresh} connected={!error} />
      {/key}
    </main>
    <CastPanel cast={snapshot.cast} assets={snapshot.assets} open={castOpen} onclose={closeCast} canRequest={!!snapshot.cast.portrait_button && snapshot.permissions.director.allowed && !error} notes={portraitNotes} onrequest={requestPortrait} />
    {#if castOpen}<button type="button" class="cast-scrim" tabindex="-1" aria-label="Dismiss cast panel" onclick={closeCast}></button>{/if}
  </div>
{:else}
  <main class="connecting"><h2>Opening your workspace</h2><p role="status">{error || 'Reading saved conversations…'}</p><button onclick={refresh}>Try again</button></main>
{/if}
