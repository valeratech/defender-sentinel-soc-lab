---
module: 102
title: Advanced hunting in the Defender portal — concept, verified against current docs
section: Detect threats by using Microsoft Defender XDR
verdict: concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide's service limits verified exact against advanced-hunting-overview (ms.date 05/12/2026): 30-day date range for Defender data unless streamed through Sentinel, 100,000-row result set, 10-minute timeout, 64 MB results size, CPU metered every 15 minutes with queries blocked at 100% until the next cycle."
  - "Guide's boolean-representation change (numeric 1/0 to textual True/False on 2026-02-25) and the AADSignInEventsBeta to EntraIdSignInEvents replacement both verified against advanced-hunting-schema-changes (ms.date 06/03/2026). One correction: the guide implies a general 30-day grace pattern, but that document gives 2025-12-09 as the specific removal date for the legacy tables. They are long gone, not lingering."
---

# MOD-102 — Advanced hunting in the Defender portal

Concept, and the most consequential module in the section for work already
designed.

Two constraints land directly on **MOD-95 / Lab 25**:

- **The 30-day boundary is hard.** Advanced hunting queries at most 30 days of
  Defender data unless streamed through Sentinel. Any comparison between
  `MicrosoftGraphActivityLogs` (retention-governed in the workspace) and
  `GraphAPIAuditEvents` (30 days) that reaches further back can only be answered
  by one side.
- **In-query time filters change which data is queried.** When a query sets its
  own time filter, streamed Sentinel data is used; to query all Defender data
  across the full 30 days the time-range picker is used instead. MOD-95's
  latency measurement is precisely an in-query time comparison across two
  surfaces, so its predeclared method must state picker-versus-in-query
  explicitly.

The module's four causes for an empty table in a lab tenant — no activity, not
licensed, outside retention, not onboarded — is the taxonomy MOD-96 walked
through for `CloudAppEvents`. The answer turned out to be a fifth cause not on
the list: a connector component not selected.
