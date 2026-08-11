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
        | grep -vE "^(0{8}-0{4}-0{4}-0{4}-0{12}|1{8}-1{4}-1{4}-1{4}-1{12})$" \
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
shopt -s nullglob globstar
imgs=( **/*.png **/*.jpg **/*.jpeg **/*.webp )
if [ ${#imgs[@]} -eq 0 ]; then
  ok "no images in repository"
else
  printf '   %d image(s) — running OCR gate\n' "${#imgs[@]}"
  if bash scripts/scan-image-text.sh "${imgs[@]}"; then
    ok "OCR gate passed (manual visual review still required — SANITIZATION.md section 4)"
  else
    hit "OCR gate blocked one or more images"
  fi
  hdr "Image metadata"
  if command -v exiftool >/dev/null 2>&1; then
    meta=$(exiftool -s -GPS* -Author -Creator -Software -HostComputer "${imgs[@]}" 2>/dev/null | grep -v "^$" || true)
    if [ -z "$meta" ]; then ok "no GPS/author/software metadata"
    else hit "metadata present:"; echo "$meta" | sed 's/^/       /'; fi
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
