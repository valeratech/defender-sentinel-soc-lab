#!/usr/bin/env bash
# ci-verify-image-metadata.sh — byte-level strip-idempotence verification.
#
# QUESTION THIS ANSWERS
#   Would the repository's own strip operation (exiftool -all= -overwrite_original)
#   change this image? If yes, the image was published unstripped.
#
# MARKERS (machine-readable, mutually exclusive per image; shared verbatim
# with the manual block in audit-pii.sh):
#   METADATA-CHECK-NOT-RUN   exiftool unavailable                       -> FAIL
#   METADATA-CHECK-FAILED    exiftool nonzero exit OR any stderr output -> FAIL
#                            (warnings fail closed even at exit 0)
#   METADATA-PRESENT         strip would change the image bytes         -> FAIL
#   metadata-clean           byte-idempotent                            -> pass
#
# REDACTION: output carries paths and markers only — never metadata values,
# never warning text (SANITIZATION.md section 10).
#
# SELF-PROOF: every run first generates a disposable image in a temp dir,
# plants a removable tag, and requires METADATA-PRESENT to fire. A gate that
# cannot fail on the toolchain executing it proves nothing.
set -uo pipefail

. "$(dirname "$0")/image-formats.sh"

if ! command -v exiftool >/dev/null 2>&1; then
  echo "METADATA-CHECK-NOT-RUN — exiftool unavailable; metadata verification did not run." >&2
  exit 1
fi

in_list() {
  local w="$1"; shift
  local x
  for x in $*; do [ "$w" = "$x" ] && return 0; done
  return 1
}

# oracle <path>: 0 clean · 1 METADATA-PRESENT · 4 METADATA-CHECK-FAILED
oracle() {
  local img="$1" work h1 h2 rc errout
  work="$(mktemp -d)" || { echo "METADATA-CHECK-FAILED $img" >&2; return 4; }
  # shellcheck disable=SC2064
  trap "rm -rf '$work'" RETURN
  cp -- "$img" "$work/copy" || { echo "METADATA-CHECK-FAILED $img" >&2; return 4; }
  h1="$(sha256sum -- "$work/copy" | cut -d' ' -f1)" || { echo "METADATA-CHECK-FAILED $img" >&2; return 4; }
  errout="$(exiftool -all= -overwrite_original "$work/copy" 2>&1 1>/dev/null)"; rc=$?
  if [ "$rc" -ne 0 ] || [ -n "$errout" ]; then
    echo "METADATA-CHECK-FAILED $img" >&2
    return 4
  fi
  h2="$(sha256sum -- "$work/copy" | cut -d' ' -f1)" || { echo "METADATA-CHECK-FAILED $img" >&2; return 4; }
  if [ "$h1" = "$h2" ]; then
    echo "metadata-clean $img"
    return 0
  fi
  echo "METADATA-PRESENT $img — the strip operation would change this image; it was not fully stripped before commit. Inspect locally with exiftool; values are deliberately not printed here." >&2
  return 1
}

# ── Self-proof: the oracle must be able to fail on THIS toolchain ───────
SELFDIR="$(mktemp -d)" || { echo "METADATA-CHECK-FAILED self-proof — mktemp failed." >&2; exit 1; }
[ -d "$SELFDIR" ] || { echo "METADATA-CHECK-FAILED self-proof — temp dir unavailable." >&2; exit 1; }
trap 'rm -rf "$SELFDIR"' EXIT
python3 - "$SELFDIR/proof.png" <<'PY'
import struct, sys, zlib
def chunk(t, d):
    return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
ihdr = struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0)
raw = b"".join(b"\x00" + b"\xff\xff\xff" * 4 for _ in range(4))
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
open(sys.argv[1], "wb").write(png)
PY
if [ ! -s "$SELFDIR/proof.png" ]; then
  echo "METADATA-CHECK-FAILED self-proof — fixture generation failed." >&2
  exit 1
fi
exiftool -overwrite_original "-PNG:Comment=self-proof-removable" "$SELFDIR/proof.png" >/dev/null 2>&1 || {
  echo "METADATA-CHECK-FAILED self-proof — could not plant removable tag." >&2
  exit 1
}
SELFOUT="$(oracle "$SELFDIR/proof.png" 2>&1)"
SELFRC=$?
# Locked P3 contract: specific return code AND exact marker identity — an
# unrelated rc=1 from future control-flow drift must not pass as self-proof.
if [ "$SELFRC" -ne 1 ] || ! printf '%s' "$SELFOUT" | grep -qF "METADATA-PRESENT $SELFDIR/proof.png"; then
  # rc 0 = oracle passed a planted image (broken oracle); rc 4 = the strip/tool
  # path itself failed. Neither proves detection; both fail the run (P3: a
  # self-proof that accepts ANY failure would green-light a broken toolchain).
  echo "METADATA-CHECK-FAILED self-proof — expected rc=1 with the METADATA-PRESENT marker on a planted fixture, got rc=$SELFRC." >&2
  exit 1
fi
echo "self-proof: oracle returned METADATA-PRESENT on a planted fixture (rc=1) on this toolchain."

# ── Verify every tracked supported image (P2: hard-checked enumeration) ──
LSFILE="$(mktemp)" || { echo "METADATA-CHECK-FAILED — could not create temp file for enumeration." >&2; exit 1; }
if ! git ls-files -z > "$LSFILE"; then
  echo "METADATA-CHECK-FAILED — git ls-files failed; tracked boundary unavailable, failing closed." >&2
  rm -f "$LSFILE"
  exit 1
fi
FAIL=0
CHECKED=0
while IFS= read -r -d '' f; do
  base="${f##*/}"
  case "$base" in *.*) ext="${base##*.}" ;; *) continue ;; esac
  in_list "$ext" $SUPPORTED_IMAGE_EXTS || continue
  CHECKED=$((CHECKED+1))
  oracle "$f" || FAIL=1
done < "$LSFILE"
rm -f "$LSFILE"

if [ "$CHECKED" -eq 0 ]; then
  echo "metadata: no supported images in the tracked tree — nothing to verify."
fi
echo "metadata: images checked: $CHECKED"
[ "$FAIL" -eq 0 ] && echo "metadata: PASS" || echo "metadata: FAIL"
exit $FAIL
