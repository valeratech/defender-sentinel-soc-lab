#!/usr/bin/env python3
"""Falsify the Builder controls.

"A control that has never failed is not known to be a control." Each mutant
below reintroduces one defect class the integration claims to prevent. The
control suite is run against a temporary copy of the repository with that
single mutation applied; the harness PASSES only if EVERY mutant makes the
suite FAIL and the unmutated copy makes it PASS.

Mutants (id: defect class -> file, exact substitution):
  M01 ERROR rendered as REJECT (L1)
  M02 tag refs accepted (L2 fail-closed removed)
  M03 empty ref stream treated as failure (L2 NOT_RUN contract)
  M04 identity check skipped before import (engine_bind)
  M05 L3 binds the wordlist member (private reachable from CI)
  M06 return channel lets child inherit parent stdout
  M07 return channel status-file grammar accepts free text
  M08 current-state checker stops enforcing P5 reachability (forged CURRENT on an
      orphaned old revision would pass). P4 is defense-in-depth: any state P4
      catches is also caught by P3/P5/P6, so P4 has no unique mutant.
  M09 current-state checker stops enforcing P1 (pointer required)
  M10 L2 evaluates the diff (new commits only) instead of the union
  M11 L2 runs without the committed baseline (baseline invented as empty)
  M12 environment VALUES not enforced (runtime_bind A7)
  M13 private root accepts group/other-readable mode
  M14 L3 zero corpus reads as clean
  M15 L3 corpus collapses to the checked-out HEAD instead of the published branch-head union
  M16 L3 ignores tags advertised by origin
  M17 current-state checker silently passes while UNBOUND
  M18 L2 union built from pushed refs only (untouched published branch ignored)   [P5-01]
  M19 categorical mode erases the frozen instrument's state line               [P5-02]
  M20 run-log directory opened following symlinks                              [P5-03]
  M21 run-log parent validation skipped (mode/owner)                            [P5-03]
  M22 effective-interpreter identity check skipped (A4)                             [P5-06]
  M23 frozen U6 implementation presence check skipped                          [P5-06]
  M24 return channel runs the child without a validated private sink           [P5-03]
  M25 environment extension check accepts an unauthorized extra variable       [P7-01]
  M26 environment ordering not enforced                                        [P7-01]
  M27 dependency closure not required to cover gitleaks                        [P7-01]
  M28 runtime qualification happens after the first governed git invocation    [P7-01]
  M29 frozen environment authority absence treated as qualified                [P7-01]
  M30 placement deletes msgctl on failure                                      [P7-04]
  M31 Phase-2 wrapper drops the required rundir argument                       [P7-03]
  (P2-status, P3 and P4 in the current-state checker are redundant with P5/P6
   for every reachable state and therefore have no unique mutant; they are
   retained as defense-in-depth and are NOT claimed as independent controls.)

Exit 0 = all mutants killed; 1 otherwise. Prints one line per mutant.

``--mutants M01,M02`` restricts the run to named mutants (the unmutated
baseline still runs first). Chunking changes nothing about the result: each
mutant is independent, applied to its own copy of the tree.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # bytecode under a publication tree is scanned by `gitleaks dir`; never leave it

import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

MUTANTS = {
    "M01": ("u6/l1_commit_msg.py", "def _fin(log: RunLog, r: R.Result) -> R.Result:\n    log(",
            "def _fin(log: RunLog, r: R.Result) -> R.Result:\n    if r.status == R.ERROR:\n        r = R.Result(r.kind, R.REJECT, 'STRUCTURAL_FINDING', counts=r.counts)\n    log("),
    "M02": ("u6/l2_pre_push.py", 'if rref.startswith("refs/tags/"):', 'if False:'),
    "M03": ("u6/l2_pre_push.py", 'return _fin(log, R.Result(KIND, R.NOT_RUN, "NO_REF_UPDATES"))',
            'return _fin(log, R.error(KIND, "REF_STREAM_MALFORMED"))'),
    "M04": ("u6/engine_bind.py", "if sha256_file(p) != expected[rel]:", "if False:"),
    "M05": ("u6/engine_bind.py", 'L3_MEMBERS = ("serialize", "runtime", "adapter", "structural")',
            'L3_MEMBERS = ("serialize", "runtime", "adapter", "structural", "wordlist")\nL3_FORBIDDEN_OVERRIDE = True'),
    "M06": ("u6/return_channel.py", "stdout=logfd, stderr=logfd,", "stdout=None, stderr=logfd,"),
    "M07": ("u6/return_channel.py", 'm = _STATUS_RE.match(text)\n                if not m:', 'm = re.match(r"^CODE=(\\S+)", text) or re.match(r"^(.*)$", text)\n                if not m:'),
    "M08": ("scripts/check-current-state.py", "if i not in seen:", "if False:"),
    "M09": ("scripts/check-current-state.py", 'if not POINTER.is_file():\n        return fail("P1 CURRENT.txt absent")',
            'if not POINTER.is_file():\n        print("check-current-state: OK (no pointer)"); return 0'),
    "M10": ("u6/l2_pre_push.py", '            rc, out = _git("rev-list", sha)', '            rc, out = _git("rev-list", "-1", sha)'),
    "M11": ("u6/l2_pre_push.py", "if not committed_baseline.is_file():", "if False:"),
    "M12": ("u6/runtime_bind.py", '        if want != "*" and got != want:\n            return False                  # altered value', "        pass"),
    "M13": ("u6/private_root.py", "if stat.S_IMODE(st.st_mode) & 0o077:\n        os.close(fd)\n        return None, R.error(kind, \"PRIVATE_ROOT_MODE\")", "pass"),
    "M15": ("u6/l3_ci_sweep.py", '    for sha in heads:\n        rc, out = _git("rev-list", sha)', '    for sha in ["HEAD"]:\n        rc, out = _git("rev-list", sha)'),
    "M16": ("u6/l3_ci_sweep.py", "    if tags:\n", "    if False:\n"),
    "M17": ("scripts/check-current-state.py", 'if rel == "UNBOUND":\n        return fail(', 'if rel == "UNBOUND":\n        print("check-current-state: OK (unbound)"); return 0\n        return fail('),
    "M18": ("u6/l2_pre_push.py", "        heads = prospective_heads(live, updates)", "        heads = prospective_heads({}, updates)"),
    "M19": ("u6/return_channel.py", '            return _fin(log, R.Result(kind, R.PASS, "PHASE2_CATEGORICAL", state=state))', '            return _fin(log, R.Result(kind, R.PASS, "PHASE2_CATEGORICAL"))'),
    "M20": ("u6/runlog.py", "_DIR_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY", "_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY"),
    "M21": ("u6/runlog.py", "    if private and stat.S_IMODE(st.st_mode) & 0o077:\n        return False", "    pass"),
    "M22": ("u6/runtime_bind.py", '    if _sha256("/proc/self/exe") != qsha:', "    if False:"),
    "M23": ("u6/runtime_bind.py", "    if find_by_identity(spec.engine_dir, spec.u6_impl_sha) is None:", "    if False:"),
    "M24": ("u6/return_channel.py", '            if logfd is None:\n                # No validated private sink', '            if logfd is None:\n                logfd = os.open(os.devnull, os.O_WRONLY)\n            if False:\n                # No validated private sink'),
    "M25": ("u6/runtime_bind.py", '    if [n for n, _ in eff] != expected:\n        return False                      # dropped, extra, or reordered', "    pass"),
    "M26": ("u6/runtime_bind.py",
            "    eff = list(environ.items())\n    expected = [n for n, _ in frozen] + [n for n, _ in additions]",
            "    eff = sorted(environ.items())\n    expected = sorted([n for n, _ in frozen] + [n for n, _ in additions])"),
    "M27": ("u6/runtime_bind.py", 'DEP_NAMES = ("python", "git", "gitleaks")', 'DEP_NAMES = ("python", "git")'),
    "M28": ("u6/l2_pre_push.py",
            "        # 3 runtime qualification BEFORE any git invocation (Pass-7 P7-01)\n        err = bind_runtime(KIND, environ, log, runtime)",
            "        _git(\"--exec-path\")  # unqualified git executed first\n        err = bind_runtime(KIND, environ, log, runtime)"),
    # A1 authority check moved to identity-addressed resolution in Pass 10; the
    # mutant follows the check, not the old line.
    "M29": ("u6/runtime_bind.py",
            "    if env_decl is None or _sha256(env_decl) != spec.env_decl_sha:",
            "    if False:\n        pass\n    if env_decl is None:\n        env_decl = spec.engine_dir"),
    "M30": ("u6/orchestrate/25-place-engine.sh", '    echo "PLACE_ENGINE staging_retained=$stage', '    rm -rf "$stage" msgctl; echo "PLACE_ENGINE removed=$stage'),
    "M31": ("u6/orchestrate/45-phase2-diag.sh", '"$diag" "$rundir"', '"$diag"'),
    "M32": ("u6/runtime_bind.py", "    if not same:", "    if False:"),
    "M33": ("u6/runtime_bind.py", '        if qver not in token.split() and qver not in token:', "        if False:"),
    "M34": ("u6/runtime_bind.py", "        if rpath != os.path.realpath(qpath) or _sha256(rpath) != qsha:",
            "        if _sha256(rpath) != qsha:"),
    # P10-01 moved the mktemp target to "$base"; the mutant follows it and also
    # removes the post-mktemp containment proof, so it defeats BOTH guards.
    "M35": ("u6/orchestrate/25-place-engine.sh",
            '  local stage; stage=$(mktemp -d "$base/msgctl-staging-XXXXXX") || return 1',
            '  local stage; stage=$(mktemp -d "$PWD/.msgctl-staging-XXXXXX") || return 1\n  repo_real=__none__'),
    "M36": ("u6/orchestrate/25-place-engine.sh",
            '    "$repo_real"|"$repo_real"/*|"") base=/tmp', '    "__never_matches__") base=/tmp'),
    "M37": ("u6/orchestrate/25-place-engine.sh", "  remote_guard || return 1", "  git remote -v"),
    "M38": ("u6/orchestrate/10-live-head-compat.sh", 'echo "HEAD sha=$("$GIT" rev-parse HEAD)', 'echo "HEAD sha=$(git rev-parse HEAD)'),
    "M39": ("u6/orchestrate/10-live-head-compat.sh",
            '  qualify_git || { echo "COMPAT_END result=REFUSED_UNQUALIFIED_GIT"; return 1; }',
            '  GIT=git'),
    "M40": ("u6/orchestrate/25-place-engine.sh", 'echo "REMOTE configured=YES source=.git/config"   # never echo the URL itself',
            'echo "REMOTE url=$url"'),
    "M14": ("u6/l3_ci_sweep.py", 'if not shas:\n        return _fin(log, R.error(KIND, "UNION_ENUMERATION_FAILED"))  # zero corpus is not clean', "pass"),
}


def run_suite(root: Path) -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "unittest", "u6.controls.test_u6"], cwd=root, capture_output=True, env=env)
    return p.returncode == 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    selected = None
    if argv and argv[0] == "--mutants":
        selected = [m.strip() for m in argv[1].split(",") if m.strip()]
        missing = [m for m in selected if m not in MUTANTS]
        if missing:
            print(f"unknown mutant id(s): {missing}")
            return 1
    ok = True
    with tempfile.TemporaryDirectory(prefix="u6fals-") as td:
        base = Path(td) / "base"
        shutil.copytree(REPO, base, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        if not run_suite(base):
            print("BASELINE: control suite FAILS unmutated - falsification meaningless")
            return 1
        print("BASELINE: PASS (unmutated)")
        # M11 needs an L2 test that relies on the baseline being absent -> ERROR; present in suite.
        items = MUTANTS.items() if selected is None else [(m, MUTANTS[m]) for m in selected]
        for mid, (rel, old, new) in items:
            work = Path(td) / mid
            shutil.copytree(base, work)
            f = work / rel
            src = f.read_text(encoding="utf-8")
            if src.count(old) != 1:
                print(f"{mid}: HARNESS DEFECT - substitution target not unique/absent in {rel}")
                ok = False
                continue
            f.write_text(src.replace(old, new), encoding="utf-8")
            killed = not run_suite(work)
            print(f"{mid}: {'KILLED' if killed else 'SURVIVED'}  ({rel})")
            ok = ok and killed
    scope = "ALL" if selected is None else ",".join(selected)
    print(f"FALSIFICATION[{scope}]:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
