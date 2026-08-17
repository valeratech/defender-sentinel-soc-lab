---
title: Shaping output — project, sort, datetime, string operators — concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide gives the case-insensitivity of contains/startswith/endswith/has and illustrates the consequence with startswith '10.1' also matching 10.10.x.x - calling it a subtle wrong answer. The same mechanism produces a total inversion, not a subtle one, when the search term is a substring of its own negation - see divergence 208, where contains matched 100 percent of rows."
---

# Shaping output

Concept only.

The walkthrough documents the mechanism behind divergence 208 and the mild form of its
consequence. The severe form — a negated value matching the term it negates, at
100% of rows — was measured here rather than published.

Also worth noting the source guide's `format_datetime()` returns-a-string caveat as a
third instance of a pattern seen twice elsewhere in one day: `LogonType` declared
`string` while holding a JSON array, and `Latitude`/`Longitude` declared `string`
on `EntraIdSignInEvents`. The declared type is not the semantics.
