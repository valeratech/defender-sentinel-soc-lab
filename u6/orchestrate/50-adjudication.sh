#!/usr/bin/env bash
# GOVERNED RUN. NOT AUTHORIZED. Frozen adjudication wrapper runtime through the
# hardened return channel. Listed so the exact invocation exists for a future
# joint lock; nothing here is live.
FROZEN_WRAPPER_SHA=c6be8ffb8836f3ed9ad11ee2af0852c0d89a99c1bc0a570491132dd6b29436cd
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
  /usr/bin/python3.12 -m u6.return_channel ADJUDICATION "$FROZEN_WRAPPER_SHA" "${1:?path to frozen wrapper runtime}" "${@:2}"
}
main "$@"
