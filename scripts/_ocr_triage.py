#!/usr/bin/env python3
"""Triage a gitleaks report produced from OCR-extracted image text.

Exit contract:
    0  clean, or warnings only
    1  blocking findings present
    2  instrument error - the report could not be trusted, so the image
       has NOT been evaluated and the caller must treat it as unscanned

Nothing here prints a matched value or any substring of one. Diagnostics carry
the image path, the rule id, the tier and a count. Error paths print the
exception *type* only: a report-read failure can otherwise echo file content
into the log, which would reintroduce the disclosure this module exists to
avoid.
"""
import json
import pathlib
import sys
from collections import Counter

ADVICE = "Re-crop or apply an opaque redaction, then flatten the image."

if len(sys.argv) != 3:
    print("  ERROR triage called with wrong argument count", file=sys.stderr)
    sys.exit(2)

img, report = sys.argv[1], sys.argv[2]

try:
    raw = pathlib.Path(report).read_text()
    # An empty *file* is a scan that produced no report; an empty *list* is a
    # scan that ran and found nothing. Normalising the former into the latter
    # is a false pass, so the emptiness check precedes parsing.
    if not raw.strip():
        print("  ERROR gitleaks report is empty", file=sys.stderr)
        sys.exit(2)
    findings = json.loads(raw)
except Exception as exc:
    print(f"  ERROR triage could not read report: {type(exc).__name__}", file=sys.stderr)
    sys.exit(2)

# Syntactically valid JSON of the wrong shape must not read as "zero findings".
if not isinstance(findings, list) or not all(isinstance(f, dict) for f in findings):
    print("  ERROR gitleaks report is not a list of findings", file=sys.stderr)
    sys.exit(2)

def tier(finding):
    tags = [str(t).lower() for t in (finding.get("Tags") or [])]
    return "warn" if "label" in tags else "block"

warn = [f for f in findings if tier(f) == "warn"]
block = [f for f in findings if tier(f) == "block"]

# The matched text is used as a de-duplication key and is never printed.
seen = set()
for f in warn:
    rule = f.get("RuleID") or "?"
    key = (rule, (f.get("Match") or "").strip())
    if key in seen:
        continue
    seen.add(key)
    print(f"  WARN  {img}: [{rule}] context or degraded match - review by eye.")

if block:
    print(f"\n  BLOCKED: sensitive text detected inside image: {img}")
    for rule, n in sorted(Counter(f.get("RuleID") or "?" for f in block).items()):
        print(f"    [{rule}] {n} match(es)")
    print(f"    {ADVICE}")
    print("    See SANITIZATION.md section 4.\n")
    sys.exit(1)

sys.exit(0)
