# Reviewer current-state authority — Stage 7 closure

Reviewer-owned authority for the Microsoft Defender XDR / Sentinel full-repository audit.

Decision date: 2026-08-30

Serialized by the Builder from the Reviewer's Stage-7 closure ruling. The Builder added
no independent governance conclusion.

## Stage

Stage 7 — terminology, tooling, CI-hardening, and repository-consistency audit against
the governed rev6 repository state, including the S3-07C terminology territory deferred
from Stage 3.

## Disposition

PASS — implementation complete, published, and CI-verified; governance closure
authorized by Reviewer.

## Closure evidence

- Stage-7 governed baseline commit: f159e3f88cf116e51a3bb30d07c60ebe7b88de33
- Baseline tree: a73073188c8dac7b586942b24e5675390fa94988
- Accepted Stage-7 construction commit: 8b91467eded415f61d5cd965e389a2898aac6589
- Accepted construction tree: e67d860f4bb50d6dc3afb19a74dccfa60330ec8e
- Changed paths: 20, matching the accepted allowlist; 0 under `u6/`
- Stage-7 CI run: 33336796015
  - repository: valeratech/defender-sentinel-soc-lab
  - headSha: 8b91467eded415f61d5cd965e389a2898aac6589 (equals the accepted commit)
  - event: push
  - branch: main
  - workflow: scrub
  - status: completed
  - conclusion: success
  - expected job set: 3, exact match; job anomalies 0; duplicate job names 0
  - required named gates: 12 of 12 concluded success; skipped gates 0
- Stage 7 disposition: CLOSED / PASS

## CI verification method

Green was established by named job and named step conclusions, not inferred from the
run-level status field. The run-level conclusion was additionally required to agree.
The governed run was selected by exact commit SHA, workflow `scrub`, event `push`, and
branch `main`, with exactly one matching run required. Step names were matched within
their own job, because `Install gitleaks` occurs in two jobs and a run-wide selector
would miscount it.

A required gate concluding `skipped` is a failure under this method. None did.

## Sanitize standing condition

MEASURED / HOLDS at the accepted commit, immediately before publication:

- `audit-pii` rc 1
- REVIEW hit-lines 1
- sole hit category: `gitleaks — working tree`
- separate redacted gitleaks pass rc 1
- findings 2, across 1 distinct path, every finding confined to `.pii-terms`
- tracked hits 0; other-untracked hits 0
- `.pii-terms` present and not tracked

The finding count is mutable host state and is deliberately not fixed by this authority.
The governed relationship is confinement and classification, not an exact count.

## gitleaks characterization

NOT MEASURED at Stage 7. The workflow's own non-zero scan rule was enforced inside the
run and the `Scan full history` gate concluded success. The commits-scanned and
bytes-scanned characterization was not derived for run 33336796015, and no value is
asserted here. `Scan full history = success` does not retroactively establish the
Stage-6 characterization, which also remains NOT MEASURED.

## Final findings disposition, as ruled

