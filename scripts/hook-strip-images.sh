#!/usr/bin/env bash
# hook-strip-images.sh — metadata strip, gated on policy (review P13).
#
# pre-commit's fail_fast defaults to false: a file BLOCKed by image-policy
# would otherwise still reach this in-place modifying hook in the same run.
# This wrapper re-runs the policy verdict on its own inputs and refuses to
# modify anything unless every input passes — the strip must never touch an
# object the policy has rejected (SANITIZATION.md section 10).
set -uo pipefail
if ! bash "$(dirname "$0")/check-image-policy.sh" "$@"; then
  echo "strip refused: one or more staged images fail image policy; nothing was modified." >&2
  exit 1
fi
command -v exiftool >/dev/null 2>&1 || { echo "exiftool not installed - required before committing images" >&2; exit 1; }
exiftool -all= -overwrite_original "$@" && git add "$@"
