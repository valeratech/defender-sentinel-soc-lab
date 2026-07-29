# Configuration Inventory & Navigation Guide

Every setting this lab has touched, grouped by **where you go to find it** rather than
by when it was configured.

Each entry answers four questions:

- **What it is** — what the setting actually controls
- **Why we configured it** — what it is for in this lab
- **Source guidance** — what the setup guides instructed
- **What we did / verified** — the observed state, and the date it was observed

Where the source guidance and the observed environment disagree, that is recorded as a
**Divergence**. Those are the most useful entries here: they are the points where
following the guide correctly still leaves you somewhere other than where the guide
says you are.

`posture-register.md` is authoritative for state and risk. This file is
hand-maintained and nothing enforces that it stays in sync — unlike
`posture-register.md`, `attack-coverage.md`, and `open-items.md`, which are generated
from source and CI-checked. If the two disagree, the register is right.

---

## Source guidance

Five setup guides were used to build this environment. They are referenced throughout
as **G1** through **G5**. Their content is not reproduced here; only what was
configured, and what was found to differ.

| Ref | Guide | Covers |
|---|---|---|
| **G1** | Microsoft 365 & Azure Sandbox — regional limitations and Teams activation | Tenant creation, E5 trial acquisition, licence assignment, Azure subscription |
| **G2** | Device Registration and Automatic Intune Enrollment Configuration Guide | Entra device join settings, MDM/MAM scope |
| **G3** | Disabling Entra ID Security Defaults for Custom Conditional Access Policies | Security Defaults, the transition to CA |
| **G4** | Integrating Microsoft Defender for Endpoint with Intune — steps and important notices | Defender↔Intune connection, both directions |
| **G5** | Deploying and Accessing an Azure Windows 11 VM with Entra ID Login | VM deployment, RBAC, NLA, Entra sign-in |

`G3` and `G5` surfaced during a documentation audit after the first version of
this file was written. That first version recorded Security Defaults (`POS-001`) as
*not in source guidance* — which was wrong, and wrong in a specific way worth naming:
absence was asserted from a partial view of the sources. The same error, in the same
document, that `POS-011` records the guides making about the environment.

**`G1`–`G5` refer to these guides as originally written.** All five have since been
revised: the divergences below were folded into the steps, and the current versions no
longer state what this document records them as stating. Every claim here about what a
guide says is therefore a claim about a superseded document, and the revised guides
disagree with it *by design* — that is what revising them was for.

The originals are the instructor's material and cannot be reproduced here, so a reader
cannot check these records directly. What a reader can know is **which ones were checked
against the original and which were not** — the same verified/asserted split the posture
register applies to settings, applied to claims about documents. The divergence table
below carries that per row. Two of the six have been read back against the original text;
the rest rest on the revised guides' own account of what changed, which is a secondary
source with an interest in the answer.

Anything marked **not in source guidance** was found or decided during the build.
Roughly half this document falls into that category, and that is the reason to keep it:
the guides cover the happy path, and the environment is what it is.

---

## Why five portals

One capability is routinely configured from more than one place, under more than one
name, with no indication that the other place exists.

`POS-009` and `POS-011` are the same integration — Defender for Endpoint talking to
Intune — seen from opposite ends. Enabling it in Defender does not enable the Intune
half. Nothing in either portal says so, and no error is raised.

**G2** makes this explicit for enrolment, giving both an Entra path and an Intune path
to the same settings and stating the portals are linked. G4 does not extend the
same treatment to the compliance connector, which is exactly where the Lab 02 finding
lives.

| Portal | URL | What lives here |
|---|---|---|
| Microsoft 365 admin center | `admin.microsoft.com` | Licences, subscriptions, billing |
| Microsoft Entra admin center | `entra.microsoft.com` | Identity, devices, CA, MDM scope |
| Azure portal | `portal.azure.com` | Subscriptions, cost, VMs, Sentinel |
| Microsoft Intune admin center | `intune.microsoft.com` | Device management, endpoint security |
| Microsoft Defender portal | `security.microsoft.com` | XDR, onboarding, hunting |

**G1** notes `portal.microsoft.com` now redirects to the Microsoft 365 home page — the
Admin tile takes you to `admin.microsoft.com` — and that *Purchase services* has been
renamed **Marketplace** under Billing.

---

# Part 1 — Microsoft ecosystem

## 1. Microsoft 365 admin center — `admin.microsoft.com`

### 1.1 Trial acquisition path — `POS-017`

- [ ] **Path:** Billing → Marketplace → All products → Microsoft 365 → *Microsoft 365 E5*
      → Details → Start free trial
- **What it is:** How the tenant obtained its E5 licensing.
- **Why:** E5 is the capability gate for this lab. Defender for Endpoint P2, Entra ID
  P2, and Defender for Cloud Apps are not in E3.
- **Source guidance (G1):** An Office 365 E5 trial must be signed up for **first**; an
  O365 E5 trial alone does not contain the licences the course needs, so M365 E5 is
  then added from the Marketplace. G1 warns the *Start free trial* button moves around
  the product page, and estimates ~$54.75/month for a single M365 E5 licence in the US
  if the trial route is unavailable. G1 also names E3 and Business Premium as regional
  fallbacks.
- **What we did:** Both trials exist, in that order. Term 2026-07-14 → 2026-08-13.
- **Note:** G1 cites an external blog post as the source for the prerequisite. That post
  covers the O365 E5 trial only and never mentions M365 E5 — so the prerequisite is
  asserted by G1 itself, not by the source it cites. The sequence was followed
  regardless, and the tenant reflects it.

### 1.2 Licence assignment — `POS-017`

- [ ] **Path:** `admin.microsoft.com` → Users → Active users → *(account)* →
      Licenses and apps *(G1's route: Billing → Licenses → subscription → Assign
      licenses)*
- **Portal trap:** **Entra ID shows licensing read-only.** `entra.microsoft.com` →
  Users → *(user)* → Licenses renders a page that cannot assign anything and says so
  only in a banner: *"Adding, removing, and reprocessing licensing assignments is only
  available within the M365 Admin Center."* Same setting, two portals, one a dead end —
  the same shape as `POS-009`/`POS-011`, and the reason the five-portal note above
  isn't padding.
- **What it is:** Which SKUs are active on the account that operates the lab.
- **Why:** G1 is explicit that adding a subscription to the tenant does **not** assign
  it to your account — that is a separate manual step.
- **Source guidance (G1):** Assign the newly added M365 E5 licence to the admin user
  after activation.
- **What we verified (2026-07-16):** Microsoft 365 E5 **and** Office 365 E5 both
  assigned, 1/25 each. 173 service plans listed under Apps.
- **Observation:** M365 E5 is a superset of O365 E5, so both being assigned is
  redundancy. It resolves itself when O365 E5 lapses.
- **Cross-reference:** G4 notes that greyed-out or failing endpoint settings usually
  mean this step was missed — see 5.2.

### 1.3 Recurring billing — `POS-017`

- [ ] **Path:** Billing → Your products → *(subscription)* → Trial subscription →
      Edit recurring billing
- **What it is:** Whether a trial converts to a paid subscription at term end.
- **Why:** Both trials took a payment method and both were configured to convert on
  2026-08-13.
- **Source guidance (G1):** Cancel the subscription before the trial ends — Billing →
  Your products → select subscription → Cancel subscription.
- **What we did instead (2026-07-16):** Turned recurring billing **off** on Office 365
  E5. **Rejected cancelling**, per Microsoft's own documentation: cancelling ends
  access, whereas turning recurring billing off leaves the subscription active until it
  expires and simply stops the conversion. Same cost, full remaining term of lab
  access.
- **Verified:** the panel now reads *Expires on August 14, 2026* in place of *changes to
  paid subscription* — the documented indication that recurring billing is off.
- **Left on deliberately:** Microsoft 365 E5, converting 2026-08-13 at 1 licence,
  1 month, pay monthly. That was Microsoft's own default for the conversion and matches
  what the lab needs — month-to-month, cancellable at any renewal.
- **Divergence from G1:** G1's cancel-based advice is not wrong, but it costs the
  remainder of the trial. Turning off recurring billing is strictly better for a lab,
  and G1 does not mention it.
- **Open, tested live 2026-08-13:** whether M365 E5 minds O365 E5 lapsing. G1 makes
  O365 E5 a prerequisite for *acquisition*. An acquisition path is not normally an
  ongoing dependency, but that is a vendor expectation, not an observation. Reversible
  until then.

### 1.4 Microsoft Teams trial — not configured

- [ ] **Path:** Billing → Marketplace → search *Teams* → Collaboration and
      communications → Start free trial
- **What it is:** A 30-day Teams add-on trial.
- **Source guidance (G1):** The default trial tenant does not include Teams. G1
  suggests waiting until the Teams modules before activating, to preserve the 30 days.
- **State:** Not activated — deliberate. The clock starts on activation.

---

## 2. Microsoft Entra admin center — `entra.microsoft.com`

### 2.1 Security Defaults — `POS-001` ⚠️ weakening

- [ ] **Path:** Entra ID → Overview → Properties → Manage security defaults
- **What it is:** A tenant-wide baseline enforcing MFA registration, blocking legacy
  authentication, and protecting privileged actions. On by default for tenants created
  since 2019-10-22.
- **Why it is off:** Security Defaults and Conditional Access are mutually exclusive.
  Lab work requiring CA cannot proceed with Defaults enabled.
- **Source guidance (G3):** An entire guide covers this. Disable via Entra ID →
  Overview → Properties → Manage security defaults, selecting *"My organization is
  planning to use Conditional Access"* as the reason. G3's stated rationale: the
  blanket MFA and legacy-auth rules disrupt scripts, CLI tooling, and device-joining
  exercises, and Entra will not run Defaults and custom CA simultaneously.
- **G3 contains a copy-paste error worth knowing about.** Its *Quick Step* block is
  Microsoft's **enable** procedure, ending *"Set Security defaults to Enabled"* —
  directly contradicting its own TLDR, which says disable. Following the Quick Step
  literally does the opposite of the guide's purpose.
- **G3 also warns**, explicitly: never leave Security Defaults disabled in production
  without immediately replacing them with equivalent or stronger Conditional Access.
  See `POS-003` — **that is a gap the guidance warned about, not one it omitted.**
- **What we verified (2026-07-16):** **Disabled.** Since the tenant default is Enabled,
  this was an **active change**, not an inherited state — recorded as such so it is not
  mistaken for a default.
- **Production answer:** Conditional Access policies replacing the baseline.
- **The problem:** nothing replaced it. See `POS-003`.

### 2.2 Conditional Access — `POS-003` ❌ gap

- [ ] **Path:** Entra ID → Protection → Conditional Access → Policies
- **What it is:** Policy-based access control — the granular replacement for Security
  Defaults.
- **Why it matters:** It is the justification for `POS-001`. Disabling Defaults is only
  defensible if CA lands in the same change window.
- **State:** None believed configured. **Asserted, not verified** — a claim, not a
  finding.
- **Compounding:** `POS-001` + `POS-003` leave the tenant weaker than a brand-new one —
  the baseline was removed and nothing took its place.
- **Ordering trap for later:** a *require compliant device* grant control depends on
  `POS-011`, which is off. The policy would deploy, report healthy, and not do what was
  intended.

### 2.3 Admin identity model — `POS-002` ⚠️ weakening

- [ ] **Path:** Entra ID → Roles and administrators → Global Administrator
      *(production answer: Identity Governance → Privileged Identity Management)*
- **What it is:** How administrative access is held — standing versus activated.
- **State:** Single standing Global Administrator across all five portals.
  **Asserted, not verified.**
- **Why it is this way:** Single-operator lab. G1 has you create one admin account
  during tenant setup and never revisits it.
