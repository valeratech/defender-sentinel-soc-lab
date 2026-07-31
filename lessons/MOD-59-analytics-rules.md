---
module: 59
title: Configure and manage analytics rules
section: Configure Detections
verdict: lab
date: 2026-07-31
artifacts:
  labs: ["11"]
  posture: [POS-045, POS-046]
  divergences: [36, 37, 38, 39]
  kql: []
corrections:
  - "Design error — suppression left unconfigured on an authored rule after the duplication mechanism had already been explained in full; 12 alerts and 12 incidents from one 92-second event."
  - "Recommended fix did not work — `extend timestamp = StartTime`, inferred from Microsoft's template, does nothing; `extend TimeGenerated = StartTime` is the working convention."
  - "Two readings withdrawn mid-lab — run 3 was called contaminated when it had succeeded, and an app-attribution hypothesis was disproved by re-running in the correct portal."
---

# Module 59 — Analytics Rules

> Module 58 was concept and produced no lessons file of its own; its content is
> the framing for this one. The lab is the firing, not the wizard.

## What was configured

**Two scheduled rules on one technique** (`T1110`, Credential Access), Lab 11:
Microsoft's `Brute force attack against Azure Portal` template, tuned (`POS-045`),
and `LAB-Bruteforce-Failed-Signins`, authored by hand (`POS-046`). Then triggered
once each, before and after a fix.

**No live endpoint needed** — both read `SigninLogs`, and failed sign-ins are
self-triggerable. Both VMs stayed deallocated.

## What was established

**Lab 10's lesson applied in advance.** The template library was searched *before*
authoring, found three brute-force templates, and the design changed as a result —
enable *and* author, turning an accidental overlap into a designed comparison.

**Alerts = lookback ÷ frequency.** `60 ÷ 5 = 12`, observed exactly: twelve alerts
at five-minute intervals for one 92-second event, then silence when the failures
aged out. Event grouping deduplicates *within* a run; only suppression
deduplicates *across* runs. With alert grouping disabled, **incidents = alerts** —
twelve queue items, each needing individual triage.

**Suppression fixed it, measured: 12 → 1.** Same rule, same trigger, one setting.

**An enabled rule is a hypothesis.** The Microsoft template has never fired,
recorded as `validated: false`, which is why the coverage matrix now reads
**Credential Access PARTIAL (1/2)** — the first PARTIAL in this repository.

**A template's value is not the query.** The query is editable and could be
written from scratch. What it embeds is domain knowledge — two Account entities,
one keyed on a strong identifier and one on a weak composite, so the entity
resolves whichever a source supplies. Custom details and alert details ship empty.

**Frequency and lookback are coupled** (row 36), the wizard and the template
detail pane disagree about incident creation (row 37), and **Sentinel scheduled
alerts receive no automated investigation** — `Unsupported alert type` on all
thirteen incidents, where Lab 10's MDO incident reads `Queued` (row 39). Module
53 established that an alert is not an action; for Sentinel rules there is no
action path at all.

**Baseline before either rule: 0 active rules.** A workspace ingesting data with
no detections running — module 58's "without analytics rules Sentinel is a data
lake," demonstrated rather than asserted. *(See MOD-61: that count excludes
anomaly rules, of which 48 were enabled.)*

## What was corrected

**Suppression was left unconfigured after the mechanism had been explained in
full.** The overlap behaviour was described — *twelve evaluations, deduplication
is what suppression is for* — and then the rule was built without it. Understanding
a failure mode is not designing against it.

**The recommended fix for the activity span did not work, and the second attempt
did.** `extend timestamp = StartTime` was inferred from the template carrying it,
not from knowing what the field does — and the template never fired, so there was
no evidence it worked there either. It changes nothing.
`extend TimeGenerated = StartTime` **works**, confirmed across two runs. The
template's idiom is stale. But it yields a **point, not a range** — 0 seconds for
a 90-second event, where before it was 60 minutes. Neither is right (row 38).

**Suppression's cost was not anticipated.** Run 4's alert reports **5 of 7**
failures: the rule ran mid-burst and suppression blocked the corrected count a
later run would have produced. **The alert you keep is the earliest and least
complete one** — a 29% undercount on the number used to judge severity.

**And two readings were withdrawn mid-lab.** Run 3 was called contaminated when
it had in fact succeeded. And a proposed finding — that `AppDisplayName` splits
one burst across apps below threshold — was disproved by re-running in the correct
portal: all seven logged as `Azure Portal`. The variance was in the test.

## What could not be tested

**Whether an alert can carry an event *range* rather than a point** from a
summarized result. *(pending)*

**The template's deviation threshold.** It failed on failure count before the
deviation logic was reached, so the argument that a three-identity tenant cannot
satisfy it is **untested rather than confirmed**.

## Cost

Zero. No VM, no Bastion. Alerts and incidents land in `SecurityAlert` and
`SecurityIncident`, both measured non-billable in module 57. Twelve duplicate
alerts cost nothing in money — the price of that pattern is analyst attention.
