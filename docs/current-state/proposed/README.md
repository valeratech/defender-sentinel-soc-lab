# Proposed current-state revisions (NOT authority)

Files here are Builder-proposed successors for Reviewer adoption. They are
never read by `scripts/check-current-state.py`, which scans only
`revisions/`. `CURRENT.txt` remains `UNBOUND` and the checker fails closed
until the Reviewer adopts a proposal.

Adoption is a Reviewer act: set `status` to `CURRENT`, bind
`reviewer_authority`, move the proposal and BOTH re-expressed superseded predecessors
(rev1 and rev0 - the checker requires the entire supersedes chain to exist)
into `revisions/`, and write the pointer line. A proposal
carries `status=PROPOSED`, which the checker rejects by design, so it cannot
be bound by accident.
