# Stage 2 — closure package (Exchange 6)

Builder-authored closure package for Reviewer final closeout (Exchange 7).
Everything here is either measured on the current publication state or
explicitly marked as a draft for Reviewer ruling. Nothing here closes a gate
or a stage; that is the Reviewer's act.

Two identities anchor this document:

```
origin/main        b7f8e2ee9484eab613697a7374e14333a2f9c2d6
predecessor        5f19815d291279d351292a80ece81a39fbaf846c
CI run             32935277166   success
```

## 1. Disposition ledger

`docs/unit6/DISPOSITIONS.md` carries the Reviewer's Exchange-5 rulings as
append-only transitions. Effective state:

| ID | effective disposition | reopening trigger |
|---|---|---|
| U6-AUTH-001 | CLOSED — ACCEPTED CURRENT LIMITATION | exact verified byte-bearing frozen authority becomes available |
| U6-ORCH-040 | CLOSED | evidence the exact-manifest commit path stages or exposes material outside its measured contract |
| U6-TEST-010 | CLOSED | none stated by Reviewer beyond contradictory evidence |
| U6-MSG-001 | CLOSED / MEASURED | contradictory evidence, or a later governed measurement showing a new published wordlist relationship |

No Unit-6 item is OPEN.

## 2. Stage-2 regression (measured, b7f8e2ee tree)

| control | result |
|---|---|
| Builder battery (`u6.controls.test_u6`) | 68 / 68 PASS |
| falsification (`u6/controls/falsify.py`) | see §2a |
| `build-attack-matrix --check` | PASS |
| `open-items --check` | PASS |
| `build-posture-register --check` | PASS |
| `check-lab-coverage --check` | PASS |
| `build-lab-index --check` | PASS |
| `check-evidence-notes` | PASS |
| `check-image-format-parity` | PASS |
| `check-current-state` | FAIL P0 AUTHORITY_UNBOUND — **correct**: fail-closed while unbound |
| `check_l3_isolation` | OK (S1–S5, W1) |
| L1 hook, authority absent | `STATUS=ERROR CODE=ENV_AUTHORITY_ABSENT RC=2` — correct refusal |
| L2 hook, authority absent | `STATUS=ERROR CODE=ENV_AUTHORITY_ABSENT RC=2` — correct refusal |
| gitleaks, full tree | 0 findings |
| bytecode directories | 0 |

Not run, and not claimed: any governed step from 25 onward. Fresh activation
was not exercised because U6-AUTH-001 is closed as an accepted limitation, not
because it was skipped.

### 2a. Falsification

Measured on the b7f8e2ee tree (regression run, Exchange 6): baseline PASS,
44/44 KILLED, 0 survived, 0 harness defect, 0 skip, 0 void; 44 defined and
44 reported, no set difference. Builder evidence; the Reviewer's independent
replays covered the four targeted new controls and the full battery.

## 3. Publication-safety gate (measured, b7f8e2ee tree)

