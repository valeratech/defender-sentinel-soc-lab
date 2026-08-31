# Reviewer current-state authority — Stage 8 closure

Reviewer-owned authority for the Microsoft Defender XDR / Sentinel full-repository audit.

Decision date: 2026-08-31

Serialized by the Builder from the Reviewer's Stage-8 rulings. The Builder added no
independent governance conclusion.

## Stage

Stage 8 — final publication review and project-audit closure against the governed rev7
repository state: the published Stage-7 closure commit
a53856ed1652ba18c665897fa0a414ff56df0186 with tree
d71c7046e10c2a290c9f5416480e7dabf20acda1. Stage 8 was opened by Reviewer directive on
Operator authorization given in the Operator's own turn on 2026-08-30. The unfrozen
successor Global Transfer was ruled not a blocker to opening; it remains a parallel
handoff task and is not a current-state authority.

## Disposition

PASS — no material in-scope blocker remained between the governed rev7 state and final
governance closure. One LOW documentation-record finding (S8-C01) was remediated,
published, and independently CI-verified before this closure was serialized; the ruleset
question deferred from Stage 2 is dispositioned (S8-J01); governance closure of the audit
programme is authorized by the Reviewer.

This is governance closure. It is not a claim that lab documentation is complete: at the
Stage-8 baseline the repository's own lab README Status rows record nine labs as
`Built, documented, validated` and eighteen as `Built, documentation in progress` (27 lab
directories; `build-lab-index.py` reports 27 by its own count), and `docs/open-items.md`
states its own count of outstanding pending markers. Those are honestly recorded states,
not defects, and this authority does not convert them.

## Closure evidence

Stage 8 published in two commits, deliberately separated so that no record asserts
closure before the remediation it closes on has landed and been verified.

Implementation (Phase A):

- Governed baseline commit: a53856ed1652ba18c665897fa0a414ff56df0186
- Baseline tree: d71c7046e10c2a290c9f5416480e7dabf20acda1
- Accepted implementation commit: cb989eed3b0f75646fa4b62ba640940d6ddb7699
- Implementation tree: b15ceda2bd5b57ec5cb5d068956af7bcc2e57d48
- Parent: a53856ed1652ba18c665897fa0a414ff56df0186; exactly one parent; exactly one
  commit ahead of the baseline
- Changed paths: 1 — `docs/instruments.md`, one insertion and one deletion in one table
  row; 0 under `u6/`
- Implementation CI run: 33432244452
  - repository: valeratech/defender-sentinel-soc-lab
  - headSha: cb989eed3b0f75646fa4b62ba640940d6ddb7699 (equals the accepted commit)
  - event: push · branch: main · workflow: scrub
  - status: completed · conclusion: success
  - exactly one matching governed run; raw job count 3; each required job name once;
    no unexpected job
  - required named gates: 12 of 12 concluded success; skipped gates 0
- Publication was a fast-forward of exactly one commit; no force push occurred.
- `core.hooksPath` measured UNSET at every hook-reachable stop — apply, commit, and push
  — so the `.githooks` L1 and L2 paths never executed.

Governance closure (Phase B): this authority is published by the Stage-8 closure commit
itself. A record cannot bind the identity of the commit that publishes it, so that
commit's SHA, its Step-3a sanitize measurement, and its exact-SHA CI verification are
recorded in the Stage-8 final Reviewer ruling and the successor Global Transfer, not here.

Measurement evidence supporting the closure, established during Stage-8 measurement:

- Live remote `refs/heads/main` equalled the governed baseline at measurement, and the
  commit object's tree equalled the tree reconstructed from the Operator-supplied source
  carrier — a verified tree-equivalent source carrier, not a byte-identical copy.
- Current-state chain at baseline: `CURRENT.txt` selected rev7; rev7 CURRENT superseding
  rev6; rev6 SUPERSEDED by rev7; `check-current-state.py` PASS across eight revisions.
- Governed instruments on a Unit-6-boundary-compliant fixture: `build-attack-matrix`,
  `build-posture-register`, `build-lab-index`, `open-items`, `check-lab-coverage`,
  `check-evidence-notes`, `check-current-state`, `check-image-format-parity` — all rc 0.
  The census, metadata, and OCR instruments were deliberately not run on that fixture and
  no repository-wide result is claimed for them; CI exercises them against a clean
  checkout.
