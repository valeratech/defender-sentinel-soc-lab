# Current state — single designated authority

Mutable project state has exactly one authoritative source in this repository:
the revision file named by `CURRENT.txt`. That revision is **Reviewer-owned**.
The Builder does not author it; the Builder may serialize what the Reviewer has
ruled, and says so inside the file when it does.

## The model

```text
revision N          payload frozen; lifecycle metadata → SUPERSEDED / N+1
      ↓ superseded by
revision N+1        payload frozen; lifecycle metadata CURRENT / absent
      ↓
CURRENT.txt selects exactly one current revision
```

A state transition creates a **new** revision that supersedes the old one. A
revision has two parts with different rules:

```text
REVISION PAYLOAD
    every field except status and superseded_by
    frozen once Reviewer-bound; never rewritten

LIFECYCLE METADATA
    status
    superseded_by
    undergo exactly one Reviewer-authorized transition, when a successor
    is adopted:   CURRENT / absent  →  SUPERSEDED / <successor id>
```

No other content of a prior revision is rewritten. The transition itself stays
reconstructable from Git history, while the current tree always presents one
unambiguous supersession chain. A revision adopted while a stage is open is
transitional: the stage's closure is recorded by a successor revision, not by
editing the one in place. A revision whose payload reads as stale is therefore
expected history; what would be defective is leaving it selected.

Workflow bookkeeping such as exchange counters is not durable project state and
is not recorded here.

## Layout

- `CURRENT.txt` — either the single word `UNBOUND`, or one line naming a file
  under `revisions/`. While `UNBOUND`, `scripts/check-current-state.py` fails
  closed: no state is selected silently, and no mirror in `history/` is
  promoted. The Reviewer binds the authority by supplying the revision file
  and the pointer line together.
- `revisions/` — Reviewer-owned revisions. New revision files are introduced
  additively. Existing revision payloads remain frozen. Only lifecycle
  metadata may undergo the single Reviewer-authorized `CURRENT → SUPERSEDED`
  transition described above. Exactly one revision carries `status: CURRENT`,
  and it carries no `superseded_by`.
- `reviewer-authority/` — the Reviewer documents that revisions bind by
  `reviewer_authority.file` and `reviewer_authority.sha256`. A revision adopted
  in-tree binds a document that exists here; earlier revisions bound documents
  that live outside this repository and are recorded by name and hash as
  provenance only.
- `proposed/` — Builder proposals for Reviewer adoption. Never authority, never
  read by the checker. See `proposed/README.md` for the historical proposals it
  retains.
- `history/` — verified copies of the mutable fields of earlier Reviewer state
  documents, bound by the SHA-256 of the document they mirror. Provenance only;
  never read as current state.

## Namespace ownership

The whole authority chain is repository-owned by construction. `docs/current-state/`,
`CURRENT.txt`, `revisions/`, every `revisions/*.json` including superseded ones,
and `reviewer-authority/` must be real, in-place repository entries: none may be
a symlink, and each must resolve exactly to its own repository path. Revision
records are repository history and cannot be imported through filesystem
indirection, even when the bytes at the far end would be valid. Superseded
revisions' Reviewer-authority documents may remain external provenance; the
revision records that name them may not.

## What the checker proves

`scripts/check-current-state.py` checks the relationship, not the values. It
proves the namespace ownership above before it reads anything. The pointer
names exactly one `CURRENT` revision that no other revision supersedes;
every `SUPERSEDED` revision is reachable from it; the supersedes graph is
acyclic; and because supersession is stored in both directions, both must
agree: `X.superseded_by = Y` exactly when `Y.supersedes` lists `X`, and the
current revision carries no `superseded_by`. For the **selected current
revision only**, the bound Reviewer authority must name one document directly
inside `docs/current-state/reviewer-authority/`; that directory must itself
resolve to exactly its repository location, so a symlinked directory is
rejected however valid its contents; the document must resolve, symlinks
followed, to a regular file whose parent is exactly that directory; and its
SHA-256 must equal the bound digest byte for byte. A well-shaped digest proves nothing on its own, and a
real file with a matching digest proves nothing if it lives outside the
repository. Superseded revisions are exempt from the authority rule on purpose:
their authorities are out-of-tree historical documents, and historical validity
must never depend on reconstructing them.

The checker runs as a pre-commit hook on these surfaces and unconditionally in
CI. It never hard-codes a stage, gate, or baseline value.

Mentions of old revision ids or old observations elsewhere in the repository
are allowed. In particular, `docs/unit6/STAGE2-CLOSURE.md` is a frozen
historical record of the Stage-2 publication state at the moment of that
closure; its mutable observations, including that `CURRENT.txt` was then
`UNBOUND`, were correct when written and are not current authority.

## External audit identifiers

`AUD-NNN` identifiers appearing in this repository (`AUD-007`, `AUD-013`,
`AUD-014`) reference external Reviewer audit findings. In-tree comments may
restate the local technical consequence of a finding, but they are not the
authoritative AUD finding record. The absence of an in-tree AUD definition is
intentional and must not be reconstructed as original evidence.
