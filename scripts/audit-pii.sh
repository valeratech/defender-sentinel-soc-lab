#!/usr/bin/env bash
#
# audit-pii.sh — sweep the repository for identifiers, PII, and operational data.
#
# WHY THIS EXISTS
#   gitleaks passing proves only that the rules we wrote found nothing. It does
#   not prove the repository is clean. This sweeps wider: every email, GUID,
#   routable IP, hostname and personal term in the tree, reported for a human to
#   judge rather than pattern-matched and forgotten.
#
#   Run it before any push that adds evidence, and periodically regardless.
#
# PERSONAL TERMS
#   Checking for your own username, hostname or email means having those strings
#   somewhere. Putting them in this script would commit the very identifiers the
#   script exists to find — so they live in `.pii-terms`, which is gitignored,
#   one term per line. Without that file the sweep still runs; it just skips the
#   personal-term pass and says so.
#
# EXIT CODES
#   0  nothing found that needs a decision
#   1  findings require review (not necessarily leaks — see output)
#
# Usage:
#   bash scripts/audit-pii.sh              # working tree
#   bash scripts/audit-pii.sh --history    # + full git history (slower)
#
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

HISTORY=0
[ "${1:-}" = "--history" ] && HISTORY=1

FOUND=0
GREP_OPTS=(-rEoh --exclude-dir=.git --exclude-dir=.venv --exclude=.pii-terms)

hdr() { printf '\n\033[1m== %s\033[0m\n' "$1"; }
ok()  { printf '   \033[32mclean\033[0m — %s\n' "$1"; }
hit() { printf '   \033[31mREVIEW\033[0m — %s\n' "$1"; FOUND=1; }

# ── 1. gitleaks, working tree ────────────────────────────────
hdr "gitleaks — working tree"
if command -v gitleaks >/dev/null 2>&1; then
  if gitleaks dir . --config .gitleaks.toml --no-banner --redact >/dev/null 2>&1; then
    ok "no rule matches"
  else
    hit "gitleaks findings — run: gitleaks dir . --config .gitleaks.toml"
  fi
else
  hit "gitleaks not installed"
fi

# ── 2. gitleaks, full history ────────────────────────────────
if [ "$HISTORY" -eq 1 ]; then
  hdr "gitleaks — full git history"
  if gitleaks git . --config .gitleaks.toml --no-banner --redact >/dev/null 2>&1; then
    ok "no rule matches in any commit"
  else
    hit "findings in history — a scrubbed working tree does not scrub git history"
  fi
fi

# ── 3. Email addresses ───────────────────────────────────────
hdr "Email addresses"
mails=$(grep "${GREP_OPTS[@]}" "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" . 2>/dev/null \
        | grep -viE "@(contoso|example)\.(com|org|net)|@contoso\.onmicrosoft\.com|@(microsoft|github)\.com|users\.noreply\.github\.com" \
        | sort -u)
if [ -z "$mails" ]; then ok "only approved placeholders"
else hit "non-placeholder addresses:"; echo "$mails" | sed 's/^/       /'; fi

# ── 4. GUIDs ─────────────────────────────────────────────────
hdr "GUIDs (tenant / subscription / workspace / object IDs)"
# Public Microsoft ASR rule GUIDs are documented constants, identical for every
# tenant — not environment identifiers. Allowlisted by exact value only; any
# other GUID (a real tenant/subscription/object ID) is still reported.
guids=$(grep "${GREP_OPTS[@]}" "\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b" . 2>/dev/null \
        | grep -vE "^0{8}-0{4}-0{4}-0{4}-0{12}$" \
        | grep -viE "^(d1e49aac-8f56-4280-b9ba-993a6d77406c|e6db77e5-3df2-4cf1-b95a-636979351e5b)$" | sort -u)
if [ -z "$guids" ]; then ok "only nil/placeholder GUIDs"
else hit "non-placeholder GUIDs:"; echo "$guids" | sed 's/^/       /'; fi

