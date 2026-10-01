# UI/UX Improvement Ideas

A backlog of possible UI/UX improvements for the WebSocket chat app. Items
marked **[done]** are implemented; the rest are a menu to pick from.

## Chat experience (biggest impact)

- **[done] Message timestamps** — shown under each bubble, with day dividers
  ("Today" / "Yesterday" / date).
- **[done] Message grouping** — consecutive messages from the same sender
  within a 5-minute window share one name label and sit with tighter
  spacing.
- **[done] Online users panel** — a header button (with a live count badge)
  opens a sheet listing everyone currently in the room, with gradient
  avatars and a "you" marker. Backed by a `users` list the server now
  includes on every roster/join/leave broadcast.
- **[done] Avatars** — initials in a gradient circle, reusing each user's
  existing hologram color. Shown beside incoming ("them") messages, once
  per grouped run; own messages skip the avatar as usual in chat UIs.
- **[done] Emoji picker and quick reactions** — a small always-visible
  reaction trigger on every bubble opens a 👍 ❤️ 😂 🎉 😮 picker. Reactions
  show as pill counts under the bubble, sync live to everyone in the room,
  and clicking your own reaction again removes it (toggle). Backed by an
  in-memory `message_id → {emoji: {usernames}}` store on the server —
  ephemeral like the rest of this app's state, wiped on restart.
- **[done] Links and formatting** — URLs (`http(s)://` and bare `www.`) are
  clickable, `` `code` `` renders inline and ``` ```blocks``` ``` as a
  `<pre>`, and the composer is now a Shift+Enter-for-newline textarea so
  real line breaks render as `<br>`. All user text is HTML-escaped first;
  the tags above are the only markup ever added, and only around already-
  escaped content.
- **[done] "Jump to latest" button** — if you've scrolled up and a new
  message from someone else arrives, a floating pill shows an unseen count
  instead of yanking your scroll position; your own sends still
  auto-scroll. Clicking it (or scrolling back down yourself) dismisses it.
- **[done] Unread badge and sound** — while the tab is in the background,
  incoming messages update the title to `(3) WebSocket Chat` and play a
  short synthesized chime (Web Audio, no audio file needed), with a
  persisted on/off toggle in the connection-log panel. Clears on refocus.

## Joining and leaving

- **[done] Better join screen** — recently-used rooms (persisted in
  localStorage) show as clickable chips, a 🎲 Random button generates a
  fun room name, and a live "N people already in #room" / "empty — you'll
  be first" preview updates as you type, sharing one fetch with the
  duplicate-name check below.
- **[done] Inline validation** — a soft, non-blocking "name already taken in
  this room" warning while typing, backed by a new read-only
  `GET /api/rooms/{room}/users` endpoint. It's intentionally a warning, not
  a hard block, since the server can't reliably tell "a different person
  took this name" apart from "you, reconnecting after a refresh."
- **[done] Shareable room links** — `/?room=general` prefills the room field
  (and focuses the name field) for a fresh visitor, so they only have to
  type a name; a saved session still always takes priority on refresh. A
  "Copy invite link" button in the online-users panel copies the current
  room's link.
- **[done] Leave confirmation** — clicking Leave opens a small themed
  "Leave #room?" dialog (Cancel / Leave) instead of disconnecting
  immediately, so one mis-tap doesn't drop you out.

## Connection and status

- **[done] Reconnect banner** — on an unexpected drop (not an explicit
  Leave), a banner shows "Reconnecting…" and retries with exponential
  backoff (1s → 15s cap), with a manual "Retry now" button. The chat screen
  and message log stay put instead of kicking you to the join screen.
- **[done] Friendlier status** — a text label beside the status dot, visible
  on both the join screen and in chat (it's part of the always-rendered
  header). Shows "Connecting…", escalating after 4s to "Waking up the
  server… this can take a bit on the free tier" for Render cold starts;
  clears once open; shows "Disconnected" on an unexpected drop (the
  reconnect banner takes over from there); stays clear after an explicit
  Leave. Capped at 42vw with an ellipsis so it can't overflow the header.
- **[done] Send button states** — disabled while the message box is empty
  or the connection isn't open (recomputed on every keystroke and status
  change), and gives a brief scale-pulse on send.

## Visual polish

- **[done] Light theme and toggle** — an Auto / Light / Dark control in the
  connection-log panel. Auto follows `prefers-color-scheme` and updates
  live if the OS theme changes; Light/Dark pin an explicit choice,
  persisted in localStorage. A light-tuned surface palette keeps the
  glassmorphism look (frosted panels, aurora, grid) legible on a pale
  canvas, with a separate deeper-contrast per-user message-color palette
  so gradient-clipped usernames stay readable. Already-rendered message
  bubbles repaint live on a switch, not just new ones. `<meta
  name="theme-color">` updates to match.
