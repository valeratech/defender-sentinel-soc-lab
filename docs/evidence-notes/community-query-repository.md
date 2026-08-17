---
title: The Azure-Sentinel community query repository — concept
date: 2026-08-12
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections:
  - "Guide does not mention that the repository's default branch is master, not main. Verified - master/README.md returns 200, main/README.md returns 404. A raw URL or branch-specific clone built on the modern convention fails, and a 404 on a raw file reads as 'that query does not exist' rather than 'wrong branch'."
  - "Repository identity verified - the README describes itself as the unified Microsoft Sentinel and Microsoft 365 Defender repository, and the folder taxonomy named in the guide is present. The specific Hunting Queries path and the YAML field set were NOT verified; a guessed filename returned 404 and the GitHub API rate-limited the working environment. Carried from source."
---

# The Azure-Sentinel community query repository

Concept only.

One consequence specific to this tenant. The source guide advises reading
`requiredDataConnectors` before running a community query, because a query for a
table you do not ingest returns nothing and looks exactly like a clean
environment.

That is not hypothetical here. Any query in the `Hunting Queries/Microsoft 365
Defender` set depending on `CloudAppEvents` returns zero rows in this tenant and
reads as *no cloud app threats* — while the actual cause is the unchecked
connector component recorded in `POS-068`.