# ── 5. Routable IPv4 ─────────────────────────────────────────
hdr "Routable IPv4 (outside RFC 5737 / RFC 1918)"
# Three-octet version strings like "8.28.0" never reach this filter. FOUR-octet
# version strings do: AMA reports its build as 1.43.0.0, shape-identical to an
# IPv4 address, flagged 2026-08-10 (Lab 21). The earlier claim that version
# numbers cannot reach this filter was wrong and is corrected here. Agent build
# numbers are public constants, identical in every tenant running that version,
# and are allowlisted by exact value. An earlier attempt to
# exclude them used ^([0-9]{1,3}\.){3}[0-9]{1,3}$ with grep -v, which silently
# excluded EVERY address and reported a planted routable IP as clean.
# Defender AV security intelligence versions are the same class: this repo
# carries 1.455.332.0 (Lab 22). Unlike 1.43.0.0 it needs NO gitleaks
# counterpart — that rule is octet-bounded (25[0-5]|2[0-4][0-9]|...) and
# 455/332 exceed 255, so it never matches there. Verified both regexes
# against 1.43.0.0, 1.455.332.0 and a routable control on 2026-08-10.
# "Both scanners always need it" is not a rule. Watch for the FIRST build
# number with every octet <= 255 that needs adding to both files again --
# that is the signal to bound this regex properly, not the line count.
# 168.63.129.16 is the Azure WireServer — a fixed virtual platform IP, identical
# in every Azure VNet, not a routable lab or attacker address. Allowlisted by
# exact value; every other public IP is still reported for review.
ips=$(grep "${GREP_OPTS[@]}" "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" . 2>/dev/null \
      | grep -vE "^(192\.0\.2\.|198\.51\.100\.|203\.0\.113\.|10\.|192\.168\.|127\.|169\.254\.|0\.0\.0\.0|255\.|172\.(1[6-9]|2[0-9]|3[01])\.)" \
      | grep -vE "^168\.63\.129\.16$" \
      | grep -vE "^1\.43\.0\.0$" \
      | grep -vE "^1\.455\.332\.0$" \
      | sort -u)
if [ -z "$ips" ]; then ok "only documentation/private ranges"
else hit "routable addresses — confirm each is attacker-side, not lab-side:"; echo "$ips" | sed 's/^/       /'; fi

# ── 5a. MAC addresses ────────────────────────────────────────
hdr "MAC addresses"
# Mirrored in .gitleaks.toml - the two scanners keep independent exception
# lists and neither reads the other. EUI-48 colon and hyphen forms; the two
# separator forms are enumerated because a per-octet [:-] class accepts mixed
# strings such as 00:00-5e:00-53:01, which are not valid addresses.
# Identifier-class boundaries stop extraction from inside a longer token
# (x00:00:5e:00:53:01z) or before a dotted suffix (00:00:5e:00:53:01.example);
# sed strips the consumed boundary characters before the exception filters.
# Dotted EUI-48 / Cisco-style three-group notation (0011.2233.4455) is
# deliberately outside this check's colon/hyphen representation scope.
# RFC 7042 reserves 00-00-5E-00-53-xx for documentation.
MACPAT='(^|[^0-9A-Za-z:._-])((([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})|(([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}))([^0-9A-Za-z:._-]|\.[^0-9A-Za-z_-]|\.$|$)'
macs=$(grep "${GREP_OPTS[@]}" "$MACPAT" . 2>/dev/null \
       | sed -E 's/^[^0-9A-Fa-f]+//; s/[^0-9A-Fa-f]+$//' \
       | grep -viE '^((00:){5}00|(00-){5}00|(ff:){5}ff|(ff-){5}ff)$' \
       | grep -viE '^(00:00:5e:00:53:|00-00-5e-00-53-)' | sort -u)
if [ -z "$macs" ]; then ok "none present"
else hit "hardware addresses - each identifies a specific machine:"; echo "$macs" | sed 's/^/       /'; fi

