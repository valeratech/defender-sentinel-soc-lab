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
  **Amended 2026-08-06:** the M365 E5 trial was extended once (`POS-077`) and now runs
  to **2026-09-14**. Office 365 E5 was deliberately *not* extended and still lapses
  **2026-08-13**, which is what makes the acquisition-dependency question testable in
  isolation.
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
- **Why:** Both trials took a payment method and both were, as first recorded on
  2026-07-16, configured to convert on 2026-08-13. Neither statement holds now: O365 E5's
  recurring billing is off, and M365 E5's conversion moved to 2026-09-15 with the
  extension.
- **Source guidance (G1):** Cancel the subscription before the trial ends — Billing →
  Your products → select subscription → Cancel subscription.
- **What we did instead (2026-07-16):** Turned recurring billing **off** on Office 365
  E5. **Rejected cancelling**, per Microsoft's own documentation: cancelling ends
  access, whereas turning recurring billing off leaves the subscription active until it
  expires and simply stops the conversion. Same cost, full remaining term of lab
  access.
- **Verified:** the panel now reads *Expires on August 14, 2026* in place of *changes to
  paid subscription* — the documented indication that recurring billing is off.
- **Corrected 2026-08-06:** that August 14 is **not the O365 expiry date**, and this
  document read it as one. The O365 E5 product page carries three banners and an
  Expiration date field all reading **2026-08-13**. The Recurring billing field renders
  the *transition day* — when the consequence of the setting lands — not the trial end.
  See divergence row 134 and `POS-078`.
- **Left on deliberately:** Microsoft 365 E5, converting **2026-09-15** at 1 licence,
  1 month, pay monthly (was 2026-08-14 before the `POS-077` extension). That was Microsoft's own default for the conversion and matches
  what the lab needs — month-to-month, cancellable at any renewal.
- **Divergence from G1:** G1's cancel-based advice is not wrong, but it costs the
  remainder of the trial. Turning off recurring billing is strictly better for a lab,
  and G1 does not mention it.
- **Open, tested live 2026-08-13** — unchanged by the extension, because O365 E5 was not
  extended: whether M365 E5 minds O365 E5 lapsing. G1 makes
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
- **CORRECTED 2026-08-01 — the "no free credit" claim above is withdrawn.** A $200
  sign-up credit exists (effective 2026-07-14, expires 2026-08-13) on a **different
  billing profile** than the one carrying lab spend — see `POS-058` and §3.6. G1 was
  right that the credit exists and wrong about the safety catch: the spending limit is
  unavailable on pay-as-you-go pricing, so this environment holds credit **without** the
  services-pause mechanism the credit model normally implies — worse than either
  position this document has held. The 2026-07-16 verification consulted resource cost
  analysis, which is scoped to the spending subscription's profile and structurally
  cannot see the other profile's credit. The original text above is retained as written;
  divergence rows 1 and 60 carry the withdrawal.

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
- **CORRECTED 2026-08-01 — "the only mechanism that actually ends spend" overstates.**
  True for compute; false for **managed disks and public IPs**, which bill while they
  exist and continued accruing into August with both VMs deallocated. Measured by
  invoice: July actual **~$10.84 pre-tax** against **~$7.58** tracked — a ~43%
  understatement, mostly storage and IP hours on "stopped" machines. Deallocation ends
  compute spend; **deletion** ends resource spend. Same family as Bastion — Lab 07
  records it billing per hour while up, and it offers no stopped/deallocated state at
  all, which is why the hosts were deleted rather than stopped — now measured on
  resources that DO have a stopped state; the state just covers less than the word
  suggests. Divergence row 61.

### 3.4 Log Analytics workspace & Microsoft Sentinel — `POS-032` ✅ hardened

