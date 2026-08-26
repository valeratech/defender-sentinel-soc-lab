"""Structurally hardened STOP/error return channel.

Problem (PRIV-002): the first full adjudication relied on a human-visible
"do not paste below this line" marker. It was breached. A marker is advice;
this module is a boundary.

Mechanism:
  1. The governed child program is bound by expected SHA-256 before exec.
  2. The child is exec'd with fd 1 and fd 2 already redirected into the
     private run log (0600, account-home sibling of the private root,
     opened relative to a validated directory with no-follow semantics) and
     fd 0 closed. Nothing derived from that log - no digest, no commitment -
     is ever transported; the log's SHA-256 stays in a private sidecar. The child CANNOT write to the operator's terminal: it has
     no descriptor that reaches it. Nothing the child prints can be pasted
     because it is never displayed.
  3. The child reports its categorical outcome ONLY by exit code and by an
     optional status file it may write at the path in the environment
     variable U6_STATUS_FILE (frozen children that know nothing of this
     channel simply never write it and are mapped by exit code alone). The
     status file grammar is: one line, ``CODE=<token>``, token in
     result.CODES. Anything else -> ERROR/STATUS_FILE_MALFORMED.
  4. The parent builds ONE U6_RETURN record from (exit code, validated
     status token) and writes that line, and only that line, to its own
     stdout. The record grammar admits no free text and carries no digest.

Exit-code mapping (categorical, matches the frozen STOP_RC vocabulary):
    0 -> PASS/OK  or the child's CODE if it names a PASS-class code
    1 -> STOP/STOP_RC_1     2 -> STOP/STOP_RC_2     3 -> STOP/STOP_RC_3
    other -> STOP/STOP_RC_OTHER     signalled -> ERROR/CHILD_SIGNALLED

Categorical mode (--categorical, used only for the frozen Phase-2
diagnostic): the frozen instrument reports its state as ONE privacy-safe
line of uppercase KEY=VALUE tokens and returns rc 0 for every ordinary
classification, ready or not. Erasing that line would collapse READY and
NOT-READY into the same PASS (Reviewer Pass-5 P5-02). In this mode the
parent reads the child's LAST stdout line from the private log, requires it
to match the strict token grammar (no paths, digits-only values allowed,
no free text), and relays it in the STATE field of the record. A line that
fails the grammar is not relayed; the result is ERROR/CATEGORICAL_MALFORMED.
The instrument is not modified.

Usage: python3 -m u6.return_channel [--categorical] <KIND> <expected-sha256> <child> [args...]
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from . import result as R
from .runlog import RunLog
from .runtime_bind import bind_runtime

_STATUS_RE = re.compile(r"^CODE=([A-Z0-9_]{1,40})\n?$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
PASS_CLASS = {"OK", "PHASE2_READY"}
NOT_READY_CLASS = {"PHASE2_NOT_READY", "PHASE2_UNDETERMINED"}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def run(kind: str, expected_sha: str, child: Path, args: list[str], *, env: dict | None = None,
        categorical: bool = False, runtime=None, bind: bool = True) -> R.Result:
    log = RunLog(kind)
    try:
        if bind:
            err = bind_runtime(kind, env if env is not None else os.environ, log, runtime)
            if err:
                return _fin(log, err)
        if not _SHA.match(expected_sha):
            return _fin(log, R.error(kind, "CHILD_IDENTITY_MISMATCH"))
        if not child.is_file():
            return _fin(log, R.error(kind, "CHILD_ABSENT"))
        actual = _sha256(child)
        log(f"child identity actual={actual} expected={expected_sha}")
        if actual != expected_sha:
            return _fin(log, R.error(kind, "CHILD_IDENTITY_MISMATCH"))
        with tempfile.TemporaryDirectory(prefix="u6-ret-") as td:
            status_path = Path(td) / "status"
            # Child fds: 0 closed, 1 and 2 -> private log file. Parent stdout
            # is not inherited: the child process has no route to it.
            log("--- child output begins (private) ---")
            logfd = log.reopen_for_child()
            if logfd is None:
                # No validated private sink: the child must not run, because
                # its output would have nowhere safe to go.
                return _fin(log, R.error(kind, "PRIVATE_SINK_UNAVAILABLE"))
            try:
                child_env = dict(env if env is not None else os.environ)
                child_env["U6_STATUS_FILE"] = str(status_path)
                p = subprocess.run(
                    [sys.executable, str(child), *args],
                    stdin=subprocess.DEVNULL, stdout=logfd, stderr=logfd,
                    env=child_env, close_fds=True,
                )
            finally:
                os.close(logfd)
            # Child bytes were appended by the child's own descriptor; resync
            # the private buffer, then find the child's last line if needed.
            log.resync_from_disk()
            child_last = _last_child_line(log.buf)
            log("--- child output ends ---")
            rc = p.returncode
            if rc < 0:
                return _fin(log, R.error(kind, "CHILD_SIGNALLED"))
            token = None
            if status_path.exists():
                try:
                    raw = status_path.read_bytes()
                except OSError:
                    return _fin(log, R.error(kind, "STATUS_FILE_MALFORMED"))
                try:
                    text = raw.decode("ascii", "strict")
                except UnicodeDecodeError:
                    return _fin(log, R.error(kind, "STATUS_FILE_MALFORMED"))
                m = _STATUS_RE.match(text)
                if not m:
                    return _fin(log, R.error(kind, "STATUS_FILE_MALFORMED"))
                token = m.group(1)
                if token not in R.CODES:
                    return _fin(log, R.error(kind, "STATUS_FILE_UNEXPECTED"))
        log(f"child rc={rc} token={token}")
        if categorical:
            if rc != 0:
                code = {1: "STOP_RC_1", 2: "STOP_RC_2", 3: "STOP_RC_3"}.get(rc, "STOP_RC_OTHER")
                return _fin(log, R.Result(kind, R.STOP, code))
            state = _categorical(child_last)
            if state is None:
                return _fin(log, R.error(kind, "CATEGORICAL_MALFORMED"))
            return _fin(log, R.Result(kind, R.PASS, "PHASE2_CATEGORICAL", state=state))
        if rc == 0:
            if token is None or token in PASS_CLASS:
                return _fin(log, R.Result(kind, R.PASS, token or "OK"))
            if token in NOT_READY_CLASS:
                return _fin(log, R.Result(kind, R.STOP, token))
            return _fin(log, R.error(kind, "STATUS_FILE_UNEXPECTED"))
        code = {1: "STOP_RC_1", 2: "STOP_RC_2", 3: "STOP_RC_3"}.get(rc, "STOP_RC_OTHER")
        return _fin(log, R.Result(kind, R.STOP, code))
    finally:
        pass


_CAT_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]{0,39}=[A-Z0-9_]{1,40}$")
_BEGIN = b"--- child output begins (private) ---\n"


def _last_child_line(buf: bytes) -> bytes | None:
    i = buf.find(_BEGIN)
    if i < 0:
        return None
    body = bytes(buf[i + len(_BEGIN):])
    lines = [l for l in body.split(b"\n") if l.strip()]
    return lines[-1] if lines else None


def _categorical(line: bytes | None):
    """Strict privacy-safe grammar: 1..8 uppercase KEY=VALUE tokens, ASCII only."""
    if line is None or len(line) > 400:
        return None
    try:
        text = line.decode("ascii", "strict").strip()
    except UnicodeDecodeError:
        return None
    toks = text.split(" ")
    if not 1 <= len(toks) <= 8 or any(not _CAT_TOKEN.match(t) for t in toks):
        return None
    return " ".join(toks)


def _fin(log: RunLog, r: R.Result) -> R.Result:
    log(f"result status={r.status} code={r.code}")
    log.close()
    return r


def emit(r: R.Result) -> int:
    """The ONLY writer to the transportable channel. Re-validates the line."""
    line = r.render()
    if not R.RECORD_RE.match(line):
        line = R.error(r.kind, "TRANSPORT_LINE_REJECTED").render()
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    return R.parse(line).rc


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    categorical = False
    if argv and argv[0] == "--categorical":
        categorical = True
        argv = argv[1:]
    if len(argv) < 3:
        return emit(R.error("RETURN", "CHILD_ABSENT"))
    kind, sha, child, *args = argv
    if not re.match(r"^[A-Z0-9_]{2,32}$", kind):
        return emit(R.error("RETURN", "CHILD_ABSENT"))
    return emit(run(kind, sha, Path(child), args, categorical=categorical))


if __name__ == "__main__":
    sys.exit(main())
