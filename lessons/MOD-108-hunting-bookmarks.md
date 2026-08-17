---
module: 108
title: Hunting bookmarks — the documented path routes to the one surface that cannot bookmark
section: Detect threats by using the Microsoft Sentinel platform
verdict: lab
date: 2026-08-14
artifacts:
  labs: ["26"]
  posture: []
  divergences: [217, 219]
  kql: []
corrections:
  - "P108-2 registered zero rows on a first query within 60 seconds of the trigger. Claude did not supply the query until several minutes after the sign-ins were reported, so the registered window had already elapsed. Falsified on the letter; the latency FLOOR is unmeasured. Second instance of the same timing error as P26-3."
  - "P108-1 scored Confirmed on its terms - six rows, all 50126, no lockout - but its PREMISE is questioned. Six rows carry three distinct timestamps, each duplicated at identical millisecond precision. See below."
  - "The guide states entity and MITRE mappings 'default to those of the hunting query that produced the results' unconditionally. Observed under MOD-110: from a raw Logs query they arrive EMPTY. The inheritance is conditional on the producing query being a mapped hunting query. Observable only because the hunting path was broken."
---

# MOD-108 — Hunting bookmarks

> A module about bookmarks in which no bookmark could be created by the
> documented route. That is the finding, and it is worth more than a filled-in
> form would have been.

## What was configured

The `LAB-Hunt-Query-Failed-Signin-Spike` query cloned into
`LAB-Hunt-Failed-Signin-Spike`, moving `Content` to `1 Queries`. Six deliberate
failed sign-ins as `labuser` at 20:28 PDT to produce a non-empty result set. Full
record in **Lab 26**.

## What was established

**`count()` over `SigninLogs` counts records, not sign-in attempts.** Six rows
from six reported attempts carry **three distinct timestamps**, each duplicated
at identical millisecond precision, with distinct `Id` per row differing in one
byte of the node segment and a single shared `CorrelationId` across all six.
`dcount(CorrelationId)` returns 1 and is useless as an attempt count.

**The doubling propagates end to end** — rows → rule threshold → alert →
incident title (`LAB-Bruteforce: 6 failed sign-ins to Azure Portal`) → the
incident's own time range, where `First activity` and `Last activity` are
identical for an event spanning 21 seconds.

**This reaches the committed record as a hypothesis, not a finding.** `DET-004`
states "seven deliberate failed sign-ins… `ResultType 50126` on all seven" —
seven *rows*. `POS-046` records suppression added after "12 alerts from one
event"; twelve is six doubled. Both may be the same phenomenon from different
angles. Needs `dcount(CreatedDateTime)` against the July data before anything is
asserted. `CreatedDateTime` is the field to group on: it reads
`03:28:49.4768815Z` where `TimeGenerated` reads `03:29:53.7026258Z`, 64 seconds
apart on one record.

**The bookmark path is unreachable from hunting.** `View results` routes to
**Advanced hunting** from both the main Queries tab and from inside a hunt.
Confirmed twice, on separated sittings 36 hours apart, in a fresh browser session.
With a result row selected the toolbar offers `Link to incident` and
`Take actions` and no bookmark control. The hunt's Bookmarks tab offers no
creation control either, and its own empty state diagrams QUERY → LOG ANALYTICS
and instructs the user to click "View query results… to view the results in Log
Analytics." Divergence 217.

**Bookmarks are not broken** — see MOD-110. Reached via Azure Logs from Sentinel's
Search page, the control is present and functional. The defect is a routing fault
in the hunting path specifically.

**`DET-004` fired and produced an incident**, first firing since 8 August, which
re-validates `POS-046` by observation. End-to-end latency `03:29:32.821Z` →
`03:37:29.5Z`, just under 8 minutes on a 5-minute schedule.

**Clone semantics confirmed by lifecycle.** Deleting the hunt removed the clone
and left the original query standing — counter unchanged at 58/396 until the
original was deleted separately.

## What was corrected

See `corrections:`. A repeat of the P26-3 timing error, a prediction whose premise
is now in question, and a guide claim that is conditional rather than absolute.

## What could not be tested

Whether the six reported attempts were three logged twice or six with three
logged — only the operator's recollection of click spacing separates them, and it
was not recorded at the time.

## Cost

$0. Six sign-in events is negligible ingestion.