# ── 5b. Routable IPv6 ────────────────────────────────────────
hdr "Routable IPv6"
# Mirrored in .gitleaks.toml. RFC 4291 textual forms: eight hextets, one of the
# compressed shapes, or a mixed dotted-decimal form whose explicit hextets
# either side of "::" total at most five. A colon count is not a validity test -
# ">=3 colons" matched the MAC 00:00:5e:00:53:01, and "has a ::" matched inside
# 1:2:3:4:5:6:7:8:9. The trailing class treats ".", "_" and "-" as identifier
# characters so an address cannot terminate before a suffix or a dotted tail.
# The sed clauses strip, in order: a label prefix (IPv6:), a leading boundary
# character, a trailing boundary character, and a sentence-final period.
V6H='[0-9a-fA-F]{1,4}'; V6D='(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
V6IPV4="$V6D(\.$V6D){3}"
V6MIX="($V6H:){6}$V6IPV4|::($V6H:){0,5}$V6IPV4|($V6H:){1}:($V6H:){0,4}$V6IPV4|($V6H:){2}:($V6H:){0,3}$V6IPV4|($V6H:){3}:($V6H:){0,2}$V6IPV4|($V6H:){4}:($V6H:){0,1}$V6IPV4|($V6H:){5}:$V6IPV4"
V6HEX="($V6H:){7}$V6H|($V6H:){1,7}:|($V6H:){1,6}:$V6H|($V6H:){1,5}(:$V6H){1,2}|($V6H:){1,4}(:$V6H){1,3}|($V6H:){1,3}(:$V6H){1,4}|($V6H:){1,2}(:$V6H){1,5}|$V6H:(:$V6H){1,6}|:((:$V6H){1,7}|:)"
V6LEAD='(^|[^0-9A-Za-z:._-]|[A-Za-z][A-Za-z0-9_]*:)'
V6TRAIL='([^0-9A-Za-z:._-]|\.[^0-9A-Za-z_-]|\.$|$)'
v6=$(grep "${GREP_OPTS[@]}" "$V6LEAD($V6MIX|$V6HEX)$V6TRAIL" . 2>/dev/null \
     | sed -E 's/^[A-Za-z][A-Za-z0-9_]*://; s/^[^0-9A-Fa-f:]+//; s/[^0-9A-Fa-f:.]+$//; s/\.$//' \
     | grep -viE '^(2001:0?db8:|fe[89ab][0-9a-f]:|f[cd][0-9a-f]{2}:|ff[0-9a-f]{2}:)' \
     | grep -viE '^(0{1,4}:){7}0*[01]$' \
     | grep -viE '^::[01]?$' | sort -u)
if [ -z "$v6" ]; then ok "only documentation/link-local/ULA/multicast/loopback"
else hit "routable IPv6 - confirm each is attacker-side, not lab-side:"; echo "$v6" | sed 's/^/       /'; fi

# ── 6. Tenant / lab hostnames ────────────────────────────────
hdr "Tenant domains and lab hostnames"
hosts=$(grep "${GREP_OPTS[@]}" "[a-z0-9-]+\.(onmicrosoft\.com|cloudapp\.azure\.com|logic\.azure\.com|azure-automation\.net)" . 2>/dev/null \
        | grep -viE "^contoso\.onmicrosoft\.com$" | sort -u)
if [ -z "$hosts" ]; then ok "only contoso.onmicrosoft.com"
else hit "real tenant/lab hostnames:"; echo "$hosts" | sed 's/^/       /'; fi

# ── 7. Azure resource IDs ────────────────────────────────────
hdr "Azure resource IDs"
rids=$(grep "${GREP_OPTS[@]}" "/subscriptions/[0-9a-fA-F-]{36}/resourceGroups/[A-Za-z0-9._()-]+" . 2>/dev/null \
       | grep -v "/subscriptions/00000000-0000-0000-0000-000000000000/" | sort -u)
if [ -z "$rids" ]; then ok "none, or placeholdered"
else hit "resource IDs embedding real subscription/RG:"; echo "$rids" | sed 's/^/       /'; fi

