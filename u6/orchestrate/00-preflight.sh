#!/usr/bin/env bash
# READ-ONLY. Runs from the GOVERNED 137-FILE BASE (no u6/ tree required):
# effective runtime object identities, engine member identities when a manifest
# is available, hook path, wordlist presence. Optional argument: path to an
# ENGINE-IDENTITIES.txt (use the one inside the package before the overlay is
# applied). Prints structured lines only.
# Prints structured lines only. Never prints wordlist content or private paths' contents.
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
  echo "PREFLIGHT_BEGIN"
  local ok=1
  check_bin() { # name path version-cmd expected-sha
    local name=$1 path=$2 vcmd=$3 exp=$4 act
    if [ -x "$path" ]; then
      act=$(sha256sum "$path" | cut -d' ' -f1)
      # Probe only after the bytes match: an unqualified object is never executed.
      if [ "$act" = "$exp" ]; then
        echo "RUNTIME name=$name path=$path version=\"$($vcmd 2>&1 | head -1)\" sha_match=YES"
      else
        echo "RUNTIME name=$name path=$path version=NOT_PROBED sha_match=NO"
        ok=0
      fi
    else
      echo "RUNTIME name=$name path=$path state=ABSENT"; ok=0
    fi
  }
  check_bin python   /usr/bin/python3.12        "/usr/bin/python3.12 --version"  1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118
  check_bin git      /usr/bin/git               "/usr/bin/git --version"         f54a87f6253aab09ed7b522bd78ddeab509105b1043076209d89127e55877a48
  check_bin gitleaks /usr/local/bin/gitleaks    "/usr/local/bin/gitleaks version" 5fd1b3b0073269484d40078662e921d07427340ab9e6ed526ccd215a565b3298
  # effective interpreter for hooks is `python3` on PATH; bind it to the qualified object
  local eff; eff=$(readlink -f "$(command -v python3)")
  echo "EFFECTIVE_PYTHON3 path=$eff qualified=$([ "$eff" = /usr/bin/python3.12 ] && echo YES || echo NO)"
  [ "$eff" = /usr/bin/python3.12 ] || ok=0
  local manifest=${1:-u6/ENGINE-IDENTITIES.txt}
  if [ ! -f "$manifest" ]; then
    # Expected before the candidate overlay is applied: the governed 137-file
    # base has no u6/ tree. Pass the manifest path from the package to check
    # engine identities pre-overlay.
    echo "ENGINE manifest=ABSENT (pre-overlay; pass a manifest path to check members)"
    echo "HOOKS_PATH value=\"$(sed -n 's/^[[:space:]]*hooksPath[[:space:]]*=[[:space:]]*//p' .git/config | head -1 || true)\" source=.git/config"
    echo "WORDLIST present=$([ -f .pii-terms ] && echo YES || echo NO)"
    echo "PREFLIGHT_END ok=$ok manifest=ABSENT"
    return $((1-ok))
  fi
  local miss=0 mism=0 present=0
  while read -r sha rel; do
    case "$sha" in ''|'#'*) continue;; esac
    if [ -f "$rel" ]; then
      present=$((present+1))
      [ "$(sha256sum "$rel" | cut -d' ' -f1)" = "$sha" ] || mism=$((mism+1))
    else miss=$((miss+1)); fi
  done < "$manifest"
  echo "ENGINE present=$present missing=$miss mismatched=$mism"
  [ "$miss" -eq 0 ] && [ "$mism" -eq 0 ] || ok=0
  echo "HOOKS_PATH value=\"$(sed -n 's/^[[:space:]]*hooksPath[[:space:]]*=[[:space:]]*//p' .git/config | head -1 || true)\" source=.git/config"
  echo "WORDLIST present=$([ -f .pii-terms ] && echo YES || echo NO)"   # presence only
  echo "COMMITTED_BASELINE present=$([ -f u6/committed-baseline ] && echo YES || echo NO)"
  echo "PREFLIGHT_END ok=$ok"
  return $((1-ok))
}
main "$@"