| ID | Disposition |
|---|---|
| S7-P01 | CLOSED / REMEDIATED — the ✅ marker was defined four different ways across the standard, the generated legend, the configuration inventory, and nine lab status rows; all current-facing renderings normalized to the declared `Built, documented, validated`. Historical narrative and non-status prose left intact |
| S7-P02 | CLOSED / REMEDIATED — 🔨 renderings normalized to the declared `Built, documentation in progress` across two lab status rows and both legends |
| S7-P03 | CLOSED / INFORMATIONAL — 🔜 is declared in three legends and used by zero labs; a status vocabulary omitting the not-built state would leave the enforcement table incomplete. No construction |
| S7-P04 | CLOSED / REMEDIATED — the open-items census remains line-oriented by contract and now asserts that every opening marker token is either counted or explicitly suppressed. A marker split across source lines fails the report rather than being silently dropped |
| S7-P05 | CLOSED / REMEDIATED — the lab-coverage axis derived its universe from `posture.yml`, so a published lab owning no register entry could not appear, be counted, or be gated; labs 25 and 26 were both in that state. The axis is now the lab directories unioned with the register's lab IDs, and a zero-entry lab renders `0/0`. This is not a ruling that those labs should own entries |
| S7-P06 | CLOSED / REMEDIATED — only `✅` triggered the uncited-entry check, so a lab whose status could not be parsed left enforcement silently. Missing README, missing status row, and unparseable marker now each fail with a stated reason. Current exposure was zero; the path was not |
| S7-P07 | CLOSED / ACCEPTED DESIGN — a zero-image OCR step is a legitimate empty corpus; the upstream census establishes that corpus and the other image gates continue to assert meaningful properties. No construction |
| S7-P08 | CLOSED / NOT A REPOSITORY FINDING — `CAL-XFER-01` has no repository counterpart; the pre-commit invocation is correct and CI backstops the same policy through `ci-image-census.sh`. This does not close the transfer-side calibration item |
| S7-P09 | CLOSED / NOT A FINDING — no verdict divergence between the per-file and tree-wide policy implementations was measured, and no current authority requires behavioural identity. A demonstrated divergence would create a new scoped item |
| S7-P10 | CLOSED / NOT A FINDING — duplicate step names across separate jobs are ordinary workflow structure; verification instruments must select within job context |
| S7-P11 | CLOSED / REMEDIATED — the generated-documentation inventory described three generated documents; it now describes the four generated documents plus the generated README lab-index region, and the five generator checks CI enforces |
| S7-P12 | CLOSED / REMEDIATED — the stale literal `5 commits scanned` is replaced by the relationship the gate actually enforces: the summary must parse, and commits and bytes scanned must both be non-zero. No replacement literal was introduced |
| S7-P13 | CLOSED / REMEDIATED — `docs/instruments.md` records, for the eleven CI-invoked instruments plus `check-image-policy.sh`, the invocation form, material preconditions, execution surface, and what a PASS actually establishes. It states that a bare `check-image-policy.sh` returns 0 having evaluated nothing, that `ci-image-census.sh` and `ci-verify-image-metadata.sh` call unrooted `git ls-files` so their corpus follows the caller, and that the census counts an indexed path absent from the worktree without examining it. These are recorded as the current implementation boundary, not as repairs |
| S7-P14 | CLOSED / REMEDIATED — `check-evidence-notes.py` derives its root from its own file location rather than the caller's working directory, and missing prerequisites fail closed with one stated line instead of an uncaught traceback |

## Measurement decisions

| ID | Ruling |
|---|---|
| S7-D01 | DO NOT MEASURE — no current repository authority requires a stage-specific literal gitleaks scan count. The enforced relationship is non-zero commits and bytes with parse failure failing closed. The Stage-6 characterization remains NOT MEASURED and is not converted to a pass |
| S7-D02 | DO NOT MEASURE — no governing documentation standard requiring UTC/local table labelling was found. Creating one would be new policy rather than auditing an existing requirement. The Stage-6 characterization remains NOT MEASURED and is not converted to a pass or a finding |

## Scope measured

Terminology, tooling, CI-hardening, and repository-consistency territory against the
governed rev6 state, including:

- the complete current-facing extent of status terminology and equivalent status
  phrasing, and the governing semantic model established from authoritative repository
  evidence;
- the open-items census parser contract and its actual current exposure to markers that
  escape a line-oriented scan;
- CI and checker architecture for fail-open behaviour, vacuous assertions, ambiguous
  invocation contracts, and mismatch between what a gate claims and what it measures;
- generated-document and source-of-truth consistency, including derived values recorded
  without their derivation and generated counts mislabelled as another quantity;
- whether repository documentation accurately describes instrument invocation,
  preconditions, execution surface, and what a PASS establishes.

## Scope not measured

- `u6/` contents or effective Unit-6 behaviour;
- tenant or effective Microsoft service state;
- whether labs 25 and 26 should own posture-register entries, which is content
  adjudication rather than tooling;
- §5 Definition-of-Done conformance of the nine ✅ labs beyond the single mechanically
  decidable criterion recorded below;
- the gitleaks scan-count characterization for run 33336796015 or for run 33278881350;
- table timezone-labelling conformance, for which no in-tree convention authority exists;
- verdict equivalence between `check-image-policy.sh` and `ci-image-census.sh`;
- Stage-8 publication and ruleset territory.

These exclusions do not weaken the Stage-7 closure and do not reopen earlier closed items.

## Definition-of-Done measurement bounding S7-P01

Before the ✅ rows were normalized to a wording containing the word *validated*, the one
mechanically decidable §5 criterion was measured across all nine ✅ labs: zero
`*(pending)*` markers remain in any of them. This is the criterion Stage 6 applied when
it regressed labs 15, 16, 17 and 24 out of ✅ under S6-P01.

It is one criterion of the eight in the §5 checklist. The remaining seven are semantic
and were not measured. This is not a finding that the nine labs are §5-conformant.

## Carry-forwards

- The Stage-2 accepted limitation remains unrepaired.
- S3-05 remains closed and untouched.
- S3-07C is discharged by S7-P01 and S7-P02 and is no longer deferred.
- S3-09 remains untouched.
- `CAL-XFER-01` and `CAL-XFER-02` remain OPEN. They are successor-transfer calibration
  corrections and are not closed by this repository closure.
