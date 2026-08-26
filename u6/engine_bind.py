"""Bind the frozen Unit-6 engine by identity before first use.

Rules (frozen):
  * expected-executable-hash binding happens BEFORE the first detector call;
  * a member whose bytes differ from ENGINE-IDENTITIES.txt is never imported;
  * each layer binds only the member set it is permitted to reach. L3 (CI)
    is structurally denied ``wordlist``, ``baseline``, ``crypto`` and
    ``identity``: those names are not in its allowed set, so no code path in
    the CI process can load them. This is separation by construction, not
    by cleanup.

All failures return a Result with STATUS=ERROR. Nothing here raises to the
caller's stdout.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import types
from pathlib import Path

from . import result as R

REPO_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_FILE = Path(__file__).resolve().parent / "ENGINE-IDENTITIES.txt"

# Member sets per layer. Names are the *frozen* module names under msgctl/.
L1_MEMBERS = ("serialize", "runtime", "adapter", "structural", "wordlist")
L2_MEMBERS = ("serialize", "crypto", "runtime", "adapter", "structural",
              "wordlist", "identity", "baseline")
L3_MEMBERS = ("serialize", "runtime", "adapter", "structural")

L3_FORBIDDEN = frozenset({"wordlist", "baseline", "crypto", "identity"})
assert not (set(L3_MEMBERS) & L3_FORBIDDEN)


def expected_identities(identity_file: Path | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (identity_file or IDENTITY_FILE).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        out[rel.strip()] = digest.strip()
    return out


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


class Engine:
    """Namespace of verified, imported frozen modules for one layer."""

    def __init__(self, members: dict[str, types.ModuleType]):
        self._m = members

    def __getattr__(self, name: str) -> types.ModuleType:
        try:
            return self._m[name]
        except KeyError:
            raise AttributeError(name) from None

    def has(self, name: str) -> bool:
        return name in self._m

    def symbol(self, module: str, name: str):
        mod = self._m.get(module)
        if mod is None or not hasattr(mod, name):
            return None
        return getattr(mod, name)


def bind(kind: str, members: tuple[str, ...], engine_dir: Path | None = None,
         identity_file: Path | None = None):
    """Return (Engine, None) or (None, Result[ERROR]).

    ``engine_dir``/``identity_file`` are overridable ONLY so the Builder
    controls can bind a labelled test double with its own identity manifest.
    Production entry points never pass them (see l1/l2/l3 modules)."""
    engine_dir = engine_dir or (REPO_ROOT / "msgctl")
    if not engine_dir.is_dir():
        return None, R.error(kind, "ENGINE_DIR_ABSENT")
    expected = expected_identities(identity_file)
    loaded: dict[str, types.ModuleType] = {}
    # Verify EVERY requested member before importing ANY of them.
    paths: dict[str, Path] = {}
    for name in members:
        rel = f"msgctl/{name}.py"   # only the eight engine modules are importable members
        p = engine_dir / f"{name}.py"
        if rel not in expected:
            return None, R.error(kind, "ENGINE_MEMBER_ABSENT")
        if not p.is_file():
            return None, R.error(kind, "ENGINE_MEMBER_ABSENT")
        if sha256_file(p) != expected[rel]:
            return None, R.error(kind, "ENGINE_IDENTITY_MISMATCH")
        paths[name] = p
    # Import under an isolated package name so the layer-scoped namespace
    # is the only route to the engine (no ``import msgctl.wordlist`` leak).
    pkg_name = f"_u6_engine_{kind.lower()}"
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(engine_dir)]
    sys.modules[pkg_name] = pkg
    try:
        for name, p in paths.items():
            spec = importlib.util.spec_from_file_location(f"{pkg_name}.{name}", p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"{pkg_name}.{name}"] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            loaded[name] = mod
    except Exception:
        return None, R.error(kind, "ENGINE_IMPORT_FAILED")
    return Engine(loaded), None


def sys_modules_reach(forbidden: frozenset[str], kind: str | None = None) -> list[str]:
    """Names in sys.modules whose leaf matches a forbidden engine member.
    Used by the L3 isolation control to prove nothing private was loaded.
    With ``kind`` the scan is limited to that layer's namespace; the CI
    process binds only L3, so in CI the two forms are equivalent."""
    prefix = f"_u6_engine_{kind.lower()}." if kind else "_u6_engine_"
    hits = []
    for name in list(sys.modules):
        leaf = name.rsplit(".", 1)[-1]
        if leaf in forbidden and name.startswith(prefix):
            hits.append(name)
    return sorted(hits)
