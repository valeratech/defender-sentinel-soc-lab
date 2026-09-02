# Lab 07 — Windows Security Events via AMA

| Field | Value |
|---|---|
| **Domain** | Ingest data into Microsoft Sentinel |
| **Objectives** | Deploy a Windows Server VM cost-safely; install the Azure Monitor Agent via a Data Collection Rule; ingest Windows Security events into `SecurityEvent` at a scoped (Common) tier; verify the pipeline and read what the telemetry actually says |
| **Depends on** | Lab 04 (Sentinel workspace, the ingestion target), POS-015 (budgets raised for this VM) |
| **Status** | ✅ Built, documented, validated |
| **Built** | 2026-07-25 |

> The first ingestion lab of the Sentinel half. Where Lab 04 proved the
> Defender-to-Sentinel *connector* path (alerts/incidents, free), this proves the
> *agent* path: a Windows machine's own Security log, collected by the Azure
> Monitor Agent through a Data Collection Rule, landing in the billed
> `SecurityEvent` table. Two different ingestion mechanisms, two different cost
> profiles.

---

## 1. Objective

Get Windows Security telemetry into Sentinel and read it honestly. A second VM —
Windows Server — is onboarded to Sentinel not through the Defender connector but
through the **Azure Monitor Agent (AMA)**, installed automatically when a **Data
Collection Rule (DCR)** is associated to it. The DCR scopes *what* is collected;
the events land in the **`SecurityEvent`** table; and the verification is not just
"did rows appear" but "what do those rows actually mean" — because the first thing
the data shows is that a machine nobody logged into still emits logon events.

## 2. The VM — deployed cost-safe

The lab needs a Windows host. It was built deliberately against the project's cost
constraints (out-of-pocket Azure, three clocks), and the deployment choices are
the point as much as the ingestion:

| Choice | Value | Why |
|---|---|---|
| Size | Standard_D2s_v3 | Smallest generally-available general-purpose size in West US for this subscription (B-series and DS1_v2 were unavailable) |
| Image | smalldisk Windows Server 2022 Datacenter Gen2 | 30 GB OS disk instead of 127 GB — the disk is a meter that bills even deallocated |
| OS disk | **Standard HDD (LRS)** | Changed from the Premium_LRS default; ~$4/mo cheaper for zero functional loss on a lab VM |
| Security type | **Standard** | Matches VM 1 (POS-018) — no vTPM. Trusted Launch would have introduced a device-attestation capability VM 1 lacks, a posture divergence with no lab purpose here |
| Public inbound | **None** | No open ports from the internet |
| Public IP | **None** (dissociated and deleted) | The default deployment attached one despite inbound None; removed entirely |
| Access | **Azure Bastion as `labadmin`** | See §3 |
| Auto-shutdown | 23:00 Pacific + email | Matches VM 1 (POS-023) — the backstop cost control |
| Patch orchestration | Manual | A deallocated lab VM does not want Azure powering it on to patch; the no-inbound posture neutralises the usual "manual patching is risky" concern |
| Boot diagnostics | Disabled | Saves the diagnostics storage cost |

Region **West US** (matching VM 1 and the `law-lab-01` workspace) and resource
group `rg-soc-lab` (so teardown stays one `az group delete`).

## 3. Access: Bastion vs RDP — a deliberate choice

VM 1 (Lab 03) exposes RDP to the internet — recorded as `POS-019`, a real
weakening. This VM deliberately does **not**. Inbound is **None**, no public IP
exists, and access is through **Azure Bastion** as the local `labadmin` account.

The tradeoff, recorded so the choice is legible later:

