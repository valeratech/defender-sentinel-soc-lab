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
| Incident queue — time window & filters | Incidents → toolbar right: calendar dropdown (`Last update time`) · below toolbar: `Filter set:` chip row → **Add filter** *(capture the chips with every export — exports honor them silently, row 114)* | 2026-08-06 |
| Manage incident (6 fields; no comments here) | Incidents → *(incident)* → **Manage incident** (top right) — name / severity / tags / assign / status / classification *(one picker, writes Classification + Determination)* | 2026-08-05 |
| Incident comments + full audit trail | Incidents → *(incident)* → **Activities** tab → **Add comment** · grid = per-field change log with before/after values; **Refresh** before trusting the badge/grid pair (row 113) | 2026-08-05 |
| Incident investigation flyout (AIR detail) | Incidents → *(incident)* → **Investigations** tab → *(row)* — `Generated on` here is the alert's birth timestamp (row 118) | 2026-08-05 |
| Detection rules (unified, thin Sentinel view) | Hunting → **Detection rules** — analytics rules render read-only detail pane; run-status columns say `Not available for analytics rules` | 2026-08-05 |
| Automation rules (Sentinel) | Microsoft Sentinel → Configuration → **Automation** → **Automation rules** tab → left rail **Enhanced rules** / **Standard rules**. *Standard = 3 triggers, one workspace, the guide's world; Enhanced = alert-trigger only, tenant-wide. Create-menu path stamps Enhanced by default — switch to Standard for incident triggers* (rows 123–125) | 2026-08-06 |
| Automation rule — free-condition build | Automation → Automation rules → Standard rules → **+ Create** → condition builder arrives empty; Value picker enumerates analytic rules incl. Fusion (row 126) | 2026-08-06 |
| Automation rule — locked-condition build | Microsoft Sentinel → Configuration → Analytics → *(rule)* → **Edit** → **Automated response** tab → **Add new** — condition pre-locked to `Current rule`; trigger pre-set to incident-created; Review + create re-saves the analytics rule | 2026-08-06 |
| Playbooks / Integration profiles | Microsoft Sentinel → Configuration → Automation → **Playbooks** / **Integration profiles** tabs *(Integration profiles opens with a pre-seeded auth-method filter over an empty list)* | 2026-08-06 |
| "Hunting" disambiguation | Three surfaces answer to Hunting: top-level **Hunting** (Advanced hunting + Custom detection rules), Sentinel **Threat management → Hunting** (hypothesis hunts, Preview), and the unified **Detection rules** page — none is the others | 2026-08-06 |
| Advanced hunting | Hunting → Advanced hunting | 2026-07-18 |
| Threat policies (hub) | Email & collaboration → Policies & rules → Threat policies | 2026-08-01 |
| Preset security policies | Threat policies → Templated policies → Preset security policies → Manage protection settings | 2026-08-01 |
| Configuration analyzer | Threat policies → Templated policies → Configuration analyzer | 2026-08-01 |
| Safe Attachments policies | Threat policies → Policies → Safe Attachments | 2026-08-01 |
| Safe Attachments — SharePoint/OneDrive/Teams + Safe Documents | Threat policies → Safe Attachments → **Global settings** (toolbar, not a policy) | 2026-08-01 |
| Safe Links policies | Threat policies → Policies → Safe Links | 2026-08-01 |
| Anti-phishing / anti-spam / anti-malware policies | Threat policies → Policies → *(each)* | 2026-08-01 |
| Tenant Allow/Block Lists | Threat policies → Rules → Tenant Allow/Block Lists | 2026-08-01 |
| DKIM / ARC | Threat policies → Rules → Email authentication settings → DKIM / ARC | 2026-08-01 |
| Advanced delivery (SecOps mailbox, phishing simulation) | Threat policies → Rules → Advanced delivery | 2026-08-01 |
| Quarantine policies | Threat policies → Rules → Quarantine policy | 2026-08-01 |
| Email Explorer (per-message actions, verdicts, export) | Email & collaboration → Explorer → All email | 2026-08-01 |
| Message headers (recipient view) | `outlook.office.com` → *(message)* → ⋯ → View → View message details | 2026-08-01 |
| Email entity page | Email & collaboration → Explorer → *(message subject)* → **Open email entity** — Timeline / Analysis / Attachments / URL / Similar emails / Email preview | 2026-08-01 |
| Message Header Analyzer | Email entity → Analysis → Copy message header → Microsoft Message Header Analyzer | 2026-08-01 |
| Take action (email remediation) | Email entity or Explorer grid → **Take action** — 3 steps: Choose actions / Choose target entities / Review and submit | 2026-08-01 |
| Investigations (AIR) | Investigation & response → Actions & submissions → Action center → **Open investigation page**; also linked from the AIR submission banner | 2026-08-01 |
| Action center | Investigation & response → Actions & submissions → **Action center** — Pending / History | 2026-08-01 |
| Recover a soft-deleted message (end user) | `outlook.office.com` → Deleted Items → **Recover items deleted from this folder** → Deletions | 2026-08-01 |
| Incidents — **structural path** | Investigation & response → **Incidents & alerts** → **Incidents**. *The `Microsoft Sentinel` subtree carries `Search`, `Threat management`, `Content management`, `Configuration` — and **no incidents**. The queue is unified across Defender and Sentinel, so it cannot live in the workspace-scoped Sentinel remainder (row 150)* | 2026-08-08 |
| **Rail items may be pins, not structure** | `Incidents` and `Cases` render on the top-level left rail **because they are pinned** (pin glyph beside each in the tree). A pinned shortcut is per-operator configuration. **Do not document a rail position as a path** — it will not reproduce for anyone else | 2026-08-08 |
| Incident — audit trail | Incidents → *(incident)* → **Activities** tab. Columns include `Performed by`, **`Trigger`** (`Automated` / `Manual`), `Activity status`. *A playbook's own comment renders `Trigger: Manual` with empty status — filtering on `Automated` loses it (row 146)* | 2026-08-08 |
| Incident — entity detail | Incidents → *(incident)* → Attack story → **Incident graph** → *(node)* → right-click → `User details`. **This opens the identity page — the directory's view, not the incident entity object.** For the entity as the playbook receives it, query `SecurityAlert`'s `Entities` column (row 152) | 2026-08-08 |
| Advanced hunting (interactive KQL) | Investigation & response → **Hunting** → **Advanced hunting**. Header states `Selected workspace: law-lab-01`. **Now resolves Log Analytics workspace tables** (`SecurityAlert` ran here) though the schema tree lists XDR tables only (row 151) | 2026-08-08 |
| Sentinel **Search** is not interactive KQL | Microsoft Sentinel → **Search** → tabs `Search` / `Saved Searches` / `Restoration`. This is the **search-jobs** feature over basic and archived logs, saved 14 days, with a `Restore` path — *not* the query surface. It also pre-seeds a `Table : SecurityEvent` filter chip | 2026-08-08 |

