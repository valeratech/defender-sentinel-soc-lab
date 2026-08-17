---
module: 110
title: Search jobs — a page that runs no search job, and the bookmark that closed MOD-108
section: Detect threats by using the Microsoft Sentinel platform
verdict: lab
date: 2026-08-15
artifacts:
  labs: ["26"]
  posture: []
  divergences: [216, 219, 221]
  kql: []
corrections:
  - "P110-1 registered four inputs from the guide - table, term, time range, results table name. The Search page has two. Claude wrote the prediction from the guide rather than from the surface; the missing controls were never there."
  - "P110-4 (union of time ranges) was untestable: no time picker exists on the Search form to set against an in-query filter."
  - "Claude repeatedly issued navigation as a bare control name without naming the portal, page, or starting point - against the repo's own navigation standard, cited in the same session. The `View results` routing question took three round trips as a result."
---

# MOD-110 — Search jobs

> The Search page did not run a search job. It handed off to the Azure portal and
> landed in the Logs blade — the synchronous, interactive surface the guide spends
> two sections distinguishing search jobs *from*.

## What was configured

One bookmark: `LAB-BM-Failed-Signin-50126`, entity `Account` / `FullName` /
`AlternateSignInName`, tactic Credential Access, technique T1110. First write ever
to `HuntingBookmark`, against a measured empty baseline. Deleted at teardown
2026-08-16 21:29 PDT. Full record in **Lab 26**.

## What was established

**No search job ran, and none can be initiated from this form.** Two inputs —
search term and a table chip. No time range, no results-table name. Clicking the
table chip **ejects to `portal.azure.com`**, landing in Logs in Simple mode with
`Time range : Last 24 hours` and `Show : 500000 results`. No `_SRCH` table was
created, so the 14-day-versus-30-day retention conflict (P109-6) stays
unresolved. Divergence 221.

**Bookmarks work on the entry path the guide describes.** Azure Logs reached from
Sentinel's Search page: `Add bookmark` present, greyed until a row is selected,
then functional. This is what narrows MOD-108's defect from "bookmarks
unavailable" to "the hunting path routes to the wrong store."

**MITRE mappings do not reach `HuntingBookmark`.** The 21-column schema has no
`Tactics` and no `Techniques`. Credential Access / T1110 were set at creation and
render in the Defender details pane, so they live in a control-plane object the
table does not carry. The bookmark guide's §4 recommends joining
`HuntingBookmark` against other tables; anyone doing so loses the ATT&CK
dimension silently. Divergence 219.

**Entity mapping is a parsing instruction, not a storage format.** Declared
`FullName` → `AlternateSignInName`; stored as
`{"Name": "labuser", "UPNSuffix": "<tenant>", "IsDomainJoined": true,
"Type": "account"}`. The platform split the UPN and **added `IsDomainJoined`,
which was never set**. All four identifier/column pairings tried passed
validation — the validator checks only that an identifier is selected, never that
it matches the column's shape. A semantically wrong mapping saves silently.

**`QueryResultRow` preserves the entire source row** — 90+ columns including
`IPAddress`, `LocationDetails`, `DeviceDetail`. A bookmark carries geolocation and
device fingerprint whether intended or not.

**The search term became a KQL rewrite:** `SigninLogs | where * has 'labuser'` —
a wildcard `has` across every column.

**`Event time mapping` defaults to `(Now)`** — the bookmarking time, not the
event time. Second instance of a Microsoft form defaulting a timestamp to the
wrong moment; the TI object stored form-open time as `created`.

**Cross-portal propagation is prompt, and the Tables page is the stale surface.**
Bookmark created in Azure at 09:04:25, visible in Defender within minutes,
`HuntingBookmark` written at the same instant — while the Tables page still showed
`Last data received` blank. The reverse of the TI grid's behaviour, where the
table led and the grid lagged.

**`TimeGenerated` renders differently by portal.** Azure Logs: UTC with an
explicit `[UTC]` header and millisecond precision. Defender surfaces: local,
unlabelled, truncated to seconds. Same row, seven hours apart, no marker on the
Defender side. Divergence 216.

## What was corrected

See `corrections:`. A prediction written from a guide rather than a surface, an
untestable clause, and a navigation standard I cited and did not meet.

## What could not be tested

Everything a search job does. No `_SRCH` table, so its naming, tier, and retention
are unmeasured, and P109-6 remains open.

## Cost

$0. No search job billed; bookmark storage is negligible.
