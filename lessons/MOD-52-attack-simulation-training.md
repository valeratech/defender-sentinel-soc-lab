---
module: 52
title: Run an attack simulation email campaign
section: Configure Detections
verdict: lab
date: 2026-07-26
artifacts:
  labs: ["09"]
  posture: [POS-035, POS-036, POS-037, POS-038, POS-039]
  divergences: [16, 17, 18, 19]
  kql: ["kql/advanced-hunting/simulation-email-telemetry.kql"]
corrections: []
---

# Module 52 — Attack Simulation Training

> The campaign confirmed what it was supposed to. Getting it to report anything
> at all produced the findings.

## What was configured

A Credential Harvest campaign — global Netflix payload, all-users targeting with
the admin excluded, Microsoft training assigned, 2 days. Recorded as `POS-037`.

Plus one thing that was never in the plan: **unified audit logging** (`POS-035`),
turned on by cmdlet after the portal path failed.

## What was established

**Attack simulation training tests users. It is not evidence about detection,
and it cannot be hunted.** Zero incidents was predicted — Microsoft exempts its
own drills. The stronger result is that the payload produces *no email telemetry
at all*, while the notifications bracketing it are recorded normally. No
`EmailEvents` row means no hunting query, no detection rule, no ATT&CK mapping.
Lab 09 §7.

Two symmetrical misreadings follow, and both are mistakes a competent person
makes: see no alert and conclude detection is broken (it was told to stand
down), or conclude the tenant is covered (nothing about detection was
exercised).

**A negative result only counts when it was predicted.** The absence of an
incident was written down as expected *before* the click. Noticing afterwards
that nothing happened would be indistinguishable from not looking.

**A five-link dependency chain no guide documents** — simulation reporting needs
unified audit logging, which needs a hydrated Exchange org, which new/trial
tenants do not have, which propagates unevenly beneath an org-level boolean.
`POS-035`, `POS-036`, divergence row 17.

**Defaults shape the teaching more than the payload does.** Payload indicators
off (`POS-039`) means the educational page is a verbatim copy of the message
with nothing marking what gave it away. Positive reinforcement off (`POS-038`)
means correct reporting receives nothing while failure receives a landing page,
two modules and weekly reminders.

## What was corrected

Nothing — but this module produced the reasoning error that later modules kept
repeating back. See "what could not be tested."

## What could not be tested

**Foreclosed by the tenant clock and by n=1**, not merely skipped: trend across
campaigns, repeat-offender behaviour (needs consecutive compromises), and 90-day
training reassignment. A 100% compromise rate with one target is arithmetic.

**Not tested, and still open:** `labuser`'s access to assigned training, which
hit *Permission Required*.

## Cost

Zero. MDO Plan 2 rides on the E5 trial; no Azure resource, no VM, no ingestion.
The expensive thing was wall-clock — roughly an hour lost to audit-log
propagation before a one-shot observation could safely be spent.