## Microsoft 365 admin center — `admin.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| **Mail-enabled security group** | Teams & groups → Active teams & groups → **Security groups** tab → Add a mail-enabled security group | 2026-08-01 |
| Subscription terms (licences, renewal, recurring billing) | Billing → Your products → *(product)* | 2026-08-01 |
| Licence assignment count | Billing → Your products — *Assigned / Available / Purchased quantity* | 2026-08-01 |

> ⚠️ **Active teams and groups opens on the *Teams & Microsoft 365 groups* tab**, whose
> primary action is *Add a Microsoft 365 group* — the wrong object for a policy scope.
> An M365 group provisions a SharePoint site and group mailbox as side effects. The
> **Security groups** tab exposes *Add a security group* and *Add a mail-enabled security
> group* side by side; that pair states the distinction more clearly than either wizard's
> own text, and the mail-enabled wizard's description ("give people access to resources
> such as SharePoint sites") actively invites the confusion.

## Microsoft Entra — `entra.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| Create a user | Users → All users → New user | 2026-07-19 |
| User usage location | Users → *(user)* → Properties → Usage location | 2026-07-19 |
| Create a security group | Groups → New group (type: Security) | 2026-07-19 |
| Device settings (join permissions) | Devices → Device settings | 2026-07-17 |
| Security defaults state | **Entra ID → Overview → Properties** tab → (bottom) `Security defaults` → **Manage security defaults** → right-hand panel, dropdown reads `Enabled` / `Disabled (not recommended)`. *The panel is editable with a `Save` — `Cancel` out after reading* | 2026-08-08 |
| Conditional Access policy list | **Entra ID → Conditional Access → Policies**. *An empty tenant renders the `What is Conditional Access?` / `Get Started` explainer instead of an empty grid — the absence of a table is the answer, not a failure to load* | 2026-08-08 |
| **Registration campaign** (the MFA nudge nobody configured) | **Entra ID → Authentication methods → Registration campaign**. `State` may read **`Microsoft managed`** — a third value beside Enabled/Disabled, meaning Microsoft holds the state and may change it without administrator action. Every dependent field (`Authentication method`, `Days allowed to snooze`, `Limited number of snoozes`) is **greyed** (`POS-085`, row 149) | 2026-08-08 |
| Sign-in logs (interactive) | **Entra ID → Conditional Access → Monitoring → Sign-in logs** → tab **`User sign-ins (interactive)`**. Columns to read: `Status`, `Sign-in error code`, **`Conditional Access`** (`Applied` / `Not Applied`), **`Authentication requirement`** (`Single-factor` / `Multifactor`). *Codes seen here: `50126` bad password, `50055` expired password, `50072` user must enroll in MFA, `50140` keep-me-signed-in interrupt* | 2026-08-08 |
| Per-user MFA (legacy state) | **Entra ID → Multifactor authentication**. *Landing view not confirmed in this build — recorded as unverified rather than asserted* | — |

