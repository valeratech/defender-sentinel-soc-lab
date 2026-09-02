# Lab 04 — Sentinel Workspace: Deployment and the Defender Pipeline

| Field | Value |
|---|---|
| **Domain** | Manage a security operations environment |
| **Objectives** | Stand up a Log Analytics workspace; enable Microsoft Sentinel; connect Defender XDR; prove endpoint→XDR→SIEM data flow with a live event; keep ingestion cost-safe |
| **Depends on** | Lab 03 (telemetry source), Lab 06 (events to forward), all prior labs (aggregated here) |
| **Status** | ✅ Built, documented, validated |
| **Built** | 2026-07-19 |

> This is the section capstone. Every prior lab feeds it: Lab 03's onboarded
> sensor, Lab 05's device groups, Lab 06's ASR events and the two ATT&CK-mapped
> detections all become *inputs* to Sentinel. Sentinel is not a fresh start —
> it is the aggregation layer over everything already built.

---

## 1. Objective

Turn a collection of Defender findings into a SIEM. Microsoft Sentinel sits on a
Log Analytics workspace and ingests security data from connected sources; the
Defender XDR connector streams the incidents and alerts this project has been
generating into that workspace, where they can be queried, correlated, and turned
into analytics rules. The goal of this lab is the pipeline itself — proving that an
event on the endpoint travels all the way to Sentinel — while keeping ingestion
inside the free tier.

## 2. Design Decisions

Every decision here was cost-driven, because Azure spend is out-of-pocket and the
lab's life is bounded by the M365 trial, not the Sentinel trial.

| Decision | Chosen | Rationale |
|---|---|---|
| Portal | **Defender portal (unified)** | On Unified RBAC (`POS-026`), Sentinel-in-Defender shares one incident queue and RBAC with Defender XDR. The Azure-portal Sentinel experience is being retired. Confirmed: the Defender portal lists the workspace as **Connected / Primary**. |
| Region | **West US** | Matches the VM (`POS`-recorded region) — data residency and no cross-region egress. Cannot be changed after creation. |
| Pricing tier | **Pay-as-you-go (Per GB 2018)** | Steady-state volume is unknown; a commitment tier would be a guess with a daily minimum charge. PAYG can be switched to commitment later once volume is known. |
| Connectors | **Defender XDR only — alerts/incidents, NOT raw events** | The single cost lever. Alert/incident sync is free; raw `Device*` event streaming bills by volume. Verified off (§4). |
| Retention | **Default (~30 days)** | Extending retention bills; a lab needs no long history. |

**Three clocks, and which one binds.** Azure spend (per active-hour, ends when the
RG is deleted); the M365 Defender trial (fixed calendar end — the *binding*
constraint, since it kills the telemetry source); and the Sentinel 31-day trial
(started at enablement, 2026-07-19 → 2026-08-19, 10 GB/day free on both Sentinel
and Log Analytics). At build time the Sentinel trial outlived the M365 trial — superseded by the 2026-08-06 M365 extension (`POS-077`): the Sentinel trial ended 2026-08-19 and the M365 term now runs to 2026-09-14. On that original reading, enabling it then
costs nothing in practice — the environment ends with M365 first.

## 3. Build

1. **Permissions** — subscription **Owner** confirmed (plus Global Administrator).
   Directory role ≠ Azure RBAC (`POS-024`): GA alone would not satisfy the
   Defender-portal auto-onboard; Owner does.
2. **Log Analytics workspace** — `law-lab-01`, West US, PAYG, in the VM's resource
   group (so the whole lab is one deletable unit — teardown is one RG delete,
   which matters when spend is out-of-pocket).
3. **Enable Sentinel** on the workspace — starts the 31-day trial.
4. **Defender XDR connector** — installed the Content hub solution (free), then
   found the connector had **auto-connected** on Sentinel enablement: the Defender
   portal's unified integration wired the whole Defender family (Endpoint,
   Identity, Cloud Apps, O365, Entra ID Protection) at `Connected` without manual
   configuration. Same-tenant + Unified RBAC produced automatic connection.

## 4. Validation

The lab is proven only if a live event travels the full pipeline. It does.

| Check | Method | Result |
|---|---|---|
| Workspace exists, queryable | Sentinel → Logs → `search *` | ✅ returns data |
| Sentinel enabled | Trial banner | ✅ 2026-07-19 → 2026-08-19, 10 GB/day free |
| Connector connected | Data connectors / Defender portal SIEM workspaces | ✅ Connected, Primary |
| **Cost-safe — raw events NOT streaming** | `DeviceEvents` in **Sentinel Logs** | ✅ **table absent** (query fails to resolve) — raw streaming off, billed path not running |
| **Pipeline — event reaches Sentinel** | Detection test → `SecurityIncident` in Sentinel | ✅ "Execution incident on one endpoint", **ProviderName: Microsoft XDR** |

### The sync latency

| Stage | Time (converted to UTC) |
|---|---|
| Detection test → Defender alert (Lab 03 measure) | ~2 min |
| Defender alert → Sentinel `SecurityIncident` | **~2 min** |

Defender→Sentinel incident sync arrived in ~2 minutes — far under the 10–30 min a
fresh connector is often quoted at, consistent with every latency this tenant has
produced. **Timezone caution (fifth occurrence):** the Defender alert renders in
local time, Sentinel `TimeGenerated` in UTC — convert before computing, or a
phantom multi-hour gap appears.

