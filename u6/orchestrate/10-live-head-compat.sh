#!/usr/bin/env bash
# READ-ONLY consolidated compatibility / current-state check.
# Compares the live working tree to the governed snapshot by a BUILDER-DEFINED
# SNAPSHOT COMPATIBILITY DIGEST. This is NOT the historical
# TREE-DIGEST-PROCEDURE.txt (that original is absent and is not reconstructed
# here) and its value is not the historical 3cc2cb79... tree digest.
# Algorithm: for every tracked path, one line "<sha256(bytes)>  <path>\n";
# lines sorted by path in C collation; sha256 of the concatenation.
# Input set: the 137 files of the verified snapshot ZIP ffd49949...afb3
# (package evidence: snapshot-tree-digest.txt lists every line).
SNAPSHOT_TREE_DIGEST=273e4b48ccc5b275d719d5af53e941a2c4a7ac0a287dccdd3f76a6c1bf39d468
SNAPSHOT_FILE_COUNT=137
# Qualified Git for this pre-overlay step. u6/ does not exist yet at step 10,
# so the immutable Reviewer-authority identities are bound literally here.
# Resolution never trusts PATH: the object must BE /usr/bin/git, its bytes must
# match, and only then is it probed. A shadow git earlier on PATH is therefore
# never executed (Reviewer remediation-2 item 1).
QUALIFIED_GIT=/usr/bin/git
QUALIFIED_GIT_SHA=f54a87f6253aab09ed7b522bd78ddeab509105b1043076209d89127e55877a48
QUALIFIED_GIT_VERSION=2.54.0
GIT=""
qualify_git() {
  local resolved; resolved=$(realpath "$QUALIFIED_GIT" 2>/dev/null) || {
    echo "GIT_UNQUALIFIED reason=ABSENT"; return 1; }
  [ "$resolved" = "$QUALIFIED_GIT" ] || { echo "GIT_UNQUALIFIED reason=NOT_THE_QUALIFIED_PATH"; return 1; }
  local sha; sha=$(sha256sum "$resolved" | cut -d' ' -f1)
  [ "$sha" = "$QUALIFIED_GIT_SHA" ] || { echo "GIT_UNQUALIFIED reason=BYTES_NOT_QUALIFIED"; return 1; }
  local ver; ver=$("$resolved" --version 2>&1)
  case "$ver" in *"$QUALIFIED_GIT_VERSION"*) ;; *) echo "GIT_UNQUALIFIED reason=VERSION_TOKEN"; return 1;; esac
  GIT="$resolved"
  echo "GIT_QUALIFIED path=$GIT version=$QUALIFIED_GIT_VERSION"
}

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
  qualify_git || { echo "COMPAT_END result=REFUSED_UNQUALIFIED_GIT"; return 1; }
  echo "COMPAT_BEGIN"
  echo "HEAD sha=$("$GIT" rev-parse HEAD) branch=$("$GIT" rev-parse --abbrev-ref HEAD) commits=$("$GIT" rev-list --count HEAD)"
  echo "REMOTE_MAIN sha=$("$GIT" rev-parse --verify -q origin/main || echo UNKNOWN)"
  local dirty; dirty=$("$GIT" status --porcelain | wc -l)
  echo "WORKTREE dirty_entries=$dirty untracked_ignored_excluded=YES"
  local n; n=$("$GIT" ls-files | wc -l)
  local digest
  digest=$("$GIT" ls-files -z | LC_ALL=C sort -z | while IFS= read -r -d '' f; do printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f"; done | sha256sum | cut -d' ' -f1)
  echo "TREE tracked_files=$n digest=$digest"
  echo "SNAPSHOT expected_files=$SNAPSHOT_FILE_COUNT expected_digest=$SNAPSHOT_TREE_DIGEST"
  if [ "$digest" = "$SNAPSHOT_TREE_DIGEST" ] && [ "$n" -eq "$SNAPSHOT_FILE_COUNT" ] && [ "$dirty" -eq 0 ]; then
    echo "COMPAT_END result=IDENTICAL_TO_GOVERNED_SNAPSHOT"; return 0
  fi
  echo "COMPAT_END result=DIVERGENT (do not apply the candidate; return this block to Builder and Reviewer)"
  return 1
}
main "$@"
