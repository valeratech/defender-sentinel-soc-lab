# Portal Navigation Index

Portal paths for every setting this project configures or verifies, each with the
date the path was last confirmed present. **Azure and Defender rename and relocate
these regularly** (this project has already hit "core folders" → "system folders"
in the ASR levels, and Microsoft is migrating Sentinel into the Defender portal by
2027). A path with a *confirmed* date says "this was true on this date" — if it has
moved since, that date is why. Treat it like the KB's `Sources checked`, not as a
standing guarantee.

Paths are written portal-first because the portal is what changes; the *setting*
being reached is stable even when its location is not.

## Microsoft Defender — `security.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| Unified RBAC — roles & permissions | System → Permissions → Roles | 2026-07-17 |
| Unified RBAC — workload activation | System → Permissions → Roles → Activate workloads / Workload settings | 2026-07-17 |
| Custom role — member assignment | System → Permissions → Roles → *(role)* → Assignments → ⋮ → Edit | 2026-07-19 |
| Endpoint onboarding package | System → Settings → Endpoints → Onboarding | 2026-07-18 |
| Defender ↔ Intune connection | System → Settings → Endpoints → Advanced features → Microsoft Intune connection | 2026-07-17 |
| Device discovery — on/off | System → Settings → Endpoints → Advanced features → Device discovery | 2026-07-19 |
| Device discovery — mode (Basic/Standard) | System → Settings → Device discovery → Discovery setup | 2026-07-19 |
| Device groups | System → Settings → Endpoints → Permissions → Device groups | 2026-07-19 |
| ASR report (detections / configuration) | Reports → Attack surface reduction rules | 2026-07-19 |
| Device inventory | Assets → Devices | 2026-07-18 |
| Device timeline | Assets → Devices → *(device)* → Timeline | 2026-07-19 |
| Incidents & alerts | Incidents & alerts → Incidents / Alerts | 2026-07-18 |
| Advanced hunting | Hunting → Advanced hunting | 2026-07-18 |

## Microsoft Entra — `entra.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| Create a user | Users → All users → New user | 2026-07-19 |
| User usage location | Users → *(user)* → Properties → Usage location | 2026-07-19 |
| Create a security group | Groups → New group (type: Security) | 2026-07-19 |
| Device settings (join permissions) | Devices → Device settings | 2026-07-17 |

## Azure — `portal.azure.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| VM role assignments (IAM) | Virtual machines → *(VM)* → Access control (IAM) → Role assignments | 2026-07-17 |
| VM Run command | Virtual machines → *(VM)* → Run command → RunPowerShellScript | 2026-07-17 |
| VM Bastion session | Virtual machines → *(VM)* → Connect → Bastion | 2026-07-18 |
| VM reset password | Virtual machines → *(VM)* → Help → Reset password | 2026-07-18 |
| VM auto-shutdown | Virtual machines → *(VM)* → Operations → Auto-shutdown | 2026-07-17 |

### Microsoft Sentinel — Azure portal / Defender portal

| Setting / view | Path | Confirmed |
|---|---|---|
| Create Log Analytics workspace | Azure → Log Analytics workspaces → Create | 2026-07-19 |
| Enable Sentinel | Azure → Microsoft Sentinel → Create → select workspace | 2026-07-19 |
| Data connectors | Azure → Microsoft Sentinel → *(workspace)* → Data connectors | 2026-07-19 |
| Store-partition census (run on BOTH portals, then diff) | Defender → Advanced hunting *and* Azure → Sentinel → Logs — same query, compare table lists | 2026-07-26 |
| Sentinel Logs (KQL) | Azure → Microsoft Sentinel → *(workspace)* → Logs — **switch Simple mode → KQL mode to write queries** | 2026-07-19 |
| SIEM workspace status (unified) | security.microsoft.com → Settings → Microsoft Sentinel → SIEM workspaces | 2026-07-19 |
| Content hub (solutions) | Azure → Microsoft Sentinel → *(workspace)* → Content hub | 2026-07-19 |

