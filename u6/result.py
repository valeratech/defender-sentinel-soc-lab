"""Unit-6 operational result vocabulary.

Every Unit-6 layer (L1, L2, L3, adjudication, diagnostics) terminates in
exactly one Result. The vocabulary is closed. No layer may emit free text
on the transportable channel; only a Result rendered by ``render()``.

Frozen contract carried from the Gate-C / Unit-6 rulings:

    PASS     policy evaluated, nothing rejected
    REJECT   policy evaluated, publication refused
    ERROR    mechanism/configuration failure - NEVER rendered as REJECT
    NOT_RUN  the layer had nothing to evaluate (e.g. L2 empty ref stream)
    STOP     governed run halted at a categorical boundary (adjudication)

Return codes are distinct per status so that a shell caller can never
confuse an execution failure with a policy verdict.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

PASS = "PASS"
REJECT = "REJECT"
ERROR = "ERROR"
NOT_RUN = "NOT_RUN"
STOP = "STOP"

STATUSES = (PASS, REJECT, ERROR, NOT_RUN, STOP)

RC = {PASS: 0, NOT_RUN: 0, REJECT: 1, ERROR: 2, STOP: 3}

# Closed code vocabulary. Adding a code is a reviewed diff of this file.
CODES = frozenset({
    # generic
    "OK", "NONE",
    # engine binding
    "ENGINE_DIR_ABSENT", "ENGINE_MEMBER_ABSENT", "ENGINE_IDENTITY_MISMATCH",
    "ENGINE_IMPORT_FAILED", "ENGINE_SYMBOL_ABSENT", "ENGINE_CALL_FAILED",
    # environment
    "ENV_UNQUALIFIED", "RUNTIME_ID_MISMATCH",
    # private root
    "PRIVATE_ROOT_UNOPENABLE", "PRIVATE_ROOT_NOT_DIR", "PRIVATE_ROOT_OWNER",
    "PRIVATE_ROOT_MODE", "PRIVATE_MEMBER_ABSENT", "PRIVATE_MEMBER_UNREADABLE",
    "WORDLIST_ABSENT", "WORDLIST_UNREADABLE",
    # baseline
    "BASELINE_UNRESOLVED", "BASELINE_COMMITTED_ABSENT", "BASELINE_INVALID",
    "BASELINE_C4_FAILED",
    # L1
    "MSG_FILE_ABSENT", "MSG_FILE_UNREADABLE", "STRUCTURAL_FINDING",
    "WORDLIST_FINDING",
    # L2
    "NO_REF_UPDATES", "L2_NOT_RUN", "REF_STREAM_MALFORMED", "TAG_REF_REFUSED",
    "NON_HEAD_REF_REFUSED", "REMOTE_NOT_ORIGIN", "ORIGIN_URL_MISMATCH",
    "UNION_ENUMERATION_FAILED", "UNION_FINDING",
    # L3
    "L3_ADVISORY_FINDINGS", "L3_CLEAN", "L3_PRIVATE_SYMBOL_REACHABLE",
    # adjudication / return channel
    "STOP_RC_1", "STOP_RC_2", "STOP_RC_3", "STOP_RC_OTHER",
    "CHILD_ABSENT", "CHILD_IDENTITY_MISMATCH", "CHILD_SIGNALLED",
    "STATUS_FILE_ABSENT", "STATUS_FILE_MALFORMED", "STATUS_FILE_UNEXPECTED",
    "TRANSPORT_LINE_REJECTED", "PRIVATE_SINK_UNAVAILABLE", "CATEGORICAL_MALFORMED",
    "PHASE2_CATEGORICAL",
    # runtime binding
    "RUNTIME_INTERPRETER_UNQUALIFIED", "RUNTIME_GIT_UNQUALIFIED",
    "RUNTIME_GITLEAKS_UNQUALIFIED", "U6_IMPL_ABSENT", "U6_IMPL_IDENTITY_MISMATCH",
    "RUNTIME_INTERPRETER_NOT_SAME_OBJECT", "RUNTIME_GIT_VERSION_MISMATCH",
    "RUNTIME_GITLEAKS_VERSION_MISMATCH",
    "ENV_AUTHORITY_ABSENT", "ENV_AUTHORITY_MALFORMED", "DEP_AUTHORITY_ABSENT",
    "DEP_AUTHORITY_MALFORMED", "DEP_CLOSURE_INCOMPLETE",
    # L2 union
    "REMOTE_QUERY_FAILED", "REMOTE_HEAD_NOT_LOCAL",
    # phase-2 diagnostic passthrough (categorical only)
    "PHASE2_READY", "PHASE2_NOT_READY", "PHASE2_UNDETERMINED",
})

_KIND = re.compile(r"^[A-Z0-9_]{2,32}$")
_COUNTS = re.compile(r"^([a-z_]+=\d+)(,[a-z_]+=\d+)*$|^$")

# Exactly the transportable line shape. Anything else is refused by the
# return channel before it can reach stdout.
# No digest or commitment derived from private material (wordlist, private
# baseline, adjudication evidence, private run log) is ever part of this line.
# STATE is present only in categorical mode: 1..8 uppercase KEY=VALUE tokens
# relayed verbatim from a frozen instrument's own privacy-safe line.
_STATE_TOKEN = r"[A-Z][A-Z0-9_]{0,39}=[A-Z0-9_]{1,40}"
RECORD_RE = re.compile(
    r"^U6_RETURN v1 KIND=([A-Z0-9_]{2,32}) STATUS=(PASS|REJECT|ERROR|NOT_RUN|STOP) "
    r"CODE=([A-Z0-9_]{1,40}) RC=([0-3]) COUNTS=([a-z_]+=\d+(?:,[a-z_]+=\d+)*|-)"
    r"(?: STATE=(" + _STATE_TOKEN + r"(?: " + _STATE_TOKEN + r"){0,7}))?$"
)


@dataclass(frozen=True)
class Result:
    kind: str
    status: str
    code: str
    counts: dict = field(default_factory=dict)
    state: str | None = None

    def __post_init__(self):
        if not _KIND.match(self.kind):
            raise ValueError("kind")
        if self.status not in STATUSES:
            raise ValueError("status")
        if self.code not in CODES:
            raise ValueError("code")
        for k, v in self.counts.items():
            if not re.match(r"^[a-z_]+$", k) or not isinstance(v, int) or v < 0:
                raise ValueError("counts")
        if self.state is not None:
            toks = self.state.split(" ")
            if not 1 <= len(toks) <= 8 or any(not re.match("^" + _STATE_TOKEN + "$", t) for t in toks):
                raise ValueError("state")

    @property
    def rc(self) -> int:
        return RC[self.status]

    def render(self) -> str:
        counts = ",".join(f"{k}={v}" for k, v in sorted(self.counts.items())) or "-"
        line = (f"U6_RETURN v1 KIND={self.kind} STATUS={self.status} CODE={self.code} "
                f"RC={self.rc} COUNTS={counts}" + (f" STATE={self.state}" if self.state else ""))
        if not RECORD_RE.match(line):
            # Defensive: the dataclass validation above should make this
            # unreachable. If reached, refuse rather than leak.
            raise ValueError("record shape")
        return line


def parse(line: str) -> Result:
    m = RECORD_RE.match(line.rstrip("\n"))
    if not m:
        raise ValueError("not a U6_RETURN record")
    kind, status, code, rc, counts, state = m.groups()
    cd = {} if counts == "-" else {k: int(v) for k, v in (p.split("=") for p in counts.split(","))}
    r = Result(kind=kind, status=status, code=code, counts=cd, state=state)
    if str(r.rc) != rc:
        raise ValueError("rc/status mismatch")
    return r


def error(kind: str, code: str, **counts) -> Result:
    return Result(kind=kind, status=ERROR, code=code, counts=counts)
