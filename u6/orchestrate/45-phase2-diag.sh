#!/usr/bin/env bash
# GOVERNED RUN. The frozen post-provision Phase-2 diagnostic, referenced by
# exact governed identity below and NOT repackaged, revised, or wrapped away,
# through the hardened return channel in categorical mode.
#
# The frozen instrument REQUIRES its run-directory argument:
#     reviewer_phase2_diag_rev1.py <rundir>
# and returns INSTRUMENT_INVOCATION_ERROR / rc 3 without it (Reviewer Pass-7
# P7-03). This script passes <rundir> through unchanged; it does not create,
# validate, or interpret it.
#
# NOT LIVE: reauthorized in principle only; execution requires joint lock.
# Usage: bash u6/orchestrate/45-phase2-diag.sh <path-to-reviewer_phase2_diag_rev1.py> <rundir>
# 🚨 The private run log stays local. Only the single U6_RETURN line is pasteable.
FROZEN_DIAG_SHA=4a510e00563cc5cbf00cd4a0556207148c3f488d9ce5b7a29d05c58113855d0a
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
  local diag=${1:?path to the frozen diagnostic} rundir=${2:-}
  if [ -z "$rundir" ]; then
    echo "PHASE2 result=REFUSED reason=RUNDIR_ARGUMENT_MISSING (the frozen instrument requires <rundir>; not supplying it would return INSTRUMENT_INVOCATION_ERROR rc3)"
    return 1
  fi
  export GIT_NO_REPLACE_OBJECTS=1 GIT_NO_LAZY_FETCH=1
  # --categorical: the instrument reports state as one privacy-safe line and rc 0
  # whether ready or not; that line is relayed verbatim in STATE.
  /usr/bin/python3.12 -m u6.return_channel --categorical PHASE2_DIAG "$FROZEN_DIAG_SHA" "$diag" "$rundir"
}
main "$@"
