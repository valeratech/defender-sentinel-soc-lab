#!/usr/bin/env python3
"""Referential-integrity validator for docs/evidence-notes/.   (rev 5)

A VALIDATOR, not a generator: it produces no document and there is no index to
regenerate. `--check` is parsed explicitly and accepted as a no-op alias so CI
invocations stay uniform with the generator gates; any other argument is an
error. Exit 0 = every note valid; exit 1 with one line per defect.

Schema enforced EXACTLY as documented:
  frontmatter keys == {title, date, artifacts, corrections} — no extras,
  no omissions, and specifically none of the retired course keys
  (module/section/verdict, called out by name when seen).
  title: str; date: str/date; corrections: list (possibly empty);
  artifacts: mapping with only known collections, each a list:
    labs        -> labs/<NN>-*/ directory exists
    posture     -> POS-NNN id present in posture.yml
    divergences -> integer row present in docs/configuration-inventory.md
    kql         -> path is under kql/ AND exists
    detections  -> DET-NNN has a real spec file under detections/
  Malformed values are controlled FAILs, never tracebacks.
"""
import glob, re, sys, os

ROOT = os.getcwd()
NOTES = os.path.join(ROOT, "docs", "evidence-notes")
REQUIRED = {"title", "date", "artifacts", "corrections"}
RETIRED = {"module", "section", "verdict"}
KNOWN_ARTIFACTS = {"labs", "posture", "divergences", "kql", "detections"}


def divergence_table(inv_text, inv_rel):
    """Return (member_row_ids, defects) for the CANONICAL divergence table.

    A divergence row is a MEMBER of one specific Markdown table, not any line in the
    file that happens to be pipe-delimited with a leading integer. The distinction is
    load-bearing: 68 governed rows once sat after two intervening prose sections,
    rendered as paragraph text by every GFM renderer, and were still accepted here
    because the old test was a line shape.

    The table is located structurally - the header row whose first cell is the row-id
    column, immediately followed by a delimiter row - and membership ends at the first
    line that is not a table row. Nothing about the table's SIZE is asserted: the row
    count is whatever the document currently defines, so this stays true as rows are
    added.
    """
    lines = inv_text.splitlines()
    start = None
    for i in range(len(lines) - 1):
        if (re.match(r"^\|\s*#\s*\|", lines[i])
                and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1])):
            start = i + 2
            break
    if start is None:
        return set(), [f"{inv_rel}: canonical divergence table not found "
                       f"(no '| # |' header followed by a delimiter row)"]

    members, order = set(), []
    end = start
    for i in range(start, len(lines)):
        if not lines[i].startswith("|"):
            end = i
            break
        m = re.match(r"^\|\s*(\d+)\s*\|", lines[i])
        if m:
            members.add(int(m.group(1)))
            order.append(int(m.group(1)))
    else:
        end = len(lines)

    defects = []
    if len(order) != len(members):
        dupes = sorted({r for r in order if order.count(r) > 1})
        defects.append(f"{inv_rel}: duplicate divergence row id(s) {dupes}")

    # The row-id namespace is a dense ascending sequence from 1. Enforced against the
    # table's OWN current contents: the expected id at each position is derived from
    # the previous row, so the rule stays true at any table size and no maximum is
    # bound here. A gap or a swap is a namespace defect even when every surviving row
    # still resolves for every citation.
    if order:
        if order[0] != 1:
            defects.append(f"{inv_rel}: divergence rows start at {order[0]}, expected 1")
        for prev, cur in zip(order, order[1:]):
            if cur != prev + 1:
                defects.append(
                    f"{inv_rel}: divergence row {cur} follows {prev} "
                    f"({'gap' if cur > prev + 1 else 'out of order'}; expected {prev + 1})"
                )

    # A row-shaped line ANYWHERE else in the document is a divergence record that has
    # fallen out of the table. Reporting it is the whole point: it is invisible to a
    # reader of the rendered page and was invisible to this checker before.
    for i, line in enumerate(lines):
        if start <= i < end:
            continue
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if m:
            defects.append(
                f"{inv_rel}:{i + 1}: divergence row {m.group(1)} is outside the "
                f"canonical divergence table (renders as prose, not a table row)"
            )
    return members, defects


