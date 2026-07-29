# Lab 08 — Entra ID and Azure Activity Connectors

| Field | Value |
|---|---|
| **Domain** | Ingest data into Microsoft Sentinel |
| **Objectives** | Connect the two foundational first-party connectors — Azure Activity (control-plane) and Microsoft Entra ID (identity); verify data flow; resolve the P1/P2 sign-in licensing question by observation |
| **Depends on** | Lab 04 (the Sentinel workspace), Lab 07 (AMA ingestion — the contrast case) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-25 |

> The connector lab that completes the ingestion section. Two first-party
> connectors, each needing configuration *beyond* installing the solution — and
> together they demonstrate why connector effort scales with how "foreign" the
> source is to Sentinel.

---

## 1. Objective

Connect the two connectors most environments configure first: **Azure Activity**
(subscription control-plane operations → `AzureActivity`) and **Microsoft Entra ID**
(identity logs → `SigninLogs`, `AuditLogs`, risk tables). Both were installed as
Content Hub solutions in a prior session; this lab does the *configuration* that
actually makes them flow — and confirms the flow by querying the tables, not by
trusting a status label.

## 2. The connector-tiers model (the analysis through-line)

Across Labs 04, 07, and 08, a pattern emerges: **the configuration a connector
needs scales with how far the data has to travel and whether the source already
sits inside Sentinel's trust/plumbing boundary.**

| Tier | Example | Config needed | Why |
|---|---|---|---|
| Same platform | Defender XDR (Lab 04) | ~none — auto-connected | Same portal, tenant, RBAC. Enabling Sentinel wired it up automatically |
| Your resource, external disk | Windows events / AMA (Lab 07) | Agent + DCR | Sentinel can't reach into a VM's event log; something must run on the box, know what to collect, and ship it |
| Separate service with its own logging | Azure Activity, Entra ID (Lab 08) | Reconfigure *that service* to export (diagnostic setting / policy) + licensing | The source is a first-class Azure/Entra logging system that exists independently; connecting it means telling *that service* to send Sentinel a copy |

This is why these two are the first to surface the guide's warning that **"connected
is not flowing"**: the connector page can read connected (Sentinel is ready to
receive) while the real work — making Entra/Azure *export* — is a separate step on
the source service. Decomposing the connector landscape this way predicts the effort
for any source: count how foreign it is and whether it owns its own logging pipeline.

## 3. Azure Activity — Method A failed, Method B worked

Azure Activity offers two routing methods. The guide recommends **Method A (Azure
Policy)** as the scalable path. In this environment it **failed twice**, and
**Method B (manual diagnostic setting)** succeeded first try.

**Method A attempts (both failed):** launched the Azure Policy Assignment wizard,
configured it correctly (scope = the subscription, workspace = law-soc-lab,
remediation task enabled, system-assigned managed identity in westus), and hit
Create — twice. Both times the submission returned **"you need to log in"**, and
**Policy → Assignments confirmed 0 policy assignments** afterward (only the
pre-existing ASC Default *initiative* was present). Not user error: the wizard's
managed-identity creation needs a privileged token, and the session kept expiring at
submission.

**Method B (succeeded):** Subscription → Activity log → Export Activity Logs → Add
diagnostic setting `activity-to-law-soc-lab`, categories Administrative + Security,
destination law-soc-lab. Saved first try. Verified: `AzureActivity` populated.

**The analysis — B was not merely a fallback, it was the appropriate choice.** For a
**single subscription**, Method B is simpler and correct; Method A's machinery
(policy + managed identity + remediation + ongoing enforcement) only earns its
complexity across *many* subscriptions with auto-enrollment of new ones. The guide's
"recommended" implicitly assumes multi-subscription scale. In a one-subscription
environment the recommended method is the harder, more failure-prone path to the
same result. The real decision rule: **count subscriptions** — one or a few →
diagnostic setting; many, or need auto-enrollment → policy.

## 4. Entra ID — the connector and the licensing question

The Entra ID connector page offers 15 log types. Selected four, cost-aware:

