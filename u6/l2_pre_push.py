"""L2 - preventive native ``pre-push`` enforcement.

Frozen contract:
  * evaluates the COMPLETE prospective published union: the live origin
    head set is queried in the same run (git ls-remote --heads origin), the
    outgoing update tuples are applied to it (update/create/delete), and
    every commit reachable from every head of the RESULTING set is scanned.
    A violation on an already-published branch this push does not touch
    still rejects (Reviewer Pass-5 P5-01). Not a diff, not the pushed refs;
  * consumes structural rules + private wordlist + accepted current L2
    baseline (committed half via baseline.load_committed, private half via
    parse_private/c4_validate);
  * single resolved ``origin`` push endpoint;
  * ``refs/heads/*`` only; any tag or other ref namespace fails closed;
  * a valid EMPTY ref-update stream yields NO_REF_UPDATES / L2_NOT_RUN and
    is not a failure (rc 0);
  * the current L2 expected baseline is NOT invented here. While the
    committed baseline artifact is absent the layer returns
    ERROR/BASELINE_UNRESOLVED (fail closed) - see docs/unit6/IMPLEMENTATION.md
    §"Baseline binding".

Load-bearing order used here (Builder-ordered; see disclosed limitation D-2):
  1 ref-update stream        2 ref namespace fail-closed
  3 frozen runtime contract  4 origin endpoint (FIRST git invocation)
  5 engine identity binding  6 private state + baseline (C4)
  7 prospective head set (live origin heads + updates) -> union -> evaluation

No git process is started before step 3 returns qualified: an unqualified or
shadowed git must be rejected, not executed.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from . import result as R
from .engine_bind import L2_MEMBERS, REPO_ROOT, bind
from .engine_iface import Iface
from .private_root import BASELINE, KEY, KEY_LEN, open_root, read_member, wordlist_path
from .runlog import RunLog
from .runtime_bind import bind_runtime

KIND = "L2"
ZERO = "0" * 40
COMMITTED_BASELINE = REPO_ROOT / "u6" / "committed-baseline"


def _git(*args: str) -> tuple[int, bytes]:
    p = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True)
    return p.returncode, p.stdout


def parse_ref_stream(data: bytes):
    """Return (updates, code). updates = list of (local_ref, local_sha, remote_ref, remote_sha)."""
    updates = []
    for raw in data.split(b"\n"):
        if not raw.strip():
            continue
        parts = raw.split(b" ")
        if len(parts) != 4 or not all(_utf8(x) for x in parts):
            return None, "REF_STREAM_MALFORMED"
        lref, lsha, rref, rsha = (x.decode("utf-8") for x in parts)
        if not (_sha40(lsha) and _sha40(rsha)) or not lref or not rref:
            return None, "REF_STREAM_MALFORMED"
        updates.append((lref, lsha, rref, rsha))
    return updates, None


def _utf8(b: bytes) -> bool:
    try:
        b.decode("utf-8", "strict")
        return True
    except UnicodeDecodeError:
        return False


def _sha40(s: str) -> bool:
    return len(s) == 40 and all(c in "0123456789abcdef" for c in s)


def commit_message_bytes(sha: str):
    rc, out = _git("cat-file", "commit", sha)
    if rc != 0:
        return None
    head, sep, body = out.partition(b"\n\n")
    return body if sep else b""


def live_origin_heads():
    """(dict ref->sha, None) or (None, code). Queried at run time from origin."""
    rc, out = _git("ls-remote", "--heads", "origin")
    if rc != 0:
        return None, "REMOTE_QUERY_FAILED"
    heads = {}
    for line in out.decode("utf-8", "replace").splitlines():
        parts = line.split("\t")
        if len(parts) != 2 or not _sha40(parts[0]) or not parts[1].startswith("refs/heads/"):
            return None, "REMOTE_QUERY_FAILED"
        heads[parts[1]] = parts[0]
    return heads, None


def prospective_heads(live: dict, updates) -> dict:
    """Apply the outgoing update tuples to the live head set."""
    result = dict(live)
    for lref, lsha, rref, rsha in updates:
        if lsha == ZERO:
            result.pop(rref, None)      # deletion
        else:
            result[rref] = lsha         # create or update
    return result


def evaluate(remote_name: str, remote_url: str, stream: bytes, *, engine_dir=None,
             identity_file=None, environ=None, committed_baseline: Path | None = None,
             runtime=None) -> R.Result:
    log = RunLog(KIND)
    environ = os.environ if environ is None else environ
    committed_baseline = committed_baseline or COMMITTED_BASELINE
    key = None
    root_fd = None
    try:
        # 1 ref-update stream
        updates, code = parse_ref_stream(stream)
        if code:
            return _fin(log, R.error(KIND, code))
        if not updates:
            log("L2_NOT_RUN: empty ref-update stream")
            return _fin(log, R.Result(KIND, R.NOT_RUN, "NO_REF_UPDATES"))
        # 2 ref namespace fail-closed
        for lref, lsha, rref, rsha in updates:
            if rref.startswith("refs/tags/"):
                return _fin(log, R.Result(KIND, R.REJECT, "TAG_REF_REFUSED"))
            if not rref.startswith("refs/heads/"):
                return _fin(log, R.Result(KIND, R.REJECT, "NON_HEAD_REF_REFUSED"))
        # 3 runtime qualification BEFORE any git invocation (Pass-7 P7-01)
        err = bind_runtime(KIND, environ, log, runtime)
        if err:
            return _fin(log, err)
        # 4 single resolved origin endpoint (first governed git use)
        if remote_name != "origin":
            return _fin(log, R.Result(KIND, R.REJECT, "REMOTE_NOT_ORIGIN"))
        rc1, fetch_url = _git("remote", "get-url", "origin")
        rc2, push_url = _git("remote", "get-url", "--push", "origin")
        urls = {fetch_url.strip().decode("utf-8", "replace"), push_url.strip().decode("utf-8", "replace")}
        if rc1 or rc2 or len(urls) != 1 or remote_url not in urls:
            return _fin(log, R.Result(KIND, R.REJECT, "ORIGIN_URL_MISMATCH"))
        # 5 engine identity binding before first detector use
        eng, err = bind(KIND, L2_MEMBERS, engine_dir, identity_file)
        if err:
            return _fin(log, err)
        api = Iface(KIND, eng, log)
        # 6 private state + baseline
        wl_path, err = wordlist_path(KIND)
        if err:
            return _fin(log, err)
        if not committed_baseline.is_file():
            log("committed baseline absent - current L2 expected baseline NOT ESTABLISHED")
            return _fin(log, R.error(KIND, "BASELINE_UNRESOLVED"))
        root_fd, err = open_root(KIND)
        if err:
            return _fin(log, err)
        key, err = read_member(KIND, root_fd, KEY, exact_len=KEY_LEN)
        if err:
            return _fin(log, err)
        priv_raw, err = read_member(KIND, root_fd, BASELINE)
        if err:
            return _fin(log, err)
        committed, err = api.baseline_load_committed(committed_baseline)
        if err:
            return _fin(log, err)
        private, err = api.baseline_parse_private(priv_raw, key)
        if err:
            return _fin(log, err)
        c4, err = api.baseline_c4_validate(committed, private)
        if err:
            return _fin(log, err)
        failures = list(getattr(c4, "failures", []) or [])
        if failures:
            log(f"C4 failures={len(failures)}")
            return _fin(log, R.error(KIND, "BASELINE_C4_FAILED"))
        terms, err = api.wordlist_load(wl_path)
        if err:
            return _fin(log, err)
        # 7 prospective head set -> complete union -> evaluation
        live, code = live_origin_heads()
        if code:
            return _fin(log, R.error(KIND, code))
        heads = prospective_heads(live, updates)
        log(f"live heads={len(live)} prospective heads={len(heads)}")
        union: set[str] = set()
        for ref, sha in sorted(heads.items()):
            rc, _ = _git("cat-file", "-e", f"{sha}^{{commit}}")
            if rc != 0:
                log(f"published head not present locally: {ref}")
                return _fin(log, R.error(KIND, "REMOTE_HEAD_NOT_LOCAL"))
            rc, out = _git("rev-list", sha)
            if rc != 0:
                return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))
            union.update(out.decode("ascii", "replace").split())
        if not union:
            return _fin(log, R.Result(KIND, R.PASS, "OK", counts={"heads": 0, "commits": 0, "structural": 0, "wordlist": 0, "exempt": 0}))
        log(f"union commits={len(union)}")
        n_struct = n_word = n_exempt = 0
        for sha in sorted(union):
            msg = commit_message_bytes(sha)
            if msg is None:
                return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))
            vb, err = api.extract_l1(msg)
            if err:
                return _fin(log, err)
            sf, err = api.structural_scan(bytes(vb))
            if err:
                return _fin(log, err)
            wf, err = api.wordlist_scan(terms, bytes(vb))
            if err:
                return _fin(log, err)
            for f in list(sf) + list(wf):
                ex, err = api.baseline_is_exempt(private, sha, f)
                if err:
                    return _fin(log, err)
                if ex:
                    n_exempt += 1
                    continue
                if f in sf:
                    n_struct += 1
                    log(f"union finding commit={sha} detector={api.struct_detector_id(f)}")
                else:
                    n_word += 1
                    log(f"union wordlist finding commit={sha}")
        counts = {"heads": len(heads), "commits": len(union), "structural": n_struct, "wordlist": n_word, "exempt": n_exempt}
        if n_struct or n_word:
            return _fin(log, R.Result(KIND, R.REJECT, "UNION_FINDING", counts=counts))
        return _fin(log, R.Result(KIND, R.PASS, "OK", counts=counts))
    finally:
        if key is not None:
            try:
                key = bytearray(key)
                for i in range(len(key)):
                    key[i] = 0
            except Exception:  # noqa: BLE001
                pass
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass


def _fin(log: RunLog, r: R.Result) -> R.Result:
    log(f"result status={r.status} code={r.code}")
    log.close()
    return r


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        r = R.error(KIND, "REMOTE_NOT_ORIGIN")
    else:
        r = evaluate(argv[0], argv[1], sys.stdin.buffer.read())
    sys.stdout.write(r.render() + "\n")
    sys.stdout.flush()
    return r.rc


if __name__ == "__main__":
    sys.exit(main())
