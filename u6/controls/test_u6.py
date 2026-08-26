"""Builder controls for the Unit-6 operational integration.

Run:  python3 -m unittest u6.controls.test_u6 -v      (from repository root)
Falsify: python3 u6/controls/falsify.py               (each mutant must FAIL)

These controls bind the LABELLED TEST DOUBLE (u6/controls/double) through
engine_bind with the double's own identity manifest. They exercise the
integration layer's contracts, not the frozen engine's detectors. They
never touch the operator's real private root, real wordlist, or real
repository: private-root resolution, the account-home used for run logs,
and REPO_ROOT are patched in-process for the duration of each test.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # bytecode under a publication tree is scanned by `gitleaks dir`; never leave it

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
U6 = HERE.parent
REPO = U6.parent
sys.path.insert(0, str(REPO))

from u6 import engine_bind, l1_commit_msg, l2_pre_push, l3_ci_sweep, private_root, result as R, return_channel, runlog, runtime_bind  # noqa: E402

DOUBLE = HERE / "double"
DOUBLE_IDS = DOUBLE / "double-identities.txt"
ADDITIONS = (("GIT_NO_REPLACE_OBJECTS", "1"), ("GIT_NO_LAZY_FETCH", "1"))
ENV_OK = dict(ADDITIONS)

# --- runtime authority doubles -------------------------------------------
# The battery tests the CONTRACT against labelled doubles built from the
# sandbox's own objects. No frozen literal is ever asserted here, and
# production never accepts a spec override (see test_production_spec_binds_frozen).
_AUTH = Path(tempfile.mkdtemp(prefix="u6auth-"))
_BIN = _AUTH / "bin"; _BIN.mkdir()
# The battery must not depend on the operator's qualified gitleaks object being
# installed in this sandbox: it qualifies a labelled stand-in of its own and
# tests that the CONTRACT binds all three dependencies.
shutil.copy(shutil.which("git"), _BIN / "git")
_gl = shutil.which("gitleaks") or "/tmp/gitleaks"
shutil.copy(_gl if os.path.exists(_gl) else shutil.which("git"), _BIN / "gitleaks")
for _f in (_BIN / "git", _BIN / "gitleaks"):
    os.chmod(_f, 0o755)
_DECL_LINES = [l for l in (DOUBLE / "u6-bounded-env.decl").read_text().splitlines()
               if l.strip() and not l.startswith("#") and not l.startswith("PATH=")]
# PATH is declared host-specific ("*"): the declaration governs MEMBERSHIP and
# ORDER, while the dependency manifest pins the OBJECTS. A shadowed PATH is
# therefore caught at A5 (the object is not the qualified one), not masked as a
# generic environment violation.
(_AUTH / "env.decl").write_text("PATH=*\n" + "\n".join(_DECL_LINES) + "\n")
def _probe_version(path, args):
    out = subprocess.run([str(path), *args], capture_output=True)
    return (out.stdout + out.stderr).decode().split()[-1]


_VERSIONS = {"python": subprocess.run([os.path.realpath("/proc/self/exe"), "--version"],
                                      capture_output=True).stdout.decode().split()[-1],
             "git": _probe_version(_BIN / "git", ("--version",)),
             "gitleaks": _probe_version(_BIN / "gitleaks", ("version",))}
(_AUTH / "dep.manifest").write_text("".join(
    f"{n} {p} {runtime_bind._sha256(p)} {_VERSIONS[n]}\n"
    for n, p in (("python", os.path.realpath("/proc/self/exe")),
                 ("git", str(_BIN / "git")), ("gitleaks", str(_BIN / "gitleaks")))))
FROZEN_ENV_DOUBLE = runtime_bind._parse_env_decl(_AUTH / "env.decl")


def runtime_double(engine_dir=DOUBLE, env_decl=None, dep_manifest=None) -> runtime_bind.RuntimeSpec:
    ed = env_decl or (_AUTH / "env.decl")
    dm = dep_manifest or (_AUTH / "dep.manifest")
    return runtime_bind.RuntimeSpec(
        env_decl_sha=runtime_bind._sha256(ed), dep_manifest_sha=runtime_bind._sha256(dm),
        u6_impl_sha=runtime_bind._sha256(DOUBLE / "u6_impl_double.py"), additions=ADDITIONS,
        engine_dir=engine_dir, env_decl=ed, dep_manifest=dm)


RUNTIME_DOUBLE = runtime_double()
# A qualified environment = the double's frozen declaration ++ exactly the two additions.
QUALIFIED_ENV = {k: (str(_BIN) if v == "*" else v) for k, v in FROZEN_ENV_DOUBLE}
QUALIFIED_ENV.update(ENV_OK)
GUID = "00000000-0000-0000-0000-000000000000"  # approved placeholder (gitleaks-allowlisted); the double flags any GUID shape


def git(cwd, *a, **kw):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, check=kw.pop("check", True), **kw)


class Sandbox:
    """Temp repo + temp 'home' + patched roots. Never touches the real ones."""

    def __init__(self):
        self.td = Path(tempfile.mkdtemp(prefix="u6ctl-"))
        self.home = self.td / "home"
        self.home.mkdir(mode=0o700)
        (self.home / ".defender-sentinel-soc-lab").mkdir(mode=0o700)
        self.repo = self.td / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "ctl@localhost")
        git(self.repo, "config", "user.name", "ctl")
        (self.repo / "f").write_text("1\n")
        git(self.repo, "add", "f")
        git(self.repo, "commit", "-q", "-m", "initial")
        self.remote = self.td / "remote.git"
        git(self.td, "init", "-q", "--bare", "remote.git")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        (self.repo / ".pii-terms").write_text("secretterm\n")
        self.priv = self.home / ".defender-sentinel-soc-lab" / "msg-controls"
        self.priv.mkdir(parents=True, mode=0o700)
        self.key = bytes(range(32))
        (self.priv / "baseline.key").write_bytes(self.key)
        os.chmod(self.priv / "baseline.key", 0o600)
        self.set_baseline([])
        self._patches = [
            mock.patch.object(private_root, "resolve_root_path", lambda: self.priv),
            mock.patch.object(engine_bind, "REPO_ROOT", self.repo),
            mock.patch.object(l2_pre_push, "REPO_ROOT", self.repo),
            mock.patch.object(l3_ci_sweep, "REPO_ROOT", self.repo),
            mock.patch.object(runlog.pwd, "getpwuid", lambda uid: SimpleNamespace(pw_dir=str(self.home))),
        ]

    def set_baseline(self, entries):
        (self.repo / "committed-baseline").write_text(json.dumps(entries))
        (self.priv / "private-baseline").write_bytes(self.key + json.dumps(entries).encode())
        os.chmod(self.priv / "private-baseline", 0o600)

    def commit(self, msg: bytes) -> str:
        (self.repo / "f").write_bytes(os.urandom(4).hex().encode() + b"\n")
        git(self.repo, "add", "f")
        p = subprocess.run(["git", "commit", "-q", "-F", "-"], cwd=self.repo, input=msg, check=True)
        return git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()

    def head(self) -> str:
        return git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()

    def __enter__(self):
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()
        shutil.rmtree(self.td, ignore_errors=True)


def l2(sb: Sandbox, stream: bytes, remote="origin", url=None, env=None, runtime=RUNTIME_DOUBLE, **kw):
    env = QUALIFIED_ENV if env is None else env
    return l2_pre_push.evaluate(remote, url if url is not None else str(sb.remote), stream,
                                engine_dir=DOUBLE, identity_file=DOUBLE_IDS, environ=env,
                                committed_baseline=sb.repo / "committed-baseline", runtime=runtime, **kw)


def stream(sb: Sandbox, rref="refs/heads/main", lsha=None):
    lsha = lsha or sb.head()
    return f"refs/heads/main {lsha} {rref} {'0'*40}\n".encode()


# ---------------------------------------------------------------- result
class TestResult(unittest.TestCase):
    def test_rc_distinct_per_status(self):
        self.assertEqual({R.RC[s] for s in (R.PASS, R.REJECT, R.ERROR)}, {0, 1, 2})
        self.assertNotEqual(R.RC[R.ERROR], R.RC[R.REJECT])

    def test_roundtrip_and_refusal(self):
        r = R.Result("L1", R.REJECT, "WORDLIST_FINDING", counts={"wordlist": 2})
        self.assertEqual(R.parse(r.render()).code, "WORDLIST_FINDING")
        with self.assertRaises(ValueError):
            R.Result("L1", R.ERROR, "free text here")
        with self.assertRaises(ValueError):
            R.parse("U6_RETURN v1 KIND=L1 STATUS=ERROR CODE=OK RC=1 COUNTS=-")
        self.assertNotIn("LOG_SHA256", r.render())


# ---------------------------------------------------------------- engine binding
class TestEngineBind(unittest.TestCase):
    def test_double_rejected_by_production_manifest(self):
        eng, err = engine_bind.bind("L1", engine_bind.L1_MEMBERS, DOUBLE)  # production identity file
        self.assertIsNone(eng)
        self.assertEqual((err.status, err.code), (R.ERROR, "ENGINE_IDENTITY_MISMATCH"))

    def test_tampered_member_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "msgctl"
            shutil.copytree(DOUBLE, d)
            (d / "structural.py").write_text((d / "structural.py").read_text() + "\n# tamper\n")
            eng, err = engine_bind.bind("L1", engine_bind.L1_MEMBERS, d, DOUBLE_IDS)
            self.assertEqual(err.code, "ENGINE_IDENTITY_MISMATCH")
            self.assertEqual(err.rc, 2)

    def test_absent_dir_and_member(self):
        _, err = engine_bind.bind("L1", engine_bind.L1_MEMBERS, Path("/nonexistent"), DOUBLE_IDS)
        self.assertEqual(err.code, "ENGINE_DIR_ABSENT")
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "msgctl"
            shutil.copytree(DOUBLE, d)
            (d / "wordlist.py").unlink()
            _, err = engine_bind.bind("L1", engine_bind.L1_MEMBERS, d, DOUBLE_IDS)
            self.assertEqual(err.code, "ENGINE_MEMBER_ABSENT")

    def test_l3_member_set_excludes_private(self):
        self.assertFalse(set(engine_bind.L3_MEMBERS) & engine_bind.L3_FORBIDDEN)
        for m in ("wordlist", "baseline", "crypto", "identity"):
            self.assertIn(m, engine_bind.L3_FORBIDDEN)


# ---------------------------------------------------------------- L1
class TestL1(unittest.TestCase):
    def run_l1(self, sb, msg: bytes):
        p = sb.td / "COMMIT_EDITMSG"
        p.write_bytes(msg)
        return l1_commit_msg.evaluate(p, engine_dir=DOUBLE, identity_file=DOUBLE_IDS, runtime=RUNTIME_DOUBLE, environ=QUALIFIED_ENV)

    def test_pass_reject_error_distinct(self):
        with Sandbox() as sb:
            self.assertEqual((self.run_l1(sb, b"clean message\n").status), R.PASS)
            r = self.run_l1(sb, f"has {GUID}\n".encode())
            self.assertEqual((r.status, r.code, r.rc), (R.REJECT, "STRUCTURAL_FINDING", 1))
            r = self.run_l1(sb, b"mentions secretterm\n")
            self.assertEqual((r.status, r.code, r.rc), (R.REJECT, "WORDLIST_FINDING", 1))
            (sb.repo / ".pii-terms").unlink()
            r = self.run_l1(sb, b"anything\n")
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "WORDLIST_ABSENT", 2))

    def test_verbatim_bytes_no_cleanup(self):
        # git's cleanup would strip a '#' comment line; L1 must still see it.
        with Sandbox() as sb:
            r = self.run_l1(sb, f"subject\n# comment with {GUID}\n".encode())
            self.assertEqual(r.status, R.REJECT)

    def test_engine_absent_is_error_not_reject(self):
        with Sandbox() as sb:
            p = sb.td / "m"
            p.write_bytes(b"x\n")
            r = l1_commit_msg.evaluate(p, engine_dir=Path("/nonexistent"), identity_file=DOUBLE_IDS, runtime=RUNTIME_DOUBLE, environ=QUALIFIED_ENV)
            self.assertEqual((r.status, r.rc), (R.ERROR, 2))
            r = l1_commit_msg.evaluate(sb.td / "missing", engine_dir=DOUBLE, identity_file=DOUBLE_IDS, runtime=RUNTIME_DOUBLE, environ=QUALIFIED_ENV)
            self.assertEqual((r.status, r.code), (R.ERROR, "MSG_FILE_ABSENT"))

    def test_stdout_is_single_record(self):
        with Sandbox() as sb:
            p = sb.td / "m"
            p.write_bytes(b"ok\n")
            with mock.patch.object(l1_commit_msg, "evaluate", lambda *a, **k: R.Result("L1", R.PASS, "OK")):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = l1_commit_msg.main([str(p)])
            lines = buf.getvalue().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertTrue(R.RECORD_RE.match(lines[0]))
            self.assertEqual(rc, 0)


# ---------------------------------------------------------------- L2
class TestL2(unittest.TestCase):
    def test_empty_stream_not_run(self):
        with Sandbox() as sb:
            r = l2(sb, b"")
            self.assertEqual((r.status, r.code, r.rc), (R.NOT_RUN, "NO_REF_UPDATES", 0))

    def test_tag_and_non_head_fail_closed(self):
        with Sandbox() as sb:
            r = l2(sb, stream(sb, rref="refs/tags/v1"))
            self.assertEqual((r.status, r.code), (R.REJECT, "TAG_REF_REFUSED"))
            r = l2(sb, stream(sb, rref="refs/notes/x"))
            self.assertEqual((r.status, r.code), (R.REJECT, "NON_HEAD_REF_REFUSED"))

    def test_single_origin(self):
        with Sandbox() as sb:
            self.assertEqual(l2(sb, stream(sb), remote="upstream").code, "REMOTE_NOT_ORIGIN")
            self.assertEqual(l2(sb, stream(sb), url="https://example.invalid/x").code, "ORIGIN_URL_MISMATCH")
            git(sb.repo, "remote", "set-url", "--push", "origin", str(sb.td / "other.git"))
            self.assertEqual(l2(sb, stream(sb)).code, "ORIGIN_URL_MISMATCH")

    def test_bare_environment_is_error_never_reject(self):
        # An environment that is not the frozen one refuses at the runtime
        # contract (here the dependency objects are unreachable first).
        with Sandbox() as sb:
            r = l2(sb, stream(sb), env={"GIT_NO_REPLACE_OBJECTS": "1"})
            self.assertEqual((r.status, r.rc), (R.ERROR, 2))
            self.assertIn(r.code, ("RUNTIME_GIT_UNQUALIFIED", "RUNTIME_GITLEAKS_UNQUALIFIED", "ENV_UNQUALIFIED"))

    def test_baseline_unresolved_fails_closed(self):
        with Sandbox() as sb:
            (sb.repo / "committed-baseline").unlink()
            r = l2(sb, stream(sb))
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "BASELINE_UNRESOLVED", 2))

    def test_private_root_checks(self):
        with Sandbox() as sb:
            os.chmod(sb.priv, 0o750)
            self.assertEqual(l2(sb, stream(sb)).code, "PRIVATE_ROOT_MODE")
            os.chmod(sb.priv, 0o700)
            (sb.priv / "baseline.key").write_bytes(b"short")
            self.assertEqual(l2(sb, stream(sb)).code, "PRIVATE_MEMBER_UNREADABLE")
            (sb.priv / "baseline.key").unlink()
            self.assertEqual(l2(sb, stream(sb)).code, "PRIVATE_MEMBER_ABSENT")

    def test_c4_mismatch_is_error(self):
        with Sandbox() as sb:
            (sb.repo / "committed-baseline").write_text("[{\"commit\":\"x\",\"detector\":\"guid\"}]")
            r = l2(sb, stream(sb))
            self.assertEqual((r.status, r.code), (R.ERROR, "BASELINE_C4_FAILED"))

    def test_untouched_published_branch_violation_rejects(self):
        # P5-01 red control: a published branch this push does not touch carries a violation.
        with Sandbox() as sb:
            git(sb.repo, "push", "-q", "origin", "main")
            git(sb.repo, "checkout", "-q", "-b", "side")
            sb.commit(f"side {GUID}\n".encode())
            git(sb.repo, "push", "-q", "origin", "side")
            git(sb.repo, "checkout", "-q", "main")
            sb.commit(b"clean main update\n")
            r = l2(sb, stream(sb))  # pushes main only
            self.assertEqual((r.status, r.code), (R.REJECT, "UNION_FINDING"))
            self.assertEqual((r.counts["heads"], r.counts["structural"]), (2, 1))
            # deleting the offending branch in the same push removes it from the prospective set
            st = stream(sb) + f"(delete) {'0'*40} refs/heads/side {git(sb.repo, 'rev-parse', 'side').stdout.decode().strip()}\n".encode()
            r = l2(sb, st)
            self.assertEqual((r.status, r.counts["heads"]), (R.PASS, 1))

    def test_published_head_missing_locally_is_error(self):
        with Sandbox() as sb:
            git(sb.repo, "push", "-q", "origin", "main")
            # another clone publishes a branch this clone has never fetched
            other = sb.td / "other"
            git(sb.td, "clone", "-q", str(sb.remote), "other")
            git(other, "config", "user.email", "o@localhost"); git(other, "config", "user.name", "o")
            git(other, "checkout", "-q", "-b", "elsewhere")
            (other / "g").write_text("g\n"); git(other, "add", "g"); git(other, "commit", "-q", "-m", "elsewhere")
            git(other, "push", "-q", "origin", "elsewhere")
            sb.commit(b"local\n")
            r = l2(sb, stream(sb))
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "REMOTE_HEAD_NOT_LOCAL", 2))

    def test_runtime_contract_load_bearing(self):
        with Sandbox() as sb:
            no_impl = runtime_double(engine_dir=sb.td)   # no file with the impl identity
            r = l2(sb, stream(sb), runtime=no_impl)
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "U6_IMPL_ABSENT", 2))
            p = sb.td / "m"; p.write_bytes(b"ok\n")
            r = l1_commit_msg.evaluate(p, engine_dir=DOUBLE, identity_file=DOUBLE_IDS, runtime=no_impl, environ=QUALIFIED_ENV)
            self.assertEqual((r.status, r.code), (R.ERROR, "U6_IMPL_ABSENT"))

    def test_runtime_refuses_without_frozen_authority(self):
        # P7-01: no env declaration / no dependency manifest -> refuse, never a weaker pass.
        with Sandbox() as sb:
            spec = runtime_bind.RuntimeSpec(RUNTIME_DOUBLE.env_decl_sha, RUNTIME_DOUBLE.dep_manifest_sha,
                                            RUNTIME_DOUBLE.u6_impl_sha, ADDITIONS, DOUBLE,
                                            sb.td / "absent.decl", RUNTIME_DOUBLE.dep_manifest)
            self.assertEqual(l2(sb, stream(sb), runtime=spec).code, "ENV_AUTHORITY_ABSENT")
            bad = sb.td / "tampered.decl"; bad.write_text((_AUTH / "env.decl").read_text() + "EXTRA=1\n")
            spec = runtime_bind.RuntimeSpec("0" * 64, RUNTIME_DOUBLE.dep_manifest_sha, RUNTIME_DOUBLE.u6_impl_sha,
                                            ADDITIONS, DOUBLE, bad, RUNTIME_DOUBLE.dep_manifest)
            self.assertEqual(l2(sb, stream(sb), runtime=spec).code, "ENV_AUTHORITY_ABSENT")  # identity, not content
            spec = runtime_bind.RuntimeSpec(RUNTIME_DOUBLE.env_decl_sha, RUNTIME_DOUBLE.dep_manifest_sha,
                                            RUNTIME_DOUBLE.u6_impl_sha, ADDITIONS, DOUBLE,
                                            RUNTIME_DOUBLE.env_decl, sb.td / "absent.manifest")
            self.assertEqual(l2(sb, stream(sb), runtime=spec).code, "DEP_AUTHORITY_ABSENT")
            partial = sb.td / "partial.manifest"
            partial.write_text("\n".join((_AUTH / "dep.manifest").read_text().splitlines()[:2]) + "\n")
            spec = runtime_double(dep_manifest=partial)
            self.assertEqual(l2(sb, stream(sb), runtime=spec).code, "DEP_CLOSURE_INCOMPLETE")

    def test_env_must_extend_frozen_exactly(self):
        # P7-01 red control: the Pass-6 defect was an unauthorized extra variable passing.
        with Sandbox() as sb:
            self.assertEqual(l2(sb, stream(sb)).status, R.PASS)          # exact extension
            extra = dict(QUALIFIED_ENV); extra["UNAUTHORIZED"] = "1"
            self.assertEqual(l2(sb, stream(sb), env=extra).code, "ENV_UNQUALIFIED")
            dropped = dict(QUALIFIED_ENV); dropped.pop(FROZEN_ENV_DOUBLE[1][0])
            self.assertEqual(l2(sb, stream(sb), env=dropped).code, "ENV_UNQUALIFIED")
            missing_add = dict(QUALIFIED_ENV); missing_add.pop("GIT_NO_LAZY_FETCH")
            self.assertEqual(l2(sb, stream(sb), env=missing_add).code, "ENV_UNQUALIFIED")
            wrong_val = dict(QUALIFIED_ENV); wrong_val["GIT_NO_LAZY_FETCH"] = "0"
            self.assertEqual(l2(sb, stream(sb), env=wrong_val).code, "ENV_UNQUALIFIED")
            reordered = {k: QUALIFIED_ENV[k] for k in list(QUALIFIED_ENV)[::-1]}
            self.assertEqual(sorted(reordered), sorted(QUALIFIED_ENV))   # membership identical; only order differs
            self.assertEqual(l2(sb, stream(sb), env=reordered).code, "ENV_UNQUALIFIED")

    def test_effective_object_identities_are_checked(self):
        # A4/A5/A6: each dependency must be the EFFECTIVE qualified object.
        with Sandbox() as sb:
            def manifest_with(name, sha=None, path=None, version=None):
                m = sb.td / f"m-{name}-{abs(hash((name, str(sha), str(path), str(version))))}.manifest"
                lines = []
                for l in RUNTIME_DOUBLE.dep_manifest.read_text().splitlines():
                    n, pth, h, ver = l.split()
                    if n == name:
                        pth, h, ver = path or pth, sha or h, version or ver
                    lines.append(f"{n} {pth} {h} {ver}")
                m.write_text("\n".join(lines) + "\n")
                return runtime_double(dep_manifest=m)
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("python", sha="0" * 64)).code,
                             "RUNTIME_INTERPRETER_UNQUALIFIED")
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("git", sha="0" * 64)).code,
                             "RUNTIME_GIT_UNQUALIFIED")
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("gitleaks", sha="0" * 64)).code,
                             "RUNTIME_GITLEAKS_UNQUALIFIED")

    def test_qualified_object_identity_is_complete(self):
        # P9-01: path + bytes + probed version for git/gitleaks; SAME OBJECT for python.
        with Sandbox() as sb:
            def manifest_with(name, sha=None, path=None, version=None):
                m = sb.td / f"q-{name}-{abs(hash((name, str(sha), str(path), str(version))))}.manifest"
                lines = []
                for l in RUNTIME_DOUBLE.dep_manifest.read_text().splitlines():
                    n, pth, h, ver = l.split()
                    if n == name:
                        pth, h, ver = str(path or pth), sha or h, version or ver
                    lines.append(f"{n} {pth} {h} {ver}")
                m.write_text("\n".join(lines) + "\n")
                return runtime_double(dep_manifest=m)
            self.assertEqual(l2(sb, stream(sb)).status, R.PASS)
            # a byte-identical COPY of the interpreter at another inode must fail
            copy = sb.td / "python-copy"
            shutil.copy(os.path.realpath("/proc/self/exe"), copy)
            self.assertEqual(runtime_bind._sha256(copy), runtime_bind._sha256("/proc/self/exe"))
            r = l2(sb, stream(sb), runtime=manifest_with("python", path=copy))
            self.assertEqual((r.status, r.code), (R.ERROR, "RUNTIME_INTERPRETER_NOT_SAME_OBJECT"))
            # a git at a different qualified path is refused even with matching bytes
            other = sb.td / "git-elsewhere"
            shutil.copy(_BIN / "git", other)
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("git", path=other)).code,
                             "RUNTIME_GIT_UNQUALIFIED")
            # version token from the harmless capability probe must match
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("git", version="0.0.0")).code,
                             "RUNTIME_GIT_VERSION_MISMATCH")
            self.assertEqual(l2(sb, stream(sb), runtime=manifest_with("gitleaks", version="0.0.0")).code,
                             "RUNTIME_GITLEAKS_VERSION_MISMATCH")

    def test_authority_resolved_by_identity_not_filename(self):
        # P9-02: production asserts no filename for either authority artifact.
        with Sandbox() as sb:
            d = sb.td / "authbyid"; d.mkdir()
            shutil.copy(RUNTIME_DOUBLE.env_decl, d / "arbitrary-name-1")
            shutil.copy(RUNTIME_DOUBLE.dep_manifest, d / "arbitrary-name-2")
            shutil.copy(DOUBLE / "u6_impl_double.py", d / "arbitrary-name-3")
            spec = runtime_bind.RuntimeSpec(
                env_decl_sha=RUNTIME_DOUBLE.env_decl_sha, dep_manifest_sha=RUNTIME_DOUBLE.dep_manifest_sha,
                u6_impl_sha=RUNTIME_DOUBLE.u6_impl_sha, additions=ADDITIONS, engine_dir=d)
            self.assertEqual(l2(sb, stream(sb), runtime=spec).status, R.PASS)
            (d / "arbitrary-name-1").unlink()
            self.assertEqual(l2(sb, stream(sb), runtime=spec).code, "ENV_AUTHORITY_ABSENT")

    def test_engine_manifest_is_canonical(self):
        # P9-02: one row per member, no duplicates, no alias naming schemes.
        rows = [l.split("  ") for l in (U6 / "ENGINE-IDENTITIES.txt").read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        paths = [r[1].strip() for r in rows]
        self.assertEqual(len(paths), len(set(paths)), "duplicate member rows")
        msgctl = [p for p in paths if p.startswith("msgctl/")]
        self.assertEqual(len(msgctl), 9, msgctl)
        self.assertIn("msgctl/u6runtime.py", msgctl)
        for invented in ("bounded-env", "dependency-manifest", "u6-bounded-env", "u6-dependencies"):
            self.assertFalse(any(invented in p for p in paths), f"filename not established by authority: {invented}")

    def test_shadow_git_rejected_and_not_executed(self):
        # P7-01: an unqualified/shadow git must be rejected BEFORE any git runs.
        with Sandbox() as sb:
            shadow = sb.td / "shadowbin"; shadow.mkdir()
            (shadow / "git").write_text("#!/bin/sh\ntouch " + str(sb.td / "GIT_RAN") + "\nexit 0\n")
            os.chmod(shadow / "git", 0o755)
            env = dict(QUALIFIED_ENV); env["PATH"] = f"{shadow}:{QUALIFIED_ENV['PATH']}"
            r = l2(sb, stream(sb), env=env)
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "RUNTIME_GIT_UNQUALIFIED", 2))
            self.assertFalse((sb.td / "GIT_RAN").exists())

    def test_no_git_process_before_qualification(self):
        # P7-01: with an unqualified environment, zero git processes must start.
        with Sandbox() as sb:
            ran = sb.td / "GIT_INVOKED"
            calls = []
            real_git = l2_pre_push._git

            def spy(*a):
                calls.append(a)
                ran.write_text("x")
                return real_git(*a)

            with mock.patch.object(l2_pre_push, "_git", spy):
                bad = dict(QUALIFIED_ENV); bad["UNAUTHORIZED"] = "1"
                r = l2(sb, stream(sb), env=bad)
            self.assertEqual(r.code, "ENV_UNQUALIFIED")
            self.assertEqual(calls, [], f"git invoked before qualification: {calls}")
            self.assertFalse(ran.exists())

    def test_production_spec_binds_frozen(self):
        spec = runtime_bind.production_spec()
        self.assertEqual(spec.u6_impl_sha, "35ee40c3b9d794881f45adbbec20e7e5832c0ec9c533de02f107e15fe494a21a")
        self.assertEqual(spec.env_decl_sha, "009a5ec831dc2dd85865ce96d9deb8aef739777f3d233680d3b960b079538e33")
        self.assertEqual(spec.dep_manifest_sha, "46e6c9e79325bb29cc227214fc37b3bfd846d15aa98417038fccf60b4c795eb5")
        self.assertEqual(spec.additions, ADDITIONS)
        self.assertEqual(spec.engine_dir, REPO / "msgctl")
        # and the shipped repository has no such authority: production refuses
        log = []
        self.assertEqual(runtime_bind.bind_runtime("L2", os.environ, log.append).code, "ENV_AUTHORITY_ABSENT")

    def test_union_pass_reject_exempt(self):
        with Sandbox() as sb:
            self.assertEqual(l2(sb, stream(sb)).status, R.PASS)
            bad = sb.commit(f"oops {GUID}\n".encode())
            sb.commit(b"later clean\n")
            r = l2(sb, stream(sb))  # union = all reachable, not the diff
            self.assertEqual((r.status, r.code), (R.REJECT, "UNION_FINDING"))
            self.assertEqual(r.counts["structural"], 1)
            sb.set_baseline([{"commit": bad, "detector": "guid"}])
            r = l2(sb, stream(sb))
            self.assertEqual((r.status, r.counts["exempt"]), (R.PASS, 1))
            # deleting the only published head leaves an empty prospective set
            git(sb.repo, "push", "-q", "origin", "main")
            r = l2(sb, f"(delete) {'0'*40} refs/heads/main {sb.head()}\n".encode())
            self.assertEqual((r.status, r.counts["commits"]), (R.PASS, 0))

    def test_malformed_stream(self):
        with Sandbox() as sb:
            self.assertEqual(l2(sb, b"a b c\n").code, "REF_STREAM_MALFORMED")
            self.assertEqual(l2(sb, b"refs/heads/main zz refs/heads/main " + b"0" * 40 + b"\n").code, "REF_STREAM_MALFORMED")


# ---------------------------------------------------------------- L3
class TestL3(unittest.TestCase):
    def test_structural_only_and_isolation(self):
        with Sandbox() as sb:
            sb.commit(b"mentions secretterm\n")  # wordlist hit must be INVISIBLE to L3
            bad = sb.commit(f"guid {GUID}\n".encode())
            git(sb.repo, "push", "-q", "origin", "main")
            # a second published branch whose finding is NOT reachable from HEAD/main
            git(sb.repo, "checkout", "-q", "-b", "side", "HEAD~2")
            sb.commit(f"side {GUID}\n".encode())
            git(sb.repo, "push", "-q", "origin", "side")
            git(sb.repo, "checkout", "-q", "main")
            sb.commit(b"unpublished local commit\n")  # not pushed: not part of the published union
            r = l3_ci_sweep.evaluate(engine_dir=DOUBLE, identity_file=DOUBLE_IDS)
            self.assertEqual((r.status, r.code, r.rc), (R.PASS, "L3_ADVISORY_FINDINGS", 0))
            self.assertEqual((r.counts["heads"], r.counts["structural"]), (2, 2))  # both heads; unpublished commit excluded
            self.assertEqual(r.counts["commits"], 4)  # initial, secretterm, guid, side
            self.assertEqual(engine_bind.sys_modules_reach(engine_bind.L3_FORBIDDEN, "L3"), [])

    def test_tag_on_origin_fails_closed(self):
        with Sandbox() as sb:
            git(sb.repo, "push", "-q", "origin", "main")
            git(sb.repo, "tag", "v1")
            git(sb.repo, "push", "-q", "origin", "v1")
            r = l3_ci_sweep.evaluate(engine_dir=DOUBLE, identity_file=DOUBLE_IDS)
            self.assertEqual((r.status, r.code, r.rc), (R.ERROR, "TAG_REF_REFUSED", 2))

    def test_no_published_heads_is_error(self):
        with Sandbox() as sb:  # nothing pushed: zero examined messages must not read clean
            r = l3_ci_sweep.evaluate(engine_dir=DOUBLE, identity_file=DOUBLE_IDS)
            self.assertEqual((r.status, r.rc), (R.ERROR, 2))

    def test_fresh_process_loads_no_private_member(self):
        # A fresh interpreter running only L3 must end with zero private engine members loaded.
        code = (
            "import sys; sys.path.insert(0, %r)\n"
            "from pathlib import Path\nfrom u6 import l3_ci_sweep, engine_bind\n"
            "l3_ci_sweep.published_refs = lambda: ([], 0)\n"
            "l3_ci_sweep.evaluate(engine_dir=Path(%r), identity_file=Path(%r))\n"
            "print(sorted(n for n in sys.modules if n.startswith('_u6_engine_')))\n"
            "print(engine_bind.sys_modules_reach(engine_bind.L3_FORBIDDEN))\n"
        ) % (str(REPO), str(DOUBLE), str(DOUBLE_IDS))
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, cwd=REPO)
        out = p.stdout.decode().splitlines()
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        loaded, reach = out[-2], out[-1]
        self.assertEqual(reach, "[]")
        for m in ("wordlist", "baseline", "crypto", "identity"):
            self.assertNotIn(f"'_u6_engine_l3.{m}'", loaded)

    def test_zero_corpus_is_error(self):
        with Sandbox() as sb:
            git(sb.repo, "push", "-q", "origin", "main")
            with mock.patch.object(l3_ci_sweep, "corpus", lambda heads: []):
                r = l3_ci_sweep.evaluate(engine_dir=DOUBLE, identity_file=DOUBLE_IDS)
            self.assertEqual((r.status, r.rc), (R.ERROR, 2))

    def test_static_isolation(self):
        p = subprocess.run([sys.executable, str(HERE / "check_l3_isolation.py")], capture_output=True, cwd=REPO)
        self.assertEqual(p.returncode, 0, p.stdout.decode() + p.stderr.decode())


# ---------------------------------------------------------------- return channel
class TestReturnChannel(unittest.TestCase):
    def child(self, sb, body: str) -> tuple[Path, str]:
        p = sb.td / "child.py"
        p.write_text("import sys, os\nstatus=os.environ['U6_STATUS_FILE']\n" + body)
        return p, return_channel._sha256(p)

    def run_rc(self, sb, child, sha, args=(), categorical=False, kind="ADJUDICATION"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = return_channel.emit(return_channel.run(kind, sha, child, list(args), env=dict(QUALIFIED_ENV),
                                                        categorical=categorical, runtime=RUNTIME_DOUBLE))
        lines = buf.getvalue().splitlines()
        self.assertEqual(len(lines), 1, lines)
        return rc, R.parse(lines[0]), sb

    def test_child_text_never_reaches_stdout(self):
        with Sandbox() as sb:
            c, sha = self.child(sb, "print('PRIVATE-MARKER-9f3a')\nsys.stderr.write('also private\\n')\nsys.exit(3)\n")
            rc, r, _ = self.run_rc(sb, c, sha)
            self.assertEqual((rc, r.status, r.code), (3, R.STOP, "STOP_RC_3"))
            logs = list((sb.home / ".defender-sentinel-soc-lab" / "runs").glob("*.log"))
            self.assertTrue(any(b"PRIVATE-MARKER-9f3a" in l.read_bytes() for l in logs))
            newest = max(logs, key=lambda l: l.stat().st_mtime)
            self.assertEqual(oct(newest.stat().st_mode & 0o777), "0o600")
            side = Path(str(newest) + ".sha256").read_text().strip()
            self.assertEqual(side, __import__("hashlib").sha256(newest.read_bytes()).hexdigest())
            self.assertNotIn(side, r.render())  # private digest never on the transportable line

    def test_status_file_grammar(self):
        with Sandbox() as sb:
            c, sha = self.child(sb, "open(status,'w').write('CODE=PHASE2_READY\\n')\n")
            self.assertEqual(self.run_rc(sb, c, sha)[1].code, "PHASE2_READY")
            c, sha = self.child(sb, "open(status,'w').write('CODE=PHASE2_NOT_READY\\n')\n")
            self.assertEqual(self.run_rc(sb, c, sha)[1].status, R.STOP)
            c, sha = self.child(sb, "open(status,'w').write('the root is /home/x/private\\n')\n")
            self.assertEqual(self.run_rc(sb, c, sha)[1].code, "STATUS_FILE_MALFORMED")
            c, sha = self.child(sb, "open(status,'w').write('CODE=NOT_A_CODE\\n')\n")
            self.assertEqual(self.run_rc(sb, c, sha)[1].code, "STATUS_FILE_UNEXPECTED")
            c, sha = self.child(sb, "open(status,'w').write('CODE=STOP_RC_3\\n')\n")  # rc0 + STOP token: inconsistent
            self.assertEqual(self.run_rc(sb, c, sha)[1].code, "STATUS_FILE_UNEXPECTED")

    def test_categorical_mode_preserves_frozen_instrument_state(self):
        # P5-02: rc0 READY and rc0 non-ready must be mechanically distinct; the instrument is untouched.
        with Sandbox() as sb:
            c, sha = self.child(sb, "print('preamble noise')\nprint('PHASE2_STATE=READY RUNDIR_STATE=AVAILABLE')\n")
            rc1, r1, _ = self.run_rc(sb, c, sha, categorical=True, kind="PHASE2_DIAG")
            c, sha = self.child(sb, "print('PHASE2_STATE=KEY_UNOPENABLE RUNDIR_STATE=AVAILABLE')\n")
            rc2, r2, _ = self.run_rc(sb, c, sha, categorical=True, kind="PHASE2_DIAG")
            self.assertEqual((rc1, rc2), (0, 0))
            self.assertEqual((r1.code, r2.code), ("PHASE2_CATEGORICAL", "PHASE2_CATEGORICAL"))
            self.assertNotEqual(r1.render(), r2.render())
            self.assertIn("PHASE2_STATE=READY", r1.state); self.assertIn("PHASE2_STATE=KEY_UNOPENABLE", r2.state)
            # a non-grammar last line (a path, lowercase, free text) is never relayed
            c, sha = self.child(sb, "print('PHASE2_STATE=READY ROOT=/home/x/.defender-sentinel-soc-lab')\n")
            _, r3, _ = self.run_rc(sb, c, sha, categorical=True, kind="PHASE2_DIAG")
            self.assertEqual((r3.status, r3.code), (R.ERROR, "CATEGORICAL_MALFORMED"))
            self.assertIsNone(r3.state)
            # without categorical mode the same rc0 child is the generic PASS/OK (adjudication semantics)
            _, r4, _ = self.run_rc(sb, c, sha, categorical=False)
            self.assertEqual(r4.code, "OK")

    def test_identity_bound_before_exec(self):
        with Sandbox() as sb:
            marker = sb.td / "ran"
            c, sha = self.child(sb, f"open({str(marker)!r},'w').write('x')\n")
            rc, r, _ = self.run_rc(sb, c, "0" * 64)
            self.assertEqual((rc, r.code), (2, "CHILD_IDENTITY_MISMATCH"))
            self.assertFalse(marker.exists())
            rc, r, _ = self.run_rc(sb, sb.td / "missing.py", sha)
            self.assertEqual(r.code, "CHILD_ABSENT")


# ---------------------------------------------------------------- private run-log sink
class TestRunLog(unittest.TestCase):
    def test_symlinked_runs_dir_is_never_followed(self):
        with Sandbox() as sb:
            target = sb.td / "elsewhere"; target.mkdir(mode=0o700)
            (sb.home / ".defender-sentinel-soc-lab" / "runs").symlink_to(target)
            log = runlog.RunLog("L1"); log("SECRET-LINE"); log.close()
            self.assertFalse(log.on_disk)
            self.assertEqual(list(target.iterdir()), [])  # nothing written through the link
            self.assertIn(b"SECRET-LINE", bytes(log.buf))  # memory fallback still records

    def test_unsafe_parent_falls_back_to_memory(self):
        with Sandbox() as sb:
            parent = sb.home / ".defender-sentinel-soc-lab"
            os.chmod(parent, 0o750)
            log = runlog.RunLog("L1"); log.close()
            self.assertFalse(log.on_disk)
            os.chmod(parent, 0o700)
            shutil.rmtree(parent)
            log = runlog.RunLog("L1"); log.close()
            self.assertFalse(log.on_disk)          # the parent is never created by a consumer
            self.assertFalse(parent.exists())

    def test_safe_path_writes_0600_and_private_sidecar(self):
        with Sandbox() as sb:
            log = runlog.RunLog("L1"); log("x"); log.close()
            self.assertTrue(log.on_disk)
            runs = sb.home / ".defender-sentinel-soc-lab" / "runs"
            self.assertEqual(oct(runs.stat().st_mode & 0o777), "0o700")
            f = runs / log.name
            self.assertEqual(oct(f.stat().st_mode & 0o777), "0o600")
            self.assertEqual(Path(str(f) + ".sha256").read_text().strip(), __import__("hashlib").sha256(f.read_bytes()).hexdigest())

    def test_return_channel_refuses_child_without_safe_sink(self):
        with Sandbox() as sb:
            (sb.home / ".defender-sentinel-soc-lab" / "runs").symlink_to(sb.td)
            marker = sb.td / "ran"
            c = sb.td / "c.py"; c.write_text(f"open({str(marker)!r},'w').write('x')\n")
            r = return_channel.run("ADJUDICATION", return_channel._sha256(c), c, [], env=QUALIFIED_ENV, runtime=RUNTIME_DOUBLE)
            self.assertEqual((r.status, r.code), (R.ERROR, "PRIVATE_SINK_UNAVAILABLE"))
            self.assertFalse(marker.exists())


# ---------------------------------------------------------------- orchestration integration
class TestOrchestration(unittest.TestCase):
    ORCH = REPO / "u6" / "orchestrate"

    def test_phase2_invocation_carries_rundir(self):
        # P7-03 control on the EXACT invocation shape: the frozen instrument
        # requires <rundir> and returns INSTRUMENT_INVOCATION_ERROR rc3 without it.
        with Sandbox() as sb:
            stub = sb.td / "diag.py"
            stub.write_text(
                "import sys\n"
                "if len(sys.argv) < 2:\n"
                "    print('INSTRUMENT_INVOCATION_ERROR'); sys.exit(3)\n"
                "rd = sys.argv[1]\n"
                "print('PHASE2_STATE=READY RUNDIR_STATE=AVAILABLE' if rd.endswith('good')\n"
                "      else 'PHASE2_STATE=KEY_UNOPENABLE RUNDIR_STATE=AVAILABLE')\n")
            sha = return_channel._sha256(stub)
            def run(args):
                return return_channel.run("PHASE2_DIAG", sha, stub, args, env=dict(QUALIFIED_ENV),
                                          categorical=True, runtime=RUNTIME_DOUBLE)
            missing = run([])
            self.assertEqual((missing.status, missing.code, missing.rc), (R.STOP, "STOP_RC_3", 3))
            ready = run([str(sb.td / "good")])
            self.assertEqual((ready.status, ready.code), (R.PASS, "PHASE2_CATEGORICAL"))
            self.assertIn("PHASE2_STATE=READY", ready.state)
            notready = run([str(sb.td / "other")])
            self.assertIn("PHASE2_STATE=KEY_UNOPENABLE", notready.state)
            self.assertNotEqual(ready.render(), notready.render())
            # and the wrapper itself refuses to invoke without the argument
            src = (self.ORCH / "45-phase2-diag.sh").read_text()
            self.assertIn("RUNDIR_ARGUMENT_MISSING", src)
            self.assertIn('"$diag" "$rundir"', src)

    def test_staging_is_outside_the_publication_tree(self):
        # P9-03: a successful placement must not leave anything inside the repo
        # that `git add -A` would publish.
        src = self._code(self.ORCH / "25-place-engine.sh")
        self.assertIn('mktemp -d "$base/msgctl-staging-XXXXXX"', src)
        self.assertNotIn('mktemp -d "$PWD', src)
        self.assertIn('STAGING_INSIDE_REPOSITORY', src)   # post-mktemp containment proof
        # executable proof: run the script against a fake repo with a source
        # package that satisfies every msgctl row, then confirm the tree is clean.
        td = Path(tempfile.mkdtemp(prefix="u6place-"))
        try:
            repo = td / "defender-sentinel-soc-lab"; repo.mkdir()
            git(repo, "init", "-q", "-b", "main")
            git(repo, "config", "user.email", "p@localhost"); git(repo, "config", "user.name", "p")
            git(repo, "remote", "add", "origin", str(td / "r.git"))
            (repo / "u6").mkdir()
            src_dir = td / "frozen"; src_dir.mkdir()
            rows = []
            for i in range(3):
                f = src_dir / f"member{i}.py"
                f.write_text(f"# labelled frozen stand-in {i}\n")
                rows.append(f"{runtime_bind._sha256(f)}  msgctl/member{i}.py")
            (repo / "u6" / "ENGINE-IDENTITIES.txt").write_text("\n".join(rows) + "\n")
            (repo / "seed").write_text("x\n"); git(repo, "add", "-A"); git(repo, "commit", "-q", "-m", "seed")
            p = subprocess.run(["bash", str(self.ORCH / "25-place-engine.sh"), str(src_dir)],
                               capture_output=True, env=dict(os.environ, HOME=str(td)))
            out = p.stdout.decode()
            self.assertIn("PLACE_ENGINE result=OK", out, out + p.stderr.decode())
            self.assertEqual(sorted(x.name for x in (repo / "msgctl").iterdir()),
                             ["member0.py", "member1.py", "member2.py"])
            # nothing staged into the publication set except the placed members
            staged = git(repo, "status", "--porcelain").stdout.decode().split()
            self.assertFalse([x for x in staged if "staging" in x], staged)
            self.assertFalse(list(repo.glob(".msgctl-staging-*")))
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_staging_refuses_a_repo_pointing_tmpdir(self):
        # P10-01 red control: TMPDIR is ambient input. Pointing it INTO the
        # repository must not produce staging inside the publication tree.
        td = Path(tempfile.mkdtemp(prefix="u6tmpdir-"))
        try:
            repo = td / "defender-sentinel-soc-lab"; repo.mkdir()
            git(repo, "init", "-q", "-b", "main")
            git(repo, "config", "user.email", "t@localhost"); git(repo, "config", "user.name", "t")
            git(repo, "remote", "add", "origin", str(td / "r.git"))
            (repo / "u6").mkdir()
            src = td / "frozen"; src.mkdir()
            rows = []
            for i in range(2):
                f = src / f"member{i}.py"; f.write_text(f"# stand-in {i}\n")
                rows.append(f"{runtime_bind._sha256(f)}  msgctl/member{i}.py")
            (repo / "u6" / "ENGINE-IDENTITIES.txt").write_text("\n".join(rows) + "\n")
            (repo / "seed").write_text("x\n"); git(repo, "add", "-A"); git(repo, "commit", "-q", "-m", "seed")
            env = dict(os.environ, HOME=str(td), TMPDIR=str(repo))
            p = subprocess.run(["bash", str(self.ORCH / "25-place-engine.sh"), str(src)],
                               capture_output=True, env=env)
            out = p.stdout.decode() + p.stderr.decode()
            self.assertIn("tmpdir_rejected=inside_repository", out, out)
            self.assertFalse(list(repo.glob("msgctl-staging-*")), out)
            self.assertFalse(list(repo.glob(".msgctl-staging-*")), out)
            untracked = git(repo, "status", "--porcelain").stdout.decode()
            self.assertNotIn("staging", untracked, untracked)
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_orchestration_executes_no_git_before_qualification(self):
        # P10-02 red control: no orchestration script may invoke git in its
        # executable body ahead of the Unit-6 runtime contract.
        offenders = {}
        for f in sorted(self.ORCH.glob("*.sh")):
            code = self._code(f)
            head = code.split("remote_guard")[0]
            # Scripts that legitimately drive git AFTER qualification (or whose
            # git use is the measurement itself) are named here; every other
            # script must contain no git invocation at all.
            # 10-live-head-compat.sh is no longer exempt: it qualifies git by
            # identity first and then calls it only through "$GIT".
            post_qualification = {"60-l2-verify.sh", "70-push.sh", "N-prebaseline-push.sh",
                                  "40-commit.sh", "55-commit-baseline.sh", "A-activate-hooks.sh"}
            for pattern in ("git remote", "git rev-parse", "$(git ", "`git ", "git config", "git status"):
                if pattern in code and f.name not in post_qualification:
                    offenders.setdefault(f.name, []).append(pattern)
        self.assertEqual(offenders, {}, f"git executed before qualification: {offenders}")
        # and the guard itself must not shell out to git
        guard = self._code(self.ORCH / "25-place-engine.sh")
        self.assertIn("remote_guard", guard)
        self.assertNotIn("git remote -v", guard)
        for f in sorted(self.ORCH.glob("*.sh")):
            self.assertNotIn("git remote -v", self._code(f), f.name)

    def test_step10_refuses_shadow_git_without_executing_it(self):
        # Reviewer remediation-2 item 1: step 10 runs before qualification and
        # must not execute a PATH-resolved (shadow) git.
        td = Path(tempfile.mkdtemp(prefix="u6shadow-"))
        try:
            repo = td / "defender-sentinel-soc-lab"; repo.mkdir()
            (repo / ".git").mkdir()
            (repo / ".git" / "config").write_text('[remote "origin"]\n\turl = https://example.invalid/x.git\n')
            shadow = td / "shadowbin"; shadow.mkdir()
            marker = td / "SHADOW_GIT_RAN"
            (shadow / "git").write_text(f"#!/bin/sh\ntouch {marker}\nexit 0\n")
            os.chmod(shadow / "git", 0o755)
            env = dict(os.environ, HOME=str(td), PATH=f"{shadow}:{os.environ['PATH']}")
            p = subprocess.run(["bash", str(self.ORCH / "10-live-head-compat.sh")], capture_output=True, env=env)
            out = p.stdout.decode() + p.stderr.decode()
            self.assertFalse(marker.exists(), f"shadow git executed: {out}")
            self.assertIn("GIT_UNQUALIFIED", out, out)          # this sandbox's git is not the qualified object
            self.assertIn("REFUSED_UNQUALIFIED_GIT", out, out)
            self.assertNotIn("COMPAT_BEGIN", out, out)          # refused before any measurement
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_no_orchestration_output_carries_a_remote_url(self):
        # Reviewer remediation-2 item 2: pasteable surfaces must not emit the URL.
        for f in sorted(self.ORCH.glob("*.sh")):
            code = self._code(f)
            self.assertNotIn("url=$url", code, f.name)
            self.assertNotIn("git remote -v", code, f.name)
            if "remote_guard()" in code:
                self.assertIn("REMOTE configured=YES source=.git/config", code, f.name)

    def test_placement_is_non_destructive(self):
        # P7-04: no deletion anywhere in the placement script's executable body.
        src = self._code(self.ORCH / "25-place-engine.sh")
        for forbidden in ("rm -rf", "rm -f", "rmdir ", "rm \""):
            self.assertNotIn(forbidden, src)
        self.assertIn("staging_retained", src)

    @staticmethod
    def _code(p: Path) -> str:
        return "\n".join(l for l in p.read_text().splitlines() if not l.lstrip().startswith("#"))

    def test_pre_overlay_scripts_run_against_a_base_without_u6(self):
        # P7-02, executably: the steps that precede the overlay must complete
        # against a repository that has no u6/ tree and no msgctl/.
        td = Path(tempfile.mkdtemp(prefix="u6base-"))
        try:
            base = td / "defender-sentinel-soc-lab"; base.mkdir()
            git(base, "init", "-q", "-b", "main")
            git(base, "config", "user.email", "b@localhost"); git(base, "config", "user.name", "b")
            (base / "README.md").write_text("base\n")
            git(base, "add", "README.md"); git(base, "commit", "-q", "-m", "base")
            git(base, "remote", "add", "origin", str(td / "r.git"))
            self.assertFalse((base / "u6").exists())
            env = dict(os.environ, HOME=str(td))
            for name, marker in (("00-preflight.sh", b"PREFLIGHT_END"), ("10-live-head-compat.sh", b"COMPAT_END")):
                p = subprocess.run(["bash", str(self.ORCH / name)], capture_output=True, env=env)
                out = p.stdout + p.stderr
                self.assertIn(marker, out, f"{name}: {out!r}")
                for bad in (b"No such file", b"command not found", b"unbound variable"):
                    self.assertNotIn(bad, out, f"{name} broke on the governed base: {out!r}")
        finally:
            shutil.rmtree(td, ignore_errors=True)

    def test_order_is_executable_from_governed_base(self):
        # P7-02: no executable line before 20 may reference u6/; nothing before
        # 25 may require msgctl/. Comments are prose, not behaviour.
        scripts = sorted(p for p in self.ORCH.glob("*.sh"))
        for p in scripts:
            n = p.name.split("-")[0]
            if not n.isdigit():
                continue
            code = self._code(p)
            if int(n) < 20:
                self.assertNotIn("-m u6.", code, f"{p.name} imports u6 before it is installed")
                for line in code.splitlines():
                    if "u6/" in line:
                        self.assertTrue("${1:-" in line or "-f " in line or "-d " in line,
                                        f"{p.name} uses u6/ unguarded before it is installed: {line}")
            if int(n) < 25:
                self.assertNotIn("msgctl", code, f"{p.name} needs msgctl/ before it is placed")
        names = [p.name for p in scripts]
        self.assertLess(names.index("25-place-engine.sh"), names.index("30-u6-runtime-qualify.sh"))
        self.assertLess(names.index("55-commit-baseline.sh"), names.index("70-push.sh"))
        self.assertLess(names.index("45-phase2-diag.sh"), names.index("55-commit-baseline.sh"))

    def test_u6runtime_is_a_placed_member(self):
        # P7-02 second circularity: A7's file must be one of the placed members.
        manifest = (REPO / "u6" / "ENGINE-IDENTITIES.txt").read_text()
        self.assertIn("35ee40c3b9d794881f45adbbec20e7e5832c0ec9c533de02f107e15fe494a21a  msgctl/u6runtime.py", manifest)

    def test_authority_digests_are_bound_without_filenames(self):
        # P9-02: the two frozen authority digests are bound in RUNTIME-IDENTITIES.txt
        # (identity-addressed) and asserted with NO filename anywhere.
        rt = (REPO / "u6" / "RUNTIME-IDENTITIES.txt").read_text()
        for sha in ("009a5ec831dc2dd85865ce96d9deb8aef739777f3d233680d3b960b079538e33",
                    "46e6c9e79325bb29cc227214fc37b3bfd846d15aa98417038fccf60b4c795eb5"):
            self.assertIn(sha, rt)
        spec = runtime_bind.production_spec()
        self.assertIsNone(spec.env_decl)
        self.assertIsNone(spec.dep_manifest)

    def test_hooks_start_no_git_before_qualification(self):
        for name in ("commit-msg", "pre-push"):
            code = self._code(REPO / ".githooks" / name)
            self.assertNotIn("git rev-parse", code)
            self.assertNotIn("$(git ", code)
            self.assertIn("dirname", code)      # root derived from the hook's own location


# ---------------------------------------------------------------- current-state checker
class TestCurrentState(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp(prefix="u6cs-"))
        (self.td / "scripts").mkdir()
        shutil.copy(REPO / "scripts" / "check-current-state.py", self.td / "scripts")
        shutil.copytree(HERE / "fixtures" / "current-state", self.td / "docs" / "current-state")
        self.cs = self.td / "docs" / "current-state"

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def run_check(self):
        return subprocess.run([sys.executable, str(self.td / "scripts" / "check-current-state.py")], capture_output=True).returncode

    def test_positive_valid_current_state(self):
        self.assertEqual(self.run_check(), 0)

    def test_shipped_tree_is_unbound_and_fails_closed(self):
        # As shipped, the repository's own pointer is UNBOUND: the gate must fail, not pick rev1.
        p = subprocess.run([sys.executable, str(REPO / "scripts" / "check-current-state.py")], capture_output=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn(b"AUTHORITY_UNBOUND", p.stdout)

    def test_negative_required_relationship_removed(self):
        (self.cs / "CURRENT.txt").unlink()
        self.assertEqual(self.run_check(), 1)

    def test_negative_authority_binding_removed(self):
        p = self.cs / "revisions" / "2026-08-25-rev1.json"
        d = json.loads(p.read_text()); del d["reviewer_authority"]; p.write_text(json.dumps(d))
        self.assertEqual(self.run_check(), 1)

    def test_negative_superseded_state_in_current_position(self):
        (self.cs / "CURRENT.txt").write_text("revisions/2026-08-22-rev0.json\n")
        self.assertEqual(self.run_check(), 1)

    def test_negative_orphan_superseded_revision(self):
        # a SUPERSEDED revision the current revision does not acknowledge (unreachable) must fail
        d = {"id": "2026-08-20-orphan", "status": "SUPERSEDED", "supersedes": [], "superseded_by": "2026-08-25-rev1",
             "reviewer_authority": {"file": "x.md", "sha256": "0" * 64}}
        (self.cs / "revisions" / "2026-08-20-orphan.json").write_text(json.dumps(d))
        self.assertEqual(self.run_check(), 1)

    def test_negative_superseded_state_with_forged_status(self):
        # forge: old revision relabelled CURRENT, new one relabelled SUPERSEDED, pointer moved back.
        for name, st in (("2026-08-22-rev0", "CURRENT"), ("2026-08-25-rev1", "SUPERSEDED")):
            p = self.cs / "revisions" / f"{name}.json"
            d = json.loads(p.read_text()); d["status"] = st; d.setdefault("superseded_by", "2026-08-22-rev0"); p.write_text(json.dumps(d))
        (self.cs / "CURRENT.txt").write_text("revisions/2026-08-22-rev0.json\n")
        self.assertEqual(self.run_check(), 1)  # P4: rev1 still supersedes rev0


if __name__ == "__main__":
    unittest.main()
