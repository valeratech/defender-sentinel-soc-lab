# Lab 26 — Hunts, Queries and Bookmarks: A Documented Path That Routes to the Wrong Store

| Field | Value |
|---|---|
| **Domain** | Microsoft Sentinel hunting — hunts, hunting queries, bookmarks, and the `HuntingBookmark` table |
| **Objectives** | Build the full hunt → query → results → bookmark chain, and determine at which link it breaks and why |
| **Depends on** | `POS-034` (Entra ID connector, `SigninLogs` connector-fed), `POS-045`/`POS-046` (the tenant's two analytics rules), `DET-004` (validated brute-force detection, same logic as the hunting query authored here), Lab 11 (the trigger method reused) |
| **Status** | ✅ Built and measured — four source guides, three sittings, every registered prediction closed |
| **Built** | 2026-08-14 through 2026-08-16 |
| **Cost** | $0.00. Hunts and queries are control-plane objects; one bookmark row; six sign-in events. Query execution is not billed |

> The chain was built end to end and **broke at the results step**. Sentinel's own
> `View results` control routes hunting-query results into Advanced hunting — the
> one surface where bookmarks do not exist — from both documented entry points,
> while the hunt's own empty state diagrams QUERY → LOG ANALYTICS and instructs
> the analyst to click exactly that control.
>
> The bookmark was eventually created by reaching Azure Logs from Sentinel's
> **Search** page instead. That is what turns "bookmarks unavailable" into a
> **routing fault in one specific path** — a materially more useful finding, and
> one only reachable because the documented path failed.

---

## 1. Objective

Four source guides describe one chain: a hunt holds queries, queries produce
results, results produce bookmarks, bookmarks promote to incidents. They are one
evidence chain and therefore one lab.

The falsifiable content was never the KQL — `DET-004` had already validated this
exact detection logic. It was whether the objects behave as documented, and
whether mappings propagate along the chain.

## 2. Predictions

Registered per source guide before portal contact. Prefixes echo the retired course numbering and match
no repo counter — see the evidence notes' `corrections:`.

| ID | Prediction | Outcome |
|---|---|---|
| P106-1 | Hunting page still carries a Preview label | **Confirmed** — on the tab |
| P106-2 | Three tabs, no `Live stream` | **Confirmed** |
| P106-3 | Hunts tab empty; metrics bar reads zero | **Split** — empty confirmed; bar is on the Queries tab |
| P106-4 | Queries tab non-empty without a solution installed | **Confirmed** — 395 / 57 active |
| P106-5 | Status and Hypothesis sets and defaults as documented | **Confirmed** |
| P106-6 | A hunt writes no workspace table | **Confirmed** |
| P107-1…-4 | Counters, `Content source`, entity limits, MITRE caps | **Confirmed** |
| P107-5 | Query returns zero rows | **Confirmed** (window amended on the record before the read) |
| P107-6 | Query saves without ever being run | **Confirmed** |
| P108-1 | Six failures, all `50126`, no lockout | **Confirmed on terms; premise questioned** |
| P108-2 | Rows not immediately queryable | **Falsified** — latency floor unmeasured |
| P108-3 | `DET-004` fires and produces an incident | **Confirmed** |
| P108-4/-5/-6 | Bookmark count, mapping inheritance, table write | **Untestable by surface**, then answered via `docs/evidence-notes/search-jobs.md` |
| P108-7 | Clone is hunt-local; main counters unmoved | **Confirmed** |
| P110-5 | `Add bookmark` present in results reached from Sentinel | **Confirmed** |

## 3. Build

**Hunt**, 2026-08-14 18:47. `LAB-Hunt-Failed-Signin-Spike`, status `New`,
hypothesis `Unknown`, owner unset. Description states a falsifiable claim anchored
to `POS-046` and Lab 11.

**Hunting query**, 20:07 after an inert first attempt at ~20:00.
`LAB-Hunt-Query-Failed-Signin-Spike` — `SigninLogs`, `ResultType != 0`,
`count() by UserPrincipalName`, `> 5`. Entity `Account` / `FullName` /
`UserPrincipalName`; Credential Access / T1110, matching `DET-004` exactly.

**No time filter, deliberately.** The creation form forbids it: *"Do not use
fixed time ranges, either directly or in a function."* The guide's worked query
opens with `ago(1h)`. Divergence 218.

**Clone into the hunt**, 2026-08-15. `Query actions` → `Add queries to hunt`. The
panel states queries are **cloned**, and updates to the original will not reach
the copy.

**Trigger**, 2026-08-14 20:28 PDT. Six deliberate failed sign-ins as `labuser` at
`portal.azure.com`, reusing Lab 11's method exactly.

**Bookmark**, 2026-08-15 09:04:25. `LAB-BM-Failed-Signin-50126`, created from
Azure Logs reached via Sentinel → Search after the hunting path failed.

## 4. Measurements

### 4.1 A hunt writes nothing

Tables search on `hunt` returns one match: `HuntingBookmark`, Analytics, 30 days,
`Last data received` blank, never written. No `Hunt` table exists. Control-plane
only, no billing — cleanly distinct from Lab 25's TI object, which carried
`_IsBillable: True`.

### 4.2 Two populations, one name

The hunt's own `Queries` tab reads "No queries were found" while the main tab
holds 396. The page states the rule: hunt-scoped queries "are not visible on the
overall Hunting queries tab."

Adding the query **cloned** it. The original showed `Results 1`; the clone arrived
at `--` and had to be run separately. Confirmed by lifecycle at teardown: deleting
the hunt removed the clone and left the original standing at 58/396.

### 4.3 Entity mapping compiles into the query

Stored KQL carries a line never authored:

```
| extend Account_0_FullName = UserPrincipalName
```

The generated column encodes entity type, index, and identifier. **Stored query
text ≠ authored query text.**

### 4.4 The tactics picker spans matrices, unlabelled

17 tactics, not 14. `Evasion`, `Impair Process Control`, `Inhibit Response
Function` are ATT&CK for ICS. Inside Credential Access, T1414/T1417/T1453/T1517
are ATT&CK for Mobile, and `Input Capture` appears twice under different IDs.
Against the 250 techniques / 14 tactics recorded in `docs/evidence-notes/mitre-attack-coverage-matrix.md` at `Matrices type view : 13
selected`, two surfaces in one product offer different tactic universes.

### 4.5 `count()` counts records, not attempts

Six reported sign-in attempts produced six rows carrying **three distinct
timestamps**, each duplicated at identical millisecond precision:

```
3:29:32.821 ×2   3:29:47.514 ×2   3:29:53.702 ×2
```

Distinct `Id` per row, differing in one byte of the node segment. A single shared
`CorrelationId` across all six, so `dcount(CorrelationId)` returns 1.

The doubling propagates the whole way: rows → threshold → alert → incident title
(`LAB-Bruteforce: 6 failed sign-ins to Azure Portal`) → the incident's own range,
where `First activity` and `Last activity` are identical for an event spanning 21
seconds.

**Open against the committed record.** `DET-004` states "seven deliberate failed
sign-ins… on all seven" — seven *rows*. `POS-046` records suppression added after
"12 alerts from one event"; twelve is six doubled. Needs `dcount(CreatedDateTime)`
against July data before assertion. `CreatedDateTime` reads `03:28:49.4768815Z`
where `TimeGenerated` reads `03:29:53.7026258Z` — 64 seconds apart on one record.

### 4.6 `DET-004` fired

| Field | Value |
|---|---|
| Incident | `LAB-Bruteforce: 6 failed sign-ins to Azure Portal`, ID 28 |
| Created | `2026-08-15T03:37:29.5Z` |
| Last activity | `2026-08-15T03:29:32.821Z` |
| **End to end** | **just under 8 minutes** on a 5-minute schedule |

First firing since 8 August; re-validates `POS-046` by observation. The incident
arrived pre-assigned to `analyst` and tagged `auto-tagged-ruleA` — Lab 19/20
automation still working two weeks on, unprompted.

### 4.7 The routing fault

`View results` routes to **Advanced hunting** from the main Queries tab and from
inside a hunt. Confirmed twice, 36 hours apart, fresh browser session. With a
result row selected the toolbar offers `Link to incident` and `Take actions` and
no bookmark control. The hunt's Bookmarks tab has no creation control.

The hunt's own empty state says: *"…click 'View query results' in hunting query
details to view the results in Log Analytics. Use the check boxes… and click 'Add
bookmark'."* **Divergence 217.**

### 4.8 What a bookmark actually stores

`HuntingBookmark`, 21 columns. Present: `BookmarkId`, `BookmarkName`,
`CreatedBy`, `EventTime`, `QueryText`, `QueryResultRow`, `QueryStartTime`,
`QueryEndTime`, `Entities`, `SoftDeleted`, `Tags`, `Notes`.

**Absent: `Tactics` and `Techniques`.** Credential Access / T1110 were set at
creation and render in the Defender details pane, so they live control-plane only.
The guide recommends joining this table against others; anyone doing so loses the
ATT&CK dimension silently. **Divergence 219.**

Entity mapping was **decomposed, not stored as declared**. `FullName` →
`AlternateSignInName` became:

```json
{"Name": "labuser", "UPNSuffix": "<tenant>", "IsDomainJoined": true, "Type": "account"}
```

`IsDomainJoined` was never set. All four identifier/column pairings tried passed
validation — it checks that an identifier is selected, not that it fits the
column. A semantically wrong mapping saves silently.

`QueryResultRow` preserves the **entire** source row, 90+ columns including
`IPAddress`, `LocationDetails`, `DeviceDetail`.

`Event time mapping` defaults to `(Now)` — the bookmarking time, not the event
time. Second instance of a form defaulting a timestamp to the wrong moment.

### 4.9 Propagation, in the opposite direction to Lab 25

Bookmark created in Azure 09:04:25; visible in Defender within minutes;
`HuntingBookmark` written at the same instant — while the Tables page still read
`Last data received` blank. **The Tables page is the stale surface**, the reverse
of Lab 25's grid.

The Defender Bookmarks tab carries a propagation banner that no other Sentinel
surface in this section does.

## 5. Teardown

2026-08-16: bookmark deleted 21:29, hunt deleted 21:31 (taking the clone), the
original hunting query deleted separately with counters returning to 57/395,
incident ID 28 resolved 21:32.

## 6. What this lab does not establish

Whether the six reported attempts were three logged twice or six with three
logged — only click-spacing recollection separates them, and it was not recorded.
Whether entity and MITRE mappings inherit from a **mapped hunting query** into a
bookmark, since that path was never reachable; the observed empty inheritance is
from a raw Logs query. The cause of the inert `Create` at ~20:00 on 2026-08-14.
