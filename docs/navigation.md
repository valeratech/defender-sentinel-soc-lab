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

**Table name by surface:** Entra sign-in data is `SigninLogs` in **Sentinel → Logs**
(Log Analytics) but `EntraIdSignInEvents` in **Defender Advanced Hunting** — same
data, two schema names. The `search * | summarize count() by $table` query is the
fastest way to see what's actually arriving and under which name.

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

**Defender Advanced Hunting is NOT Sentinel Logs.** Same KQL, different data
stores. Defender hunting (`security.microsoft.com` → Advanced hunting) queries
Defender XDR's free raw lake — the `Device*` tables, column `Timestamp`. Sentinel
Logs queries the Log Analytics workspace — only connector-forwarded data
(`SecurityIncident`, `SecurityAlert`), billed, column `TimeGenerated`. A `Device*`
query works in the first and fails to resolve in the second. Confirm which store
before querying, and mind the column-name difference.

## Which surface answers which question

Navigation is not only "where is the setting" — it is also "which view answers my
question." For endpoint activity, the surfaces are not interchangeable (Lab 06 §7):

| Question | Surface |
|---|---|
| Is something attacking this box that needs attention? | Incidents & alerts |
| What happened on this device, step by step? | Assets → Devices → Timeline |
| Is an ASR rule firing, and how often? | Advanced hunting *(the ASR report omits locally-set rules — `POS-031`)* |
| Hunt a pattern across all devices? | Advanced hunting (`DeviceEvents`) |
| Who holds a Defender role? | System → Permissions → Roles → *(role)* → Edit assignment *(count only shown until opened)* |