| | RDP (public 3389) | Azure Bastion |
|---|---|---|
| Internet exposure | Port open to the entire internet — brute-forced within minutes of going live | **Zero** open ports; VM has no public IP |
| Cost | Free (just the VM) | Bastion host bills per hour (~$0.19/hr Basic) — *more than the VM* while running |
| Clipboard | Works, sometimes finicky | Built-in text clipboard sharing |
| File transfer | Drive redirection | Limited on Basic SKU |
| Native feel | Snappy, multi-monitor | Browser tab, no multi-monitor |
| Quirk | — | Some SKUs reject `domain\` / `.\` username formats — bare username required |

The decision here favours **Bastion + inbound None**: the security win (no
internet-facing surface at all) outweighs Bastion's running cost, especially since
Bastion is already deployed for VM 1. The result is a *better* posture than VM 1 —
this VM cannot be reached from the internet at all. The standing cost consequence:
Bastion is the meter to watch — it bills more than the VM while up, so it is a
per-session teardown decision, not a leave-it-running one.

**Amended 2026-08-12 — this note is SKU-specific.** It was written against the
**Basic** SKU (~$0.19/hr) deployed here. A **Developer** SKU host created and
deleted in Lab 21 produced **no meter row at all** in a per-meter export
covering the subscription's full usage history, against Sentinel's daily
zero-cost rows as control. Teardown discipline stands for Basic and Standard;
it is not required by cost for Developer. `POS-099`.

## 4. Build: DCR, agent, collection tier

1. **Content hub** → installed the **Windows Security Events** solution. (It did
   **not** auto-install its stated dependency, *Endpoint Threat Protection
   Essentials* — see §7. The detection layer that solution provides is deferred to
   a later analytics-rule lab; ingestion does not need it.)
2. **Data connectors** → *Windows Security Events via AMA* → **Create data
   collection rule** (`dcr-winsec-lab`, in `rg-soc-lab`).
3. **Resources** → selected `LAB-SRV-DEFENDER-01`. Selecting the VM here is what
   **auto-installs the Azure Monitor Agent** — no separate agent step.
4. **Collect** → **Common**, not All. This is the cost decision (§6).
5. **Review + create.** AMA extension deployed to the VM in **under 5 minutes**.

## 5. Validation

Verified in order — agent alive, then data flowing.

| Check | Query | Result |
|---|---|---|
| Agent alive | `Heartbeat \| where TimeGenerated > ago(30m)` | ✅ 10 heartbeats, `SCAgentChannel: Direct`, AMA v1.43.0.0 |
| Events landing | `SecurityEvent \| where TimeGenerated > ago(30m)` | ✅ rows present — EventID 4688 (process creation), 4673 (privileged service) |
| Which table | (the above) | ✅ `SecurityEvent`, **not** `WindowsEvent` — confirms the direct-AMA path |

**Timing:** `Heartbeat` and `SecurityEvent` were both empty at ~5 minutes
post-install (the `Heartbeat` table did not yet exist — `KS204 table not found`,
because a Log Analytics table is created on first write). Both populated shortly
after. Empty-then-populates is propagation, not failure — the same discipline as
every prior lab. The DCR-to-VM association was confirmed in the portal
(`dcr-winsec-lab` → Resources → the VM) before concluding it was lag.

## 6. The cost decision — Common, not All

The DCR's collection tier is the single largest cost lever in this lab. The Windows
Security log is high-volume — every logon, privilege use, and process creation. The
tiers:

- **All Security Events** — the firehose. Every audit event. Convenient in a demo,
  expensive in practice.
- **Common** — a curated set of the security-relevant IDs (the 4624/4625/4672/4688
  family). Chosen here.
- **Minimal** — smaller still.
- **Custom (XPath)** — arbitrary scoping to specific Event IDs.

**Common was chosen deliberately.** And the reason it matters *here specifically*:
the `SecurityEvent` table has a free daily allowance **only under Defender for
Servers Plan 2** (500 MB/day per licensed server). This environment does **not**
have Defender for Servers enabled (Defender for Cloud was declined at Lab 04), so
`SecurityEvent` ingestion **bills fully** against the 10 GB/day trial allowance.
There is no free tier cushioning "All" here — the scoping is the only cost control.

## 7. Findings

**1. The direct-AMA path lands in `SecurityEvent`.** `SCAgentChannel: Direct`
confirms this is the per-machine AMA path, not WEF/WEC. The events are in
`SecurityEvent` (rich rule coverage) and *not* `WindowsEvent` (the forwarded-events
table). The other half of that distinction — `WindowsEvent`, populated by a
WEF/WEC collector — was **not** exercised: it needs a collector plus source
machines, an on-prem topology this environment does not have. So `SecurityEvent`
is *observed*; `WindowsEvent` is *documented, not observed*.

**2. Hostname truncation — Azure name ≠ OS hostname.** The VM is named
`LAB-SRV-DEFENDER-01` (19 characters) in Azure, but Windows caps the NetBIOS
computer name at 15, so the `Computer` field in every event reads
**`LAB-SRV-DEFENDE`**. A KQL filter of `Computer == "LAB-SRV-DEFENDER-01"` returns
nothing; matching requires the truncated name or `startswith`. Flagged as a risk at
VM creation, confirmed here in the data.

**3. Machine-context events — the VM is WORKGROUP-joined.** The events show the
account as `WORKGROUP\LAB-SRV-...` with AccountType `Machine`. This confirms the VM
is **WORKGROUP-joined, not domain-joined** (consistent with the Entra-only, no-AD
environment), and the 4688 process-creation events are the machine running its own
processes, not user activity.

**4. "Successful logon" (4624) does not mean someone logged in.** The VM was
started and *never signed into* — yet the Security log carried 4624 "an account was
successfully logged on" events. Breaking down by `LogonType`: **2× Type 5 (service
logon), and zero of any other type** (the `LogonType == 2` interactive query
returned nothing). Type 5 is the Service Control Manager starting SYSTEM services —
machine activity, no human. The lesson is an analyst one: the raw 4624 count is
meaningless without `LogonType`. Type 2 (interactive), 3 (network), and 10
(RemoteInteractive/RDP-Bastion) are the human-relevant ones; Type 5 is noise. Here,
every "logon" on a machine nobody touched was a service starting — exactly as it
should be, and exactly the kind of thing that misleads a count-based query.

## 8. Deferred

- **Endpoint Threat Protection Essentials** (the `SecurityEvent` analytics rules
  and hunting queries) was not installed — it did not auto-install with the Windows
  Security Events solution, contrary to the source guidance, and ingestion does not
  require it. Detection *on* this data (analytics rules firing against
  `SecurityEvent`) is the natural follow-up, deferred to the alerts/incidents
  response work later in the course.
- **`WindowsEvent` / WEF path** — not exercised (no collector topology); documented
  from the guide, not observed.
- **OS disk → Standard HDD** was applied. Bastion teardown is a per-session cost
  decision (see §3).

## 9. References

- `POS-033` (this VM + DCR + Common-tier ingestion), `POS-015` (budgets raised for
  it), `POS-019` (VM 1's RDP exposure this VM deliberately avoids), `POS-018` (VM
  security type), `POS-032` (the Sentinel workspace this feeds)
- Microsoft Learn — Windows Security Events via AMA connector; Azure Monitor Agent;
  Data Collection Rules