- Published refs: `main` plus three historical branches, each a fully merged ancestor of
  `main` (`git merge-base --is-ancestor`); 85 commits reachable from `main`
  (`git rev-list --count`) at the Stage-8 baseline, no merge commits (`git log --merges`),
  one committer identity (`git log --format=%ce`).

## CI verification method

Green was established by named job and named step conclusions, not inferred from the
run-level status field; the run-level conclusion was additionally required to agree. The
governed run was selected by exact 40-hex commit SHA, workflow `scrub`, event `push`, and
branch `main`, with exactly one matching run required. Step names were matched within
their own job, because `Install gitleaks` occurs in two jobs and a run-wide selector would
miscount it. A required gate concluding `skipped` is a failure under this method; none did.

An abbreviated SHA is not acceptable for run selection: `gh run list --commit` returns
`no runs found` for a short form while the run exists under the full 40-character form,
which is a silent false negative rather than an error.

The workflow contract was re-derived from `.github/workflows/scrub.yml` rather than
carried from prior documents: three jobs, twelve substantive gates, the only conditional
step being the auxiliary SARIF upload, no Unit-6 reference, and `audit-pii.sh` never
invoked in CI.

## Sanitize standing condition

MEASURED / HOLDS at the accepted implementation commit
cb989eed3b0f75646fa4b62ba640940d6ddb7699, immediately before publication:

- `audit-pii` rc 1
- section shape: the exact source-derived ordered eleven-category shape, with the image
  corpus empty at measurement time
- REVIEW hit-lines 1; sole hit category `gitleaks — working tree`
- personal-terms pass ran; not skipped
- separate redacted gitleaks pass rc 1; report a parseable JSON list
- findings across 1 distinct path, every finding confined to `.pii-terms`
- tracked hits 0; other-untracked hits 0
- `.pii-terms` present, untracked, and ignored

The finding count observed at that stop is execution evidence for that stop only. It is
mutable host state, is deliberately not fixed by this authority, and is not promoted into
a current-state constant. The governed relationship is confinement and classification.

The parser was built from the exact `scripts/audit-pii.sh` bytes rather than from prose,
and recognises the two shapes that source permits: the eleven categories, or those
eleven followed by `Image metadata` as the final section when the image corpus is
non-empty. The image corpus is built by worktree globbing rather than from the tracked
set, and `.gitignore` permits image-bearing ignored surfaces, so both shapes are
source-valid. Any other observed shape is NOT MEASURED rather than failed, because an
unrecognised shape means the instrument did not observe the run it was built for.

## gitleaks characterization

NOT MEASURED at Stage 8. S7-D01 stands: the enforced relationship is a parseable summary
with non-zero commits and bytes scanned, and no literal count is asserted. The Stage-6
characterization remains NOT MEASURED.

## Final findings disposition, as ruled

| ID | Disposition |
|---|---|
| S8-C01 | CLOSED / REMEDIATED — LOW. `docs/instruments.md` recorded the execution surface of `check-evidence-notes.py` as `CI`, while the pre-commit hook `generated-docs-fresh` also invokes it. The Surface cell now reads `CI, pre-commit`. Documentation understatement only; no behavioural, privacy, or authority-chain impact. Confirmed independently by the Reviewer against the supplied carrier. Remediated in commit cb989eed3b0f75646fa4b62ba640940d6ddb7699 and CI-verified by run 33432244452 before this closure was serialized. A new Stage-8 finding against the state Stage 8 measured; Stage 7 is not reopened |
| S8-C02 | CLOSED / NOT A FINDING — the measured fact is accepted: `docs/instruments.md` is not linked from the README repository map and is reached through a prose mention in `docs/configuration-inventory.md`. The README map is selective and establishes no contract that every load-bearing document receives an individual link; the omission makes the instrument contract neither unavailable nor incorrect. Discoverability enhancement only. README unchanged |
| S8-J01 | CLOSED / DECIDED — no ruleset or classic branch-protection configuration is required as a condition of final governance closure. Repository rulesets: MEASURED, none present on the public rulesets surface during Stage-8 measurement, corroborated independently by Builder and Reviewer. Classic branch protection: NOT MEASURED at Stage 8; the 2026-08-19 observation in `SANITIZATION.md` is retained as historical evidence only and is not re-dated. Successful historical direct pushes establish that those pushes were permitted; they do not establish universal historical absence of protection or of bypass conditions, and no such absence is recorded here. The repository publishes through a governed direct-publication model with exact-SHA CI verification; adding a GitHub configuration dependency at closure would create new mutable state requiring its own configured-versus-effective adjudication without resolving an existing blocker. Deliberately not a ruling that branch protection lacks security value. No GitHub settings mutation is required or authorized by this closure; no Unit-6 dependency is created |