## Azure — `portal.azure.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| VM role assignments (IAM) | Virtual machines → *(VM)* → Access control (IAM) → Role assignments | 2026-07-17 |
| VM Run command | Virtual machines → *(VM)* → Run command → RunPowerShellScript | 2026-07-17 |
| VM Bastion session | Virtual machines → *(VM)* → Connect → Bastion | 2026-07-18 |
| VM reset password | Virtual machines → *(VM)* → Help → Reset password | 2026-07-18 |
| VM auto-shutdown | Virtual machines → *(VM)* → Operations → Auto-shutdown | 2026-07-17 |
| RG role assignment (scope check!) | Resource groups → *(RG)* → Access control (IAM) → **+ Add → Add role assignment** — *read the breadcrumb before assigning: `(RG) \| Access control` vs `(workspace) \| Access control` are one click apart and produce different scopes* | 2026-08-05 |
| Role assignment state (the truth surface) | *(scope)* → Access control (IAM) → **Role assignments** tab — State column: `Active Permanent` vs `Eligible time-bound`. **The RG wizard's Assignment type tab defaults to Eligible; the wizard summary does not surface it** (`POS-072`, row 122) | 2026-08-05 |
| PIM — activate an Azure role (user side) | Search `Privileged Identity Management` *(listed as "Microsoft Entra Privileged Identity Management")* → **Tasks → My roles → Azure resources** → Eligible assignments → *(row)* → **Activate** — *not* Manage → Azure resources (admin config), *not* the Entra roles tab | 2026-08-06 |
| PIM — active/expired elevations, early deactivate | Same blade → **Active assignments** / **Expired assignments** tabs; active rows carry **Deactivate** | 2026-08-06 |
| Playbook / logic app — two routes to the same resource | **(a)** `security.microsoft.com` → Microsoft Sentinel → Configuration → Automation → **Playbooks** tab → *(name)*. **(b)** `portal.azure.com` → **All services → Logic apps** → *(name)*. Route (a) lists only logic apps tagged `LogicAppsCategory: security` **and** carrying a Sentinel trigger; route (b) lists every logic app in the subscription. Neither is a superset by accident — they answer different questions | 2026-08-07 |
| Playbook deployment from template | Sentinel → Configuration → Automation → **Playbooks** tab → left rail **Playbook Templates** → *(template row)* → detail pane → **Create Playbook**. *Read `Trigger type` in the pane before creating — three variants of the reset-password template differ in that field alone and are otherwise byte-identical* | 2026-08-07 |
| Playbook create menu (four starting points) | Automation → **Playbooks** tab → **+ Create ▸ Logic App playbook ▸** → incident / alert / entity / blank. *Re-parented: a `Generated playbook` item now sits above, pushing the original four into a submenu* | 2026-08-07 |
| Deployment wizard — workspace scope | Deploy blade → Basics → check **Enable diagnostic settings** → the workspace renders as **plain text with no chevron or border**; clicking the name opens a **Workspace scope** flyout with a checkbox and Apply. A selection control with no affordance | 2026-08-07 |
| Deployment wizard — connection state | Deploy blade → **Connections** step → rows ship **collapsed**, showing only *"New connection will be configured"*. Expand each for *"No connections available"* in red. The **Review + Create** step is the only screen that says *"Authorize this connection after deployment"* | 2026-08-07 |
| Logic app designer | All services → **Logic apps** → *(app name)* → **Development Tools → Logic app designer** — blade title becomes `*(app name)* \| Logic app designer` | 2026-08-07 |
| Designer — **`Save` is mandatory and unsignalled** | Designer toolbar → **Save**. Authorizing a connection clears the card error, empties the Flow Checker, and drops the `Connections` red dot **without persisting anything**. No dirty-state marker, no title asterisk, no confirmation on navigate-away. The only tell is `Save` going from greyed to enabled | 2026-08-07 |
| Automation rule — attach a playbook | `security.microsoft.com` → Sentinel → Configuration → **Automation** → **Automation rules** tab → left rail **Standard rules** → **+ Create**. Conditions/Actions/Expiration/Order do **not** render until a Trigger is selected. `Order` auto-fills to the next free slot | 2026-08-07 |
| **`Manage playbook permissions` is a doc link, not a control** | Inline beside the playbook dropdown in the rule form. Opens `learn.microsoft.com`, not a blade. No permission grant is reachable from the rule-creation form; the same toolbar on the Automation rules grid has no equivalent control either | 2026-08-07 |
| Failed portal operation — where the error actually lives | The Defender portal toast auto-dismisses and its **bell → Notifications** panel retains nothing (*"New notifications from the current session will appear here"*). Authoritative record: `portal.azure.com` → Resource groups → *(RG)* → **Activity log** → Timespan **Last 6 hours** → the `Failed` row → **JSON** tab. The Summary line names no cause | 2026-08-07 |
| Connection authorization (delegated) | Designer → expand `For each` → expand `Condition` → **True** branch → *(the erroring card)* → parameters pane → **Change connection → Add new → sign in**. Pane then reads `Connected to <upn>` | 2026-08-07 |
| Logic app — workflow JSON | Logic apps → *(app)* → **Development Tools → Logic app code view** *(also reachable as `Code view` in the designer toolbar)* | 2026-08-07 |
| Designer — error list (Flow Checker) | Designer toolbar → **Errors** *(red dot)* → Flow Checker pane, `Errors (n)` / `Warnings (n)`. **The canvas does not show errors on collapsed containers** — the reset-password template's one error sits two levels down, inside `For each` → `Condition` → True branch | 2026-08-07 |
| Designer — per-connection state | Designer toolbar → **Connections** *(red dot)* → flyout, **collapsed by default**; expand each connector for status and the list of actions using it | 2026-08-07 |
| Designer — action authentication | Designer canvas → click the **card body** *(not the `+` on the connector line, which inserts a new action)* → **Parameters** tab → **Advanced parameters** → `Authentication`. Managed-identity actions name the identity and audience here | 2026-08-07 |
| Designer — run-after config | Designer canvas → *(card)* → **Settings** tab → **Run after**. The small green/grey/red dot cluster above a card is this setting rendered | 2026-08-07 |
| Designer — credential logging | Designer canvas → *(card)* → **Settings** tab → **Security** → `Secure inputs` / `Secure outputs`. **Both ship Off** — the reset-password template therefore writes the plaintext password into run history | 2026-08-07 |
| Logic app — managed identity + Azure RBAC | Logic apps → *(app)* → **Settings → Identity** → **System assigned** tab → `Azure role assignments`. *Note `Settings` is both a collapsible group and an item inside it; `Identity` sits below `Access keys`* | 2026-08-07 |
| Logic app — trigger network exposure | Logic apps → *(app)* → **Settings → Settings** → **Access Control Configuration**: `Trigger access option` (defaults **Any IP**) and `Content Access Control`, which restricts *retrieval of run-history inputs and outputs* by IP — empty by default | 2026-08-07 |
| Logic app — run history retention | Same blade → **Runtime options** → `Run history retention in days` *(Default = 90 for Consumption; this is how long a logged credential persists)* | 2026-08-07 |
| Logic app — API connection resources | Logic apps → *(app)* → **Development Tools → API connections**, or Resource groups → *(RG)* → the `{connector}-{playbook name}` rows of type **API Connection**. *Deleting the workflow does not delete these* | 2026-08-07 |
| Logic app — Overview essentials worth reading | Logic apps → *(app)* → **Overview** → `Essentials`. **`Definition`** is a **full-tree** action count (11 where the canvas renders 4 collapsed cards, row 142); **`Workflow Type: Stateful`** is what persists every action's inputs and outputs to run history; **`Runs last 24 hours`** answers "did it execute" in one field | 2026-08-08 |
| **`Workflow URL` reads `--` permanently** | Same panel. Not propagation lag — an `ApiConnectionWebhook` trigger registers its callback **through the API connection** (`"callback_url": "@{listCallbackUrl()}"`), so the URL is never a property of the workflow resource (row 139) | 2026-08-08 |
| Run history — **three surfaces, not one** | **(a)** Logic apps → *(app)* → Overview → **`Run history`** tab — blank grid when empty, `Start time (Local Time)`, `Resubmit`. **(b)** → **Development Tools → Run history** — renders **`No runs`** when empty, `Start time` unlabelled, different column order. **(c)** the run monitor — no `Identifier` column at all. *One surface asserts the negative; another leaves it to be inferred (row 141)* | 2026-08-08 |
| **Trigger history** (separate store from run history) | Logic apps → *(app)* → Overview → **`Trigger history`** tab → *(row)* → History pane. **A webhook registration logs here as `Fired: False` / `Status: Succeeded`** — `Succeeded` means the subscription took, not that the playbook ran (row 140). *The pane's `Inputs link` renders the resolved `listCallbackUrl()` — a SAS-signed invocation credential. Read-scoped and short-expiry, but do not open or paste it* | 2026-08-08 |
| Run detail — per-action results | Logic apps → *(app)* → Development Tools → Run history → *(run)* → monitor canvas → *(card)* → **Parameters** tab → `Inputs` / `Outputs` / `Properties`. `Status code`, `Client tracking ID` and `Action tracking ID` are under `Properties`. **Expand `Condition` cards** — branches render collapsed as `2 Cases` and the skipped branch shows a grey dash with reason `ActionBranchingCondition` | 2026-08-08 |
| Run → incident correlation key | Run detail → **`Client tracking ID`** — formatted `{incident GUID}_{incident number}`. The only field joining a Logic Apps run to the Sentinel incident that launched it | 2026-08-08 |
| Logic Apps designer — experience switch | The run monitor and designer render a banner: *"You are using the previous Logic Apps experience"* with **`Switch to preview experience`**. *Do not switch mid-observation — the rendering changes under the reading* | 2026-08-08 |

