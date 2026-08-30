#!/usr/bin/env python3
"""Report outstanding documentation debt across labs and detections.

Every converted writeup carries `*(pending)*` markers where a fact was not
observed by the writer. Those markers are the difference between this
repository and one that quietly reconstructs plausible history — but a marker
nobody can find is the same as no marker at all.

This walks the tree, groups every outstanding item under its lab and section,
and writes docs/open-items.md. Documentation debt becomes a tracked artifact
rather than something remembered.

Usage:
    python3 scripts/open-items.py           # regenerate report
    python3 scripts/open-items.py --check   # exit 1 if report is stale
    python3 scripts/open-items.py --list    # print to stdout, write nothing
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "open-items.md"
# The corpus is the TRACKED repository, taken from git, not whatever Markdown
# happens to sit in the working tree. A three-directory allowlist was the
# previous scope and silently omitted live debt in docs/configuration-inventory.md
# and docs/navigation.md; scanning the filesystem instead swings the other way and
# lets an untracked scratch file fail the gate. Neither is the corpus this report
# claims authority over. Exclusions below are explicit paths and path prefixes,
# never a filename pattern, so a future tracked file cannot escape the census by
# being named a particular way.
EXCLUDED_PREFIXES = (
    "docs/current-state/",  # governed authority chain: revision records, not documentation debt
    "u6/",                  # frozen Stage-2 territory, inert and out of scope
)
EXCLUDED_PATHS = frozenset({
    "docs/open-items.md",      # this report
    "labs/_TEMPLATE.md",       # template artifacts, named individually and not by prefix
    "detections/_TEMPLATE.md",
})
SCOPE_NOTE = (
    "Scope: every tracked `.md` file in the repository, as listed by "
    "`git ls-files`, excluding `docs/current-state/` (authority chain), "
    "`u6/` (frozen, inert), the two `_TEMPLATE.md` files, and this report. "
    "Untracked working-tree files are not part of the corpus. A marker must "
    "open and close on one source line; one that does not is reported as an "
    "escape and fails this report rather than being silently dropped."
)

# The convention is `*(pending)*` / `*(pending — why)*`. Require the LEADING
# emphasis asterisk: it is what separates a marker from product UI text that
# merely contains the word, e.g. the Action center's "(pending / history)" tab.
# The closing `)*` is deliberately NOT required. A marker whose text contains a
# nested parenthetical closes that inner paren first, so `[^)]*` terminates
# early and a trailing `\*` then fails against the rest of the line — which is
# exactly what labs/01 line 95 does. Requiring the closing asterisk drops that
# real marker from the census.
PENDING = re.compile(r"\*\(pending[^)]*\)", re.I)
# The census is line-oriented, and a marker wrapped across source lines
# escapes it silently — which is exactly how the Lab-17 instance survived
# until Stage 6 found it by hand. OPENING matches the marker's opening
# token alone. Every opening token must be either counted by PENDING or
# suppressed by a stated rule below; anything else is an escape, and
# escapes fail loudly rather than quietly shrinking the census.
#
# This is deliberately NOT multiline parsing. The contract stays one
# marker, one line; the detector makes a violation of that contract
# visible instead of invisible.
OPENING = re.compile(r"\*\(pending", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
STATUS = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*(.+?)\s*\|", re.M)
# A marker inside backticks is prose *about* the convention, not a use of it.
# Likewise blockquotes, which carry the explanatory note at the top of a writeup.
# Without this, the tracker counts its own vocabulary as debt and gets ignored.
INLINE_CODE = re.compile(r"`[^`]*`")


def scan(path: pathlib.Path) -> list[tuple[int, str, str]]:
    """Return (line_no, section, text) for each pending marker."""
    hits = []
    section = "(preamble)"
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        h = HEADING.match(line)
        if h:
            section = h.group(2).strip()

        if line.lstrip().startswith(">"):
            continue
        # Strip inline code spans before testing, so `*(pending)*` in prose
        # about the convention does not register as an open item.
        if not PENDING.search(INLINE_CODE.sub("", line)):
            continue

        text = line.strip()
        # Collapse table rows to something readable
        if text.startswith("|"):
            cells = [c.strip() for c in text.strip("|").split("|")]
            text = " / ".join(c for c in cells if c and not set(c) <= {"-"})
        hits.append((i, section, text[:100]))
    return hits


def escapes(path: pathlib.Path) -> list[tuple[int, str]]:
    """Return (line_no, text) for opening markers the census cannot see.

    Applies scan()'s own suppression rules first, so convention prose in a
    blockquote or inside inline code is not reported: those are legitimately
    excluded, not escaped. What remains is a marker that opens on a line and
    does not close on it.

    The test is per TOKEN, not per line. Asking whether the line holds any
    complete marker lets one masked the other: on

        *(pending — complete)* and *(pending

    the first marker satisfies a line-level test while the second escapes
    silently. So every complete marker is removed first, and whatever opening
    token survives that removal is unaccounted for.
    """
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(">"):
            continue
        residue = PENDING.sub("", INLINE_CODE.sub("", line))
        if OPENING.search(residue):
            out.append((i, line.strip()[:100]))
    return out


def tracked_markdown() -> list[pathlib.Path]:
    """The tracked .md corpus, from git. Fails closed rather than guessing.

    git ls-files reads the index, so a file staged in a pre-commit run counts
    and an untracked working-tree file does not. If git cannot answer, this
    raises instead of falling back to the filesystem: a census that silently
    changes corpus is the defect this function exists to prevent.
    """
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--", "*.md"],
        capture_output=True, check=True,
    )
    return [ROOT / p for p in out.stdout.decode("utf-8").split("\0") if p]


def corpus() -> list[pathlib.Path]:
    """The census corpus: tracked Markdown minus the governed exclusions."""
    keep = []
    for path in sorted(tracked_markdown()):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(EXCLUDED_PREFIXES) or rel in EXCLUDED_PATHS:
            continue
        keep.append(path)
    return keep


def audit_escapes() -> list[tuple[str, int, str]]:
    """Every escaped opening marker in the corpus, as (path, line, text)."""
    found = []
    for path in corpus():
        rel = path.relative_to(ROOT).as_posix()
        found += [(rel, i, s) for i, s in escapes(path)]
    return found


def collect() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in corpus():
        rel = path.relative_to(ROOT).as_posix()
        body = path.read_text(encoding="utf-8")
        hits = scan(path)
        if not hits:
            continue
        m = STATUS.search(body)
        out[rel] = {"status": m.group(1) if m else "—", "hits": hits}
    return out


def render(data: dict[str, dict]) -> str:
    total = sum(len(v["hits"]) for v in data.values())
    lines = [
        "# Open Documentation Items",
        "",
        "<!-- GENERATED by scripts/open-items.py — do not edit by hand. -->",
        "",
        "Outstanding `*(pending)*` markers. Each one is a fact the writeup does not",
        "have and will not invent. See `docs/documentation-standard.md` §5.",
        "",
        SCOPE_NOTE,
        "",
        f"**{total} open item(s) across {len(data)} file(s).**",
        "",
    ]

    if not data:
        lines += ["Nothing outstanding.", ""]
        return "\n".join(lines)

    for path, meta in data.items():
        lines += [
            f"## `{path}`",
            "",
            f"Status: {meta['status']}",
            "",
            "| Line | Section | Item |",
            "|---|---|---|",
        ]
        for line_no, section, text in meta["hits"]:
            safe = text.replace("|", "\\|")
            lines.append(f"| {line_no} | {section} | {safe} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if report stale")
    ap.add_argument("--list", action="store_true", help="print, do not write")
    args = ap.parse_args()

    escaped = audit_escapes()
    if escaped:
        for rel, line_no, text in escaped:
            print(
                f"ESCAPE {rel}:{line_no} — pending marker opens and does not "
                f"close on this line, so the census cannot see it: {text}",
                file=sys.stderr,
            )
        print(
            "\nA marker split across source lines is invisible to this report. "
            "Reflow it onto one line; the census is line-oriented by contract.",
            file=sys.stderr,
        )
        return 1

    content = render(collect())

    if args.list:
        print(content)
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != content:
            print("Open-items report is stale.", file=sys.stderr)
            print("Run: python3 scripts/open-items.py", file=sys.stderr)
            return 1
        print("Open-items report up to date.")
        return 0

    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
