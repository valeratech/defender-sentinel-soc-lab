#!/usr/bin/env bash
# image-formats.sh — the single machine authority for publication image formats.
#
# WHY THIS EXISTS
#   AUD-007: five surfaces each carried their own hardcoded extension list, and
#   the lists disagreed (gif was metadata-stripped but never OCR-scanned or
#   censused). Divergence was latent, not enforced against. This file is the
#   one place the sets are defined; scripts/check-image-format-parity.py fails
#   the build if any surface drifts from it.
#
# RULES
#   - Extensions are lowercase-exact. A mis-cased extension (.PNG) is rejected
#     at the policy hook and the CI census rather than taught to every surface.
#   - REJECTED_IMAGE_EXTS and GITATTRIBUTES_BINARY_IMAGE_EXTS are DERIVED.
#     Never edit the derived lines; edit the components and the derivations
#     follow. The parity checker re-derives and compares.
#   - Policy rationale lives in SANITIZATION.md section 10, which mirrors these
#     sets in a fenced machine-readable block that the parity checker verifies.
readonly SUPPORTED_IMAGE_EXTS="png jpg jpeg webp"
# Single-image contract (AUD-007 facet g): every supported publication image
# must represent exactly one OCR-relevant image — PNG/WebP animation and JPEG
# Multi-Picture Format (MPO) are rejected; scripts/detect-animation.py
# enforces this by content, not by this list — the list exists so prose and
# policy surfaces can be contract-checked against it.
readonly SINGLE_FRAME_ENFORCED_EXTS="png webp jpg jpeg"
# Content↔extension binding (AUD-007 facet g / review P11): a supported
# extension is only valid over its own format. Detected MIME must equal the
# mapped value; a GIF renamed .png is a mismatch, not a supported image.
# Derived-checked by the parity gate: every supported extension maps exactly
# once, every mapping key is a supported extension.
readonly SUPPORTED_IMAGE_MIME_MAP="png=image/png jpg=image/jpeg jpeg=image/jpeg webp=image/webp"
readonly REJECTED_RASTER_IMAGE_EXTS="gif bmp tif tiff avif heic heif ico jfif"
readonly REJECTED_TEXTUAL_IMAGE_EXTS="svg"
readonly REJECTED_IMAGE_EXTS="${REJECTED_RASTER_IMAGE_EXTS} ${REJECTED_TEXTUAL_IMAGE_EXTS}"
readonly GITATTRIBUTES_BINARY_IMAGE_EXTS="${SUPPORTED_IMAGE_EXTS} ${REJECTED_RASTER_IMAGE_EXTS}"
