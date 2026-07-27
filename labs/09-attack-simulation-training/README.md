# Lab 09 — Attack Simulation Training

| Field | Value |
|---|---|
| **Domain** | Response / Awareness |
| **Objectives** | Run a phishing simulation against real users; measure delivery, compromise, and training; establish what simulation telemetry does and does not produce |
| **Depends on** | Lab 00 (E5 licensing, MDO Plan 2), Lab 03 (the detection pipeline this is contrasted against) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-26 |

> The first Defender for Office 365 capability here, and the first that tests
> people rather than machines. The campaign confirmed what it was supposed to.
> Getting it to report anything at all produced the findings.

---

## 1. Objective

Add a measured social-engineering capability: deliver a realistic credential-harvest
message to a real mailbox, observe what the user does, and confirm what the platform
records. The campaign is the smaller half. The larger question is what a simulation
is *evidence of* — whether it exercises detection, whether it can be hunted, and what
an analyst is entitled to conclude from a clean result.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Simulation vs automation | **Single simulation** | Simulation automation | Automation fires on conditions and can carry multiple techniques; a first observation needs a deterministic technique, payload, and send time. A standing schedule is also pointless in a tenant expiring 2026-08-13 |
| Technique | **Credential Harvest** | Six others | The most common real starting point, MITRE-curated, and the only technique available even in the reduced E3 trial — so least likely to surprise on entitlement |
| Targeting | **All users, admin excluded** | Select `labuser` directly | One extra click tests two mechanics instead of one: whether all-users resolves, and whether the exclusion excludes. Mirrors the production shape of targeting broadly and carving out |
| Training | **Assign for me (recommended)** | No training / manual selection | Half the feature is the training arc; skipping it observes delivery only |
| Training due date | **7 days after end** (2026-08-04) | 30 (default) or 15 | 30 days lands 2026-08-25, twelve days past tenant expiry — the completion arc would never be observable |
| Campaign duration | **2 days** | Up to 30 | Both the floor and the default. Keeps the completion transition inside the tenant's life |
| `Send a test` | **Declined** | Send to self | It delivers to the currently signed-in user — the admin, which is the exclusion control. A simulated phish in the control mailbox makes an exclusion failure indistinguishable from a test artifact (`documentation-standard.md` §1) |
| Workstation SSO prompt | **"No, this app only"** | "Yes" | The Yes path *registers the device with the organization*. That would place an admin Primary Refresh Token on the operator's own workstation and add a non-lab machine to the device inventory — the exact condition `POS-021` exists to prevent, reached from a direction no prior lab was watching |
| Audit logging | **Enabled** (`POS-035`) | Leave as found | Unplanned. Discovered mid-lab; without it the report captures nothing |

## 3. Build

Portal wizard, ten steps, `Email & collaboration > Attack simulation training >
Simulations > Launch a simulation`. Configuration as recorded in `POS-037`.

The unplanned half was not portal work. `POS-035` and `POS-036` were resolved in
Exchange Online PowerShell:

```powershell
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser   # 3.10.1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Connect-ExchangeOnline
Get-ConnectionInformation | Format-List UserPrincipalName, State

Get-OrganizationConfig    | Format-Table Identity, IsDehydrated          # POS-036
Get-AdminAuditLogConfig   | Format-List UnifiedAuditLogIngestionEnabled  # POS-035
Set-AdminAuditLogConfig   -UnifiedAuditLogIngestionEnabled $true
```

`Set-ExecutionPolicy` is a change to the **operator's workstation**, not the tenant,
so it is not a posture entry — but it blocks the module from loading and anyone
reproducing this hits it.

