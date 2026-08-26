#!/usr/bin/env bash
# MUTATING (working tree only). Extracts the candidate overlay and activates the
# native hooks path. No verification, no commit, no push: those are 21 and 22,
# held and observed separately. Usage: bash u6/orchestrate/20-apply-candidate.sh <overlay.tar.gz>
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
  local tgz=${1:-}
  [ -f "$tgz" ] || { echo "APPLY overlay=ABSENT"; return 1; }
  echo "APPLY overlay_sha256=$(sha256sum "$tgz" | cut -d' ' -f1)"
  tar xzf "$tgz" -C . || { echo "APPLY result=EXTRACT_FAILED"; return 1; }
  # Hook ACTIVATION is deliberately NOT done here: it is a separate step
  # (u6/orchestrate/A-activate-hooks.sh) taken only once the frozen authority
  # is present, and it must not be a side effect of extracting files. Nothing
  # in this script executes git (Reviewer Pass-10 P10-02).
  echo "APPLY hooks_path=\"$(sed -n 's/^[[:space:]]*hooksPath[[:space:]]*=[[:space:]]*//p' .git/config | head -1 || true)\" (unchanged by this step)"
  echo "APPLY extracted_paths=$(tar tzf "$tgz" | grep -vc '/$')"
  echo "APPLY result=EXTRACTED (nothing staged, nothing committed, hooks not activated)"
}
main "$@"
