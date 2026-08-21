#!/usr/bin/env bash
# ci-image-census.sh — tracked-tree image census (advisory/detective CI layer).
#
# Boundary is git membership: git ls-files -z, hard-checked before its output
# is consumed (a failed enumeration must never look like an empty repository).
# Filenames stay NUL-delimited end to end.
#
# Layer 1 (extension): any tracked file with an image-like extension
#   (supported or rejected, ANY case) must be exact-lowercase supported.
# Layer 2 (content): MIME detection over every tracked file — output and exit
#   status captured separately, detection failure fails closed. Any image/*
#   without a supported lowercase extension fails. Floor is libmagic signature
#   knowledge; unknown formats fall back to layer 1.
# Layer 3 (single-frame, AUD-007 facet g): supported images are checked by the
#   content-driven detector; animated PNG/WebP is rejected before OCR — a
#   later frame can carry text single-raster OCR never sees.
# (SANITIZATION.md section 10.)
#
# --list0 : emit NUL-delimited supported CLEAN image paths on stdout for the
#           OCR step. Verdict logic identical; report lines go to stderr.
set -uo pipefail

. "$(dirname "$0")/image-formats.sh"

LIST0=0
[ "${1:-}" = "--list0" ] && LIST0=1

in_list() {
  local w="$1"; shift
  local x
  for x in $*; do [ "$w" = "$x" ] && return 0; done
  return 1
}

mime_for_ext() { # supported ext -> bound MIME, empty if unmapped
  local e="$1" pair
  for pair in $SUPPORTED_IMAGE_MIME_MAP; do
    [ "${pair%%=*}" = "$e" ] && { printf '%s' "${pair#*=}"; return 0; }
  done
  return 1
}

# ── Hard-checked tracked enumeration (P1): never consume a failed stream ──
LSFILE="$(mktemp)" || { echo "FAIL  could not create temp file for enumeration." >&2; exit 1; }
trap 'rm -f "$LSFILE"' EXIT
if ! git ls-files -z > "$LSFILE"; then
  echo "FAIL  git ls-files failed — tracked boundary unavailable; failing closed." >&2
  exit 1
fi

FAIL=0
TRACKED=0
SUPPORTED_COUNT=0

while IFS= read -r -d '' f; do
  TRACKED=$((TRACKED+1))
  base="${f##*/}"
  ext=""
  case "$base" in *.*) ext="${base##*.}" ;; esac
  lower="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"

  imagelike=0
  if [ -n "$ext" ] && { in_list "$lower" $SUPPORTED_IMAGE_EXTS || in_list "$lower" $REJECTED_IMAGE_EXTS; }; then
    imagelike=1
  fi

  supported_ok=0
  if [ "$imagelike" -eq 1 ]; then
    if in_list "$ext" $SUPPORTED_IMAGE_EXTS; then
      supported_ok=1
    else
      echo "FAIL  $f — image-like extension '.$ext' violates the lowercase supported set (SANITIZATION.md section 10)." >&2
      FAIL=1
      continue
    fi
  fi

  # ── Layer 2 (P4): capture MIME output and status separately ──
  mime="$(file --brief --mime-type -- "$f" 2>/dev/null)"; mrc=$?
  if [ "$mrc" -ne 0 ] || [ -z "$mime" ]; then
    echo "FAIL  $f — MIME detection failed (rc=$mrc); failing closed (SANITIZATION.md section 10)." >&2
    FAIL=1
    continue
  fi
  case "$mime" in
    image/svg+xml)
      echo "FAIL  $f — detected SVG content; SVG is a rejected publication image format (SANITIZATION.md section 10)." >&2
      FAIL=1
      continue
      ;;
    image/*)
      if [ "$supported_ok" -ne 1 ]; then
        echo "FAIL  $f — detected image content ($mime) without a supported lowercase image extension (SANITIZATION.md section 10)." >&2
        FAIL=1
        continue
      fi
      ;;
  esac

  # ── Content↔extension binding (P11): the extension is only valid over its
  # own format. Applies to every supported-extension file regardless of what
  # libmagic detected — text/plain under .png is as much a mismatch as
  # image/gif under .png.
  if [ "$supported_ok" -eq 1 ]; then
    bound="$(mime_for_ext "$ext")" || bound=""
    if [ -z "$bound" ]; then
      echo "FAIL  $f — supported extension '.$ext' has no MIME binding in the authority; failing closed (SANITIZATION.md section 10)." >&2
      FAIL=1
      continue
    fi
    if [ "$mime" != "$bound" ]; then
      echo "FAIL  $f — content/extension mismatch: detected $mime under '.$ext' (bound to $bound) (SANITIZATION.md section 10)." >&2
      FAIL=1
      continue
    fi
  fi

  # ── Layer 3 (facet g): single-frame contract on supported images ──
  if [ "$supported_ok" -eq 1 ]; then
    python3 "$(dirname "$0")/detect-animation.py" "$f"
    arc=$?
    case "$arc" in
      0) : ;;  # structurally complete single image
      1)
        echo "FAIL  $f — multi-image content (APNG/animated WebP/JPEG MPO); supported publication images must contain exactly one image (SANITIZATION.md section 10)." >&2
        FAIL=1
        continue
        ;;
      3)
        # Every supported extension is governed by the single-image contract
        # (review P22): "no contract applies" means the content is not a
        # recognised supported container at all. Fail closed.
        echo "FAIL  $f — content is not a recognised PNG/WebP/JPEG container; the single-image contract cannot be evaluated, failing closed (SANITIZATION.md section 10)." >&2
        FAIL=1
        continue
        ;;
      *)
        echo "FAIL  $f — single-image check could not parse this image (rc=$arc); failing closed (SANITIZATION.md section 10)." >&2
        FAIL=1
        continue
        ;;
    esac
    SUPPORTED_COUNT=$((SUPPORTED_COUNT+1))
    [ "$LIST0" -eq 1 ] && printf '%s\0' "$f"
  fi
done < "$LSFILE"

{
  echo "census: tracked files: $TRACKED · supported clean images: $SUPPORTED_COUNT"
  if [ "$FAIL" -eq 0 ]; then
    if [ "$SUPPORTED_COUNT" -eq 0 ]; then
      echo "census: no images in the tracked tree — nothing further to scan."
    fi
    echo "census: PASS"
  else
    echo "census: FAIL"
  fi
} >&2
exit $FAIL
