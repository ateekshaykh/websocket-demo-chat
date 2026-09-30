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
- **Avatars** — initials in a gradient circle, reusing each user's existing
  hologram color.
- **Emoji picker and quick reactions** — e.g. 👍 ❤️ 😂 on hover or long-press.
- **Links and formatting** — clickable URLs, line breaks, and maybe code
  blocks.
- **"Jump to latest" button** — shown when you've scrolled up and new
  messages arrive.
- **Unread badge and sound** — tab title like `(3) WebSocket Chat` and an
  optional soft ping when the tab is in the background.

## Joining and leaving

- **Better join screen** — recent rooms as chips, a "random room name"
  button, and a live "3 online" preview for the room.
- **[done] Inline validation** — a soft, non-blocking "name already taken in
  this room" warning while typing, backed by a new read-only
  `GET /api/rooms/{room}/users` endpoint. It's intentionally a warning, not
  a hard block, since the server can't reliably tell "a different person
  took this name" apart from "you, reconnecting after a refresh."
- **Shareable room links** — `/?room=general` opens with the room prefilled,
  plus a copy-link button in the header.
- **Leave confirmation** — a small confirm step so one mis-tap doesn't drop
  you out.

## Connection and status

- **[done] Reconnect banner** — on an unexpected drop (not an explicit
  Leave), a banner shows "Reconnecting…" and retries with exponential
  backoff (1s → 15s cap), with a manual "Retry now" button. The chat screen
  and message log stay put instead of kicking you to the join screen.
- **Friendlier status** — a text pill like "Connected" or "Reconnecting"
  beside the status dot. Render's cold starts also deserve a "Waking up the
  server…" message.
- **Send button states** — disabled when empty or offline, with a subtle
  sending animation.

## Visual polish

- **Light theme and toggle** — dark glass suits the app, but some users
  prefer light; it would also respect the system setting.
- **Theme accent picker** — e.g. cyan/violet, pink/orange, green/teal.
- **Empty states** — a friendly illustration or hint in a fresh room
  ("Say hi 👋").
- **Micro-interactions** — message send animation, button ripple, smoother
  panel open/close.
- **Custom scrollbar and focus rings** — consistent styling across every
  element.

## Mobile and accessibility

- **Keyboard handling** — keep the input above the mobile keyboard and the
  latest message in view.
- **Swipe gestures** — swipe down to close the connection log.
- **Screen-reader support** — announce new messages with `aria-live`, and
  check color contrast on the dimmer text.
- **Reduced motion** — the aurora background already respects
  `prefers-reduced-motion`, but the message-rise and typing-dot bounce
  animations don't yet.
- **PWA support** — installable to the home screen with the logo as the
  icon.

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
