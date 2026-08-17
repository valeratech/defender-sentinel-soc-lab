---
title: Anomaly rules and NRT execution semantics
date: 2026-08-10
artifacts:
  labs: [21]
  posture: [POS-090, POS-091]
  divergences: [168, 169, 170, 171, 172]
  kql: []
corrections:
  - "Guide: 'each anomaly rule can be edited — thresholds and parameters are adjustable through the standard analytics-rule interface.' False for built-ins: the portal refuses and directs the user to duplicate first."
  - "Guide: 'both versions write to the Anomalies table so you can compare over a 24-hour sample.' Incomplete: the duplicate arrives Disabled and must be enabled explicitly. The distinguishing mechanism is also a Flighting tag, not only the rule id."
  - "Guide: promoting the customized rule demotes the original. Confirmed — but the guide stops there. Deleting the promoted rule leaves the original demoted, with nothing to restore it."
  - "Guide: 'zero results with zero errors is the expected outcome in a quiet lab.' Half right. The guide anticipates a null; it does not anticipate a positive result produced by a history-scoped validation surface, which is what any lab with prior 4625 activity will see."
  - "Guide teaches the baseline × threshold NRT rule as a working brute-force detector, noting only that it is static-threshold rather than ML. The deeper defect is unstated: bin(TimeGenerated, 1h) cannot span an hour in a rule that sees one minute of ingestion per execution."
  - "Guide's NRT limits section does not mention that incident settings govern alert visibility across two Defender surfaces — the difference between finding your alert and concluding your rule is broken."
---

# Anomaly rules and NRT execution semantics

> Nominally: built-in anomaly rules, and writing your own anomaly-style
> detection as an NRT rule. Actually: two lessons in surfaces that report
> confidently and wrongly — an authoring wizard that validates a broken rule
> against the wrong data, and an anomaly lifecycle where five correct-looking
> fields compose into a silently disabled detection.

## What was configured

**Phase 1 — nothing persisted.** An anomaly rule was duplicated, its threshold
moved 0.7 → 0.5, the copy promoted to Production, then deleted and the original
restored. Executed twice. The tenant ended identical to its starting state.

**Phase 2 — one experimental rule.** `LAB-NRT-4625-Window-Test`, NRT,
`baseline = 1; threshold = 2` (deliberately reduced from the guide's 5/3 for
hand-executability; the semantic under test is unchanged), incidents **off**,
**no `DET-` id**. Built to fail measurably, disabled at teardown, retained as
evidence.

The reduction and the no-id decision are recorded rather than silent: the rule
is a falsification test, not a detection, and must not enter the catalogue.

## What was established

**The hour bin preserves no state between executions** (Lab 21 §8.1). Eight
qualifying failures on one account in one clock hour — four distributed, four
concentrated. The distributed four produced no alert; the concentrated four
produced an alert reporting **4**, not 8. `bin(TimeGenerated, 1h)` names a
bucket that never holds more than one minute of ingested data. `POS-046` reached
the same constraint from `SigninLogs` by design decision three weeks earlier;
this measures it from `SecurityEvent`. Two stores, one constraint.

**The validation surface produces evidence for the wrong conclusion**
(Lab 21 §8.2). Pre-save validation runs against Log Analytics over the panel's
range — seven days — not NRT semantics. The broken query returns a matching row
and looks healthy. A confidently wrong yes is worse than a silent zero.

**Alert visibility is governed by a setting on a different step**
(Lab 21 §8.3, `POS-091`). With incidents off, a firing rule is absent from the
Defender alerts queue *and* the `AlertInfo` table while present in
`SecurityAlert`. `AlertInfo` held 21 other Sentinel alerts at the time, so the
absence is configuration, not fault. Extends the store-partition finding in `docs/evidence-notes/entities-and-ueba.md`.

**The anomaly rule lifecycle composes into a silent-disable hazard**
(Lab 21 §4.3, `POS-090`). Built-ins cannot be edited, only duplicated;
duplicates arrive Disabled; promotion demotes the counterpart atomically;
deletion does not restore; and the Edit form renders Mode at a default rather
than the stored value, so opening a rule and saving silently writes Production.
Mode has no column — a badge is the only honest surface.

**AMA uploads on a quantised slot grid** (Lab 21 §5). Fourteen consecutive
`_TimeReceived` values ≡ 17 (mod 20), holding across a guest reboot. Delivery
delay is quantised, not distributed. This measurement is what made the two
controls designable — without it, a null is ambiguous and a fire is
uninterpretable.

**A measured fix does not transfer across rule types** (Lab 21 §8.5). `POS-046`'s
suppression fix belongs to a 12:1 lookback-to-frequency ratio; NRT's is 1:1, so
there is nothing to suppress. The same error class appeared twice in one lab —
the `P89-6` rejection was the other instance.

## What was corrected

Six guide claims, listed in the `corrections:` frontmatter. The two that matter
most: **thresholds are not adjustable on built-ins** (the portal says so
explicitly and the guide does not), and **the guide's expectation of a null
validation result** anticipates the wrong failure mode — a positive result from
a history-scoped surface is both more likely and more dangerous.

Also corrected within this repository, not the guide: **`P89-6` was rejected
before testing** for transferring `DET-004`'s `alerts = lookback ÷ frequency`
formula across rule types, and two predictions authored here were **falsified**
in flight — that Disabled + Production would be refused, and that Control B
would report a count of 3. Both recorded on the lab record.

## What could not be tested

**`P89-5b` — comparing anomaly output between Flighting and Production
versions.** Structurally impossible in this tenant, not merely untested: the
`Anomalies` table holds 0 rows (`docs/evidence-notes/enabling-ueba.md`, `POS-044`), so there is nothing to
compare. Three identities and a quiet tenant give the models no baseline, and a
share of the 48 enabled rules have no connected data source at all.

**`P89-10` — whether the Bastion Developer SKU bills.** Deferred by billing
latency, not foreclosed. Resolves on a Cost analysis read.

**Whether other anomaly models expose more than one tunable parameter.**
`Anomalous Azure operations` exposes exactly one — Thresholds → Score. Observed
for this rule; not generalised to the other 47.

## Cost

VM 2 for **3 h 18 m** (10:17 → ~13:35 US/Pacific). One Bastion Developer SKU
host created and deleted inside the window; charge unverified (`P89-10`).
Phase 1 cost nothing — no VM, no ingestion, no metered surface.

The wall-clock the money did not buy: **≤ 17 minutes** from VM start to first
heartbeat, against Lab 07's ~5-minute working expectation, plus a Bastion login
failure caused by an Entra-versus-local identity collision that no cost line
records.
