---
name: CouldHappen
description: A local fiction reading room with a petrol shell, saffron events, and serif prose.
colors:
  petrol: "#11515c"
  petrol-deep: "#083740"
  saffron: "#f2b51d"
  saffron-deep: "#dda20b"
  ink: "#142e34"
  muted: "#48626a"
  line: "#b2cdd2"
  line-soft: "#cfdfe2"
  reading: "#edf5f6"
  surface: "#f9fcfc"
  panel: "#e6f1f3"
  panel-deep: "#dfecee"
  cast-surface: "#e9f3f4"
  on-petrol: "#ffffff"
  on-saffron: "#11272c"
  focus: "#0a4c57"
  focus-on-petrol: "#ffdd87"
  link: "#0c5b68"
  selection: "#f2cb67"
  warning-bg: "#fff3cd"
  warning-border: "#bf8f1f"
  warning-ink: "#574111"
  recovery-bg: "#e1eef0"
  recovery-border: "#a9c6cb"
  recovery-ink: "#203d43"
  placeholder: "#5b7076"
  disabled-bg: "#cfdee1"
  input-surface: "#fdfefe"
  input-line: "#9cb9bf"
  input-line-hover: "#789aa1"
typography:
  display:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "clamp(1.6rem, 2.6vw, 2.4rem)"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "clamp(1.9rem, 3vw, 2.7rem)"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "1.4rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "clamp(1.16rem, 1.65vw, 1.55rem)"
    fontWeight: 400
    lineHeight: 1.58
    letterSpacing: "0em"
  label:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0em"
  control:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0em"
  caption:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: "0em"
rounded:
  xs: "3px"
  sm: "6px"
  control: "7px"
  prose: "9px"
  panel: "10px"
components:
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.on-petrol}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0.55rem 1.15rem"
    height: "44px"
  tab-active:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.on-saffron}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0.55rem 1.15rem"
    height: "44px"
  send:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0.6rem 1.35rem"
    height: "44px"
  send-hover:
    backgroundColor: "{colors.saffron-deep}"
  send-disabled:
    backgroundColor: "{colors.disabled-bg}"
    textColor: "{colors.muted}"
  connecting-button:
    backgroundColor: "{colors.petrol}"
    textColor: "{colors.on-petrol}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0.55rem 1.25rem"
    height: "44px"
  composer:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "0.9rem 1.15rem 1rem"
  composer-input:
    backgroundColor: "{colors.input-surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0.7rem 0.85rem"
  prose-entry:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.prose}"
    padding: "0.9rem 1.6rem"
  role-label-writer:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0.22rem 0.95rem"
  role-label-human:
    backgroundColor: "{colors.petrol}"
    textColor: "{colors.on-petrol}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0.22rem 0.95rem"
  cast-frame:
    backgroundColor: "{colors.reading}"
    rounded: "{rounded.panel}"
  cast-head:
    backgroundColor: "{colors.petrol}"
    textColor: "{colors.on-petrol}"
    typography: "{typography.title}"
    padding: "0.8rem 1.25rem"
  character-entry:
    backgroundColor: "{colors.reading}"
    textColor: "{colors.ink}"
    padding: "1.15rem 1.25rem 1.35rem"
  status-warning:
    backgroundColor: "{colors.warning-bg}"
    textColor: "{colors.warning-ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.sm}"
    padding: "0.65rem 1rem"
  status-recovery:
    backgroundColor: "{colors.recovery-bg}"
    textColor: "{colors.recovery-ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.sm}"
    padding: "0.65rem 1rem"
---

# Design System: CouldHappen

## Overview

**Creative North Star: "The Woven Reading Room"**

CouldHappen is a reading room built inside a petrol shell. The fiction gets a pale, cool page; the cast and controls sit at a working edge. The interface is deliberately quiet around the prose: no avatar feed, no card dashboard, no permanent app chrome competing with the sentence the visitor is reading. Petrol carries structure. Saffron marks the event—the active channel, the send action, the writer's side of a role change.

The "woven" move is the role rule: a paired petrol/saffron 3px hairline with a two-diamond interlace at the 62% split, its label chip docked at the left. It appears at every role change, and the same split returns, shortened, in empty states. Serif type is reserved for fiction, names, and headings; sans type handles controls, labels, and status. Depth is mostly drawn: 1px hairlines and tonal panels, with soft petrol-tinted shadows only for floating notices and the narrow-screen cast drawer.

The system assumes a local, trusted workspace that may legitimately be empty. Public story/director logs start with no entries, the cast starts with no characters, and portraits appear only when the writer discloses an asset. An initial letter in the portrait field is the honest fallback; no portrait, scene, or biography is fabricated to fill the room. The comp's illustrative story and portraits are reference material, not product content.

