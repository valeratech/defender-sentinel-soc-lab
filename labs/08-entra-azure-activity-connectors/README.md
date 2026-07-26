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

## 5. Validation and the surface-schema finding

A `search * | where TimeGenerated > ago(1h) | summarize count() by $table`
(run in the Defender-portal Advanced Hunting surface) returned, among others:

| Table | Count | Meaning |
|---|---|---|
| `AzureActivity` | 4 | ✅ Azure Activity (Method B) flowing |
| `EntraIdSignInEvents` | 489 | ✅ Entra sign-in data flowing — **licensing test PASSED** |
| `EntraIdSpnSignInEvents` | 2 | Service-principal sign-ins |
| `GraphAPIAuditEvents` | 934 | Graph activity |
| `SecurityEvent` | 1261 | Lab 07's DCR still ingesting |
| `Heartbeat` | 60 | AMA alive |

**The finding — `SigninLogs` vs `EntraIdSignInEvents`.** Querying `SigninLogs`
(the name the guide uses) returned nothing, while `EntraIdSignInEvents` held 489
rows. These are the **same sign-in data under two schema names**: `SigninLogs` is the
**Log Analytics workspace** table name (query it in Sentinel → Logs);
`EntraIdSignInEvents` is the **Defender-portal Advanced Hunting** name. Same
underlying events, two surfaces, two schemas — the identity-data instance of the
Lab 04 distinction (Advanced Hunting `Timestamp` vs Sentinel Logs `TimeGenerated`).
An analyst following the guide's `SigninLogs` while in Advanced Hunting sees "no
data" and may wrongly conclude the licensing failed — when 489 events sit right there
under the other name. **The licensing test passed**; the earlier empty `SigninLogs`
was a surface-schema mismatch, not a licensing failure.

**Latency:** both connectors were empty at first query (~10 min) and populated after
(Entra ~10-15 min, Azure Activity 15-60 min). Empty-then-populates is propagation —
and confirmed here that the config had genuinely applied (both diagnostic settings
exist) before concluding it was lag.

## 6. Findings

1. **Connector effort scales with source foreignness** — the tiers model (§2),
   grounded in Labs 04/07/08 as same-platform / external-disk / separate-service.
2. **Method A (policy) failed, Method B (diagnostic setting) worked** — and for one
   subscription, B is architecturally correct, not a workaround (§3). Environmental,
   not user error.
3. **`SigninLogs` vs `EntraIdSignInEvents`** — same sign-in data, two schema names by
   query surface; querying the wrong name reads as "no data / licensing failed" (§5).
4. **Licensing test passed** — Entra P2 (E5 trial) is live; sign-in ingestion works
   (489 events). The two risk tables (`AADRiskyUsers`/`AADUserRiskEvents`) may stay
   empty even when licensed — they populate only on actual risk detection, and a
   quiet lab tenant produces none; empty risk tables are not a licensing failure.
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
