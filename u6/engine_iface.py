"""Engine call surfaces used by the integration layer.

Every call into the frozen engine goes through this file. The entry points
named in the Builder transfer §10 are used verbatim:

    adapter.extract_l1(msg_bytes)                 -> bytes   (verbatim bytes for L1)
    structural.scan_message(msg_bytes)            -> iterable of findings
    structural.struct_detector_id(finding)        -> str
    baseline.load_committed(path)                 -> committed baseline object
    baseline.parse_private(raw_bytes, key_bytes)  -> private baseline object
    baseline.c4_validate(committed, private)      -> C4Result (.failures iterable)

Three surfaces are NOT named in any transfer and are INTERFACE ASSUMPTIONS,
carried as a disclosed limitation until confirmed against the frozen bytes:

    wordlist.load_terms(path)                     -> terms object
    wordlist.scan_message(terms, msg_bytes)       -> iterable of findings
    baseline.is_exempt(private, commit_sha, finding) -> bool   (L2 exemption test)

If a symbol is absent the layer returns ERROR/ENGINE_SYMBOL_ABSENT. If a
call raises, the layer returns ERROR/ENGINE_CALL_FAILED. Neither is ever
rendered as REJECT. Exception text is never transported (it may carry
private values on supported loader paths - Gate-C two-surface ruling); it is
written to the private run log only.
"""
from __future__ import annotations

from . import result as R


class Iface:
    def __init__(self, kind: str, engine, log):
        self.kind, self.e, self.log = kind, engine, log

    def _sym(self, module: str, name: str):
        s = self.e.symbol(module, name)
        if s is None:
            self.log(f"symbol absent: {module}.{name}")
        return s

    def _call(self, fn, *a):
        try:
            return fn(*a), None
        except Exception as exc:  # noqa: BLE001 - text goes to private log only
            self.log(f"engine call failed: {type(exc).__name__}: {exc}")
            return None, R.error(self.kind, "ENGINE_CALL_FAILED")

    # ---- L1 / L2 / L3 shared ----
    def extract_l1(self, msg: bytes):
        fn = self._sym("adapter", "extract_l1")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        return self._call(fn, msg)

    def structural_scan(self, msg: bytes):
        fn = self._sym("structural", "scan_message")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        out, err = self._call(fn, msg)
        if err:
            return None, err
        return list(out or []), None

    def struct_detector_id(self, finding) -> str:
        fn = self._sym("structural", "struct_detector_id")
        if fn is None:
            return "UNKNOWN"
        try:
            return str(fn(finding))
        except Exception:  # noqa: BLE001
            return "UNKNOWN"

    # ---- wordlist (L1, L2 only; structurally unreachable from L3) ----
    def wordlist_load(self, path):
        fn = self._sym("wordlist", "load_terms")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        return self._call(fn, path)

    def wordlist_scan(self, terms, msg: bytes):
        fn = self._sym("wordlist", "scan_message")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        out, err = self._call(fn, terms, msg)
        if err:
            return None, err
        return list(out or []), None

    # ---- baseline (L2 only) ----
    def baseline_load_committed(self, path):
        fn = self._sym("baseline", "load_committed")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        return self._call(fn, path)

    def baseline_parse_private(self, raw: bytes, key: bytes):
        fn = self._sym("baseline", "parse_private")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        return self._call(fn, raw, key)

    def baseline_c4_validate(self, committed, private):
        fn = self._sym("baseline", "c4_validate")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        return self._call(fn, committed, private)

    def baseline_is_exempt(self, private, commit_sha: str, finding):
        fn = self._sym("baseline", "is_exempt")
        if fn is None:
            return None, R.error(self.kind, "ENGINE_SYMBOL_ABSENT")
        out, err = self._call(fn, private, commit_sha, finding)
        if err:
            return None, err
        return bool(out), None
