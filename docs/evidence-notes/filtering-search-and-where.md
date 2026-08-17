---
title: Filtering with search and where — concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide states 4624 is audited by default on Windows machines. True of the OS default, but what reaches this tenant's SecurityEvent table is governed by the DCR collection tier set in Lab 07, not by the OS default. Any prediction about event counts here must be made against the DCR, not the documentation."
---

# Filtering with search and where

Concept only.

Two items batched for a later execution pass, both pure reads against this
tenant's own workspace:

- **`Show tables with no data`.** The guide notes the Log Analytics table list
  hides empty tables by default, with the setting behind the `...` context menu.
  That is the same shape as divergence 209 on a different surface — an empty
  thing omitted rather than shown as empty, so absence from the list cannot
  distinguish "does not exist" from "exists and is empty."
- **`SecurityEvent` `AccountType` split.** The guide lands on "4624 does not mean
  a human logged in." `docs/evidence-notes/kql-fundamentals-and-surfaces.md` measured that principle on Entra sign-ins
  (97.74% non-interactive) and `docs/evidence-notes/purview-audit-log-search.md` measured it on the Purview audit log. The
  Windows security event log would be a third measured surface for one
  principle.