### First-party connectors — Azure Activity & Entra ID (Lab 08)

| Setting / view | Path | Confirmed |
|---|---|---|
| Azure Activity (Method B — worked) | Subscriptions → *(sub)* → Activity log → Export Activity Logs → + Add diagnostic setting → law-soc-lab | 2026-07-25 |
| Azure Activity (Method A — failed) | Data connectors → Azure Activity → Launch Azure Policy Assignment wizard | failed x2 |
| Entra ID connector | Data connectors → Microsoft Entra ID → Open connector page → select log types → Apply | 2026-07-25 |
| Verify Entra diagnostic setting | Entra ID → Monitoring & health → Diagnostic settings (AzureSentinel_law-soc-lab) | 2026-07-25 |

**Method A vs B:** for a single subscription the manual diagnostic setting (B) is
simpler and correct; the policy wizard (A) only earns its complexity across many
subscriptions and failed here on managed-identity/session. **Count subscriptions.**

**Table name by surface — corrected 2026-07-26.** These are **not** two names for one
dataset, which is what this note previously said. `SigninLogs` is a Log Analytics
workspace table written by the Entra diagnostic setting and scoped by the log types
you selected; `EntraIdSignInEvents` is a Defender XDR lake table written by XDR
regardless of your connector. On the unified Defender surface **both resolve at once**
with very different counts. See Lab 08 §5 and the store-partition method below.

### Windows Security Events ingestion (agent path)

| Setting / view | Path | Confirmed |
|---|---|---|
| Install the solution | Content hub → search "Windows Security Events" → Install | 2026-07-25 |
| Create the DCR | Data connectors → Windows Security Events via AMA → Create data collection rule | 2026-07-25 |
| Verify DCR association | Monitor → Data Collection Rules → *(rule)* → Resources | 2026-07-25 |
| Confirm AMA installed | VM → Extensions → AzureMonitorWindowsAgent | 2026-07-25 |

Selecting the VM in the DCR's Resources tab auto-installs the Azure Monitor Agent —
no separate agent step. Windows Security events via **direct AMA** land in
**`SecurityEvent`**; via a **WEF/WEC collector** they land in **`WindowsEvent`** —
same source log, different tables, different rule coverage. Collection tier
(All/Common/Minimal/Custom) is the ingestion cost lever; `SecurityEvent` bills fully
without Defender for Servers P2.

**Defender Advanced Hunting is NOT Sentinel Logs — but the unified portal reaches
both.** Same KQL, different data stores; from `security.microsoft.com` a single
query can return tables from each, which is why a census there is not a statement
about what your workspace holds. Run it on **both** portals and diff the table lists:
what survives into the Azure run is workspace-resident and billable, what drops out
is XDR-native and free (`kql/sentinel/store-partition-diff.kql`, measured 2026-07-26). Defender hunting (`security.microsoft.com` → Advanced hunting) queries
Defender XDR's free raw lake — the `Device*` tables, column `Timestamp`. Sentinel
Logs queries the Log Analytics workspace — only connector-forwarded data
(`SecurityIncident`, `SecurityAlert`), billed, column `TimeGenerated`. A `Device*`
query works in the first and fails to resolve in the second. Confirm which store
before querying, and mind the column-name difference.

### Email & collaboration — Attack simulation training (Lab 09)

