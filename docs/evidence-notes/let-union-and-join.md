---
title: let, union and join — concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide's union section states that inputs need not share schemas and that missing columns appear empty. It does not address a source contributing zero rows, which vanishes from the result entirely rather than rendering a zero - see divergence 209."
---

# let, union and join

Concept only.

One constraint carried forward to **Lab 25**, where the designed
experiment correlates `MicrosoftGraphActivityLogs` (Log Analytics) with
`GraphAPIAuditEvents` (advanced hunting):

KQL's `join` defaults to `kind=innerunique`, which deduplicates the left side's
join keys before matching, and which left row survives is not guaranteed. An
unqualified join in that experiment could silently drop duplicate-request
evidence the experiment exists to observe. **Every join in Lab 25 carries an
explicit `kind=`.** `leftanti` is also the natural shape for that lab's
non-retroactivity prediction — rows present on one surface and absent on the
other.
