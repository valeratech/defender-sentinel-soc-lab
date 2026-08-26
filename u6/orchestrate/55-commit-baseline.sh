#!/usr/bin/env bash
# MUTATING (index + ONE local commit). Commits the Reviewer-ACCEPTED current
# L2 expected baseline artifact at u6/committed-baseline. The artifact's
# bytes and identity come from the accepted adjudication outcome; this script
# verifies the identity Ryan pastes from the Reviewer acceptance and refuses
# on mismatch. Usage: bash u6/orchestrate/45-commit-baseline.sh <path> <accepted-sha256>
# Repository guard WITHOUT executing git (Reviewer Pass-10 P10-02): an
# unqualified or shadowed git must not run before the Unit-6 runtime contract
# has established authority. The remote is read textually from .git/config.
remote_guard() {
  [ -f .git/config ] || { echo 'NO .git/config - STOP'; return 1; }
  local url; url=$(sed -n 's/^[[:space:]]*url[[:space:]]*=[[:space:]]*//p' .git/config | head -1)
  [ -n "$url" ] || { echo 'NO REMOTE URL - STOP'; return 1; }
  echo "REMOTE configured=YES source=.git/config"   # never echo the URL itself
}

main() {
  cd ~/defender-sentinel-soc-lab || { echo 'WRONG DIR - STOP'; return 1; }
  remote_guard || return 1
  local src=${1:?baseline artifact path} exp=${2:?accepted sha256}
  [ -f "$src" ] || { echo "BASELINE source=ABSENT"; return 1; }
  [ "$(sha256sum "$src" | cut -d' ' -f1)" = "$exp" ] || { echo "BASELINE result=IDENTITY_MISMATCH"; return 1; }
  cp "$src" u6/committed-baseline
  git add u6/committed-baseline
  git commit -F- <<'MSG'
Stage 2: commit Reviewer-accepted current L2 expected baseline

Binds u6/committed-baseline (baseline.load_committed). The private half
remains under the private root and is never committed.
MSG
  echo "BASELINE commit=$(git rev-parse HEAD)"
  git log -1 --format=%B | tail -3
}
main "$@"
