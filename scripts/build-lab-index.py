#!/usr/bin/env python3
"""Generate the Lab Index block in README.md from labs/*/README.md.

Why this exists
---------------
On 2026-08-11 the repository carried 24 labs and 98 posture entries. The root
README advertised **19 labs** and **80 entries**, and every lab in its table
read `Built, documenting` while five of them were complete and committed.

Every *generated* document was correct at that moment — the posture register,
the lessons index, the lab-coverage report, the ATT&CK matrix, the open-items
list. All five are CI-enforced and none had drifted. The one surface that had
drifted was the one with no gate behind it: hand-maintained prose on the
repository's front page, which is also the first thing any reader sees.

That is the repository's own recurring thesis pointed at itself. A control that
is never verified degrades silently, and the failure is invisible precisely
because nothing is checking. Fixing the numbers by hand would have reset the
clock and guaranteed a recurrence at Lab 24. This script removes the mechanism
instead.

What it does NOT do
-------------------
It does not generate the README. The thesis, the architecture notes, the
navigation guidance and the editorial framing are authored and stay authored —
turning the front page into a build artifact would trade one maintenance
problem for a worse one. Only the volatile state is derived: the lab table,
which is a *mirror* of facts that live elsewhere.

Authority
---------
Each lab's own `README.md` is authoritative for its title and status. This
table restates them. Where the two disagree, the lab is right and this file is
stale — that is what `--check` exists to catch.

Two deliberate omissions:

* **The Domain column is dropped.** The old table classified labs into a
  taxonomy — Environment, Response, Ingestion, Detection, Data protection —
  that does not exist in any lab's frontmatter. Each lab's `Domain` field is
  descriptive prose ("Microsoft Purview Audit (unified audit log) / Microsoft
  Purview eDiscovery (content search) / …"), not a category. Deriving the
  taxonomy would mean hand-maintaining a mapping *inside this script*, which
  moves the drift rather than removing it.
* **Status is truncated at the em-dash.** Lab statuses carry an elaboration
  ("✅ Built and measured — two phases, zero cost, both VMs deallocated
  throughout"). The claim is the part before the dash; the elaboration belongs
  on the lab page, not the index.

Usage:
    python3 scripts/build-lab-index.py            # regenerate
    python3 scripts/build-lab-index.py --check    # CI: staleness check
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
README = ROOT / "README.md"

BEGIN = "<!-- BEGIN GENERATED LAB INDEX -->"
END = "<!-- END GENERATED LAB INDEX -->"

DIR_RE = re.compile(r"^(\d{2})-")
H1_RE = re.compile(r"^#\s+Lab\s+\d+\s+[—-]\s+(.*?)\s*$", re.M)
STATUS_RE = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*(.*?)\s*\|\s*$", re.M)


def load() -> tuple[list[dict], list[str]]:
    """Read every lab directory. Returns (entries, errors)."""
    entries: list[dict] = []
    errors: list[str] = []

    for path in sorted(LABS.iterdir()):
        if not path.is_dir():
            continue
        m = DIR_RE.match(path.name)
        if not m:
            errors.append(f"{path.name}/ does not start with a two-digit lab number")
            continue

        readme = path / "README.md"
        if not readme.exists():
            errors.append(f"{path.name}/ has no README.md")
            continue

        text = readme.read_text(encoding="utf-8")

        h1 = H1_RE.search(text)
        if not h1:
            errors.append(f"{path.name}/README.md has no '# Lab NN — Title' heading")
            continue

        status = STATUS_RE.search(text)
        if not status:
            errors.append(f"{path.name}/README.md has no '| **Status** |' row")
            continue

        # The claim is the part before the em-dash; the rest is elaboration.
        short = re.split(r"\s+[—-]\s+", status.group(1), maxsplit=1)[0].strip()

        entries.append(
            {
                "number": m.group(1),
                "dir": path.name,
                "title": h1.group(1).strip(),
                "status": short,
            }
        )

    return entries, errors


def render(entries: list[dict]) -> str:
    lines = [
        BEGIN,
        "",
        "| # | Lab | Status |",
        "|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| [{e['number']}](labs/{e['dir']}/) | {e['title']} | {e['status']} |"
        )
    lines += [
        "",
        f"*{len(entries)} labs. Generated from each lab's own `README.md` by "
        "`scripts/build-lab-index.py` and CI-enforced — the lab pages are "
        "authoritative for their titles and statuses; this table mirrors them.*",
        "",
        END,
    ]
    return "\n".join(lines)


def splice(readme_text: str, block: str) -> str:
    start = readme_text.find(BEGIN)
    stop = readme_text.find(END)
    if start == -1 or stop == -1:
        raise SystemExit(
            f"README.md is missing the generated-block markers.\n"
            f"Expected {BEGIN} ... {END}"
        )
    return readme_text[:start] + block + readme_text[stop + len(END) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if stale")
    args = parser.parse_args()

    if not LABS.exists():
        print("No labs/ directory; nothing to do.")
        return 0

    entries, errors = load()
    if errors:
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        print(
            "\nA lab that cannot be read is a lab the front page cannot mirror.",
            file=sys.stderr,
        )
        return 1

    current = README.read_text(encoding="utf-8")
    updated = splice(current, render(entries))

    if args.check:
        if current != updated:
            print("README lab index is stale.", file=sys.stderr)
            print("Run: python3 scripts/build-lab-index.py", file=sys.stderr)
            return 1
        print(f"README lab index up to date; {len(entries)} lab(s).")
    else:
        README.write_text(updated, encoding="utf-8")
        print(f"Wrote lab index into README.md; {len(entries)} lab(s).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