- [ ] **Path (workspace):** Log Analytics workspaces → Create
- [ ] **Path (Sentinel):** Microsoft Sentinel → Create → select workspace
- **What it is:** The Log Analytics workspace `law-lab-01` is the data store; Microsoft Sentinel is the SIEM/SOAR layer enabled on top of it.
- **Why:** The section capstone — the aggregation layer that every prior lab feeds into.
- **Source guidance (module 35 guide):** Create a workspace, enable Sentinel, connect data sources; retention and ingestion are the cost levers.
- **What we verified (2026-07-19):** Workspace `law-lab-01`, **West US** (matches the VM's region), **Pay-as-you-go (Per GB 2018)**, placed in the VM's resource group so the whole lab is one deletable teardown unit (`POS-015`). Sentinel enabled — trial **2026-07-19 → 2026-08-19**, 10 GB/day free on both Sentinel and Log Analytics. Creating the workspace is free; ingestion and retention beyond the free window are the meters. Commitment-tier decision deferred until steady-state volume is known (`POS-032` revisit).
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

### 3.6 Azure billing topology — `POS-058` ❌ gap — recorded 2026-08-01

- [ ] **Path:** Cost Management + Billing → Billing scopes (and → Payment methods per
  profile)
- **What it is:** Which billing account and billing profile every dollar and every
  credit actually attaches to.
- **What we verified (2026-08-01):** **Two Microsoft Customer Agreement billing
  accounts, identically named**, each with its own billing profile. Profile A holds the
  **$200 credit** (effective 2026-07-14, expires 2026-08-13) and has never carried a
  charge. Profile B carries **every dollar of lab spend** and holds no credit. Under
  MCA, credits attach to a billing profile and pay down only that profile's invoice —
  the credit is **structurally unable to reach the lab**.
- **Why it went unseen for 18 days:** the surface consulted (resource cost analysis) is
  scoped to the spending subscription and cannot render another profile's credit. The
  payment-methods page answers a different question than the cost page — the
  identify-the-surface rule applied to money.
- **Decision, with reasoning:** **do not chase the credit.** Migration or rebuild to
  capture $200 costs hours of an 11-day budget, and the existing VMs carry the ASR
  state that `POS-031`'s pending enforcement-scope test is a test *of*. It expires
  unspent by choice.
- **Related hazard:** both subscriptions are named **`Azure subscription 1`**. Every
  portal picker shows the name; the name does not disambiguate. Renaming one is a
  standing recommendation.

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

### 3.5 Second VM (LAB-SRV-DEFENDER-01) and its access posture - POS-033 ✅ hardened

- [ ] **Path (create):** Virtual machines > Create > Azure virtual machine
- [ ] **Path (access):** via Azure Bastion as labadmin (no public inbound)
- **What it is:** A Windows Server 2022 VM built to be the source for agent-based Windows Security Event ingestion.
- **Why:** Lab 07 needs a Windows host whose own Security log can be collected by the Azure Monitor Agent.
- **What we verified (2026-07-25):** Standard_D2s_v3 (smallest generally-available size in West US - B-series and DS1_v2 were unavailable for this subscription), smalldisk WS2022 Datacenter Gen2, **Standard HDD** (changed from the Premium default), Security type **Standard** (POS-018 parity, no vTPM), **inbound None**, **no public IP** (the deployment attached one despite inbound None; dissociated and deleted), auto-shutdown 23:00 Pacific + email, **Manual** patch orchestration, boot diagnostics off. Access is **Azure Bastion as labadmin**.
- **Access reasoning (Bastion vs RDP):** VM 1 exposes RDP to the internet (POS-019, a weakening). This VM deliberately does not - inbound None + no public IP means it cannot be reached from the internet at all, a **better** posture than VM 1. The tradeoff: Bastion bills per hour (~$0.19/hr Basic, more than the VM while running), so it is a per-session teardown decision; RDP would be free but internet-exposed. Bastion also gives built-in clipboard sharing and, on some SKUs, requires a bare username.

### 3.6 Data Collection Rule (dcr-winsec-lab) - POS-033 ✅ hardened

- [ ] **Path:** Content hub > install "Windows Security Events" > Data connectors > Windows Security Events via AMA > Create data collection rule
- [ ] **Path (verify association):** Monitor > Data Collection Rules > dcr-winsec-lab > Resources
- **What it is:** The DCR that installs the Azure Monitor Agent on the VM and collects its Windows Security log into the SecurityEvent table.
- **Why:** The first agent-based ingestion path in the project - distinct from POS-032's connector path.
- **What we verified (2026-07-25):** DCR `dcr-winsec-lab` in rg-soc-lab, associated to LAB-SRV-DEFENDER-01. Selecting the VM in the DCR's Resources tab **auto-installed the AMA extension** (under 5 min). Collection tier **Common** (not All) - the cost decision, because SecurityEvent has NO free allowance here (that allowance needs Defender for Servers P2, which this environment lacks). Verified: Heartbeat (SCAgentChannel Direct, AMA v1.43), SecurityEvent populated with 4688/4673 events. Data lands in **SecurityEvent**, not WindowsEvent.

### 3.7 Azure Activity connector (diagnostic setting) - POS-034 ✅ hardened

- [ ] **Path (Method B, used):** Subscriptions > Azure subscription 1 > Activity log > Export Activity Logs > + Add diagnostic setting > law-lab-01
- [ ] **Path (Method A, failed):** Data connectors > Azure Activity > Launch Azure Policy Assignment wizard
- [ ] **Path (verify):** Subscription > Activity log > Export Activity Logs (setting activity-to-law-lab-01 exists)
- **What it is:** Subscription control-plane operations (resource create/modify/delete, role assignments, policy changes) streamed to law-lab-01, landing in AzureActivity.
- **Why:** Control-plane monitoring - the record of who did what to the subscription.
- **What we verified (2026-07-25):** Configured via **Method B (manual diagnostic setting)** after **Method A (Azure Policy) failed twice** - "you need to log in" at submission, 0 policy assignments confirmed both times (managed-identity/session token). Method B (categories Administrative + Security -> law-lab-01) succeeded first try. AzureActivity populated (verified). For one subscription, Method B is the appropriate choice, not a fallback - Method A's policy+identity+remediation machinery only earns itself across many subscriptions.

### 3.8 Microsoft Entra ID connector - POS-034 ✅ hardened

- [ ] **Path:** Data connectors > Microsoft Entra ID > Open connector page > select log types > Apply
- [ ] **Path (verify):** Entra ID > Monitoring & health > Diagnostic settings (AzureSentinel_law-lab-01 exists)
- **What it is:** Identity logs - sign-ins, directory audits, and Entra ID Protection risk - streamed to law-lab-01.
- **Why:** The foundation of identity-based detection and hunting.
- **What we verified (2026-07-25):** Enabled Sign-In Logs, Audit Logs, Risky Users, User Risk Events (high-volume types left off - the connector-level cost lever). Apply wrote the diagnostic setting AzureSentinel_law-lab-01. Sign-in ingestion needs P1/P2; the E5 trial's P2 is live - **licensing test passed**, 489 sign-in events captured.
- **Two stores, not two names (corrected 2026-07-26):** **SigninLogs** is a Log Analytics workspace table written by this connector's diagnostic setting, scoped by the log types selected, and billable. **EntraIdSignInEvents** is a Defender XDR lake table written by XDR regardless of this connector, covering every sign-in class, and free. On the unified Defender surface both resolve in one query with very different counts (6 vs 972 on 2026-07-26); in Sentinel > Logs only SigninLogs exists. The original empty SigninLogs was propagation lag (~10-15 min), not a naming mismatch. Diffing one census across both portals is the reusable form of this - see `kql/sentinel/store-partition-diff.kql`.

### 3.9 Unified audit logging - `POS-035` ✅ hardened

- [ ] **Path (portal, could not complete):** Defender > System > Audit > Start recording user and admin activity
- [ ] **Path (used):** Exchange Online PowerShell > `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true`
- [ ] **Path (verify):** `Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled` - **in the EXO endpoint only**
- **What it is:** Tenant-wide recording of user and admin activity into the Microsoft 365 substrate.
- **Why:** Attack simulation reporting depends on it, and nothing else in this project had needed it. The tenant recorded nothing until 2026-07-26.
- **What we verified (2026-07-26):** Read `False` by cmdlet, set `True` by cmdlet, confirmed `True` on a later read. The **portal could not do this**: System > Audit showed two independent faults at once ("trouble figuring out if activity is being recorded" and "Failed to load data") and its enable button produced a Client Error. The page's inability to *determine* state was a separate fault from the state itself.
- **Endpoint trap:** the same cmdlet in Security & Compliance PowerShell returns `False` **even when auditing is on** (Microsoft Learn). Wrong endpoint returns a permanently false value with nothing to distinguish it from a true one.
- **Cost:** none. Audit data lives in the M365 substrate, not `law-lab-01`. Becomes an ingestion cost only if the Office 365 connector is later added to Sentinel.

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


### 3.16 Microsoft Sentinel UEBA - `POS-044` ✅ hardened (enabled 2026-07-28)

- [ ] **Path:** Defender > System > Settings > Microsoft Sentinel > UEBA
- [ ] **Path (verify residency):** Azure > Sentinel > Logs — `kql/sentinel/store-partition-diff.kql`
- [ ] **Path (verify billability):** Azure > Sentinel > Logs — `Usage | where IsBillable == true`
- **State:** Entra ID sync on, Active Directory off, **7 data sources connected (3 carrying data)**, behaviors layer off.
- **The cost shape:** the feature is free; the data it generates is not. `IdentityInfo` is now a **billable** DataType at 0.001416 MB/24h. Total billable volume 0.0437 MB/day against 10 GB/day.
- **Residency ≠ billability.** The store-partition census answers *which store*; `Usage | where IsBillable` answers *what is metered*. `AzureActivity` is workspace-resident **and free** — see the Lab 08 §7 correction.
- **Enabling is three acts** — feature toggle, directory sync, data source connection — and the page reports "enabled" after the first, with `0 sources` and both directories `Sync disabled`.
- **Measured:** initial sync under an hour against Learn's "a few days"; `BehaviorAnalytics` inherits the **source event's** timestamp, so UEBA's own latency is not measurable from `TimeGenerated`.
- **Open:** `BehaviorAnalytics` billability — absent from the billable list, but its only row postdates `Usage`'s reporting lag. *(pending)*


### 3.17 Sentinel analytics rules - `POS-045`, `POS-046` ✅ (Lab 11)

- [ ] **Path:** Defender > Microsoft Sentinel > Configuration > Analytics — three tabs: Active rules, Rule templates, **Anomalies**
- **Baseline before this lab:** `Active rules: 0`. But see divergence row 41 — that count **excludes anomaly rules**, of which **48 were enabled**.
- **Two rules, one technique** (`T1110`): Microsoft's template tuned (`POS-045`, never fired) and `LAB-Bruteforce-Failed-Signins` authored (`POS-046`, fired twice).
- **Measured:** alerts = lookback ÷ frequency. 60 ÷ 5 = **12 alerts and 12 incidents** from one 92-second event; suppression at 1 hour → **1 and 1**.
- **`Anomalies` table:** resolves, **0 rows over 7 days**. Provisioned by UEBA (`POS-044`), never written to.
- **ASIM:** `imAuthentication` does not resolve — parsers are Content Hub content and none is installed (row 40).
- **Activity span, resolved:** `extend timestamp` (Microsoft's template idiom) does nothing; `extend TimeGenerated = StartTime` works — but yields a point, not a range. **And suppression freezes a mid-burst snapshot:** run 4's alert reports 5 of 7 failures, a 29% undercount (row 38, `POS-046`).


### 3.18 Defender for Office 365 threat policies - `POS-047`-`POS-055` (Lab 12)

- [ ] **Path:** Defender > Email & collaboration > Policies & rules > **Threat policies** - Templated policies / Policies / Rules
- **Baseline before this lab:** no custom threat policy of any type, no rules of any type, both presets off, one Safe Attachments policy and one Safe Links policy (both Built-in protection).
- **Built-in protection enabled and inert** (`POS-048`): four surfaces report it healthy; neither control message carries `X-MS-Exchange-AtpMessageProperties`, both scoped messages do. n=2 each side (row 47).
- **`SA-Sales-DynamicDelivery`** (`POS-054`) - Dynamic Delivery, scoped to `sales-lab`, and carrying `Redirect: True` that the wizard warned would not apply, accepted anyway, and stored (row 43).
- **Wizard default action is Off**, not Block (row 44).
- **Precedence is not in the objects** - creating the custom policy wrote no exclusion into Built-in protection; both rules read `Priority: 0` on incomparable scales (row 48).
- **Measured:** 3.249 s and 3.454 s end-to-end with Safe Attachments; the placeholder never appeared, including for a file novel by construction (row 46).
- **Configuration analyzer:** 18 recommendations against the shipped defaults, all `Not started` - 4 anti-spam, 12 anti-phishing, 1 DKIM, 1 Outlook (row 45, `POS-049`, `POS-050`, `POS-052`).
- **Defaults recorded:** anti-phishing impersonation protection inert (`POS-049`), anti-spam junk-not-quarantine at BCL 7 (`POS-050`), anti-malware ZAP and file filter on (`POS-051`), DKIM absent (`POS-052`), `AutoForwardingMode: Automatic` (`POS-053`), Safe Attachments global settings on (`POS-055`).
- **Explorer is eventually consistent** - `Additional actions` read `--` for the second Sales message at first export and `Dynamic delivery-Success` on re-export of the identical query. Nothing marks the row as incomplete (row 50).
- **Withdrawn:** a latency inversion claimed from run 1 and disproved by run 2 - see `labs/12-mdo-threat-policies/README.md` §6.


### 3.19 Explorer investigation and Defender-native remediation - `POS-056`, `POS-057` (Lab 13)

- [ ] **Path:** Defender > Email & collaboration > **Explorer** > All email > *(message)* > Open email entity; and Investigation & response > Actions & submissions > **Action center**
- **The Action Center holds remediations, not investigations** - AIR produced no entry on either tab; a soft delete produced one immediately (row 53). Closes `MOD-53`.
- **Two response paths, separated at every layer** - different confirmation wording, different destination link, Approval ID present on one and absent on the other. Both `Scope: MDO`.
- **Approval ID is an identifier, not a gate** - the remediation landed in History, already `Approved`, `Decided by` its own submitter, `Action source: Manual office action` (row 53).
- **Every action generates the next artifact** - investigating created an alert (`Admin triggered manual investigation of email`, `Category: Probing`, Resolved, no incident); remediating created a second investigation.
- **AIR measured end to end:** 9 s, 4 reputation lookups, 4 entities, `Evidence (0)`, `No threats found`. `File Hash Reputation` alone took 5 s (row 56).
- **Propagation, sharpest instance:** `Log (0)` became `Log (4)` minutes later with no action taken (row 55). See the through-line note below.
- **Soft delete is reversible by the mailbox owner** (`POS-057`, row 59).
- **Global Administrator cannot preview delivered mail** (`POS-056`) - a separate Unified RBAC permission, which makes the single-GA model *insufficient* as well as risky.
- **Withdrawn:** the entity page's empty `Policy` field, initially read as a sixth-surface failure - `CAT:NONE` shows it is correctly empty. See `labs/13-explorer-air-remediation/README.md` §6.


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
| 1 | **G1**: Azure free trial gives $200 credit; services pause at exhaustion; card never auto-charged | ~~Pay-as-you-go, uncapped, no credit~~ (`POS-005`) — **"no credit" WITHDRAWN 2026-08-01, see row 60.** The credit exists on another billing profile; the safety-net half of this row stands | **The safety net does not exist** — that conclusion survives the correction. No spending limit is available. Budgets notify but cannot cap. Deallocation (`POS-016`, itself corrected — row 61) controls compute only | **revision notes only** — original G1 not read back; environment claim corrected by live verification, row 60 |
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
| 13 | (implicit) an Azure VM's name is its hostname | The Azure resource name **LAB-SRV-DEFENDER-01** (19 chars) exceeds the 15-char Windows NetBIOS limit, so the OS hostname and the `Computer` field truncate to **LAB-SRV-DEFENDE** (`POS-033`) | A KQL filter of `Computer == "LAB-SRV-DEFENDER-01"` returns nothing. Match the truncated name or use `startswith`. Silent — the query just returns empty | **live, 2026-07-25** — confirmed in Heartbeat and SecurityEvent data |
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
| 33 | **Microsoft Learn**: enabling UEBA requires *Microsoft Sentinel Contributor* at workspace scope and *Log Analytics Contributor* at resource-group scope — Azure RBAC | The portal's own banner reads **"Only a Global Administrator or a Security Administrator in your Microsoft Entra ID can turn this feature on or off"** — an **Entra** role. The enable succeeded (`POS-044`) | Two different permission models named for the same action. This project asserted, on Learn's basis, that Global Admin alone would not suffice — **that assertion was wrong**, and the portal was right about what the portal enforces | **live, 2026-07-28** — banner read, enable succeeded |
| 34 | **Microsoft Learn**: UEBA initial synchronization *"may take a few days"*; UEBA writes to `BehaviorAnalytics`, `IdentityInfo`, `UserPeerAnalytics`, `UserAccessAnalytics` | Enabled 02:58 UTC; `IdentityInfo` carried data by **03:50 UTC — under an hour**. And only **two of the four tables** appeared: `IdentityInfo` (4 rows) and `BehaviorAnalytics` (1) (`POS-044`) | The duration estimate is presumably written for thousands of identities; for three it is off by ~2 orders of magnitude. The missing two need peer groups and access history a three-identity tenant may be unable to produce — **hypothesis, indistinguishable from latency on one census** | **live, 2026-07-28/29** |
| 35 | **Portal**, *Recommended settings*: "Click *Connect available data sources* to automatically select and connect all eligible data sources" | Seven sources went green; **three carry data**. Two are Entra log types **deliberately declined** in Lab 08 (`POS-034`), one names the **legacy agent** connector where Lab 07 built AMA + DCR ingestion, one needs a running device (`POS-044`) | **Eligible means the connector exists, not that anything flows through it.** Four sources will read `Connected` indefinitely and contribute nothing, and the page offers no way to tell them from the three that work — `POS-011`'s shape, inside the recommended path | **live, 2026-07-28** |
| 36 | **Analytics-rule guide** §2: query scheduling has two settings — how often to run, and how far back to look — described independently | **They are coupled.** A lookback of ≥2 days forces a frequency of ≥1 hour. Discoverable only as a validation error after entering an invalid pair (`POS-045`) | The Microsoft brute-force template ships at 1 day / 7 days and cannot be tuned below **1 hour** without starving its own `avgFailures` baseline, which joins over `ago(7d)`. The wizard states query scope is capped by rule scope, so shortening the lookback silently changes the query's maths | **live, 2026-07-30** |
| 37 | **Rule template detail pane**: `Create incidents from this rule: Disabled` | The **wizard that instantiates that template defaults it to Enabled** — confirmed independently by building a from-scratch rule, which also defaulted Enabled (`POS-045`, `POS-046`) | Same object, two views, opposite values, and nothing indicates which is authoritative. Had the pane been right, the rule would produce alerts that never reach the incident queue — invisible to anyone watching incidents rather than alerts | **live, 2026-07-30** |
| 38 | **Microsoft's own rule template** ends its query with `\| extend timestamp = StartTime` — the apparent convention for telling Sentinel which column is the event time | **That idiom is stale and does nothing.** Alerts continued reporting `First`/`Last activity` 60 minutes apart — the lookback window — for events spanning ~90 seconds. `\| extend TimeGenerated = StartTime` **works**, confirmed across two runs (`POS-046`) | A **39× overstatement** on the field an analyst reads first to judge scope, produced by copying a convention Microsoft still ships. The working fix yields a **point, not a range**: a summarized row has one `TimeGenerated`, so the alert now reports 0 seconds for a 90-second event. Neither value is correct | **live, 2026-07-31**, four runs |
| 39 | **Action center guide** §6: automated investigation runs on alerts and pends actions for approval | **All 13 Sentinel incidents read `Investigation state: Unsupported alert type`**, where Lab 10's MDO incident reads `Queued` (`POS-046`) | Defender's automated investigation does not support Sentinel scheduled-detection alerts. Module 53 established that an alert is not an action; this narrows it — **for Sentinel-authored rules there is no action path at all**, so no AIR, no investigation, no Action Center entry | **live, 2026-07-31** |
| 40 | **ASIM guide** §3: ASIM ships built-in normalized schemas that recognise common event types across platforms "without you writing any mapping syntax" | `imAuthentication` **does not resolve** in this workspace — *Failed to resolve table or column expression*. ASIM parsers are Content Hub **content**, and no solution has ever been installed here | Not a licensing or data gap: the failed sign-ins from Lab 11 are perfectly normalisable, there is simply no function to normalise them with. `POS-011`'s shape again — described as built-in, unreachable until a second step nobody mentions | **live, 2026-07-31** |
| 41 | **UEBA guide** §7: anomaly rule templates are *"enabled by default"*; **and this repository** recorded "Sentinel ships with no detections running" on observing `Active rules: 0` | Both halves need correcting. **48 anomaly rules are enabled**, so the guide is right — and the Active rules count **excludes anomaly rules**, so the repository's inference was wrong. The `Anomalies` table resolves and returns **0 rows over 7 days** | Three surfaces, three answers to "what detection is running": 0, 48, and 0 rows. Only the table says whether anything happened. 48 enabled detections cannot fire in a three-identity tenant with no behavioural baseline — `POS-044` from a second direction | **live, 2026-07-31** |
| 42 | **Guide** §2: Standard and Strict presets are *"assigned to no one until you turn it on"* — implying an off toggle over an existing configuration | `Get-EOPProtectionPolicyRule` and `Get-ATPProtectionPolicyRule` return **nothing** — not `State: Disabled`, no object at all (`POS-047`) | The rule objects are created only when a preset is first enabled in the portal. **Absence and disabled render identically**, and this tenant does it three times: the presets, DKIM (`NoDKIMKeys`, `POS-052`), and Safe Attachments rules pre-lab. Enabling any of them creates the object rather than changing a value | **live, 2026-08-01** |
| 43 | **Wizard**, in text directly above the checkbox: *"Enable redirect only supports the Monitor action"* | The checkbox ticks. The address field activates. Format validation fires, applicability validation does not. Selecting Dynamic Delivery afterwards triggers no re-check. **The Review page renders both settings with green status dots.** Submission succeeds and the backend stores `Redirect: True` beside `Action: DynamicDelivery` (`POS-054`) | Six checkpoints, one written rule, zero enforcement. Confirmed inert — no redirect copy of either test message arrived. A green status dot is an affirmative claim, made here about a setting the product had already explained would not apply. Guide §7 lists redirect as a general option and is separately wrong; Learn scopes it to Monitor | **live, 2026-08-01**, n=2 |
| 44 | **Guide** §7 action table: **Block** is the default Safe Attachments action | The creation wizard pre-selects **Off — "attachments will not be scanned by Safe Attachments"** | Click through accepting defaults and you ship a policy with a name, a scope, an entry in the policy list and `Status: On` that scans nothing. The register's thesis arriving as a shipped product default rather than as anyone's misconfiguration | **live, 2026-08-01** |
| 45 | **Guide** §3: Configuration analyzer compares your ***custom*** policy settings against the recommendations | It returned **18 recommendations against the shipped defaults** — 4 anti-spam, 12 anti-phishing, 1 DKIM, 1 Outlook — in a tenant with no custom policies at all. Learn's scope is any policy less secure than Standard or Strict | A free, dated, Microsoft-generated measurement of how far the tenant sits below Microsoft's own recommendation, available before anything is built. **This repository predicted the guide's version and was wrong with it** | **live, 2026-08-01** |
| 46 | **Guide** §7/§11: sandbox scanning *"can take up to a minute"*; **Learn**: *"typically within 15 minutes"* | `X-MS-Exchange-Transport-EndToEndLatency` — **3.249 s** and **3.454 s** across two runs, the second on a file globally novel by construction (`POS-054`) | Both overstate by one to two orders of magnitude. Consequence for the feature: Dynamic Delivery's placeholder **never appeared**, because detonation completes ahead of the delivery decision and there is nothing to hold back. The user-visible behaviour the guide uses to justify the feature is invisible in normal operation | **live, 2026-08-01**, n=2 |
| 47 | **Portal**: Built-in protection `Status: On`, `Priority: Lowest`; **`Get-ATPBuiltInProtectionRule`**: `State: Enabled`; **`Get-SafeAttachmentPolicy`**: `Action: Block`, `Enable: True`; every scoping and exception field empty, i.e. all recipients, no exclusions | **Neither control message carries `X-MS-Exchange-AtpMessageProperties`.** Both messages to the mailbox covered by the custom policy do. n=2 each side, two hours apart, identical sender and file (`POS-048`) | **The lab's headline.** Not two surfaces disagreeing — four surfaces agreeing and being wrong. An analyst inheriting this tenant would read every configuration surface as saying attachments are protected. The portal note ("enabled only for **paid** Defender for Office 365 tenants"; this tenant is on trial) is a candidate explanation and is **not established** — the advance prediction that the policy was active was falsified | **live, 2026-08-01**, n=2 |
| 48 | **Guide** §9: custom policies of the same type carry a priority, and *"the preset wins"* | Built-in protection's priority is fixed at **Lowest** and a custom policy beats it. After the custom policy was created, Built-in protection's `ExceptIf*` fields stayed **empty** and its `WhenChanged` was unmoved — the service writes **no** exclusion (`POS-054`) | Precedence is evaluated at mail-flow time, not materialised in the objects. **Read both rules cold from an export and both claim every recipient.** Both also read `Priority: 0`, on two scales that are not comparable and neither of which is labelled — where Exchange convention says lower number is higher priority, and Built-in protection is last | **live, 2026-08-01** |
| 49 | **This repository**, ten recorded occurrences: *"Defender renders local, Azure renders UTC"* | Both halves need correcting. `Get-AntiPhishPolicy` returns `WhenChanged 16:30:08` local and `WhenChangedUTC 23:30:08`; **the Defender portal displays 23:30**. `Get-DistributionGroup` returns `WhenCreated 12:17:32` local; **the M365 admin center displays 12:17** | **The Defender portal renders UTC unlabelled and the M365 admin center renders local.** Proven on single objects carrying both forms rather than inferred across two. Defender is also inconsistent with itself — Tenant Allow/Block stamps `(UTC-07:00)` on its columns while the policy panes and Configuration analyzer label nothing. An analyst correlating an incident across the two consoles is reading two clocks with identical formatting, seven hours apart | **live, 2026-08-01** |
| 50 | **Explorer**, the surface an analyst reaches for: `Additional actions` reports what was done to a message | At first export, `Dynamic delivery-Success` on the first Sales message and **`--` on the second** — same policy, same recipient, two hours apart, both carrying the `SA` header. **Re-running the identical export later returned the value on both.** The field was not withheld; it had not been indexed yet | **Explorer is eventually consistent and does not say so.** Nothing in the UI, the export, or the column header distinguishes *no action was taken* from *not yet written* — so the lag produces a **wrong answer**, not a missing one, on the most-trusted surface. Fourth propagation delay recorded in this tenant, after Exchange hydration (12 days, `POS-036`), group membership → transport (~20 min), and threat policy application. The message header, stamped at delivery, is the only immediately authoritative surface. **Lag bounded to under ~1 h at the low end and unmeasured at the high end — export times were not recorded, which is the method error** | **live, 2026-08-01**, resolved |
| 51 | **EXO V3 module** ships `Get-MessageTrace` and `Get-MessageTraceDetail`; both load, bind parameters, and accept pipeline input | Both fail at execution with a deprecation notice dated **2025-09-01** — eleven months prior — and **return empty rather than erroring** | Two subsequent piped commands ran cleanly against nothing, producing no output and no complaint. **A monitoring script built on these reports zero messages rather than reporting a failure.** Same shape as the policy findings one layer down: present, callable, inert. `Get-MessageTraceV2` and `Get-MessageTraceDetailV2` work | **live, 2026-08-01** |
| 52 | **Explorer** renders one `Additional actions` value per message | The UI shows `Dynamic delivery-Succeeded`; the CSV export of the same row shows `Dynamic delivery-Success`. Separately, the UI column reads `Timestamp (UTC -07:00)` and renders local while the export column reads `Email date (UTC)` and renders UTC | One field, one value, two strings — which breaks any programmatic match written against the surface you happened to read. But the timestamp half is a **counterexample to row 49**: Explorer renders two zones from one tool and **labels both**, which the Defender policy panes and Configuration analyzer do not do at all | **live, 2026-08-01** |
| 53 | **Guide** §7: remediation actions *"flow to the Action Center for approval and history"* | **AIR produced no Action Center entry on either tab.** A soft delete against the same message produced one immediately, with Approval ID `6570a3` (`POS-057`). The two paths also differ at the confirmation layer — AIR reports "1 **investigation** actions completed" and links to the investigations page; the remediation reports "1 action(s) completed" and links to the action center | **This closes `MOD-53`.** The Action Center holds **remediations, not investigations** — its columns are Approval ID, Action type, Decision, Decided by, Status, every one about an approval lifecycle. Lab 03's empty Action Center was correctly attributed to *no remediable artifact existed*; here is the independent confirmation from a second product scope. Also: the remediation landed in **History, never Pending**, already `Approved` and `Decided by` its own submitter — **the Approval ID is an identifier, not a gate** | **live, 2026-08-01** |
| 54 | **Submission banner:** *"1 investigation actions completed"* | The second investigation was still `Status: Running` on the investigations page well after its banner claimed completion — 1 m 11 s and counting, against the first investigation's 9 s | The banner reports completion of the **submission**, not of the investigation, and does not say so. An operator reading it as written would conclude the investigation had finished and its verdict was final | **live, 2026-08-01** |
| 55 | **Investigation detail page:** tab counters state quantities — `Log (0)` | The same page read **`Log (4)`** minutes later, with no action taken and no reload prompt. The four entries were reputation checks that had already executed by the time the counter said zero | **The sharpest propagation instance in this repository, and the reason propagation is now a second through-line.** A parenthesised count is not a blank field or a spinner — it is the product stating a quantity, and it was wrong. Fifth measured instance, spanning **12 days** (Exchange hydration, `POS-036`) to **minutes** (here), via group membership (~20 min), threat policy application (< 1 h), and Explorer indexing (row 50). The last two render not as *missing* but as **a confident zero**. **Rule: a zero is a claim about the index, not about the event** — an absence needs a second identical query before it reaches a file. Microsoft knows: the soft-delete confirmation warns "several minutes"; the Explorer export, this counter, and group replication warn nothing | **live, 2026-08-01** |
| 56 | **Investigations grid** column header: `Action count` — 4 | The same four appear as `Entities analyzed (4)` in the investigation graph and `Log (4)` on its tab. `Entities (4)` breaks down as 1 IP address, 1 email, 2 email clusters. **Two different fours that coincide** — four entities examined, four log actions executed | The column named *Action* shows the *entity* count, and neither states what was done. Only the Log tab does: Sender IP investigation (0.15 s), Mail cluster identification (0.34 s), **File Hash Reputation (5 s)**, Sender domain investigation (0.20 s) — four reputation lookups, no remediation, on a 9-second investigation of which one check consumed 55% | **live, 2026-08-01** |
| 57 | **Message Header Analyzer** headline: *"Delivered after 4 seconds"* | The analyzer's own hop table shows creation at 14:00:57 and final hop at 14:01:15 — **18 seconds**. It sums inter-hop delays (0+1+0+3) and silently drops 14 seconds of sender-side queueing | One message now has **four** latency figures: `EndToEndLatency` 3.25 s (Microsoft-side only), analyzer headline 4 s (inter-hop only), message trace `Receive`→`Deliver` 5 s (transport events), analyzer timestamps 18 s (creation to delivery). They differ by nearly **6×** and measure different intervals. This vindicates the withdrawn Lab 12 latency finding from the other direction — three of these were called "independent measurement methods" and are neither independent nor comparable. **The tool's headline number is the one that omits the most** | **live, 2026-08-01** |
| 58 | **Microsoft Message Header Analyzer** parses Exchange Online headers into a readable breakdown | Two `Unknown fields` entries: `DIR:INB` and the entire `ARA:` rule-attribution list — **both emitted by Exchange Online Protection**. In the `Other` section, values appear stripped of their field names entirely | **`SA` sits in `Other` as a bare unlabelled string.** That is `X-MS-Exchange-AtpMessageProperties`, the single field that distinguished the two policy paths across four messages in Lab 12 — and Microsoft's own analyzer renders it as a value with no key. The parse is otherwise correct: SPF/DKIM/DMARC/composite all Pass, SCL 1, BCL 0, matching the manual read exactly | **live, 2026-08-01** |
| 59 | **Guide** §7 and the Take action wizard present Junk / Deleted items / **Soft delete** / Hard delete as adjacent choices, distinguished as *recoverable* versus *permanent* | Soft delete executed (Approval ID `6570a3`, Action Center History, Approved, Completed) and the message was then **restored by the mailbox owner** via Deleted Items → Recover items deleted from this folder → Deletions. Two clicks, standard end-user client, no admin involvement, **no notification to the operator who remediated it** (`POS-057`) | Correct behaviour — soft delete is documented as recoverable and that is its purpose. Neither the wizard nor the guide states **who** can recover. In the case remediation exists for — a compromised or complicit mailbox — the message sits one click from restoration by the account under investigation, and the Action Center still reads `Completed`. Hard delete is the control that closes it, presented as an adjacent radio button with no indication of the difference | **live, 2026-08-01** |
| 60 | **This table, row 1** (and `POS-005` as first written): the environment has *no free credit* | A **$200 sign-up credit exists** — effective 2026-07-14, expiring 2026-08-13, attached to **billing profile A**, which has never carried a charge; all lab spend bills to **profile B** (`POS-058`). Under MCA a credit pays down only its own profile's invoice | The 2026-07-16 check consulted resource cost analysis — a surface structurally unable to see another profile's credit. **Residency ≠ billability had a billing-side sibling: existence ≠ reachability.** Credit exists, is worth $0 to this lab, and expires unspent by recorded decision. G1 was right that the credit exists; wrong that a safety catch comes with it — the spending limit is unavailable on pay-as-you-go pricing, so this is credit **without** the net | **live, 2026-08-01** — self-correction, withdrawal recorded rather than edited away |
| 61 | `POS-016` as first written (and §3.3): deallocation is *"the only mechanism that actually ends spend"* | True for compute only. **Managed disks and public IPs bill while they exist** and kept accruing into August with both VMs deallocated. July invoice: **~$10.84 pre-tax actual vs ~$7.58 tracked** (~43% under) | "Stopped (deallocated)" ends the compute meter and leaves the storage and IP meters running — the stopped state covers less than the word suggests. Same family as Bastion (bills while existing, offers no stopped state at all — the reason the hosts were deleted, not stopped). Deletion, not deallocation, is what ends resource spend | **live, 2026-08-01** — measured by invoice, self-correction |
| 62 | `POS-017` as originally written states the license answer flatly: 1 paid license converts on 2026-08-13 | **Three surfaces report 25 licenses** (trial allocation, Change plan panel, Azure billing inventory) against **one reporting 1 paid license** (M365 admin center renewal field) | Stating only the resolution caused a real misreading — the 25 was briefly raised as a 25-license billing exposure when re-encountered. The renewal field answers "what converts to paid"; the 25 is trial provisioning. The disagreement is the durable fact and now the recorded one | **live, 2026-08-01** — register amended to carry the disagreement |
| 63 | Guide (verified 2026-07-26): Create policy goes straight to template categories | An undocumented modal precedes everything: "What info do you want to protect?" offering two answers — Enterprise applications & devices vs Inline web traffic | The guide's step 1 is the wizard's step 2. The modal also answers an *information* question with two *delivery surfaces* — question and answer set do not match. Inline web traffic is the strongest candidate for the metered pay-as-you-go path | **live, 2026-08-01** |
| 64 | Guide §4: "Select the locations you actually want to protect rather than blanket-enabling everything" | The wizard blanket-enables: seven locations checked by default, all scoped All — including two that cannot function in this tenant (On-prem: prerequisites unmet; Instances: no MDCA) | The default is the opposite of the guidance — same shape as Lab 12's Safe Attachments wizard defaulting Off against enable-it guidance, in the other direction. Two enabled locations were then named unsupported by simulation at the mode step, disclosed only after Locations let them through silently | **live, 2026-08-02** |
| 65 | Guide treats template confidence as a single dial | U.S. Financial Data ships MIXED confidence — Credit Card High, Bank Account and ABA Medium — visible only by opening each SIT row | "The template's confidence" is three tuning decisions under one name. Defensible design (Luhn makes High achievable on cards; bank accounts need keyword proximity) but undocumented and unsignalled in the UI | **live, 2026-08-02** |
| 66 | Guide presents the template as one detection | The Review screen shows the policy compiling into TWO rules: Low volume (the 1–9 SIT conditions) and High volume (the ≥10 threshold toggle) | The SIT instance count (1–9) and the threshold (default 10) are not two dials on one rule but two discrete rules that tile. Explains the plural in "Send alerts if any of the DLP rules match." Rule-level structure is where module 68's priority-evaluation question (P5) will resolve | **live, 2026-08-02** |
| 67 | Admin units step: a scoping convenience | Banner: admin-unit scoping silently removes unsupported locations (Fabric, Copilot) from the next step, with no indication at the Locations step of what disappeared | A choice on screen N invisibly edits screen N+1. Full directory was kept; the trap is recorded untriggered | **live, 2026-08-02** |
| 68 | One location, one name | The Locations step calls it "Instances"; the Policy-mode banner and Review screen call the same location "Microsoft Defender for Cloud Apps" | Two names for one location within one wizard run. Same family as the Priority 0/"Lowest" and picker-label findings — the label is not the identity | **live, 2026-08-02** |
| 69 | Template description: "…including information like credit card, account information, and debit card numbers" | The template's SIT list: Credit Card, U.S. Bank Account, ABA Routing — no debit-card SIT | Description drifts from contents. Small, but it is the surface a selector reads | **live, 2026-08-02** |
| 70 | Published SIT definition (fetched 2026-08-02): U.S. Bank Account Number has a single 75-level pattern — no keyword-free tier | The live Test panel returned a Low-tier result for the same entity | Cloud entity and published definition disagree, or the Test panel renders sub-threshold evidence the XML does not describe. Mechanism deliberately not asserted — recorded as the discrepancy it is | **live, 2026-08-02** |
| 71 | Session working assumption: ABA routing numbers carry a checksum the SIT validates | Microsoft's SIT documentation: ABA Routing Number, `Checksum: No` | The assumption is withdrawn rather than resolved — whether Func_aba_routing validates the real-world check digit is undocumented either way. Test design routed around it with a real published institutional routing number, which passes regardless | **live, 2026-08-02** — assumption withdrawn |
| 72 | Guide §9: a new DLP policy takes 30–60 minutes to activate, up to 24 hours on trial subscriptions | The "New policy created" confirmation page warns of nothing — no activation window, no trial caveat | The surface most likely to precede a premature "it's broken" (the moment the operator goes looking for results) carries no propagation warning. Microsoft's inconsistent-warning pattern, worst-placed instance yet | **live, 2026-08-02** |
| 73 | — (not in source guidance) | The Purview DLP policy list renders LOCAL time: creation at 16:04 PDT wall clock rendered "Aug 2, 2026 4:04 PM" | Third timestamp surface decoded: Defender portal UTC-unlabelled, M365 admin center local, Purview local. Retroactively decodes the pre-seeded policies' Jul 14 9:39 PM provisioning stamp as Pacific evening | **live, 2026-08-02** — measured against wall clock |
| 74 | — (not in source guidance) | One nine-digit routing number matched BOTH ABA Routing and U.S. Bank Account at Medium — three Medium instances from a two-number document | Cross-matching measured under control: overlapping patterns double-count one value. The Phase A pre-policy false positives (Poland Passport / DEA / HKID on a tenant containing neither) are this mechanism unobserved. Refines P-C4: expect 1 ABA / 2 Bank Account in the simulation report | **live, 2026-08-02** |
| 75 | Policy sync status tab: "Your policy was successfully applied and will take effect immediately… fully enforced immediately after the sync is completed" | The policy is in simulation mode and enforces nothing | The sync-status text is mode-blind — enforcement language rendered verbatim on a non-enforcing policy | **live, 2026-08-03** |
| 76 | Overview progress text: "We finished scanning all items on Share Point, One Drive, ThirdPartyApps, OnPremisesScanner" | The adjacent table renders ThirdPartyApps and OnPremisesScanner as **In progress 0%** — and the mode-step banner had declared both unsupported by simulation | One card, two answers; and *not applicable* renders as a scan that never finishes. The CSV renders the same state as `-`, a third rendering | **live, 2026-08-03** |
| 77 | "Scanning in realtime" (Exchange/Teams/Device) implies immediate visibility | Evaluation is real-time (grid stamps = send minute, twice); the report indexes **8–12 min** behind it (absent 07:14, present 07:18 for a 07:06 send) | The confident-zero window, measured at both ends. A read inside the window reports a zero that is a claim about the index, not the event | **live, 2026-08-03** — measured twice |
| 78 | "Restart the simulation" + dialog: "Please confirm if you want to restart the simulation" | Restart is a **destructive rebuild**: at-rest results rebuilt from current state; **real-time history wiped and unrecoverable** (transit events do not replay). 2 matches → 0; the wiped Exchange match's email still exists in the mailbox | The dialog names zero consequences. An operator "refreshing" a simulation silently deletes every real-time match it ever recorded. Post-restart sends do append (pipeline survives; history does not) | **live, 2026-08-03** |
| 79 | One report, one answer | At 09:34 the Items grid showed **1 item** while the same policy's overview export (16:34 GMT) showed **Total matches 0** | Grid indexing and overview aggregation run on different cadences — same policy, same minute, contradictory counts. Fifth distinct rendering of "how many matches exist" | **live, 2026-08-03** |
| 80 | Match details visible to the operator who built the policy | "The role 'Data Classification Content Viewer' is required to view the sensitive info details" — rendered to Global Administrator | Fourth measured GA-insufficiency (mail preview, comm compliance, sensitive-info details; vs Adaptive Protection walking in). GA creates the policy, runs the simulation, sees the match, cannot see the values | **live, 2026-08-03** |
| 81 | — | Purview timestamp conventions, one solution: policy list **local unlabelled** · CSV export **GMT labelled** · Items grid **UTC unlabelled** · IRM alerts filter **UTC labelled** | Four conventions, four surfaces. Decodable only with wall-clock anchors; the labelled ones are the free tells | **live, 2026-08-03** — measured against wall clock |
| 82 | Deleting matched content — evidence outcome undocumented | Delete → match persists (historical record); restart → match gone (rebuild); recycle-bin residency untouched throughout | The DLP evidence lifecycle is surface-dependent: the answer to "what happens to the evidence when the content is deleted" is *which surface, and did anyone restart* | **live, 2026-08-03** |
| 83 | **IRM Policies grid** column `Users in scope` and the policy flyout's `User coverage` both describe the same policy's population | Grid: **0**. Flyout, same policy, same page: *"This policy is covering **all active users** in your org. Great job!"* with the coverage gauge pinned to **High**. Unchanged across two reads 20 h apart (`POS-064`) | **One policy, one screen, two mutually exclusive scope claims** — the sharpest surface disagreement in this repository, and it beats "Healthy ≠ capable" because both numbers are on screen simultaneously. The grid's 0 is the load-bearing one: it persisted 49 h, which makes it structural rather than propagation, and it is the leading explanation for why the trigger never fired. The flyout congratulates the operator for coverage the grid says does not exist | **live, 2026-08-05** |
| 84 | **IRM trigger wizard**, same screen: the DLP policy *"must be configured to generate 'High' severity incident reports"* | The trigger dropdown listed **all five tenant DLP policies with zero mode or severity annotation** — including `Lab14-USFinancial-Simulation`, which runs in simulation with template-default (never-High) incident reports. It was selected, saved, and the policy reported `Healthy` | **Selector accepts, runtime rejects, no feedback anywhere.** The requirement is stated one paragraph from the control that ignores it. Measured over 49 h across three surfaces: the match occurred (`LAB15 TRIGGER TEST.eml`, Aug 3 4:11 PM UTC, in Lab 14's own report) and produced no alert, no notification, no active alert. Four candidate blockers, none distinguished by any surface — the product cannot tell the operator which of its own preconditions failed | **live, 2026-08-05** |
| 85 | **IRM policy indicators** are a finite set with a count | Three surfaces, three taxonomies: the indicator chooser renders **17 categories**; the policy screen renders **12 categories** with different per-category totals; the review page states **"45/126"**. This repository's own count from the chooser is **103** | No two agree, and the review page's denominator matches neither. Same family as the SIT counts (325 in MDCA's picker vs 327 in Purview, twice) — a product cannot state how many of its own primitives exist. `POS-063` records the 45-enabled figure against the 103 denominator and names the disagreement rather than resolving it | **live, 2026-08-03** |
| 86 | **DLP** (Lab 14) confirmed its policy silently — no latency warning at any step | **IRM warns about the same class of delay twice**: on the review page and again on the confirmation, the latter reading *"at least 24 hours for the triggering event to occur **and score user activity**"* | The paired opposite, and the phrasing matters: the delay is on trigger **evaluation**, not merely on alert surfacing. Two Purview solutions provisioned in one window, one warning twice and one not at all, about propagation behaviour that both have. The warning was also **correct and insufficient** — 49 h produced nothing, so the stated floor bounded nothing | **live, 2026-08-05** |
| 87 | **Policy `Status`** is the field an operator reads to know whether a policy is working | Read `Healthy` at creation (08:52 8/3), then **`1 warning`** from 8/4 onward with **no configuration change between**. The warning: *"Physical badging data isn't being uploaded"* — an optional connector never configured and irrelevant to a DLP-triggered policy. The health job is demonstrably live (last-updated stamp moved 08-04 09:08 → 08-05 04:38) | **The health evaluator reports on what it can enumerate, not on what is broken.** Across two days of live passes it never mentioned zero users in scope, never mentioned a trigger structurally unable to fire, and did flag a connector nobody asked for. `Healthy` meant configuration-valid; `1 warning` means a different thing is configuration-invalid. Neither ever meant *capable of firing*. Companion: `Policy alert effectiveness` renders **0%** — a computed metric over an empty set, presented as a definite number | **live, 2026-08-05** |
| 88 | **Role-group propagation** is documented with a one-hour ceiling | Admin added to the Insider Risk Management role group at **07:50** 8/3. The Alerts grid served content by **~09:00** (functional access, ~70 min). The Policies-page banner — *"you aren't assigned to a role group that allows you to view alerts"* — was **still rendering at 08:53** and outlived the condition it warned about past the documented ceiling. Gone by the 8/4 read | **The warning outlived its condition.** Sixth propagation instance in this tenant, and the second where the surface reports a stale state as a current one rather than reporting nothing. Transition never caught — upper bound only, which is the method limit. `POS-061` | **live, 2026-08-04** |
| 89 | **Detection options**, `Select all` on the sequences list | Selecting all enabled **4 of ~21** sequences. The remainder were greyed because their step-indicators (obfuscate, archive, delete, third-party upload, unallowed domain) live in **org-disabled indicator categories** (`POS-063`) | `Select all` means *all selectable*, and nothing on the screen says the set was filtered by a setting made on a different page. An operator who enabled the recommended org indicators and then selected everything available would reasonably believe sequences are fully covered; 17 of 21 are silently off. Configuration coupling across two surfaces with no cross-reference in either direction | **live, 2026-08-03** |
| 90 | **Triggering events** are presented as a flat list of choices | The **exfiltration** trigger activities carry a **pay-as-you-go banner** — metered trigger activities, disclosed in a footnote on the same screen that presents them as peers of the free options | The default trigger path leads into billing, and the disclosure is sized like a footnote rather than like a meter. Same shape as DLP's non-M365 sources (Lab 14) and the Instances location: metered capability presented adjacent to free capability with the distinction carried by small print. Inventory taken at the same time: 9 M365 + 15 non-M365 activities, the latter all MDCA- or connector-gated | **live, 2026-08-03** |
| 91 | **Guide**: the IRM role-group family is **5 groups** | **Seven** exist: Insider Risk Management (17 roles), IRM Admins (5), Analysts (7), Approvers (2), Auditors (2), Investigators (10), Session Approvers (1). The guide omits Approvers and Session Approvers. All seven were empty before this lab | Two of seven missing is a 40% undercount of the permission surface, in a solution whose whole premise is separation of duty between the person who configures and the person who investigates. The omitted pair are both *approval* roles — the ones a real deployment uses to gate access to investigation content | **live, 2026-08-03** |
| 92 | **Policy settings** flyout enumerates the policy's configuration for review | It lists template, user coverage, user scope, content to prioritize, scoring, triggering thresholds, policy indicators, detection options, cumulative exfiltration, boosters, and indicator thresholds — and **never names the triggering event**. `User matches a DLP policy → Lab14-USFinancial-Simulation` appears nowhere | The single most load-bearing element of the configuration — the only thing that can cause this policy to do anything — is absent from its own settings summary. An operator auditing the policy from this pane cannot see what fires it, and the pane gives no indication anything is missing | **live, 2026-08-04** |
| 93 | **Adding a user to a Purview role group** is a Purview-plane operation | Two minutes after the 07:50 role-group add, a Microsoft-operated principal named **`PurviewRoleAssignmentMigrator`** assigned the **Entra directory role** `Purview Workload Content Reader` to the same identity — **outside PIM**, unrequested. Surfaced only by an Entra ID Protection notification email, never by Purview (`POS-065`) | **Second cross-product side-effect provisioning measured here**, structurally identical to Lab 14's DLP policy auto-creating MDCA file policies (Lab 16). An action in one product provisioned privilege in a different permission system, and the only notification came from a third. Note what it did *not* grant: Purview still demands `Data Classification Content Viewer` for sensitive-info details (row 80) — two similarly named content-reader roles, neither implying the other | **live, 2026-08-03** |
| 94 | **Lab 14's DLP policy** runs `In simulation **without notifications**` | Two notification emails arrived from `Office365Alerts@microsoft.com` — Aug 2 11:06 PM UTC and Aug 3 2:29 PM UTC, activity `UnifiedSimulationCompletionNotification`, subject *"A low-severity alert has been triggered"* | Not a product fault — **two notification subsystems behind one word.** The policy setting governs end-user policy tips; these are admin alerts raised by the alert-policy system (Lab 10's territory). The label reads global and is not. Bonus measurement: both emails self-stamp UTC, giving **simulation completion at 2 min** in both runs (16:04 create → 16:06 complete; 07:27 restart → 07:29 complete) — which is what withdrew Lab 16's mirror-creation inference | **live, 2026-08-05** |
| 95 | **Guide 53**: a substantial set of MDCA policies ships enabled | **23 of 26 built-ins carry `[Disabled]`.** The June 15 2025 **dynamic threat detection model** migration disabled the anomaly-policy objects; the page carries the banner. Three survive ACTIVE — all OAuth/threat-intelligence, none behavioural (`POS-066`) | **The largest accumulator correction of this course arc.** The policy list is not a detection inventory: 23 objects that read as configured detections are inert placeholders for a model that runs somewhere this page does not show. Same family as the Sentinel three-surface detection count (row 41) — asking *what is running* of a list that answers *what exists*. The migration took UEBA and left TI (inference from the survivor set, labelled) | **live, 2026-08-04** |
| 96 | **Creating a DLP policy** (Lab 14) is a Purview-plane operation | The MDCA Activity log holds **five events, all of them this**: at Aug 2 **17:52 local**, MIP auto-created **two mirror CAS file policies** — one per compiled DLP rule, High-volume with an alert bell, Low-volume without — **and flipped the file-monitoring toggle**, in a console that had not been opened (`POS-067`) | **First cross-product side-effect provisioning measured here**; `POS-065` is the second, two labs later. An action in one product created objects and changed a setting in another, discoverable only by reading a log nobody was directed to. **Two corrections attach to this row**: an earlier claim that monitoring was ON *since provisioning* was wrong — our own action flipped it; and the reading of 17:52 as ≈ sync completion is **withdrawn**, since the DLP completion alert self-stamps 16:06, leaving 1 h 46 m the inference cannot cover. Mechanism reopened | **live, 2026-08-04**, one correction and one withdrawal |
| 97 | **App connector** status column reads `Connected` | **Zero user telemetry, confirmed on three independent surfaces**: Activity log = 5 admin events; `CloudAppEvents` = 0 rows over 7 days; connector `Last activity` = `-`. Unified audit verified **ON**, eliminating the leading suspect with no replacement found (`POS-068`) | `Connected` describes a configuration relationship, not a data flow, and the page offers nothing that distinguishes them — the fifth member of the status-label family after `Healthy`, `Available`, `Completed`, and `Enabled`. Three-surface agreement is why this is recorded as **genuine no-flow** rather than a rendering fault, and why the obvious cause being ruled out is recorded rather than a replacement being guessed. This is also the strongest available explanation for row 106 | **live, 2026-08-05** |
| 98 | **File-policy wizard** presents an empty filter set to be built up | Two filters arrive **pre-seeded**: `Access level = Public/External` and `Last modified after 08/04 4:18 AM`. Both were removed for this build (`POS-069`) | **The default scope excludes private files.** An operator who accepts the wizard as presented builds a policy structurally blind to internal-only content — the exact content a data-loss control exists to find — and nothing on the screen frames the pre-seeded filters as a scope decision. Same shape as Lab 14's blanket-enabled locations in the opposite direction: there the default was too broad, here too narrow, and in both cases the default is the thing the guidance warns against | **live, 2026-08-04** |
| 99 | **Sensitive information types** are a single tenant-wide catalogue | MDCA's DCS picker offers **325**. Purview reported **327**, twice, on separate reads | Two products, one engine family, one catalogue, two counts. Unresolved and recorded as such. Joins the IRM indicator taxonomies (row 85) as the second instance of a product being unable to state how many of its own primitives exist | **live, 2026-08-04** |
| 100 | **Policy list** renders the tenant's policies | The unfiltered list showed **27 policies with one MIP mirror**; the `Category: DLP` filtered view showed **both mirrors**. Same page, same moment, different census | **Filtered views are authoritative here and the unfiltered list is not** — pagination mis-rendered the count, which means the surface an operator reaches for first is the one that lies. Caught only because the mirror pair was already known from the Activity log; without that prior, the 27 would have been recorded as fact | **live, 2026-08-04** |
| 101 | **Defender portal renders UTC unlabelled** (row 49, ten occurrences) | The **MDCA Activity log renders LOCAL**, unlabelled — decoded by impossibility, since a UTC reading would place the mirror creation *before* the policy that caused it existed | A counterexample from inside the same portal. Row 49 corrected *"Defender local, Azure UTC"* to *"Defender UTC"*; this corrects that in turn to **"Defender UTC except MDCA"**. Three conventions now live under one portal shell, and the only reliable decode was a causality violation rather than any label | **live, 2026-08-04** |
| 102 | **A page** uses one timestamp convention | The **Audit page** labels its search inputs `(UTC)` and its results column `Creation time (UTC-07:00)` — **both conventions on one page, both correctly labelled** | The counter-example that makes rows 49/52/81/101 a criticism rather than a complaint: labelling both is possible, costs nothing, and one Microsoft team does it. The problem elsewhere is not difficulty | **live, 2026-08-04** |
| 103 | **Enforcement and its alerting** are configured together | `Enforce app access` **UNCHECKED**; `Generate alert for blocked app access` **ON at Informational** (`POS-070`) | The reverse of enabled-but-inert: the action is disabled and the notification for it is armed. An alert that cannot fire will read healthy indefinitely. It also breaks an otherwise coherent asymmetry — data-plane visibility on by default, endpoint and third-party integration off, enforcement off — permissive about seeing, conservative about acting, except here | **live, 2026-08-04** |
| 104 | **Lab 14** recorded a Jan 6 2027 retirement banner on the DLP Instances location | The MDCA Policies page carries **the same date, to the day**: *"File policies in Microsoft Defender for Cloud Apps will be retired on January 6, 2027"* — with the **`Migrate (Coming Soon)` button greyed out** | Cross-confirmation from a second product that the two retirements are one event. The greyed button is the finding: Microsoft names the migration path an operator must take, on a feature retiring in five months, and has not shipped it. The whole of Lab 16 is therefore built on a surface with a stated end date and no exit | **live, 2026-08-05** |
| 105 | **MIP mirror policies** were created by the DLP policy and compile its rules | Source policy `Lab14-USFinancial-Simulation`: **2 matches**. Both mirrors, `ACTIVE`, severities set, one carrying an alert bell: **0 matches** each, at both reads (`POS-067`) | Objects that exist, list as active, and register nothing their parent registers. This is the literal form of the repository's through-line, and it is worse than an inert policy someone configured: **nobody configured these**, so nobody has a reason to check them. An operator auditing MDCA sees two DLP-category policies covering their financial data and no indication that they are hollow | **live, 2026-08-05** |
| 106 | **Purview DCS and MDCA DCS** are the same classification engine, offered the same three SITs, pointed at the same file | Same 243 bytes, same name, same OneDrive path. **Purview**: matched within minutes — U.S. Bank Account 2 Medium / 2 Low, ABA Routing 1 Medium / 1 Low. **MDCA**, advanced settings untouched: **0 at +3 h 30 m and 0 at +27 h** (`POS-069`) | Recorded as **divergence with mechanism open**, not as a calibration result — a zero cannot be resolved into *scanned and below threshold* versus *never scanned*, and row 97's silent connector makes the second live. The operator-facing fact survives either reading: **content Purview flags at Medium is invisible to a default MDCA file policy at 27 hours.** Two-read rule satisfied; no published SLA exists to bound the wait | **live, 2026-08-05** |
| 107 | **Policy filters** include a `Matched policies` filter, per older material | The filter is gone, replaced by a tombstone: *"Matched policies filter is no longer available"* | A retired control that still announces itself where it used to be. Minor, and worth recording as the counterpart to row 104's unshipped replacement — one surface tells you what left, the other tells you what is coming and does not arrive | **live, 2026-08-04** |
| 108 | **Wizard feedback box** collects optional input at the end of policy creation | *"OK to contact me"* arrives **pre-checked**, with the admin UPN **pre-filled** | Opt-out consent on a creation wizard, in a security product, on the same screen as the Create button. It sits against the grain of the rest of this surface, where the defaults are conservative about acting (`POS-070`) — the consent default is the one permissive setting in the wizard. Recorded as observed; no PII left the tenant, and the UPN is display-only under `SANITIZATION.md` | **live, 2026-08-04** |
| 109 | **Classification** is one taxonomy — the guide and the picker present *Informational, expected activity → Security testing* | One field, **two vocabularies, two surfaces each**: the picker and the Activities audit log say `Informational, expected activity`; the incident header and the queue CSV say **`Benign Positive`** — a term the selection UI never shows. The header and the audit entry display both values on the same screen simultaneously (`POS-071`) | The UI-label-vs-schema-value pattern landing on the incident queue: an analyst told to classify as "Informational, expected activity" who then filters or reports on classification finds no such value — it is stored as the legacy/API term. Determination (`Security testing`) is consistent everywhere; only the classification group translates | **live, 2026-08-06** |
| 110 | An empty field has one representation | Four renderings of "nothing here yet" across adjacent fields: queue CSV `Not set`, classification audit entry `"Not Set"`, determination audit entry `"Not available"`, alert-export Investigation state **blank**; the comment's Activity status is also blank where every other audit row says `Completed` | Trivial individually; collectively, no two surfaces of this product agree on how to spell an empty value — which matters the moment anyone parses an export | **live, 2026-08-06** |
| 111 | **Guide §5**: Manage incident holds seven fields — name, severity, tags, assignment, status, *comments*, classification | The pane holds **six controls**; Comments live on the **Activities tab** (`Add comment`), a tab the guide does not mention. The classification picker is one hierarchical control that writes **two** audited fields (Classification + Determination) | The seventh field is not missing — it is elsewhere, on the incident's own audit-log surface. Six pane controls, eight audited write targets (7 fields + comment), one guide claim off by one in each direction | **live, 2026-08-05** |
| 112 | **Last update time** reflects activity on the incident | A managed-field write advances it (17:07, then 17:24 on resolve); a **comment does not** — the header still read 17:07 on the same screen displaying the 17:19 comment | An incident can accumulate investigation notes indefinitely while its queue-visible freshness stays frozen. Sorting the queue by last-update to find recently-worked incidents misses comment activity entirely | **live, 2026-08-05** |
| 113 | The **Activities tab** (undocumented in the guide) is presumed a minor log | It is the incident's full audit trail: one entry per correlated alert (`Automated`, `Correlations`), **one entry per managed field per save** with before/after values (`Manual`, `Incident Management`, performer UPN), comments as their own `Comment` type. One Save produced seven discrete field entries. Badge and grid update independently — the comment was counted by the badge before the grid rendered it; one Refresh reconciled | The per-field decomposition with before/after values is the accountability story §5 gestures at, living on the tab the guide skips. The badge/grid lag cost one withdrawn hypothesis (a filter was suspected; the grid was merely stale) — the two-read rule caught it before it reached a file | **live, 2026-08-05** |
| 114 | A first-run view shows the data | **Pre-seeded filters, instances five through seven**: the incident Alerts tab defaults to `Status: New, In progress` (exported 2 of 3 alerts while the badge said 3); the analyst's first-ever queue view opened pre-narrowed to `Priority score: 15-100` (hiding 15 of 20 visible incidents); the Azure Sentinel Incidents blade defaults to `Last 24 hours` + a 2-value status filter and rendered "No incidents were found" over 17 real incidents | The standing rule extends: clear the chips before trusting a zero — **and before trusting an export**, because exports honor the on-screen filter silently. Corollary recorded as process: every queue export now gets its filter-chip state captured with it, because a morning export's missing rows (IDs 20–22, all Resolved) could not be retroactively attributed to a chip nobody recorded | **live, 2026-08-06** |
| 115 | **Active alerts** is one number | Three surfaces, three serializations of the same field: incident header renders the ratio `2/3`; the queue CSV exports the **total** (`3`) under the "Active alerts" header; the Assets-tab CSV exports the **ratio as a literal string** (`"2 / 3"`) | No stable export semantics — each surface serializes its own way. The mechanism behind the ratio closed en route: alert 3 was AIR-resolved, so 2-active-of-3-total (`POS-071`) | **live, 2026-08-05** |
| 116 | **Exposure level** for one device reads one value | Same Assets tab, same moment: UI **Medium** (warning triangle), CSV export **Low** — reproduced on a second read after a status change and a refresh. Risk level agreed across both surfaces on both reads; only Exposure split | A clean same-surface UI-vs-export divergence, field-specific (not a stale-export smell, since the adjacent field agrees). Which surface carries the truth is not determinable from here; mechanism open | **live, 2026-08-05** |
| 117 | **Guide §4**: an empty Investigations tab "reflects your configuration, not the incident's severity" | The tab enumerates only investigations that **ran** (incident 1: the one AIR run, `No threats found`, 12m34s). Alerts with no investigation have no representation at all — and *why* one did not run (`Unsupported alert type` on all 17 Sentinel incidents, per the queue) is stated nowhere on the tab | The truer statement spans both incident types: the surface reports what it can enumerate, not what is absent or why — the IRM-health-evaluator shape on a new surface. The queue's `2 investigation states` against the tab's one investigation object remains an open denominator question | **live, 2026-08-05** |
| 118 | Correlation runs continuously; an alert waits to be linked | The incident **is** its first correlation event (creation 16:02:50.730Z, first Alert-link activity .753Z — 23 ms). The XDR RunScript analytic **generated** its alert 7 h 37 m after the activity it describes — and correlated it in the same second — 5 m 26 s after fresh telemetry from the second test run arrived | The withdrawn version of this row claimed a 7 h 37 m *correlation* lag; the Investigation flyout's `Generated on` timestamp killed it — the alert did not exist to be orphaned. What survives, labeled inference: XDR-layer detection latency, with new activity plausibly triggering evaluation of the morning's event. Seed selection also noted: the Medium alert seeded the incident though the Informational alert's activity was first | **live, 2026-08-05** |
| 119 | Automation's conclusions write back into the fields other surfaces read | AIR resolved an alert while leaving **Determination `Not Set`**, taking **ownership** (`Assigned to: API-Automated Investigation and Response`), and leaving the resolved alert's evidence **Remediation status blank** while never-examined entities read `Active`. The three auto-resolved MDO incidents (20–22) likewise closed with Classification/Determination `Not set`; ID 20 is `Resolved` with Investigation state still `Running` | Automation closes without verdicts — the field §5 says feeds detection tuning is exactly the one it leaves empty — and the evidence grid reads as the inverse of the truth: unexamined items look like open work, examined-and-cleared items look like nothing | **live, 2026-08-06** |
| 120 | Status propagates between incident and alert layers symmetrically | **Downward propagates**: resolving incident 1 zeroed its member alerts (2/3 → 0/3); marking ID 19 In Progress flipped its alert to `In progress`. **Upward does not**: AIR resolving incident 1's RunScript alert on Jul 19 left the incident Active/Unassigned/Unclassified for 18 days | Asymmetric by direction, observed in both states on both incident types. Partial automated remediation is invisible at queue level | **live, 2026-08-06** |
| 121 | An assignment picker offers principals that can own work | Both portals' owner/assignee pickers enumerate the **raw directory**: users, distribution lists (`sales-lab`, Lab 12's DL), security groups (`SOC Device Admins`), and tenant-wide groups, in the same list as assignable users | An accountability field whose picker does not distinguish principals that can act from ones that cannot. Whether a DL is *accepted* as assignee was deliberately not tested — no junk state written | **live, 2026-08-05** |
| 122 | Granting a role is one action with one result | The full observed arc for `POS-072`/`POS-074`: the RG-scope IAM wizard carries an **Assignment type** tab the workspace-scope wizard lacks, and it silently produced **Eligible time-bound (1 year)** where the plan assumed Active permanent; the wizard summary did not surface the state — the **IAM Role assignments grid did**. Activation then forced **MFA registration** on a method-less account (`POS-073`), granted the role for a bounded window, and on expiry every surface retracted (queue 22 → 5, nav rail collapsed, the Sentinel service page rendering *"Don't have a subscription?"* to an identity whose role had merely expired). Post-activation, the unified portal's **read path** arrived in ~2 min (queue 5 → 22, full nav) while the **write path** refused at T+17 min — *"You're missing permissions to manage this incident"*, on Sentinel and MDO incidents alike — and worked by T+12 h on a fresh token, where the same identity then performed the §1 write it was refused. The activation-duration slider opened at the 0.5 h floor on first use and at 8 h on second; the Defender portal needed a manual sign-out/in on day two where PIM's auto-refresh sufficed on day one; the analyst's export rendered the workspace as a **GUID** where the admin's rendered its name; the nav rail's post-activation chrome grew a `+ Create` control on day two that day one's activation had not shown | The permissions error attributed to the *identity* what was only true of the *cache* — the wizard-copy-is-not-a-state-surface family, now including error messages. The original write-path-divergence claim is **withdrawn** on its second read; what replaces it is bounded and operational: after role activation, a refused write with a permissions error may be stale state — re-authenticate and re-read before believing it, because in production that message sends an analyst to an admin to fix permissions that were never broken. The expiry side is the design working: the forget-to-revoke failure mode is structurally deleted, and PIM's per-elevation MFA enforced stronger auth than the tenant baseline ever configured | **live, 2026-08-06** |
| 123 | **Guide (mod 78/79)** describes one kind of automation rule | The Automation rules tab splits **Enhanced** and **Standard**, and they are different engines: **Enhanced** offers exactly one trigger (`When alert is created` — the only option in its wizard) and is tenant-level/multi-workspace/generated-playbook territory; **Standard** carries all three of the guide's triggers, binds to one workspace, and is the world the guide actually describes. Neither is named in the source material | The guide predates or ignores the bifurcation. The alert trigger exists in *both* kinds, so "which kind runs my alert automation" is a real operator question the guide cannot ask. The tab's own blurb calls Standard "limited conditions and actions" — yet Standard's condition picker offers ~40 entity properties down to process command line and registry key (row 125) | **live, 2026-08-06** |
| 124 | The Automation rules list carries a pre-seeded trigger filter (recorded earlier as a filter to clear) | On the **Enhanced** view the chip reads `Trigger: When alert is created` over an empty list — but that is the *only value an Enhanced rule can have*. The chip is a mandatory property rendered as an optional filter. The **Standard** view's chip reads `Trigger: 3 selected` (all three) plus `Workspace: law-lab-01 (Primary)` | The pre-seeded-filter pattern's edge case: not a filter narrowing a view but a tautology wearing a filter's clothes. Clearing it changes nothing because there is nothing else to show | **live, 2026-08-06** |
| 125 | One field, one default | **Trigger default across four surfaces:** Enhanced list (alert-only chip) · Enhanced wizard (alert-only, sole option) · Standard standalone wizard (**no default**, forced choice) · analytics-rule entry-point wizard (**`When incident is created`** pre-selected). The pre-check's observed incident-created default belonged only to the fourth | Four surfaces, four behaviours for one field. The opinionated entry point (analytics-rule path, which also *locks* the condition) is the one that pre-picks the trigger; the neutral standalone wizards force an explicit choice. Coherent once seen, invisible from any single surface | **live, 2026-08-06** |
| 126 | The two creation surfaces build the same rule | **Automation page:** condition builder arrives **empty and free** — an `IF / Group operator: AND` tree with `+ Condition (And)` / `+ Condition group (Or)`, and a Value picker that **enumerated three analytic rules** (`Advanced Multistage Attack Detection` = Fusion, `Brute force attack against Azure Portal`, `LAB-Bruteforce-Failed-Signins`) with an `All` wildcard; operator limited to `Contains` / `Does not contain`. **Analytics-rule path:** condition arrives **pre-populated and LOCKED** — `Analytic rule name / Contains / Current rule`, operator and value both greyed, a late-bound token that survives renames, with free And/Or composition still available beneath it | The lab's thesis in one comparison: same feature, two doors, two binding models — enumerated-at-creation (chosen rule identities) vs resolved-at-runtime (rename-safe token). The Fusion entry is a bonus: the condition picker shows a detection the Analytics management list does not (row-41 family — three surfaces, three answers for "how many detections run here") | **live, 2026-08-06** |
| 127 | An automation rule's condition is a scope you set | The saved Rule A row renders `Custom detection rule name: Any` though only `Analytic rule name` was conditioned — the unconstrained dimension serializes as a **wildcard**, not an absence | Cosmetic here (the analytic-name condition gates everything), but it is how one Standard rule spans both detection systems: every dimension you do not constrain reads `Any`, and the analytics-rule's Automated-response tab lists a rule as a match by **evaluating conditions against the rule**, so Rule A (name-matched) and Rule B (`Current rule`) both appear there despite different binding | **live, 2026-08-06** |
| 128 | `Suppression` for `LAB-Bruteforce-Failed-Signins` has one value | Three surfaces, and the unified one disagrees: the **Azure analytics pane** and the **analytics-rule wizard Review** both state `Stop for 1 hour if alert is triggered`; the **Lab 17 unified Detection Rules pane** rendered Suppression **blank** for the same rule | Two-against-one, same rule, same field. The unified thin view omits a field the authoring surfaces render — the operator reading suppression there would conclude the rule has none. Confirmed across both labs' reads | **live, 2026-08-06** |
| 129 | Alert grouping / incident correlation is one setting | Three vocabularies: the **unified pane** said `Incident correlation: Disabled`; the **Azure pane** showed `Alert grouping: Disabled`; the **wizard Review** distinguishes **two** fields — `Alert grouping: Disabled` *and* `Incident correlation: Tenant default` | The classification-field pattern (row 109) recurring on rule configuration: adjacent-but-distinct settings collapsed differently per surface, so "is correlation on?" gets a different-shaped answer depending on where you read it | **live, 2026-08-06** |
| 130 | Ordered automation rules execute in sequence | Incident 23's audit log, millisecond resolution: alert correlated `18:12:16.543Z`; **Rule A** (Order 1) tag `18:12:25.140Z`; **Rule B** (Order 2) assign `18:12:27.983Z` — strict lowest-order-first, ~2 s apart, both `Automated`, both performer `Automation rule-<name>`. Then at `18:12:27.986Z`, 3 ms after its own assignment, **Rule B logged a second `Tags changed to auto-tagged-ruleA` under its own identity** — though Rule B has no tag action | Ordering, serial spacing, and per-rule attribution all confirmed against the guide. The anomaly is the finding: the likeliest mechanism is a second-in-order rule re-committing the incident's full managed-state post-image (by then carrying Rule A's tag), recorded under B. The tag is idempotent, so the queue, header, and chip all read one clean tag — the duplicate write exists **only** at millisecond resolution in the audit log. Outcome correct, record shows work that did not happen, visible only where no one looks (`POS-076`) | **live, 2026-08-06** |
| 131 | `Priority score` tracks the detection | Incident 23 scored **1**; the eighteen historical `LAB-Bruteforce-Failed-Signins` incidents all scored **3**; incident 1 scored **72** and held 72 through resolution as benign (row from Lab 17). Same rule, same account, three scores | The automation rules touched only tags and owner, so something independent shifted the score between 7/31 and today. Mechanism unchased across two labs now; recorded as an open oddity, not a claim | **live, 2026-08-06** |
| 132 | An extension dialog stating "30 days" adds 30 days | **Extend trial end date** on Microsoft 365 E5, clicked 2026-08-06. Dialog verbatim: extendable **once, for 30 days**. Resulting Expiration date **2026-09-14** — **32 days** after the previous 2026-08-13 expiry, and not 30 days from the extension date either (that would be 2026-09-05) | Five of six elements of prediction P77-1 held (one extension, once only, no payment method, no duration choice, allocation still 25). The arithmetic did not. The anchor the +30 is measured from is **not identified and not asserted** — what is recorded is a dialog promising 30 and a field moving 32. Two extra days in the lab's favour, but a number that cannot be derived from the dialog is a number that cannot be planned against (`POS-077`) | **live, 2026-08-06** |
| 133 | Fields on one panel describe one subscription's state | Same panel, post-extension: **Expiration date** moved 8/13→**9/14** and **Recurring billing** moved 8/14→**9/15**, both by exactly 32 days with the +1 offset preserved. **Next invoice available did not move at all** — still **8/15/2026**, now thirty days *before* the paid subscription it invoices for begins | The two that moved are a **derived pair**, not independent values — useful negative result for row 134. The third is stale with **no indication that it is stale**, sitting alongside two correct fields on one screen. Also confirms the write is asynchronous: "request accepted and pending processing", and nothing moved until a refresh. Receipt is not effect (`POS-077`) | **live, 2026-08-06** |
| 134 | A trial has an end date | Two trials expiring on one date produced **four dates across five surfaces**, all inside `admin.microsoft.com`, all pre-extension on 2026-08-06: **8/12** (admin's Licences and apps banner), **8/13** (O365 product page ×4, Your products ×2, and arithmetically — the dialog states the M365 E5 was created 7/14, +30 = 8/13), **8/14** (both products' Recurring billing lines and the Renew or cancel panel), **8/15** (Next invoice available) | Three of the four describe genuinely different events — expiry, conversion, invoice — that a reader collapses into "when does the trial end". **This register collapsed two of them for three weeks**: POS-017 recorded the Recurring billing field's *transition day* as the O365 expiry date, and O365 does not expire on the 14th. The 8/12 banner is unexplained, appears on one surface, and was read once; recorded unresolved rather than reconciled (`POS-078`) | **live, 2026-08-06** |
| 135 | The Licences page inventories the tenant's licences | Three surfaces, three different inventories of four SKUs: **Active users** lists M365 E5, **Power Automate Free**, O365 E5. **Your products** lists M365 E5, **Entra ID Free**, O365 E5. **Billing → Licences** lists two. No surface shows all four; no two agree | Power Automate Free appears only where licences are assigned to *people*; Entra ID Free only where products are *billed*; the page whose stated job is licence inventory shows the fewest. Two hypotheses withdrawn getting here — the `+2` filter chip was called a pre-seeded filter (**Reset all** changed nothing; the chip is the default inclusive view) and Billing → Licences was predicted to surface the SKU because its own filter reads `Account type: Organization, Self-service`. The two-read rule decided the direction: the SKU read **checked**, 9999/10000 seats, so billing is omitting a real assignment rather than the grid being stale (`POS-079`, `POS-080`) | **live, 2026-08-06** |
| 136 | **Guide (mod 80)**: attach the playbook to an automation rule; if it lacks permission it will not appear in the dropdown | The `Run Logic Apps playbook` dropdown **offered** the playbook — directly above static text reading *"If a playbook appears unavailable, it means Microsoft Sentinel does not have explicit permissions to run it."* Creating the rule then failed: ARM `BadRequest`, *"Missing required permissions for Microsoft Sentinel on the playbook resource"*. Granting `Microsoft Sentinel Automation Contributor` to the `Azure Security Insights` service principal and resubmitting the **identical** form succeeded | **Two checks in one blade, disagreeing**: the dropdown filters on trigger type, the create path validates authorization. The operator sees an available playbook and an explanation of unavailability side by side, and neither is the check that decides. Sentinel validates the launch permission at **authoring** time, not run time — so the predicted failure mode (rule fires, playbook silently never runs) cannot occur here. Withheld → refused; granted → created; nothing else changed (`POS-082`) | **live, 2026-08-07** |
| 137 | `Manage playbook permissions` on the rule form grants the missing permission; a failed operation leaves a record | It is a **documentation link** — opens learn.microsoft.com. No grant is reachable from the rule form. And the failure was nearly unrecoverable: the toast auto-dismissed, and Defender's bell → Notifications retained nothing (*"New notifications from the current session will appear here"*). The only record was Azure → Activity log, operation **`Update Automation Rules`** (not "Create"), **JSON** tab | The remedy-shaped control is a link, and the diagnosis lives in a different portal under a verb that does not match the action attempted. The Activity log **Summary** tab names no cause; only the JSON body carries the ARM error. An operator who dismissed the toast and looked where the error appeared has no record that it happened | **live, 2026-08-07** |
| 138 | The designer canvas shows errors, and authorizing a connection resolves them | Authorizing cleared the card error, emptied the Flow Checker and dropped the Connections red dot **without persisting anything** — the only tell that a save was still required was `Save` un-greying. Separately, the one deployment error sat two levels down inside `For each` → `Condition` → True branch, invisible on the collapsed canvas | Two failure modes of the same surface. An earlier claim that "the guide is wrong, the canvas is clean" was **withdrawn** — the canvas was collapsed, not clean. Clearing an error indicator is not the same event as writing the fix, and nothing on the blade distinguishes them | **live, 2026-08-07** |
| 139 | A deployed playbook has a `Workflow URL` | Reads `--` on Overview. Read three times: before the grants, after all five, and after a completed run. Code view gives the mechanism — the trigger is `ApiConnectionWebhook` with `"callback_url": "@{listCallbackUrl()}"`, registered **through the Sentinel API connection** rather than exposed as a property of the workflow | Structural and permanent, not propagation lag. An item carried across two sessions as "still outstanding" resolves as *never coming* — the distinction matters because one is worth waiting for and the other is not. The SAS-signed callback does exist; it is two clicks away in Trigger history under a read-scoped link, which retires an earlier claim that it could not be reached from the portal | **live, 2026-08-08** |
| 140 | Trigger history records the trigger firing | Contains one row dated two days before any incident: **`Fired: False`, `Status: Succeeded`**, duration ~1 s. That is the webhook **subscription**, logged as a trigger evaluation | `Succeeded` here means "the registration took", not "the playbook ran" — the field rendered first answers a different question than the one an operator scanning for green is asking. Trigger history and Run history are **independent stores**: run history read `No runs` while this row had existed for two days. It is also the surface that separates "Sentinel never called" from "the run failed" | **live, 2026-08-08** |
| 141 | Run history is a surface | Three surfaces for one run. Overview → `Run history` tab: blank grid when empty, columns Identifier/Status/Start time (**Local Time**)/Duration/Static Results, `Resubmit` + `Add filter`. Development Tools → `Run history` blade: **`No runs`** when empty, columns **Status/Start time**(unlabelled)/Identifier/…, fixed filter row, `Refresh`. The run monitor: **no Identifier column at all** | The empty-state divergence is the finding: one surface asserts the negative, the other renders nothing and leaves it to be inferred — indistinguishable from a grid that has not loaded. The timezone label extends the per-surface timezone throughline (rows 81, 101) to a third product: same portal, same resource, one surface states the rendering basis and the other does not | **live, 2026-08-08** |
| 142 | The designer canvas shows the workflow | Overview → Essentials reads **`Definition: 1 trigger, 11 actions`**. The canvas renders **4** collapsed cards. Counting the definition: 4 top-level + 3 in `For each` + 3 in the true branch + 1 in `else` = 11 | The numeric surface was honest about what the visual surface concealed, on the *previous blade*. Row 138's collapsed-container error was discoverable from a field an operator had already walked past. Same finding as row 138 approached from the opposite direction | **live, 2026-08-08** |
| 143 | The playbook generates a temporary password per account it resets | `Initialize variable` and `Set variable - password` are **siblings** of `For each`, not children, and `runAfter` chains them `Initialize → Set → Entities - Get Accounts → For each`. The password is generated **two actions before** the playbook retrieves the incident's entities. Confirmed statically in code view and at runtime in the monitor | Every account entity on one incident receives the **same** credential, and the design cannot do otherwise without moving the action. **Latent, not exercised**: this incident carried one account entity (`For each` read `1 of 1`), so the run does not demonstrate the failure — only the structure that permits it. A multi-account incident is what would surface it | **live, 2026-08-08** |
| 144 | `Condition - is manager available` tests whether the user has a manager | It tests `@outputs('HTTP - get manager')['statusCode'] = 200`, and its `runAfter` accepts **`Succeeded` *and* `Failed`** — so a failed HTTP action does not halt the branch, it routes it. The two branches write different comments: the true branch names the manager; the **`else` branch writes the plaintext temporary password into the Sentinel incident comment**. Either way the run reports `Succeeded` | **The degraded path is the leaky path.** Any non-200 — 403, 404, 429, propagation lag — publishes a live credential to a surface readable by any Sentinel Reader and persisting independently of run history's retention. And the template's success test is disproved by its own sibling: `HTTP - reset a password` returned **204 No Content**. Graph success is not one number, and the workflow hardcodes one. Not exercised on this run (200, true branch, `False` **Skipped** / `ActionBranchingCondition`) — structurally present, one transient fault away (`POS-084`) | **live, 2026-08-08** |
| 145 | `Secure inputs` / `Secure outputs` are Off, so the protection was disabled | There is no `runtimeConfiguration` block on the action at all — the property **does not exist until set**. The designer renders a toggle for something absent. Runtime confirms the consequence: the temporary password rendered in **plaintext** in run-history Inputs on both the reset and the mail action | Nobody disabled the protection; nobody enabled it. Combined with `Workflow Type: Stateful` (which is what persists every action's inputs and outputs), two defaults jointly produce the exposure and neither was a decision. **The credential is not the only secret logged**: `HTTP - get manager` carries no `$select`, so Graph returned the full user object — display name, mail, and the account holder's **business phone number** — persisted for the same 90 days to satisfy a workflow that reads one field (`POS-084`) | **live, 2026-08-08** |
| 146 | The incident audit trail attributes automated actions to automation | Incident 24's Activities: the three automation rules read `Trigger: Automated`, `Activity status: Completed`. The playbook's comment — the only action that changed a credential — reads **`Trigger: Manual`**, performer `Playbook-Reset-Microsoft-Entra-ID-User-Password---Incident-Trigger`, with `Activity status` and `Policy status` **empty** | An operator auditing "what did automation do to this incident" and filtering on `Trigger = Automated` **loses exactly the row that mattered**. The three cosmetic changes are attributed correctly; the consequential one is misfiled and carries no completion status. `Performed by` is also a name this object has nowhere else — a ninth vocabulary for one thing | **live, 2026-08-08** |
| 147 | A playbook's notification is sent by the automation | The delegated Office 365 connection is authorized as `admin`, so the mail arrived **From `admin` To `admin`** — the recipient is the apparent sender — with a copy in Sent Items, at **`Low importance`** | Automated security mail is indistinguishable from mail the recipient sent, passes SPF/DKIM/DMARC as a legitimate internal send so no anti-spoofing control will flag it, and attributes the action to a human in the audit trail. **Not a choice in the template**: the Office 365 connector offers no managed-identity option, while the two Graph calls in the same workflow use the managed identity. One run, two principals, one of them inherited silently (`POS-083`) | **live, 2026-08-08** |
| 148 | Resetting a compromised password remediates the account | The reset **did** invalidate the old credential — it was rejected at sign-in (`50126`). The forced-change ceremony that followed then **accepted that same just-invalidated value as the new password** | **The remediation is reversible by the account holder in one step.** In the threat model this playbook exists for, that holder may be the attacker, and they satisfy `Current password` with the temporary credential the playbook mailed. The automation's reported outcome and the tenant's end state diverge completely. Which of three mechanisms permits it — password-history depth, a forced-change bypass, or an admin `PATCH` that never writes history — is **not established and not asserted** | **live, 2026-08-08** |
| 149 | MFA prompts come from tenant policy — security defaults, Conditional Access, or per-user MFA | Security Defaults **Disabled** (`POS-001`); the Conditional Access policy list is **empty** (the blade rendered its `What is Conditional Access?` / `Get Started` state); all 28 rows of the 24-hour sign-in log read `Conditional Access: Not Applied`. The requirement came from **`Authentication methods → Registration campaign`, `State: Microsoft managed`**, Include `All users`, every dependent field greyed | **This inverts the repository's recurring shape.** The usual finding is *configured, and ineffective*; this is **unconfigured, and in force**. The tenant cannot answer "is a registration campaign enabled here" from its own configuration — Microsoft holds the state, and the blade says settings may change over time without administrator action. Observed effect: five `50072` interrupts in ten minutes, each followed by a successful single-factor sign-in. One unresolved discrepancy: the blade names the method `Passkey (FIDO2)`; the screens offered Microsoft Authenticator (`POS-085`) | **live, 2026-08-08** |
| 150 | Sentinel's objects live under the portal's Microsoft Sentinel section | In the Defender portal the `Microsoft Sentinel` subtree renders `Search`, `Threat management`, `Content management`, `Configuration` — and **no incidents**. Incidents are at `Investigation & response → Incidents & alerts → Incidents`, outside the Sentinel section entirely. The Home page banner reads **`Microsoft Sentinel is here`** with `Learn how to maximize this trial` — an onboarding prompt whose five cards are all tasks to complete | The incident queue is unified across Defender and Sentinel, so it cannot live in the workspace-scoped Sentinel remainder. **The banner announcing the migration addresses someone starting Sentinel, not someone whose navigation just changed** — it names no moved paths and no prior portal. Recorded with a date because both portals still answer today and one of them will not after 31 March 2027; this evidence is unrepeatable once the Azure paths close | **live, 2026-08-08** |
| 151 | Two KQL stores sit behind one query language, and Defender's advanced hunting cannot see workspace tables | `SecurityAlert` — a Log Analytics workspace table — **ran in Defender's Advanced hunting**, header reading `Selected workspace: law-lab-01`, returning the alert's full `Entities` blob. The schema tree still lists XDR tables only | The store split as this repository recorded it **no longer holds in this build**. Dated rather than amended: the earlier finding was true when observed and this is true now, and collapsing the two would erase the change. Whether workspace tables appear in the schema tree or only resolve at query time is unchecked | **live, 2026-08-08** |
| 152 | The name a portal renders for an entity is the entity | Four surfaces — incident grid `Impacted assets`, incident-graph node, alert list, and the entity card — all rendered **`labuser`**. The `SecurityAlert` `Entities` object carries `Name`, **`UPNSuffix`**, `UserPrincipalName`, `DisplayName` and `AccountName`, all populated | **Four concurring displays and one authoritative store.** They agreed because they all render the same field, not because they were right. Consequence for the playbook: the template rebuilds the UPN as `concat(Name, '@', UPNSuffix)` — with a `For_each`/`for_each` casing inconsistency repeated five times, resolving only because the expression engine is case-insensitive — while a complete `UserPrincipalName` sits unused in the same object. The reconstruction is the only thing that could produce a malformed URI, and a malformed URI routes to row 144's leaky branch | **live, 2026-08-08** |
| 153 | Seven failed sign-ins are seven sign-in events | Seven `50126` rows across ten seconds, carrying **three** distinct Request IDs (3 + 1 + 3) — the portal groups retries within one authentication session under a single request | True at the event level, false at the request level. `DET-004` counts `SigninLogs` rows, so the detection still saw seven and the threshold behaved as designed — but "seven failed sign-ins" and "seven sign-in attempts" are not the same claim, and the surface that would tell them apart is a column nobody reads | **live, 2026-08-08** |

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
- Why does `Computer == "LAB-SRV-DEFENDER-01"` return nothing? → the OS hostname truncates to 15 chars (`LAB-SRV-DEFENDE`); use `startswith` (`POS-033`)
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
| 154 | A capacity that bills from creation is usable from creation | `Create` succeeded at **11:00:07** and the first answer landed at **11:14** — **nine setup screens** between them: `Finish setup in Security Copilot` *Required*, a second `Get started`, `Workspace info` (own name + own data storage location), `Getting ready for you…`, capacity selection, `Help improve Copilot`, M365 data notice, Purview logging, `Assign roles`, `You're all set` | Guides 62 and 64 both go from capacity to prompting. **14 minutes of a paid clock hour elapsed before the product could answer anything** — a quarter of the hour, billed, spent on consent screens | **live, 2026-08-09** |
| 155 | Overage can be turned off | `Enable Overage Capacity` **will not disable**. ARM confirms the schema: `overageState` + `overageAmount`, with **no `Disabled` value**. Zero is `overageState: "Limited"`, `overageAmount: 0`. Form default is **`Allow Unlimited Overage Capacity`** | Overage is structurally always enabled; the only control is its ceiling. The as-shipped configuration is unbounded. "We disabled overage" would be the wrong sentence — it is bounded, not off (`POS-087`) | **live, 2026-08-09** |
| 156 | Exceeding provisioned capacity bills overage | Session consumed **1.5 units** against **1** provisioned, with `Overage units used` reading **`0 of 0`** throughout. At-capacity tooltip: *All available units used — we won't charge you for the extra units it took to finish your last operation* | Microsoft absorbs completion of an in-flight operation past the ceiling. **Documented in none of guides 60–65.** An earlier claim that the unlimited default would have billed $6 for the 0.5 is **withdrawn** — unsupported by this evidence | **live, 2026-08-09** |
| 157 | A capacity warning indicates while it matters | A warning triangle sat on the `copilotlab` tab during the session with **no tooltip and no target**. The explanatory tooltip *and* the red overrun segment on the usage chart became readable only **after** the capacity was deleted | The condition is legible only once it can no longer be acted on. Same family as row 146 — a signal present at the wrong surface, at the wrong time | **live, 2026-08-09** |
| 158 | Four Defender surfaces render the account entity; Copilot renders the same one | Prompt 2 returned **four typed identifiers** for one entity — `Account Name` `labuser`, `Azure AD User ID`, `User Principal Name`, and **`User SID`** (`S-1-12-1-…`, Entra-issued) — where incident grid, graph node, alert list and `AccountName` column all show `labuser` (row 152) | The entity is one object with strong and weak identifiers; the portal displays the weak one. **The truncation is a display choice, and the layer above it is not bound by it.** The SID appears on no portal surface documented in twenty labs | **live, 2026-08-09** |
| 159 | Copilot inherits the portal's audit-trail defect | Prompt 3 described the playbook as an **automated action** with the detection as its trigger — contrary to the incident audit trail, which files that one consequential action as **`Trigger: Manual`** with empty status (row 146). It then asserted **`No other automated investigation or follow-up actions were recorded`** while **four** `Automated` / `Completed` rows sat in Activities | **Prediction P20-6 inverted.** It corrected the mislabelled minority and erased the correctly-labelled majority — and stated the absence positively rather than leaving it open. Reading past a defect and inventing an absence in one answer | **live, 2026-08-09** |
| 160 | `detected on` reports detection | Prompt 1: *detected on 2026-08-08 at 18:47:30 UTC*. That is a correct UTC conversion of **First activity** (11:47:30 local). Detection — incident creation — was **`18:57:27Z`** | The ten-minute detection latency Lab 19 measured to the millisecond is silently collapsed into the field an analyst reads as an SLA. A status word answering a different question, now at the AI layer | **live, 2026-08-09** |
| 161 | One capability answered the session | `3 steps completed` expands to **`Chose Incident Analysis`** on prompts 1 and 2, and **`Chose Microsoft Defender XDR`** on prompt 3. Usage monitoring attributes the whole session to `Plugins used: Microsoft Defender XDR` | A session-level rollup naming one plugin where two capabilities ran. An earlier claim that the dashboard confirmed the source for all three prompts is **withdrawn**; the data path behind the four identifiers is **not established** | **live, 2026-08-09** |
| 162 | Deleting a metered resource deletes its record | RG deletion destroyed `copilotlab`. `copilotlab-ws`, the full session transcript, and usage monitoring's **1.5-unit row** all survive | Guide 62 §3 claims the workspace persists; it does not mention the **consumption record** does. Inverse of `POS-084` — there run history retained what nobody wanted kept; here billing evidence outlives the billed resource | **live, 2026-08-09** |
| 163 | One object, one name | `Microsoft Security compute capacities` (blade — **sentence case**, not the Title Case of the docs), `Set up your Copilot capacity` (create form), `Microsoft.SecurityCopilot/capacities` (ARM). Residency renders as *allow Copilot to evaluate prompts anywhere in the world* → `Cross-region compute: Not allowed` → `crossGeoCompute: "NotAllowed"` | Three strings for the residency control across Basics, Review and ARM; only the third is submitted. **P20-2 withdrawn** on the casing. GA product provisions through apiVersion **`2024-11-01-preview`** | **live, 2026-08-09** |
| 164 | `Capacity region` is a choice | Renders as **static text** `US East` with no control, while `Prompt evaluation location` is a dropdown. ARM carries **both** as parameters — `geo: "US"` and `location: "eastus"` | The platform accepts both; the portal exposes one. Guide 62 instructs picking the closest region for a field that offers no choice — so the RG (West US) and its capacity (East US) diverge by design, not error | **live, 2026-08-09** |
| 165 | An empty container reports itself as empty | Empty `rg-copilot-lab` reads **`No resources match your filters`** under `Type equals all` / `Location equals all`. Usage monitoring offers a **page 2** holding `No dimensional usage data to show`. Message center search for `Security Copilot` returns **5 items, none about Security Copilot** — four Purview agent notices, matched because those agents run on SCUs | Three empty-state misreports in one lab. The Message center case is `MOD-83`'s Purview correction seen from the other side: the search matched the **dependency**, not the product | **live, 2026-08-09** |
| 166 | Setup consent is where setup consent is administered | Four consent surfaces, four shapes: overage (toggle, defaulted **unlimited**); cross-geo compute (checkbox, labelled *recommended for optimal performance*); telemetry + security-AI-model training (two toggles, both **ON**); M365 service data (**no control**, single `Continue`, opt-out at `Owner settings`). Purview Customer Data logging shipped **OFF** | **Unconfigured, and in force — four times in fourteen minutes.** Two controls state that the real setting lives on a page the wizard never shows. One default ran the customer's way, which falsifies the easy generalisation (`POS-089`) | **live, 2026-08-09** |
| 167 | Selecting a resource group enables acting on it | The Resource groups **list-level** toolbar exposes no Delete; ticking a group's checkbox enables nothing. `Delete resource group` exists only inside the group's own Overview blade | An affordance that selects without enabling. The delete dialog then confirmed *all dependent resources, including hidden types, are shown* — **1** — so the Resources list was not a filtered undercount | **live, 2026-08-09** |
| 168 | Analytics rule validation tests the rule as it will run | Pre-save validation runs the query against **Log Analytics over the panel's range** (Last 7 days), not against NRT execution semantics. The refuted hour-aggregation query returned a matching row and read as healthy | The surface produces positive evidence that a structurally broken rule works. A confidently wrong yes, not a silent failure | Lab 21 §8.2 |
| 169 | An anomaly rule's Edit form shows its current Mode | Grid badge read `FLGT` (Flighting) while the Edit wizard's General step rendered **Production** selected, on an untouched duplicate created minutes earlier | The Edit form defaults rather than hydrates. Any save from it silently writes Production; the grid badge is authoritative | Lab 21 §4.3 |
| 170 | Deleting a promoted anomaly rule restores the demoted original | Promotion demotes the counterpart atomically and correctly. Deleting the promoted copy leaves the original in Flighting, `Last modified` unmoved — no Production version remains | Demotion is a state on the original, not a maintained relationship. Automatic down, manual back, no warning on any surface | Lab 21 §4.3 |
| 171 | An NRT alert's reported query window reflects its execution model | `ExtendedProperties` records a ~12-hour window (`08:22:26Z` → `20:20:27Z`) on a rule documented to run once per minute with a one-minute lookback — and the alert's own evidence record counts 4 where 12 hours holds at least 8 | The metadata contradicts both the documented model and the alert's own result. Candidate AM/PM rendering error recorded; **not isolated** | Lab 21 §8.4 |
| 172 | A firing analytics rule is visible in the Defender alert surfaces | Alert present in `SecurityAlert`; absent from the Defender alerts queue and from `AlertInfo`, which held 21 other Sentinel alerts at the same read | Incident settings govern alert visibility across two Defender surfaces. Both nulls are indistinguishable from "the rule never fired" | Lab 21 §8.3, `POS-091` |
| 173 | PUA protection is on and blocking; audit mode detects and logs without blocking | `PUAProtection` reads **2 (audit)**. A PUA test file downloaded, persisted on disk, and produced **no threat object, no event 1116, no event 1117** — with real-time protection, MAPS reporting and sample submission all on. An EICAR positive control on the same machine minutes later produced all three | An auditing control that fails silently produces exactly the evidence of a clean environment. "Audit" and "logged" are not the same claim, and only the second is testable | Lab 22 §8.1, `POS-092` |
| 174 | The browser blocks an unsafe download | Edge refused with `"PotentiallyUnwanted.exe can't be downloaded securely"` and left the **complete 33 KB payload** on disk as an orphaned `.crdownload` in the Edge cache | The block is of the save, not of the transfer. The bytes arrived and stayed — and that retained copy is the one cloud investigation later adjudicated Malicious | Lab 22 §8.3 |
| 175 | AMTSO test logic: if the file downloads, the configuration is wrong | Three outcomes are indistinguishable at the browser — PUA blocks the file, the browser blocks the save, audit mode allows it while recording nothing. Both command-line retrievals returned silently to the prompt; only a corner toast differed | A test whose pass condition is "the file did not appear" cannot separate a working control from a different control from no control | Lab 22 §8.4 |
| 176 | Clicking `Initiate Automated Investigation` starts an automated investigation | Incident and investigation were created at **5:15:41 PM**, 53 seconds after the antivirus detection, triggering alert `'EICAR_Test_File' malware was prevented`, detection source `DetectionEngine`. The manual click three minutes later registered as its own alert (`Automated investigation started manually`, category Suspicious activity) and joined the run in flight. Four surfaces agree | The alert title names the analyst action, not the cause of the investigation. An operator reading the queue would conclude a human caused it | Lab 22 §8.5 |
| 177 | The incident's `Evidence and Response` tab holds the incident's evidence | Incident scope: **1** entity (`eicar.com`, Malicious, Prevented). That incident's own investigation: **2**, both Malicious — the second awaiting approval. The incident's left rail reads `All evidence (1) / Files (1)`, confirming completeness within its scope | Same tab name, same page position, two objects, two scopes. The omitted entity is the one needing a human decision, and nothing on the narrower surface signals the omission | Lab 22 §8.6 |
| 178 | The Action Center is where pending approvals are found and actioned | The Pending tab read `0 items / No actions found` while the investigation rendered `Pending actions (1)`. A re-read hours later, no filters set, showed the item present and unchanged | Propagation, not permanent divergence — but a transient null on the approval queue is indistinguishable from an empty queue, and the analyst working that surface sees nothing to approve | Lab 22 §8.7 |
| 179 | Investigation duration reports how long the investigation took | `2:31h` at read, against a last completed analysis step **ten minutes** after start. The remainder is time awaiting human approval | Duration is elapsed wall time including queue time. An investigation whose approval waits three days reports a duration of three days | Lab 22 §8.7 |
| 180 | An automated action carries the times it was created and completed | The Pending actions tab renders `File created date` — a property of the file. The Log tab's pending row renders no execution start time. The completed quarantine's CSV export carries `ActionStatus: Completed` with an **empty `EndTime`**. The only absolute anchor is the Action Center's `Action update time`, which is not labelled as a creation time | The action lifecycle is uninstrumented at both ends; any age or duration for an action is inferred rather than read | Lab 22 §8.7 |
| 181 | One state, one label | The same pending state renders as `Pending action` (investigation header), `Pending approval` (Investigations list and investigation status column), and `Pending` (Action Center) | Three labels for one state across three surfaces, each internally consistent and none cross-referenced | Lab 22 §8.7 |
| 182 | Device names render truncated in portal display surfaces | `LAB-WIN11-` — 15 characters — on **six** surfaces including the **machine-readable Action Center CSV export**, which carries the truncated value as data rather than rendering a display name | The truncation is not a rendering artefact. At minimum it is the device identity MDE holds, whatever the OS hostname says | Lab 22 §8.8, `POS-033` |
| 183 | Deallocating a VM ends the charges for it | Both VMs read `Stopped (deallocated)`; the client VM's public IP is **SKU Standard, Assignment Static**, still associated, and bills continuously for as long as the resource exists — roughly $0.005/hr, ~$3.65/month | Compute stops; the IP meter does not. MOD-84's mechanism, caught from configuration before the invoice rather than inferred from billing afterwards | Lab 22 §9, `POS-094` |
