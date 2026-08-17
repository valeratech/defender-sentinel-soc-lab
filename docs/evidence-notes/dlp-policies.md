---
title: Implement data loss prevention policies
date: 2026-08-03
artifacts:
  labs: ["14"]
  posture: [POS-059, POS-060, POS-061, POS-062]
  divergences: [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82]
  kql: []
corrections:
  - "The ABA-checksum assumption carried in from session notes was contradicted by the SIT documentation (Checksum: No); withdrawn, and the test design routed around it with a published institutional routing number."
  - "No Low confidence tier was predicted for U.S. Bank Account Number (the published definition has a single 75-level pattern); the live Test panel returned one. Recorded as a docs-vs-product divergence with the mechanism unasserted."
---

# DLP: What the Defaults Are, and What the Evidence Survives

> The policy was deliberately all defaults, which made the wizard itself the
> instrument: what does Microsoft ship when nobody decides anything? Then Phase
> D asked the sharper question — what happens to detection *evidence* when the
> content moves, and when the operator presses the one button that looks like a
> refresh.

## What was configured

One DLP policy from the U.S. Financial Data template, simulation mode, every
wizard value a template default except the surface choice, the template, and
the name. It landed at priority 4 behind four pre-seeded policies stamped in
the tenant-provisioning window — three of them enforcing, none of them chosen.
`POS-059` records that inheritance; `POS-062` records the policy and its
measured outcome.

## What the defaults said

The template is a notify-and-report posture wearing an enforcement product's
name: tips, threshold alerts, and incident reports all on; the only enforcement
action off; the entire device-action section off while the Devices location
ships checked. Scope, instrumentation, and mode support turned out to be three
independent lists — two locations were enabled, non-functional, *and* excluded
by simulation, disclosed only at the final wizard step (rows 64, 76).

Mixed confidence inside one template (row 65), a two-rule compilation the guide
presents as one detection (row 66), and a 1–9 instance range tiling with a ≥10
threshold explained why: the "template" is several tuning decisions under one
name, and the SIT Test function — the highest-information surface in the walkthrough
— showed the confidence tiers as cumulative gates, every qualifying tier
reported at once.

## What Phase D measured

Detection worked, and precisely: the pre-validated payload matched at rest
(including content uploaded before activation) and in transit, with the exact
predicted per-SIT split — one value legitimately counted by two SITs. The
pipeline decomposed cleanly: evaluation at the send minute, report indexing
8–12 minutes behind. The confident zero in between was measured at both ends
this time instead of being fallen into (row 77).

Then the evidence lifecycle (row 82): delete the matched file and the report
keeps claiming it — a historical record, not a live view. Press **Restart the
simulation** and the record rebuilds destructively: at-rest results regenerate
from what still exists, and **real-time history is wiped unrecoverably**,
because transit events do not replay. Two matches became zero behind a
confirmation dialog that names no consequences (row 78). The third send proved
the pipeline survived its own history's destruction.

## The surfaces disagreed to the end

Five renderings of "how many matches exist," four timestamp conventions in one
solution (row 81), three names for one location, and — in the same minute — an
Items grid saying 1 while the overview export said 0 (row 79). Global
Administrator could build the policy, run the simulation, and read the match,
but not the matched values (row 80) — the fourth measured GA-insufficiency,
against `POS-061`'s seventy empty role groups.

## What transfers

Test content against the SIT before trusting a policy report; the Test function
answers in seconds what activation windows answer in hours. Treat a simulation
report as an evaluation log with a demolition button attached. And when a
surface offers "restart," ask what it does to history before assuming it means
refresh — nothing on the screen will tell you.
