#!/usr/bin/env python3
"""Verify the current-state authority relationship.

This checker binds STRUCTURE plus the relationship to ONE designated state
authority (docs/current-state/CURRENT.txt). It never hard-codes a stage,
gate, or baseline value: a well-shaped record can still be false, so the
relationship is what is checked, and the values are read only to confirm
they are internally consistent with that relationship.

Passes when:
  P0  the current-state namespace is repository-owned by construction:
      docs/current-state/, CURRENT.txt, revisions/, and every revisions/*.json
      (superseded ones included) are real in-place entries, none a symlink,
      each resolving exactly to its own repository path. Revision records are
      repository history and cannot be imported through filesystem indirection,
      even when the bytes at the far end would be valid.
      CURRENT.txt is one line. The single word UNBOUND means the
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
  P7  the CURRENT revision's reviewer_authority resolves INSIDE the designated
      authority namespace: the value names one document directly under
      docs/current-state/reviewer-authority/; that directory itself resolves
      to exactly its repository location (no symlinked component anywhere in
      its path); the document resolves (symlinks followed) to a regular file
      whose parent is exactly that directory; and the file's SHA-256 equals
      the bound digest byte for byte. A digest that is merely
      well-shaped proves nothing, and a real file with a matching digest proves
      nothing either if it lives outside the repository. Superseded revisions
      are exempt on purpose: their authorities are out-of-tree historical
      documents bound by name and hash as provenance, and historical validity
      must never depend on reconstructing them.
  P8  supersession is stored in both directions and both must agree:
      X.superseded_by = Y  iff  Y.supersedes contains X. The current revision
      carries no superseded_by. Two copies of one relationship that can drift
      are not a source of truth until something proves they agree.

Historical/superseded mentions elsewhere in the repository are allowed.
Exit 0 on pass; 1 on failure with a one-line reason per failed rule.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CS = ROOT / "docs" / "current-state"
POINTER = CS / "CURRENT.txt"
REVS = CS / "revisions"

REQUIRED = ("id", "status", "supersedes", "reviewer_authority")
AUTH_DIR = CS / "reviewer-authority"
AUTH_REL = "docs/current-state/reviewer-authority/"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# history/ is deliberately not scanned: labelled copies are never candidates.
def fail(msg: str) -> int:
    print(f"check-current-state: FAIL {msg}")
    return 1


def owned(path: Path, kind: str) -> str | None:
    """Prove that a path is repository-owned by construction.

    ROOT is already resolved, so a path built beneath it resolves to itself
    exactly when no component of it is a symlink. Anything that resolves
    elsewhere is not repository state, however valid the bytes at the other
    end: the current-state authority chain must be selectable only from
    files that live where the repository says they live. Returns a reason on
    failure, None on success. Applied uniformly to every path this checker
    reads, so the invariant is not enforced one surface at a time.
    """
    rel = path.relative_to(ROOT).as_posix()
    if path.is_symlink():
        return f"{rel} is a symlink; current-state paths must be real repository entries"
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        return f"{rel} absent"
    if resolved != path:
        return f"{rel} resolves elsewhere ({resolved}); namespace escaped"
    if kind == "dir" and not path.is_dir():
        return f"{rel} is not a directory"
    if kind == "file" and not path.is_file():
        return f"{rel} is not a regular file"
    return None


def main() -> int:
    # Namespace ownership first: nothing is read from a path that has not been
    # proven to be a real, in-place repository entry.
    for path, kind in ((CS, "dir"), (POINTER, "file"), (REVS, "dir")):
        why = owned(path, kind)
        if why:
            return fail(f"P0 current-state namespace: {why}")
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
        why = owned(p, "file")
        if why:
            return fail(f"P0 revision record: {why}")
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

    # P7: the selected authority must be real, not merely well-formed. Only the
    # CURRENT revision is held to this; see the module docstring for why the
    # superseded ones are not.
    ra = cur["reviewer_authority"]
    rel = ra["file"]
    # Namespace first, existence second. The string must name a document inside
    # the authority directory as a plain relative path: no absolute paths, no
    # traversal, no normalisation tricks.
    if rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel):
        return fail(f"P7 current reviewer_authority must be a relative in-tree path: {rel}")
    if not rel.startswith(AUTH_REL) or not rel.endswith(".md"):
        return fail(f"P7 current reviewer_authority must name {AUTH_REL}<document>.md: {rel}")
    doc = rel[len(AUTH_REL):]
    if "/" in doc or doc in ("..", ".", "", ".md"):
        return fail(f"P7 current reviewer_authority must be one document directly under {AUTH_REL}: {rel}")
    # The namespace root itself must be where the repository says it is. ROOT is
    # already resolved, so if any component of the authority directory is a
    # symlink, resolving it changes the path - and a directory that resolves
    # elsewhere is not the designated namespace, however valid its contents.
    why = owned(AUTH_DIR, "dir")
    if why:
        return fail(f"P7 designated authority directory: {why}")
    # Then the document: it must resolve, symlinks followed, to a regular file
    # whose parent is exactly the (now proven) authority directory.
    auth_path = AUTH_DIR / doc
    try:
        resolved = auth_path.resolve(strict=True)
    except OSError:
        return fail(f"P7 current reviewer_authority file not in tree: {rel}")
    if resolved.parent != AUTH_DIR:
        return fail(f"P7 current reviewer_authority resolves outside {AUTH_REL}: {rel}")
    if not resolved.is_file():
        return fail(f"P7 current reviewer_authority is not a regular file: {rel}")
    actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    if actual != ra["sha256"]:
        return fail(f"P7 current reviewer_authority digest mismatch for {ra['file']}: "
                    f"bound {ra['sha256'][:12]}..., file is {actual[:12]}...")

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

    # P8: both stored directions of every supersession agree.
    if "superseded_by" in cur:
        return fail(f"P8 current revision {cur['id']} must not carry superseded_by")
    for i, d in revs.items():
        if i == cur["id"]:
            continue
        succ = d["superseded_by"]
        if i not in revs[succ]["supersedes"]:
            return fail(f"P8 {i} says superseded_by {succ}, but {succ}.supersedes does not list {i}")
    for y, d in revs.items():
        for x in d["supersedes"]:
            if revs[x].get("superseded_by") != y:
                return fail(f"P8 {y} supersedes {x}, but {x}.superseded_by is "
                            f"{revs[x].get('superseded_by')!r}, not {y}")

    print(f"check-current-state: OK current={cur['id']} authority={cur['reviewer_authority']['file']} "
          f"namespace=owned authority_verified=namespace+sha256 chain_verified=reciprocal revisions={len(revs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
