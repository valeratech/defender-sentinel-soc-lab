# Current state — single designated authority

Mutable project state has exactly one authoritative source in this repository:
the revision file named by `CURRENT.txt`. That revision is **Reviewer-owned**.
The Builder does not author it.

- `CURRENT.txt` — either the single word `UNBOUND`, or one line naming a file
  under `revisions/`. While `UNBOUND`, `scripts/check-current-state.py` fails
  closed: no state is selected silently, and no mirror in `history/` is
  promoted. The Reviewer binds the authority by supplying the revision file
  and the pointer line together.
- `revisions/` — Reviewer-owned current revision(s). Append-only once bound.
- `history/` — verified copies of earlier Reviewer state documents' mutable
  fields, labelled by the exact SHA-256 of the document they mirror. Provenance
  only; never read as current state.

`scripts/check-current-state.py` checks the relationship, not the values:
the pointer names exactly one `CURRENT` revision that no other revision
supersedes, and every `SUPERSEDED` revision is reachable from it. Mentions of
old revision ids elsewhere in the repository are allowed.
