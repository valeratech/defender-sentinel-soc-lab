---
module: 106
title: Hunts — a control-plane container, and a metrics bar on the wrong tab
section: Detect threats by using the Microsoft Sentinel platform
verdict: lab
date: 2026-08-14
artifacts:
  labs: ["26"]
  posture: []
  divergences: []
  kql: []
corrections:
  - "P106-3 predicted the metrics bar would be absent because no hunts existed, and that creating one would materialise it. Creating a hunt did not. The bar exists on the `Queries` tab, not the `Hunts` tab - the location clause was falsified as framed, not the existence clause. `Livestream Results` holds a counter slot on that bar for a feature the product has retired."
  - "The guide describes creating a hunt and then discusses bookmarks as though they hang off query results generally. It never states that a hunt is a container opened by clicking its name, with its own Queries, Bookmarks, and Entities tabs. That step is not discoverable from the guide."
---

# MOD-106 — Hunts

> A hunt is not a query and not a saved search. It is a **container** with its own
> scoped populations — and the page that describes it never says you open it by
> clicking its name.

## What was configured

One hunt: `LAB-Hunt-Failed-Signin-Spike`, status `New`, hypothesis `Unknown`,
owner unset. Deleted at teardown 2026-08-16 21:31 PDT. Full record in **Lab 26**.

## What was established

**A hunt writes nothing to the workspace.** No `Hunt` table exists; the only
match on `hunt` in Tables is `HuntingBookmark`. Control-plane only, no ingestion,
no billing. This distinguishes it cleanly from the TI object, which was marked
billable at 786 bytes.

**Hunt-scoped and workspace-scoped are separate populations.** The hunt's own
`Queries` tab reads "No queries were found" while the main Queries tab holds 396.
The page states the rule outright: queries in the hunt tab "are not visible on the
overall Hunting queries tab."

**The `Hunts` tab is still Preview**, eight days after `docs/navigation.md` line
39 recorded it. The marker is on the tab, not the page — which is why the guide's
navigation line omits it.

**Livestream is retired but still counted.** No `Live stream` tab exists;
`Livestream Results` holds a metric slot reading 0 on the Queries tab.

**395 hunting queries ship by default, 57 active**, with no solution installed.
Set against MOD-105's finding that the claimed 27 TI analytics-rule templates do
not exist here, two content types provision on entirely different terms.

**Status ordering is not a workflow.** New → Active → Closed, then Backlog and
Approved trailing after Closed. Both of the trailing values precede Active in any
real process. Same trap as the ATT&CK matrix's column ordering.

## What was corrected

See `corrections:`. The metrics bar exists on a sibling tab, and the guide omits
the step that opens a hunt.

## What could not be tested

Whether the metrics bar populates — `validated hypotheses`, `new incidents`,
`new analytic rules` — since the hunt's hypothesis was never moved off `Unknown`
and no rule or incident was created from it.

## Cost

$0. Metadata object; query execution is not billed.
