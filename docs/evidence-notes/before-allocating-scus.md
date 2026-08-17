---
title: Warning before allocating SCUs — prerequisites and cost discipline
date: 2026-08-08
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections: []
---

# Before allocating SCUs

> The last guide before money. Its content is one sentence with consequences:
> Security Copilot capacity **bills while it exists, not while it is used, and
> has no stopped state**. Everything else — the order of operations, the
> session pattern, the arithmetic — follows from that.

## What was configured

Nothing. No capacity resource was created.

## What was established

**Capacity precedes workspace.** Standalone deployment has a fixed sequence:
the workspace — where sessions, promptbooks and settings live — cannot be
created until SCU capacity exists to run it. So the first concrete action of a
standalone deployment is creating the capacity resource, from either the
Security Copilot portal or the Azure portal; both produce the same Azure
resource against the subscription.

**The meter starts at creation, not at use.** One provisioned SCU bills $4 for
the hour whether five minutes or fifty-five are spent in it. Deletion stops
billing; the hours the resource existed are charged and nothing after. Crossing
an hour boundary alive bills the next block. A forgotten capacity resource costs
roughly **$96/day**, consistent with the ~$2,900/month figure in the Security Copilot overview guide.

**This names a category the repo already had.** `POS-016`'s correction of
2026-08-01 established it by measurement, not by analogy: deallocation ends
*compute* spend, only deletion ends *resource* spend — recorded there as "the
same shape as Bastion, billed while existing, no stopped state." That correction
was forced by the July invoice, which measured ~$10.84 pre-tax actual against
~$7.58 tracked, an understatement of roughly 43%, most of it storage and public
IP hours attributed to machines the portal reported as deallocated.

Azure resources therefore divide into **stop-to-stop-billing** and
**delete-to-stop-billing**. This project's primary cost control — VM
deallocation, `POS-016` — reaches only the first class. Bastion, managed disks,
public IP addresses and now Security Copilot capacity all sit in the second.
Security Copilot capacity is a new member of an existing category, not a new
problem.

The consequence is that deletion must be **a planned step with a time on it**,
not an end-of-session habit. `POS-016`'s open REVISIT already says the current
mechanism is operator memory, which is not a control. At $4/hour that gap has a
price for the first time.

## What was corrected

**The source guide's cost escape hatch does not exist in this subscription.** It
offers Azure free-account credit as covering experimentation comfortably, with
the provision-work-delete cycle as the fallback for paid subscriptions.
`POS-058` forecloses the first option here: the $200 credit sits on billing
profile A while every dollar of lab spend bills to profile B, and under a
Microsoft Customer Agreement a credit pays down only its own profile's invoice —
structurally unreachable, recorded `revisit: false`. It also expires
**2026-08-13**, likely before this arc runs.

So the source guide's two paths collapse to one: the provision-work-delete cycle on a
paid subscription. Recorded because this is the first instance of a previously
committed finding **pre-refuting a later guide's advice** rather than being
corrected by one.

## What could not be tested

**The sequence in §1 is scoped to standalone deployments, and whether this
tenant is one is unresolved.** The Security Copilot overview evidence note records the open inclusion question;
this is the third consecutive file written against it. The capacity-first
ordering is documented for provisioned deployments and is carried here as
conditional, not asserted for this environment. If inclusion proves active, an
unmodifiable Default capacity already exists, no provisioning step applies, and
none of the three unpaid Copilot guides requires a withdrawal — they were written conditionally
because the condition is genuinely open.

**Operational sharpening, recorded before the paid hour.** The source guide advises
deleting the capacity resource in the same hour it was created. Against the
hourly-block rule (`docs/evidence-notes/security-compute-units-capacity.md`) the real target is: finish inside one clock hour,
or buy the second knowingly at $4. Given three guides to execute and a
documentation pace that captures live, one hour is unlikely. The plan is
**two clock hours, $8, against a $10 ceiling**, overage capped at zero, with
deletion timed before the third boundary rather than "the same hour," and no
delete-and-retry inside an hour.

## Cost

$0. Nothing was provisioned.

This closes the unpaid run. Lab 20's paid run opens the meter.