### Microsoft Sentinel — Azure portal / Defender portal

| Setting / view | Path | Confirmed |
|---|---|---|
| Create Log Analytics workspace | Azure → Log Analytics workspaces → Create | 2026-07-19 |
| Enable Sentinel | Azure → Microsoft Sentinel → Create → select workspace | 2026-07-19 |
| Data connectors | Azure → Microsoft Sentinel → *(workspace)* → Data connectors | 2026-07-19 |
| Store-partition census (run on BOTH portals, then diff) | Defender → Advanced hunting *and* Azure → Sentinel → Logs — same query, compare table lists | 2026-07-26 |
| Sentinel Logs (KQL) | Azure → Microsoft Sentinel → *(workspace)* → Logs — **switch Simple mode → KQL mode to write queries** | 2026-07-19 |
| Sentinel incidents (Azure side, full triage) | Azure → Microsoft Sentinel → *(workspace)* → Threat management → **Incidents** — *defaults to `Last 24 hours` + a 2-value status filter; widen before trusting "No incidents were found"* (row 114). Detail pane: Owner / Status / Severity dropdowns, comments, `+ Create incident (Preview)` | 2026-08-05 |
| SIEM workspace status (unified) | security.microsoft.com → Settings → Microsoft Sentinel → SIEM workspaces | 2026-07-19 |
| Content hub (solutions) | Azure → Microsoft Sentinel → *(workspace)* → Content hub | 2026-07-19 |