## 5. Evidence

The synced incident carried `ProviderName: Microsoft XDR` — the proof it arrived
*through the connector from Defender*, not from some other source. `FirstActivityTime`
(event origin) and `LastModifiedTime` (Sentinel arrival) bracket the end-to-end
travel. Identifiers in the row (incident GUID, owner UPN/objectId) are not
reproduced here per `SANITIZATION.md`; the finding is the arrival and provenance,
not the GUID.

## 6. Failures & Fixes

**`SecurityAlert` empty while `SecurityIncident` had data.** The first sync
delivered the **incident wrapper** before the discrete alert row, so a query
against `SecurityAlert` returned nothing while the incident was already present.
`search *` (which scans all tables) found it where `SecurityAlert | take 10` had
missed it. The lesson: to confirm Defender→Sentinel flow, query `SecurityIncident`
or `search *`, not only `SecurityAlert` — the incident is the leading indicator.

**Historical incidents do not backfill.** Queries over 7 days returned nothing for
incidents created *before* the connector existed (Lab 03's original incident). The
Defender XDR connector is a **forward stream** — it syncs incidents created after
connection, not history. Data flow must be proven with a *fresh* event, which is
why the detection test was re-run.

**The Logs blade opens in Simple mode.** The current Log Analytics Logs experience
defaults to a point-and-click "Simple mode" with no text editor; writing KQL
requires switching to **KQL mode**. The classic blade opened straight into the
editor — a portal change worth knowing (`docs/navigation.md`).

### Retention and the data lake

Two workspace-level findings belong to this lab and were measured after the build.

**Table retention (`POS-102`).** Read 2026-08-15/16, every table in the workspace carried Analytics 30 days and Total 30 days — no archive tier beyond the interactive window, so the gap long-term retention exists to fill was zero. That dated observation stands. **Re-measured 2026-09-01:** the pattern still holds across the workspace *except* `Usage` and `AzureActivity`, which now render **90/90**. Whether those two reflect platform-fixed defaults, a change since the earlier read, or a rendering difference is **NOT MEASURED**; the exception is recorded, not explained.

**The data lake tier (`POS-103`).** Provisioned and integrated, holding no data — a fourth instance of the provisioned-but-inert pattern this section kept finding. Read 2026-09-01, the Tables surface still reports a **Data lake tier of 0** against 182 Analytics-tier tables. Integration status and data flow are different facts, and only the first was ever green.

## 7. Analysis

**Sensor vs connector — different layers, different jobs.** A *sensor* produces
telemetry: the Defender for Endpoint sensor (SENSE) installed on `LAB-WIN11-01` in
Lab 03 watches the machine from inside and streams to the Defender cloud — it is the
*source*, one per device, software on the endpoint. A *connector* moves telemetry:
the Defender XDR connector is a cloud-to-cloud pipe, no software anywhere, that
forwards already-collected data from Defender's service into the Sentinel workspace
— tenant-level, one per source. The Lab 06 ASR event was *generated by the sensor*,
*detected by Defender*, and *forwarded by the connector*: three layers, three roles.
Diagnostically this matters — no data from a device is a sensor problem; data in
Defender but not Sentinel is a connector problem, fixed differently.

**Defender Advanced Hunting vs Sentinel Logs — same KQL, different stores, different
cost.** Both use KQL, but they query different databases. Defender Advanced Hunting
(`security.microsoft.com`) queries Defender XDR's own data lake — the raw `Device*`
tables (`DeviceEvents`, `DeviceProcessEvents`, …), everything the sensor produces,
**free**, with the timestamp column `Timestamp`. Sentinel Logs queries the Log
Analytics workspace — which holds **only what connectors forward** (`SecurityIncident`,
`SecurityAlert`), **billed** by ingestion, with the timestamp column `TimeGenerated`.
This is why `DeviceEvents` works in Defender hunting but fails to resolve in Sentinel
Logs: same query, same language, different store — one has the raw telemetry, the
other only the forwarded alerts. It is also the whole cost model: the raw endpoint
telemetry stays free in Defender's lake and is *not* duplicated into the billed
Sentinel store. If a future need required correlating `DeviceEvents` with a non-Defender
source *inside* Sentinel, raw streaming would be enabled and paid for. This lab does
not, so it isn't — the verified cost-safe state (§4). The practical upshot: the
project's existing `kql/` queries are portable — the language transfers; only the
store and its cost change.

**The pipeline, proven with data:**

```
Endpoint  (LAB-WIN11-01 — Lab 03 sensor)
   │  detection test
Defender for Endpoint  (EDR alert)
   │
Defender XDR  (incident correlation)
   │  connector, ~2 min, forward-only
Microsoft Sentinel  (SecurityIncident, ProviderName: Microsoft XDR)  ✅
```

Every arrow is measured; every stage is proven from a single live event. This is
the aggregation the whole section was building toward — one endpoint's activity,
onboarded in Lab 03, grouped in Lab 05, blocked and detected in Lab 06, arriving in
the SIEM as a correlated, queryable incident.

## 8. References

- `POS-032` (workspace + connector + cost-safe state), `POS-026` (Unified RBAC),
  `POS-024` (directory role ≠ Azure RBAC), `POS-029`/Lab 03 (the sensor)
- `DET-001`, `DET-002` — the detections whose alerts now have a SIEM to arrive in
- Microsoft Learn — Onboard Microsoft Sentinel; Connect Microsoft Defender XDR