# ── 8. Personal terms (gitignored .pii-terms) ────────────────
hdr "Personal terms"
if [ -f .pii-terms ]; then
  pfound=0
  n=0
  while IFS= read -r term; do
    [ -z "$term" ] && continue
    case "$term" in \#*) continue ;; esac
    n=$((n+1))
    files=$(grep -rilF "$term" . --exclude-dir=.git --exclude=.pii-terms 2>/dev/null | tr '\n' ' ')
    if [ -n "$files" ]; then
      # Report the term's line number, never the term itself. Printing it would
      # put the identifier into terminal scrollback, CI logs, and any pasted
      # output — reintroducing the exposure this check exists to prevent.
      hit "term #$n (.pii-terms line $n) found in: $files"
      pfound=1
    fi
  done < .pii-terms
  [ "$pfound" -eq 0 ] && ok "no personal terms present"
else
  printf '   \033[33mSKIPPED\033[0m — no .pii-terms file.\n'
  printf '     Create it (gitignored) with one term per line: username, hostname,\n'
  printf '     personal email, tenant display name, real device names.\n'
fi

# ── 9. Commit author identities ──────────────────────────────
hdr "Commit author identities"
if [ -d .git ]; then
  authors=$(git log --format='%ae%n%ce' 2>/dev/null | sort -u)
  bad=$(echo "$authors" | grep -viE "users\.noreply\.github\.com" || true)
  echo "$authors" | sed 's/^/       /'
  if [ -n "$bad" ]; then
    hit "addresses above are permanent and public in every clone"
  else
    ok "all authorship via GitHub noreply"
  fi
else
  ok "not a git repository"
fi