### First-party connectors — Azure Activity & Entra ID (Lab 08)

| Setting / view | Path | Confirmed |
|---|---|---|
| Azure Activity (Method B — worked) | Subscriptions → *(sub)* → Activity log → Export Activity Logs → + Add diagnostic setting → law-lab-01 | 2026-07-25 |
| Azure Activity (Method A — failed) | Data connectors → Azure Activity → Launch Azure Policy Assignment wizard | failed x2 |
| Entra ID connector | Data connectors → Microsoft Entra ID → Open connector page → select log types → Apply | 2026-07-25 |
| Verify Entra diagnostic setting | Entra ID → Monitoring & health → Diagnostic settings (AzureSentinel_law-lab-01) | 2026-07-25 |

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
| Sentinel analytics rules | Microsoft Sentinel → Configuration → Analytics — Active rules / Rule templates / **Anomalies** | 2026-07-30 |
| Anomaly rules (48, all enabled) | *(above)* → **Anomalies** tab — **excluded from the Active rules count** (`POS-044`, row 41) | 2026-07-31 |
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



| Security Copilot capacity — list | Search **`Microsoft Security compute capacities`** *(the blade renders sentence case; Microsoft's docs use Title Case, so a search on the documented string still resolves)* → the list. `Showing 1 - 0 of 0` with `Type equals all` is the unfiltered no-capacity read | 2026-08-09 |
| Security Copilot capacity — create | Same blade → **+ Create** → blade titled **`Set up your Copilot capacity`**. Fields: Subscription, Resource group, Capacity name *(lowercase letters and numbers only — **no hyphens**)*, Prompt evaluation location, cross-geo checkbox, **Capacity region (static text, not selectable)**, Provisioned SCUs, Overage Capacity Setup, Terms and Conditions | 2026-08-09 |
| The submitted configuration (ground truth for the form) | Create blade → **Review + Create** → **`View automation template`** → **Parameters** tab — the ARM values actually posted (`crossGeoCompute`, `overageState`, `overageAmount`, `geo`, `location`). *The only surface not subject to the form's label rewording* | 2026-08-09 |
| Resource group — delete | Resource groups → **click the group name** → Overview toolbar → **Delete resource group**. *The list-level toolbar has **no** Delete; ticking a row's checkbox enables nothing* (row 167) | 2026-08-09 |

## Microsoft Purview — `purview.microsoft.com`

| Task | Path | Confirmed |
|---|---|---|
| Reach Data Loss Prevention (first visit) | Purview **Home → solution tiles → Data Loss Prevention** — absent from the left nav until launched once, then pins (pin persisted across sessions) | 2026-08-01; pin re-confirmed 2026-08-02 |
| DLP policy list | Data Loss Prevention → Policies — the Mode column encodes the tips sub-option ("In simulation with/without notifications") | 2026-08-02 |
| Test content against a SIT (policy-independent) | Classifiers → Sensitive info types → *(select SIT)* → **Test** → upload file — reports every qualifying confidence tier with supporting keywords | 2026-08-02 |
| DLP simulation results | Policies → *(policy)* → **View simulation** — Simulation overview / Items for review / Alerts tabs; overview counters and the Items grid aggregate on different cadences (row 79) | 2026-08-03 |
| DLP metered-features usage | Data Loss Prevention → Pay-as-you-go usage report — readable without linking a subscription | 2026-08-01 |
| Role group membership | Settings → Roles and scopes → Role groups (Export for the CSV; contains no PII) | 2026-08-01 |
| IRM alerts | Insider Risk Management → Users → **Alerts (preview)** (an Alerts (classic) coexists; Agents has a third Alerts) | 2026-08-03 |

## Microsoft Security Copilot — `securitycopilot.microsoft.com`

| Task | Path | Confirmed |
|---|---|---|
| Pre-provisioning state | Portal root — `Welcome to Microsoft Security Copilot` / *Let's get your workspace set up.* / **Get started**. **The rail is empty at this stage** — no Settings, no capacity entry. *This surface cannot confirm whether capacity exists; it only implies it. Read the Azure capacities blade for a direct answer* | 2026-08-09 |
| First-run setup (nine screens) | **Get started** → `Workspace info` (Workspace name + **Data storage location**, a fourth location field no guide names) → `Getting ready for you…` → **Select the capacity you'd like to use** → `Help improve Copilot` → M365 service-data notice → `Logging audit data in Microsoft Purview` → `Assign roles` → `You're all set` (carries the Azure resource links and the **bare subscription GUID**) | 2026-08-09 |
| Run a starter prompt | Home → **Prompts to try** → `Prompts` tab → **`Defender incident summary`** *(row 2, tagged `Incident Analysis` — not a product plugin, unlike its neighbours)* → fill `Incident ID` → submit | 2026-08-09 |
| Which capability answered | Any response → expand **`N steps completed`** → `Chose …` row. *Prompts 1–2 read `Chose Incident Analysis`; prompt 3 read `Chose Microsoft Defender XDR`. The usage dashboard's `Plugins used` is a **session-level rollup** and does not match per-prompt attribution* (row 161) | 2026-08-09 |
| SCU consumption | Left rail → **Owner → Usage monitoring** — `Provisioned units used`, `Overage units used`, per-session table with `Units used`, `Category`, `Type`, `Copilot experience`, `Plugins used`. **Hover the capacity-tab warning triangle** for the at-capacity explanation — it renders no tooltip until after the capacity is deleted (row 157) | 2026-08-09 |
| Session transcripts (survive teardown) | Left rail → **History → All history** → `My sessions`. *Workspace, transcripts and the usage record all persist after the capacity resource is deleted* (row 162) | 2026-08-09 |
| Where the relocated opt-outs live | Left rail → **Owner → Owner settings** — named by both the M365 service-data screen and the Purview logging screen as the place their setting is actually administered. *Not walked in Lab 20* | inherited, unverified |

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
| How many detections are actually running? | **Ask three surfaces.** Active rules excludes anomaly rules; the Anomalies tab shows 48 enabled; the `Anomalies` table shows whether any ever wrote (row 41) |
| Is a workspace table actually *billable*? | Not the census — `Usage \| where IsBillable == true`. Residency and billability are different questions (`POS-044`, Lab 08 §7) |
| Where do user-reported phish actually go? | Not answerable from the portal — `Get-ReportSubmissionPolicy` / `Get-ReportSubmissionRule` in EXO PowerShell, and even then the effective mailbox is in neither (`POS-040`) |
| Who holds a Defender role? | System → Permissions → Roles → *(role)* → Edit assignment *(count only shown until opened)* |
| Will this content match a SIT? | **Not the policy or its report** — Classifiers → SIT → Test answers in seconds, policy-independent, before any activation wait (Lab 14) |
| What timezone is this Purview timestamp? | Depends on the surface: policy list local unlabelled, CSV export GMT labelled, Items grid UTC unlabelled, IRM alerts UTC labelled (row 81) |
| Is an IRM policy actually able to fire? | **Not `Status`.** `Healthy` means configuration-valid; `1 warning` may be about an unrelated connector. Read `Users in scope` on the Policies grid — 0 is structural (row 83, `POS-064`) |
| Where do IRM alerts live? | Three surfaces: Insider Risk Management → **Users → Alerts (preview)**, → **Alerts (classic)**, and a third under **Agents → Alerts**. Which one populates first is itself a finding |
| Did an IRM alert fire at all, regardless of dashboard? | The **admin mailbox** — the first-alert notification toggle is ON by default and works when the grids are ambiguous (Lab 15 §5) |
| Which org indicators are on? | Purview → Insider Risk Management → **Settings → Policy indicators**. Reachable only through the policy wizard's forced dialog on first run (`POS-063`) |
| What triggering event does an IRM policy use? | **Not the Policy settings flyout** — it omits the trigger entirely. Edit policy → Triggers (row 92) |
| Was a directory role assigned without me? | Entra ID → Roles and administrators. The only notification came from Entra ID Protection email, not from the product that caused it (`POS-065`, row 93) |
| Which MDCA policies are actually running? | **Not the policy list** — 23 of 26 built-ins are `[Disabled]` by the dynamic threat detection model, which runs where this page does not show (`POS-066`, row 95) |
| How many MDCA policies exist? | **Use a filtered view.** The unfiltered list mis-paginated and undercounted the MIP mirrors; `Category: DLP` showed both (row 100) |
| Is the app connector actually carrying data? | **Not the `Connected` label.** Ask three: Activity log, `CloudAppEvents` in advanced hunting, and the connector's `Last activity` column (`POS-068`, row 97) |
| Did another product configure something in MDCA? | Cloud apps → **Activity log**. It is the only surface that showed Lab 14's DLP policy auto-creating file policies and flipping file monitoring (`POS-067`, row 96) |
| Where is the file-monitoring toggle? | Settings → Cloud apps → **Microsoft Information Protection → Files** *(path verbatim — it is not under Policies)* |
| What timezone does MDCA render? | **Local, unlabelled** — the exception to the Defender portal's UTC (row 101). The Audit page labels both of its own conventions (row 102) |
| Why is `Inspect protected files` greyed? | An Entra permission grant to the MDCA application is missing — application-consent, not a role gap on the operator (`POS-069`) |
| Where does a **playbook** live? | **Both portals, and not as alternatives.** A playbook is a Sentinel object *and* an Azure object simultaneously. Its **Sentinel half** — the Playbooks list, automation rules, incidents — is Defender-primary; Azure paths for these are legacy and close when Sentinel leaves the Azure portal on **31 March 2027**. Its **Azure half** — the workflow, designer, code view, run history, Identity, IAM, API connections, Activity log — has no Defender equivalent and will not move, because Logic Apps is a different product Sentinel borrows. Treating Azure as a fallback for the same thing is the conflation `docs/concepts/playbook-identity-model.md` exists to unpick |
| Did the playbook actually **execute**? | **Not `Trigger history`, and not the incident's `Trigger` column.** Trigger history logs the webhook *registration* as `Succeeded` (row 140); the incident audit trail files the playbook's own action as `Manual` (row 146). The one field that answers it is Logic apps → *(app)* → Overview → **`Runs last 24 hours`** |
| What did Sentinel actually hand the playbook? | **Not any portal rendering of the entity** — four of them truncate it to `Name` (row 152). Query the store: `SecurityAlert \| project Entities` in Defender → Advanced hunting |
| Where has a playbook-handled **credential** come to rest? | **Three places, and rotation cleans one.** Run history action inputs (90-day default), the sending mailbox's Inbox **and** Sent Items, and the account itself (`POS-084`) |