**Key Characteristics:**
- Petrol shell (#11515c), saffron event color (#f2b51d), pale cool reading ground (#edf5f6), dark ink prose (#142e34).
- Self-hosted Reader Serif (Source Serif 4) for prose; Reader Sans (Source Sans 3) for controls and status.
- Two-column reading/cast topology: prose owns the flexible column, cast is a separate 25%-max frame; the cast becomes a drawer at 860px.
- A 3px petrol→saffron rule with two interlaced diamonds marks every role change.
- Flat tonal layering: 1px lines, tinted panels, and only four low-opacity petrol shadows.
- Real disclosed data only; honest empty, paused, blocked, and recovery states in ordinary text.
- 44px navigation/Send targets, a 40px cast close, a 3px focus ring, and a reduced-motion path.

## Colors

A cool petrol structure around a pale reading ground, with saffron reserved for the event and almost nowhere else.

### Primary
- **Petrol Shell** (#11515c): the topbar, cast header, human role labels, the first 62% of every role rule, blockquote rule, and the connecting-state action. It is the structural color; it is allowed to hold white text.
- **Deep Petrol** (#083740): hover on petrol actions and the tint source for shadows. Not a background for prose.

### Secondary
- **Saffron Event** (#f2b51d): the active channel tab, the Send button, the writer-side role label, and the last 38% of the role rule. It is an event, not a wash.
- **Deep Saffron** (#dda20b): Send hover and the pending-status dot. Selection uses the lighter saffron wash (#f2cb67) with ink text.

### Neutral
- **Reading Ink** (#142e34): prose, headings, labels on pale ground; on-saffron text is the darker #11272c.
- **Muted Slate** (#48626a): channel subtitles, cast descriptions, composer help, disposition and revision status.
- **Cool Reading Ground** (#edf5f6): the room; body and reader background.
- **Prose Leaf** (#f9fcfc): the prose card only; the cast frame interior stays on the Cool Reading Ground.
- **Composer Panel** (#e6f1f3): the composer shell, inline code, and pre blocks.
- **Portrait Field** (#dfecee): the empty portrait field behind the initial-letter fallback.
- **Cast Margin** (#e9f3f4): the separate cast column.
- **Hairline Blue** (#b2cdd2): structural 1px borders—cast column, cast frame, composer, and the reading-heading rule.
- **Soft Hairline** (#cfdfe2): prose card, character row dividers, and lighter separators.
- **On Petrol** (#ffffff): text on petrol.
- **Focus Petrol** (#0a4c57): the global 3px focus ring. On petrol surfaces the ring becomes **Saffron Focus** (#ffdd87).
- **Quiet Link** (#0c5b68): inline links in prose and supporting copy.
- **Input Leaf** (#fdfefe), **Input Hairline** (#9cb9bf), **Input Hairline Hover** (#789aa1), **Placeholder Slate** (#5b7076): the composer field.
- **Disabled Ground** (#cfdee1): disabled Send; its text stays Muted Slate.
- **Warning Wash / Rule / Ink** (#fff3cd / #bf8f1f / #574111): connection and validation errors only.
- **Recovery Wash / Rule / Ink** (#e1eef0 / #a9c6cb / #203d43): the paused / awaiting-direction status only.

**The Two-Accent Rule.** Petrol is structure; saffron is the event. Saffron appears on the active tab, the Send action, writer-side role labels, selection, and the second half of a rule—never as a full-panel background wash.

**The Honest Ground Rule.** The reading ground stays cool and pale. No warm cream paper, no full-bleed dark prose field. Prose sits on Prose Leaf inside the Cool Reading Ground; the cast gets its own tonal margin.

## Typography

**Display Font:** Reader Serif (self-hosted Source Serif 4; Georgia fallback)
**Body Font:** Reader Serif for prose; Reader Sans (self-hosted Source Sans 3; system-ui fallback) for controls
**Label Font:** Reader Sans

**Character:** A book page with municipal signage at its edge. The serif is set large and open for sustained reading; the sans is compact, weighted, and plain for labels, tabs, status, and help. There are no display sans faces, all-caps eyebrows, or letterspaced kickers.

### Hierarchy
- **Display** (600, clamp(1.6rem, 2.6vw, 2.4rem)/1.1, -0.015em): the CouldHappen wordmark only.
- **Headline** (600, clamp(1.9rem, 3vw, 2.7rem)/1.1, -0.015em): the channel heading (“The story” / “Director”). The empty-state heading drops to 400 weight and 1.25 line-height.
- **Title** (600, 1.4rem/1.2, -0.01em): character names; the Cast header is 1.45rem.
- **Body** (400, clamp(1.16rem, 1.65vw, 1.55rem)/1.58): all prose entries and Director notes, max 68ch. Markdown h2 is 1.25em; h3/h4 are 1.08em, both serif.
- **Label** (600, 0.95rem/1.2): role chips and entry labels.
- **Control** (600, 1.02–1.06rem/1.3): tab labels, composer label, and Send; the connecting action uses the 1rem base. Controls never shrink below 1rem on narrow screens.
- **Caption** (400, 0.88–0.9rem/1.35–1.45): dispositions, revision notices, composer help, and permission/pause status in the composer foot; Muted Slate.

**The Prose-Only Serif Rule.** Serif carries fiction, names, and headings. Sans carries controls, role labels, status, help, and cast descriptions. Never set a control or status line in serif; never set a prose paragraph in sans.

**The Measure Rule.** Prose stops at 68ch. Empty-state copy stops at 52ch; heading support stops at 62ch. A longer prose line is a layout defect, not a density choice.

## Layout

The app is a 100dvh flex column. A fixed-height petrol topbar (84px desktop, 112px at ≤860px) holds the wordmark, Story/Director tabs, and—on narrow screens—the Cast toggle. Below it, the workspace is a two-column grid: `minmax(0, 1fr)` for the reader and `minmax(280px, 25%)` for the cast. The reader column owns the remaining height; its heading is fixed, its conversation scrolls, and its composer stays at the base of the column rather than floating over the prose.

The reader column uses 1.15rem 1.75rem 1rem padding on desktop. The reading heading has a 1px Hairline Blue bottom border and 0 1.6rem 1.05rem padding; its subtitle is capped at 62ch. Conversation entries sit on a 1.25rem .2rem 1.5rem scroll region, each article separated by 1.9rem and a 0.3rem top pad. A 26px scroll fade (22px on narrow screens) blends the last line into the reading ground. The conversation keeps a 100px minimum height, disables overflow anchoring, and preserves its own scroll position.

Prose cards use 0.9rem 1.6rem internal padding and a 68ch measure; at ≤860px they tighten to 0.7rem 1rem and 1.2rem type. Long tokens wrap anywhere. The cast column is a tonal margin with a 1px left border, 1.35rem 1rem 2rem padding, and its own scroll. Its frame is clipped to a 10px radius so the petrol header sits flush.

The spacing rhythm is authored as literal rem steps, not a custom-property scale: roughly 0.45, 0.55, 0.7, 0.8, 0.9, 1, 1.15, 1.25, 1.35, 1.6, 1.75, and 2.4rem. Reuse the nearest established step rather than introducing a finer one.

At ≤860px the workspace becomes a single column. The topbar grows to 112px and wraps: the wordmark and Cast toggle share the first row, the two tabs take a full-width second row. The cast column disappears and returns as a fixed right drawer at `min(92%, 380px)`, with a petrol scrim (`rgba(8, 47, 55, .42)`) and a 10px-radius frame. At ≤420px the wordmark drops to 1.4rem, the textarea minimum height drops to 64px, the composer foot stacks, and Send becomes full width. The document floor is 280px and the layout was reviewed at 320px. Safe-area bottom insets are respected on the reader and drawer.

**The Reading Column Rule.** Prose owns the flexible column. The composer stays at its base; the cast stays in its own frame. Never interleave cast cards with entries, never turn the composer into a floating toolbar, and never let permanent dashboard chrome take the first viewport.

**The One Scroll Rule.** The page itself does not scroll. The conversation and the cast column scroll independently, each with its own remembered position; the narrow-screen drawer scrolls as one surface.

## Elevation & Depth

The system is flat by default and tonal by construction. Depth comes from 1px Hairline Blue / Soft Hairline boundaries, the shift from Cool Reading Ground to Prose Leaf or Composer Panel, and the cast's tonal margin. There is no elevation stack and no shadow on tabs, buttons, prose cards, or the cast frame.

### Shadow Vocabulary
- **Banner ambient** (`0 6px 14px -12px rgba(8, 55, 64, .55)`): connection errors and recovery banners only.
- **Skip-link lift** (`0 6px 18px -10px rgba(8, 55, 64, .55)`): the focused skip link.
- **Composer lift** (`0 10px 28px -24px rgba(8, 55, 64, .55)`): the composer shell's quiet separation from the reading ground.
- **Drawer cast** (`-28px 0 70px -38px rgba(8, 55, 64, .7)`): the narrow-screen cast drawer.

**The Hairline-First Rule.** Boundaries are lines, not shadows. If a boundary needs emphasis, change the 1px line or the tonal panel; do not add elevation.

**The Tinted Shadow Rule.** Any shadow is petrol-tinted (#083740) with a large negative spread and alpha at or below .7. No gray or black drop shadows.

## Shapes

Corners are quiet and small. Inline code uses 3px; role chips, inline pre, error banners, and the skip link use 6px; buttons and the composer textarea use 7px; prose cards use 9px; the composer shell and cast frame use 10px. Nothing exceeds 10px. There are no pills, no 24px blobs, and no mixed corner languages.

Borders are consistently 1px except the role rules, which are 3px. The signature silhouette is the interlaced pair of 16×18 diamonds inside a 34×22 knot: the saffron diamond sits left, the petrol diamond right, both filled with the reading ground and stroked at 2.6. The role label is a small 6px chip docked on the left of the rule; the thread runs to the right edge. Portrait fields are 4:3, clipped to 6px, with `object-fit: contain`; the fallback is a single serif initial in Portrait Field.

**The Quiet Corner Rule.** Stay at or below 10px. Controls are 6–7px, prose 9px, panels 10px. A pill button or a larger radius is a different world.

## Components

### Topbar and Navigation
A petrol band, 84px tall, with the serif wordmark separated from the tabs by a 1px white-at-40% rule. Tabs are transparent sans controls with 44px minimum height, 0.55rem 1.15rem padding, and 0.18s background/color transitions. Hover adds `rgba(255,255,255,.1)`; the active tab becomes Saffron Event with #11272c text and `aria-current="page"`. Focus uses the Saffron Focus ring. At ≤860px the bar wraps to 112px, the wordmark divider disappears, and the Cast toggle appears with a 1px white-at-38% border. The toggle carries `aria-expanded` and `aria-controls`.

### Buttons
- **Shape:** 7px radius, 1px transparent border, 600 sans weight, `0.55rem 1.25rem` base padding.
- **Send (primary action):** Saffron Event ground, Reading Ink text, 44px minimum height, `0.6rem 1.35rem` padding. Hover deepens to Deep Saffron; disabled becomes Disabled Ground with Muted Slate text and no pointer.
- **Connecting action:** Petrol ground, white text; hover Deep Petrol.
- **Feedback:** `:active` applies `filter: brightness(.94)`; focus is the 3px Focus Petrol ring at 3px offset. There is no shadow and no transform.

### Composer
A Composer Panel shell with a 1px Hairline Blue border, 10px radius, `0.9rem 1.15rem 1rem` padding, and the Composer lift shadow. The label is 600 1.05rem sans. The textarea is Input Leaf with a 1px Input Hairline, 7px radius, `0.7rem 0.85rem` padding, 1.05rem/1.45 sans, a 76px minimum height (72px narrow, 64px at ≤420px), and a 26vh maximum. Border shifts to Input Hairline Hover; focus uses the global ring; placeholder is Placeholder Slate. The foot holds a 0.9rem muted status line (max 62ch) and Send. Status copy is state-specific: connection interrupted and draft retained; permission reason; story paused until direction is interpreted; saved before writer handling; or the current save notice. Send disables while sending, disconnected, unauthorized, or empty. Ctrl/Cmd+Enter submits. Drafts, pending save identity, and scroll anchors persist in sessionStorage; a save failure retains the text and either offers “Retry same save” or reports an uncertain receipt.

### Prose Entry and Role Rule
Each entry begins with the signature rule: a 1.4rem petrol lead, a 6px role chip, and a flexible 3px thread that runs petrol to 62% then saffron to 100%; the 34×22 two-diamond knot is centered on the split. Story labels are “Your contribution” (petrol chip, white text) and “Writer continuation” (saffron chip, ink text); Director labels are “You · Director” and “Writer · Director”. The prose card below is Prose Leaf with a 1px Soft Hairline, 9px radius, and serif body. Human entries may carry a 0.88rem disposition line with a 6px dot: Deep Saffron for pending, petrol for addressed, Hairline Blue for deferred. Revised passages carry a hollow petrol dot and “Passage updated”; they do not re-reveal. Entry identity stays stable across polls, and a changed body hash swaps the prose without replaying the reveal.

### Cast Panel
A separate `<aside>` with a 1px Hairline Blue left border, Cast Margin ground, and its own scroll. Inside, a 10px clipped frame holds a petrol header (serif 1.45rem “Cast”, white) and character rows divided by Soft Hairline. Each row has a 4:3 portrait field (Portrait Field ground, 6px radius, contain fit, single serif initial fallback) followed by a 1.4rem serif name, `.01em` tightening, and a 1rem/1.5 muted description. No cast data means one honest empty sentence, not a placeholder character. At ≤860px the panel becomes a fixed right drawer with a scrim; focus moves to its Close control, the background leaves the tab order with `inert`, focus returns to the toggle on close, and Escape dismisses it.

### State Language
- **Empty reader:** a 78×3 split rule (56% petrol / 44% saffron), a 400-weight serif headline at 1.9–2.7rem, and 1.08rem/1.65 muted copy capped at 52ch. The story and Director states have different honest copy; neither implies stored content.
- **Connecting:** centered, max 48rem, 12vh top padding, serif 1.8–2.6rem headline, muted status, and a petrol “Try again” action.
- **Error:** Warning Wash ground, Warning Rule border, Warning Ink text, 6px radius, `role="alert"`.
- **Recovery / awaiting direction:** Recovery Wash ground, Recovery Rule border, Recovery Ink text, `role="status"`. Story and Director get different next-step copy.
- **Blocked composer:** status text (“Saving paused while the writer composes.”), disabled Send, retained draft—never a spinner, skeleton, or disabled-looking whole page.

**The Reveal-Only-New Rule.** Only a newly arrived writer passage reveals, at 120 characters per second (0.12 chars/ms), capped at 5 seconds. Initial history and revised passages appear whole. The reveal walks sanitized text nodes only, never partial HTML. `prefers-reduced-motion` makes every animation and transition instant.

**The Real-Data Rule.** Public logs and cast may be empty. Portraits, biographies, and scene prose appear only when the writer discloses them; the fallback initial and the empty sentences are the correct visual states. Never fabricate content to make a composition look full.

### Accessibility
The reading region is a labelled `role="log"` with `aria-live="off"` and `tabindex="0"` so it can be scrolled by keyboard without announcing every poll. Focus is always visible: 3px Focus Petrol at 3px offset, Saffron Focus on petrol surfaces, and an inset offset on the reading region. The skip link is first in the tab order. Tabs expose `aria-current`, the Cast toggle exposes `aria-expanded`/`aria-controls`, and the drawer is a `dialog` with `aria-modal`, background `inert`, focus moved to Close, Escape to dismiss, and focus returned to the toggle. Errors use `role="alert"`; connecting, recovery, and save status use `role="status"`. Status is never color-only: every dot has a text label. The textarea has a visible label and `aria-describedby` save status. Primary actions stay at 44px; the cast close is a 40px square inside the petrol header. The document holds at 280px and was reviewed at 320px, and `prefers-reduced-motion` removes the reveal and every transition.

### Motion Grammar
State changes are small and functional: 0.18s ease on tab background/color, 0.16s ease on Send and textarea borders, and `brightness(.94)` on press. New writer prose uses the character reveal; nothing else animates. Reading position is preserved per channel; the reader follows only when already within 80px of the bottom, snaps a newly cut entry into view when less than 160px is clipped, and starts a long new passage from its top rather than its end. Under reduced motion, the reveal is skipped entirely and scroll behavior is immediate.

## Do's and Don'ts

### Do:
- **Do** use petrol for shell/structure and saffron for the active channel, Send, writer-side labels, selection, and the rule's second half.
- **Do** keep prose on Prose Leaf inside the Cool Reading Ground at a 68ch maximum.
- **Do** mark every role change with the paired 3px rule and two-diamond knot at the 62% split.
- **Do** keep the cast in its own framed column; use the fixed drawer and scrim at ≤860px.
- **Do** prefer 1px Hairline Blue / Soft Hairline boundaries and tonal panels; reserve the four tinted shadows for floating notices and the drawer.
- **Do** set fiction, names, and headings in Reader Serif; controls, labels, status, and descriptions in Reader Sans.
- **Do** render only writer-disclosed data and use the honest empty, fallback, blocked, and recovery states.
- **Do** keep 44px primary action targets, the labelled 40px cast close, the 3px focus ring, the skip link, the 280px floor, and the reduced-motion path.

### Don't:
- **Don't** introduce a third accent or wash a whole panel in saffron.
- **Don't** add a card feed, avatar row, or permanent dashboard chrome; don't move cast content into the reading column.
- **Don't** use pill buttons, radii above 10px, hard offset shadows, or glyph icons.
- **Don't** add all-caps eyebrows, letterspaced kickers, or display sans faces.
- **Don't** fabricate portraits, cast entries, scene prose, or controls that the workspace does not actually supply.
- **Don't** animate initial history or revised passages; reveal only new writer prose.
- **Don't** communicate status by color alone, and don't substitute spinners or skeletons for plain state text.
- **Don't** let prose exceed 68ch or set controls/status in serif.
