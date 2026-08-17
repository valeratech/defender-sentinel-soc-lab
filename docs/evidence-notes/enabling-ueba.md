---
title: Implement behavioral analytics
date: 2026-07-31
artifacts:
  labs: ["08"]
  posture: [POS-044]
  divergences: [41]
  kql: []
corrections:
  - "Claim withdrawn — 'Sentinel ships with no detections running' was wrong; 48 anomaly rules were enabled the whole time, on a tab the Active rules count excludes."
---

# Enabling UEBA

> The configuration was already done in the entities-and-UEBA guide (`POS-044`). What this guide
> added was one testable claim, and testing it corrected something said here two
> days earlier.

## What was configured

Nothing new. UEBA was enabled 2026-07-28 and is recorded in `POS-044`.

## What was established

**48 anomaly rules are enabled, and they have written nothing.** The guide says
anomaly rule templates are *"enabled by default"* — correct, and verified. The
`Anomalies` table **resolves** (so it was provisioned when UEBA was enabled) and
returns **0 rows over 7 days**.

Anomaly rules detect deviation from a baseline. Three identities, seventeen days
of tenant history, almost no activity — there is no baseline to deviate from.
**48 detections, all enabled, all structurally unable to fire here.** That is
`POS-044`'s "UEBA cannot demonstrate its value in this environment" arriving from
a second, independent direction.

**Three surfaces, three pictures of "what detection is running."** Active rules
said **0**. The Anomalies tab said **48 enabled**. The `Anomalies` table said
**0 rows**. Only the third answers whether anything actually happened
(divergence row 41).

**The RBAC contradiction resolves, and the course guide beats the vendor
documentation.** Divergence row 33 recorded Learn naming Azure RBAC roles while
the portal banner named an Entra role. This guide states **both** are required —
Security Administrator in Entra (which Global Admin holds by inheritance), *plus*
Owner/Contributor at resource-group scope or the least-privilege Sentinel
Contributor + Log Analytics Contributor pairing. A rare direction for that to run.

**On-prem AD sync requires Defender for Identity with a sensor on a domain
controller** — confirming that leaving it off was correct rather than merely
convenient.

## What was corrected

**"Sentinel ships with no detections running" was wrong.** It was said here on
observing `Active rules: 0`, and 48 anomaly rules were enabled the entire time on
a separate tab that had been noticed and not opened. The accurate statement is
narrower and more useful: **the Active rules count covers scheduled, NRT and
Microsoft-security rules; anomaly rules are a separate class and are excluded.**
A workspace reading 0 active rules can have 48 detections enabled.

Same shape as everything else this section: the number depends on which surface
you ask.

## What could not be tested

**The behaviors layer** — separately enabled, per data source, creating
`SentinelBehaviorInfo` and `SentinelBehaviorEntities`. Still off, deliberately,
and it carries the same free-feature-billable-data shape as UEBA itself.

## Cost

Zero. Reading tabs and querying an empty table.
