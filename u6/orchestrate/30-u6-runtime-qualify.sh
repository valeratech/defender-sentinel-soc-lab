#!/usr/bin/env bash
# GOVERNED RUN (read-only). Runs the FROZEN Unit-6 implementation's own
# runtime composition through the hardened return channel so that EFFECTIVE
# U6 state is derived by the frozen procedure from the objects it consumes,
# and compared to the EXPECTED identities recorded in u6/RUNTIME-IDENTITIES.txt.
# The Builder does not reimplement that composition.
# Runs AFTER 20 (u6/ installed) and 25 (msgctl/ placed): both are prerequisites,
# because this script is itself part of the candidate and the frozen members it
# binds are placed by 25 (Reviewer Pass-7 P7-02).
# Refuses (CHILD_IDENTITY_MISMATCH / CHILD_ABSENT) unless the file at $1 hashes
# to the frozen U6 implementation identity; msgctl/u6runtime.py placed by 25 is
# that file. NOT LIVE.
FROZEN_U6_IMPL_SHA=35ee40c3b9d794881f45adbbec20e7e5832c0ec9c533de02f107e15fe494a21a
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
  export GIT_NO_REPLACE_OBJECTS=1 GIT_NO_LAZY_FETCH=1
  /usr/bin/python3.12 -m u6.return_channel --categorical U6_QUALIFY "$FROZEN_U6_IMPL_SHA" "${1:-msgctl/u6runtime.py}" "${@:2}"
}
main "$@"