- **Sign-In Logs** (`SigninLogs`) — the licensing test + foundation of identity monitoring
- **Audit Logs** (`AuditLogs`) — any licence tier, low volume, directory changes
- **Risky Users** (`AADRiskyUsers`) and **User Risk Events** (`AADUserRiskEvents`) — Entra ID Protection risk telemetry (needs P2)

The high-volume optional types (non-interactive, service-principal, Graph activity,
etc.) were left off — volume without proportional value in a lab, the connector-level
cost lever in practice.

Apply wrote an Entra diagnostic setting **`AzureSentinel_law-soc-lab`** →
law-soc-lab (confirmed at Entra ID → Monitoring & health → Diagnostic settings),
using the same diagnostic-setting mechanism that made Method B work for Azure
Activity — and, unlike the Azure Activity *policy* path, it applied cleanly.

**The licensing gotcha (guide §3):** ingesting Entra **sign-in** logs needs P1 or
P2; other log types work on any tier. On a Free/O365 tenant, sign-in logs silently
never populate. This tenant's E5 trial should include P2 — verified by result, not
assumed.

## 5. Validation, and a finding that had to be withdrawn

### What was observed on build day (2026-07-25)

A `search * | where TimeGenerated > ago(1h) | summarize count() by $table`, run in
the **Defender-portal** Advanced Hunting surface, returned among others:

| Table | Count | Meaning |
|---|---|---|
| `AzureActivity` | 4 | ✅ Azure Activity (Method B) flowing |
| `EntraIdSignInEvents` | 489 | Entra sign-in data present |
| `EntraIdSpnSignInEvents` | 2 | Service-principal sign-ins |
| `GraphAPIAuditEvents` | 934 | Graph activity |
| `SecurityEvent` | 1261 | Lab 07's DCR still ingesting |
| `Heartbeat` | 60 | AMA alive |

`SigninLogs` returned nothing. This lab originally concluded that `SigninLogs` and
`EntraIdSignInEvents` were **the same sign-in data under two schema names**, one per
query surface, and shipped that as Finding 3. The confirming test — querying
`SigninLogs` in Sentinel Logs — was proposed at the time and never run.

### The correction (2026-07-26)

The identical census was run on **both** portals within four minutes of each other.

| | Defender portal | Azure / Sentinel Logs |
|---|---|---|
| `SigninLogs` | 6 | **7** |
| `EntraIdSignInEvents` | 972 | **absent** |
| `EntraIdSpnSignInEvents` | 4 | **absent** |
| `GraphAPIAuditEvents` | 3578 | **absent** |
| `EmailEvents` / `EmailUrlInfo` | 1 / 10 | **absent** |
| `IdentityInfo` | 1 | **absent** |
| `SecurityEvent` | 1368 | 1368 |
| `Heartbeat` | 135 | 135 |
| `AzureActivity` | 10 | 10 |
| `Usage` | 12 | 12 |

**Two names for one dataset cannot appear side by side in a single result and
disagree about how many rows exist.** The original finding was inference, and it was
wrong.

### What is actually true: different producers, not different names

| | Producer | Scope governed by | Cost |
|---|---|---|---|
| `SigninLogs`, `AuditLogs` | the Entra diagnostic setting written by this connector | **the four log types selected in §4** | billable |
| `EntraIdSignInEvents`, `EntraIdSpnSignInEvents`, `GraphAPIAuditEvents`, `EmailEvents`, `EmailUrlInfo`, `IdentityInfo` | Defender XDR, natively | Microsoft | free |

The decisive evidence was already in this lab and went unread. §4 records that the
high-volume Entra log types — non-interactive, **service-principal**, **Graph
activity** — were deliberately declined. Tables carrying precisely that data cannot
be fed by the connector that refused it. `EntraIdSpnSignInEvents` and
`GraphAPIAuditEvents` sitting in the Defender census were the disproof, present from
the first day and unnoticed.

The 6-versus-972 gap follows: six interactive sign-ins in 24 hours is exactly right
for a single-operator tenant, while XDR collects every sign-in class regardless of
what this connector was told to send.