## Measurement decisions

| ID | Ruling |
|---|---|
| S7-D01 | STANDS — not remeasured at Stage 8 |
| S7-D02 | STANDS — not remeasured at Stage 8 |
| S8-M01 | NOT MEASURED — classic branch protection on `main`. This is an evidence-boundary statement, not a DO NOT MEASURE ruling; it may be measured under a later scoped item. Absence is not inferred |

## Scope measured

- published repository identity and current-state authority integrity, separating live
  remote measurement from source-carrier reconstruction;
- final publication protection to the extent legitimately observable: repository rulesets
  measured, classic branch protection not measured, effective publication history read
  from immutable commit evidence;
- the current CI and publication contract as re-derived from the workflow, including job
  and gate structure, skip semantics, pins, invocation-surface agreement with
  `docs/instruments.md`, and the absence of any Unit-6 dependency;
- generated-state and instrument coherence on a compliant fixture, including the
  pre-commit surface against the instrument contract;
- integrity of every governance carry-forward in the published Stage-7 authority and rev7;
- privacy, Unit-6, and publication-safety architecture by inspection: no host-only
  artifact class tracked, private wordlist unreachable from CI by construction, Unit-6 L1
  and L2 activation surfaces present but dependent on `core.hooksPath`, L3 present and
  unwired;
- final publication readiness against the frozen acceptance criteria.

## Scope not measured

- `u6/` contents or effective Unit-6 behaviour;
- classic branch protection on `main` (S8-M01);
- step-level gate conclusions of the Stage-7 closure run 33340553447, which remain the
  Stage-7 ruling's evidence and were not re-derived at Stage 8;
- the host sanitize standing condition outside the governed Step-3a stop;
- the precise pre-runner failure point of the withdrawn Step-3a r1 invocation
  (S8A-EXEC-3A-01), ruled not required for closure;
- the Stage-2 accepted limitation, the Stage-6 DO-NOT-MEASURE items, and every closed
  Stage-3 through Stage-7 finding, none of which Stage 8 reopened or repaired;
- tenant or effective Microsoft service state; lab content quality or §5
  Definition-of-Done conformance; historical scratch; private baseline contents.

These exclusions do not weaken the Stage-8 closure and do not reopen earlier closed items.

## Carry-forwards

- The Stage-2 accepted limitation remains unrepaired.
- S3-05 remains closed and untouched.
- S3-07C remains discharged by S7-P01 and S7-P02 and is not Stage-8 work.
- S3-09 remains untouched: a nonblocking historical carry-forward.
- `CAL-XFER-01` and `CAL-XFER-02` remain OPEN with their corrections incorporated into
  the successor Global Transfer. They are transfer-side calibration items; this repository
  closure does not close them, and freezing the transfer establishes the transfer's
  identity only.
- The scratch-retention question remains outstanding and now additionally covers six
  Stage-8 Phase-A execution directories: step 1, step 2, step 3a r1, step 3a r2, step 3b,
  and step 4.
- Unit 6 remains inert. `core.hooksPath` was measured UNSET at every hook-reachable
  Stage-8 execution stop. The `u6/` subtree is unchanged at
  deb025cf611164476c2e7c0365b41f74818ba838.

## Execution incidents

- S8A-EXEC-3A-01 — CLOSED / FAIL-CLOSED PRE-RUNNER STOP. A repeated paste of the locked
  Step-3a block stopped at its fresh-scratch guard because `~/stage8a-step3a-exec-r1`
  already existed from an earlier invocation. A locked read-only inspection of that
  scratch found `endpoint.txt`, `STOP.txt`, `hooksPath.txt`, and `step3a.log` all absent;
  because the paste block creates `step3a.log` through `tee` when the runner pipeline
  begins, its absence establishes that the earlier invocation never reached runner
  execution. No sanitize measurement was performed by it and none was lost. The exact
  pre-runner failure point was ruled not required for closure and remains NOT MEASURED,
  and the Builder's hypothesis about it was not promoted to evidence. The subsequent
  execution at fresh scratch `~/stage8a-step3a-exec-r2` was therefore the first actual
  execution of that instrument, not a re-measurement. The r1 scratch is retained and must
  not be reused or cleaned.

## Measurement-record items

