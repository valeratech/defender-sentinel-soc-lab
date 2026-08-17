---
title: Security compute units and Security Copilot capacity
date: 2026-08-08
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections: []
---

# Security compute units and capacity

> The billing-mechanics guide, and the one that sets the shape of the paid
> work ahead. Its most useful content is not the price but the **unit of
> billing**: SCUs bill in whole clock-hour blocks, so the cost of the Copilot
> arc is a function of how many hour boundaries it crosses, not how long the
> work takes.

## What was configured

Nothing. No capacity resource was created and no SCUs were provisioned.

## What was established

**Capacity is an Azure resource.** Standalone provisioning rides on an active
Azure subscription: a named capacity object in a chosen region, where the region
determines where prompt evaluation runs and therefore carries the data-residency
consequence. SCU counts are adjustable from either the Azure portal or the
Security Copilot portal.

**One pool, all experiences.** Standalone sessions, embedded surfaces,
promptbooks and agents draw from the same provisioned capacity (`docs/evidence-notes/security-copilot-overview.md`).

**Two models.** Provisioned capacity bills hourly per provisioned SCU ($4 at
current list) for the steady-state baseline; overage bills on consumption ($6)
for spikes above it, and can be capped or left unlimited.

Precision on overage, verified 2026-08-08: it bills per overage SCU **consumed**
at one-decimal granularity, not per hour. Microsoft's worked example charges 4
provisioned SCUs at $4 plus 3.2 overage SCUs at $6 — $35.20 within a single
hour. "Per hour" is close enough to be harmless in conversation and wrong in a
cost model.

**Hourly blocks, and the churn trap.** Provisioned SCUs bill in whole hourly
blocks with a one-hour minimum, against provisioned capacity rather than elapsed
60-minute periods. Any usage inside an hour bills as a full unit regardless of
start or stop time. The canonical case: provision at 9:05, remove at 9:35, add
again at 9:45 → **two units billed for the 9–10 hour**. The practice that
follows is to make provisioning changes on hour boundaries and not to churn —
a delete-and-retry inside one hour doubles the charge.

**Usage monitoring** in the Security Copilot portal tracks consumption per
session and per feature. Splunk framing: treat it the way you treat ingestion
volume against a licence — the consumption data *is* the capacity plan.

## What was corrected

Two, both caught before shipping, both recorded rather than silently edited.

**The Purview example has expired.** The source guide illustrates the
separate-wallets rule with Purview Data Security Investigations metering in
SCUs — "same unit name, separate wallets." DSI now bills AI capacity in **Data
Security Investigation Compute Units**, which replaced the SCU model for that
solution. The rule survives; the illustration does not. Purview still spends
SCUs, but through its **agents** — the DLP and Insider Risk Triage agents and
the DSPM Posture agent all require provisioned SCUs to run. Correct statement:
*different* unit name, separate wallets, and DSI is the wrong example for it.

**Inclusion skips provisioning, not the resource.** The source guide states that
tenants under the M365 E5/E7 inclusion consume the monthly pool without an Azure
capacity resource. There is a capacity object: the auto-created **Default
Security Copilot Capacity**, tenant-wide, holding a default workspace, **not
modifiable**, not billed hourly, and displaying cost values that are
informational rather than charges. What inclusion removes is provisioning and
management. The distinction is load-bearing for the capacity-creation guide and capacity-teardown guide.

## What could not be tested

No capacity was provisioned, so the hourly-block mechanic is carried from
documentation and not observed. Whether the portal renders a provisioning
control at all depends on the unresolved inclusion question (`docs/evidence-notes/security-copilot-overview.md`).

**The source guide's overage guidance is inverted for this environment, and the
inversion is deliberate.** The guidance — pre-allocate overage headroom so a
demand spike does not hit a capacity wall — frames the trade as *surprise on the
bill* versus *throttle during a crisis*. That is correct for a production SOC,
where being throttled mid-incident is the expensive outcome. Here there is no
incident, no crisis, and a fixed ceiling, so the expensive outcome is the bill
and a throttle costs only a retry. **Overage will be capped at zero, and a
second clock hour bought deliberately at $4 rather than left to $6 units that
engage on their own.** Recorded because a reader who knows the product would
otherwise read the configuration as a mistake: it is the same reasoning against
opposite inputs.

## Cost

$0. Nothing was provisioned.

Forward: the arc's exposure is bounded by clock hours crossed, not by work
done — one hour $4, two hours $8, against a $10 ceiling. Provisioning changes
happen on the hour, and there are no retries inside one.
