---
title: Archived log data — a guide whose subject does not exist in this tenant
date: 2026-08-15
artifacts:
  labs: []
  posture: [POS-102, POS-103]
  divergences: [220]
  kql: []
corrections:
  - "P109-4 predicted the restore table picker would offer no eligible table. It offers 14, none of which has a byte in long-term retention. The picker does not filter on whether archived data exists."
  - "Claude estimated the earliest telemetry expiry from an incident dated 2026-07-18 and put the retention deadline at 2026-08-17. The Tables ingestion chart's x-axis starts 2026-07-24 on a 30-day window, which would put it near 2026-08-23. Neither was measured; `Last data received` per table is the authoritative field and was not read for the oldest table."
  - "POS-102 and POS-103 record workspace-level settings and are cited to Lab 04 (labs/04-sentinel-workspace/), which already owns POS-032. They are not artifacts of Lab 25 or Lab 26; citing them there would satisfy check-lab-coverage.py dishonestly. Whether Lab 04 is the right long-term owner is audit material."
---

# Archived log data

> Long-term retention is not a destination. It is the gap between a table's
> interactive retention and its total retention — and in this workspace that gap
> is zero, so the source guide's subject does not exist.

## What was configured

Nothing. Scoped reads-only by operator decision, and subsequently made permanent:
the tenant and subscription are being scrapped, so raising retention has no
consumer. Recorded as a decision, not an unrun task.

## What was established

**The archive gap is zero, workspace-wide.** Every table reads Analytics 30 /
Total 30. Data is deleted at 30 days rather than aged into long-term retention.
The `Manage <table>` panel states the mechanism outright: *"This XDR table is
automatically integrated with the data lake once retention is increased from the
default 30-day period."* Nothing enters long-term retention, so
search-over-archive and restore cannot be demonstrated here at any future date.
Recorded as `POS-102`.

**No plan selector exists.** `Analytics tier` is a fixed heading, not a dropdown.
The only two controls are `Analytics retention` (9 values to 2 years) and
`Total retention` (19 values to 12 years). Total renders relative to Analytics —
`Same as Analytics retention (30 days)` — which is the tier model made visible.
Neither `Basic` nor `Auxiliary` is offered.

**The restore picker offers 14 tables with no archived data**, and defaults to a
7-day range fully inside interactive retention — free to query in Logs. The
default restore, accepted as offered, bills to hydrate data already available.
Divergence 220.

**The 14 appear to be tables that actually hold data**, against 192 total. A free
inventory of real workspace contents, and independent corroboration that
`HuntingBookmark` was empty at that point.

**Restore limits confirmed exactly, five for five:** 2-day minimum, 60 TB per
restore, 4 restores per table per week, 2 concurrent per workspace, 1 active per
table. Charges stated as **per day of data restored**; no minimum floor appears
in the panel, contrary to the guide.

**The data lake is provisioned and inert.** `Data lake tier: 0`,
`Lake tier: 0 KB`, while tables read `Data lake: Integrated`. Capability wired,
activation conditional on a retention increase that has been declined.
Recorded as `POS-103`.

**The Search page still says "archive."** *"Search across standard, basic, and
archive logs"* — the terminology the guide states has been superseded by
"long-term retention."

## What was corrected

See `corrections:`. A prediction falsified by a picker that does not filter, a
retention deadline estimated from the wrong field, and the ownership of the two
posture entries this walkthrough produced.

## What could not be tested

Everything the source guide is nominally about. Search over long-term retention and
restore both require archived data, and this workspace has none and now never
will.

## Cost

$0. All reads. No restore initiated — the one operation here that bills
continuously while the restored table exists.