- **Source guidance (G1):** Creates the account. Does not discuss role scoping.
- **Production answer:** Role-scoped accounts; PIM eligible rather than standing.
- **Consequence:** One account, permanently privileged, used for daily work. Every audit
  log entry carries the same actor, so administrative activity cannot be distinguished
  from routine activity. Compounds with `POS-001` and `POS-003`.

### 2.4 Elevate access to all Azure subscriptions — `POS-004` ✅ default

- [ ] **Path:** Entra ID → Overview → Properties → Access management for Azure resources
- **What it is:** Grants the Global Administrator User Access Administrator at root
  scope across every subscription in the tenant. Entra roles and Azure RBAC are
  separate planes; this toggle is the bridge.
- **Why recorded:** It is **Off**, matching baseline — recorded so it is not mistaken
  for a decision.
- **Source guidance:** Not in G1–G5.
- **Verified:** 2026-07-16.

### 2.5 Users may join devices to Microsoft Entra ID — `POS-006` ⚠️ weakening

- [ ] **Path:** Entra ID → Devices → Device settings
- **What it is:** Which users may join Windows devices to the tenant.
- **Why:** Required before any device can be joined and subsequently enrolled.
- **Source guidance (G2):** Set to **All**. G2 explicitly notes production should use
  *Selected* to restrict this to specific security groups, and that *All* is chosen for
  smooth lab onboarding.
- **What we did:** Set to All, per G2.
- **State:** All. **Asserted, not verified from the portal.**
- **Production answer:** Selected, scoped to a security group — as G2 itself says.

### 2.6 MDM and MAM user scope — `POS-007`, `POS-008`

- [ ] **Path (Entra):** Entra ID → Mobility (MDM and WIP) → Microsoft Intune
- [ ] **Path (Intune):** Devices → Enrollment → Automatic Enrollment
- **What it is:** What makes a Windows device automatically enrol in Intune the moment
  it joins Entra ID. Scope = None means devices join Entra but never appear in Intune.
- **Why:** Without it, nothing in Labs 02–03 has a device to act on.
- **Source guidance (G2):** MDM user scope → **All**; WIP/MAM user scope → **All**
  (G2 notes WIP may display as MAM depending on portal version). G2 gives **two paths**
  — Method A via Entra, Method B via the Intune admin center — and states they are the
  same settings viewed from linked portals.
- **What we did:** Configured via the **Entra path only** (Method A).
- **Gap:** G2's Method B was not used to verify. The settings were never confirmed from
  the Intune side, and neither scope has been observed in the portal — both are
  asserted. Given `POS-011` is a case of one portal not reflecting another, G2's own
  suggestion to check both is worth taking.
- **Baseline:** None. So this **was** a change, not an inherited default.
- **Production answer:** Scoped by group during staged rollout.
- **Expected behaviour (G2):** on sign-in with an organizational account, the device
  registers in Entra, silently registers with Intune, and receives baselines,
  compliance policies, and Defender rules. G2 notes enrolment can take 5–10 minutes and
  suggests a manual sync from Windows settings if the device does not appear.

### 2.7 Automatic MDM enrolment never fires — `POS-022` ❌ gap — **the Lab 01 finding**

**It doesn't happen.** The device joined Entra on 2026-07-14 and was still absent from
Intune three days later. Not slow — absent.

**Every precondition verified individually. All pass:**

| Precondition | State | Verified by |
|---|---|---|
| MDM user scope = All | ✅ | Entra portal (`POS-007`) |
| Device holds the MDM discovery URL | ✅ | `dsregcmd` — **matches the portal value exactly** |
| Device eligible for auto-enrolment | ✅ | `DeviceEligible : YES` |
| Primary Refresh Token | ✅ | `AzureAdPrt : YES`, 17:09:30 UTC |

**And nothing happens:**

| Check | Result |
|---|---|
| Scheduled tasks under `\Microsoft\Windows\EnterpriseMgmt` | **none** |
| Enrolment events (ID 71/72/75/76) in `DeviceManagement-Enterprise-Diagnostics-Provider/Admin` | **none**, in a log spanning back before the VM existed |
| Device in Intune | **absent** |

**Not blocked. Never started.** No error is raised because nothing is attempted.

**Hypothesis, not conclusion:** the join path. G5 builds a VM whose Entra join is done
by the `AADLoginForWindows` extension at deployment — not by a user-driven join through
Settings or OOBE. MDM scope is *necessary but not sufficient*; something must trigger
enrolment, and the extension join appears not to. Suggestive: Azure Virtual Desktop's
host-pool creation offers an explicit *"enrol VMs with Intune"* checkbox that plain VM
creation lacks — which would be redundant if extension joins enrolled themselves.

**What is established** is the observation: preconditions met, behaviour absent, silent.

**Why this is the sharpest divergence yet:** G2 and G5 are each internally correct. G2
describes user-driven join behaviour; G5 builds a VM that doesn't join that way.
Followed together they produce a device that will **never** enrol — and neither guide is
wrong enough for the failure to surface.

**Left unenrolled deliberately.** Lab 03 onboards to Defender via local script and
doesn't need Intune. Forcing it (`deviceenroller.exe /c /AutoEnrollMDM`) requires local
admin, which `POS-021` deliberately removed, and it enrols in the *calling user's*
context — so forcing it as Global Admin would bind the device to the very account
`POS-021` exists to keep off the endpoint.

**Diagnostic path worth keeping** — every step was read from the device, not inferred
from documentation:

```powershell
dsregcmd /status                     # AzureAdPrt, DeviceEligible, MdmUrl, TpmProtected
Get-ScheduledTask -TaskPath "\Microsoft\Windows\EnterpriseMgmt\*"
Get-WinEvent -LogName "Microsoft-Windows-DeviceManagement-Enterprise-Diagnostics-Provider/Admin" |
  Where-Object { $_.Id -in 75,76,71,72 }
```

Note `dsregcmd`'s **SSO State is per-user**. Run via Azure Run command it executes as
SYSTEM and reports `AzureAdPrt : NO` regardless of truth. It must be run inside the
user's session.

**Timestamp trap (Lab 03).** `DeviceEvents` / `DeviceInfo` render `Timestamp` in the
portal's configured timezone, not necessarily UTC and not necessarily your local
clock. Latency computed by subtracting an onboarding wall-clock time from a portal
`Timestamp` reads wildly wrong until both are in one zone — during Lab 03 an apparent
14-hour gap was briefly read as evidence the sensor had *backfilled* pre-onboarding
history. It had not: comparing `Timestamp` against `ingestion_time()` showed a
consistent ~3.5-minute gap, i.e. a live stream. The lesson: confirm the portal
timezone before computing any latency, and use `ingestion_time()` when the question
is "when did MDE **receive** this" — `Timestamp` answers "when did it **happen** on
the device", an adjacent question the column name does not warn you about.

**`Get-MpPreference` does not return ASR rules in entry order (Lab 06).**
The `AttackSurfaceReductionRules_Ids` and `_Actions` arrays are index-aligned to each
other but not to the order rules were added. Reading the actions in the order you typed
the `Add-MpPreference` commands inverts every rule's state — a rule you set to Block
reads as Audit. Confirm state by pairing Id[i] with Action[i] within the returned
arrays (`0` off · `1` block · `2` audit · `6` warn), never by input order.

**`Add-MpPreference` appends; `Set-MpPreference` replaces (Lab 06).**
Building a multi-rule ASR set with `Set` twice silently discards the first rule. Use
`Add` to accumulate.

**ASR report omits locally-set rules (Lab 06, `POS-031`).**
The Defender ASR report (Reports → Attack surface reduction rules) is scoped to
policy-managed rules. Rules set locally with `Add-MpPreference` enforce on the endpoint
but show as "Rules off" / not configured in the report, and produce zero rows in the
Detections view even with all filters set to Any. Verify ASR activity in Advanced
hunting, not the report. On this tenant the only available ASR path *is* local
PowerShell (Intune foreclosed, `POS-022`), so all ASR here is invisible to that report.

**Assets CSV `Last device update` is check-in time, not config time (Lab 05).**
The device-inventory export column `Last device update` records the device's last
telemetry check-in, not when a configuration was applied to it. Computing a
configuration latency (e.g. device-group propagation) by subtracting an Apply time
from this column produces a nonsense figure — during Lab 05 it turned ~28 minutes of
normal propagation into an apparent ~30-hour outage and spawned three false failure
theories before the real elapsed time was confirmed. Sibling to the UTC timestamp
trap: confirm which clock a timestamp actually measures before computing against it.

**Device-group rule wizard ships un-deletable empty AND conditions (Lab 05).**
The Add-device-group rule builder pre-populates four AND-joined conditions (Name,
Domain, Tag, OS). Only conditions added *beyond* these defaults get a delete icon, so
the three empty defaults cannot be removed. They are ignored in evaluation — Preview
matches with them empty — so the rule works, but a reader inspecting a saved rule sees
three empty AND clauses and reasonably suspects them as the cause of a non-match. They
are not. Rule out the timestamp and propagation first.

**`OnboardingState` lives in two places and they disagree (Lab 03, module 27).**
The registry `HKLM:\SOFTWARE\Microsoft\Windows Advanced Threat Protection\Status`
value `OnboardingState` read `1` on the onboarded device; the identically-named
field from `Get-MpComputerStatus` was **blank** on the same device at the same time.
The registry value is authoritative — it is what the SENSE service writes on first
start. `Get-MpComputerStatus` is the antivirus-centric view and its onboarding field
is unreliable. Same field name, two sources, no signal which to trust; confirm onboard
from the registry `Status` key (and `OrgId` for the tenant), not from the AV cmdlet.

**Guest-agent "Ready" ≠ extensions work (Lab 03, `POS-028`).** A VM guest agent
reporting `Ready` with a version string still hung every Run Command and VMAccess
operation indefinitely while control-plane reads returned instantly. Same shape as
`POS-011`'s "Available" and `POS-026`'s role that "appears complete": a status field
answering a narrower question than the one asked. Do not treat agent `Ready` as proof
the extension channel is live; the confirming signal is an extension operation that
actually **returns**.

---

### 2.8 Scoped analyst identity — `POS-027` ✅ hardened

- [ ] **Path:** Users → All users → New user → Create new user *(set Usage location under Properties)*
- **What it is:** A dedicated Defender-portal analyst account, created so console work stops requiring the Global Administrator.
- **Why:** To separate the identity that *operates* the SOC console from the identity that *owns* the tenant — the second half of least-privilege that `POS-002` names and does not yet close.
- **Source guidance (module 24 guide):** The role-creation prerequisites cover who may *create* a role; they say nothing about what the *assignee* needs.
- **What we verified (2026-07-17):** Account created with **no directory roles, no group memberships, no licence**. Usage location set at creation — a licence cannot be assigned later without it, and the failure does not say so. After URBAC activation (§5.4), analyst reached the Defender portal and the views the scoped role grants; no licence was needed. Does **not** close `POS-002` — the Global Administrator is still the identity doing the work until analyst is the one used.

### 2.9 SOC Device Admins security group — Lab 05

- [ ] **Path:** Groups → New group → *type: Security, membership: Assigned*
- **What it is:** An Entra security group holding the analyst identity, created to be bound to a Defender device group's user-access assignment (§5.6).
- **Why:** The *who* half of scoped device access. An Entra group holds people; a Defender device group holds devices; this group is what connects the two.
- **Source guidance (module 31 guide):** Create the admin group first, then grant it access to the device group.
- **What we verified (2026-07-19):** Group created, analyst added as sole member. Bound to the *Lab Client Machines* device group in §5.6, through which analyst gained scoped visibility of the device — the composition `POS-030` records as resolved.

## 3. Azure portal — `portal.azure.com`

### 3.1 Subscription funding model — `POS-005` ❌ gap — **major divergence**

