---
module: 79
title: Create and configure automation rules
section: Configure Sentinel / automation
verdict: lab
date: 2026-08-06
artifacts:
  labs: ["18"]
  posture: [POS-075, POS-076]
  divergences: [123, 124, 125, 126, 127, 128, 129, 130, 131]
  kql: []
corrections: []
---

# Module 79 — Create and configure automation rules

> Build an automation rule. Built two, through two different doors, to watch
> the doors differ — then triggered both on one incident and read the result
> at millisecond resolution.

## What was configured

Two Standard automation rules in `law-soc-lab` (`POS-075`): Order 1 tags
DET-004 incidents, Order 2 assigns them to the analyst. Both Enabled,
Indefinite. The tenant had zero automation rules before this (P79-1).

## What was established

The two-entry-point thesis, observed from both sides: the Automation page's
builder arrives empty and free (enumerating three analytic rules including
Fusion, which the Analytics list omits); the analytics-rule path arrives
locked to a rename-safe `Current rule` token (rows 126, 127). The
Enhanced/Standard split as two engines the guide never names (row 123). The
trigger default resolved across four surfaces (row 125). Serial execution,
ordering, per-rule attribution, ~11 s automation latency, and non-retroactivity
all confirmed against a live trigger (`POS-076`, row 130) — including one
audit-only anomaly: a second-in-order rule logging the first rule's tag under
its own identity, idempotent and invisible outside the millisecond log. Plus
three surfaces still disagreeing about the rule's suppression, grouping, and
priority score (rows 128, 129, 131).

## What was corrected

Nothing shipped and disproved. Rule A's first-attempt-as-Enhanced was a build
detour, not a repo correction — recorded in Lab 18 §6 as the finding that
surfaced the Enhanced/Standard split.

## What could not be tested

Whether the `Change status → Closed` action carries a classification
sub-picker (the guide's noise-suppression pattern) — not built, since neither
rule closes incidents. The playbook action (`Run Logic Apps playbook`) and its
Automation Contributor dependency are G57. The priority-score mechanism (1 vs
3 vs 72 for one detection) remains unchased across two labs.