# ── 10. Images ───────────────────────────────────────────────
hdr "Committed images"
# Extension set comes from the single machine authority; the parity gate
# fails the build if an independent list reappears here (AUD-007).
. "$(dirname "$0")/image-formats.sh"
shopt -s nullglob globstar nocaseglob
# Policy view first (P7): image-like files that are NOT lowercase supported
# must surface here, not vanish into "no images". nocaseglob catches case
# variants; verdict logic below distinguishes them.
allimgs=()
for _ext in $SUPPORTED_IMAGE_EXTS $REJECTED_IMAGE_EXTS; do
  for _f in **/*."$_ext"; do allimgs+=( "$_f" ); done
done
shopt -u nocaseglob
imgs=()
POLICY_HIT=0
in_word_list() { local w="$1"; shift; local x; for x in $*; do [ "$w" = "$x" ] && return 0; done; return 1; }
for _f in "${allimgs[@]}"; do
  _ext="${_f##*.}"
  if in_word_list "$_ext" $SUPPORTED_IMAGE_EXTS; then
    # Content↔extension binding (P11/P17): the manual audit must agree with
    # the census and policy hook about what a supported image IS. Detected
    # MIME must equal the authority-mapped value; failing closed otherwise.
    if ! command -v file >/dev/null 2>&1; then
      hit "image policy: $_f — 'file' unavailable; content/extension binding cannot be verified, failing closed (SANITIZATION.md section 10)"
      POLICY_HIT=1
      continue
    fi
    _mime="$(file --brief --mime-type -- "$_f" 2>/dev/null)"; _mrc=$?
    if [ "$_mrc" -ne 0 ] || [ -z "$_mime" ]; then
      hit "image policy: $_f — MIME detection failed; failing closed (SANITIZATION.md section 10)"
      POLICY_HIT=1
      continue
    fi
    _bound=""
    for _pair in $SUPPORTED_IMAGE_MIME_MAP; do
      [ "${_pair%%=*}" = "$_ext" ] && _bound="${_pair#*=}"
    done
    if [ -z "$_bound" ] || [ "$_mime" != "$_bound" ]; then
      hit "image policy: $_f — content/extension mismatch: detected $_mime under '.$_ext' (bound to ${_bound:-nothing}) (SANITIZATION.md section 10)"
      POLICY_HIT=1
      continue
    fi
    imgs+=( "$_f" )
  else
    hit "image policy: $_f — extension '.$_ext' violates the lowercase supported set (SANITIZATION.md section 10)"
    POLICY_HIT=1
  fi
done
if [ ${#imgs[@]} -eq 0 ] && [ "$POLICY_HIT" -eq 0 ]; then
  ok "no images in repository"
elif [ ${#imgs[@]} -gt 0 ]; then
  printf '   %d supported image(s) — running single-frame check and OCR gate\n' "${#imgs[@]}"
  # Single-frame contract (AUD-007 facet g) before OCR.
  FRAME_HIT=0
  for img in "${imgs[@]}"; do
    python3 "$(dirname "$0")/detect-animation.py" "$img"
    _arc=$?
    case "$_arc" in
      0) : ;;
      1) hit "image policy: $img — multi-image content (APNG/animated WebP/JPEG MPO); supported publication images must contain exactly one image (SANITIZATION.md section 10)"; FRAME_HIT=1 ;;
      3) hit "image policy: $img — content is not a recognised PNG/WebP/JPEG container; the single-image contract cannot be evaluated, failing closed (SANITIZATION.md section 10)"; FRAME_HIT=1 ;;
      *) hit "image policy: $img — single-image check could not parse this image; failing closed"; FRAME_HIT=1 ;;
    esac
  done
  if bash scripts/scan-image-text.sh "${imgs[@]}"; then
    ok "OCR gate passed (manual visual review still required — SANITIZATION.md section 4)"
  else
    hit "OCR gate blocked one or more images"
  fi
  hdr "Image metadata"
  # Byte-level strip idempotence: would the repository's own strip operation
  # (exiftool -all= -overwrite_original) change this image? Markers shared
  # verbatim with scripts/ci-verify-image-metadata.sh. Output carries paths
  # and markers only — never metadata values, never warning text. A check
  # that did not run is never reported clean, and every oracle step fails
  # closed to the same standard as the CI implementation (SANITIZATION.md
  # section 10).
  if ! command -v exiftool >/dev/null 2>&1; then
    hit "METADATA-CHECK-NOT-RUN — exiftool unavailable; metadata verification did not run"
  else
    META_HIT=0
    for img in "${imgs[@]}"; do
      _mw="$(mktemp -d)" || { hit "METADATA-CHECK-FAILED $img"; META_HIT=1; continue; }
      if ! cp -- "$img" "$_mw/copy"; then
        hit "METADATA-CHECK-FAILED $img"; META_HIT=1; rm -rf "$_mw"; continue
      fi
      if ! _h1="$(sha256sum -- "$_mw/copy" | cut -d' ' -f1)" || [ -z "$_h1" ]; then
        hit "METADATA-CHECK-FAILED $img"; META_HIT=1; rm -rf "$_mw"; continue
      fi
      _err="$(exiftool -all= -overwrite_original "$_mw/copy" 2>&1 1>/dev/null)"
      _rc=$?
      if [ "$_rc" -ne 0 ] || [ -n "$_err" ]; then
        hit "METADATA-CHECK-FAILED $img"; META_HIT=1; rm -rf "$_mw"; continue
      fi
      if ! _h2="$(sha256sum -- "$_mw/copy" | cut -d' ' -f1)" || [ -z "$_h2" ]; then
        hit "METADATA-CHECK-FAILED $img"; META_HIT=1; rm -rf "$_mw"; continue
      fi
      rm -rf "$_mw"
      if [ "$_h1" != "$_h2" ]; then
        hit "METADATA-PRESENT $img — strip would change this image; inspect locally with exiftool (values deliberately not printed here)"
        META_HIT=1
      fi
    done
    # P7: never print a clean line above red findings.
    if [ "$META_HIT" -eq 0 ]; then
      ok "metadata check clean (byte-level strip idempotence, ${#imgs[@]} image(s))"
    fi
  fi
fi

# ── Verdict ──────────────────────────────────────────────────
echo
if [ "$FOUND" -eq 0 ]; then
  printf '\033[32m== AUDIT CLEAN\033[0m — nothing requiring a decision.\n'
  printf 'Automation reports patterns, not judgment. Screenshots still need a human look.\n'
  exit 0
else
  printf '\033[31m== AUDIT: REVIEW REQUIRED\033[0m — see items marked REVIEW above.\n'
  printf 'Not every finding is a leak. Each one is a decision you have to make.\n'
  exit 1
fi