- [ ] **Path:** Subscriptions → *(subscription)* → Overview
- **What it is:** How Azure consumption is funded, and what happens when it exceeds
  expectations.
- **Source guidance (G1):** Register for a free Azure account for **$200 credit over 30
  days** plus 12 months of selected free services. G1 describes a *safety catch*:
  Microsoft will not automatically charge the card when the trial expires or credits run
  out — services are paused and disabled instead, and the card is billed only on a
  manual upgrade to pay-as-you-go. G1 also gives a path to check the credit balance:
  Subscriptions → *(subscription)* → Cost Management + Billing → Payment methods →
  Azure credits.
- **What we verified (2026-07-16):** **Pay-as-you-go, uncapped. No free credit.**
- **Divergence — the most consequential in this document:** the safety catch G1
  describes **does not exist in this environment.** There is no credit to exhaust, no
  automatic pause, and no service disable. The **spending limit feature is unavailable
  on pay-as-you-go**, so there is no mechanism that stops spend — only mechanisms that
  report it. Following G1 and assuming the safety net is present would be wrong, and the
  way you would find out is an invoice.
- **What we did about it:** budgets (`POS-015`) and deallocation discipline
  (`POS-016`), neither of which G1 mentions because G1 assumes the credit model.

### 3.2 Cost budgets — `POS-015` ✅ hardened — not in source guidance

- [ ] **Path:** Subscriptions → *(subscription)* → Cost Management → Budgets → + Add
- **What it is:** Threshold-based cost notification. **Notification only.**
- **Why:** `POS-005` removed the safety net G1 assumed. Lab 03 starts billable compute;
  Lab 04 adds Log Analytics ingestion.
- **Source guidance:** None. G1 assumes credits and a hard stop, so it has no reason to
  discuss budgets.
- **What we did:** two budgets, deliberately:
  - `rg-soc-lab` scope, $15/mo, Actual 50/80/100
  - Subscription scope, $25/mo, Actual 50/80/100 **+ Forecasted 100**
- **Decision:** two scopes, not one. **Rejected consolidating in both directions** — a
  resource-group budget cannot see spend outside its group (Lab 04's workspace may land
  elsewhere, and ingestion is the largest projected cost); a subscription budget cannot
  attribute spend to a component. Cost of both: duplicate mail when spend falls inside
  the group.
- **Gotcha found:** **budget scope is fixed at creation.** The subscription budget had
  to be created new; the existing one could not be rescoped.
- **Limits, recorded rather than glossed:**
  1. Budgets notify, they do **not** cap
  2. Azure evaluates budgets every **8–24 hours**, not on demand — an alert can arrive
     a day after a runaway resource starts billing
  3. Covers **Azure only**; the M365 conversion (`POS-017`) bills through a separate
     system and is invisible to Azure Cost Management at any scope
  4. The resource-group budget remains Actual-only — its warnings arrive after spend
  5. **Neither alert has ever fired.** Recipients are set; the notification path is
     unvalidated, which by this repo's standard makes it a hypothesis, not a control

### 3.3 Lab VM power state — `POS-016` ✅ hardened, still flagged

- [ ] **Path:** Virtual machines → *(VM)* → Overview → Status
- **What it is:** Whether the VM's compute is released or merely powered off.
  **Stopped** and **Stopped (deallocated)** are different states — shutting down from
  inside the guest OS leaves compute allocated and billing, and the portal reports that
  as plain *Stopped*. Only the portal's Stop action deallocates.
- **Why it matters:** Given `POS-005` (no cap) and `POS-015` (notify only, 8–24h lag),
  **deallocation is the only mechanism here that actually ends spend.**
- **Source guidance:** None. G1's credit model made this unnecessary; `POS-005` makes it
  essential.
- **What we verified (2026-07-16):** **Stopped (deallocated).**
- **Why still flagged:** a *state* was verified, not a *control*. The mechanism is
  operator memory, and Lab 03 onward means sessions ending at unpredictable times.
  Auto-shutdown (VM → Operations → Auto-shutdown) would make it a control and costs
  nothing.

### 3.4 Log Analytics workspace & Microsoft Sentinel — `POS-032` ✅ hardened