| Setting / view | Path | Confirmed |
|---|---|---|
| Attack simulation training | Email & collaboration → Attack simulation training | 2026-07-26 |
| Launch a campaign | *(above)* → Simulations → Launch a simulation → **single simulation** (not automation) | 2026-07-26 |
| Campaign report | *(above)* → Simulations → *(campaign)* → Report / Users / Details | 2026-07-26 |
| Campaign timeline | *(campaign)* → View Activity Timeline | 2026-07-26 |
| Excluded users | *(campaign)* → Report → View excluded users or groups | 2026-07-26 |
| Payload / training / notification library | Attack simulation training → Content library | 2026-07-26 |
| Repeat offender & training thresholds | Attack simulation training → Settings | *(pending — tab not opened)* |
| Unified audit logging (portal) | System → Audit → Start recording user and admin activity | 2026-07-26 — **could not complete, see below** |
| Exchange message trace | Email & collaboration → Exchange message trace | 2026-07-26 |
| Action center (pending / history) | Actions and submissions → Action center | 2026-07-27 |
| Microsoft Secure Score | Exposure management → Microsoft Secure Score | 2026-07-27 |
| Sentinel UEBA | System → Settings → Microsoft Sentinel → UEBA (three acts: toggle, directory sync, connect sources) | 2026-07-28 |
| Sentinel analytics rules | Microsoft Sentinel → Configuration → Analytics | *(pending — not yet visited)* |
| Alert policies (49; 48 built-in) | Email & collaboration → Policies & rules → Alert policy | 2026-07-28 |
| Alert tuning | Settings → Microsoft Defender XDR → Rules → Alert tuning | 2026-07-28 |
| Threat analytics | Threat intelligence → Threat analytics | 2026-07-27 |
| Custom indicators (IOC) | Settings → Endpoints → Rules → Indicators (file hash / IP / URL-domain / certificate) | 2026-07-27 |
| Enforcement scope (MDE settings mgmt) | Settings → Endpoints → Configuration management → Enforcement scope | 2026-07-27 |
| Secure Score history (exportable, 185 rows) | *(above)* → History → Export | 2026-07-27 |
| Submissions (6 tabs, incl. User reported) | Actions and submissions → Submissions | 2026-07-27 |
| User reported settings | Settings → Email & collaboration → User reported settings — **opening this page creates the policy object** (`POS-040`) | 2026-07-27 |

**Audit logging is not reliably reachable from the portal.** System → Audit rendered
two independent faults at once and its enable button raised a Client Error. The
working path is Exchange Online PowerShell (`Set-AdminAuditLogConfig`), and the
verifying read **must** run in the EXO endpoint — the same cmdlet in Security &
Compliance PowerShell returns `False` even when auditing is on. See `POS-035`.

**Simulation campaign dates anchor to the review-page submit timestamp**, not to the
recorded "Simulation launched" event. The launched event anchors nothing — Lab 09 §5.


## Which surface answers which question

Navigation is not only "where is the setting" — it is also "which view answers my
question." For endpoint activity, the surfaces are not interchangeable (Lab 06 §7):

| Question | Surface |
|---|---|
| Is something attacking this box that needs attention? | Incidents & alerts |
| What happened on this device, step by step? | Assets → Devices → Timeline |
| Is an ASR rule firing, and how often? | Advanced hunting *(the ASR report omits locally-set rules — `POS-031`)* |
| Hunt a pattern across all devices? | Advanced hunting (`DeviceEvents`) |
| Did a phishing *simulation* leave telemetry? | Nowhere — the payload is absent from `EmailEvents` and `EmailUrlInfo` (`POS-037`) |
| Was anything actually *remediated*? | Actions and submissions → Action center → History. Empty ≠ broken — a detection with no remediable artifact logs nothing (Lab 03 §7) |
| Are my ASR rules actually configured? | **Ask both.** Exposure management → Secure Score → Recommended actions says Completed 9/9; the ASR report says Rules off. Same rules, same tenant (Lab 06 §7) |
| Is a workspace table actually *billable*? | Not the census — `Usage \| where IsBillable == true`. Residency and billability are different questions (`POS-044`, Lab 08 §7) |
| Where do user-reported phish actually go? | Not answerable from the portal — `Get-ReportSubmissionPolicy` / `Get-ReportSubmissionRule` in EXO PowerShell, and even then the effective mailbox is in neither (`POS-040`) |
| Who holds a Defender role? | System → Permissions → Roles → *(role)* → Edit assignment *(count only shown until opened)* |
