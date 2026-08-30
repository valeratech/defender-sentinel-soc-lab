# Lab 25 — Threat Intelligence: An Indicator Nothing Was Joined To

| Field | Value |
|---|---|
| **Domain** | Microsoft Sentinel threat intelligence / Intel management / STIX object creation / TI table schema and billing flag |
| **Objectives** | Determine whether a manually created threat indicator reaches a workspace table, which table receives it, whether it is marked billable, and whether any analytics rule in this tenant joins against it |
| **Depends on** | `POS-034` (Entra ID connector, `SigninLogs` billable and connector-fed), `POS-045`/`POS-046` (the tenant's only two analytics rules, both `SigninLogs`-based) |
| **Status** | ✅ Built, documented, validated — created 2026-08-14, revoked 2026-08-16, seven predictions registered before portal contact |
| **Built** | 2026-08-14 through 2026-08-16 |
| **Cost** | Effectively $0. `_BilledSize: 786` bytes, `_IsBillable: True`. Query execution unbilled. No connector, no solution, no feed |

> The source guide reads as "connect a threat feed." The architectural point is that TI
> in the workspace is a **reference dataset** — a lookup that analytics rules join
> against — not another telemetry stream you monitor. That framing makes the
> tenant's answer legible: the indicator was created, was valid, was unrevoked,
> was marked billable, and **no rule in this workspace referenced a TI table at
> all.**

---

## 1. Objective

One question, answerable at negligible cost without installing a solution or
connecting a feed:

> Does the chain — indicator exists and unrevoked and in window → an analytics
> rule matches its type → the log table is ingested → the rule is enabled — hold
> in this tenant?

Scope was deliberately minimal: one hand-made object, no feed. A feed would have
committed the workspace to continuous ingestion five days before the Sentinel
trial's cost transition, to populate a lookup nothing was joined to.

## 2. Predictions

Registered before any portal action. Prefix `P26-n` — see the lesson's
`corrections:` for why the number does not match the lab.

| ID | Prediction | Outcome |
|---|---|---|
| P26-1 | Intel management empty at baseline | **Confirmed** |
| P26-2 | Lands in `ThreatIntelIndicators`; legacy table absent | **Split** — landing confirmed, absence falsified |
| P26-3 | Not queryable within ~60s of creation | **Untestable** — window elapsed before first query |
| P26-4 | Zero active rules reference a TI table | **Confirmed** |
| P26-5 | `ThreatIntelIndicators` on Analytics, workspace-default retention | **Confirmed** |
| P26-6 | Revocation appends a row rather than mutating | **Confirmed** |
| P26-7 | The 27 claimed TI rule templates are templates, not active rules | **Falsified** — they do not exist here |

## 3. Build

**Baseline, 2026-08-14.** Intel management: *"No threat intelligence data has
been found in your workspace."* Zero objects across all five tabs.

**Object created 15:45 PDT.** `New` → `TI object` → `Indicator`. Pattern builder,
domain-name, `ti-lab-test.invalid` — RFC 2606 reserved, cannot resolve, cannot
collide with `.pii-terms`. Name `LAB-TI-Test-Domain`. `Valid until` set 8/17
00:00 local; everything else left at shipped defaults.

**Defaults as shipped, captured before entry:** `Pattern builder` selected;
`Valid from`, `Created`, `Modified` pre-filled at form-open time; `Source`
pre-filled `Microsoft Sentinel`; `Valid until` **empty and required**;
`Confidence` `Is null` checked; TLP and Severity empty; `Revoked` unchecked.

**Revoked 2026-08-16 21:27 PDT** via `Edit` → `Revoked`, acknowledging the form's
warning that revocation is permanent.

## 4. Measurements

### 4.1 Where it landed, and the billing flag

```
ThreatIntelIndicators | where TimeGenerated > ago(2h)
| project _IsBillable, _BilledSize, ObservableValue, Type
→ True, 786, "ti-lab-test.invalid", ThreatIntelIndicators
```

The record is **marked billable** at 786 bytes. That figure is a **floor** — no
description, tags, TLP, or severity were set. Which meter applies and at what
rate was not measured and is not asserted; nor was any other TI ingestion path.

`Type` returns the table name, not the STIX object type; `where Type ==
"indicator"` returns nothing.

### 4.2 The legacy table

Four TI tables exist, all Analytics / 30 days: `ThreatIntelIndicators`,
`ThreatIntelObjects`, `ThreatIntelExportOperation`, and the legacy
`ThreatIntelligenceIndicator`.

```
ThreatIntelligenceIndicator | summarize Rows = count(), …
→ Rows 0, Earliest null, Latest null
```

Present, queryable, on the Analytics plan, at 30 days retention, and holding
nothing. Current Sentinel TI ingestion no longer targets it — the object created
here landed in `ThreatIntelIndicators` — and this workspace was created after
that migration. The Intel management empty state names the legacy table as the
destination for TI data on the same page that banners the migration away from it.
**Divergence 215.**

### 4.3 Schema

`getschema`, 2026-08-16 — 23 columns. Promoted: `Confidence` (int), `Pattern`,
`ObservableKey`, `ObservableValue`, `Type`, `ValidFrom`, `ValidUntil`, `Created`,
`Modified`, `Tags`, and three independent lifecycle booleans `IsDeleted`,
`IsActive`, `Revoked`.

**Not promoted: TLP, severity, name, description, source.** Both TLP and severity
render in the details pane. Where a populated value is stored was **not
established by this object** — both were left unset at creation, so only their
absence from the column list is measured. Microsoft documents TLP as
`AdditionalFields.TLPLevel`; severity storage is unverified here. A rule cannot
filter on either as a column.

Note `_IsBillable`, `_BilledSize`, and `_SubscriptionId` appear in the Logs schema
tree but not in `getschema` output — computed billing columns, still projectable,
which is how §4.1's measurement was taken.

### 4.4 The chain, and where it breaks

| Link | State |
|---|---|
| Indicator exists, unrevoked, in window | ✅ |
| An analytics rule matches its type | ❌ **zero rules reference a TI table** |
| The log table is ingested | n/a |
| The rule is enabled | n/a |

The tenant holds exactly two active analytics rules, both `SigninLogs`-based,
both T1110. Searching rule templates for `threat intelligence` returns **one**
result; `TI map` returns **none**. The portal's claim of *"27 out-of-the-box
analytics rules available in the Analytics blade"* is false as written here.

The one template that does exist —
`Microsoft Defender Threat Intelligence Analytics`, Gallery Content, template last
updated **Mar 14 2023** — carries Microsoft's own warning: *"One or more data
sources used by this rule is missing."* Two of its four sources
(`ASimDnsActivityLogs`, `ASimNetworkSessionLogs`) are empty here. Enabled, it
would join `ThreatIntelIndicators` against nothing.

### 4.5 Append-only semantics — P26-6

Revocation at 21:27:04, queried immediately and again minutes later:

```
TimeGenerated            IsActive  Revoked  IsDeleted  Modified
Aug 14 3:45:52 PM        true      (empty)  false      Aug 14 3:30:00 PM
Aug 16 9:27:04 PM        false     true     false      Aug 14 3:30:00 PM
```

Two rows, one `Id`, original untouched. **Confirmed.**

Three things fall out. `Revoked` renders empty on the original where `IsDeleted`
renders `false` — null and false handled inconsistently within one row.
`Modified` never moved: not at creation, not at revocation two days later, so it
is a STIX property copied from the form rather than a record of change. And the
first query after a successful revocation returned only the original row —
revocation lagged the UI by minutes where creation had been queryable in seconds.
The two-read discipline is what prevented scoring this falsified.

### 4.6 Timestamps

`created`, `modified`, and `valid_from` all stored `2026-08-14T22:30:00Z` — the
moment the **form was opened**. `TimeGenerated` is `22:45:52.126Z`, matching the
creation toast. The indicator's validity begins fifteen minutes before it existed.

`Id` = `base64("Microsoft Sentinel")---indicator--<uuid>`, verified both
directions. The `Source` field is baked into the primary key.

### 4.7 Surface behaviour

The Intel management grid did **not** populate on creation: the tab counter read
`Indicators (1)` beside a grid reading `No TI objects`. A manual refresh resolved
it, so self-healing is unmeasured — the refresh destroyed that measurement.

## 5. Teardown

Revoked rather than deleted, 2026-08-16 21:27 PDT, scoring P26-6. The rows remain
in `ThreatIntelIndicators` for the table's 30-day retention; revocation is
permanent per the form's own warning.

## 6. What this lab does not establish

Whether MDTI or TAXII connector paths carry the same billing flag as manual
creation. Where TLP and severity are stored when populated. Whether the 27
claimed templates ship with the Threat Intelligence solution. Whether the
creation-to-query latency floor is seconds or shorter — P26-3's window elapsed
and is not reopenable on this object.
