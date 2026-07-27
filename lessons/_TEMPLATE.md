---
module: NN
title: Short module title
section: Course section name
verdict: lab | concept | mixed
date: YYYY-MM-DD
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections: []
---

# Module NN — Title

> One or two sentences. What this module turned out to be about, as distinct
> from what it was nominally about.

## What was configured

What actually changed in the tenant. **Often nothing** — most modules are reads,
and "nothing was configured" is a finding when the module looked like it should
have produced something.

## What was established

The findings, each pointing at where it authoritatively lives. Cross-reference;
do not restate. If a paragraph here could replace reading the lab, it is too long.

## What was corrected

Claims that shipped and were disproved. Mirror each into the `corrections:`
frontmatter list so it reaches the index.

## What could not be tested

Foreclosed by cost, by the tenant clock, or by n=1 — and *which*, since those
are different limitations. Distinguish "not tested" from "cannot be tested here."

## Cost

Money, and the wall-clock that money did not buy.
