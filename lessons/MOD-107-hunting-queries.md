---
module: 107
title: Hunting queries — entity mapping is compiled into the KQL, and a form that contradicts its guide
section: Detect threats by using the Microsoft Sentinel platform
verdict: lab
date: 2026-08-14
artifacts:
  labs: ["26"]
  posture: []
  divergences: [218]
  kql: []
corrections:
  - "The guide's worked query opens with `| where TimeGenerated >= ago(1h)`. The creation form's own banner forbids it: 'Do not use fixed time ranges, either directly or in a function, in your query. Otherwise, we cannot show changes in query results over time.' Windowing belongs to the page scope control; the Results delta columns depend on it. The query was authored without a time filter and P107-5 amended on the record before the read, not after."
  - "Claude asked for the full tactics list to be expanded and photographed, which placed the dropdown over the panel footer. That is one of two candidate causes for the inert `Create` observed immediately afterward. The instruction may have created the condition it then diagnosed."
---

# MOD-107 — Hunting queries

> The interesting part is not the KQL. It is that entity mapping is **rewritten
> into the query text**, and that the form forbids the time filter the guide
> leads with.

## What was configured

One hunting query: `LAB-Hunt-Query-Failed-Signin-Spike`, `SigninLogs`, threshold
`> 5`, entity mapping `Account` / `FullName` / `UserPrincipalName`, tactic
Credential Access, technique T1110 — deliberately identical to `DET-004` so the
two objects are comparable. Deleted at teardown 2026-08-16. Full record in
**Lab 26**.

## What was established

**Entity mapping compiles into the query.** The stored KQL carries
`| extend Account_0_FullName = UserPrincipalName`, a line never authored. The
generated column name encodes entity type, index, and identifier. Stored query
text ≠ authored query text, which matters for anyone diffing or exporting these.

**The tactics picker spans multiple ATT&CK matrices, unlabelled.** 17 tactics,
not 14 — `Evasion`, `Impair Process Control`, `Inhibit Response Function` are
ATT&CK for ICS. Inside Credential Access, T1414/T1417/T1453/T1517 are ATT&CK for
Mobile, and `Input Capture` appears twice under different IDs. Against MOD-104's
250 techniques / 14 tactics at a 13-matrix filter, two surfaces in one product
offer different tactic universes with no indication of which is which.

**A named zero.** `Results 0` with the run counter moving `0/0` → `0/1`. Because
`POS-034` records the connector and `DET-004` fired on this exact logic, this
repo can state the zero means *no qualifying activity* — not a missing table, not
a missing connector, not a syntax fault. The surface distinguishes
ran-and-found-nothing from never-ran: every other row shows `--`.

**`Content source: Custom`** distinguishes editable from read-only content;
`Data sources` was derived from the query text without being declared.

**Unresolved: `Create` inert with no validation feedback.** First attempt ~20:00,
no response, no error text, no write (counters verified in a separate tab).
Second attempt succeeded 20:07. Two variables changed between them — description
re-entered as raw text rather than a markdown-formatted paste, and a hard refresh
with the tactics tree collapsed clear of the footer. Cause not isolated, single
occurrence. **The finding that survives either way: the form rejected silently.**

## What was corrected

See `corrections:`. The guide's worked query violates the form's own instruction,
and one of the two candidate causes for the inert submit was created by my own
instruction.

## What could not be tested

Whether the description content or the overlaid dropdown caused the inert
`Create` — a single-variable retest was available and deliberately not run.

## Cost

$0. Metadata object; query execution is not billed.
