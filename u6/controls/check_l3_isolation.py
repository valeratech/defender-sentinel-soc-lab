#!/usr/bin/env python3
"""Prove the CI/L3 path cannot reach private material - by construction.

Static (AST) rules over the L3 closure {u6/l3_ci_sweep.py, u6/engine_bind.py,
u6/engine_iface.py, u6/result.py, u6/runlog.py}:
  S1  no import of u6.private_root (the only private-root resolver)
  S2  no import of pwd-derived private path builders other than runlog's
      account-home sibling ("runs"), i.e. the literal "msg-controls" never
      appears in the closure
  S3  the literals ".pii-terms", "baseline.key", "private-baseline",
      "K_term", "K_auth" never appear in the closure
  S4  l3_ci_sweep binds exactly engine_bind.L3_MEMBERS and that tuple shares
      no member with L3_FORBIDDEN
  S5  engine_iface's wordlist/baseline methods are never CALLED from
      l3_ci_sweep (attribute-call scan)
Workflow rule:
  W1  .github/workflows/scrub.yml contains none of the S3 literals and no
      step passes a path/env naming the private root

Exit 0 = isolated; 1 = a rule failed (printed).
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # bytecode under a publication tree is scanned by `gitleaks dir`; never leave it

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
U6 = ROOT / "u6"
CLOSURE = ["l3_ci_sweep.py", "engine_bind.py", "engine_iface.py", "result.py", "runlog.py"]
FORBIDDEN_LITERALS = (".pii-terms", "baseline.key", "private-baseline", "K_term", "K_auth", "msg-controls")
PRIVATE_METHODS = {"wordlist_load", "wordlist_scan", "baseline_load_committed",
                   "baseline_parse_private", "baseline_c4_validate", "baseline_is_exempt"}


def fail(msg):
    print(f"check-l3-isolation: FAIL {msg}")
    return 1


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from u6 import engine_bind  # noqa: E402

    for name in CLOSURE:
        src = (U6 / name).read_text(encoding="utf-8")
        tree = ast.parse(src, name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                if isinstance(node, ast.ImportFrom) and node.level and node.module == "private_root":
                    return fail(f"S1 {name} imports private_root")
                if any(m.endswith("private_root") for m in mods):
                    return fail(f"S1 {name} imports private_root")
                if isinstance(node, ast.ImportFrom) and node.level and node.module in (None, ""):
                    if any(a.name == "private_root" for a in node.names):
                        return fail(f"S1 {name} imports private_root")
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for lit in FORBIDDEN_LITERALS:
                    if lit in node.value and not _is_docstring(tree, node):
                        return fail(f"S2/S3 {name} contains literal {lit!r}")
        if name == "l3_ci_sweep.py":
            calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
            if calls & PRIVATE_METHODS:
                return fail(f"S5 l3_ci_sweep calls private engine surface {sorted(calls & PRIVATE_METHODS)}")
            binds = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "bind"]
            if len(binds) != 1:
                return fail("S4 l3_ci_sweep must call bind exactly once")
            arg = binds[0].args[1]
            if not (isinstance(arg, ast.Name) and arg.id == "L3_MEMBERS"):
                return fail("S4 l3_ci_sweep must bind L3_MEMBERS")
    if set(engine_bind.L3_MEMBERS) & engine_bind.L3_FORBIDDEN:
        return fail("S4 L3_MEMBERS overlaps L3_FORBIDDEN")

    wf = (ROOT / ".github" / "workflows" / "scrub.yml").read_text(encoding="utf-8")
    for lit in FORBIDDEN_LITERALS:
        if lit in wf and lit not in (".pii-terms",):  # .pii-terms may be named in a comment explaining it is absent
            return fail(f"W1 workflow names {lit!r}")
    if re.search(r"\.pii-terms", re.sub(r"#.*", "", wf)):
        return fail("W1 workflow references .pii-terms outside a comment")
    print("check-l3-isolation: OK (S1-S5, W1)")
    return 0


def _is_docstring(tree, node) -> bool:
    # Module/function docstrings are allowed to NAME the forbidden artifacts
    # when documenting their absence; code constants are not.
    for parent in ast.walk(tree):
        body = getattr(parent, "body", None)
        if body and isinstance(body[0], ast.Expr) and body[0].value is node:
            return True
    return False


if __name__ == "__main__":
    sys.exit(main())
