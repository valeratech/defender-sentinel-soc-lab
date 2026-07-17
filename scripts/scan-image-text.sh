#!/usr/bin/env bash
#
# scan-image-text.sh — OCR staged images and scan the extracted text.
#
# WHY THIS EXISTS
#   gitleaks reads bytes, not pixels. A screenshot containing a tenant GUID, a
#   UPN, or a lab public IP passes every textual scan, because the identifier is
#   encoded as image data. This script rasterizes that text back into something
#   scannable.
#
# WHAT IT IS NOT
#   A net, not a guarantee. OCR recovers word-shaped tokens well and
#   high-entropy hex poorly; a GUID in a screenshot may survive OCR too mangled
#   for any pattern to catch. A clean result here does NOT discharge the manual
#   visual review required by SANITIZATION.md section 4.
#
# TIERS
#   BLOCK — a rule matched a probable real value. Commit aborts.
#   WARN  — portal-chrome label detected ("Tenant ID", "Directory:"). Labels OCR
#           reliably even when the adjacent value does not, so they are a useful
#           prompt. They do not block: sanitized screenshots legitimately
#           contain these words, and a gate that fires on every clean image is a
#           gate that gets switched off.
#
set -uo pipefail

CONFIG="${GITLEAKS_OCR_CONFIG:-.gitleaks-ocr.toml}"
BLOCKED=0

for dep in tesseract gitleaks python3; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "ERROR: '$dep' not installed. Required to scan images before commit." >&2
    echo "  macOS: brew install tesseract gitleaks" >&2
    echo "  Linux: apt-get install -y tesseract-ocr; see github.com/gitleaks/gitleaks" >&2
    exit 1
  fi
done

[ -f "$CONFIG" ] || { echo "ERROR: OCR config '$CONFIG' not found." >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

for img in "$@"; do
  [ -f "$img" ] || continue
  stem="$WORK/$(basename "$img")"

  # --psm 11 (sparse text): portal screenshots are UI chrome, not prose.
  if ! tesseract "$img" "$stem" --psm 11 -l eng >/dev/null 2>&1; then
    echo "  WARN  OCR failed on $img - review manually." >&2
    continue
  fi
  [ -s "${stem}.txt" ] || continue

  # Whitespace-collapsed variant: OCR injects spaces into hex runs
  # ("72f988bf" -> "7 2(988bf"), defeating value patterns. Scan both.
  #
  # [:blank:] (space/tab), NOT [:space:] — the latter strips newlines, welding
  # the whole page into one line so patterns match across unrelated rows. Real
  # example: tesseract reads the external-link glyph as "@", and a collapsed
  # page turned "Learn more @" + "Your organization is not protected..." into a
  # false-positive email match. Line boundaries are load-bearing.
  tr -d '[:blank:]' < "${stem}.txt" > "${stem}.despaced.txt"

  for variant in "${stem}.txt" "${stem}.despaced.txt"; do
    gitleaks dir "$variant" --config "$CONFIG" \
      --report-format json --report-path "${variant}.json" \
      --no-banner --exit-code 0 >/dev/null 2>&1 || true
    [ -f "${variant}.json" ] || continue

    if ! python3 "$(dirname "$0")/_ocr_triage.py" "$img" "${variant}.json"; then
      BLOCKED=1
    fi
  done
done

if [ "$BLOCKED" -ne 0 ]; then
  echo "Image scan failed. Commit aborted."
  exit 1
fi

echo "Image scan passed. Manual visual review still required (SANITIZATION.md section 4)."
exit 0
