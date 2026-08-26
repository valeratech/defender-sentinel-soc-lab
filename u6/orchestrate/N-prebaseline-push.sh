#!/usr/bin/env bash
# NEGATIVE CONTROL, not a progression step. Demonstrates that a push attempted
# BEFORE the accepted baseline is committed is refused by L2 with
# ERROR/BASELINE_UNRESOLVED (rc 2). Uses --dry-run: nothing is published even
# if the hook were somehow to pass. Expected U6_RETURN: STATUS=ERROR CODE=BASELINE_UNRESOLVED.
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
  [ -f u6/committed-baseline ] && { echo "N-PREBASELINE not applicable: baseline present"; return 1; }
  git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'
  git push --dry-run origin main; echo "N-PREBASELINE push_rc=$? (expected non-zero)"
}
main "$@"
