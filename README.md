# /demo-it

**Turn your last commit into a launch film.** A Claude Code skill that reads what you shipped and makes a short, auto-playing Framer Motion video about the feature: kinetic typography, your real screen flying in with a camera that zooms onto each click, a before/after wipe, springy highlight cards, word-by-word captions and optional voice. You get one shareable link (a claude.ai Artifact) or a single HTML file.

No FFmpeg, no API keys, no screen recording. Type `/demo-it`.

## What it does

1. **Pick the source.** Latest commit, today's commits, the commits you choose, or a feature by name. Say it in the prompt ("demo my last commit") or pick from one question.
2. **Understands the feature like a user would.** It reads the diff and the components it touches, then works out the promise, the moment the feature shows itself, and what it replaced.
3. **Storyboards a 30-50 s film** from your product's real strings, layout and colours. No source code or commit hashes appear on screen; it explains the feature, not the implementation.
4. **Builds and publishes.** A React + Framer Motion player turns the storyboard into one page that plays itself. Space pauses, arrows skip, **Voice** narrates.

### Scenes

| Scene | What you see |
|---|---|
| `hook` | Poster lines spring in; `~old~` words get struck through |
| `screen` | Your UI in a browser/phone frame, 3D fly-in, camera zooms to each click, cursor, spotlight, notes |
| `beforeafter` | Old vs new, revealed by a glowing wipe |
| `highlights` | 2-4 benefit cards that spring in |
| `journey` | How someone uses it, lit step by step |
| `number` | One honest figure that counts (3 → 1) |
| `terminal` | For CLI features: typed commands, streamed output |
| `end` | Title flip, sparks, where to try it |

## Install

```bash
git clone https://github.com/OutOfAmine/demo-it ~/.claude/skills/demo-it
```

Then, in any git repo, open Claude Code and run:

```
/demo-it
```

or just ask: *"make a demo of what I shipped today"*.

Needs Python 3.8+ and git. The film loads React, Framer Motion and fonts from public CDNs, so it needs an internet connection to play.

## Files

```
SKILL.md                    the instructions Claude follows
assets/player.html          the React + Framer Motion player
scripts/collect_changes.py  lists commits, collects the diff for a source
scripts/build_demo.py       checks a storyboard and builds the page
references/scenes.md        every scene type and field
examples/round-pick.json    a full storyboard to copy from
```

Build an example yourself:

```bash
python scripts/build_demo.py examples/round-pick.json -o round-pick.html
```

## License

MIT
