#!/usr/bin/env bash
# MUTATING (working tree). Places the frozen Unit-6 members into msgctl/ from
# the Reviewer-verified exact frozen package. Runs AFTER 20 (which installs
# u6/ENGINE-IDENTITIES.txt); the admitted 137-file base has no u6/ tree.
#
# The staging workspace is PROVEN outside the repository (Reviewer Pass-10
# P10-01): TMPDIR is ambient input and may point into the tree, so it is used
# only if its realpath lies outside the repository realpath, /tmp is the
# fallback, and after mktemp the realpath of the staging directory is checked
# against the repository realpath again. Containment -> refuse, place nothing.
# Failure evidence is still retained - outside the tree, where it cannot
# contaminate a commit.
#
# NON-DESTRUCTIVE ON FAILURE (Reviewer Pass-7 P7-04): every member is copied
# into a staging directory and verified there. Production placement happens
# only after ALL identities pass, so no partial state is ever installed. On
# failure nothing under msgctl/ is created or removed and the staging
# directory is LEFT IN PLACE for inspection; its path is printed.
#
# Usage: bash u6/orchestrate/25-place-engine.sh <dir-with-exact-frozen-members>
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
  local src=${1:-}
  [ -d "$src" ] || { echo "PLACE_ENGINE source_dir=ABSENT"; return 1; }
  [ -f u6/ENGINE-IDENTITIES.txt ] || { echo "PLACE_ENGINE manifest=ABSENT (run 20-apply-candidate.sh first)"; return 1; }
  local repo_real; repo_real=$(realpath .) || return 1
  local base=${TMPDIR:-/tmp}
  # TMPDIR is ambient: accept it only when it is provably outside the repository.
  local base_real; base_real=$(realpath -m "$base" 2>/dev/null) || base_real=""
  case "$base_real" in
    "$repo_real"|"$repo_real"/*|"") base=/tmp
      echo "PLACE_ENGINE tmpdir_rejected=inside_repository fallback=/tmp" ;;
  esac
  local stage; stage=$(mktemp -d "$base/msgctl-staging-XXXXXX") || return 1
  # Prove it after the fact as well: symlinks, races and odd mounts all land here.
  local stage_real; stage_real=$(realpath "$stage") || return 1
  case "$stage_real" in
    "$repo_real"|"$repo_real"/*)
      echo "PLACE_ENGINE result=REFUSED reason=STAGING_INSIDE_REPOSITORY staging=$stage_real"
      return 1 ;;
  esac
  echo "PLACE_ENGINE staging_outside_repository=$stage_real"
  local bad=0 n=0
  while read -r sha rel; do
    case "$sha" in ''|'#'*) continue;; esac
    case "$rel" in msgctl/*) ;; *) continue;; esac
    local name=${rel#msgctl/}
    n=$((n+1))
    if [ ! -f "$src/$name" ]; then echo "PLACE_ENGINE member=$name state=SOURCE_ABSENT"; bad=1; continue; fi
    cp "$src/$name" "$stage/$name" || { echo "PLACE_ENGINE member=$name state=COPY_FAILED"; bad=1; continue; }
    if [ "$(sha256sum "$stage/$name" | cut -d' ' -f1)" != "$sha" ]; then
      echo "PLACE_ENGINE member=$name state=IDENTITY_MISMATCH"; bad=1; continue
    fi
    echo "PLACE_ENGINE member=$name state=STAGED_VERIFIED"
  done < u6/ENGINE-IDENTITIES.txt
  if [ "$bad" -ne 0 ]; then
    echo "PLACE_ENGINE result=REFUSED members_expected=$n"
    echo "PLACE_ENGINE staging_retained=$stage (nothing placed, nothing removed - inspect the staged members)"
    return 1
  fi
  mkdir -p msgctl || return 1
  cp "$stage"/. msgctl/ -a || { echo "PLACE_ENGINE result=PLACEMENT_FAILED staging_retained=$stage"; return 1; }
  local mism=0
  while read -r sha rel; do
    case "$sha" in ''|'#'*) continue;; esac
    case "$rel" in msgctl/*) ;; *) continue;; esac
    [ "$(sha256sum "$rel" | cut -d' ' -f1)" = "$sha" ] || mism=$((mism+1))
  done < u6/ENGINE-IDENTITIES.txt
  echo "PLACE_ENGINE placed=$n post_placement_mismatched=$mism staging=$stage"
  [ "$mism" -eq 0 ] && echo "PLACE_ENGINE result=OK staging_retained=$stage (remove manually once accepted)"
  [ "$mism" -eq 0 ]
}
main "$@"
