---
module: 88
title: Tearing down Security Copilot capacity
section: Configure Sentinel / automation
verdict: lab
date: 2026-08-09
artifacts:
  labs: ["20"]
  posture: ["POS-087"]
  divergences: [157, 162, 165, 167]
  kql: []
corrections:
  - "P20-8 wrong. Predicted session consumption well under 1 SCU-hour; measured 1.5 units against 1 provisioned."
  - "P20-9 wrong. Predicted the usage dashboard would lag; it read near-live, within a minute of the session."
  - "Withdrawn: the claim that the unlimited-overage default would have billed $6 for the 0.5-unit excess. The at-capacity tooltip states Microsoft absorbs the extra units needed to finish an in-flight operation, so what the cap prevented on this session is unknown. The MOD-83 decision to bound overage stands on its own reasoning, not on this evidence."
  - "P20-11 remains OPEN, not confirmed. The $4 figure is inferred from the billing model and the 11:00-12:00 clock-hour window; cost analysis reported nothing on the day. POS-016 was forced by a 43% gap between tracked and actual spend, so the amount is not asserted until an invoice confirms it."
---

# Module 88 — Tearing down the capacity

> The module that closes the meter, and the last of Section 7. Its stated
> content is one delete operation. What it actually demonstrates is that the
> **evidence of consumption outlives the consuming resource**, and that the
> warning which would have been useful only becomes readable once it can no
> longer be acted on.

## What was configured

`rg-copilot-lab` deleted 11:23 PDT, inside the 11:00–12:00 clock-hour block
the capacity was provisioned in. Confirmed: `Showing 1 - 0 of 0` on the
capacities blade, resource group gone.

## What was established

**The dedicated resource group is a safety interlock, not tidiness.** This
module tears down by typing a group name into a confirm dialog. The Create form
had defaulted the resource group to the alphabetically first group in the
subscription, and the Copilot group sits **directly adjacent** to the group
holding this project's lab infrastructure in that same alphabetised list. Had
capacity landed in a shared group, following this module
literally would have destroyed lab infrastructure irreversibly. The dialog's
typed-name confirmation is the only thing standing between the two.

The dialog does state *all dependent resources, including hidden types, are
shown* — 1 — so the Resources list was not a filtered undercount.

**Deletion is not immediately visible.** The confirmation dialog remained open
showing zero resources where it had shown one. Read as propagation and resolved
by re-reading the capacities blade rather than clicking `Delete` again on a
stale dialog. The **two-read rule** applied to a deletion, and propagation
appearing once more in a project where it spans twelve days to minutes.

**Billing evidence outlives the billed resource.** Guide 62 claims the
workspace persists. It does — and so do the full session transcript and the
usage-monitoring row showing 1.5 units. That is the inverse of `POS-084`, where
run history retained a credential nobody wanted kept; here the record that
survives is the one you want.

**The throttle condition is retrospective.** A warning triangle sat on the
capacity tab during the session with no tooltip and no target. Its explanation —
*All available units used. We won't charge you for the extra units it took to
finish your last operation* — and the red overrun segment on the chart both
became readable **after** deletion. Nothing warned at 1.0 while there was still
a decision to make.

## What was corrected

Four, in frontmatter: two wrong predictions, one withdrawn claim of my own
about what the overage cap prevented, and `P20-11` held open rather than
declared.

## What could not be tested

**The invoice.** Cost analysis at billing-account scope reported `No cost
reported during this period` with `ACTUAL COST --` on the day. The billed
amount is inferred, not measured, and a second read is owed.

**Whether an orphaned workspace persists indefinitely.** It survived the
capacity by hours. Whether Microsoft reaps it on a timer is unknown, which is
why the session evidence was captured while it existed rather than deferred.

## Cost

Deletion inside the provisioning clock hour: **one unit**. Section 7 closes
here — module 88 is its last.
