---
name: CouldHappen
description: A dim petrol reading room with saffron events, hairline rules and serif prose in a centred column.
colors:
  petrol: "#4fa3ae"
  petrol-deep: "#2c7782"
  saffron: "#f2b51d"
  saffron-deep: "#dda20b"
  ink: "#e2eef0"
  muted: "#8fabb0"
  line: "#1e434a"
  line-soft: "#133239"
  reading: "#061a1e"
  surface: "#0a2227"
  panel: "#0d2a30"
  panel-deep: "#113339"
  cast-bg: "#04151a"
  link: "#7fc4cd"
  on-saffron: "#11272c"
typography:
  wordmark:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "1.18rem"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "0.34em"
  headline:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "clamp(1.7rem, 2.7vw, 2.4rem)"
    fontWeight: 400
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "1.32rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "0.01em"
  body:
    fontFamily: "Reader Serif, Source Serif 4, Georgia, serif"
    fontSize: "clamp(1.13rem, 1.32vw, 1.34rem)"
    fontWeight: 400
    lineHeight: 1.74
    letterSpacing: "0.002em"
  label:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.22em"
  control:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "0.76rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.18em"
  caption:
    fontFamily: "Reader Sans, Source Sans 3, system-ui, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.01em"
rounded:
  all: "2px"
components:
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    height: "44px"
  tab-active:
    textColor: "{colors.saffron}"
    borderBottom: "2px {colors.saffron}"
  send:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.on-saffron}"
    typography: "{typography.control}"
    rounded: "{rounded.all}"
    height: "42px"
  send-hover:
    backgroundColor: "{colors.saffron-deep}"
  send-disabled:
    backgroundColor: "transparent"
    borderColor: "{colors.line}"
  composer-input:
    backgroundColor: "mix(reading 70%, black)"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.all}"
  role-label-writer:
    textColor: "mix(saffron 72%, ink)"
    typography: "{typography.label}"
  role-label-human:
    textColor: "mix(petrol 80%, ink)"
    typography: "{typography.label}"
---

# Design System: CouldHappen

<!-- dev-only -->
The decision behind this design is [ADR-6](docs/decisions/ADR-6-dark-petrol-reader.md).
<!-- /dev-only -->

## Overview

**Creative North Star: "The Dim Reading Room"**

CouldHappen is a room you read in at night. The page is a near-black petrol; the prose is pale cool ink set large in a centred column; the cast sits in a darker rail at the side. There are no prose cards, no chips, no panels around the sentence being read. Petrol carries structure. Saffron marks the event: the active channel, Send, the writer's side of a role change, the drop cap.

A role change is a hairline: a short coloured lead, a small uppercase label ("Writer" in saffron, "You" in petrol), and a 1px thread to the edge. The player's own words sit indented behind a petrol rule, a step quieter than the writer's prose. The first letter of each writer passage is a saffron drop cap.

When a story turns on a theme with a backdrop (the scene-images package), the newest scene picture lies behind everything, blurred and faint, and its colour can tint the structure. Without one, a soft petrol glow at the top of the room and a faint grain keep the ground from looking flat.

The system assumes a local, trusted workspace that may legitimately be empty. Logs and cast start empty; portraits appear only when the writer discloses an asset. A serif initial is the honest portrait fallback; nothing is fabricated to fill the room.

