#!/usr/bin/env bash
# MUTATING (index + ONE local commit). Only after the preceding verification
# returned ok=1 in the same sitting and both roles have locked this step.
# No push (see 70-push.sh).
#
# CORRECTED (Reviewer Stage-2 ruling, successor Builder): the predecessor of
# this script staged with `git add -A`, which sweeps every unrelated
# working-tree change into the governed commit. That behaviour was ruled NOT
# AUTHORIZED FOR OPERATOR USE after it was measured staging an unrelated
# uncommitted evidence note alongside the governed set (63 paths staged where
# 62 were governed). This version stages EXACTLY the paths named in a manifest
# supplied by the caller, verifies the staged set equals that manifest, and
# refuses otherwise. There is no path through this script that stages an
# unnamed file.
#
# The commit message is supplied as a FILE, never embedded here: an embedded
# message goes stale against the state it claims. The predecessor's embedded
# message asserted a CI job (commit-msg-structural) that the committed state
# does not wire, which is a false claim on a publication surface.
#
# Usage: bash u6/orchestrate/40-commit.sh <manifest-file> <message-file>
#   manifest-file  one repository-relative path per line, no globs, no blanks
#   message-file   the exact commit message bytes
#
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
  cd ~/defender-sentinel-soc-lab || { echo 'COMMIT result=REFUSED reason=WRONG_DIR'; return 1; }
  remote_guard || return 1

  local manifest=${1:-} msgfile=${2:-}
  [ -f "$manifest" ] || { echo "COMMIT result=REFUSED reason=MANIFEST_ABSENT"; return 1; }
  [ -f "$msgfile" ]  || { echo "COMMIT result=REFUSED reason=MESSAGE_FILE_ABSENT"; return 1; }
  [ -s "$msgfile" ]  || { echo "COMMIT result=REFUSED reason=MESSAGE_FILE_EMPTY"; return 1; }

  # The index must be empty: this script owns what it stages.
  local pre_index; pre_index=$(git diff --cached --name-only | wc -l | tr -d ' ')
  [ "$pre_index" -eq 0 ] || { echo "COMMIT result=REFUSED reason=INDEX_NOT_EMPTY entries=$pre_index"; return 1; }

  # Record unrelated dirt so it can be proven untouched afterwards.
  local dirty_before; dirty_before=$(git status --porcelain=v1 | wc -l | tr -d ' ')

  # Manifest grammar: no blanks, no globs, no absolute paths, no traversal.
  # Output is pasteable: COUNTS AND CATEGORIES ONLY, never a path from the
  # manifest or the tree (Reviewer Stage-2 Exchange-2 item 3).
  local n=0 unsafe=0 globs=0 absent=0 p
  while IFS= read -r p; do
    case "$p" in
      ''|'#'*) continue ;;
      /*|../*|*/../*|*/..) unsafe=$((unsafe+1)); continue ;;
      *'*'*|*'?'*|*'['*)   globs=$((globs+1)); continue ;;
    esac
    [ -e "$p" ] || { absent=$((absent+1)); continue; }
    n=$((n+1))
  done < "$manifest"
  if [ $((unsafe+globs+absent)) -ne 0 ]; then
    echo "COMMIT result=REFUSED reason=MANIFEST_INVALID unsafe_paths=$unsafe glob_paths=$globs absent_paths=$absent"
    return 1
  fi
  [ "$n" -gt 0 ] || { echo "COMMIT result=REFUSED reason=MANIFEST_EMPTY"; return 1; }

  # Stage EXACTLY the manifest paths. No -A, no -u, no pathspec expansion.
  local staged_ok=1
  while IFS= read -r p; do
    case "$p" in ''|'#'*) continue ;; esac
    git add -- "$p" || staged_ok=0
  done < "$manifest"
  [ "$staged_ok" -eq 1 ] || { echo "COMMIT result=REFUSED reason=STAGE_FAILED"; git reset -q; return 1; }

  # Scratch for the exactness proof is PROVEN outside the repository before
  # use, in the accepted order (Reviewer Pass-10 P10-01, re-applied here per
  # Stage-2 Exchange-2 item 2): canonicalize the candidate TMPDIR, fall back
  # to /tmp if it is inside the tree or invalid, create, canonicalize the
  # created directory, prove containment again, only then use it. Nothing is
  # ever created inside the tree, and a refused scratch is removed.
  local repo_real; repo_real=$(realpath .) || { git reset -q; return 1; }
  local base=${TMPDIR:-/tmp}
  local base_real; base_real=$(realpath -m "$base" 2>/dev/null) || base_real=""
  case "$base_real" in
    "$repo_real"|"$repo_real"/*|"") base=/tmp; echo "COMMIT tmpdir_rejected=inside_repository fallback=/tmp" ;;
  esac
  local tmp; tmp=$(mktemp -d "$base/u6commit-XXXXXX") || { git reset -q; return 1; }
  local tmp_real; tmp_real=$(realpath "$tmp") || { rm -rf "$tmp"; git reset -q; return 1; }
  case "$tmp_real" in
    "$repo_real"|"$repo_real"/*)
      rm -rf "$tmp"; echo "COMMIT result=REFUSED reason=SCRATCH_INSIDE_REPOSITORY"; git reset -q; return 1 ;;
  esac
  # The staged set must equal the manifest exactly - nothing more, nothing less.
  grep -vE '^[[:space:]]*(#|$)' "$manifest" | LC_ALL=C sort -u > "$tmp/expected"
  git diff --cached --name-only | LC_ALL=C sort > "$tmp/staged"
  if ! diff -q "$tmp/expected" "$tmp/staged" >/dev/null; then
    # counts only - never the paths (pasteable surface)
    echo "COMMIT result=REFUSED reason=STAGED_SET_NOT_EXACT expected=$(wc -l < "$tmp/expected" | tr -d ' ') staged=$(wc -l < "$tmp/staged" | tr -d ' ') unexpected=$(comm -13 "$tmp/expected" "$tmp/staged" | wc -l | tr -d ' ') missing=$(comm -23 "$tmp/expected" "$tmp/staged" | wc -l | tr -d ' ')"
    git reset -q; rm -rf "$tmp"; return 1
  fi
  echo "COMMIT staged=$(wc -l < "$tmp/staged" | tr -d ' ') exact_match=YES"
  rm -rf "$tmp"

  git commit -F "$msgfile" >/dev/null || { echo "COMMIT result=REFUSED reason=COMMIT_REJECTED (L1 may have blocked; see U6_RETURN)"; return 1; }

  echo "COMMIT sha=$(git rev-parse HEAD)"
  echo "COMMIT paths=$(git diff-tree --no-commit-id --name-only -r HEAD | wc -l | tr -d ' ')"
  echo "COMMIT commits=$(git rev-list --count HEAD)"

  # Unrelated working-tree state must be exactly as it was.
  local dirty_after; dirty_after=$(git status --porcelain=v1 | wc -l | tr -d ' ')
  if [ "$dirty_after" -eq "$((dirty_before - n))" ] || [ "$dirty_after" -eq "$dirty_before" ]; then
    echo "COMMIT unrelated_dirty_preserved=$dirty_after (was $dirty_before, governed=$n)"
  else
    echo "COMMIT result=WARN reason=UNRELATED_WORKTREE_STATE_CHANGED before=$dirty_before after=$dirty_after"
  fi
  echo "COMMIT result=LOCAL_ONLY"
}
main "$@"
