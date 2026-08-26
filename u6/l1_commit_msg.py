"""L1 - local commit-message enforcement (native ``commit-msg`` hook).

Frozen contract:
  * operates on the VERBATIM bytes of the message file git hands the hook;
    no cleanup/normalization emulation;
  * consumes structural rules and the private wordlist; consumes NO
    private baseline (exemptions are an L2 concern);
  * runs only under the frozen Unit-6 runtime contract (u6.runtime_bind);
  * distinguishes PASS (rc 0), REJECT (rc 1), ERROR (rc 2);
  * an execution/configuration ERROR is never rendered as REJECT.

stdout: exactly one U6_RETURN line. Finding detail: private run log only.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from . import result as R
from .engine_bind import L1_MEMBERS, bind
from .engine_iface import Iface
from .private_root import wordlist_path
from .runlog import RunLog
from .runtime_bind import bind_runtime

KIND = "L1"


def evaluate(msg_path: Path, *, engine_dir=None, identity_file=None, runtime=None, environ=None) -> R.Result:
    log = RunLog(KIND)
    return _evaluate(msg_path, log, engine_dir, identity_file, runtime, environ)


def _evaluate(msg_path: Path, log: RunLog, engine_dir, identity_file, runtime, environ) -> R.Result:
    # 1. verbatim bytes first - if we cannot read what git gave us, ERROR.
    if not msg_path.is_file():
        return _fin(log, R.error(KIND, "MSG_FILE_ABSENT"))
    try:
        raw = msg_path.read_bytes()
    except OSError:
        return _fin(log, R.error(KIND, "MSG_FILE_UNREADABLE"))
    log(f"message bytes={len(raw)}")

    # 1b. frozen Unit-6 runtime contract (interpreter, git, env, U6 impl identity).
    err = bind_runtime(KIND, os.environ if environ is None else environ, log, runtime)
    if err:
        return _fin(log, err)

    # 2. engine identity binding BEFORE first detector use.
    eng, err = bind(KIND, L1_MEMBERS, engine_dir, identity_file)
    if err:
        return _fin(log, err)
    api = Iface(KIND, eng, log)

    # 3. wordlist presence (private, local-only).
    wl_path, err = wordlist_path(KIND)
    if err:
        return _fin(log, err)

    # 4. verbatim extraction via frozen adapter.
    msg, err = api.extract_l1(raw)
    if err:
        return _fin(log, err)
    if not isinstance(msg, (bytes, bytearray)):
        log("adapter.extract_l1 returned non-bytes")
        return _fin(log, R.error(KIND, "ENGINE_CALL_FAILED"))

    # 5. structural.
    sfind, err = api.structural_scan(bytes(msg))
    if err:
        return _fin(log, err)
    for f in sfind:
        log(f"structural finding detector={api.struct_detector_id(f)}")

    # 6. wordlist.
    terms, err = api.wordlist_load(wl_path)
    if err:
        return _fin(log, err)
    wfind, err = api.wordlist_scan(terms, bytes(msg))
    if err:
        return _fin(log, err)
    log(f"wordlist findings={len(wfind)}")  # counts only; never term text

    counts = {"structural": len(sfind), "wordlist": len(wfind)}
    if wfind:
        return _fin(log, R.Result(KIND, R.REJECT, "WORDLIST_FINDING", counts=counts))
    if sfind:
        return _fin(log, R.Result(KIND, R.REJECT, "STRUCTURAL_FINDING", counts=counts))
    return _fin(log, R.Result(KIND, R.PASS, "OK", counts=counts))


def _fin(log: RunLog, r: R.Result) -> R.Result:
    log(f"result status={r.status} code={r.code}")
    log.close()
    return r


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        r = R.error(KIND, "MSG_FILE_ABSENT")
    else:
        r = evaluate(Path(argv[0]))
    sys.stdout.write(r.render() + "\n")
    sys.stdout.flush()
    return r.rc


if __name__ == "__main__":
    sys.exit(main())