- The scratch-retention question remains outstanding and now covers six additional
  Stage-7 execution directories.
- Unit 6 remains inert. `core.hooksPath` was measured UNSET at every hook-reachable
  execution stop — apply, commit, sanitize, and push — so the `.githooks` L1 and L2
  enforcement never executed.

## Execution incidents

- S7-EXEC-3A-01 — CLOSED / CORRECTED IN R4. The locked Step-3a runner counted REVIEW
  hit lines and section headings anchored at column zero; `audit-pii.sh` emits leading
  spaces and ANSI formatting around both tokens, so the parser could never observe a
  hit. It reported zero hits on a host where `audit-pii` had exited 1, which is the
  REVIEW-required path. The stop was fail-closed and the standing condition was NOT
  MEASURED, not failed. A newly locked ANSI-normalising revision measured the condition
  successfully on the unchanged committed state.
- R3 Step-3a runner `833d4475…` — WITHDRAWN FOR FUTURE EXECUTION. Its single failed
  execution remains legitimate historical evidence and it must not be re-run.
- S7-EXEC-TRANSCRIPT-01 and S7-EXEC-TRANSCRIPT-02 — CLOSED / RECURRENT TERMINAL-DISPLAY
  CORRUPTION / NO STATE IMPACT ESTABLISHED. Two Operator transcripts rendered the outer
  invocation line malformed. In both cases the runner emitted complete ordered output to
  its exact endpoint and re-derived its state from Git rather than from the echoed
  command text. Root cause NOT MEASURED. A clean later transcript is an observation and
  does not resolve either incident.
- S7-EXEC-PREFLIGHT-REMOTE-01 — CLOSED / READ-ONLY REMOTE CONTACT / NO REPOSITORY
  IMPACT. A Builder control fixture fetched governed `origin/main`, and a later Builder
  preflight read governed `main` by `git ls-remote`. No write occurred and no push was
  attempted. Step 3b was deliberately not rehearsed through the network path, because
  once its local guards pass the locked runner is capable of reaching a real push.
- S7-EXEC-PUBLISH-01 — CLOSED / PUBLISHED AS LOCKED.
- R4-REC-01 — CLOSED / NONBLOCKING RECORD CORRECTION. Byte counts recorded for four
  carried-forward runners in the R4 package were character counts, not byte counts.
  SHA-256 identities were correct and remain governing; no artifact required
  regeneration.

## Governance rulings recorded during Stage 7

These entries record governance rulings that controlled Stage-7 execution. Active
project instructions remain authoritative for durable process governance; this
authority records the rulings historically and does not supersede future active
project instructions.

- MARKER-GOV-01 — during Stage 7 the Reviewer ruled that the active project-instruction
  convention controlled Operator-action presentation: ⚠️ was used only for an exact
  action jointly locked by Builder and Reviewer that the Operator had to perform then.
  That ruling superseded the conflicting Global Transfer §1 marker convention for
  Stage-7 process at the time. The frozen transfer was not modified and its former
  convention remains valid historical evidence of the rule that governed when it was
  written. Existing in-tree uses of ⚠️ are content semantics and were not reclassified
  as Operator actions. Future process governance remains controlled by active project
  instructions, not by this historical entry.
- PRIV-EVIDENCE-01 — the ruling applied during Stage 7 was that HOST-ONLY sensitivity is
  semantic and instruction-bound rather than inferred from a filename prefix:
  `HOST-ONLY-*` is a naming aid, and absence of the prefix does not imply a file is safe
  to relay. It was applied to `audit-pii.raw`, `gitleaks-dir.json`, and the captured push
  transport output, none of which carry that prefix. Active project instructions remain
  the durable authority for private-data handling.

## Tenant

No tenant object was created, modified, or read during Stage 7. Every change is text in
the repository.

## Reopening trigger

A later challenge to the evidence, measurement, or reasoning inside a finding's recorded
SCOPE MEASURED may petition to reopen that finding, and reopening requires an explicit
Reviewer ruling.

A challenge concerning territory outside that recorded scope creates a new scoped item
and does not reopen this closure.

## Stage board at this decision

- Stage 1: CLOSED
- Stage 2: CLOSED WITH ACCEPTED LIMITATION
- Stage 3: CLOSED / PASS
- Stage 4: CLOSED / PASS
- Stage 5: CLOSED / PASS
- Stage 6: CLOSED / PASS
- Stage 7: CLOSED / PASS
- Stage 8: NOT_STARTED
