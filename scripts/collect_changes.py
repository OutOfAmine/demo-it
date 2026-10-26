#!/usr/bin/env python3
"""Gather the commits and diff a demo is built from.

Usage:
  collect_changes.py list [-n 15]          recent commits, grouped by day (for picking)
  collect_changes.py show <spec> [...]     commit messages, diffstat and a trimmed diff

<spec> is one of:
  last              the latest commit (HEAD)
  today             every commit made since local midnight
  since:<when>      e.g. since:yesterday, since:2026-10-20, since:"3 days ago"
  last:<N>          the N latest commits
  <sha>[,<sha>...]  specific commits (any order, they are sorted oldest first)
  <a>..<b>          a git range
  grep:<text>       commits whose message mentions <text> (case-insensitive)
  wip               uncommitted changes (staged + unstaged)

Options for show:
  --repo PATH       repository to read (default: current directory)
  --max-lines N     cap for diff lines per file (default 120)
  --max-total N     cap for the whole diff (default 1500)
"""
import argparse
import datetime as dt
import subprocess
import sys

# lockfiles, build output and other noise that never helps explain a feature
SKIP = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Cargo.lock",
        ".min.js", ".min.css", ".map", ".snap", "dist/", "build/", ".next/", "vendor/")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # lets the very first commit be diffed


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def cmd_list(repo, n):
    fmt = "%h\x1f%ad\x1f%an\x1f%s"
    out = git(repo, "log", f"-n{n}", f"--format={fmt}", "--date=format:%Y-%m-%d %H:%M", "--shortstat")
    rows, cur = [], None
    for line in out.splitlines():
        if "\x1f" in line:
            sha, date, author, subj = line.split("\x1f", 3)
            cur = {"sha": sha, "date": date, "author": author, "subj": subj, "stat": ""}
            rows.append(cur)
        elif line.strip() and cur:
            cur["stat"] = line.strip().replace(" changed", "").replace("insertions(+)", "+").replace("insertion(+)", "+").replace("deletions(-)", "-").replace("deletion(-)", "-")
    today = dt.date.today().isoformat()
    day = None
    for i, r in enumerate(rows, 1):
        d = r["date"][:10]
        if d != day:
            day = d
            print(f"\n## {d}{'  (today)' if d == today else ''}")
        print(f"{i:>2}. {r['sha']}  {r['date'][11:]}  {r['subj']}  [{r['stat']}]")
    n_today = sum(1 for r in rows if r["date"].startswith(today))
    print(f"\n{n_today} commit(s) today. Branch: {git(repo, 'rev-parse', '--abbrev-ref', 'HEAD').strip()}")


def day_start(when):
    """git reads a bare date as 'that day at the current time'; a demo means the whole day."""
    w = when.strip().lower()
    if w == "yesterday":
        return (dt.date.today() - dt.timedelta(days=1)).isoformat() + " 00:00"
    if len(w) == 10 and w[4] == "-" and w[7] == "-":
        return w + " 00:00"
    return when


def resolve(repo, spec):
    """Return (list of shas oldest-first, label) or (None, 'wip')."""
    if spec == "wip":
        return None, "uncommitted changes"
    if spec == "last":
        return [git(repo, "rev-parse", "HEAD").strip()], "latest commit"
    if spec == "today":
        midnight = dt.datetime.now().strftime("%Y-%m-%d 00:00")
        shas = git(repo, "log", f"--since={midnight}", "--format=%H").split()
        return shas[::-1], "today's commits"
    if spec.startswith("since:"):
        shas = git(repo, "log", f"--since={day_start(spec[6:])}", "--format=%H").split()
        return shas[::-1], f"commits since {spec[6:]}"
    if spec.startswith("last:"):
        shas = git(repo, "log", f"-n{int(spec[5:])}", "--format=%H").split()
        return shas[::-1], f"last {spec[5:]} commits"
    if spec.startswith("grep:"):
        shas = git(repo, "log", "-i", f"--grep={spec[5:]}", "--format=%H", "-n50").split()
        return shas[::-1], f"commits mentioning '{spec[5:]}'"
    if ".." in spec:
        shas = git(repo, "rev-list", "--reverse", spec).split()
        return shas, f"range {spec}"
    shas = [git(repo, "rev-parse", s.strip()).strip() for s in spec.split(",") if s.strip()]
    order = {s: int(git(repo, "log", "-1", "--format=%ct", s).strip()) for s in shas}
    return sorted(shas, key=order.get), "selected commits"


