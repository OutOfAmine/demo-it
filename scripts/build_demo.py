#!/usr/bin/env python3
"""Turn a demo storyboard (JSON) into one self-contained, auto-playing HTML page.

Usage: build_demo.py demo.json [-o demo.html] [--artifact]

Checks the storyboard first and prints warnings for things that make a demo
drag or break (too many scenes, long captions, huge code blocks, bad selectors).
Exits non-zero only on errors that would stop the page from playing.
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "player.html"
TYPES = {"hook", "text", "screen", "beforeafter", "highlights", "journey", "number", "terminal", "end"}


def check(demo):
    errors, warns = [], []
    scenes = demo.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        return ["'scenes' must be a non-empty list"], warns
    if not demo.get("title"):
        warns.append("no top-level 'title' (used for the page title)")
    if not 4 <= len(scenes) <= 9:
        warns.append(f"{len(scenes)} scenes; 5-8 usually feels right")
    types = [s.get("type") for s in scenes]
    if "screen" not in types and "terminal" not in types and "beforeafter" not in types:
        warns.append("no screen/terminal/beforeafter scene: the viewer never sees the feature itself")
    for i, s in enumerate(scenes, 1):
        where = f"scene {i} ({s.get('type', '?')})"
        t = s.get("type")
        if t not in TYPES:
            errors.append(f"{where}: unknown type, use one of {sorted(TYPES)}")
            continue
        say = s.get("say", "")
        if not say:
            warns.append(f"{where}: no 'say' caption")
        elif len(say.split()) > 22:
            warns.append(f"{where}: caption is {len(say.split())} words; aim for <= 22")
        if t == "hook":
            lines = s.get("lines") or []
            if not 1 <= len(lines) <= 3:
                errors.append(f"{where}: needs 1-3 'lines'")
            for ln in lines:
                if len(ln.replace("*", "").replace("~", "").split()) > 7:
                    warns.append(f"{where}: hook line '{ln}' is long; kinetic lines hit hardest at <= 6 words")
        if t == "terminal" and not s.get("steps"):
            errors.append(f"{where}: needs 'steps'")
        if t == "screen":
            states = s.get("states") or []
            if not states:
                errors.append(f"{where}: needs 'states'")
            elif states[0].get("html") is None and not states[0].get("image"):
                errors.append(f"{where}: first state needs 'html' or 'image'")
            if len(states) > 6:
                warns.append(f"{where}: {len(states)} states; 2-5 keeps it moving")
            for k, st in enumerate(states, 1):
                tgt = st.get("target")
                if tgt and not st.get("at"):
                    # every target must exist in the screen that is showing at that moment
                    html = next((x.get("html") for x in reversed(states[:k]) if x.get("html") is not None), "") or ""
                    m = re.match(r"^[#.]([\w-]+)$", tgt) or re.match(r"^\[data-demo=['\"]?([\w-]+)", tgt)
                    if m and m.group(1) not in html:
                        warns.append(f"{where} state {k}: target {tgt} not found in the current screen's html")
                if (st.get("do") or st.get("zoom")) and not (tgt or st.get("at")):
                    warns.append(f"{where} state {k}: 'do'/'zoom' without a target or 'at'")
        if t == "beforeafter":
            for side in ("before", "after"):
                v = s.get(side) or {}
                if v.get("html") is None and not v.get("items"):
                    errors.append(f"{where}: '{side}' needs 'html' or 'items'")
        if t == "highlights" and not 2 <= len(s.get("items") or []) <= 4:
            warns.append(f"{where}: 2-4 highlights read best")
        if t == "journey" and not 2 <= len(s.get("nodes") or []) <= 5:
            warns.append(f"{where}: journeys read best with 2-5 steps")
        if t == "number":
            try:
                float(s.get("to"))
                if s.get("from") is not None:
                    float(s.get("from"))
            except (TypeError, ValueError):
                errors.append(f"{where}: 'to' (and 'from') must be numbers; put units in prefix/suffix")
    return errors, warns


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("demo")
    ap.add_argument("-o", "--out")
    ap.add_argument("--artifact", action="store_true", help="emit a page body for claude.ai Artifacts (no doctype/html/head/body)")
    a = ap.parse_args()
    src = pathlib.Path(a.demo)
    demo = json.loads(src.read_text(encoding="utf-8"))
    errors, warns = check(demo)
    for w in warns:
        print("warn:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        sys.exit(1)
    # "</" must not appear raw inside the inline <script>
    data = json.dumps(demo, ensure_ascii=False).replace("</", "<\\/")
    title = demo.get("title", "Demo").replace("<", "&lt;")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__DEMO_DATA__*/null", data, 1).replace("__DEMO_TITLE__", title, 1)
    if a.artifact:
        # the Artifact host wraps the page in its own doctype/html/head/body
        html = re.sub(r"(?im)^\s*(<!doctype html>|</?html[^>]*>|</?head>|</?body>|<meta (charset|name=\"viewport\")[^>]*>)\s*\n", "", html)
    out = pathlib.Path(a.out) if a.out else src.with_suffix(".html")
    out.write_text(html, encoding="utf-8")
    print(f"built {out} ({len(demo['scenes'])} scenes, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
