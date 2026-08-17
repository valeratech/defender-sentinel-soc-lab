---
title: Searching the audit log — closing the read side of a pipeline opened sixteen days earlier
date: 2026-08-11
artifacts:
  labs: [23]
  posture: [POS-095]
  divergences: [184, 185, 186, 187, 188, 189, 190, 191, 192]
  kql: []
corrections:
  - "Guide presents a single combined 'Workloads / record types' filter. The surface renders Workloads and Record Types as two separate fields, in different columns, and adds a third the guide omits entirely: Activities - operation names."
  - "Guide names the path filter 'File, folder, or site'. It renders as ObjectId (File, folder, or site) — the schema field name, with the friendly description parenthesised."
  - "Guide: the friendly Activities list is the way to select an operation. The list contains identical labels across activity groups and identical labels repeated within one group, and the selected chip drops the group qualifier. It is a display vocabulary, not a query key; Activities - operation names takes the schema string and is what the search actually ran on."
  - "Guide: Search-UnifiedAuditLog is the cmdlet underlying the portal tool, returning the same records. For identical scope it returned 21 rows against the portal's 19. The two extras are the same records emitted twice at different ResultIndex positions, confirmed by identical Identity. No error, no warning: an analyst counting rows overcounts by ten percent."
  - "Guide describes export as taking time. Export is a second asynchronous job with its own progress state, not a slow download, and the Export control remains greyed after the completion banner renders."
  - "Guide implies a submitted search's criteria are lost from the form. The form does reset to defaults on submit, but the completed job restates the full query in a Search Query Information header — which also renders unresolved format tokens {9} {10} {11} {12} in place of the empty optional criteria."
---

# Searching the audit log

> Nominally: run a search. Actually: the first read-back of a pipeline this
> repository enabled on 2026-07-26 and never once consumed — plus a cmdlet that
> returns a wrong row count without erroring, seven renderings of one timestamp,
> and a sign-in record that no human performed.

## What was configured

Nothing. Every action was a read. One search job was created and is retained
30 days; no tenant setting changed and no cost was incurred.

## What was established

**`POS-035`'s read side is closed** (`POS-095`, Lab 23 §7.2). Lab 09 enabled
unified audit ingestion by cmdlet on 2026-07-26 after the portal path failed,
and nothing had ever queried the result. A bounded search over 2026-07-26 →
2026-08-11 for `UserLoggedIn` by one identity returned **19 records**, and
`Get-AdminAuditLogConfig` still read `UnifiedAuditLogIngestionEnabled : True`
sixteen days on. Enabled, still enabled, and demonstrably producing retrievable
records — three claims, one of which had never been tested.

**`UserLoggedIn` does not mean a human logged in** (Lab 23 §7.6,
divergence 191). The record selected for detail carried
`RequestType: OAuth2:Token`,
`UserAgent: Windows-AzureAD-Authentication-Provider/1.0`, and a client IP in
Microsoft address space — a non-interactive token acquisition, rendered in the
results grid as `User logged in`, visually indistinguishable from the
interactive sign-ins in the same result set. This is the direct analogue of the
repository's existing `4624 does not mean a human logged in`, now measured on a
second product and a different log.

**The cmdlet's row count is wrong** (Lab 23 §7.5, divergence 190). Portal
export 19, `Search-UnifiedAuditLog` 21, identical scope and identical bounds.
The sets were diffed rather than estimated: the export is a strict subset, and
both extras are second occurrences of timestamps already present. `Identity`
settles it — the same record GUID at two `ResultIndex` positions (9 and 12; 14
and 17) with `ResultCount 21`. Nineteen distinct records; the cmdlet emits two
of them twice, silently.

**A mid-run count is not a partial answer** (Lab 23 §7.3). `Total results` read
`8` at 77.78% and `19` at completion — not proportional, and `Progress` rendered
exactly 7/9, so the job steps a fixed unit count rather than estimating. Reading
the in-progress figure as the result would have been wrong by more than half.

**One field, three representations, and the portal disagrees with itself**
(divergence 189). `RecordType` renders as the string
`AzureActiveDirectoryStsLogon` in the results grid, as the bare integer `15` in
the record flyout and in the CSV export, and the payload's `Workload` reads
`AzureActiveDirectory`. The flyout agrees with the export; the grid agrees with
the cmdlet. **The Azure AD-era vocabulary is not buried in a payload — it is a
rendered grid column on a 2026 Purview surface**, for a product renamed to
Microsoft Entra ID more than two years ago.

**Seven renderings of one timestamp, three of them unlabelled** (divergence
187). Header `GMT`; grid column `Date (UTC)`; job list `Creation time
(UTC-07:00)`; CSV `2026-08-10T23:27:39.0000000Z ` with a trailing space inside
the quoted value; raw JSON bare ISO with no zone marker at all; cmdlet bare US
locale; flyout labelled `Date (UTC)` over a bare value. All reconcile to the
same instant. **The authoritative object is the only one that never says what
timezone it is in.**

**The friendly-name vocabulary is not a query key** (divergence 188). Two
distinct duplication classes on one surface: identical labels across activity
groups (`User logged in` under both Workplace Analytics and Viva goals) and
identical labels repeated within a single group (Microsoft Fabric rendering
`Logged in to Git provider` twice, adjacent and indistinguishable). Selecting
one drops the group qualifier from the chip, so the field then displays a value
that no longer identifies what was chosen. `Activities - operation names` is the
schema field and is what the search ran on.

**A live production surface leaking format tokens** (divergence 186). The
completed job's `Search Query Information` header renders
`, , {9} {10} {11} {12}` — positional format-string indices standing in for the
empty optional criteria, customer-facing, on a Microsoft security product.

**Labels that do not describe their contents** (divergence 185). The flyout's
`Users` field renders the subject's object GUID; the UPN appears further down as
`UserId`, and the grid's `User` column rendered the UPN. `Item` renders a
well-known first-party application ID under a label that reads as a document.
And the flyout **never names the raw object at all** — the container the CSV
calls `AuditData` has no label on the surface that displays it.

## Confirmed absences

**No Entra sign-in entry was found in the friendly-name list** under the search
strings `user logged`, `sign`, or `logged`. **Its absence is NOT established.**
The list is long and scrollable and cannot be enumerated by hand; an attempt to
establish absence by scrolling was a method error and is recorded as one. The
authoritative enumeration — a `View list of operation names` link in the
operation-names tooltip — was not visited.

**No records were sought for the `analyst` identity.** `P93-8` remains open. The
identity is unlicensed by design (`POS-027`) and may simply have never signed
in, in which case the result would be thin rather than informative.

## What was corrected

Six guide claims, all in the frontmatter above, plus one withdrawal and three
authoring errors of my own — all recorded in Lab 23 §6 rather than smoothed
over. The withdrawal: the job list rendered `2 items` beside a single row on
first read and `1 item` on second read. Transient async settling, **withdrawn as
a divergence** rather than published at the stronger reading.

## Cost

$0. Both VMs deallocated throughout. One search job, 3m 46s of service time, one
CSV export, no consumption meter touched.

## Cross-references

Lab 23 §7 · `POS-095` · `POS-035` (ingestion enabled, Lab 09) · `POS-027`
(`analyst` unlicensed by design) · `docs/evidence-notes/purview-audit-tiers-and-licensing.md` (tier boundary) · `docs/evidence-notes/ediscovery-content-search.md` (the same
session, the other data plane) · Lab 03 (`4624` does not mean a human logged in)
