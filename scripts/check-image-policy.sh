#!/usr/bin/env bash
# check-image-policy.sh — staged-filename image policy (pre-commit hook logic).
#
# Receives staged filenames from pre-commit (broad any-case image-extension
# trigger routes candidates here; POLICY lives in this logic, not the regex).
# Verdicts, from the machine authority:
#   - exact-lowercase supported extension            -> pass
#   - case variant of a supported extension (.PNG)   -> BLOCK: rename to lowercase
#   - rejected extension, any case (gif/svg/bmp/...) -> BLOCK: unsupported format
# See SANITIZATION.md section 10.
set -uo pipefail

# shellcheck source=image-formats.sh
. "$(dirname "$0")/image-formats.sh"

in_list() { # word list...
  local w="$1"; shift
  local x
  for x in $*; do [ "$w" = "$x" ] && return 0; done
  return 1
}

BLOCKED=0
for f in "$@"; do
  base="${f##*/}"
  case "$base" in *.*) ext="${base##*.}" ;; *) continue ;; esac
  lower="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  if in_list "$ext" $SUPPORTED_IMAGE_EXTS; then
    # Content↔extension binding (P11): detected MIME must equal the mapped
    # value for this extension; smuggled formats block here, before any
    # strip/OCR hook can treat them as ordinary supported images.
    if [ -f "$f" ]; then
      if ! command -v file >/dev/null 2>&1; then
        echo "BLOCK  $f — 'file' unavailable; content/extension binding cannot be verified, failing closed (SANITIZATION.md section 10)." >&2
        BLOCKED=1
        continue
      fi
      mime="$(file --brief --mime-type -- "$f" 2>/dev/null)"; mrc=$?
      if [ "$mrc" -ne 0 ] || [ -z "$mime" ]; then
        echo "BLOCK  $f — MIME detection failed; failing closed (SANITIZATION.md section 10)." >&2
        BLOCKED=1
        continue
      fi
      bound=""
      for pair in $SUPPORTED_IMAGE_MIME_MAP; do
        [ "${pair%%=*}" = "$ext" ] && bound="${pair#*=}"
      done
      if [ -z "$bound" ] || [ "$mime" != "$bound" ]; then
        echo "BLOCK  $f — content/extension mismatch: detected $mime under '.$ext' (bound to ${bound:-nothing}) (SANITIZATION.md section 10)." >&2
        BLOCKED=1
        continue
      fi
    fi
    # Single-frame contract (facet g): reject animated content before it
    # reaches strip/OCR. Content-driven check; rc 3 = no frame contract.
    if [ -f "$f" ]; then
      python3 "$(dirname "$0")/detect-animation.py" "$f"
      arc=$?
      case "$arc" in
        0) : ;;
        1) echo "BLOCK  $f — multi-image content (APNG/animated WebP/JPEG MPO); supported publication images must contain exactly one image (SANITIZATION.md section 10)." >&2; BLOCKED=1 ;;
        3) echo "BLOCK  $f — content is not a recognised PNG/WebP/JPEG container; the single-image contract cannot be evaluated, failing closed (SANITIZATION.md section 10)." >&2; BLOCKED=1 ;;
        *) echo "BLOCK  $f — single-image check could not parse this image; failing closed (SANITIZATION.md section 10)." >&2; BLOCKED=1 ;;
      esac
    fi
    continue
  elif in_list "$lower" $SUPPORTED_IMAGE_EXTS; then
    echo "BLOCK  $f — mis-cased image extension '.$ext'. Supported formats are lowercase-exact; rename to '.$lower' (SANITIZATION.md section 10)." >&2
    BLOCKED=1
  elif in_list "$lower" $REJECTED_IMAGE_EXTS; then
    echo "BLOCK  $f — '.$ext' is not a supported publication image format (SANITIZATION.md section 10)." >&2
    BLOCKED=1
  fi
done
exit $BLOCKED
