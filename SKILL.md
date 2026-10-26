---
name: demo-it
description: Turns a feature, the latest commit, today's commits, or any commits you pick into a short, creative launch film about the feature — kinetic typography, the product's real screen flying in with a camera that zooms onto each click, a before/after wipe, springy highlight cards — built with Framer Motion, auto-playing with word-by-word captions and optional voice, published as one shareable page (a claude.ai Artifact when available). Use it whenever the user says /demo-it, "demo this", "make a demo/video of what I built", "show off this feature", "demo my last commit", "what did I ship today, make it a video", "promo for this feature", "walkthrough of this PR", or wants something to post or share to show a change — even if they don't say "demo".
---

# demo-it

Make a 30-50 second launch film for one feature: the kind of clip a product team posts when they ship. It explains **what the feature does for the person using it**, never how the code works: no source code, no file names, no commit hashes on screen. The film is a storyboard (`demo.json`) played by a bundled React + Framer Motion player. Your job is what only you can do: understand the change, find the story a user cares about, and stage it with the product's real screens, words and colours.

Scripts live next to this file. Below, `SKILL_DIR` is this skill's folder.

## 1. Pick the source

If the request already says what to demo, use it and don't ask:

| User says | spec |
|---|---|
| "my last commit", "this commit" | `last` |
| "today", "what I did today" | `today` |
| "last 3 commits" | `last:3` |
| "since Monday" | `since:monday` |
| a sha / range / PR branch | `a1b2c3d,e4f5g6h` / `main..feature-x` |
| "the invite feature" | feature by name (see below) |
| "what I haven't committed" | `wip` |

Otherwise ask one question with these choices (use the ask-user tool if you have one, so it's one click): **Latest commit**, **Today's commits**, **Pick commits**, **A feature by name**. For *Pick commits*, run `list` and show the numbered list; the user replies with numbers or shas. If there are no commits today, say so and offer the latest commit instead.

```bash
python SKILL_DIR/scripts/collect_changes.py list -n 15 --repo <repo>
python SKILL_DIR/scripts/collect_changes.py show <spec> --repo <repo>
```

`show` prints the commit messages, diffstat and a diff trimmed of lockfiles and build output. If a file you need was cut by the budget, read it directly.

**Feature by name**: a feature is code, not necessarily a commit. Try `show grep:<name>` and also search the codebase for the name (routes, components, commands, flags). Film the feature as it exists now.

When several commits are picked, find the one feature they add up to. If they're unrelated, film the most user-visible one and tell the user which you chose.

## 2. Understand it as a user would

The diff tells you what changed; the film is about what a person can now do. Read the diff, then open the files that render it — the component, the page, the command's help text — and collect:

- **The promise**: who notices this and what's better for them, in ≤ 6 words. That's the hook and the end title.
- **The moment**: the click, tap, keystroke or command where the feature shows itself. That's the screen scene.
- **The before**: what used to happen (the bug, the extra steps, the missing option). That's the struck word in the hook or the before side of the wipe.
- **The look**: real strings, labels, layout and colours (CSS variables, Tailwind config, theme files, the logo's colour) so screens are recognisable.

Never invent behaviour, numbers or UI the product doesn't have. When the change has nothing a user sees (performance, refactor, infra), film the effect a user feels — faster load, no stutter, fewer steps — with `number`, `beforeafter` lists and `highlights`, and keep it honest. If the change is too thin for a film (typo, version bump), say so and offer a 3-scene version instead of padding.

## 3. Storyboard

Read `references/scenes.md` now; it has every scene type and field. A shape that works:

1. **hook** — 1-3 poster lines. Often "the old way, struck through → the new way".
2. **screen** — the feature in action on the product's own screen: 2-5 states, zooming in on the key click and back out to show the result.
3. **beforeafter** — the same screen before and after, wiped. Strongest for fixes and redesigns.
4. **highlights** or **journey** — what you get, or how you use it end to end. Pick the one that fits; often skip both.
5. **number** — only if one honest figure tells the story ("3 steps → 1").
6. **end** — the promise again as a title, where to try it.

5-8 scenes, one idea each. Vary rhythm: a loud typographic beat, then a calm screen, then a quick wipe.

Captions (`say`) are what a presenter would say over the footage: short, concrete, present tense, about the user ("Pick one round. Connect. Still one."), never about code ("we now cache the dataset attribute"). Write them in the language the user writes to you in unless they ask otherwise, and set `lang` to match.

Save files outside the user's repo so the demo never ends up in a commit: the session's scratchpad/temp directory if you have one, otherwise the OS temp dir. Name them with a short slug of the title (`round-pick.json`).

## 4. Build and check

```bash
python SKILL_DIR/scripts/build_demo.py <dir>/round-pick.json -o <dir>/round-pick.html
```

Fix every `ERROR`; treat warnings as strong suggestions (a missing target means the camera and cursor go nowhere). If you have a browser tool, serve the folder over http, let it play, check the console, and look at the screen scene once — the usual bugs are screen markup that overflows its frame and targets that don't exist. The page loads React and Framer Motion from public CDNs, so it needs a connection.

## 5. Publish (the "one click" part)

- **Artifact tool available** (claude.ai / Claude desktop): rebuild with `--artifact` (the host adds its own doctype/head/body, so the builder leaves them out) and publish that HTML as an Artifact (icon `play`, a one-sentence description of the feature). If your environment asks you to load a design skill first, do so; the player already follows the page contract (title, explicit colours, dark look by design, mobile layout, CDN allowlist), so it shouldn't need changes. Give the user the link.
- **No Artifact tool**: open the HTML in the default browser (`start`, `open` or `xdg-open`) and give the path.

End with the link/path, the scenes in one line, and that **Voice** narrates, space pauses, arrows skip, and a screen recording turns it into a video file.

## Iterating

For changes ("shorter", "more about the lobby", "in French", "more playful"), edit the JSON and rebuild; don't hand-edit the HTML. Republish to the same artifact so the link stays the same.
