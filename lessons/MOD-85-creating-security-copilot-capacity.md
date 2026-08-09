---
module: 85
title: Creating a Security Copilot capacity
section: Configure Sentinel / automation
verdict: lab
date: 2026-08-09
artifacts:
  labs: ["20"]
  posture: ["POS-087", "POS-088", "POS-089"]
  divergences: [154, 155, 163, 164, 166, 167]
  kql: []
corrections:
  - "P20-2 withdrawn. The blade renders `Microsoft Security compute capacities` in sentence case, not the Title Case used by the guide and by Microsoft's own documentation."
  - "The guide's example capacity name `copilot-demo` is invalid. The field accepts lowercase letters and numbers only - no hyphens, no spaces."
  - "The guide instructs picking the closest capacity region. `Capacity region` renders as static text with no control, while ARM accepts `location` as a parameter - the platform allows the choice, the portal does not expose it."
---

# Module 85 — Creating a Security Copilot capacity

> The module the meter starts on. Its real content is not the create flow but
> what the create flow **defaults to**, and how far the labels drift between
> the form, the review pane, and the payload actually submitted.

## What was configured

Capacity `copilotlab` — 1 SCU, resource group `rg-copilot-lab` (dedicated,
created empty in advance), prompt evaluation location **US**, cross-geo
compute **not allowed**, overage **limited to 0**, capacity region **East US**
(not selectable). Provisioned 11:00:07 PDT, deleted 11:23 the same clock hour.

Full record in `labs/20-security-copilot/README.md`.

## What was established

**The defaults are the module.** `Enable Overage Capacity` ships **on**, set to
`Allow Unlimited Overage Capacity` — unbounded spend, below a cost estimate
that describes only the provisioned $4. The residency checkbox is labelled
*recommended for optimal performance*. The resource group field defaults to the
alphabetically first group in the subscription, which in this tenant is
`NetworkWatcherRG`.

**Overage has no off.** The toggle will not disable. ARM explains why: the
schema carries `overageState` and `overageAmount` with no `Disabled` value.
Zero is `state: Limited, amount: 0`. The accurate sentence is *bounded*, not
*off* (`POS-087`).

**`View automation template` is the only surface not subject to relabelling.**
The residency control appears as *allow Copilot to evaluate prompts anywhere in
the world* on Basics, `Cross-region compute: Not allowed` on Review, and
`crossGeoCompute: "NotAllowed"` in ARM. Only the third is submitted. ARM also
shows `geo` and `location` as **separate parameters**, which is why the static
`Capacity region` is a portal decision rather than a platform constraint.

**Capacity and workspace are two resources in two portals**, bound by an
explicit selection step — which is the mechanism behind the workspace surviving
the capacity's deletion (module 88).

**$4 × 730 = $2,920.** The estimate uses the average-month convention, not 720
hours.

## What was corrected

Three, listed in frontmatter: the blade's casing (P20-2 withdrawn), the guide's
invalid example name, and the unselectable capacity region.

## What could not be tested

Whether the M365 E5 **inclusion** path renders this flow differently. Modules
82–84 recorded the question as open; Lab 20 resolved it for **this** tenant —
`Showing 1 - 0 of 0` on an unfiltered read, no Message center notice, no
in-product banner. A trial E5 does not satisfy the *paid licence* formula here.
That is one tenant on one date, not a general finding, and the rollout is
phased.

## Cost

1 provisioned SCU for one clock hour. **$4 inferred, not invoiced** — cost
analysis reported nothing on the day (`P20-11` open, `POS-087`).
