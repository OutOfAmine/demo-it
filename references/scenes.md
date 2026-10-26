# Storyboard format (demo.json)

The player is a short launch film built with React + Framer Motion: springy kinetic type, a device that flies in and a camera that zooms onto what the user clicks, a before/after wipe. It explains the feature to someone who uses the product. No source code, no commit hashes on screen.

```json
{
  "title": "Round pick sticks",
  "product": "Your Friends Hate You",
  "meta": "private rooms · Oct 19",
  "theme": { "accent": "#e2483a", "accent2": "#ffcf3a" },
  "badge": true,
  "lang": "en-US",
  "scenes": [ ... ]
}
```

- `product`: shown top-left. Use the product's name, not the repo path.
- `theme.accent` (+ optional `accent2` for gradients): take them from the project's brand (CSS variables, Tailwind config, logo). The film itself is always dark; project screens keep their own colours.
- `badge`: small "made with /demo-it" credit. `false` hides it.
- `lang`: voice language for the Voice button (`en-US`, `fr-FR`, `ar-MA`...).

Every scene accepts:
- `say`: the caption, revealed word by word (spoken when Voice is on). 8-22 words.
- `hold`: ms to stay after the animation (default 1300).
- `kicker` / `title`: chip + headline above the scene (hook and end have their own). `*word*` paints a word with the accent gradient; `~word~` strikes it.

## hook: kinetic typography (open with this)
```json
{ "type": "hook", "kicker": "New in private rooms", "lines": ["Pick *one* round.", "Get ~three~ *one*."], "say": "..." }
```
1-3 lines, each ≤ 6 words, revealed one per beat with a springy blur-in. A `~struck~` word gets a red line drawn through it and fades: perfect for "what used to happen" → "what happens now". Write it like a poster, not a sentence.

## screen: the feature in action (the heart of the film)
```json
{ "type": "screen", "title": "Pick it once. *It stays.*", "device": "browser", "url": "yfhy.game/room/7KQ2", "height": 440, "bg": "#2a3a1a",
  "css": ".lobby{padding:28px;font:15px system-ui} .btn{padding:10px 16px;border-radius:10px;background:#ff5a36;color:#fff;display:inline-block} .is-active{outline:3px solid #fff}",
  "states": [
    { "html": "<div class='lobby'>…<div class='btn' id='pick'>5 rounds</div></div>", "target": "#pick", "do": "click", "zoom": 1.6, "note": "Host picks 5" },
    { "html": "<div class='lobby'>…<b id='val'>5</b></div>", "target": "#val", "do": "spot", "zoom": 1, "note": "Still 5 after connecting" },
    { "target": "#name", "do": "type", "text": "Amine" }
  ], "say": "..." }
```
- `device`: `browser` (default), `phone` (tall, rounded, no URL bar) or `window`. `url` is what the bar shows: the real route for web apps, the app or file name otherwise.
- The device flies in with a 3D tilt. A state with `html` cross-fades to a new screen; a state without `html` keeps the screen and only moves.
- `zoom`: camera zoom onto the target (`true` = 1.7, or a number like 1.4-2.2; `1` zooms back out). Zoom in on the moment that matters, then back out to show the result in context. That push-in is what makes it feel like a film.
- `do`: `click` (cursor press + ripple, and the target gets class `is-active` or the class in `toggle`), `type` (types `text` into the target), `spot` (dims everything else), or omit to just move the cursor.
- `note`: a white tooltip by the target. `hold`: ms on this state (default 1100).
- `css` applies inside the screen only (shadow DOM). Give targets ids, and target the tight element (the button, the value, an `inline-flex` group), not a full-width row: the spotlight and cursor frame whatever box the target has.
- `image` instead of `html` shows a real screenshot; aim with `"at": [x%, y%, w%, h%]`.
- Rebuild the screen from the project's real markup, copy and palette: read the component, reuse its strings, layout and colours. Recognisable beats generic. 2-5 states.

## beforeafter: a wipe from the old way to the new
```json
{ "type": "beforeafter", "title": "Same lobby, *no surprises*", "height": 380, "css": "…", "bg": "#2a3a1a",
  "before": { "label": "Before", "html": "<div class='lobby'>… 3 rounds …</div>" },
  "after":  { "label": "After",  "html": "<div class='lobby'>… 1 round …</div>" }, "say": "..." }
```
Shows `before`, then a glowing divider sweeps across revealing `after`. Each side is either a screen (`html`, sharing the scene's `css`/`bg`) or a list (`"items": ["Copy the code", "Send it"]`; before items get ✕, after items ✓). Screens make the strongest wipe: same layout, one thing different.

## highlights: what you get, as cards that spring in
```json
{ "type": "highlights", "title": "What changed for *hosts*", "items": [
  { "icon": "🎯", "title": "Pick 1 to 10 rounds", "body": "Any number, any time before start." },
  { "icon": "🔒", "title": "Only the host decides", "body": "Guests see the choice, can't edit it." } ], "say": "..." }
```
2-4 cards. Benefits in the user's words, not implementation.

## journey: how someone uses it, step by step
```json
{ "type": "journey", "title": "From lobby to *final ranking*", "nodes": [
  { "icon": "🎛️", "label": "Pick rounds", "sub": "In the room lobby" },
  { "icon": "✅", "label": "Everyone ready" },
  { "icon": "🏆", "label": "Final ranking", "sub": "After the last round" } ], "say": "..." }
```
2-5 nodes lit one by one along a growing line. These are user actions or moments, not services or functions.

## number: one figure that tells the story
```json
{ "type": "number", "from": 3, "to": 1, "suffix": " round", "label": "means *exactly* one round", "say": "..." }
```
Counts up (or from `from` to `to`, then shows "was …" struck). `prefix` / `suffix` hold units. Only numbers that are true from the code or the commit message.

## terminal: for CLI / API features only
```json
{ "type": "terminal", "title": "One command", "shell": "zsh — my-app", "prompt": "$",
  "steps": [ { "cmd": "npx my-cli export --format csv", "out": [ { "t": "✔ 1,204 rows exported", "k": "ok" }, { "t": "→ out/report.csv", "k": "dim" } ] } ], "say": "..." }
```
Output `k`: `ok`, `err`, `warn`, `dim`, or plain. Output is derived from the real log/print strings in the code.

## end: the closing card
```json
{ "type": "end", "kicker": "Live now", "title": "Your rounds, your rules.", "tagline": "Private rooms in Your Friends Hate You", "cta": "yfhy.game", "say": "..." }
```
Letters flip in, a burst of sparks, then the tagline and a call to action: where to try it (URL, route, command), or leave `cta` out.
