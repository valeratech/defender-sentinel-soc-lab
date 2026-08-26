#!/usr/bin/env bash
# VERIFICATION ONLY. Exercises the L2 native pre-push hook against the live
# origin without publishing anything: a dry-run push still invokes pre-push.
# Runs only after a Reviewer-accepted current baseline has been committed
# (45). Expect STATUS=PASS. A REJECT means the prospective published union
# still carries a non-exempt finding; an ERROR means the runtime, engine,
# private state or baseline binding is not satisfied.
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
  git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'
  git push --dry-run origin main
}
main "$@"
