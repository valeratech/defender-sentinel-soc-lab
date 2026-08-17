---
title: summarize, time filtering, extend and take — concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide's note that the column is TimeGenerated for Log Analytics and Timestamp for advanced hunting repeats the framing corrected in MOD-96: EntraIdSignInEvents carries both, identical."
---

# summarize, time filtering, extend and take

Concept only. Language mechanics.

Two properties worth carrying into predictions rather than recording as findings:
`dcount()` is approximate by design, and `count_distinct()` is the exact form —
so any future claim resting on a distinct count uses the latter. And `take` is
unordered, which is safe only when it follows a `summarize` or `sort`; the
queries in `docs/evidence-notes/kql-fundamentals-and-surfaces.md` are clean on this because every `take` ran after ordering.
