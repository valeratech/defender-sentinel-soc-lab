#!/usr/bin/env python3
"""Verify the current-state authority relationship.

This checker binds STRUCTURE plus the relationship to ONE designated state
authority (docs/current-state/CURRENT.txt). It never hard-codes a stage,
gate, or baseline value: a well-shaped record can still be false, so the
relationship is what is checked, and the values are read only to confirm
they are internally consistent with that relationship.

Passes when:
  P0  CURRENT.txt exists and is one line. The single word UNBOUND means the
      Reviewer has not yet bound the current authority: the checker FAILS
      CLOSED (rc 1, reason AUTHORITY_UNBOUND). It never selects a mirror
      from history/ in place of the missing authority.
  P1  CURRENT.txt names one existing revisions/*.json
  P2  the named revision parses, carries every required key, status=CURRENT,
      and binds a reviewer_authority {file, sha256(64 hex)}
  P3  exactly one revision in revisions/ has status=CURRENT, and it is the
      named one
  P4  no revision lists the current revision in its `supersedes`
      (superseded state may not occupy the current-authority position)
  P5  every other revision has status=SUPERSEDED, names `superseded_by`,
      and is reachable from the current revision by walking `supersedes`
  P6  the supersedes graph is acyclic and every referenced ID exists

Historical/superseded mentions elsewhere in the repository are allowed.
Exit 0 on pass; 1 on failure with a one-line reason per failed rule.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CS = ROOT / "docs" / "current-state"
POINTER = CS / "CURRENT.txt"
REVS = CS / "revisions"

REQUIRED = ("id", "status", "supersedes", "reviewer_authority")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# history/ is deliberately not scanned: labelled copies are never candidates.
def fail(msg: str) -> int:
    print(f"check-current-state: FAIL {msg}")
    return 1


def main() -> int:
    if not POINTER.is_file():
        return fail("P1 CURRENT.txt absent")
    lines = POINTER.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1 or not lines[0].strip():
        return fail("P1 CURRENT.txt must be exactly one non-empty line")
    rel = lines[0].strip()
    if rel == "UNBOUND":
        return fail("P0 AUTHORITY_UNBOUND - Reviewer-owned current revision not yet bound; refusing to select state")
    if not re.match(r"^revisions/[A-Za-z0-9._-]+\.json$", rel):
        return fail("P1 pointer must name revisions/<name>.json")
    cur_path = CS / rel
    if not cur_path.is_file():
        return fail(f"P1 pointed revision missing: {rel}")

    revs: dict[str, dict] = {}
    by_path: dict[Path, dict] = {}
    for p in sorted(REVS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return fail(f"P2 unparsable revision {p.name}")
        if not isinstance(d, dict):
            return fail(f"P2 revision not an object: {p.name}")
        for k in REQUIRED:
            if k not in d:
                return fail(f"P2 {p.name} missing required key {k}")
        if not isinstance(d["id"], str) or d["id"] in revs:
            return fail(f"P2 duplicate/invalid id in {p.name}")
        if d["status"] not in ("CURRENT", "SUPERSEDED"):
            return fail(f"P2 {p.name} status must be CURRENT or SUPERSEDED")
        ra = d["reviewer_authority"]
        if not (isinstance(ra, dict) and isinstance(ra.get("file"), str) and ra.get("file")
                and isinstance(ra.get("sha256"), str) and HEX64.match(ra["sha256"])):
            return fail(f"P2 {p.name} reviewer_authority must bind file + sha256")
        if not isinstance(d["supersedes"], list) or not all(isinstance(x, str) for x in d["supersedes"]):
            return fail(f"P2 {p.name} supersedes must be a list of ids")
        revs[d["id"]] = d
        by_path[p.resolve()] = d

    cur = by_path.get(cur_path.resolve())
    if cur is None:
        return fail("P2 pointed revision not loaded")
    if cur["status"] != "CURRENT":
        return fail("P2 pointed revision is not status=CURRENT")

    currents = [i for i, d in revs.items() if d["status"] == "CURRENT"]
    if currents != [cur["id"]]:
        return fail(f"P3 exactly one CURRENT revision required, found {currents}")

    for i, d in revs.items():
        for s in d["supersedes"]:
            if s not in revs:
                return fail(f"P6 {i} supersedes unknown id {s}")
            if s == cur["id"]:
                return fail(f"P4 superseded state in current position: {i} supersedes current {s}")

    # reachability + acyclicity from current
    seen: set[str] = set()
    stack = [cur["id"]]
    path: list[str] = []
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(revs[n]["supersedes"])
    # cycle check (DFS with colors)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {i: WHITE for i in revs}

    def dfs(n: str) -> bool:
        color[n] = GREY
        for s in revs[n]["supersedes"]:
            if color[s] == GREY:
                return False
            if color[s] == WHITE and not dfs(s):
                return False
        color[n] = BLACK
        return True

    for i in revs:
        if color[i] == WHITE and not dfs(i):
            return fail("P6 supersedes graph has a cycle")

    for i, d in revs.items():
        if i == cur["id"]:
            continue
        if d["status"] != "SUPERSEDED":
            return fail(f"P5 {i} is not SUPERSEDED")
        if d.get("superseded_by") not in revs:
            return fail(f"P5 {i} superseded_by must name an existing revision")
        if i not in seen:
            return fail(f"P5 {i} is not reachable from the current revision")

    print(f"check-current-state: OK current={cur['id']} authority={cur['reviewer_authority']['file']} "
          f"revisions={len(revs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
