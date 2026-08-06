---
module: 77
title: Investigate and remediate incidents in Microsoft Sentinel
section: Configure Sentinel / incident response
verdict: lab
date: 2026-08-06
artifacts:
  labs: ["17"]
  posture: [POS-071, POS-072, POS-073, POS-074]
  divergences: [109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
  kql: []
corrections:
  - "The RunScript alert's 7 h 37 m gap was written up as correlation latency; the Investigation flyout's Generated-on timestamp showed the alert did not exist until then. XDR detection latency, correlated at birth."
  - "An activity timestamp was read as an auto-resolution timestamp; the real chain is generation + AIR at 13:10 PDT, resolution at 13:23."
  - "A missing comment on the Activities grid was attributed to a pre-seeded filter; the grid was stale and one Refresh reconciled it. Withdrawn before it reached a file."
  - "The unified portal refusing the Responder's write at T+17 min was provisionally framed as a permanent URBAC-only write path; the T+12 h re-read on a fresh token opened the pane and saved the write. Withdrawn; replaced by the bounded read-vs-write propagation finding (row 122)."
---

# Module 77 — Investigate and remediate incidents in Microsoft Sentinel

> Nominally a walkthrough of the incident page and the Manage pane. What it
> turned out to be about: a classification stored under a name the picker
> never shows, an audit trail on a tab the guide doesn't mention, and a role
> whose grant, activation, and honoring turned out to be three separate
> events on three separate clocks.

## What was configured

Incident 1 fully triaged and resolved as *Informational, expected activity —
Security testing* (`POS-071`). Microsoft Sentinel Responder assigned to the
analyst as an **Eligible time-bound** PIM assignment at resource-group scope
(`POS-072`), with MFA registration forced onto the account by the activation
flow (`POS-073`). ID 19 owner-assigned and moved to In Progress by the
analyst under an activated role, once from each portal (`POS-074`).

## What was established

The classification vocabulary split (picker vs display/export vs audit log —
row 109), the six-field Manage pane with comments living on the Activities
tab (row 111), the Activities tab as a per-field audit trail with before/after
values (row 113), comments not advancing the update stamp (row 112), AIR's
verdict-less closures (row 119), asymmetric incident↔alert status propagation
(row 120), pre-seeded filter instances five through seven with the
export-discipline corollary (row 114), and the full role-grant arc — Eligible
by silent default, per-elevation MFA, read and write arriving on different
clocks, a permissions error describing a cache, and clean self-expiry
(row 122). Lab 17 §8 holds the analysis; the rows hold the evidence.

## What was corrected

Four withdrawals, mirrored in the frontmatter. Two were caught by a single
authoritative timestamp, one by a Refresh, and one by the two-read rule
applied to the lab's own headline — the largest claim of the lab did not
survive its second read, and recording that is the lab.

## What could not be tested

Whether the unified Detection Rules pane carries an edit control for an
identity with authoring rights — the analyst's bare toolbar is a description
until the admin-side comparison is read (tracked as *(pending)* in Lab 17).
Whether the T+17 min write refusal was hours-scale propagation or token
staleness — the morning re-read came through a sign-out/in, so the two cannot
be separated here; the bounded window (17 min – 12 h) and the operational
lesson survive either mechanism. Whether a distribution list is *accepted* as
an incident assignee — deliberately not tested, no junk state written.