And the original empty `SigninLogs` needs no exotic explanation. The **Latency**
note below — in this same section — records Entra propagation at 10–15 minutes, and
the query was run at roughly 10. The correct explanation was sitting beside the
wrong one; the tidier story won.

### The replacement finding: the store-partition method

One census, run on both portals, diffed. **What survives into the Azure list is
workspace-resident and billable. What drops out is XDR-native and free.**

That converts a cost question from argument into measurement, costs nothing, and
repeats on demand. Its first result was reassuring: `GraphAPIAuditEvents` — 3,578
events in 24 hours, the volume that prompted the check — bills nothing. The entire
billable surface is five tables at negligible volume against 10 GB/day.

It also settled a question ahead of the behavioural-analytics section: `IdentityInfo`
is XDR-side, so it is **not** evidence of UEBA running in this workspace.

Query kept at `kql/sentinel/store-partition-diff.kql`.

### Timestamp trap, sixth occurrence

The two exports disagreed by **exactly seven hours** across three tables, matching to
the second:

| Table | Defender export | Azure export (UTC) |
|---|---|---|
| `SecurityEvent` | Jul 25, 5:50:09 PM | Jul 26, 00:50:09.620 |
| `Heartbeat` | Jul 25, 5:52:45 PM | Jul 26, 00:52:45.841 |
| `AzureActivity` | Jul 25, 5:59:14 PM | Jul 26, 00:59:14.588 |

The Defender export rendered local time; the Azure export rendered UTC **and said so**,
labelling its column `Latest [UTC]` where the Defender export left it unlabelled. That
header difference is a free tell. Every prior occurrence compared two different events
across surfaces; this one is the same rows exported twice, so the offset is measured
rather than inferred.

### Latency

Both connectors were empty at first query (~10 min) and populated after — Entra
~10–15 min, Azure Activity 15–60 min. Empty-then-populates is propagation, confirmed
here by checking that both diagnostic settings genuinely existed before concluding
lag. This is the note that should have explained the empty `SigninLogs` on day one.

## 6. Findings

1. **Connector effort scales with source foreignness** — the tiers model (§2),
   grounded in Labs 04/07/08 as same-platform / external-disk / separate-service.
2. **Method A (policy) failed, Method B (diagnostic setting) worked** — and for one
   subscription, B is architecturally correct, not a workaround (§3). Environmental,
   not user error.
3. **`SigninLogs` vs `EntraIdSignInEvents` — different producers, not different
   names** (§5). The workspace tables are connector-fed, scoped by the log types
   selected here, and billable; the `EntraId*`/`GraphAPI*`/`Email*` tables are
   Defender XDR-native, unaffected by this connector, and free. *This finding
   replaces the original Finding 3, which claimed the two were one dataset under two
   surface-specific names. That was inference, its confirming test was skipped, and
   it was withdrawn 2026-07-26.* The **store-partition method** — one census run on
   both portals, table lists diffed — separates billable from free by measurement.
4. **Licensing test passed — conclusion unchanged, evidence corrected.** Entra P2
   (E5 trial) is live. The 489 `EntraIdSignInEvents` originally cited proves nothing
   about this connector, being XDR-native and present regardless of it. The proof is
   `SigninLogs` populated **in the workspace** — 7 events, latest 2026-07-26 21:56
   UTC, the last of them the operator's own Azure-portal sign-in minutes earlier,
   which also shows the interactive-only scope behaving as selected. The two risk
   tables (`AADRiskyUsers`/`AADUserRiskEvents`) may stay empty even when licensed —
   they populate only on actual risk detection, and a quiet lab tenant produces none;
   empty risk tables are not a licensing failure. `AuditLogs` was selected but absent
   from a 24-hour window on 2026-07-26 — a quiet tenant is the likely reason, recorded
   as unconfirmed rather than assumed.
5. **Both connectors are platform diagnostic settings** — VM-independent, so they
   keep ingesting with the VM and Bastion deallocated.

## 7. Cost