def main():
    args = sys.argv[1:]
    if args and args != ["--check"]:
        print(f"usage: check-evidence-notes.py [--check]   (unknown: {args})", file=sys.stderr)
        sys.exit(2)
    errors = []
    try:
        import yaml
    except ImportError:
        print("FAIL: PyYAML unavailable", file=sys.stderr); sys.exit(1)
    posture = open(os.path.join(ROOT, "posture.yml"), encoding="utf-8").read()
    pos_ids = set(re.findall(r"id:\s*\"?(POS-\d+)\"?", posture))
    inv = open(os.path.join(ROOT, "docs", "configuration-inventory.md"), encoding="utf-8").read()
    inv_rel = os.path.join("docs", "configuration-inventory.md")
    div_rows, div_defects = divergence_table(inv, inv_rel)
    errors.extend(div_defects)
    labs = {os.path.basename(d.rstrip("/")).split("-")[0]
            for d in glob.glob(os.path.join(ROOT, "labs", "*", ""))}
    det_specs = set()
    for p in glob.glob(os.path.join(ROOT, "detections", "**", "*.md"), recursive=True):
        m = re.search(r"(DET-\d+)", os.path.basename(p))
        if m: det_specs.add(m.group(1))

    notes = sorted(glob.glob(os.path.join(NOTES, "*.md")))
    if not notes: errors.append(f"no notes found under {NOTES}")
    for p in notes:
        rel = os.path.relpath(p, ROOT)
        raw = open(p, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
        if not m: errors.append(f"{rel}: missing frontmatter"); continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception as ex:
            errors.append(f"{rel}: frontmatter parse error: {ex}"); continue
        if not isinstance(fm, dict):
            errors.append(f"{rel}: frontmatter is not a mapping"); continue
        keys = set(fm)
        for k in sorted(keys & RETIRED):
            errors.append(f"{rel}: retired course-layer key `{k}` survives")
        for k in sorted(REQUIRED - keys):
            errors.append(f"{rel}: missing required key `{k}`")
        for k in sorted(keys - REQUIRED - RETIRED):
            errors.append(f"{rel}: unexpected key `{k}` — schema is exactly {sorted(REQUIRED)}")
        if "title" in fm and not isinstance(fm["title"], str):
            errors.append(f"{rel}: title is not a string")
        if "date" in fm:
            import datetime
            if not isinstance(fm["date"], (str, datetime.date)):
                errors.append(f"{rel}: date is not a scalar date/string")
        if "corrections" in fm and not isinstance(fm["corrections"], list):
            errors.append(f"{rel}: corrections is not a list (null is not an empty list)")
        arts = fm.get("artifacts")
        if not isinstance(arts, dict):
            if "artifacts" in fm:
                errors.append(f"{rel}: artifacts is not a mapping (null is not an empty mapping)")
            arts = {}
        for k in sorted(set(arts) - KNOWN_ARTIFACTS):
            errors.append(f"{rel}: unknown artifacts collection `{k}`")
        def aslist(key):
            v = arts.get(key)
            if v is None: return []
            if not isinstance(v, list):
                errors.append(f"{rel}: artifacts.{key} is not a list"); return []
            return v
        for lab in aslist("labs"):
            if str(lab).zfill(2) not in labs:
                errors.append(f"{rel}: cited lab {lab!r} does not exist")
        for pid in aslist("posture"):
            if not isinstance(pid, str) or not re.fullmatch(r"POS-\d+", pid):
                errors.append(f"{rel}: malformed posture id {pid!r}")
            elif pid not in pos_ids:
                errors.append(f"{rel}: cited {pid} not found in posture.yml")
        for d in aslist("divergences"):
            if not (isinstance(d, int) or (isinstance(d, str) and d.isdigit())):
                errors.append(f"{rel}: malformed divergence row ref {d!r}")
            elif int(d) not in div_rows:
                errors.append(f"{rel}: cited divergence row {d} is not a member of the canonical divergence table")
        kql_root = os.path.realpath(os.path.join(ROOT, "kql"))
        for q in aslist("kql"):
            qs = str(q)
            real = os.path.realpath(os.path.join(ROOT, qs))
            if not (real == kql_root or real.startswith(kql_root + os.sep)):
                errors.append(f"{rel}: kql ref {qs!r} does not resolve under kql/ (canonical containment)")
            elif not os.path.exists(real):
                errors.append(f"{rel}: kql ref {qs} does not exist")
        for det in aslist("detections"):
            if not isinstance(det, str) or not re.fullmatch(r"DET-\d+", det):
                errors.append(f"{rel}: malformed detection ref {det!r}")
            elif det not in det_specs:
                errors.append(f"{rel}: cited {det} has no detection spec")
    for e in errors: print(f"FAIL: {e}", file=sys.stderr)
    print(f"check-evidence-notes: {len(notes)} notes, {len(errors)} defect(s)")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