## 4. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Audit logging live | `Get-AdminAuditLogConfig`, EXO endpoint | `True` | ✅ `True` (`POS-035`) |
| Org hydrated | `Get-OrganizationConfig` + a write that exercises it | `IsDehydrated False` **and** writes succeed | ⚠️ disagreed for ~30 min (`POS-036`) |
| Campaign launches | Simulations tab | Status `In progress` | ✅ `In progress` |
| Delivery | `labuser` mailbox | Message arrives | ✅ ~1 min, **Focused Inbox** |
| Filtering bypassed | Delivery location | Not Junk, not quarantined | ✅ Focused, not Other |
| Exclusion holds | Report denominators | `/1`, admin absent | ✅ every denominator `/1` |
| Compromise recorded | Report | Clicked + credentials | ✅ both, 1/1 |
| Training auto-assigned | Notifications + report | ≥1 module | ✅ **2** modules, ~90 s behind each trigger |
| Report populates | Report tab | Non-empty | ✅ fully populated |
| **No incident raised** | Incidents & alerts, 1-week window | 0 | ✅ **0 incidents, 0 alerts** |
| Payload in email telemetry | `EmailEvents` / `EmailUrlInfo` | *(expected present)* | ❌ **absent from both** |

The last row is the one that changed the lab's conclusion.

## 5. Evidence

**Campaign timeline** — four platform timestamps, and they do not agree:

| Event | Time |
|---|---|
| Review page submit | 16:20:02 |
| Simulation scheduled | 16:20:19 |
| Message delivered (Outlook) | 16:21 |
| Simulation launched | 16:22:00 |

Delivery is recorded *before* the launch event. Not impossible — "launched" may be
written when the send batch completes — but as displayed the ordering is inverted.

**The anchor is the submit stamp, and this is deducible rather than assumed.** Both
derived dates (campaign end, training due) compute from 16:20:02, and so do the
elapsed counters: first link clicked at 2h55m11s puts the click at 19:15:13, first
credential at 2h58m37s puts it at 19:18:39, and the two training notifications
landed at 19:17 and 19:20 — each ~90 seconds after its trigger, in the right order.
Anchor the same counters to 16:22:00 instead and the first notification arrives
*before* the click that caused it. The recorded `launched` event anchors nothing.

Related: the review page recomputed its launch time from 16:13:35 to 16:20:02
between arriving and submitting. That looked cosmetic. It is the value every
derived date in the campaign hangs from.

**Report** — 100% compromised, 0% reported, predicted 37%. `Positive Reinforcement
Message Delivered 0/0` (`POS-038`). Two modules assigned by trigger:
`Business Email Compromise | ClickedPayload` and `Ransomware | Compromised`.

**Email telemetry, 6-hour window** — `EmailEvents` returned two rows, both training
notifications from `attacksimulationtraining.com`, `ThreatTypes` empty, delivered to
Inbox. `EmailUrlInfo` returned four rows, all `security.microsoft.com` training
links. **The payload appears in neither.** Records from eight minutes prior were
present while one from three hours prior was not, so ingestion lag does not explain
it — under lag, the newer rows would be the missing ones.

## 6. Failures & Fixes

**The dependency chain, five links, none of it in any guide.** Simulation reporting
needs unified audit logging → which needs a hydrated Exchange organisation → which
new/trial tenants do not have → which propagates unevenly across backend servers.
Full account in `POS-035` and `POS-036`.

**Two portal messages, wrong in opposite directions.** "Complete organizational
setup" reported a Client Error for an operation that had in fact completed. The
Audit page reported inability to determine a state that a cmdlet read instantly.
Neither was trustworthy; the PowerShell reads were.

**Three tests, two answers.** `Get-OrganizationConfig` said hydrated.
`Enable-OrganizationCustomization` said already enabled. `Set-AdminAuditLogConfig`
raised `InvalidOperationInDehydratedContextException`. Resolved by waiting ~30
minutes, after which the identical write succeeded — per-object propagation behind
an org-level boolean (`POS-036`).

**Training inaccessible to the target user.** `labuser` was assigned two modules,
received both notifications, and hit **Permission Required** on the landing page's
*Go to training* button. Both the button and the emailed links resolve to
`security.microsoft.com` — the admin portal domain — so there is only one surface
and "the button targets the wrong place" is eliminated. What remains is a genuine
role requirement or browser-session contamination — the portal was open as admin in
the same browser.
*(pending — access untested in a clean private session; labuser holds no roles by design)*