- **[done] Theme accent picker** — cyan/violet (default), pink/orange, and
  green/teal, picked via swatches next to the theme control and persisted
  separately from it. Drives buttons, links, focus rings, the aurora
  background, and the header logo everywhere via CSS custom properties
  (including RGB-triple tokens for translucent tints/glows) — one
  consistent brand hue across the whole app, independent of light/dark.
- **[done] Empty states** — a waving-hand hint ("No messages yet — say hi to
  get things started") centered over the log, shown fresh on every join
  (this app keeps no history) and hidden the instant a real chat message
  — from anyone — arrives.
- **[done] Micro-interactions** — a delegated ripple effect on every
  button/chip/pill/swatch (covers ones created later, like reaction pills
  and room chips, with no per-element wiring needed); a quick pop-in on
  the reaction picker; and a real fix for the connection-log/online/leave-
  confirm panels, which looked like they animated but actually popped
  instantly — `display: none` can't be transitioned, so they now toggle
  via opacity/visibility/pointer-events instead, verified mid-transition.
- **[done] Custom scrollbar and focus rings** — the themed scrollbar
  (previously only on the message log) now also applies to the settings
  panels, the composer, and code blocks, with `scrollbar-width`/-`color`
  added for Firefox alongside the existing WebKit rules. A single global
  `:focus-visible` ring in the accent color now covers every interactive
  element — keyboard-only (never shows on a mouse click), verified both
  ways.

## Mobile and accessibility

- **[done] Keyboard handling** — `100dvh` plus the viewport meta's new
  `interactive-widget=resizes-content` keep the composer pinned above an
  on-screen keyboard on modern mobile browsers without extra JS. On top of
  that: focusing the composer scrolls it into view once the keyboard's
  resize settles, and a `visualViewport` resize listener snaps the log to
  the latest message when the keyboard opens — but only if you were
  already following the conversation, so scrolling up to read history
  doesn't get undone by the keyboard appearing.
- **[done] Swipe gestures** — dragging down on a bottom sheet's handle
  (connection log and online-users both use it) follows your finger live
  and closes past an 80px threshold, snapping back below it. A visible
  grip bar marks the drag target. Verified via simulated pointer drags:
  both the follow-finger motion and the threshold-based close/snap-back.
- **[done] Screen-reader support** — the message log and connection-log
  panel are now `role="log"` with `aria-live="polite"` and
  `aria-relevant="additions"`, so new messages and connection events get
  announced (one honest trade-off: reaction-pill updates live inside the
  same region, so they're announced too — standard for chat apps, but not
  perfectly surgical). Checked `--fg-subtle` (the dimmest text token)
  against its backgrounds with the actual WCAG contrast formula: dark mode
  was 4.33:1, light mode as low as 2.74:1, both below the 4.5:1 AA
  threshold for normal text. Retuned both to ≥4.5:1 on the primary canvas
  (dark `#6b7394→#6e7696`, light `#878fa3→#677087`) while keeping it
  visibly dimmer than `--fg-muted`.
- **[done] Reduced motion** — added `prefers-reduced-motion` guards for
  every remaining looping/motion animation that didn't already have one:
  the message-rise entrance, the typing-dot bounce, and the connecting
  status-dot pulse.
- **[done] PWA support** — a web manifest (name, icons, `display:
  standalone`, theme color) plus `apple-touch-icon` and the relevant
  `apple-mobile-web-app-*` meta tags make the app installable, using the
  logo as the icon: the favicon SVG directly (crisp on browsers that
  support SVG manifest icons) paired with a real rasterized 180×180 PNG
  for iOS, which needs one. Verified by fetching the manifest and icon
  over HTTP and checking status/content-type/JSON — installability itself
  (the actual "Add to Home Screen" prompt) isn't something this
  environment can trigger to verify end-to-end.

## Connection log

- **Filter and copy** — filter by type (sent, received, errors) and add a
  "Copy log" button.
- **Clearer framing** — it currently reads like a debug console; could be
  reframed as a friendlier "Activity" panel.

## Suggested first pass — done

1. Message timestamps and grouping
2. Online users panel
3. Auto-reconnect banner
4. Duplicate-name check on the join screen

These four make the app feel like a real chat product and fix the rough
edges already run into during development.
