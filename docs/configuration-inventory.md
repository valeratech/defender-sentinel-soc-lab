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

---

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

### 3.4 Log Analytics workspace — Lab 04 🔜

- [ ] **Path:** Log Analytics workspaces
- **State:** Not yet built.
- **Watch:** which resource group it lands in — see `POS-015`. And retention, the main
  ingestion-cost lever.

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

### 5.3 Device onboarding — Lab 03 🔨

- [ ] **Path:** System → Settings → Endpoints → Onboarding
- **State:** In progress.
- **Capture live:** method chosen *and rejected*; enrolled → Intune inventory →
  Defender device list → first `DeviceEvents` rows; error text verbatim.

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

## The six divergences

Where the source guides and this environment disagree. Every one was found by checking
rather than assuming, and every one is silent — no guide step is wrong enough to raise
an error.

Recorded against the guides **as originally written** (see *Source guidance* above). All
six have since been corrected in the revised versions.

| # | Guide says | Environment is | Consequence | Record |
|---|---|---|---|---|
| 1 | **G1**: Azure free trial gives $200 credit; services pause at exhaustion; card never auto-charged | Pay-as-you-go, uncapped, no credit (`POS-005`) | **The safety net does not exist.** No spending limit is available. Budgets notify but cannot cap. Deallocation (`POS-016`) is the only real control | **revision notes only** — original G1 not read back |
| 2 | G4: The MDE↔Intune connection lets Intune enforce compliance based on Defender's device risk | Connection *Available*, but `POS-011` is **Off** | G4's two steps do not enable risk-based compliance. The step that does is never mentioned. Following the guide exactly produces an integration that reports healthy and does not do what the guide says | **original, 2026-07-17** — two steps, toggle absent, verbatim |
| 3 | **G1**: Cancel the subscription before the trial ends | Turned recurring billing off instead (`POS-017`) | Cancelling ends access immediately; turning recurring billing off keeps the trial to full term and stops the conversion. Same cost, four more weeks of lab | **revision notes only** — original G1 not read back |
| 4 | **G2**: the device silently registers with Intune after sign-in | Never enrols (`POS-022`) | **The sharpest one.** G2 describes user-driven join behaviour; G5 builds a VM joined by the `AADLoginForWindows` extension. Both guides individually correct; together they produce a device that never enrols, with every precondition satisfied and no error raised | **revision notes only** — original G2 not read back |
| 5 | **G5**: troubleshoot Entra sign-in failure by disabling blocking Conditional Access policies | **Zero CA policies exist** (`POS-003`) | The prescribed remedy has no cause to address. The real failure was `AADSTS50055` — expired password on a new account — found in `dsregcmd`, not in the guide. Following the guidance would mean hunting for policies that aren't there, or disabling unrelated things to make an error go away | **original, 2026-07-17** — §5 read back verbatim |
| 6 | **G3**: *Quick Step* block instructs setting Security defaults to **Enabled** | Its own TLDR says disable | A copy-paste of Microsoft's *enable* procedure into a guide about disabling. Following the Quick Step literally does the opposite of the guide's purpose | **revision notes only** — original G3 not read back |

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