## 7. Analysis

**Attack simulation training tests users. It is not evidence about detection, and it
cannot be hunted.** Zero incidents was predicted — Microsoft exempts its own drills,
because a 5,000-user campaign raising 5,000 incidents would bury the SOC that
scheduled it. The stronger result is that the payload produces *no email telemetry
at all*, while the notifications bracketing it are recorded normally. No
`EmailEvents` row means no hunting query, no custom detection rule, no analytics
rule, no ATT&CK mapping. Nothing can be built on this data because there is no data.

Two symmetrical misreadings follow, and both are mistakes a competent person makes:
run a simulation, see no alert, conclude phishing detection is broken — it was told
to stand down; or conclude the tenant is covered — nothing about detection was
exercised. Validating the detection path is a different exercise against different
artifacts — the safe form is vendor-published test artifacts, as `DET-001` did for
the endpoint.
*(pending — real phishing detection path untested, distinct from simulation)*

**A negative result only counts when it was predicted.** The absence of an incident
was written down as the expected outcome before the click. Noticing afterwards that
nothing happened would have been indistinguishable from not looking.

**A property read is not a capability test.** `IsDehydrated: False` was treated as
settling the question and it did not; only the write that exercised the object
revealed the real state. That is this repository's own thesis — configured is not
effective — and it was applied to the tenant all day and not to the reasoning about
it. `POS-011` reads a healthy status over a dead control; `POS-036` reads a true
property over an unusable capability. Same failure, opposite polarity.

**Same command, different endpoint, different meaning.** `Get-AdminAuditLogConfig`
returns `False` permanently in Security & Compliance PowerShell even when auditing
is on. With `POS-034`'s corrected finding (two stores behind one query language) and
the Lab 04 surface distinction, that is three instances across KQL tables, portal
surfaces, and PowerShell endpoints. Enough to stop being a curiosity: **identify the
surface before trusting the answer.**

**The typosquat is correct design.** The drill arrives from `templatern.com` and
lands the victim on `sharepointle.com`. Microsoft runs simulations from
attacker-shaped infrastructure because the address bar is where a trained user
actually catches a credential harvest, and first-party branding there would
invalidate the exercise. The operational consequence: allow-listing spans more than
the sender domain, and a tenant with strict DNS or egress filtering could deliver
the mail and break the click — which reads as a user who did not engage rather than
a control that intervened.

**Exemption is not blanket.** The message bypassed filtering entirely and still had
its remote content blocked by Outlook's Safe Senders behaviour. Filtering and
client-side rendering protection are separate mechanisms; the guide's framing
collapses them.

**Defaults shape the teaching more than the payload does.** Payload indicators off
(`POS-039`) means the educational page is a verbatim copy of the message with
nothing marking what gave it away. Positive reinforcement off (`POS-038`) means the
user who *correctly reports* a phish receives nothing, while the user who fails gets
a landing page, two modules, and weekly reminders. The behaviour the capability
exists to encourage is the only one with no feedback path — and both are inherited
defaults, not decisions.

**What a 100% compromise rate means with one target: nothing.** It is arithmetic.
The metric that matters is the trend across campaigns, which this tenant cannot
produce. Recorded as foreclosed rather than untested, along with repeat-offender
behaviour and 90-day training reassignment.

## 8. References

- `POS-035` (audit logging), `POS-036` (hydration), `POS-037` (the campaign),
  `POS-038` (notification defaults), `POS-039` (payload indicators), `POS-021`
  (the endpoint-identity decision the SSO prompt would have undone)
- Lab 03 — the detection pipeline this lab is the deliberate inverse of
- Lab 08 / `POS-034` — the surface-vs-store finding this lab's endpoint trap repeats
- `kql/advanced-hunting/simulation-email-telemetry.kql`
- Microsoft Learn — Attack simulation training; Turn auditing on or off;
  Enable-OrganizationCustomization
