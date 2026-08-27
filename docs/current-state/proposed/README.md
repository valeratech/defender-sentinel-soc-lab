# Proposed current-state revisions (NOT authority)

Files here are Builder-proposed successors offered for Reviewer adoption. They
are never read by `scripts/check-current-state.py`, which scans only
`revisions/`. A proposal carries `status: PROPOSED`, which the checker rejects
by design, so it cannot be bound by accident.

Adoption is a Reviewer act: the Reviewer writes the adopted revision under
`revisions/`, binds `reviewer_authority` to a document in
`reviewer-authority/`, and writes the pointer line in `CURRENT.txt`. The
proposal is not moved or rewritten; what was adopted is whatever the Reviewer
placed in `revisions/`, and it may differ from the proposal.

## What this directory retains

- `2026-08-26-rev2.json` — a **historical proposal**, non-authoritative,
  superseded by the adopted `revisions/2026-08-26-rev2.json`, which the
  Reviewer bound with different content. Retained verbatim as proposal
  evidence. It shares the adopted revision's `id` because it proposed that
  revision; the directory, the `PROPOSED` status, and this note are what keep
  it from being read as the adopted one.
- `2026-08-22-rev0.superseded.json`, `2026-08-25-rev1.superseded.json` — the
  re-expressed predecessors that shipped with the rev2 proposal so the
  supersedes chain could be adopted whole. Historical, non-authoritative.

The current authority is whatever `CURRENT.txt` names; see `../README.md`.
