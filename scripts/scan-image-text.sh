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

# Image-level accounting. Disposition is per IMAGE, not per variant: an image
# has two variants, so incrementing inside the variant loop can count one image
# twice. An image is EVALUATED only once both variants were produced, scanned
# and triaged successfully.
TOTAL=0; EVALUATED=0; UNSCANNED=0; EMPTY=0
IDX=0

for img in "$@"; do
  [ -f "$img" ] || continue
  TOTAL=$((TOTAL+1))

  # Work identity is a monotonic counter inside the already-unique mktemp dir.
  # Deriving it from basename made distinct images share every work path: a
  # later scanner failure then consumed an earlier image's stale report and the
  # gate passed an image it never scanned.
  IDX=$((IDX+1))
  stem="$WORK/img${IDX}"

  if ! tesseract "$img" "$stem" --psm 11 -l eng >/dev/null 2>&1; then
    echo "  ERROR OCR failed on $img — image NOT evaluated." >&2
    UNSCANNED=$((UNSCANNED+1)); continue
  fi

  if [ ! -s "${stem}.txt" ]; then
    # OCR ran and recovered no text. That is materially weaker than "no
    # sensitive text exists", so it is recorded and warned rather than treated
    # as clean — but it is not fatal: blocking every textless diagram makes a
    # gate people switch off, and section 4 manual review still applies.
    echo "  WARN  OCR recovered no text from $img — manual review still required." >&2
    EMPTY=$((EMPTY+1))
  fi

  # Second variant: OCR frequently inserts spaces inside identifiers. The
  # transform is checked, because this script runs without `set -e` and a silent
  # failure would leave the variant meant to recover spaced identifiers missing
  # while the raw variant scanned fine.
  if ! tr -d '[:blank:]' < "${stem}.txt" > "${stem}.despaced.txt"; then
    echo "  ERROR despacing transform failed for $img — image NOT evaluated." >&2
    UNSCANNED=$((UNSCANNED+1)); continue
  fi

  img_ok=1
  for variant in "${stem}.txt" "${stem}.despaced.txt"; do
    # Remove any prior report before the attempt: a stale file must never be
    # able to stand in for a scan that did not produce one.
    rm -f "${variant}.json"

    gitleaks dir "$variant" --config "$CONFIG" \
      --report-format json --report-path "${variant}.json" \
      --no-banner --exit-code 0 >/dev/null 2>&1
    grc=$?
    if [ "$grc" -ne 0 ]; then
      echo "  ERROR gitleaks exited $grc on $img — image NOT evaluated." >&2
      img_ok=0; break
    fi
    if [ ! -f "${variant}.json" ]; then
      echo "  ERROR gitleaks produced no report for $img — image NOT evaluated." >&2
      img_ok=0; break
    fi

    python3 "$(dirname "$0")/_ocr_triage.py" "$img" "${variant}.json"
    trc=$?
    case "$trc" in
      0) : ;;
      1) BLOCKED=1 ;;
      *) echo "  ERROR triage failed ($trc) on $img — image NOT evaluated." >&2
         img_ok=0; break ;;
    esac
  done

  if [ "$img_ok" -eq 1 ]; then EVALUATED=$((EVALUATED+1)); else UNSCANNED=$((UNSCANNED+1)); fi
done

echo "images: $TOTAL · evaluated: $EVALUATED · empty-text: $EMPTY · not evaluated: $UNSCANNED"

if [ "$((EVALUATED + UNSCANNED))" -ne "$TOTAL" ]; then
  echo "Image scan accounting error: $EVALUATED + $UNSCANNED != $TOTAL." >&2
  exit 1
fi

if [ "$UNSCANNED" -ne 0 ]; then
  echo "Image scan INCOMPLETE — $UNSCANNED image(s) not evaluated. Commit aborted."
  exit 1
fi

if [ "$BLOCKED" -ne 0 ]; then
  echo "Image scan failed. Commit aborted."
  exit 1
fi

echo "Image scan passed. Manual visual review still required (SANITIZATION.md section 4)."