- ERR-04 — ACCEPTED / NONBLOCKING. A Builder non-mutation check ran `git add -A` on the
  sparse compliant fixture, staging the fifty unmaterialized `u6/` index entries as
  deletions. The fixture's index was thereby mutated; no worktree byte, Operator
  repository, tenant state, private material, or `u6/` materialization changed, and the
  published tree reference was restored from the published object before any further
  conclusion was drawn.
- ERR-05 — ACCEPTED / NONBLOCKING. A mechanical invocation-string comparison omitted the
  census row of `docs/instruments.md`; the row was confirmed by direct read of the
  workflow.
- ERR-06 — NONBLOCKING. A Builder construction harness ran under `set -e` and aborted at
  the first intended non-zero checker exit, truncating a control log. No candidate content
  was affected; the harness was corrected and the candidate rebuilt to the same tree.
- ERR-07 — NONBLOCKING. A build script of unestablished provenance was found at a path
  the Builder was writing to. Its outputs matched the Builder's own patch bytes exactly,
  but provenance could not be established, so the script and its outputs were quarantined
  by digest and every artifact was regenerated from the Builder's visible script. No
  quarantined artifact was delivered.
- ERR-08 — NONBLOCKING. A test harness stripped a leading path separator from an expected
  remote identity, so a negative control tested identity rather than the condition it was
  written for. The harness was corrected and the affected controls re-run.
- ERR-09 — NONBLOCKING. A Builder relay stated a hook-skip count that contradicted its own
  enumeration in the same paragraph; corrected by mechanical count. No gate or commit
  impact.
- ERR-10 — NONBLOCKING. A Builder relay understated the retained Stage-8 scratch
  inventory; corrected to six by enumeration of the executed stops.

ERR-09 and ERR-10 share one cause — a count asserted from recollection rather than
derived — which is the failure mode the numeric-evidence discipline exists to prevent.

## Governance rulings recorded during Stage 8

These entries record rulings that controlled Stage-8 process. Active project instructions
remain authoritative for durable process governance.

- BUILDER-CAL-U6-01 — CALIBRATION BOUNDARY VIOLATION / NO OPERATOR OR REPOSITORY IMPACT.
  During successor-Builder intake a new index-backed fixture materialized the supplied
  `u6/` contents. No activation occurred and no repository, host, tenant, or Stage-7 state
  was affected. The controlling rule for every later fixture: inspect or hash a carrier's
  existing `u6/` bytes in place if needed; never extract, copy, reconstruct, or
  materialize `u6/` into a new fixture; carry its already-established tree identity by
  index reference; and make no repository-wide census or materialization claim from a
  fixture that omits tracked paths.
- CAL-XFER-GOV-01 — freezing a transfer establishes the identity of the transfer and does
  not close a governance disposition. `CAL-XFER-01` and `CAL-XFER-02` remain OPEN until a
  designated current-state authority explicitly closes them.
- PROVENANCE-01 — a Git tree reconstructed from a source carrier's contents and modes that
  equals a published tree is a verified tree-equivalent source carrier; it is not a
  byte-identical copy, and commit identity is established separately from the remote
  commit object.
- PUBLICATION-SEQ-01 — implementation completion and governance closure are separate acts
  and must be separately published. A closure record may not be published in the same
  commit as the remediation it closes on, because the current-state chain would then
  assert closure before the remediation had been published and CI-verified. Stage 8
  followed the Stage-7 architecture: implementation commit, exact-SHA CI verification,
  then closure serialization.
- OBSERVABILITY-SEQ-01 — the mechanism required to observe the result of an irreversible
  act must be proven usable before the act. The Stage-8 push runner establishes `gh`
  presence and valid authentication before any remote-mutating operation and fails closed
  otherwise, so a publication cannot occur that the verification step could not then
  observe.

## Tenant

No tenant mutation was authorized or performed during Stage 8, and no Stage-8 closure
conclusion depends on tenant evidence. Every change is text in the repository.

## Reopening trigger

A later challenge to the evidence, measurement, or reasoning inside a finding's recorded
SCOPE MEASURED may petition to reopen that finding, and reopening requires an explicit
Reviewer ruling.

A challenge concerning territory outside that recorded scope creates a new scoped item and
does not reopen this closure.

## Stage board at this decision

- Stage 1: CLOSED
- Stage 2: CLOSED WITH ACCEPTED LIMITATION
- Stage 3: CLOSED / PASS
- Stage 4: CLOSED / PASS
- Stage 5: CLOSED / PASS
- Stage 6: CLOSED / PASS
- Stage 7: CLOSED / PASS
- Stage 8: CLOSED / PASS
