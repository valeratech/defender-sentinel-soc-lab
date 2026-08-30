#!/usr/bin/env python3
"""Generate docs/lab-coverage.md and gate posture entries against their labs.

Why this exists
---------------
`POS-022` is the Lab 01 finding. It was written into `posture.yml`, into
`docs/configuration-inventory.md`, and into the divergence table. It was never
written into `labs/01/README.md`, which went on printing the vendor claim
`POS-022` disproves — as a forward-looking prediction — for three days, while
every gate in this repository reported green.

Nothing was broken. The generators were in sync, because they check generated
docs against their sources and nothing checked hand-written prose against the
register. The absence of an error was not evidence the documentation worked.

That is `POS-011`'s shape, turned on the repo itself, and it is the specific
class this script closes: **a finding that reached the register and never
reached the lab it belongs to.**

What it can and cannot do
-------------------------
Every posture entry carries a `lab:` field, which is an assertion that the
entry belongs to that lab. This script checks the assertion is reciprocated —
that `labs/<lab>/README.md` cites the ID at least once.

It catches silence. It does not catch contradiction: a lab could cite
`POS-022` and still describe enrolment as working, and this would pass. But in
the case that motivated it, the silence and the contradiction were the same
fact — the lab never mentioned the entry *because* it had never been revisited.
Citation is not comprehension. It is a cheap mechanical proxy for "someone went
back," and going back is the part that was missed.

Enforcement
-----------
Blocking on every uncited entry today would fail 20 of 23 and turn CI red, and
a gate that is red on arrival gets switched off — the same reasoning that keeps
the OCR IP heuristic at warning tier (SANITIZATION.md section 4).

So the gate follows the repository's own 🔨/✅ semantics, where the gap between
them is load-bearing (documentation-standard.md section 6):

  🔨 built, documentation in progress — reported as debt in
                                       docs/lab-coverage.md. Does not fail.
  ✅ built, documented, validated     — uncited entry FAILS. Publishing a lab
                                       is the claim
                           that its writeup is complete; an orphaned finding
                           means it is not.

The debt is tracked rather than remembered, and the gate bites at exactly the
moment the claim goes public. `--strict` fails on any uncited entry regardless
of status, for when the backlog is cleared.

Two further contracts, both added in Stage 7:

  * The lab axis is every lab DIRECTORY unioned with every lab ID the register
    names — not the register alone. A published lab owning no entry used to be
    absent from this report entirely rather than shown as 0/0.
  * A lab whose status cannot be parsed FAILS. Only "✅" triggers the uncited
    check, so "unknown" was a silent exemption from gating.

Usage:
    python3 scripts/check-lab-coverage.py            # regenerate
    python3 scripts/check-lab-coverage.py --check    # CI: staleness + published labs
    python3 scripts/check-lab-coverage.py --strict   # fail on any uncited entry
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "posture.yml"
LABS = ROOT / "labs"
OUTPUT = ROOT / "docs" / "lab-coverage.md"

STATUS_RE = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*(.+?)\s*\|", re.MULTILINE)


def lab_readme(lab: str) -> pathlib.Path | None:
    """labs/01-device-registration-... -> the README for lab '01'."""
    for d in sorted(LABS.glob(f"{lab}-*")):
        p = d / "README.md"
        if p.exists():
            return p
    return None


def directory_labs() -> list[str]:
    """Lab IDs that exist as directories, independent of the register.

    The register is not the lab universe. Deriving the axis only from
    posture.yml made a lab that owns no entry invisible here — it could not
    appear, could not be counted, and could not be gated. Labs 25 and 26 were
    both published in that state. A lab with no entries is a legitimate
    outcome and renders 0/0; what is not legitimate is the report silently
    covering 25 of 27 labs while reading as though it covered all of them.

    Membership is the DIRECTORY, not the README inside it. Requiring a README
    here would rebuild the same hole one level down: a lab owning no register
    entry would drop out of the axis the moment its README went missing, and
    the register half of the union could not carry it. Whether the README
    exists is a question for lab_readme() and the missing-status gate, which
    is where it can be reported instead of disappearing.
    """
    return sorted(
        d.name.split("-", 1)[0]
        for d in LABS.glob("[0-9][0-9]-*")
        if d.is_dir()
    )


def lab_status(text: str) -> str:
    """Published (✅), documenting (🔨), planned (🔜), or unknown."""
    m = STATUS_RE.search(text)
    if not m:
        return "unknown"
    s = m.group(1)
    for marker in ("✅", "🔨", "🔜"):
        if marker in s:
            return marker
    return "unknown"


def audit(entries: list[dict]) -> list[dict]:
    # Union: every lab directory, plus any lab ID the register names even if
    # no such directory exists (a dangling lab: field must stay visible, not
    # be quietly dropped by switching the axis).
    labs = sorted(set(directory_labs()) | {e["lab"] for e in entries})
    rows = []
    for lab in labs:
        path = lab_readme(lab)
        text = path.read_text(encoding="utf-8") if path else ""
        ids = [e["id"] for e in entries if e["lab"] == lab]
        rows.append(
            {
                "lab": lab,
                "path": path.relative_to(ROOT).as_posix() if path else None,
                "status": lab_status(text) if path else "missing",
                "cited": [i for i in ids if i in text],
                "uncited": [i for i in ids if i not in text],
                "total": len(ids),
            }
        )
    return rows


def render(rows: list[dict]) -> str:
    total = sum(r["total"] for r in rows)
    cited = sum(len(r["cited"]) for r in rows)
    blocking = [r for r in rows if r["status"] == "✅" and r["uncited"]]

    L = [
        "# Posture Register ↔ Lab Coverage",
        "",
        "<!-- GENERATED by scripts/check-lab-coverage.py — do not edit by hand. -->",
        "",
        "Every entry in `posture.yml` names a `lab:`. That field asserts the entry",
        "belongs to that lab's writeup. This report checks the assertion is",
        "reciprocated — that the lab cites the ID at least once.",
        "",
        "An entry recorded in the register and never mentioned in its own lab is a",
        "finding that landed in the filing system and never reached the document it",
        "belongs to. It fails no gate: the generators verify generated docs against",
        "their sources, and prose is neither.",
        "",
        "The lab axis below is every lab directory in the repository, unioned with",
        "any lab ID the register names. A lab that owns no register entry renders",
        "`0/0`: that is a legitimate state and not a claim that it should own one.",
        "",
        f"**{cited} of {total} entries cited in their own lab.**",
        "",
        "| Lab | Status | Cited | Uncited |",
        "|---|---|---|---|",
    ]
    for r in rows:
        u = ", ".join(f"`{i}`" for i in r["uncited"]) or "—"
        L.append(f"| {r['lab']} | {r['status']} | {len(r['cited'])}/{r['total']} | {u} |")

    L += [
        "",
        "## Enforcement",
        "",
        "| Lab status | Uncited entry |",
        "|---|---|",
        "| 🔜 planned | not counted |",
        "| 🔨 built, documentation in progress | **debt** — reported here, does not fail CI |",
        "| ✅ built, documented, validated | **fails CI** |",
        "",
        "Marking a lab ✅ is the claim that its writeup is complete. An entry the",
        "register assigns to that lab and the lab never mentions contradicts the claim,",
        "so that is where the gate bites. Until then the debt is tracked rather than",
        "remembered — `docs/documentation-standard.md` §5.",
        "",
    ]
    if blocking:
        L += ["**Currently blocking:**", ""]
        for r in blocking:
            L.append(f"- Lab {r['lab']} (✅) — {', '.join('`'+i+'`' for i in r['uncited'])}")
        L.append("")
    else:
        L += [
            "No published lab has an uncited entry. Labs owning no register entry "
            "are in scope of this statement and cannot be blocked by it.",
            "",
        ]

    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="CI: staleness + published labs")
    ap.add_argument("--strict", action="store_true", help="fail on any uncited entry")
    args = ap.parse_args()

    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8")) or {}
    entries = data.get("entries") or []
    rows = audit(entries)
    content = render(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if args.check or args.strict:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != content:
            print("Lab coverage report is stale.", file=sys.stderr)
            print("Run: python3 scripts/check-lab-coverage.py", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")

    # S7-P06 — a lab whose status cannot be read drops out of enforcement
    # entirely: only "✅" fails, so "unknown" and "missing" were a silent
    # exemption. The gate must not decide a lab is safe because it could not
    # read it.
    unreadable = [r for r in rows if r["status"] in ("unknown", "missing")]
    if unreadable:
        for r in unreadable:
            if r["status"] == "missing":
                print(
                    f"FAIL lab {r['lab']}: no labs/{r['lab']}-*/README.md. The lab "
                    f"cannot be gated because it cannot be read.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"FAIL lab {r['lab']} ({r['path']}): no **Status** row carrying "
                    f"a ✅/🔨/🔜 marker. Status governs whether an uncited entry "
                    f"fails, so an unreadable status cannot be treated as safe.",
                    file=sys.stderr,
                )
        return 1

    failing = [
        r for r in rows
        if r["uncited"] and (args.strict or r["status"] == "✅")
    ]
    if failing:
        for r in failing:
            ids = ", ".join(r["uncited"])
            print(
                f"FAIL lab {r['lab']} ({r['status']}): register assigns "
                f"{ids} to this lab; {r['path']} does not cite them.",
                file=sys.stderr,
            )
        print(
            "\nA finding recorded in the register and absent from its own lab is "
            "not documented.",
            file=sys.stderr,
        )
        return 1

    if args.check or args.strict:
        print("Lab coverage report up to date; no published lab has an uncited entry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
