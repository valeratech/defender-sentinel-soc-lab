#!/usr/bin/env bash
# MUTATING (index + ONE local commit). Only after 21-verify returned ok=1 in
# the same sitting and both roles have locked this step. No push (see 25).
# The commit message goes through the L1 hook; expect one U6_RETURN line.
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
  git add -A
  echo "COMMIT staged=$(git diff --cached --name-only | wc -l)"
  git commit -F- <<'MSG'
Stage 2: integrate Unit-6 L1/L2/L3 operational layer (Gate D candidate)

Adds u6/ (engine binding by frozen identity, private-root consumer,
L1 commit-msg, L2 pre-push, L3 CI structural sweep, hardened return
channel), native hooks under .githooks/, current-state authority under
docs/current-state/ with scripts/check-current-state.py, CI job
commit-msg-structural, Builder test battery with falsification harness,
Amendment B disclosure in SANITIZATION.md.

Current L2 expected baseline: NOT ESTABLISHED (u6/committed-baseline absent;
L2 fails closed with BASELINE_UNRESOLVED until a Reviewer-accepted baseline
is committed).
MSG
  echo "COMMIT sha=$(git rev-parse HEAD)"
  git log -1 --format=%B | tail -5
  git log --oneline | wc -l
  echo "COMMIT result=LOCAL_ONLY"
}
main "$@"