- [ ] **Path (workspace):** Log Analytics workspaces → Create
- [ ] **Path (Sentinel):** Microsoft Sentinel → Create → select workspace
- **What it is:** The Log Analytics workspace `law-soc-lab` is the data store; Microsoft Sentinel is the SIEM/SOAR layer enabled on top of it.
- **Why:** The section capstone — the aggregation layer that every prior lab feeds into.
- **Source guidance (module 35 guide):** Create a workspace, enable Sentinel, connect data sources; retention and ingestion are the cost levers.
- **What we verified (2026-07-19):** Workspace `law-soc-lab`, **West US** (matches the VM's region), **Pay-as-you-go (Per GB 2018)**, placed in the VM's resource group so the whole lab is one deletable teardown unit (`POS-015`). Sentinel enabled — trial **2026-07-19 → 2026-08-19**, 10 GB/day free on both Sentinel and Log Analytics. Creating the workspace is free; ingestion and retention beyond the free window are the meters. Commitment-tier decision deferred until steady-state volume is known (`POS-032` revisit).
- **The permissions trap:** the Defender-XDR auto-onboard (§5.7) needs subscription **Owner** (Azure RBAC). Global Administrator is a *directory* role and does not confer it — the account here holds both (`POS-024`), so the auto-onboard succeeded, but GA alone would have been blocked.

### 3.5 Lab endpoint VM — `POS-018`, `POS-019`, `POS-020`, `POS-023`

- [ ] **Path:** Virtual machines → *(VM)* → Overview · Networking · Operations
- **What it is:** The Windows 11 endpoint every later lab acts on.
- **Source guidance (G5):** Resource group, VM name, closest region, no infrastructure
  redundancy, **Security Type → Standard**, Windows 11 Enterprise, 2 vCPU / 8 GiB,
  local admin account, **RDP 3389 allowed**, Standard HDD, **Login with Microsoft
  Entra ID**, **auto-shutdown enabled**, boot diagnostics disabled.
- **What we deployed:** `Standard_D2s_v3` (2 vCPU / 8 GiB), Windows 11
  `10.0.26200.8875`, Entra login on, auto-shutdown 23:00 Pacific with notification.
  **Deviation:** named for its purpose rather than G5's suggested name.
- **Cost:** ~$70/month running continuously, against a $25/month subscription budget
  (`POS-015`) — 100% in roughly ten days of uptime. `POS-023` is what keeps that
  theoretical.

#### Security Type = Standard — `POS-018` ⚠️

G5 says to change it. It doesn't say what it costs. **Four independent observations,
one cause:**

| Observation | Source |
|---|---|
| no `securityProfile` block | VM JSON view |
| `TpmPresent: False`, `TpmReady: False` | `Get-Tpm` |
| `Confirm-SecureBootUEFI` → `False` | in-session PowerShell |
| `TpmProtected: NO`, `KeyProvider: Microsoft Software Key Storage Provider` | `dsregcmd /status` |

And it surfaces in the identity plane too — the Entra sign-in log records
**`Token protection - Sign In Session: Unbound (Status code: 1003)`**. With no vTPM the
Primary Refresh Token cannot be bound to the device, so a stolen token is replayable
elsewhere.

**It also breaks compliance from a second direction.** Intune compliance policies
commonly evaluate Secure Boot and TPM. This device can satisfy neither. So
`POS-011` blocks the risk signal *and* the device would fail the checks even if the
signal arrived — fixing the toggle alone would not produce a working control.

#### RDP exposure — `POS-019`

G5: *"Ensure RDP (3389) is allowed."* Portal default source is **Any** — the entire
internet. Scoped to the operator's IP on 2026-07-17.

**The exposure was never RDP alone. It was the composition:**

```
3389 open to Any            (G5 default)
  + NLA disabled            (POS-020, G5 instructs)
  + no MFA baseline         (POS-001)
  + no Conditional Access   (POS-003)
  + sign-in as Global Admin (POS-002, G5 instructs)
  = internet-facing path to tenant compromise
```

Every element is individually defensible in a lab. Together they are not, and **no
single guide step is wrong enough to notice.** The VM being deallocated between
sessions is what kept it theoretical.

#### NLA disabled — `POS-020` ⚠️

Genuinely required for G5's approach: Entra auth happens at the Windows login screen,
and NLA validates credentials before a session exists, so it blocks the flow.

Verified at both ends: registry `UserAuthentication = 0` (read via **Run command** — the
exposed path was not used to inspect the exposed path), and `enablecredsspsupport:i:0`
in the `.rdp` file.

```
full address:s:203.0.113.10:3389
prompt for credentials:i:1
username:s:azuread\analyst@contoso.onmicrosoft.com
enablecredsspsupport:i:0
authentication level:i:2
```

**The file weakens two things and G5 explains one.** `authentication level:i:2` means
*warn but connect* when server identity can't be verified — a downgrade of server
authentication, not just client pre-auth. Unmentioned.

#### Sign-in identity — `POS-021` ✅ not in source guidance

G5 signs in as the tenant Global Administrator, because at that point in the course
it's the only Entra account that exists.

An Entra-joined device receives a **Primary Refresh Token** for whoever signs in, and
it lives on the device. So G5's flow places a tenant-admin token on the endpoint that
later labs deliberately attack — and per `POS-018` that token is unbound, so it's
replayable.

Created `labuser`: no roles, no groups, **M365 E5 assigned** (required — an unlicensed
account won't enrol), **Virtual Machine User Login** (not *Administrator* Login), scoped
to the single VM. Also more faithful for the labs ahead: ASR and attack-simulation
results as a non-admin are what an analyst actually sees.

---

## 4. Microsoft Intune admin center — `intune.microsoft.com`

### 4.1 Allow MDE to enforce Endpoint Security Configurations — `POS-010`

- [ ] **Path:** Endpoint security → Setup → Microsoft Defender for Endpoint →
      *Allow Microsoft Defender for Endpoint to enforce Endpoint Security
      Configurations*
- **What it is:** Security-settings management via MDE — lets Intune policy reach
  devices MDE sees but Intune does not manage.
- **Why:** G4 presents this as Step 2 of the integration, the Intune-side counterpart
  to `POS-009`.
- **Source guidance (G4):** Toggle **On**, then Save at the top of the blade.
- **What we verified (2026-07-16):** On. Baseline is Off — so this was a change.
- **Production answer:** On only where MDE-onboarded devices are not Intune-enrolled;
  worth scoping deliberately rather than leaving broadly on.

### 4.2 Connect Windows devices to MDE — `POS-011` ❌ gap — **the Lab 02 finding**

- [ ] **Path:** Endpoint security → Microsoft Defender for Endpoint → Compliance policy
      evaluation → *Connect Windows devices version 10.0.15063 and above to Microsoft
      Defender for Endpoint*
- **What it is:** The toggle allowing MDE's device risk score to reach Intune compliance
  evaluation.
- **What we verified (2026-07-16):** **Off.**
- **Source guidance (G4): not mentioned.** This is the divergence that matters.

  G4 states that integrating MDE and Intune enables real-time telemetry sharing, and
  that the connection **allows Intune to enforce compliance based on a device's risk
  level reported by Defender**. That is the stated purpose of the entire procedure.

  G4 then gives two steps — the Defender-side connection (`POS-009`) and the
  enforcement toggle (`POS-010`). **Neither enables risk-based compliance.** The toggle
  that does sits on a different blade in the same portal, and G4 never mentions it.

  Following G4 exactly and completely therefore produces an integration that reports
  *Available*, raises no error, and **does not do the thing G4 says it does.**
- **Consequence:** device risk does not reach Intune compliance. The risk → compliance →
  Conditional Access chain is architecture, not a working control. A compliance policy
  written against device risk will deploy successfully, report healthy, and **silently
  never fire.**
- **Why it was findable at all:** only by checking the setting rather than the status.
  Connection status reads *Available* (`POS-009`) because the Defender half is on.
  Every surface says healthy.
- **The lesson:** the absence of an error is not evidence a control works.

### 4.3 Connect Android / iOS devices to MDE — `POS-012` ✅ default

- [ ] **Path:** Endpoint security → Microsoft Defender for Endpoint
- **State:** Off for both compliance and app protection — matches baseline. Mobile is
  out of scope for this lab.
- **Source guidance:** Not in G1–G5.

### 4.4 Block unsupported OS versions — `POS-013` ✅ default

- [ ] **Path:** Endpoint security → Microsoft Defender for Endpoint
- **State:** Off — matches baseline.
- **Source guidance:** Not in G1–G5.

### 4.5 Days until partner is unresponsive — `POS-014` ✅ default

- [ ] **Path:** Endpoint security → Microsoft Defender for Endpoint
- **What it is:** How long Intune keeps trusting MDE's last-known signal before treating
  the partner as unresponsive.
- **State:** 7 — matches baseline.
- **Source guidance:** Not in G1–G5.

---

## 5. Microsoft Defender portal — `security.microsoft.com`

### 5.1 Microsoft Intune connection — `POS-009` ✅ hardened

- [ ] **Path:** System → Settings → Endpoints → Advanced features → *Microsoft Intune
      connection* → Save preferences
- **What it is:** The Defender half of the MDE↔Intune bridge — permits Defender to
  communicate outward to Intune.
- **Why:** G4 Step 1.
- **Source guidance (G4):** Toggle On, Save preferences. G4 warns the Defender portal's
  left navigation is collapsed by default in newer versions and must be expanded to
  reach System → Settings — and advises focusing on the objective (linking the endpoint
  security tool to the management suite) rather than memorising a layout Microsoft keeps
  changing.
- **What we verified (2026-07-16 17:34:32):** On. Connection status **Available**.
- **The trap:** this is the same integration as `POS-011`, seen from the other end.
  This being On is what makes the status read *Available* — which is precisely why the
  Intune half being Off is invisible.

### 5.2 Endpoints provisioning delay — not a setting, but load-bearing

- **What it is:** The backend provisioning lag between assigning an E5 licence and
  Defender's Endpoints features actually appearing.
- **Source guidance (G4):** three notes that explain most "it's broken" moments in
  Labs 02–03:
  1. After assigning an MDE or M365 E5 licence, Endpoints features may not appear
     immediately — M365, Entra ID, and Defender need time to complete backend
     provisioning. Some Defender workloads may work while the Endpoints section or its
     settings are still missing. This usually resolves on its own.
  2. After saving integration settings, background synchronisation can take **1–2
     hours** to propagate. Connection status screens may not update immediately.
  3. If settings fail to save or controls are greyed out, check the E5 licence is
     actually assigned (see 1.2). Without E5 the tenant lacks the endpoint security
     engine the integration requires.
- **Why it is recorded here:** these are the difference between waiting and
  troubleshooting something that is not wrong. Lab 00 confirmed the wait is real —
  over an hour before Endpoints appeared.

### 5.3 Device onboarding — `POS-029` ✅ hardened

- [ ] **Path:** System → Settings → Endpoints → Onboarding *(select OS, connectivity type, deployment method, download package)*
- **What it is:** The onboarding package that installs and registers the Defender for Endpoint sensor on a device.
- **Why:** The SOC's first endpoint. Before this the `Device*` advanced-hunting tables were empty; after it, they are the data plane every later lab reads from.
- **Source guidance (module 25 guide):** Download the local script, run it elevated on the device, confirm the device appears in the portal.
- **What we verified (2026-07-18):** `LAB-WIN11-01` onboarded via **local script** — the only available path here, because the Intune path is foreclosed (`POS-022`, and independently `POS-011`/`POS-018`). Connectivity type **Streamlined**, confirmed applied via `DeviceInfo.ConnectivityType` rather than assumed from the selection. Sensor Active and streaming. Latencies all at/under vendor numbers: onboard→inventory ~2 min, →first telemetry ~3.5 min, detection→alert ~2 min. Device-side confirmation: registry `Status\\OnboardingState = 1`, `OrgId` correct tenant, `AMRunningMode Normal` (the ASR precondition, §5.5).
- **The trap:** the portal showing the device confirms only that the *cloud* sees it. Device-side registry is the authoritative onboard check — and the same `OnboardingState` field from `Get-MpComputerStatus` reads blank on a correctly onboarded device. See the traps register below.
- **What onboarding is not:** telemetry, not management. The device is *watched* (streaming) but not *governed* (obeys no policy) — onboarding is not enrolment. A fully-reporting endpoint looks managed and is not.

### 5.4 Unified RBAC activation — `POS-026` ✅ hardened

- [ ] **Path:** System → Permissions → Roles → *Activate workloads* / Workload settings
- **What it is:** The switch that makes Defender begin enforcing custom URBAC roles and their assignments for each workload.
- **Why:** A custom role is defined and assigned but enforces nothing until its workload is activated. Activation is what turns the analyst role (§5.4a) into a working control.
- **Source guidance (module 24 guide):** States URBAC is the default model for new tenants — Defender for Endpoint since 2025, Office 365 P2 since July 2026.
- **What we verified (2026-07-17):** All workloads activated (previously **zero** active). "Default model" means the *legacy* model is unavailable — not that the unified model is switched on. Measured before/after directly: signed in as the assigned analyst before activation — no Incidents, no Hunting, no Assets; activated the workloads; signed in again — all three present, nothing else changed. This before/after is **unrepeatable once telemetry exists** — the absence of data only proves anything on a tenant that has none.

### 5.4a Scoped analyst role — `POS-027` ✅ hardened

- [ ] **Path:** System → Permissions → Roles → Create custom role *(role membership readable only via Edit)*
- **What it is:** A custom URBAC role, *SOC Analyst — Read Only*, granting **Security data basics (read)** only.
- **Why:** The permission half of the scoped analyst identity (§2.8) — minimal read access to operate the console without tenant authority.
- **Source guidance (module 24 guide):** Data sources are a hard boundary; scoping to a single workload is done by deselecting the others.
- **What we verified (2026-07-17):** Role created, Security data basics (read). ⚠️ Assignment scoped to **all four data sources** (Endpoint, Office 365, Identity, Cloud Apps) where this lab has endpoints only — the wizard defaults to all data sources selected, and tight scoping is an active deselection step that was missed. Role membership is readable only by opening the Edit dialog; the list view shows a count, not members.

### 5.5 Attack Surface Reduction rules — `POS-031` ✅ hardened

- [ ] **Path (view/report):** Reports → Attack surface reduction rules
- [ ] **Path (set):** local PowerShell on the device — `Add-MpPreference -AttackSurfaceReductionRules_Ids <guid> -AttackSurfaceReductionRules_Actions <Enabled|AuditMode>`
- **What it is:** Behavioral rules that block attacker techniques (Office child processes, WMI/PSExec process creation, LSASS access, etc.).
- **Why:** Endpoint hardening, and a demonstration of the audit-vs-block distinction end to end.
- **Source guidance (module 33 guide):** Deploy via Intune/policy; view results in the ASR report.
- **What we verified (2026-07-19):** Two rules set via **local PowerShell** (the only path — Intune foreclosed, `POS-022`), both **Block**: WMI event-subscription persistence, and PSExec/WMI process creation. Precondition met: `AMRunningMode Normal` (§5.3) — rules enforce rather than silently no-op. Audit vs Block demonstrated on one rule with an identical trigger: Audit → action allowed, silent, event 1122, `...Audited`; Block → refused, notification, event 1121, `...Blocked`. Near-instant local and cloud latency.
- **The headline trap:** the ASR **report shows this device "Rules off"** — 0 in block, 0 in audit — while both rules actively block. The report is scoped to *policy-managed* (Intune) rules; locally-set rules enforce but are invisible to the console. A direct downstream consequence of `POS-022`: local PowerShell is the only path here, and it is exactly the path the report cannot see. Verify ASR in **Advanced hunting**, not the report — and ASR blocks are telemetry, not alerts (never in the alert queue).

### 5.6 Device group, automation, and scoped access — `POS-030` ✅ hardened

- [ ] **Path:** System → Settings → Endpoints → Permissions → Device groups → Add device group
- **What it is:** A rule-based device group binding devices to an automation level and to a set of admins.
- **Why:** Two boundaries in one object — a policy boundary (remediation level) and an access boundary (which admins manage the devices).
- **Source guidance (module 31 guide):** Create the group with a membership rule, set the automation level, grant an Entra group access.
- **What we verified (2026-07-19):** Group *Lab Client Machines*, membership rule *Name starts with the lab prefix*, remediation **Semi (approval for non-temporary folders)** — chosen so ASR/detection tests are not auto-quarantined before observation. User access scoped to *SOC Device Admins* (§2.9). Membership committed in **≤28 min** (Apply 06:11 → committed 06:39; vendor 30–60). Analyst gained scoped visibility of the device as a group member — the RBAC composition (unlicensed Unified-RBAC identity + legacy device-group access) resolved as predicted.
- **The trap:** during the propagation window the device sat in **Ungrouped (default)** under **Full remediation** — the opposite of the chosen Semi. The rule previewed as matching instantly while committed membership lagged. Do not test against a device until membership commits, not merely until the rule previews. The exclusion half of scoped access (analyst *denied* an out-of-group device) is un-runnable at one device — `POS-030` revisit.

### 5.7 Device discovery — `POS-032`-adjacent ✅ default

- [ ] **Path (on/off):** System → Settings → Endpoints → Advanced features → Device discovery
- [ ] **Path (mode):** System → Settings → Device discovery → Discovery setup
- **What it is:** Onboarded devices observing and probing the network to surface unmanaged devices.
- **Why:** Verify the capability and its blast radius; a candidate source for a second device (Lab 05's T4).
- **Source guidance (module 32 guide):** Standard is default; watch the network scope.
- **What we verified (2026-07-19):** **On**, **Standard** mode (active probing), all onboarded devices. Log4j2 unauthenticated-probing sub-toggle **off** (default, correctly). **Zero discovered devices** — the single-VM isolated subnet has no unmanaged neighbours, so the capability is active with nothing to act on. Produced no onboardable second device, so Lab 05's T4 exclusion test stays blocked. Full note in the environment section below.

### 5.8 Defender XDR → Sentinel connector — `POS-032` ✅ hardened

- [ ] **Path:** Microsoft Sentinel → *(workspace)* → Content hub → install *Microsoft Defender XDR* → Data connectors → Microsoft Defender XDR
- [ ] **Path (status, unified):** security.microsoft.com → Settings → Microsoft Sentinel → SIEM workspaces
- **What it is:** The cloud-to-cloud connector that forwards Defender XDR incidents and alerts into the Sentinel workspace.
- **Why:** Completes the pipeline — endpoint telemetry and detections become Sentinel input.
- **Source guidance (module 35 guide):** Install the connector, connect incidents/alerts, optionally stream raw events.
- **What we verified (2026-07-19):** Connector **auto-connected** on Sentinel enablement — the unified portal wired the whole Defender family at *Connected/Primary* with no manual step. **Cost-safe:** raw `Device*` streaming **OFF** — confirmed by `DeviceEvents` failing to resolve as a table in the Sentinel Logs blade (it resolves fine in Defender Advanced Hunting — different store). Pipeline proven: detection test → Defender alert → Sentinel `SecurityIncident` (ProviderName *Microsoft XDR*), **~2 min sync** (UTC-converted).
- **The traps:** connector is **forward-only** (history does not backfill — prove flow with a fresh event); the incident wrapper syncs *ahead* of the discrete alert (query `SecurityIncident` or `search *`, not `SecurityAlert` alone); the Logs blade opens in Simple mode and must be switched to KQL mode.



---

# Part 2 — Everything else

Not Microsoft, and not in any source guide. Built for this repo.

## 6. GitHub repository configuration

### 6.1 Secret Protection and Push Protection

- [ ] **Path:** Repository → Settings → *(Security)* → Advanced Security
- **What it is:** Server-side secret scanning, and blocking of pushes containing
  detected secrets.
- **Why:** Local hooks are bypassable with `--no-verify`, and a clone without
  `pre-commit install` has no hooks at all. Server-side is neither.
- **State:** Both On.
- **Note:** The menu was renamed — no longer *Code security and analysis*, and the
  feature is no longer *Secret scanning*. Push protection is default-on for new public
  repos.
- **Consequence worth knowing:** free on public repos; **going private would silently
  remove this control** unless licensed.

### 6.2 Commit identity

- [ ] **Path:** GitHub → Settings → Emails
- **What it is:** Whether a real address is embedded in commit metadata.
- **Why:** A public repo embeds the author address in every commit, permanently, for
  anyone who clones. Under this repo's own `SANITIZATION.md` §1 that is attributable
  data — inconsistent to scrub UPNs from screenshots while publishing an inbox in the
  git log.
- **State:** Keep my email addresses private; noreply address used for all commits.

---

## 7. Sanitization gates — three layers

Design premise: **any single gate will be bypassed, disabled, or wrong.**

| Layer | Runs | Bypassable? | Catches |
|---|---|---|---|
| pre-commit | before commit | yes — `--no-verify` | everything, earliest |
| Push protection | server-side | no | known secret patterns |
| GitHub Actions | after push | no | everything, full history |

### 7.1 pre-commit — 13 hooks

- [ ] **Path:** `.pre-commit-config.yaml` · install with `pre-commit install`

| Hook | Purpose |
|---|---|
| `check-added-large-files` | accidental blobs |
| `detect-private-key` | key material |
| `check-json` / `check-yaml` | parse before commit |
| `end-of-file-fixer` / `trailing-whitespace` / `mixed-line-ending` | hygiene |
| `gitleaks (Azure/Sentinel scrub rules)` | the custom ruleset below |
| `block-binaries` | executables |
| `block-raw-captures` | `.pcap`, `.evtx` — raw captures carry more than intended |
| `strip-image-metadata` | EXIF via exiftool |
| `ocr-scan-images` | OCR then scan — see 7.3 |
| `generated-docs-fresh` | generated docs match their sources |

### 7.2 gitleaks source rules — `.gitleaks.toml`, 13 custom rules

- [ ] **Path:** `.gitleaks.toml` · `gitleaks git . --config .gitleaks.toml`

`azure-guid-any` · `azure-resource-id` · `azure-tenant-domain` · `upn-email` ·
`log-analytics-workspace-key` · `azure-ad-client-secret` · `azure-ad-secret-prefixed` ·
`logic-app-callback-url` · `azure-sas-token` · `azure-storage-connection-string` ·
`automation-webhook` · `public-ipv4-review` · `azure-vm-public-dns`

- **Design:** `[extend] useDefault = true` — all default rules plus these. Placeholder
  allowlists rather than path exemptions.
- **Engine constraint:** gitleaks uses **RE2**. No lookahead, no lookbehind, no
  backreferences. Exclusions must be allowlists, not negative assertions.
- **Found the hard way:** a global path exemption for `SANITIZATION.md` meant the
  document defining the redaction policy was the one file the scanner never read.
  Removed — the regex allowlists already cleared the placeholders, so it bought nothing
  and cost the scanner its most important file.
- **Scope note:** these rules are tuned for a Sentinel lab, where any public IP is
  suspect. Run against an IOC portfolio they produce ~92 findings, because there public
  IPs **are** the deliverable. Identical rules, opposite verdict, purely from context.

### 7.3 OCR gate — `.gitleaks-ocr.toml` + `scripts/scan-image-text.sh`

- [ ] **Path:** `bash scripts/scan-image-text.sh <image>`
- **Why it exists:** gitleaks reads bytes, not pixels. A screenshot is an opaque blob to
  every text scanner. Given lab evidence *is* screenshots, that gap is the whole
  exposure.
- **Pipeline:** tesseract OCR → despace pass → gitleaks against extracted text
- **Two tiers:** BLOCK (real values) / WARN (labels, heuristics)

9 rules: `ocr-identifier-label` · `ocr-directory-chrome` · `ocr-fuzzy-guid` ·
`ocr-fuzzy-onmicrosoft` · `ocr-fuzzy-cloudapp` · `ocr-email` · `ocr-ip-context` ·
`ocr-fuzzy-ipv4` · `ocr-ipv4`

- **The central finding — anchors.** Tesseract eats periods in small UI text. What
  survives is whatever the pattern can grip:

| Content | OCR damage | Recoverable? |
|---|---|---|
| Email | `analyst@contoso.com` → `analyst@contosocom` | **yes** — the `@` survives |
| Domain | separators dropped | **yes** — `onmicrosoft` survives |
| GUID | `72f988bf` → `7 2(988bf` | poor — fuzzy + despaced only |
| **IPv4** | `203.0.113.135` → `2030113.135` | **no** — no anchor exists |

- **Stated plainly in `SANITIZATION.md` §4: the OCR gate does not reliably catch IP
  addresses in images.** Strip an IP's dots and it is indistinguishable from a version
  string or a timestamp. The first fuzzy rule caught the IP *and* every four-digit year
  — and a gate that always warns is a gate nobody reads. IPs therefore get a heuristic
  at WARN tier and a documented limitation.
- **Every bug in these rules was found by a real screenshot.** Synthetic tests rendered
  text too cleanly to reproduce the damage real portal UI causes.

### 7.4 audit-pii.sh — 10-check sweep

- [ ] **Path:** `bash scripts/audit-pii.sh [--history]`
- **Checks:** gitleaks tree · gitleaks **full history** · emails · GUIDs · routable IPv4
  · tenant/lab hostnames · Azure resource IDs · personal terms · commit authors · images
  (OCR + EXIF)
- **Design note:** a script grepping for your own username would have to **contain**
  your username. Terms live in `.pii-terms`, gitignored, and findings report `term #2`
  rather than the term itself — printing it would put the identifier into scrollback and
  any pasted output.
- **Why `--history` matters:** it flagged history while the working tree was clean.
  Scrubbing a file does not scrub the commit that introduced it.

---

## 8. GitHub Actions — `.github/workflows/scrub.yml`

- [ ] **Path:** Repository → Actions → scrub

| Job | Does |
|---|---|
| `gitleaks (source)` | installs pinned gitleaks, scans **full history**, uploads SARIF |
| `gitleaks (image OCR)` | tesseract + gitleaks over every committed image |
| `Generated docs freshness` | `--check` on all three generators |

- **Pins:** `checkout@v7`, `setup-python@v6`, `upload-artifact@v6` — all Node 24.
  **Node 20 is removed from runners 2026-09-16**, with no opt-out after that date.
- **Why not `gitleaks/gitleaks-action`:** two reasons, both found by failure.
  1. It derives its scan range from the push event as `first_commit^..last`. After a
     history rewrite the first commit in the push is the **root commit** — and `root^`
     cannot exist. git fatals, the action scans **0 bytes**, reports *no leaks found*,
     then exits 1 because stderr was non-empty.
  2. It pins **its own** gitleaks build (8.24.3) regardless of what runs locally — so CI
     and pre-commit were scanning with different engines and different default rules.
- **The fix:** install the binary, run `gitleaks git .`, pin the version once in `env:`
  as `GITLEAKS_VERSION: 8.28.0` — same as local, and no range arithmetic to get wrong.
- **What to check in the log:** `5 commits scanned`. The old job reported *no leaks
  found* while scanning zero bytes. The commit count is what distinguishes a gate that
  looked from one that didn't.

---

## 9. Generated documentation

Three docs are **built from source and CI-enforced**. Editing them by hand fails the
build — they cannot drift.

- [ ] `python3 scripts/build-posture-register.py` → `docs/posture-register.md`
      ← `posture.yml`
- [ ] `python3 scripts/build-attack-matrix.py` → `docs/attack-coverage.md`
      ← detection frontmatter
- [ ] `python3 scripts/open-items.py` → `docs/open-items.md`
      ← `*(pending)*` markers in writeups

All three take `--check`, which is what CI runs.

`attack-coverage.md` distinguishes **CLAIMED / PARTIAL / COVERED** — only *validated*
detections count as coverage. A matrix that counts unvalidated rules as green is a
marketing document.

**This file is not generated.** It is maintained by hand and can drift. The register is
authoritative.

---

## 10. Local toolchain — WSL Ubuntu 24.04

- [ ] `gitleaks 8.28.0` — binary, not apt (not packaged)
- [ ] `exiftool 12.76` — `libimage-exiftool-perl`
- [ ] `tesseract 5.3.4` — `tesseract-ocr`
- [ ] `pre-commit 4.6.0` — via **pipx**; Ubuntu 24.04 blocks system `pip install`
      (PEP 668)
- [ ] `python3-yaml` — via **apt**, not pip, so system `python3` can see it (pipx would
      isolate it away from the generator scripts)
- [ ] `git-filter-repo 2.47.0` — history rewriting
- [ ] `gh 2.96.0` — from GitHub's apt repo; Ubuntu's package lags

- **WSL gotcha:** work on the **Linux filesystem**, not `/mnt/c/`. On Windows drives
  `chmod` silently does nothing without the `metadata` mount option — scripts stay
  non-executable, git records `100644`, and the hooks break.
- **Verify exec bits survived:** `git ls-files -s scripts/` → all `100755`.

---

## 11. Repo-level design decisions

- [ ] **`SANITIZATION.md`** — 5 data classes (secrets / identifiers / attributable /
      operational / indirect); placeholders are nil-GUID, `contoso.onmicrosoft.com`,
      `analyst@contoso.com`, RFC 5737 ranges, `LAB-WIN11-01`, `rg-soc-lab`
- [ ] **`docs/documentation-standard.md`** — never assert what wasn't observed; vendor
      expectation ≠ observed result; every decision names its rejected alternative;
      every lab-only weakening names the production answer
- [ ] **Status vocabulary** — 🔜 not built · 🔨 built, documenting · ✅ done and
      validated · *(pending)* = fact not yet known
- [ ] **Organisation** — by SOC capability + exam domain + ATT&CK, deliberately not by
      lecture order
- [ ] **Numbering** — follows actual build order, not the exam blueprint

**IOC policy:** this repo does not print invented IP addresses as examples. Labelling a
live routable address as attacker infrastructure is a factual claim about whoever holds
that allocation, and documentation examples get copied without their context. An address
appears only when genuinely observed and attributed.

---

### 3.5 Second VM (WIN-SRV-DEFENDER-01) and its access posture - POS-033 ✅ hardened

- [ ] **Path (create):** Virtual machines > Create > Azure virtual machine
- [ ] **Path (access):** via Azure Bastion as labadmin (no public inbound)
- **What it is:** A Windows Server 2022 VM built to be the source for agent-based Windows Security Event ingestion.
- **Why:** Lab 07 needs a Windows host whose own Security log can be collected by the Azure Monitor Agent.
- **What we verified (2026-07-25):** Standard_D2s_v3 (smallest generally-available size in West US - B-series and DS1_v2 were unavailable for this subscription), smalldisk WS2022 Datacenter Gen2, **Standard HDD** (changed from the Premium default), Security type **Standard** (POS-018 parity, no vTPM), **inbound None**, **no public IP** (the deployment attached one despite inbound None; dissociated and deleted), auto-shutdown 23:00 Pacific + email, **Manual** patch orchestration, boot diagnostics off. Access is **Azure Bastion as labadmin**.
- **Access reasoning (Bastion vs RDP):** VM 1 exposes RDP to the internet (POS-019, a weakening). This VM deliberately does not - inbound None + no public IP means it cannot be reached from the internet at all, a **better** posture than VM 1. The tradeoff: Bastion bills per hour (~$0.19/hr Basic, more than the VM while running), so it is a per-session teardown decision; RDP would be free but internet-exposed. Bastion also gives built-in clipboard sharing and, on some SKUs, requires a bare username.

### 3.6 Data Collection Rule (dcr-winsec-labsrv) - POS-033 ✅ hardened

- [ ] **Path:** Content hub > install "Windows Security Events" > Data connectors > Windows Security Events via AMA > Create data collection rule
- [ ] **Path (verify association):** Monitor > Data Collection Rules > dcr-winsec-labsrv > Resources
- **What it is:** The DCR that installs the Azure Monitor Agent on the VM and collects its Windows Security log into the SecurityEvent table.
- **Why:** The first agent-based ingestion path in the project - distinct from POS-032's connector path.
- **What we verified (2026-07-25):** DCR `dcr-winsec-labsrv` in rg-defender-lab, associated to WIN-SRV-DEFENDER-01. Selecting the VM in the DCR's Resources tab **auto-installed the AMA extension** (under 5 min). Collection tier **Common** (not All) - the cost decision, because SecurityEvent has NO free allowance here (that allowance needs Defender for Servers P2, which this environment lacks). Verified: Heartbeat (SCAgentChannel Direct, AMA v1.43), SecurityEvent populated with 4688/4673 events. Data lands in **SecurityEvent**, not WindowsEvent.

### 3.7 Azure Activity connector (diagnostic setting) - POS-034 ✅ hardened

- [ ] **Path (Method B, used):** Subscriptions > Azure subscription 1 > Activity log > Export Activity Logs > + Add diagnostic setting > law-soc-lab
- [ ] **Path (Method A, failed):** Data connectors > Azure Activity > Launch Azure Policy Assignment wizard
- [ ] **Path (verify):** Subscription > Activity log > Export Activity Logs (setting activity-to-law-soc-lab exists)
- **What it is:** Subscription control-plane operations (resource create/modify/delete, role assignments, policy changes) streamed to law-soc-lab, landing in AzureActivity.
- **Why:** Control-plane monitoring - the record of who did what to the subscription.
- **What we verified (2026-07-25):** Configured via **Method B (manual diagnostic setting)** after **Method A (Azure Policy) failed twice** - "you need to log in" at submission, 0 policy assignments confirmed both times (managed-identity/session token). Method B (categories Administrative + Security -> law-soc-lab) succeeded first try. AzureActivity populated (verified). For one subscription, Method B is the appropriate choice, not a fallback - Method A's policy+identity+remediation machinery only earns itself across many subscriptions.

### 3.8 Microsoft Entra ID connector - POS-034 ✅ hardened

- [ ] **Path:** Data connectors > Microsoft Entra ID > Open connector page > select log types > Apply
- [ ] **Path (verify):** Entra ID > Monitoring & health > Diagnostic settings (AzureSentinel_law-soc-lab exists)
- **What it is:** Identity logs - sign-ins, directory audits, and Entra ID Protection risk - streamed to law-soc-lab.
- **Why:** The foundation of identity-based detection and hunting.
- **What we verified (2026-07-25):** Enabled Sign-In Logs, Audit Logs, Risky Users, User Risk Events (high-volume types left off - the connector-level cost lever). Apply wrote the diagnostic setting AzureSentinel_law-soc-lab. Sign-in ingestion needs P1/P2; the E5 trial's P2 is live - **licensing test passed**, 489 sign-in events captured.
- **Two stores, not two names (corrected 2026-07-26):** **SigninLogs** is a Log Analytics workspace table written by this connector's diagnostic setting, scoped by the log types selected, and billable. **EntraIdSignInEvents** is a Defender XDR lake table written by XDR regardless of this connector, covering every sign-in class, and free. On the unified Defender surface both resolve in one query with very different counts (6 vs 972 on 2026-07-26); in Sentinel > Logs only SigninLogs exists. The original empty SigninLogs was propagation lag (~10-15 min), not a naming mismatch. Diffing one census across both portals is the reusable form of this - see `kql/sentinel/store-partition-diff.kql`.

### 3.9 Unified audit logging - `POS-035` ✅ hardened

- [ ] **Path (portal, could not complete):** Defender > System > Audit > Start recording user and admin activity
- [ ] **Path (used):** Exchange Online PowerShell > `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true`
- [ ] **Path (verify):** `Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled` - **in the EXO endpoint only**
- **What it is:** Tenant-wide recording of user and admin activity into the Microsoft 365 substrate.
- **Why:** Attack simulation reporting depends on it, and nothing else in this project had needed it. The tenant recorded nothing until 2026-07-26.
- **What we verified (2026-07-26):** Read `False` by cmdlet, set `True` by cmdlet, confirmed `True` on a later read. The **portal could not do this**: System > Audit showed two independent faults at once ("trouble figuring out if activity is being recorded" and "Failed to load data") and its enable button produced a Client Error. The page's inability to *determine* state was a separate fault from the state itself.
- **Endpoint trap:** the same cmdlet in Security & Compliance PowerShell returns `False` **even when auditing is on** (Microsoft Learn). Wrong endpoint returns a permanently false value with nothing to distinguish it from a true one.
- **Cost:** none. Audit data lives in the M365 substrate, not `law-soc-lab`. Becomes an ingestion cost only if the Office 365 connector is later added to Sentinel.

### 3.10 Exchange organisation customization (hydration) - `POS-036` ✅ default, irreversible

- [ ] **Path:** Exchange Online PowerShell > `Get-OrganizationConfig` / `Enable-OrganizationCustomization`
- **What it is:** New tenants ship *dehydrated*, sharing consolidated configuration objects rather than owning unique copies. Hydration is a one-time, **irreversible** move to a customizable state.
- **Why it is here:** It gates unified audit logging, it is invisible in every portal, and it had already been crossed before this project read the value.
- **What we verified (2026-07-26):** `IsDehydrated False`, and `Enable-OrganizationCustomization` returned "not required." **But `Set-AdminAuditLogConfig` failed with `InvalidOperationInDehydratedContextException` at the same time** - two sources said hydrated, the one operation that attempted work disagreed. Resolved by waiting ~30 minutes, after which the identical write succeeded. Per-object propagation behind an org-level boolean; Microsoft documents the org flag and says nothing about what sits under it.

### 3.11 Attack simulation campaign - `POS-037` ✅ hardened

- [ ] **Path:** Defender > Email & collaboration > Attack simulation training > Simulations > Launch a simulation
- [ ] **Path (report):** same > select the campaign > Report / Users / Details tabs, and View Activity Timeline
- **What it is:** A Credential Harvest campaign (Netflix global payload) to all users with the admin excluded, Microsoft training assigned, 2026-07-26 16:20:02 to 2026-07-28 16:20:02.
- **Why:** The first capability in this project that measures people rather than machines.
- **What we verified (2026-07-26):** Delivery ~1 min to the Focused Inbox, bypassing filtering. Compromise recorded. Two training modules assigned **by behaviour** (`ClickedPayload`, `Compromised`), ~90 s behind each trigger. Report fully populated, all denominators `/1` (exclusion held). **Zero incidents and zero alerts** over a one-week window - predicted, since Microsoft exempts its own drills.
- **The finding:** the payload is **absent from `EmailEvents` and `EmailUrlInfo` entirely**, while the training notifications either side of it are recorded normally in both. A simulation cannot be hunted - no row means no query, no detection rule, no ATT&CK mapping. Attack simulation training tests **users**; it is not evidence about detection coverage.


### 3.12 User reported settings - `POS-040` ✅ default, read-only visit that wrote state

- [ ] **Path:** Defender > Settings > Email & collaboration > User reported settings
- [ ] **Path (verify):** Exchange Online PowerShell > `Get-ReportSubmissionPolicy` / `Get-ReportSubmissionRule`
- **What it is:** What the Outlook and Teams Report buttons do, where reported items go, and what the reporting user is told afterwards.
- **What we verified (2026-07-27):** Built-in Report button (not a third-party add-in), Outlook and Teams monitoring on, quarantine reporting allowed, `EnableReportToMicrosoft True`. Submissions baseline clean — 0 across every counter on both tabs.
- **Blank is not unset:** routing reads *Microsoft and my reporting mailbox* with an empty mailbox field. That empty field is the documented default and resolves to the **global admin's mailbox**, undisplayed until the first user reports. Policy carries `ReportPhishToCustomizedAddress True`; the rule defining that address does not exist.
- **Four silent defaults:** confirm-before-reporting off, success message off, results email off, positive reinforcement *Do not deliver* (`POS-038`). Correct reporting behaviour receives no feedback of any kind.
- **Observation wrote state:** the policy object was created 2026-07-27 12:56:04 UTC on a tenant created 2026-07-14 — by opening the page, not by saving anything.
- **Open:** the reporting mailbox is not a SecOps mailbox, which Learn flags as important specifically when Attack simulation training is in use. Not exercised.


### 3.13 Microsoft Secure Score - baseline reading, 2026-07-27 (no configuration)

- [ ] **Path:** Defender > Exposure management > Microsoft Secure Score (Overview / Recommended actions / History / Metrics & trends)
- **What it is:** Microsoft's own measurement of this tenant's configuration posture, scored as points earned over points available. Read-only; nothing was set, planned, or risk-accepted.
- **Baseline (2026-07-27):** **44.68%**, 509.33 / 1140 points. Identity **16.49%**, Data 77.78%, Device 49.07%, Apps 40%. 114 to address, 0 planned, 0 risk accepted, 0 regressed. Peer comparison 44.68 vs **46.75** for organisations of similar size.
- **The Identity number corroborates `POS-001`.** Security Defaults are off with no Conditional Access replacing them, and Identity is the weakest category by a wide margin with both top recommendations by score impact being MFA. Secure Score is measuring the gap the register already documented.
- **`POS-031` disproved and narrowed** — both locally-set ASR rules read **Completed, 9/9**, and the history logged the 0/9 → 9/9 transition on Lab 06's build date. Full account in Lab 06 §7.
- **The score is a ratio, and the denominator moves.** The score rose 35% → 46.2% by 07-18, **fell to 44.7% on 07-19**, and has been flat since — with **Regressed = 0**. Nothing got worse: 56 further recommendations became relevant on 07-19 (mostly Apps, as Defender for Office 365 came into scope), enlarging the denominator faster than the numerator. A falling Secure Score can be a licensing event rather than a security event.
- **The largest movement was discovery, not hardening.** 118 of 185 history entries are dated 07-18, the day Lab 03 onboarded the endpoint: Defender Antivirus 10/10, real-time protection 10/10, firewall 10/10, SmartScreen 9/9, SMBv1 disabled 8/8 and a long tail besides. Those points reflect **stock Windows 11 defaults being discovered**, not work performed.
- **Most of this project is invisible to it.** Labs 07 and 08 (ingestion, 07-25) and Lab 09 (attack simulation, 07-26) produced **no Secure Score movement at all**. Correct — they are not configuration controls in its model — but it bounds what the number measures.
- **No actor attribution.** All 185 history entries read `Attributed to: System`, including the actions the operator performed personally.
- **`Last synced` is per-recommendation, and the page's "up to 24 hours" describes no particular row.** *Ensure Microsoft 365 audit log search is Enabled* still read `0/3 · To address` on 2026-07-28 — but its Last synced is **2026-07-25**, two days before auditing was enabled (`POS-035`). Not evaluated-and-refused; **not re-evaluated**. Its source product is **Microsoft Information Protection**, where the ASR rules are Defender for Endpoint and synced 07-27. A status of *To address* therefore means the control is absent **or** that product has not re-read since it was added — check Last synced before concluding either. Licensing is not the blocker (`Have license? Yes`).


### 3.14 Enforcement scope / MDE security settings management - `POS-041` ⬜ default, off

- [ ] **Path:** Defender > Settings > Endpoints > Configuration management > Enforcement scope
- [ ] **Second switch (not visited):** Intune > Endpoint security > Microsoft Defender for Endpoint connector settings — the same page carrying `POS-011`
- **What it is:** Lets MDE enforce security configuration on devices **not enrolled in Intune**. Requires both switches.
- **State (2026-07-27):** `Use MDE to enforce security configuration settings from Intune` = **Off**. Observed, not changed.
- **Why it matters:** it corrects Lab 06's asserted claim that local PowerShell was the only deployment path. It was not — this path exists for exactly the unenrolled case, and was simply off.
- **Adjacent:** `Intune Permissions` is empty; no Entra group has ever been granted Endpoint Security permissions in Intune.
- **Deferred test:** deploying the two ASR rules as policy and watching whether the ASR report starts showing them is a direct test of `POS-031`'s mechanism. Needs a live endpoint, so it batches with custom detections and analytics rules. *(pending)*


### 3.15 Threat analytics - read-only survey, 2026-07-27 (no configuration)

- [ ] **Path:** Defender > Threat intelligence > Threat analytics
- [ ] **Path (notifications):** Settings > Microsoft Defender XDR > Email notifications — three tabs, all empty (`POS-042`)
- **Not a third console.** The per-threat **Recommended actions** tab *is* Secure Score, filtered to that threat — identical columns, identical global rank numbers, same `Last synced`. It agrees with Secure Score because it is Secure Score, so the ASR disagreement remains two-way.
- **`Misconfigured devices: 1` explained:** two of four threat-relevant recommendations unmet on one device. Both are ASR-family and both are **different rules** from the two Lab 06 set — consistent with Secure Score, no contradiction.
- **Endpoints exposure is half the described feature** — vulnerabilities only ("no trackable vulnerabilities associated with this threat"); the configuration half lives on the Recommended actions tab.
- **IOCs unreachable** — see divergence row 26.
- **Adjacent, noted for later:** the Recommended actions tab carries a banner offering to configure Secure Score data visibility by data source in **URBAC** — relevant to `POS-027` and to `POS-002`, the one standing unverified entry.


## The divergences

Where the source guides and this environment disagree. Every one was found by checking
rather than assuming, and every one is silent — no guide step is wrong enough to raise
an error.

Rows 1–6 are recorded against the section-1 guides **as originally written**; all six have
since been corrected in the revised versions. Rows 7+ are live-era divergences from the
endpoint/Sentinel section — decided or discovered during configuration, per the
live-configuration rule (the guide is correct for a normal environment; the deviation is
this environment's).

| # | Guide says | Environment is | Consequence | Record |
|---|---|---|---|---|
| 1 | **G1**: Azure free trial gives $200 credit; services pause at exhaustion; card never auto-charged | Pay-as-you-go, uncapped, no credit (`POS-005`) | **The safety net does not exist.** No spending limit is available. Budgets notify but cannot cap. Deallocation (`POS-016`) is the only real control | **revision notes only** — original G1 not read back |
| 2 | G4: The MDE↔Intune connection lets Intune enforce compliance based on Defender's device risk | Connection *Available*, but `POS-011` is **Off** | G4's two steps do not enable risk-based compliance. The step that does is never mentioned. Following the guide exactly produces an integration that reports healthy and does not do what the guide says | **original, 2026-07-17** — two steps, toggle absent, verbatim |
| 3 | **G1**: Cancel the subscription before the trial ends | Turned recurring billing off instead (`POS-017`) | Cancelling ends access immediately; turning recurring billing off keeps the trial to full term and stops the conversion. Same cost, four more weeks of lab | **revision notes only** — original G1 not read back |
| 4 | **G2**: the device silently registers with Intune after sign-in | Never enrols (`POS-022`) | **The sharpest one.** G2 describes user-driven join behaviour; G5 builds a VM joined by the `AADLoginForWindows` extension. Both guides individually correct; together they produce a device that never enrols, with every precondition satisfied and no error raised | **revision notes only** — original G2 not read back |
| 5 | **G5**: troubleshoot Entra sign-in failure by disabling blocking Conditional Access policies | **Zero CA policies exist** (`POS-003`) | The prescribed remedy has no cause to address. The real failure was `AADSTS50055` — expired password on a new account — found in `dsregcmd`, not in the guide. Following the guidance would mean hunting for policies that aren't there, or disabling unrelated things to make an error go away | **original, 2026-07-17** — §5 read back verbatim |
| 6 | **G3**: *Quick Step* block instructs setting Security defaults to **Enabled** | Its own TLDR says disable | A copy-paste of Microsoft's *enable* procedure into a guide about disabling. Following the Quick Step literally does the opposite of the guide's purpose | **revision notes only** — original G3 not read back |
| 7 | **Module 25 guide**: run the onboarding script from an elevated *interactive* command prompt | Used SYSTEM via Azure Run Command instead — then, when Run Command proved unavailable (`POS-028`), the interactive `labadmin` path via Bastion | First divergence of the live era, and a chosen one: SYSTEM avoids an interactive privileged session on the endpoint (`POS-021`). Recorded here rather than in a guide revision note, per the live-configuration rule — the guide is correct for a normal device; the deviation is environment-specific | **live, 2026-07-18** — decided during configuration, no revision note exists |
| 8 | **Module 24 guide**: a created and assigned URBAC role is complete | Role enforces nothing until its **workload is activated** (`POS-026`) | "Default model" (legacy unavailable) is not "active" (enforcing). The assigned analyst sees no Incidents/Hunting/Assets until activation, with no warning. The one divergence a source guide named in advance | **live, 2026-07-17** — before/after measured, unrepeatable once telemetry exists |
| 9 | **Module 31 guide**: the membership rule places the device in the group | Rule matches instantly in **preview**; committed membership lags 30–60 min, during which the device sits in **Ungrouped / Full remediation** — the opposite of the chosen Semi (`POS-030`) | Every visible signal reads "configured" while the intended policy is not in force and the default one is. Do not test until membership *commits*, not merely until the rule previews | **live, 2026-07-19** — Apply 06:11 → committed ≤06:39 |
| 10 | **Module 33 guide**: the ASR **report** shows which rules are firing | Report shows the device **"Rules off"** — 0 detections at filter=Any — while both locally-set rules actively block (`POS-031`) | The report is scoped to policy-managed rules; locally-set (PowerShell) rules are invisible to it. A downstream consequence of `POS-022` — local PowerShell is the only path here, and the report cannot see it. Verify in Advanced hunting | **live, 2026-07-19** — confirmed with filters at Any and via event log/hunting |
| 11 | **Module 35 guide**: connect the Defender XDR connector manually; incident sync is a configured step | Connector **auto-connected** on Sentinel enablement (unified portal + Unified RBAC); and it is **forward-only** — history does not backfill (`POS-032`) | No manual connect was needed. Proving flow requires a *fresh* event, not a query for existing incidents; and the incident wrapper syncs ahead of the discrete alert, so `SecurityAlert` alone reads empty while the incident is present | **live, 2026-07-19** — pipeline proven with a fresh detection test |
| 12 | **Windows events guide**: installing the Windows Security Events solution pulls in its dependency, Endpoint Threat Protection Essentials | The dependency did **NOT** auto-install — it showed "not installed" after the solution went in (`POS-033`) | Ingestion does not need it (it is the detection layer, not the ingestion layer), so it did not block the lab — but the "installs with dependencies" claim did not hold here. Detection on SecurityEvent is deferred to the later alerts/incidents work | **live, 2026-07-25** — observed at Content hub install |
| 13 | (implicit) an Azure VM's name is its hostname | The Azure resource name **WIN-SRV-DEFENDER-01** (19 chars) exceeds the 15-char Windows NetBIOS limit, so the OS hostname and the `Computer` field truncate to **WIN-SRV-DEFENDE** (`POS-033`) | A KQL filter of `Computer == "WIN-SRV-DEFENDER-01"` returns nothing. Match the truncated name or use `startswith`. Silent — the query just returns empty | **live, 2026-07-25** — confirmed in Heartbeat and SecurityEvent data |
| 14 | **Azure Activity guide**: Method A (Azure Policy) is the recommended path to stream Activity logs | The policy wizard **failed twice** — "you need to log in" at submission, 0 policy assignments confirmed; **Method B (manual diagnostic setting) worked first try** (`POS-034`) | Not user error — the wizard's managed-identity creation needs a privileged token and the session kept expiring. For a single subscription Method B is architecturally appropriate anyway; Method A's complexity only earns itself at multi-subscription scale. Decision rule: count subscriptions | **live, 2026-07-25** — 0 policy assignments confirmed both attempts |
| 15 | **Entra guide**: verify sign-in ingestion by querying `SigninLogs` | `SigninLogs` was empty when queried ~10 min after Apply, while `EntraIdSignInEvents` held 489 rows in the Defender surface. **Amended 2026-07-26** — this was originally recorded as the two being one dataset under two surface-specific names. A census run on both portals returned *both* tables together in Defender (6 vs 972) and only `SigninLogs` in Azure, disproving that. Different **producers**: `SigninLogs` is connector-fed, scoped by the selected log types, billable; `EntraIdSignInEvents` is Defender XDR-native and free (`POS-034`) | The residual divergence is real but smaller than claimed: the guide's verification step gives a **false negative if run inside the propagation window** (~10–15 min), and on the unified surface a similarly named XDR table with ~160× the volume sits beside it, inviting exactly the misreading recorded here. The original entry picked the schema-name explanation over the propagation-lag one documented in the same section | **live, 2026-07-25**; **corrected live, 2026-07-26** — both-portal census |
| 16 | **Attack simulation guide** §4: *Simulations > Launch a simulation*, then straight to Select technique | The portal interposes a fork first - **automation (multiple techniques, condition-triggered) vs single simulation (one technique, one payload)**. Choosing the top radio silently lands you in a different feature (`POS-037`) | Same destination, one undocumented decision. The guide covers automations separately in §6 without noting that the launch flow now begins by asking which one you want | **live, 2026-07-26** |
| 17 | **Attack simulation guide** §1 lists licensing as the prerequisite (MDO Plan 2 / E5) | Licensing is necessary and **not sufficient**. Reporting additionally requires unified audit logging (`POS-035`), which requires a hydrated Exchange org (`POS-036`), which new/trial tenants do not have. Nothing in the guide mentions any of it | Follow the guide exactly on a fresh tenant and the campaign launches cleanly, reports nothing, and the only clue is a portal banner naming one link of a five-link chain | **live, 2026-07-26** - banner observed, chain resolved by cmdlet |
| 18 | **Attack simulation guide** §3: *Send a test* sits at payload selection | It is **also** on the Review page. Not documented, and it delivers to the **currently signed-in user** - which is the excluded admin in this design, i.e. the exclusion control | Testing into the control mailbox makes an exclusion failure indistinguishable from a test artifact. Declined deliberately (`documentation-standard.md` §1) | **live, 2026-07-26**; Microsoft Learn confirms the Review-page button |
| 19 | **Attack simulation guide** §2 enumerates seven techniques and their payloads | Seven confirmed. But **QR code payloads are absent from the guide entirely** - they replace the phishing URL for Credential Harvest, Link to Malware, Drive-by URL, OAuth Consent Grant and How-to Guide | A whole payload class, and currently a live phishing trend, missing from the technique inventory an analyst would plan campaigns from | **Microsoft Learn, 2026-07-26** - not observed in-portal |
| 20 | **Action center guide** §4/§6: an empty Action Center means either submitted-item analysis has not returned, or the devices are set to *No automated response* | Neither applied. Lab 03's detection ran an automated investigation (`senseir.exe` self-collection observed) on a device under **Full** automation, and `Action center → History` still reads "No actions found" | A third cause is missing from the list and it is the one that applies: **the detection produced no remediable artifact**. The test downloads from `127.0.0.1` where nothing is served, so no supported action — quarantine, registry, service, driver, task, device — has an object. Following the guide's two-item list sends an analyst hunting a misconfiguration that does not exist. **An alert is not an action**; detection coverage and remediation coverage are separate measurements | **live, 2026-07-27** — Action center read directly |
| 21 | **Action center guide** §3: user reported settings govern where reports route — read the page to know the destination | The page cannot tell you. The mailbox field is blank (confirmed placeholder), and blank is the documented default meaning **the global admin's mailbox**, which is not displayed until after the first user reports. The cmdlets split it further: the policy carries `ReportPhishToCustomizedAddress True` while `Get-ReportSubmissionRule` returns nothing (`POS-040`) | Configuration spread across two objects, one absent, operative value in neither and invisible in the portal. **The only way to learn where reports go is to send one.** `POS-011`'s shape at a third polarity — a blank field over a live destination | **live, 2026-07-27** — portal + `*-ReportSubmission*` cmdlets |
| 22 | **Microsoft Learn** documents the default user-reported state (routing, blank mailbox, no submission rule) | It does not mention that the default policy object **does not exist until the settings page is opened**. `WhenCreatedUTC` reads 2026-07-27 12:56:04 on a tenant created 2026-07-14 — inside the window of the first visit, `WhenChangedUTC` identical (`POS-040`) | **Reading configuration wrote configuration.** Nothing was saved and no Save exists for that action. A secondary source claims this; this is the direct measurement. An audit is not necessarily a non-event, which undercuts the assumption every audit rests on | **live, 2026-07-27** — `Get-ReportSubmissionPolicy` timestamps |
| 23 | **Secure Score guide** §1/§8: the score "regresses if configuration drifts" — a falling number means posture got worse | The score **fell from 46.2% to 44.7% on 07-19 with `Regressed = 0`**. Nothing drifted. 56 further recommendations became relevant that day as Defender for Office 365 came into scope, enlarging the denominator faster than the numerator | The score is a **ratio**, and the denominator moves independently of posture. A drop can be a licensing or capability event rather than a security one, and the guide offers no way to tell them apart. Read the Regressed count before reading the trend | **live, 2026-07-27** — History export, 185 entries |
| 24 | **Lab 06 / `POS-031`** (this repository, not a vendor guide): locally-set ASR rules are "invisible to the console" | Too broad. **Microsoft Secure Score shows both rules Completed at 9/9** and its history logged the 0/9 → 9/9 transition on 2026-07-19, Lab 06's build date. The ASR *report* remains blind; Secure Score is not | Self-correction. The narrow claim (the ASR report is scoped to policy-managed rules) survives and is now **established rather than inferred** — Secure Score logging the change proves the configuration reached the cloud, so the report's blindness is scope, not lag. The corrected finding is stronger: two consoles in one product, same configuration, opposite readings | **live, 2026-07-27** — Recommended actions + History export |
| 25 | **Lab 06 §2** (this repository): with Intune enrolment foreclosed (`POS-022`) and no AD for GPO, "PowerShell is the only available path" for deploying ASR rules | A third path existed and was never checked. **Settings → Endpoints → Enforcement scope** offers MDE security settings management, described in the portal as applying "to devices that are not yet enrolled to Intune" — this tenant exactly. It is **off**, which is the shipped default (`POS-041`) | Self-correction, and an **asserted absence** — the class this repository keeps catching elsewhere. The consequence is not cosmetic: policy-deployed rules are the class the ASR report *can* see, so `POS-031`'s headline finding exists because a switch was off and openable rather than because a path was closed | **live, 2026-07-27** — toggle read, not changed |
| 26 | **Threat analytics guide** §3: IOC access "requires tenant verification — a one-time process that can take at least an hour" | It is a **business identity check**, not an administrative wait. The flow demands business formation documents, domain ownership records and **government-issued ID**, and frames the operator as the organisation's legal representative | Not a licensing or configuration gate but a **legal-entity gate**, which a trial tenant on `.onmicrosoft.com` has nothing to satisfy. Threat analytics IOCs are therefore **structurally unreachable** here. Verification was **not started** — declining to submit personal identity documents to unlock a lab feature is the record | **live, 2026-07-27** — flow opened, not completed |
| 27 | **Threat analytics guide** §2 lists eight threat categories: ransomware, extortion, phishing, hands-on-keyboard, activity group, vulnerability, attack campaign, tool/technique | The portal's categories are **seven and different** — Activity, Actor, Core threat, Technique, Tool, Vulnerability, OSINT — each with an in-product definition | The guide's list is the **Threat tags** column, not Category. Two distinct fields conflated, and they filter separately. Also: OSINT is 687 of the seven counters' 1,000, where the guide files OSINT as a newer preview capability | **live, 2026-07-27** — category tooltip |
| 28 | **Threat analytics guide** §2/§7: "Highest exposure threats" ranks what you are most exposed to; track exposure over time as you remediate | Exposure level is **ternary and recency-bound**: `Not available`, `0 - Low`, `30 - Medium`. Everything carrying a value was published Jul 2026; the unassessed block is the 2023–2025 back catalogue | The panel ranks a **recent slice**, and most of the 3,150-item library is not scored at all. A two-valued field across the scored portion is not a gradient, and in a single-device tenant "highest exposure" is close to meaningless. Only 2 of a dozen-plus columns are filterable (Category, Threat tags) | **live, 2026-07-27** — sorted ascending, 3,150 items |
| 29 | **Alert policy guide** §3/§5: create a custom policy for the activity you care about; built-in policies are mentioned separately as background | A built-in policy — *Creation of forwarding/redirect rule* — **already covered the chosen activity** and fired alongside the custom one at Informational. Same activity, same user, same timestamp: **2 alerts, 2 emails, 1 incident** (`POS-043`, `DET-003`) | 49 policies in this tenant, **48 built-in**. The guide never says *check the built-ins for overlap before authoring*, and its absence produced duplicate alerting on the very first custom policy created. This is how alert fatigue starts — unexamined overlap, not bad policies | **live, 2026-07-28** |
| 30 | **Alert policy guide** §2/§3: the three parts are activity, conditions and trigger; pick a trigger | The **threshold trigger is pre-selected**, at 15 activities in 60 minutes. In a three-identity tenant no threshold policy on any activity would ever fire | Accepting the default yields a policy that is enabled, correctly configured and **structurally silent**. The guide's own §8 warns that most "policy not working" reports are timing or aggregation — three sections away from the page that pre-selects the trigger causing it | **live, 2026-07-28** |
| 31 | **Alert policy guide** §2: choose an activity by name from the list | The friendly label is not the stored value. The picker offers *Created mail forward/redirect rule*; the policy stores **`Activity is MailRedirect`**, and `MailRedirect` is what appears in the alert body and the unified audit log | The schema value is the one you hunt on, and nothing in the wizard reveals it — it surfaces only on the review page and in the notification. Same shape as `POS-034`'s two-store finding and Lab 09's PowerShell endpoint trap: **the name depends on the surface** | **live, 2026-07-28** |
| 32 | **Alert policy guide** §3 step 1: give the policy a descriptive name and description so you can identify its alerts later | The **description reaches nobody**. Both notification emails — custom and built-in — carry identical `Details` text, so that string is a property of the *activity*, not the policy. Severity is the only field the custom policy actually changed | A description written to carry context (here, the MITRE `T1114.003` reference) exists only in the portal. An analyst reading the alert email gets Microsoft's generic activity text regardless of what was authored | **live, 2026-07-28** |

---

## Navigation drill

Cover the path column. From each portal's home page, find:

1. The toggle deciding whether device risk reaches Intune compliance *(4.2)*
2. The other half of that same integration *(5.1)*
3. Where Security Defaults is enabled or disabled *(2.1)*
4. Where automatic Intune enrolment is scoped — **both** paths *(2.6)*
5. Where a budget's scope is chosen, and why it cannot be changed later *(3.2)*
6. Where you would see whether a VM is billing you right now *(3.3)*
7. Where recurring billing is turned off without cancelling *(1.3)*
8. Where a custom Defender role's workloads are activated *(5.4)*
9. Where a device group's automation (remediation) level is set *(5.6)*
10. Where you confirm raw endpoint events are NOT streaming to Sentinel *(5.8 — DeviceEvents fails to resolve in Sentinel Logs)*
11. Where device-discovery mode (Basic/Standard) is chosen *(5.7)*
12. Where a Data Collection Rule's event tier (All/Common/Minimal/Custom) is set *(3.6 — and why Common, not All)*
13. Where you confirm the Azure Monitor Agent installed on a VM *(VM > Extensions > AzureMonitorWindowsAgent)*

Then, without looking:

- Which two settings compound into a weaker-than-default tenant? → `POS-001` + `POS-003`
- Which setting makes a compliance policy silently never fire? → `POS-011`
- Which single mechanism actually stops Azure spend here? → `POS-016`, deallocation
- Which charge has no alert attached at all? → the M365 conversion, `POS-017`
- Which settings are asserted but never observed? → `POS-002`, `POS-006` — down from
  five; `POS-003`, `POS-007`, `POS-008` were verified 2026-07-17
- Which two independent faults each break device-risk compliance on their own? →
  `POS-011` (connector off) and `POS-018` (no TPM/Secure Boot to evaluate)
- Which finding has every precondition satisfied and still never happens? → `POS-022`
- Which role reads "complete" but enforces nothing until a separate step? → `POS-026`, workload activation
- Which control blocks live while the console reports the device unprotected? → `POS-031`, locally-set ASR vs the policy-scoped report
- Which query works in Defender hunting and fails in Sentinel Logs — and why that failure is good news? → `DeviceEvents`; it confirms raw streaming is off (cost-safe), `POS-032`
- Which two SOC surfaces speak the same KQL over different data stores? → Defender Advanced Hunting (free raw lake, `Timestamp`) and Sentinel Logs (billed workspace, `TimeGenerated`)
- Which collection tier turns a Windows Security Events DCR into a firehose, and why does it bill fully here? → "All"; SecurityEvent's free allowance needs Defender for Servers P2, which this environment lacks (`POS-033`)
- Why does `Computer == "WIN-SRV-DEFENDER-01"` return nothing? → the OS hostname truncates to 15 chars (`WIN-SRV-DEFENDE`); use `startswith` (`POS-033`)
- On a VM nobody logged into, why are there 4624 "successful logon" events? → LogonType 5 service logons (SYSTEM); the meaning is in LogonType, not the count (`POS-033`)

## Device discovery — environment note (Lab, module 32)

Device discovery verified **On**, **Standard** mode (active probing), scoped to all
onboarded devices, 2026-07-19. The **Log4j2 unauthenticated-probing** sub-toggle is
**off** (default; the more aggressive option, correctly disabled).

**Zero discovered devices.** The single-VM isolated Azure subnet presents no unmanaged
neighbours, so the capability is active with nothing to act on — configured, effective,
empty by environment. It will stay empty until a second device shares the segment. The
Azure fabric (e.g. the WireServer at `168.63.129.16`) is visible in device *telemetry*
but is not surfaced as a discoverable device. Active-probing rules-of-engagement matter
in production; moot at n=1. No onboarded second device is produced, so Lab 05's T4
exclusion test remains blocked.
