---
title: KQL fundamentals — and what querying the tenant with it actually revealed
date: 2026-08-12
artifacts:
  labs: []
  posture: [POS-068]
  divergences: [208, 209]
  kql: []
corrections:
  - "Guide: the CloudAppEvents table carries much of the unified audit log. Overstated. Microsoft's own table reference (advanced-hunting-cloudappevents-table, ms.date 05/15/2025) says the table is populated by records from Microsoft Defender for Cloud Apps and lists SaaS connectors; the only audit reference on the page is the AuditSource column, whose values are all MDCA mechanisms. CloudAppEvents carries MDCA-connector telemetry ABOUT Office 365 activity, which overlaps the unified audit log's subject matter without being a copy of it."
  - "Guide presents Timestamp (advanced hunting) versus TimeGenerated (Sentinel/Log Analytics) as a strict either/or and calls it the single most common reason a copied query fails. The trap is real but not universal: EntraIdSignInEvents carries BOTH columns, and they are identical - 1,358 rows over one day, min delta 0, max delta 0, exactly one distinct value. Neither column is an ingestion timestamp on that table; a latency figure computed by subtracting one from the other would be a constant zero masquerading as a measurement."
  - "Guide's operator list distinguishes contains (substring) from has (whole term) and separately warns that == is case-sensitive. It does not say the two compose into a trap. Because contains is case-INSENSITIVE, it matched every row of a column whose values were the negation of the search term - see divergence 208."
  - "Claude asserted a column named ResultType on EntraIdSignInEvents without checking the schema, one message after stating that checking the schema before trusting a query is the durable skill. The column does not exist; the surface returned a semantic error. ResultType is a Sentinel SigninLogs column. Corrected by getschema."
---

# KQL fundamentals, and what querying the tenant with it actually revealed

The source guide itself is language mechanics: the pipeline shape, `where`, `summarize`,
`project`, `bin()`. That part is concept — it earns a guide, not a lab.

What earned a record is that one claim in the source guide was checkable against state
this repository had already measured, and checking it opened a chain that closed
`POS-068`'s open mechanism.

## The claim that was checkable

The guide states `CloudAppEvents` carries much of the unified audit log. This
tenant held both halves of that claim already:

- `POS-068` (2026-08-05): `CloudAppEvents` returned **0 rows over 7 days**, three
  surfaces agreeing on genuine no-flow, obvious cause eliminated, **no
  replacement found**.
- `POS-095` (2026-08-11): the unified audit log returned **19 `UserLoggedIn`
  records** spanning 07-26 to 08-11.

Overlapping windows. Audit data demonstrably present; the table said to carry it
demonstrably empty.

## What the queries measured

| Query | Result | What it establishes |
|---|---|---|
| `CloudAppEvents \| count` | **0** | Empty across all time, not 0 in a window |
| `union` of four tables, 30d | `AlertInfo` 30 · `DeviceLogonEvents` 86 · `EntraIdSignInEvents` 30,781 · `CloudAppEvents` **absent** | The zero is the table, not the surface — and see divergence 209 |
| `CloudAppEvents` over the `docs/evidence-notes/purview-audit-log-search.md` window | *No results found* | The 19 audit records are not there |
| `EntraIdSignInEvents` `LogonType` split | **21,926 non-interactive / 507 interactive** | Sign-ins live in a dedicated table, and see below |
| `Timestamp` vs `TimeGenerated`, 1d | 1,358 rows, one distinct delta of **0** | Aliases on this table |

## 97.74% of sign-ins are not a person

`docs/evidence-notes/purview-audit-log-search.md` established qualitatively that `UserLoggedIn` in the Purview audit log
included `OAuth2:Token` service authentication rendered identically to human
sign-ins — the `4624` principle on a second product.

`EntraIdSignInEvents` separates what the audit log conflated. Over the same
window, **21,926 of 22,433 events (97.74%) are `nonInteractiveUser`**. In this
tenant, reading a sign-in record as "a human authenticated" is wrong roughly
forty-three times in forty-four.

This is the same principle on a third surface, and the first time it has a
population-level number attached rather than a single illustrative record.

## The operator trap

Recorded as divergence **208**. Three operators against one column, one query:
`==` returned 0, `contains` returned all 30,801 rows, `has` returned the correct
933. `contains` is case-insensitive, so `nonInteractiveUser` contains
`interactiveUser` — the negation is invisible to the operator.

Neither wrong answer errors. Both are plausible numbers.

## Why this closed POS-068

The guide's overstated claim was corrected by fetching Microsoft's own table
reference — which, in its Prerequisites section, names the exact control that
governs whether the table is populated at all:

> To make sure the `CloudAppEvents` table is populated: Go to the Defender portal
> and select **Settings > Cloud apps > App connectors**. In the **Select
> Microsoft 365 components** page, select the **Microsoft 365 activities**
> checkbox.

Reading that page in this tenant found five of six components unchecked,
including `Microsoft 365 activities`. `POS-068` had recorded the obvious cause
eliminated with no replacement found; this is the replacement, and it was
documented and on-screen the whole time, three non-obvious interactions away from
every surface that reports health.

Full resolution, including why `Test connection: Success` is not evidence of
effective collection, is recorded in `POS-068` rather than split across records.

## Consequence for community and generated queries

Any query — from the Azure-Sentinel repository, from an assistant, from a
textbook — that depends on `CloudAppEvents` returns zero rows in this tenant and
reads as *no cloud app threats found*. The cause is an unchecked connector
component. This is the concrete form of the standing warning that an empty result
is ambiguous between a wrong query and absent data, and it is a fifth cause not
in the usual four (no activity, not licensed, outside retention, not onboarded).
