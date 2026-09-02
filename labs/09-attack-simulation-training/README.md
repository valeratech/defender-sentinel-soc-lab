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
| Simulation vs automation | **Single simulation** | Simulation automation | Automation fires on conditions and can carry multiple techniques; a first observation needs a deterministic technique, payload, and send time. A standing schedule is also pointless in a tenant then expiring 2026-08-13 (extended to 2026-09-14 on 2026-08-06, `POS-077`; the design decision stands on the determinism argument, not the clock) |
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
| Exclusion holds | Report denominators **and** the excluded mailbox itself | `/1`, admin absent, nothing delivered | ✅ every denominator `/1`; admin Inbox **and Junk** empty of the payload and of any training notification *(verified independently 2026-07-27)* |
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

**The exclusion is verified twice, from both sides.** The report's denominators all
read `/1`, which is the platform describing its own behaviour. The excluded admin
mailbox was then checked directly — no payload in Inbox or Junk, and no training
notification. Platform-reported and independently observed are different grades of
evidence, and an exclusion claim resting only on the first is the weaker kind this
repository exists to distinguish.

**Report** — 100% compromised, 0% reported, predicted 37%. `Positive Reinforcement
Message Delivered 0/0` (`POS-038`). Two modules assigned by trigger:
`Business Email Compromise | ClickedPayload` and `Ransomware | Compromised`.

**"0% reported" is a behavioural result, not a missing control** *(verified
2026-07-27)*. The Outlook **Report** button is present in `labuser`'s mailbox with
both options — *Report junk* and *Report phishing*. The capability existed and went
unused. Without that check the figure was ambiguous between "the user didn't report"
and "the user couldn't," and those are different findings. What the button would
*do* is `POS-040`, and the answer is less obvious than the metric suggests.

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
**Converted to a decision, 2026-09-01** (`PC-REM-01`, Reviewer-locked). Opening the training link writes training state against the preserved campaign, for modest remediation value. **Scope measured:** persisted completed campaign and current AST reporting/settings state (2026-09-01). **Scope not measured:** clean/private-session retry behaviour; role requirement vs session contamination is established in neither direction. **Reopening trigger:** a separately authorized expendable AST campaign or training-link validation designed from inception for that test.

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
**Converted to a decision, 2026-09-01** (`PC-REM-01`, Reviewer-locked). The real phishing-detection path stays untested here: building a fresh phishing experiment to clear this line would be new technical construction, not documentation of work performed. **Scope measured:** the Attack Simulation Training campaign and its observed telemetry and reporting behaviour — the simulation payload was absent from both `EmailEvents` and `EmailUrlInfo`, and the campaign did not establish real-phishing detection coverage. **Scope not measured:** end-to-end detection of a real phish; established in neither direction. **Reopening trigger:** a separately authorized, safely bounded real-phishing-detection validation.

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

**The reporting path is configured to be silent, and reading it changed it**
(`POS-040`, observed 2026-07-27). Four inherited defaults across two feature areas
all point the same way: no confirmation prompt, no success message, no results
email, and positive reinforcement set to *Do not deliver*. A user who correctly
reports a phish receives nothing. A user who fails receives a landing page, two
modules, and weekly reminders. That does not explain the 0% here — `labuser` simply
did not report — but it explains why nobody would learn that reporting is worth
doing.

Two things surfaced underneath it that are sharper than the defaults themselves.
**The routing destination is in neither object that supposedly holds it**: the
policy says *send to a customised address*, the rule that would define that address
does not exist, and per Learn the effective recipient is the global admin's mailbox,
which no surface displays until someone reports. Blank is not unset. And
**`Get-ReportSubmissionPolicy` shows the policy was created 2026-07-27, thirteen
days after the tenant** — inside the window in which the settings page was first
opened, and never modified since. Reading configuration wrote configuration. An
audit is not necessarily a non-event, which undercuts an assumption every audit
rests on.

One consequence recorded but not tested: Learn instructs that the reporting mailbox
be identified as a SecOps mailbox specifically when Attack simulation training is in
use, or a user report may trigger an unwanted training assignment. This tenant's is
not. The campaign was live while this was discovered, and testing it would have
falsified the committed 0%.
**Converted to a decision, 2026-09-01** (`PC-REM-01`, Reviewer-locked). The SecOps-mailbox interaction was not exercised while the campaign was live because testing it would have falsified the committed 0%, and it is not exercised now because the committed campaign is the evidence this lab exists to preserve. **Scope measured:** campaign and reporting behaviour with the reporting mailbox *not* designated SecOps, as recorded above; current AST settings state measured 2026-09-01 (Repeat offender threshold 2, Training threshold 90 days, training completion 0%, repeat offenders 0). **Scope not measured:** behaviour under designation, including whether a user report triggers an unwanted training assignment. Neither outcome is established. **Reopening trigger:** a separately authorized expendable AST campaign designed from inception for that test.

Secure Score gives this a falsifiable follow-up. Its history shows *Ensure Microsoft
365 audit log search is Enabled* at **0/3** as of 07-19; auditing was turned on
2026-07-27, and the portal states score updates take up to 24 hours.

**Checked 2026-07-28 — the prediction is not yet testable, and the reason is the
finding.** The recommendation still reads `0/3 · To address`, but its **Last synced
is 2026-07-25** — two days *before* auditing was enabled. This is not "evaluated and
not credited"; it is **not re-evaluated at all**, and only the `Last synced` column
distinguishes those two states.

The row also names its source: **Product = Microsoft Information Protection**,
Category Apps. The ASR recommendations, sourced from Defender for Endpoint, synced
2026-07-27. So **`Last synced` is per-recommendation and follows the source
product's own cadence** — the blanket "up to 24 hours" at the top of the page
describes no particular row, and here it is already contradicted by one. Licensing
is not the blocker (`Have license? Yes`).

Practical consequence: a Secure Score recommendation reading *To address* means
either the control is absent **or** that product has not re-evaluated since it was
added. Read `Last synced` before concluding anything from a status.
**Resolved by read, 2026-09-01.** "Ensure Microsoft 365 audit log search is Enabled" renders **Completed**, **3/3 points**, **Last synced 8/31/2026** — the recommendation is credited. The historical *To address* state (stale sync 2026-07-25) stands as recorded and is superseded forward, not rewritten; this read does not independently establish the exact time the control became effective.

**What a 100% compromise rate means with one target: nothing.** It is arithmetic.
The metric that matters is the trend across campaigns, which this tenant cannot
produce. Recorded as foreclosed rather than untested, along with repeat-offender
behaviour and 90-day training reassignment.

## 8. References

- `POS-035` (audit logging), `POS-036` (hydration), `POS-037` (the campaign),
  `POS-040` (user reported settings — the reporting half of the same story),
  `POS-038` (notification defaults), `POS-039` (payload indicators), `POS-021`
  (the endpoint-identity decision the SSO prompt would have undone)
- Lab 03 — the detection pipeline this lab is the deliberate inverse of
- Lab 08 / `POS-034` — the surface-vs-store finding this lab's endpoint trap repeats
- `kql/advanced-hunting/simulation-email-telemetry.kql`
- Microsoft Learn — Attack simulation training; Turn auditing on or off;
  Enable-OrganizationCustomization
