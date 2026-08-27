#!/usr/bin/env python3
"""Generate docs/attack-coverage.md from detection spec frontmatter.

The README advertises an ATT&CK coverage matrix. A hand-maintained matrix
drifts from the detections it claims to describe within about two weeks, so it
is derived instead: the detection specs are the source of truth and this
regenerates the table from them.

Deliberate design point: a detection with `validated: false` is reported as
CLAIMED, not COVERED. The gap between "I wrote a rule" and "I proved it fires"
is the interesting part of a coverage map, and collapsing the two is how
coverage maps end up lying.

Usage:
    python3 scripts/build-attack-matrix.py [--check]

    --check  exit 1 if the committed matrix is stale (for CI)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DETECTIONS = ROOT / "detections"
OUTPUT = ROOT / "docs" / "attack-coverage.md"
TEMPLATE = DETECTIONS / "_TEMPLATE.md"

# Enumerated frontmatter fields. The ALLOWED VALUES ARE NOT DEFINED HERE: they are
# re-derived from the trailing comment on the corresponding line of the detection
# template, which is the declared schema authority. Two independently maintained
# copies of a vocabulary drift apart, and the drift stays invisible until something
# reads both - so there is one copy, and this reads it.
ENUM_FIELDS = ("status", "platform", "rule_type", "severity")

TACTIC_NAMES = {
    "TA0001": "Initial Access", "TA0002": "Execution", "TA0003": "Persistence",
    "TA0004": "Privilege Escalation", "TA0005": "Defense Evasion",
    "TA0006": "Credential Access", "TA0007": "Discovery",
    "TA0008": "Lateral Movement", "TA0009": "Collection",
    "TA0010": "Exfiltration", "TA0011": "Command and Control",
    "TA0040": "Impact", "TA0043": "Reconnaissance",
    "TA0042": "Resource Development",
}


def parse_frontmatter(text: str) -> dict | None:
    """Minimal YAML frontmatter reader.

    Intentionally dependency-free: this runs in a pre-commit hook and in CI,
    and adding PyYAML to make a contributor's first commit fail is a poor
    trade. Handles only the scalar/list subset the template uses.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None

    data: dict = {}
    key = None
    for raw in m.group(1).splitlines():
        line = raw.split(" #")[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s+-\s+", line):
            if key:
                data.setdefault(key, []).append(line.split("-", 1)[1].strip())
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            data[key] = v if v else []
    return data


class SchemaError(Exception):
    """The declared schema authority is missing or unusable."""


def truthy(v) -> bool:
    return str(v).strip().lower() in {"true", "yes", "1"}


def collect() -> list[dict]:
    specs = []
    for path in sorted(DETECTIONS.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm or not fm.get("id"):
            continue
        if str(fm.get("id")).strip() == "DET-000":  # untouched template copy
            continue
        fm["_path"] = os.path.relpath(path, OUTPUT.parent).replace(os.sep, "/")
        fm["_abs"] = path
        specs.append(fm)
    return specs


def declared_vocabulary() -> dict[str, list[str]]:
    """Read the allowed values for each enumerated field off the detection template.

    The template line carries them as a trailing comment:

        rule_type: scheduled      # scheduled | nrt | custom-detection | ...

    Deriving them here rather than restating them means the template stays the one
    place a value is declared. A field with no parseable comment is reported rather
    than silently treated as unconstrained.
    """
    if not TEMPLATE.exists():
        raise SchemaError(f"schema authority missing: {TEMPLATE.relative_to(ROOT)}")
    vocab: dict[str, list[str]] = {}
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\w+):\s*\S+\s*#\s*(.+)$", line)
        if m and m.group(1) in ENUM_FIELDS:
            vocab[m.group(1)] = [v.strip() for v in m.group(2).split("|") if v.strip()]
    missing = [f for f in ENUM_FIELDS if f not in vocab]
    if missing:
        raise SchemaError(
            f"{TEMPLATE.relative_to(ROOT)} declares no allowed values for: "
            + ", ".join(missing)
        )
    return vocab


def validate_schema(specs: list[dict]) -> list[str]:
    """Every spec's enumerated fields must hold a value the template declares."""
    vocab = declared_vocabulary()
    errors = []
    for s in specs:
        for field in ENUM_FIELDS:
            value = str(s.get(field, "")).strip()
            if value not in vocab[field]:
                errors.append(
                    f"{s['_path']}: {field}={value!r} is not in the vocabulary declared "
                    f"by {TEMPLATE.relative_to(ROOT)} ({' | '.join(vocab[field])})"
                )
    return errors


def validate_links(specs: list[dict]) -> list[str]:
    """Every generated detection link must resolve from the generated document.

    A generator and its output agreeing with each other proves only that they were
    produced by the same code. This resolves each emitted href against the directory
    the document lives in, so a generator that is wrong and an artifact that is wrong
    in the same way still fail.
    """
    errors = []
    for s in specs:
        target = (OUTPUT.parent / s["_path"]).resolve()
        if not target.is_file():
            errors.append(
                f"{OUTPUT.relative_to(ROOT)}: link for {s['id']} -> {s['_path']} "
                f"does not resolve from {OUTPUT.parent.relative_to(ROOT)}/"
            )
    return errors


def render(specs: list[dict]) -> str:
    lines = [
        "# ATT&CK Coverage",
        "",
        "<!-- GENERATED by scripts/build-attack-matrix.py — do not edit by hand. -->",
        "",
        "Derived from detection spec frontmatter in `detections/`.",
        "",
        '**COVERED** means every rule mapped to that tactic has been proven to fire',
        "on a known-true event (`validated: true`). **PARTIAL** means some have.",
        "**CLAIMED** means none have. The distinction is the point of this table: an",
        "unvalidated rule is a hypothesis, not coverage.",
        "",
    ]

    if not specs:
        lines += ["*No detections specified yet.*", ""]
        return "\n".join(lines)

    active = [s for s in specs if str(s.get("status")).strip() != "retired"]
    validated = [s for s in active if truthy(s.get("validated"))]

    lines += [
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| Detections specified | {len(specs)} |",
        f"| Active (not retired) | {len(active)} |",
        f"| Validated (proven to fire) | {len(validated)} |",
        f"| Unvalidated | {len(active) - len(validated)} |",
        "",
        "## By Tactic",
        "",
        "| Tactic | Techniques | Detections | State |",
        "|---|---|---|---|",
    ]

    by_tactic: dict[str, list[dict]] = {}
    for s in active:
        for t in s.get("tactics") or ["(unmapped)"]:
            by_tactic.setdefault(str(t).strip(), []).append(s)

    for tactic in sorted(by_tactic):
        rows = by_tactic[tactic]
        name = TACTIC_NAMES.get(tactic, tactic)
        techs = sorted({t for r in rows for t in (r.get("techniques") or [])})
        ids = ", ".join(f"`{r['id']}`" for r in rows)
        n_ok = sum(1 for r in rows if truthy(r.get("validated")))
        if n_ok == 0:
            state = f"CLAIMED (0/{len(rows)})"
        elif n_ok == len(rows):
            state = f"COVERED ({n_ok}/{len(rows)})"
        else:
            # Partial must never render as COVERED. A single validated rule does
            # not make a tactic green when its sibling techniques are unproven —
            # that is exactly the overstatement this table exists to prevent.
            state = f"PARTIAL ({n_ok}/{len(rows)})"
        lines.append(
            f"| {name} (`{tactic}`) | {', '.join(techs) or '—'} | {ids} | {state} |"
        )

    lines += ["", "## Detections", "",
              "| ID | Name | Platform | Type | Severity | Status | Validated |",
              "|---|---|---|---|---|---|---|"]
    for s in sorted(specs, key=lambda x: str(x["id"])):
        lines.append(
            f"| [`{s['id']}`]({s['_path']}) | {s.get('name','')} | "
            f"{s.get('platform','')} | {s.get('rule_type','')} | "
            f"{s.get('severity','')} | {s.get('status','')} | "
            f"{'yes' if truthy(s.get('validated')) else '**no**'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if committed matrix is stale")
    args = ap.parse_args()

    specs = collect()

    try:
        problems = validate_schema(specs) + validate_links(specs)
    except SchemaError as exc:
        print(f"detection schema: {exc}", file=sys.stderr)
        return 1
    if problems:
        for p in problems:
            print(f"detection schema/link: {p}", file=sys.stderr)
        print(f"{len(problems)} defect(s); refusing to generate.", file=sys.stderr)
        return 1

    content = render(specs)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != content:
            print("ATT&CK coverage matrix is stale.", file=sys.stderr)
            print("Run: python3 scripts/build-attack-matrix.py", file=sys.stderr)
            return 1
        print("ATT&CK coverage matrix up to date.")
        return 0

    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
