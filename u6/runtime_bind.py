"""Frozen Unit-6 runtime qualification - load-bearing, fail-closed.

The frozen contract is NOT "the two additions are present". It is:

    the complete frozen Gate-A BOUNDED_ENV declaration, plus exactly the two
    ruled additions, with nothing dropped, reordered, altered or added,

asserted before anything else runs, over a dependency set closed on
{python, git, gitleaks}, with EFFECTIVE identities derived from the objects
actually resolved rather than substituted from expected literals.

Authority artifacts (bytes absent from every delivered bundle; NEVER
reconstructed from prose - Reviewer Pass-7 P7-01/P5-08):

    msgctl/bounded-env.txt          009a5ec8...   frozen BOUNDED_ENV declaration
    msgctl/dependency-manifest.txt  46e6c9e7...   closed dependency manifest
    msgctl/u6runtime.py             35ee40c3...   frozen U6 implementation

While any is absent or fails its identity, qualification returns ERROR and no
governed operation runs: no git process, no private-state access, no detector
call. That is the state of the shipped candidate - activation is refused, not
approximated. Composition of the EFFECTIVE U6 runtime ID belongs to the frozen
implementation itself (u6/orchestrate/30-u6-runtime-qualify.sh); this module
does not reimplement it.

Order:

    A1  environment declaration present at its frozen identity
    A2  dependency manifest present at its frozen identity, grammar valid,
        closed over exactly {python, git, gitleaks}
    A3  assert_extends_frozen: effective environment == declaration (in
        declared order) ++ additions (in order), values exact
    A4  effective interpreter: /proc/self/exe is the SAME OBJECT as the
        qualified path - (st_dev, st_ino) equality - and only then is it
        hashed. A byte-identical copy at another inode fails by design.
    A5  effective git:      resolved path == the qualified path, realpath'd,
                            SHA-256 match, then a harmless capability probe
                            whose version token must match the manifest
    A6  effective gitleaks: same three properties
    A7  frozen U6 implementation present under engine_dir at its identity

Nothing is executed until its path AND digest have matched, so an unqualified
or shadowed object is rejected without ever running. The capability probe
(``git --version``, ``gitleaks version``) touches no repository, network or
state. A declaration value of ``*`` means host-specific-but-required (the
variable must be present, any value).

Grammars
    declaration:  NAME=VALUE            one per line, order significant
    manifest:     <name> <path> <sha256>   exactly python, git, gitleaks
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import result as R

IDENTITY_FILE = Path(__file__).resolve().parent / "RUNTIME-IDENTITIES.txt"
REPO_ROOT = Path(__file__).resolve().parent.parent
ADDITIONS = (("GIT_NO_REPLACE_OBJECTS", "1"), ("GIT_NO_LAZY_FETCH", "1"))
DEP_NAMES = ("python", "git", "gitleaks")
DEP_CODES = {"python": "RUNTIME_INTERPRETER_UNQUALIFIED",
             "git": "RUNTIME_GIT_UNQUALIFIED",
             "gitleaks": "RUNTIME_GITLEAKS_UNQUALIFIED"}
VERSION_CODES = {"git": "RUNTIME_GIT_VERSION_MISMATCH",
                 "gitleaks": "RUNTIME_GITLEAKS_VERSION_MISMATCH"}
# Harmless capability probe per tool (no repository, network or state access).
PROBE = {"git": ("--version",), "gitleaks": ("version",)}


@dataclass(frozen=True)
class RuntimeSpec:
    env_decl_sha: str
    dep_manifest_sha: str
    u6_impl_sha: str
    additions: tuple
    engine_dir: Path
    # Optional explicit authority paths. Production leaves these None and
    # resolves both artifacts identity-addressed under engine_dir; the Builder
    # battery passes labelled doubles here.
    env_decl: Path | None = None
    dep_manifest: Path | None = None


def _sha256(p) -> str | None:
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 16), b""):
                h.update(c)
        return h.hexdigest()
    except OSError:
        return None


def _parse_env_decl(path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, sep, value = line.partition("=")
        if not sep or not name:
            raise ValueError("declaration grammar")
        out.append((name, value))
    return out


def _parse_dep_manifest(path) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 4 or len(parts[2]) != 64:
            raise ValueError("manifest grammar")
        out[parts[0]] = (parts[1], parts[2], parts[3])   # path, sha256, version token
    return out


def production_spec() -> RuntimeSpec:
    vals: dict[str, tuple[str, str]] = {}
    impl = None
    for line in IDENTITY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] in ("env_declaration", "dependency_manifest") and len(parts) == 2:
            vals[parts[0]] = parts[1]
        elif parts[0] == "u6_impl":
            impl = parts[-1]
    if "env_declaration" not in vals or "dependency_manifest" not in vals or impl is None:
        raise RuntimeError("RUNTIME-IDENTITIES.txt incomplete")
    engine_dir = REPO_ROOT / "msgctl"
    return RuntimeSpec(
        env_decl_sha=vals["env_declaration"],
        dep_manifest_sha=vals["dependency_manifest"],
        u6_impl_sha=impl,
        additions=ADDITIONS,
        engine_dir=engine_dir,
        env_decl=None,          # identity-addressed under engine_dir
        dep_manifest=None,
    )


def assert_extends_frozen(frozen: list[tuple[str, str]], additions: tuple, environ) -> bool:
    """True only when the effective environment is exactly the frozen
    declaration in its declared order followed by exactly the additions."""
    eff = list(environ.items())
    expected = [n for n, _ in frozen] + [n for n, _ in additions]
    if [n for n, _ in eff] != expected:
        return False                      # dropped, extra, or reordered
    for (name, want), (_, got) in zip(list(frozen) + list(additions), eff):
        if want != "*" and got != want:
            return False                  # altered value
    return True


def find_by_identity(engine_dir, sha: str):
    d = Path(engine_dir)
    if not d.is_dir():
        return None
    for p in sorted(d.iterdir()):
        if p.is_file() and _sha256(p) == sha:
            return p
    return None


def bind_runtime(kind: str, environ, log, spec: RuntimeSpec | None = None):
    """None when fully qualified, else Result[ERROR]. Invokes no dependency."""
    spec = spec or production_spec()
    env_decl = spec.env_decl or find_by_identity(spec.engine_dir, spec.env_decl_sha)
    dep_manifest = spec.dep_manifest or find_by_identity(spec.engine_dir, spec.dep_manifest_sha)
    # A1 environment declaration
    if env_decl is None or _sha256(env_decl) != spec.env_decl_sha:
        log("A1 frozen environment declaration absent or not at its identity - activation refused")
        return R.error(kind, "ENV_AUTHORITY_ABSENT")
    # A2 dependency manifest
    if dep_manifest is None or _sha256(dep_manifest) != spec.dep_manifest_sha:
        log("A2 frozen dependency manifest absent or not at its identity - activation refused")
        return R.error(kind, "DEP_AUTHORITY_ABSENT")
    try:
        frozen = _parse_env_decl(env_decl)
    except (OSError, ValueError):
        return R.error(kind, "ENV_AUTHORITY_MALFORMED")
    try:
        deps = _parse_dep_manifest(dep_manifest)
    except (OSError, ValueError):
        return R.error(kind, "DEP_AUTHORITY_MALFORMED")
    if set(deps) != set(DEP_NAMES):
        log(f"A2 dependency manifest does not close over {DEP_NAMES}")
        return R.error(kind, "DEP_CLOSURE_INCOMPLETE")
    # A3 extends-frozen
    if not assert_extends_frozen(frozen, spec.additions, environ):
        log("A3 effective environment is not the frozen declaration plus exactly the additions")
        return R.error(kind, "ENV_UNQUALIFIED")
    # A4 effective interpreter: SAME OBJECT, then bytes. A byte-identical copy
    # at another inode is not the qualified object and must fail.
    qpath, qsha, _qver = deps["python"]
    try:
        a, b = os.stat("/proc/self/exe"), os.stat(qpath)
        same = (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
    except OSError:
        same = False
    if not same:
        log("A4 effective interpreter is not the same object as the qualified path")
        return R.error(kind, "RUNTIME_INTERPRETER_NOT_SAME_OBJECT")
    if _sha256("/proc/self/exe") != qsha:
        log("A4 effective interpreter bytes are not the qualified bytes")
        return R.error(kind, DEP_CODES["python"])
    # A5/A6 effective git and gitleaks: qualified path, qualified bytes, then a
    # harmless capability probe. The probe runs only after path and digest have
    # matched, so an unqualified or shadowed object is never executed.
    for name in ("git", "gitleaks"):
        qpath, qsha, qver = deps[name]
        found = shutil.which(name, path=environ.get("PATH"))
        rpath = os.path.realpath(found) if found else None
        if rpath != os.path.realpath(qpath) or _sha256(rpath) != qsha:
            log(f"A5/A6 effective {name} is not the qualified object - rejected without executing it")
            return R.error(kind, DEP_CODES[name])
        try:
            out = subprocess.run([rpath, *PROBE[name]], capture_output=True, timeout=30,
                                 env={"PATH": environ.get("PATH", ""), "LC_ALL": "C"})
            token = (out.stdout + out.stderr).decode("utf-8", "replace")
        except (OSError, subprocess.SubprocessError):
            token = ""
        if qver not in token.split() and qver not in token:
            log(f"A5/A6 {name} capability probe did not report the qualified version token")
            return R.error(kind, VERSION_CODES[name])
    # A7 frozen U6 implementation
    if find_by_identity(spec.engine_dir, spec.u6_impl_sha) is None:
        log("A7 frozen U6 implementation absent at its frozen identity")
        return R.error(kind, "U6_IMPL_ABSENT")
    log("runtime qualified: A1 env authority, A2 dep manifest, A3 extends-frozen, "
        "A4 same-object interpreter, A5-A6 qualified path+bytes+version, A7 U6 implementation")
    return None
