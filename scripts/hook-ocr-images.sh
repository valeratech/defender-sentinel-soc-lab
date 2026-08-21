#!/usr/bin/env bash
# hook-ocr-images.sh — OCR scan, gated on policy (review P13).
#
# Same rationale as hook-strip-images.sh: with fail_fast=false, a policy-
# rejected image would still reach the OCR hook. Scanning is not modifying,
# but treating a rejected object as an ordinary supported image is exactly
# what facet (g) exists to prevent (SANITIZATION.md section 10).
set -uo pipefail
if ! bash "$(dirname "$0")/check-image-policy.sh" "$@"; then
  echo "OCR refused: one or more staged images fail image policy." >&2
  exit 1
fi
exec bash "$(dirname "$0")/scan-image-text.sh" "$@"
