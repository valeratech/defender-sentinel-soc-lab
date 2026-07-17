#!/usr/bin/env python3
"""Split gitleaks OCR findings into warn (labels) and block (values) tiers.

Exit 0 = warnings only or clean. Exit 1 = blocking findings present.
"""
import json
import pathlib
import sys

img, report = sys.argv[1], sys.argv[2]

try:
    findings = json.loads(pathlib.Path(report).read_text() or "[]")
except Exception:
    sys.exit(0)

block, warn = [], []
for f in findings:
    tags = [t.lower() for t in (f.get("Tags") or [])]
    (warn if "label" in tags else block).append(f)

ADVICE = {
    "ocr-identifier-label": "identifier label - confirm the adjacent value is redacted",
    "ocr-directory-chrome": "directory/account chrome - crop tighter if not needed",
    "ocr-ip-context":       "wording that usually precedes an IP - check for an address beside it",
    "ocr-fuzzy-ipv4":       "possible IP with OCR-eaten separators - verify by eye, OCR cannot confirm",
}

seen = set()
for f in warn:
    rule = f.get("RuleID") or "?"
    m = (f.get("Match") or "").strip()[:40]
    if (rule, m) in seen:
        continue
    seen.add((rule, m))
    advice = ADVICE.get(rule, "review this")
    print(f"  WARN  {img}: {m!r} - {advice}")

if block:
    print("")
    print(f"  BLOCKED: sensitive text detected inside image: {img}")
    for f in block:
        print(f"    [{f.get('RuleID')}] {(f.get('Match') or '').strip()[:60]!r}")
    print("    Re-crop or apply an opaque redaction, then flatten the image.")
    print("    See SANITIZATION.md section 4.")
    print("")
    sys.exit(1)

sys.exit(0)