def is_test(path):
    return any(t in path for t in ("test", "spec", "__snapshots__", "fixtures"))


def trim_diff(diff, max_lines, max_total):
    out, total, skipped = [], 0, []
    blocks = ("\n" + diff).split("\ndiff --git ")[1:]
    # source changes explain a feature better than its tests, so they get the budget first
    blocks.sort(key=lambda b: is_test(b.splitlines()[0] if b else ""))
    for block in blocks:
        header = block.splitlines()[0] if block else ""
        path = header.split(" b/")[-1] if " b/" in header else header
        if any(s in path for s in SKIP) or "Binary files" in block[:400]:
            skipped.append(path)
            continue
        lines = ("diff --git " + block).splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more lines in {path})"]
        room = max_total - total
        if room < 15:
            skipped.append(path + " (budget)")
            continue
        if len(lines) > room:
            lines = lines[:room] + [f"... (cut for budget, read {path} directly)"]
        out.extend(lines)
        total += len(lines)
    return "\n".join(out), skipped


def cmd_show(repo, spec, max_lines, max_total):
    shas, label = resolve(repo, spec)
    top = git(repo, "rev-parse", "--show-toplevel").strip()
    remote = git(repo, "config", "--get", "remote.origin.url", check=False).strip()
    print(f"# Source: {label}\nRepo: {top}\nRemote: {remote or '(none)'}\n")
    if shas is None:
        stat = git(repo, "diff", "HEAD", "--stat")
        diff = git(repo, "diff", "HEAD", "-U4")
        if not stat.strip():
            sys.exit("No uncommitted changes. Try `last` or run `list`.")
    else:
        if not shas:
            sys.exit(f"No commits match '{spec}'. Run `list` to see what exists.")
        print("## Commits (oldest first)")
        for s in shas:
            print(git(repo, "log", "-1", "--format=- %h  %ad  %an%n  %s%n%w(0,2,2)%b", "--date=format:%Y-%m-%d %H:%M", s).rstrip())
        first, last = shas[0], shas[-1]
        has_parent = git(repo, "rev-list", "--parents", "-n1", first).split()[1:] != []
        base = f"{first}^" if has_parent else EMPTY_TREE
        between = git(repo, "rev-list", f"{base}..{last}" if has_parent else last).split()
        if len(shas) == 1 or set(shas) == set(between):
            rng = (base, last)
            stat = git(repo, "diff", "--stat", *rng)
            diff = git(repo, "diff", "-U4", *rng)
        else:
            # non-contiguous pick: show each commit's own patch
            stat = "\n".join(git(repo, "show", "--stat", "--format=%h %s", s) for s in shas)
            diff = "\n".join(git(repo, "show", "-U4", "--format=", s) for s in shas)
    print("\n## Diffstat\n" + stat.rstrip())
    body, skipped = trim_diff(diff, max_lines, max_total)
    if skipped:
        print("\nSkipped (noise or over budget): " + ", ".join(skipped))
    print("\n## Diff\n" + body)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["list", "show"])
    ap.add_argument("spec", nargs="?", default="last")
    ap.add_argument("-n", type=int, default=15)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--max-lines", type=int, default=120)
    ap.add_argument("--max-total", type=int, default=1500)
    a = ap.parse_args()
    if a.cmd == "list":
        cmd_list(a.repo, a.n)
    else:
        cmd_show(a.repo, a.spec, a.max_lines, a.max_total)


if __name__ == "__main__":
    main()