**Key characteristics:**
- Near-black petrol ground (#061a1e), pale cool ink (#e2eef0), petrol structure (#4fa3ae), saffron event (#f2b51d).
- Self-hosted Reader Serif (Source Serif 4) for prose, names and headings; Reader Sans (Source Sans 3) for labels and controls, set small, uppercase and letterspaced.
- A centred 46rem reading column with a 63ch measure; the cast is a separate rail (300px to 27%) that becomes a drawer at 980px.
- Hairlines, not boxes. Corners are 2px.
- Every colour is a variable. A sheet theme can replace the fourteen base colours and everything else follows.

## Colors

### Base colours (themable)

These fourteen are the variables a sheet theme may replace (`accent` maps to `--petrol`, `highlight` to `--saffron`, `side-bg` to `--cast-bg`; the rest keep their names).

- **Petrol** (`--petrol`, #4fa3ae): structure. Section headings (The story, Cast), the human role label and lead, links' family, the focus border on the composer, the top glow.
- **Deep Petrol** (`--petrol-deep`, #2c7782): the rule beside the player's own words and blockquotes, hover borders.
- **Saffron** (`--saffron`, #f2b51d): the event. Active tab, Send, the writer label and lead, the drop cap, sheet values, the pending dot's family.
- **Deep Saffron** (`--saffron-deep`, #dda20b): Send hover, the pending dot, the error rule.
- **Ink** (`--ink`, #e2eef0): headings and control text; prose is a slightly softened ink.
- **Muted** (`--muted`, #8fabb0): channel subtitles, captions, status lines, dispositions, cast descriptions.
- **Line** (`--line`, #1e434a) and **Soft Line** (`--line-soft`, #133239): every boundary.
- **Reading** (`--reading`, #061a1e): the room.
- **Surface**, **Panel**, **Deep Panel** (#0a2227, #0d2a30, #113339): hover grounds, inline code, the error and recovery notices.
- **Cast rail** (`--cast-bg`, #04151a): the cast column and drawer.
- **Link** (`--link`, #7fc4cd): links and the portrait request.

### Mixed tones

Defined in `web/src/styles.css` with `color-mix()` from the base colours, so they follow a theme: prose ink (ink 90% into reading), bright (headings, emphasis), quiet (the player's prose, blockquotes), faint (disabled text, the portrait initial), the two role-label colours, the focus ring (saffron toward white), the input ground and line, the topbar chrome, and the scrim. Only the text on saffron (#11272c) is fixed.

**The Two-Accent Rule.** Petrol is structure; saffron is the event. Saffron appears on the active tab, Send, the writer's label and lead, the drop cap and sheet values. It is never a wash over a panel.

**The Contrast Floor.** Prose (about 12:1), labels (7:1 or more), muted text (about 7:1) and Send's label (8:1) clear WCAG AA on the reading ground. The player's indented prose is the quietest body text and stays above 5:1. A theme must be checked in a real browser before it is kept.

## Typography

**Character:** a book in a dim room. The serif is large and loose for long reading (1.74 line height). Everything that is not fiction is small Reader Sans, uppercase and letterspaced, so it recedes.

- **Wordmark** (400 serif, 1.18rem, 0.34em tracking, uppercase): the topbar name. A theme name replaces "CouldHappen" when scene-images sets one.
- **Headline** (400 serif, 1.7–2.4rem): empty-state and connecting headlines.
- **Title** (400 serif, 1.32rem): character names; the sheet title is 1.15rem.
- **Body** (400 serif, clamp(1.13rem, 1.32vw, 1.34rem)/1.74): prose, max 63ch. Markdown headings are 600 serif at 1.16em and 1.04em. The composer textarea is serif at 1rem/1.6, so the player writes in the same voice they read.
- **Label** (600 sans, 0.7rem, 0.22em tracking, uppercase): role labels, the composer label, section headings (0.74rem, 0.26em).
- **Control** (600 sans, 0.72–0.78rem, 0.12–0.18em tracking, uppercase): tabs, Send, quick actions, the portrait request.
- **Caption** (400 sans, 0.72–0.84rem): status, dispositions (uppercase), captions (italic).

**The Prose-Only Serif Rule.** Serif carries fiction, names, headlines and the composer field. Sans carries controls, labels and status.

**The Measure Rule.** Prose stops at 63ch inside a 46rem column; empty-state copy at 50ch.

## Layout

The app is a 100dvh flex column over a fixed backdrop layer. A 66px topbar (the chrome tone, a 1px bottom line) holds the wordmark, a divider, and the Story / Director tabs as underlined text. Below it the workspace is a two-column grid: `minmax(0, 1fr)` for the reader and `minmax(300px, 27%)` for the cast rail.

The reader column has a small uppercase heading row (petrol title, muted subtitle), the scrolling conversation, and the composer at its base. Heading, entries and composer all centre on the same 46rem column (`max(2.5rem, (100% - 46rem) / 2)` side padding). Fades at the top (22px) and bottom (34px) of the scroll region blend lines into the ground. Entries are 2.4rem apart.

The composer is not a box: a 1px top line over a gradient into the input ground, the label, the textarea, and a foot with the status line on the left and quick actions and Send on the right.

At ≤980px the workspace becomes one column. The topbar grows to 108px and wraps; the tabs take their own row and the Cast toggle appears. The cast becomes a fixed right drawer at `min(92%, 380px)` over a scrim. At ≤440px the composer foot stacks and Send fills the width. The document floor is 280px.

**The Reading Column Rule.** Prose owns the centre. The composer stays at the base; the cast stays in its rail. No floating toolbars, no dashboard chrome.

**The One Scroll Rule.** The page does not scroll. The conversation and the cast rail scroll on their own, each keeping its position.

## Elevation & Depth

Flat. Depth comes from the darker chrome and cast rail, 1px lines, and the backdrop layer behind everything. The only shadows are the inset vignette on portraits and the narrow-screen drawer's cast shadow.

**The Hairline-First Rule.** Boundaries are lines. If a boundary needs emphasis, change the line, not the elevation.

## Shapes

Every corner is 2px: buttons, the textarea, code, notices, portraits, picture plates. Borders are 1px; the active tab's underline is 2px. Portraits are 4:3 with `object-fit: cover` and a soft inset vignette; the fallback is a single serif initial in the faint tone.

## Components

### Topbar and navigation
The chrome band with the uppercase serif wordmark, a 1px divider, and tabs as uppercase sans text with 44px targets. Inactive tabs are muted and brighten to ink on hover; the active tab is saffron with a 2px saffron underline and `aria-current="page"`.

### Buttons
- **Send:** saffron ground, dark text, uppercase control type, 42px tall. Hover deepens to deep saffron. Disabled becomes a transparent outline with faint text.
- **Quick actions** (`.action`, added by scene-images): outlined, petrol-tinted text, beside Send inside `.composer-actions`.
- **Portrait request** (`.ask`): outlined, link colour, uppercase, quiet.
- **Feedback:** `:active` moves a button down 1px; focus is a 2px ring in the focus tone at 3px offset.

### Composer
Label "What do you do?" in the human label colour; a serif textarea on the input ground with a 1px input line that turns petrol on focus; an italic muted placeholder. The status line is state-specific (connection interrupted and draft retained; permission reason; paused until direction is interpreted; saved before writer handling; the current notice). Send disables while sending, disconnected, unauthorized or empty. Ctrl/Cmd+Enter submits. Drafts and pending saves persist in sessionStorage.

### Prose entry and role rule
Each entry starts with the rule: a 26px lead (saffron for the writer, petrol for the player), the label ("Writer" or "You"), and a 1px thread in the line colour. Writer prose follows in the body serif with a saffron drop cap. The player's prose is indented 1.15rem behind a deep-petrol rule, in the quiet tone, with no drop cap. Human entries carry an uppercase disposition line with a 5px dot: deep saffron pending, petrol addressed, line deferred. Revised passages carry a hollow petrol square and "Passage updated" and do not re-reveal. Pictures attached to a passage sit below it as a 3:2 plate with an italic caption and open in a lightbox.

### Cast rail
A darker `<aside>` with a 1px left line and its own scroll. The heading is an uppercase petrol label over a line. Each character is a 4:3 portrait, a serif name and a muted description, divided by soft lines. No cast data means one italic empty sentence. Below the cast, the sheet panel (rpg-mechanics) uses the same language: a serif title, uppercase group labels, rows with dotted dividers and saffron values. At ≤980px the rail becomes a drawer: focus moves to Close, the background is `inert`, Escape dismisses, and focus returns to the toggle.

### State language
- **Empty reader:** a 34px petrol-to-saffron hairline, a serif headline, muted copy at 50ch. Story and Director have different honest copy.
- **Connecting:** centred serif headline, muted status, a saffron "Try again".
- **Error:** a saffron-tinted notice with a deep-saffron rule, `role="alert"`.
- **Recovery / awaiting direction:** a panel-ground notice with a deep-petrol rule, `role="status"`.
- **Blocked composer:** status text and a disabled Send; the draft is kept. Never a spinner or skeleton.

**The Reveal-Only-New Rule.** Only a newly arrived writer passage reveals, at 120 characters per second, capped at 5 seconds. History and revised passages appear whole. `prefers-reduced-motion` makes every animation and transition instant.

**The Real-Data Rule.** Logs and cast may be empty. Portraits, biographies and prose appear only when the writer discloses them.

### Accessibility
The reading region is a labelled `role="log"` with `aria-live="off"` and `tabindex="0"`. Focus is always visible. The skip link is first in the tab order. Tabs expose `aria-current`; the Cast toggle exposes `aria-expanded` and `aria-controls`; the drawer is modal with background `inert`. Errors use `role="alert"`, status lines `role="status"`. Status is never colour-only: every dot has a text label. Tabs keep 44px targets, Send and quick actions 42px, the cast close 40px. The document holds at 280px.

### Motion
0.16s transitions on Send, quick actions and the textarea border; a 1px press. New writer prose uses the character reveal; nothing else animates. Reading position is kept per channel; the reader follows only when already near the bottom.

### Themes and the backdrop
The stock reader needs no theme. A sheet theme (scene-images) may replace the fourteen base colours, set `data-scheme` to `light` or `dark`, name the room (the wordmark and tab title), and turn on the backdrop: the newest scene picture painted behind everything at 34% opacity, blurred 26px and darkened. With the backdrop on, the petrol accent may be sampled from that picture, so the structure takes the scene's colour. A warm, dim example theme is in the scene-images package.

## Do's and Don'ts

### Do:
- **Do** keep petrol for structure and saffron for the event.
- **Do** keep prose in the centred column at 63ch, with no card around it.
- **Do** mark every role change with the hairline rule and its small uppercase label.
- **Do** take every colour from a variable, so a theme recolours the whole room.
- **Do** keep 2px corners, 1px lines, and the labelled, keyboard-reachable controls.
- **Do** render only writer-disclosed data and the honest empty and recovery states.

### Don't:
- **Don't** put prose in boxes or cards, or add a feed, avatar row or dashboard chrome.
- **Don't** add a third accent or wash a panel in saffron.
- **Don't** hard-code a colour in the stylesheet that a theme cannot reach (the text on saffron is the one exception).
- **Don't** use large radii, pills, or drop shadows beyond the drawer.
- **Don't** animate history or revised passages.
- **Don't** let prose exceed 63ch, or set controls and status in serif.
