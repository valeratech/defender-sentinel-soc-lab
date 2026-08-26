#!/usr/bin/env bash
# VERIFICATION ONLY. Runs every gate and the Builder test battery against the
# applied working tree. Commits nothing. Cleans nothing: on failure the tree is
# left exactly as it failed so the evidence can be inspected.
# Precondition: the Reviewer-owned current-state revision has been bound
# (docs/current-state/CURRENT.txt is not UNBOUND); otherwise the current-state
# gate fails closed by design.
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
  local ok=1
  RUNNER_TMP_GL=$(mktemp); export RUNNER_TMP_GL
  step() { echo "VERIFY step=$1 begin"; if "${@:2}"; then echo "VERIFY step=$1 result=PASS"; else echo "VERIFY step=$1 result=FAIL"; ok=0; fi; }
  git add -A -n >/dev/null  # dry run only; nothing is staged here
  step precommit        pre-commit run --all-files
  step current-state    python3 scripts/check-current-state.py
  export PYTHONDONTWRITEBYTECODE=1   # bytecode is scanned by gitleaks dir; never create it here
  step l3-isolation     python3 u6/controls/check_l3_isolation.py
  step test-battery     python3 -m unittest u6.controls.test_u6
  step falsification    python3 u6/controls/falsify.py
  step gitleaks-json    bash -c 'set -o pipefail; gitleaks dir . --config .gitleaks.toml --no-banner --redact --report-format json --report-path "$RUNNER_TMP_GL" 2>&1 | sed -E "s/\x1b\[[0-9;]*m//g"; n=$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$RUNNER_TMP_GL"); echo "GITLEAKS findings=$n"; [ "$n" -eq 0 ]'
  step audit-pii        bash scripts/audit-pii.sh
  echo "VERIFY_END ok=$ok"
  return $((1-ok))
}
main "$@"
