---
module: 97
title: Practice environments and AI-assisted KQL — concept
section: Detect threats by using Microsoft Defender XDR
verdict: concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide states the Log Analytics demo environment result cap is 30,000 rows; MOD-98 states the portal caps at 500,000; Microsoft's advanced hunting documentation gives 100,000 for advanced hunting (advanced-hunting-overview, ms.date 05/12/2026). These are three different surfaces rather than a contradiction, but no single number should be quoted without naming which surface it governs."
  - "aka.ms/lademo, the demo workspace's table availability, and the 25-tab limit were not verified - the host is unreachable from the working environment. Carried from source."
---

# MOD-97 — Practice environments and AI-assisted KQL

Concept only. The demo workspace is not this tenant and nothing here is testable
against it.

Worth noting that the module's two warnings both had live instances the same day
this guide was read: an empty result being ambiguous between a wrong query and
absent data (resolved for `CloudAppEvents` in MOD-96), and generated KQL
referencing plausible column names that do not exist (`ResultType`, corrected by
`getschema` — recorded in MOD-96's corrections).

The repository already held this calibration from the Security Copilot work:
generated output is a draft to validate. This module arrives at the same place
from a different direction and adds nothing to the record.
