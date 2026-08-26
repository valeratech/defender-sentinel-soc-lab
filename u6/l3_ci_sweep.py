"""L3 - CI structural-only union sweep. DETECTIVE / ADVISORY.

Frozen contract:
  * structural rules only; never the preventive authority (L2 is);
  * query-time corpus semantics: the corpus is the COMPLETE PUBLISHED
    BRANCH-HEAD UNION - every commit reachable from every ``refs/heads/*``
    the origin remote advertises at the moment of the query (``git
    ls-remote --heads``). Not HEAD, not an event range, not event.before,
    not a changed-commit subset. Any tag advertised by origin fails closed
    (ERROR/TAG_REF_REFUSED): tag publication is outside the frozen
    contract and the workflow runs on tag pushes so this is exercised;
  * expected-executable-hash binding BEFORE first detector use;
  * private wordlist, baseline.key, private-baseline, K_term, K_auth, raw
    term values, private commit prose and adjudication evidence are absent
    from CI BY CONSTRUCTION:
      - this module imports nothing from u6.private_root;
      - it binds L3_MEMBERS only (engine_bind refuses wordlist/baseline/
        crypto/identity for KIND=L3 - they are not in the allowed set);
      - it takes no path, env var or CLI argument that could name private
        material;
      - controls/check_l3_isolation.py proves the above statically (AST) and
        dynamically (sys.modules after a run).

Exit: findings are ADVISORY (rc 0, CODE=L3_ADVISORY_FINDINGS, counts on the
record and GitHub annotations). Mechanism failure is rc 2 (ERROR): a sweep
that cannot prove it looked must not read as clean.
"""
from __future__ import annotations

import subprocess
import sys

from . import result as R
from .engine_bind import L3_FORBIDDEN, L3_MEMBERS, REPO_ROOT, bind, sys_modules_reach
from .engine_iface import Iface
from .runlog import RunLog

KIND = "L3"


def _git(*args: str) -> tuple[int, bytes]:
    p = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True)
    return p.returncode, p.stdout


def published_refs():
    """Query origin at run time. Returns (head_shas, tag_count) or (None, None)."""
    rc, out = _git("ls-remote", "--heads", "--tags", "origin")
    if rc != 0:
        return None, None
    heads, tags = [], 0
    for line in out.decode("utf-8", "replace").splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            return None, None
        sha, ref = parts
        if ref.startswith("refs/tags/"):
            tags += 1
        elif ref.startswith("refs/heads/"):
            heads.append(sha)
    return heads, tags


def corpus(heads: list[str]) -> list[str] | None:
    """Union of commits reachable from every published head."""
    union: set[str] = set()
    for sha in heads:
        rc, out = _git("rev-list", sha)
        if rc != 0:
            return None
        union.update(out.decode("ascii", "replace").split())
    return sorted(union)


def message_bytes(sha: str):
    rc, out = _git("cat-file", "commit", sha)
    if rc != 0:
        return None
    _, sep, body = out.partition(b"\n\n")
    return body if sep else b""


def evaluate(*, engine_dir=None, identity_file=None, annotate: bool = False) -> R.Result:
    log = RunLog(KIND)
    eng, err = bind(KIND, L3_MEMBERS, engine_dir, identity_file)
    if err:
        return _fin(log, err)
    # Prove, in-process, that no private member became reachable.
    if sys_modules_reach(L3_FORBIDDEN, KIND):
        return _fin(log, R.error(KIND, "L3_PRIVATE_SYMBOL_REACHABLE"))
    api = Iface(KIND, eng, log)
    heads, tags = published_refs()
    if heads is None:
        return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))
    if tags:
        log(f"origin advertises tags={tags}: fail closed")
        return _fin(log, R.error(KIND, "TAG_REF_REFUSED"))
    log(f"published heads={len(heads)}")
    shas = corpus(heads)
    if shas is None:
        return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))
    if not shas:
        return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))  # zero corpus is not clean
    n = 0
    by_detector: dict[str, int] = {}
    for sha in shas:
        msg = message_bytes(sha)
        if msg is None:
            return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))
        vb, err = api.extract_l1(msg)
        if err:
            return _fin(log, err)
        sf, err = api.structural_scan(bytes(vb))
        if err:
            return _fin(log, err)
        for f in sf:
            n += 1
            d = api.struct_detector_id(f)
            by_detector[d] = by_detector.get(d, 0) + 1
            log(f"structural finding commit={sha} detector={d}")
            if annotate:
                # Detector ID + commit only. No message text ever leaves the process.
                sys.stderr.write(f"::warning title=L3 structural::commit {sha} detector {d}\n")
    counts = {"heads": len(heads), "commits": len(shas), "structural": n}
    if sys_modules_reach(L3_FORBIDDEN, KIND):
        return _fin(log, R.error(KIND, "L3_PRIVATE_SYMBOL_REACHABLE"))
    code = "L3_ADVISORY_FINDINGS" if n else "L3_CLEAN"
    return _fin(log, R.Result(KIND, R.PASS, code, counts=counts))


def _fin(log: RunLog, r: R.Result) -> R.Result:
    log(f"result status={r.status} code={r.code}")
    log.close()
    return r


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    r = evaluate(annotate=("--annotate" in argv))
    sys.stdout.write(r.render() + "\n")
    sys.stdout.flush()
    return r.rc


if __name__ == "__main__":
    sys.exit(main())