Both connectors bill per GB into the workspace, but at low lab volume: `AzureActivity`
is sparse (control-plane actions only), `SigninLogs`/`AuditLogs` are modest in a
quiet tenant. The two ingestion cost levers the section closes on — **connectors
(coarse on/off)** and **DCRs (fine, filter-at-source)** — are the disciplines already
applied across Labs 07 and 08: declining high-volume Entra types is Lever 1;
Lab 07's Common-not-All DCR is Lever 2. The section's optimization guidance
externally validates the cost discipline the project had been applying independently.

**Measured, 2026-07-26 — and corrected 2026-07-29.** This originally read: *"the
billable surface is exactly five tables — `SecurityEvent`, `Heartbeat`, `Usage`,
`AzureActivity`, `SigninLogs`."* **Wrong.** A `Usage | where IsBillable == true`
query on 2026-07-29 returned three: `SigninLogs`, `AuditLogs`, `IdentityInfo`.
`AzureActivity` had 11 events in the window and does not appear as billable, and
neither does `Usage` itself.

The error was conflating **workspace-resident** with **billable**. The
store-partition census separates the free XDR lake from the workspace, and that
finding stands — but there is a **second split inside the workspace**, between
billable and free data sources, which the census cannot see. `AzureActivity` is
workspace-resident *and* free. **`Usage` with `IsBillable` is the instrument for
billability; the census is the instrument for residency.** Two questions, two tools.

This also establishes that `SecurityAlert` and `SecurityIncident` are free — the
entire Defender XDR → Sentinel path built in Lab 04 costs nothing to carry. The largest table visible from the Defender portal
(`GraphAPIAuditEvents`, 3,578 events in 24 hours) is XDR-native and bills nothing.
Declining the high-volume Entra log types in §4 is doing exactly what it was chosen to
do. `Usage` reports on a lag of several hours, so the most recent window reads as
not-yet-reported rather than as zero.

## 7b. UEBA — enabled 2026-07-28, and what it cost (`POS-044`)

This lab's connectors are UEBA's inputs, so the enablement is recorded here rather
than in a lab of its own — nothing was built, one feature was switched on.

**The finding is the cost shape.** Learn says no licence is required and there is
no extra cost for UEBA, then says it generates new data in new workspace tables and
storage charges therefore apply. Both are true; only the first is memorable.
Measured here:

| DataType | BillableMB / 24h |
|---|---|
| `SigninLogs` | 0.038757 |
| `AuditLogs` | 0.003583 |
| **`IdentityInfo`** | **0.001416** |

**"The feature is free" and "enabling it is free" are different claims.**

**The store-partition method detected a table changing sides.** `IdentityInfo` was
XDR-only on 2026-07-26 — that absence was the evidence used to conclude UEBA was
off. It is now workspace-resident and metered.

**Prediction 2 of 4**, recorded before the fact: `IdentityInfo` and
`BehaviorAnalytics` appeared, `UserPeerAnalytics` and `UserAccessAnalytics` did
not. Three identities may have no peer groups to compare and no access history to
analyse — hypothesis, not established, and indistinguishable from latency on one
census.

**Initial sync took under an hour**, against Learn's "may take a few days."

**`AuditLogs` — the open caveat from §6 is closed.** It was recorded on 2026-07-26
as *selected but absent, quiet tenant likely, unconfirmed rather than assumed*. It
carries data as of 2026-07-29. The connector was fine; the tenant was quiet.

## 8. Deferred

- **The SigninLogs sign-in workbook** — now that sign-in data flows, the Entra Sign-in
  workbook template will render (the item deferred since the "Configuring Sentinel"
  section). Build/observe it when convenient.
- **Full licensing granularity** — sign-in ingestion (P1/P2) is confirmed; whether the
  risk tables populate awaits an actual risk detection.

## 9. References

- `POS-034` (both connectors), `POS-032` (the workspace they feed), `POS-024`
  (subscription Owner — the permission Method A's managed identity needed), Lab 04
  (Defender XDR connector, the same-platform tier), Lab 07 (AMA, the external-disk tier)
- Microsoft Learn — Azure Activity connector; Microsoft Entra ID connector; diagnostic
  settings
