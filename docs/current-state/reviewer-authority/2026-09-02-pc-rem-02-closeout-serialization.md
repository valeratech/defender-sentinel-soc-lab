# Reviewer current-state authority — PC-REM-02 closeout serialization

Reviewer-owned authority for the Microsoft Defender XDR / Sentinel repository current-state chain.

Decision date: 2026-09-02

Serialized by the Builder from the Reviewer's PC-REM-02 ruling together with mechanically measured publication facts. The Builder added no independent governance conclusion.

## Scope

PC-REM-02 is a new scoped item opened from a third-party post-remediation review of the published repository.

It does not reopen PC-REM-01, which remains CLOSED / PASS / PUBLISHED / CI VERIFIED. It does not reopen the original eight-stage repository audit, which remains closed on its own historical evidence. Stage 2 remains CLOSED WITH ACCEPTED LIMITATION under the Operator's permanent decision.

PC-REM-02 contains exactly four items:

1. Lab 01 escaped `*(build narrative pending)*` marker.
2. Lab 02 escaped `*(build narrative pending)*` marker.
3. Stale `POS-015` budget propagation in `docs/configuration-inventory.md`.
4. `open-items.py` detector hardening required to prevent recurrence of items 1 and 2. This is part of the root-cause cure, not a scope expansion.

No tenant, licensing, role, policy, subscription, workspace or VM mutation was involved at any point.

## Findings as measured

The two markers escaped the census because the detector required `pending` as the first token inside the emphasized parenthetical. `*(build narrative pending)*` reads as a marker to a human and was invisible to the instrument, so the generated report stated zero open items while two lab pages carried unfinished narratives.

The `POS-015` entry in `docs/configuration-inventory.md` still presented the first-configured budget amounts as current and asserted that the resource-group budget remained Actual-only. Both statements were superseded by later measurement.

## Corrections published

The two build narratives were written from evidence already recorded in their own labs; no new tenant claim was introduced.

The `POS-015` correction preserves the historical first configuration, records the 2026-07-19 raise, records the 2026-09-01 re-measurement, and supersedes rather than erases the Actual-only statement.

The detector now matches `pending` anywhere inside the emphasized parenthetical while retaining the leading emphasis boundary that excludes ordinary product prose. Measured across the repository, the change catches exactly the two escaped markers and produces no other match.

## Publication 3 — PC-REM-02 correction

```text
baseline                 eb477fad856ee2b774f880a0251f14f5b27860be
published commit         d4e34dea6de444caf4aee65ca7352bee68c5dc77
published tree           a9e1dc06b24efd6191721f09fabcafbd369a44ef
parent                   eb477fad856ee2b774f880a0251f14f5b27860be
parents                  1
changed paths            4
changed paths under u6/  0
current-state changes    0
CI run                   33681928931
CI workflow / event      scrub / push
CI branch                main
CI jobs                  3
CI steps                 32
CI steps skipped         0
CI result                success
open items after         0
escaped markers after    0
```

## Serialization boundary

The commit that publishes this revision cannot record its own commit SHA or its own post-publication CI run inside the revision it publishes.

```text
publishing commit  SELF_NOT_SELF_RECORDABLE
CI verification   EXACT_SHA_VERIFICATION_RECORDED_OUTSIDE_THIS_REVISION
changed paths     4
u6 changes        0
```

## Reopening trigger

PC-REM-02 may be reopened only by explicit Reviewer ruling based on evidence that measurement, correction, publication or reasoning inside its recorded scope was invalid. A challenge outside that scope creates a new scoped item and leaves this closure standing.

## Stage board carried forward

```text
1  CLOSED
2  CLOSED_WITH_ACCEPTED_LIMITATION
3  CLOSED_PASS
4  CLOSED_PASS
5  CLOSED_PASS
6  CLOSED_PASS
7  CLOSED_PASS
8  CLOSED_PASS
```
