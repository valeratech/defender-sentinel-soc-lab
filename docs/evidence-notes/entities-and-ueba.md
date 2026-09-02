---
title: Classify and analyze data by using entities
date: 2026-07-29
artifacts:
  labs: ["08"]
  posture: [POS-044, POS-034]
  divergences: [33, 34, 35]
  kql: ["kql/sentinel/store-partition-diff.kql"]
corrections:
  - "Lab 08 — 'the billable surface is exactly five tables' conflated workspace-resident with billable; AzureActivity and Usage are workspace-resident and free."
  - "Prerequisite claim withdrawn — Global Admin was asserted insufficient for enabling UEBA on Learn's basis; the portal states it is exactly what is required, and the enable succeeded."
---

# Entities and UEBA

> Entity mapping belongs to the analytics-rules guide, where rules are actually built. What was
> live here was one decision deferred since the start of the section: whether to
> enable UEBA, and what it costs.

## What was configured

**UEBA, enabled 2026-07-28 19:58 local (02:58 UTC)** — `POS-044`. Entra ID
directory sync on, Active Directory off, seven data sources connected, behaviors
layer deliberately off.

## What was established

**The feature is free and the data it generates is billable — measured, not
quoted.** Learn states both halves and only the first is memorable. `IdentityInfo`
now appears as a **billable** DataType at 0.001416 MB/24h, alongside `SigninLogs`
and `AuditLogs`. Total billable volume **0.0437 MB/day** against a 10 GB/day
allowance. **"The feature is free" and "enabling it is free" are different
claims.**

**The store-partition method detected a table changing sides.** `IdentityInfo` was
XDR-lake-only on 2026-07-26 — that absence was the evidence used to conclude UEBA
was not running. It is now workspace-resident and metered. The method built during
the Lab 08 correction worked on a question it wasn't built for.

**Prediction: 2 of 4**, on the record beforehand. `IdentityInfo` and
`BehaviorAnalytics` appeared; `UserPeerAnalytics` and `UserAccessAnalytics` did
not. Hypothesis, unestablished: three identities have no peer groups to compare
and almost no access history, so those two may be structurally unpopulatable
rather than merely slow — indistinguishable from latency on a single census.

**Initial sync took under an hour**, against Learn's "may take a few days."

**`BehaviorAnalytics` inherits the source event's timestamp** — its only row
matches the latest `SigninLogs` row to the millisecond. So a behaviour record
tells you when the activity happened, not when UEBA noticed, and **UEBA's own
latency cannot be measured from `TimeGenerated`**.

**Enabling UEBA is three acts and the page reports "enabled" after the first.**
Toggle, then directory sync, then data sources. With only the toggle on, both
directories read `Sync disabled` and the source list read `0 sources` — switched
on, analysing nothing. Only the empty-state text reveals the order.

**"Connect available data sources" connects everything eligible, and eligible
means the connector exists.** Seven green, **three carrying data**. Two are Entra
log types deliberately declined in Lab 08, one names the *legacy agent* connector
where Lab 07 built AMA + DCR, one needs a running device. Four will read
`Connected` indefinitely and contribute nothing, indistinguishable on the page
from the three that work.

**An open caveat closed.** `AuditLogs` was recorded on 2026-07-26 as *selected but
absent — quiet tenant likely, unconfirmed rather than assumed*. It now carries
data. The connector was fine; the tenant was quiet, which is exactly what
`POS-034` declined to assume at the time.

## What was corrected

**Lab 08 said the billable surface was five tables.** It is three. `AzureActivity`
had 11 events in the measured window and is not billable; neither is `Usage`. The
error was conflating **workspace-resident** with **billable** — the census
separates the free XDR lake from the workspace, but a **second split exists inside
the workspace** that the census cannot see. `Usage | where IsBillable` answers
billability; the census answers residency. Two questions, two tools.

This also establishes that `SecurityAlert` and `SecurityIncident` are free — the
whole Defender XDR → Sentinel path from Lab 04 costs nothing to carry.

**A prerequisite claim was wrong.** Learn names Azure RBAC roles; the portal names
an Entra role, and the enable succeeded on Global Admin. I asserted the Learn
version and told the operator Global Admin would not suffice. The portal was right
about what the portal enforces.

## What could not be tested

**UEBA's actual value.** Fifteen days of tenant life, three identities, almost no
activity. No baseline means no anomaly detection means nothing to evaluate. This
was designed as a **plumbing test** and must not be read as an assessment of the
feature.

**The behaviors layer** — separate tab, independently enabled, creating two more
billable tables. Left off.

**`BehaviorAnalytics` billability** — absent from the billable list, but its only
row postdates `Usage`'s reporting lag. Absence from a lagging table is not
evidence. **Resolved by read, 2026-09-01:** lag-cleared, `BehaviorAnalytics` holds 579 rows and `Usage` reports 143 records for it with **IsBillable = true** — billable at very small measured volume (rounds to 0.000 GB at 3 dp).

## Cost

**0.0437 MB/day measured**, of which UEBA contributes 0.0014. No Azure resource,
no VM, no Bastion. The feature added a billable line item and no meaningful spend.
