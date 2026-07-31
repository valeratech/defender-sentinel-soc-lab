---
module: 60
title: Query Microsoft Sentinel data by using ASIM parsers
section: Configure Detections
verdict: concept
date: 2026-07-31
artifacts:
  labs: []
  posture: []
  divergences: [40]
  kql: []
corrections: []
---

# Module 60 — ASIM

> Concept, with one free query that turned a documentation claim into a
> measurement.

## What was configured

Nothing. ASIM parsers are KQL functions; running them costs nothing, and none
were installed.

## What was established

**ASIM is documented as built-in and is not present until installed.** The
guide describes normalized schemas that "ship" and "recognize common event types
across platforms without you writing any mapping syntax." Run against this
workspace:

```
imAuthentication
| where TimeGenerated > ago(24h)
```

→ `Failed to resolve table or column expression named 'imAuthentication'`.

ASIM parsers are workspace **content**, delivered through Content Hub solutions.
No solution has ever been installed here — every connector came from the connector
gallery — so no parser functions exist. Not a licensing gap and not a data gap:
the fourteen failed sign-ins from Lab 11 are perfectly normalisable, there is
simply no function to normalise them with. `POS-011`'s shape again — a capability
described as built-in, unreachable until a second step nobody mentions
(divergence row 40).

**The Splunk parallel holds, with an acronym trap.** ASIM is Sentinel's CIM: same
problem, same solution, content written against a schema rather than per source.
But the guide's "OSSEM Common Information Model" is the Open Source Security
Events Metadata project — **not Splunk's CIM**. Two unrelated standards sharing
three letters.

Where the mechanics diverge: Splunk normalises through props/transforms and
tags supplied by TAs, accelerated via data models and `tstats`; ASIM normalises
through KQL functions called by name, query-time by default, with ingest-time
normalisation via DCR transformations as the acceleration path.

## What could not be tested

**Whether installing the ASIM solution makes `imAuthentication` resolve.** Free to
install, but it is another content deployment on a tenant with days left, and the
finding — *documented as built-in, absent in practice* — is the useful part.
*(not attempted)*

**Ingest-time normalisation**, which would need the Lab 07 DCR and therefore a
running VM.

## Cost

Zero.
