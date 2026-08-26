#!/usr/bin/env bash
# ACTIVATION (repository configuration only). Points git at the Unit-6 native
# hooks. Deliberately separate from extraction and from any commit, and NOT
# part of the numbered progression: activating before the frozen authority is
# present would make every local commit and push return ERROR by design.
#
# Take this step only when 25 (members placed) and 30 (runtime qualified) have
# both returned OK. Reverse with: git config --unset core.hooksPath
remote_guard() {
  [ -f .git/config ] || { echo 'NO .git/config - STOP'; return 1; }
  local url; url=$(sed -n 's/^[[:space:]]*url[[:space:]]*=[[:space:]]*//p' .git/config | head -1)
  [ -n "$url" ] || { echo 'NO REMOTE URL - STOP'; return 1; }
  echo "REMOTE configured=YES source=.git/config"   # never echo the URL itself
}

main() {
  cd ~/defender-sentinel-soc-lab || { echo 'WRONG DIR - STOP'; return 1; }
  remote_guard || return 1
  [ -d .githooks ] && [ -x .githooks/commit-msg ] && [ -x .githooks/pre-push ] || {
    echo "ACTIVATE result=REFUSED reason=HOOKS_ABSENT"; return 1; }
  git config core.hooksPath .githooks
  echo "ACTIVATE hooks_path=$(sed -n 's/^[[:space:]]*hooksPath[[:space:]]*=[[:space:]]*//p' .git/config | head -1)"
  echo "ACTIVATE result=OK (L1 and L2 are now live for this clone)"
}
main "$@"