| surface | state |
|---|---|
| `msgctl/` (private authority) in tree | ABSENT |
| `.pii-terms` tracked | NO (gitignored) |
| `u6/committed-baseline` | ABSENT (L2 fails closed BASELINE_UNRESOLVED by design) |
| `.pre-commit-config.yaml` | at base identity `d882c53b…` — no Unit-6 wiring |
| `.github/workflows/scrub.yml` | at base identity `d039c8ba…` — no Unit-6 wiring |
| CI jobs | `gitleaks`, `image-ocr`, `attack-matrix` only; `commit-msg-structural` not wired |
| private/CI separation | intact — `L3_MEMBERS` binds no wordlist member |
| `core.hooksPath` | UNSET (verified by the locked block's guard on the operator host) |
| activation scripts | present, unexecuted |
| `docs/current-state/CURRENT.txt` | `UNBOUND` |

No private authority was introduced in Stage 2. Unit-6 remains inert.

## 4. Repository baseline

```
origin/main                b7f8e2ee9484eab613697a7374e14333a2f9c2d6   (measured: push + ls-remote equality + GitHub)
CI run                     32935277166 success                        (measured: gh run watch --exit-status)
tracked files (expected)   200
tree digest (expected)     96350519e023deb8476eb3eb566483129c14720199e7e6f0fb1b0bd577297d2f
```

The tree digest is EXPECTED, computed from the reconstruction (137-file base
+ verified 62-file overlay + verified 7-file delta) with the
`10-live-head-compat.sh` algorithm, which was first validated by reproducing
the bound `273e4b48…` literal on the 137-file base. It is **not measured on
the operator host**. It becomes measured if the Reviewer chooses to have the
operator run the read-only digest line in the Exchange-6 handoff; otherwise
it stays labelled EXPECTED in the proposed revision.

## 5. Current-state authority (PROPOSED — not authority)

`docs/current-state/proposed/` holds a Builder-proposed successor revision
`2026-08-26-rev2.json` carrying the measurements in this document, plus the
re-expressed superseded predecessors `2026-08-25-rev1` and `2026-08-22-rev0`.
The checker scans only `revisions/`; the proposals are inert and
`CURRENT.txt` remains `UNBOUND`.

The proposal carries `status=PROPOSED` and
`reviewer_authority=REVIEWER_TO_SUPPLY`. Both are rejected by the checker by
design, so the proposal cannot be bound by accident or without the Reviewer
supplying the authority document identity.

### 5a. State durability controls (measured against the real checker)

| control | result |
|---|---|
| P — full chain adopted as documented (rev0 SUPERSEDED → rev1 SUPERSEDED → rev2 CURRENT, pointer to rev2) | `OK current=2026-08-26-rev2 revisions=3` |
| N — `reviewer_authority` left unsupplied | FAIL P2 |
| N — `status` left PROPOSED | FAIL P2 |
| N — pointer names rev2, rev2 absent | FAIL P1 (missing current relationship) |
| N — rev2 present, rev1 absent | FAIL P6 (missing relationship) |
| N — rev1 present, rev0 absent | FAIL P6 |
| N — rev0 present but unreachable from current | FAIL P5 |
| N — pointer names the superseded rev1 | FAIL P2 (superseded in current position) |
| N — rev1 flipped to CURRENT alongside rev2 | FAIL P3 |
| N — rev1 lists rev2 in `supersedes` (cycle / superseded-in-current-position) | FAIL P4 |

Finding from the positive control: adoption requires the **entire**
supersedes chain in `revisions/`, three files not two. The first positive
attempt with only rev1 + rev2 failed P6. That would have surfaced during
Reviewer adoption in Exchange 7; it is fixed in the proposals.

## 6. Gate-D disposition (DRAFT for Reviewer ruling)

```
Gate D

fresh activation demonstrated       NO
reason                              exact frozen authority unavailable
                                    (U6-AUTH-001 CLOSED — ACCEPTED CURRENT LIMITATION)

construction checkpoint             COMPLETE   5f19815d… (62/62 bytes, 62/62 modes)
publication                         COMPLETE   b7f8e2ee… on origin/main
current CI                          GREEN      32935277166
wordlist publication measurement    COMPLETE   U6-MSG-001 CLOSED / MEASURED
orchestration defect                CLOSED     U6-ORCH-040
test portability defect             CLOSED     U6-TEST-010
missing-authority condition         CLOSED BY DISPOSITION

proposed final status
CLOSABLE WITH ACCEPTED LIMITATION
```

This draft never states "fresh activation verified". It states what was
measured, what was closed by disposition, and the single trigger that
reopens the activation question.

## 7. Stage-2 disposition (DRAFT for Reviewer ruling)

```
Stage 2

commits                    5 remediation commits + Unit-6 checkpoint + correction commit
AUD-007 … AUD-013          CLOSED (prior)
AUD-014                    commit-message publication surface:
                             construction COMMITTED (inert)
                             wordlist surface MEASURED (no growth; Unit-6-era commits clean)
                             structural-detector surface NOT MEASURED (frozen detector unavailable)
                             enforcement NOT ACTIVE (U6-AUTH-001)
Gate D                     CLOSABLE WITH ACCEPTED LIMITATION (§6)
current-state authority    PROPOSED rev2 awaiting Reviewer adoption (§5)

proposed final status
CLOSED WITH ACCEPTED LIMITATION
```

**Carry-forward / reopening triggers**

- U6-AUTH-001 reopens on exact verified byte-bearing authority. On reopening,
  the frozen sequence resumes at step 25 with identity verification by the
  integration itself (`runtime_bind.py` A1–A7, `25-place-engine.sh`), never
  by transfer prose.
- AUD-014 enforcement (L1/L2 activation, L3 wiring) is downstream of that
  reopening and is not a Stage-3 dependency.
- U6-MSG-001 reopens on a later governed measurement showing a new published
  wordlist relationship. The instrument is committed and can be re-run locally
  at any time; its output is bounded by design.
- Ruleset question: **DEFERRED to Stage 8 final-publication review**. Branch
  protection is not bound to unavailable or intermediate Unit-6 checks.

## 8. What this package does not claim

- No fresh L1/L2/L3 activation or integration verification.
- No effective Unit-6 runtime composition.
- No governed structural-message detector execution.
- No Reviewer authority: the current-state revision is PROPOSED only, and
  the Gate-D and Stage-2 dispositions are drafts.
- The tree digest for b7f8e2ee is EXPECTED, not measured on the operator host.
