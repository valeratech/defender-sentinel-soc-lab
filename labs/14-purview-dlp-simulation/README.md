# Lab 14 — Purview DLP: a US Financial Policy in Simulation

| Field | Value |
|---|---|
| **Domain** | Data protection |
| **Objectives** | Build a DLP policy from the U.S. Financial Data template on wizard defaults; measure what a tenant classifies before any policy exists; validate synthetic content against the SITs independently of the policy; observe the simulation report |
| **Depends on** | Lab 12 (the provisioning-window pattern; Built-in protection as the `default`-kind precedent), `POS-002` (the identity this lab quantifies) |
| **Status** | ✅ Built, documented, validated — Phases A–D complete |
| **Built** | 2026-08-01 – 2026-08-03 (A: 08-01 · B–C: 08-02 · D: 08-03) |

> The policy is deliberately **all defaults** — the only human inputs in the
> entire wizard were the Step 0 surface choice, the template selection, and the
> name. That makes the build itself a measurement: what does Microsoft ship when
> nobody decides anything? The answer (`POS-062`) ran through every screen: enabled
> locations that cannot function, notify-everything-enforce-nothing actions,
> and a tenant that was classifying content before any policy existed.

---

## 1. Objective

The DLP-policy assignment's assignment: create a US Financial DLP policy, default locations,
simulation mode. This lab treats the assignment as an instrument. Three
questions:

1. **What exists before the first policy?** (Phase A: four pre-seeded policies,
   a pre-policy classification baseline, and 70 empty role groups)
2. **What does the template actually configure?** (Phase B: every default on
   every screen, recorded before anything was touched)
3. **Does it detect?** (Phases C–D: pre-validated synthetic content, then the
   simulation report — *configured is not the same as effective*, and this lab
   does not get to claim effective until D observes it)

Cost: none for this lab. The metered DLP path is non-M365 data sources
(pay-as-you-go banner investigated, usage report read: 0 items, nothing linked,
nothing accruing). E5-trial-bound: everything here dies **2026-09-14** (was 2026-08-13; extended once on 2026-08-06, `POS-077`).

## 2. Predictions

Recorded before building (P1–P5) and before triggering (P-C1–P-C4):

| # | Prediction | Status |
|---|---|---|
| P1 | Devices selectable, produces nothing (Purview needs own onboarding) | ✅ CONFIRMED — Device: 0 matches, "Scanning in realtime" (no at-rest device scan), device actions all off, VMs deallocated: nothing through three stacked mechanisms |
| P2 | Simulation report empty at first check regardless of elapsed time | voided by sequencing — content seeded before first read; report already populated at 14.5 h |
| P3 | Pre-seeded default DLP policies exist | ✅ CONFIRMED — four |
| P4 | Purview role groups have no members; everything runs on GA | ✅ CONFIRMED — 70 groups, zero members |
| P5 | DLP evaluates all matching policies, not first-match | deferred to the DLP evaluation-order guide |
| P-C1 | SIT Test matches the doc at Medium for both SITs, policy-independent | ✅ CONFIRMED — plus two unpredicted findings (§5) |
| P-C2 | OneDrive file uploaded pre-activation still appears in simulation (at-rest scan) | ✅ CONFIRMED — first read showed the file as the match |
| P-C3 | Email sent pre-activation would never appear (transit-only) | premise ✅ CONFIRMED by three surfaces (Exchange "Scanning in realtime", "as they're sent", no retroactive scan) — deliberately untriggered |
| P-C4 | Matches land under the Low volume rule only; refined: 1 ABA / 2 Bank Account (cross-match) | ✅ CONFIRMED exactly — "1 of 2 policy rules" (Low volume), ABA 1 Med / Bank Account 2 Med |
| P-D1 | Existing matches persist after the file is deleted (report = historical record) | ✅ CONFIRMED — both matches unchanged 2 min post-delete |
| P-D2 | Restarting the simulation rebuilds at-rest results; deleted file's match disappears | ✅ CONFIRMED — rebuild found nothing, reported nothing |
| P-D3 | Exchange match's fate under restart — open, both branches recorded | RESOLVED: **WIPED** — restart destroys real-time history, which no rescan can recreate |

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Step 0 surface | **Enterprise applications & devices** | Inline web traffic | Assignment targets classic locations; inline web is the strongest candidate for the metered pay-as-you-go path |
| Template | **U.S. Financial Data** | 3 other U.S.-specific financial templates | Assignment names it; the existence of four overlapping U.S. regimes is itself recorded |
| Name | `Lab14-USFinancial-Simulation` | template default (identical to template name) | This tenant already holds four policies nobody named; a fifth called "U.S. Financial Data" would be indistinguishable from provisioning |
| Every other wizard value | **template default, untouched** | — | The defaults are the observation |
| The one override held ready | uncheck 15-day auto-enable | — | Not needed — ships unchecked, and verified unchecked. Would have fired 2026-08-17, which was then past trial death. **Amended 2026-08-06:** the trial now runs to 2026-09-14 (`POS-077`), so that date falls *inside* the tenant's life and the clock no longer forecloses the timer. Nothing is running — but if this policy ever leaves simulation mode, re-read the checkbox rather than assuming it harmless |
| Test values | **published/public** — a real institutional routing number + arbitrary digits with published keywords | generated realistic values | Public routing numbers identify banks, not people; nothing synthetic needs to look real |
| Content validation | **SIT Test function before seeding** | seed and wait | Decouples content-validity from policy activation; an empty report tomorrow is then provably policy-side |
| Seeding order | OneDrive pre-activation, email post-activation | both at once | The OneDrive file carries the retroactivity test (P-C2); the email tests transit cleanly without confounding it |

## 4. Build

### Phase A — before any policy (2026-08-01)

**Navigation trap:** DLP absent from the Purview left nav on arrival; reached
via the Home solution tiles, after which it pins (persisted across sessions —
confirmed pinned 2026-08-02). → `docs/navigation.md`.

**Pre-policy classification baseline:** Featured insights showed **17 items /
Microsoft 365** and three SIT types — Poland Passport (2), DEA Number (2), HKID
(2) — on a tenant containing lab mail and service notifications. Microsoft's
term: *zero change management*. Almost certainly false positives
(weakly-anchored patterns); not verified — Content explorer displays matched
content and the sanitization rule keeps that display-only. Recorded as the
measured false-positive floor that predates the first policy. → `POS-060`.

**Four pre-seeded policies**, all `Last modified Jul 14, 2026 9:39 PM` (now
decoded: Pacific — the provisioning window that also produced Lab 12's
auto-created groups): priorities 0–3, **three enforcing**, one in simulation
with notifications. Nobody chose any of them. Third instance of the
provisioning-window pattern. → `POS-059`.

**Role groups:** CSV export parsed — **70 built-in role groups, 0 users and 0
security groups in all 70**, no custom groups. Organization Management 47
roles/0 members; Compliance Administrator 46/0. The CSV contains no PII —
committable evidence, unusually. → `POS-061`; `POS-002`'s Purview dimension.

**Billing:** pay-as-you-go banner investigated; usage report readable unlinked
(0 items / 3 months; schema exposed while empty); Locations step later named
the metered path as non-M365 sources. No cost decision required.

### Phase B — the wizard, all defaults recorded (2026-08-02)

Step 0 (undocumented in the guide): **"What info do you want to protect?"** —
two *delivery surfaces* offered as an answer to an *information* question.
Chose Enterprise applications & devices.

Template: U.S. Financial Data (Financial category, 13 templates, 4
U.S.-specific; Enhanced is both a category and a suffix; description mentions
debit cards the SIT list lacks). Conditions read without saving: **mixed
confidence** — Credit Card High, Bank Account and ABA Medium — instance count
1–9 each, group operator `Any of these`, 327 SITs available.

Admin units: Full directory (default). Banner: scoping to an admin unit
silently removes unsupported locations from the next step.

Locations: **seven checked by default, all "All"** — including two that cannot
function here (On-prem repositories: prerequisites unmet; Instances: no MDCA).
Six banners recorded, including Instances' early-2027 retirement. The guide
says select deliberately; the wizard blanket-enables.

Protection actions (defaults): tips ON, threshold toggle ON at **10**,
incident reports ON ("you and your global admin" — the same account here),
alerts ON, **restrict/encrypt OFF**. Incident reports cover only
Exchange/SPO/OD/Teams — four of seven in-scope locations.

Access/override (defaults): every master toggle **off**; the entire device
section greyed with every action `Audit only` and file activities "Don't
restrict." Devices is in scope and uninstrumented — P1's "produces nothing"
now has a by-configuration path independent of the onboarding hypothesis.
Unpredicted find: **Recall snapshot protection** (Copilot+ PC), default Audit
only, absent from the guide.

Policy mode: Simulation preselected; tips-in-simulation unchecked; **15-day
auto-enable unchecked** (the one default we were ready to change). Banner names
On-prem and MDCA as unsupported by simulation — the two inert locations,
excluded from the very mode the policy runs in, disclosed only at the last
step.

Review: locations list correct, and the policy compiles into **two rules** —
`Low volume` (the 1–9 SIT conditions) and `High volume` (the ≥10 threshold).
The guide presents one detection; the product builds two.

**Created 16:04 PDT 2026-08-02** (portal stamp; wall clock 16:05 within a
minute — the stamp is the event-time surface and is authoritative). Landed:
**priority 4** (predicted), Mode `In simulation without notifications`, sync
`Sync in progress` at ~16:10. Purview list renders **local time** — third
timestamp surface decoded (Defender UTC-unlabelled / M365 admin local /
Purview local).

### Phase C — pre-validated trigger content (2026-08-02)

Test document (`lab14-dlp-test.txt`, 243 bytes): a wire-instruction paragraph
carrying one real published institutional routing number adjacent to the
keyword "ABA routing number," and one arbitrary 12-digit string adjacent to
"Checking account no." — both keywords verbatim from the published SIT
definitions, everything within the 300-character proximity window. Values are
ephemeral test inputs and appear nowhere in this repository (`audit-pii.sh`
treats them as failures by design — the staged-payload negative control).

**SIT Test results (Classifiers → Sensitive info types → Test):**

| SIT | Result |
|---|---|
| ABA Routing Number | **Medium — 1 unique match**, supporting elements `"routing number","ABA"`; plus a Low entry for the same value (pattern-only tier) |
| U.S. Bank Account Number | **Medium — 2 unique matches** — the account string *and the routing number* (cross-match); plus a Low entry the published definition does not contain |

Both target tiers hit; content validity established independent of the policy.

**Seeded:** uploaded to the admin OneDrive root, **16:28 PDT**, Private,
unshared — 24 minutes after policy creation, near-certainly before activation.
The file *is* the P-C2 experiment.

## 5. Findings beyond the predictions

1. **The Test function shows every qualifying tier** — confidence levels are
   cumulative gates, rendered as multiple simultaneous results. First surface
   in the project to expose classifier internals.
2. **Cross-matching measured under control:** one routing number = two SITs =
   three Medium instances from a two-number document. The pre-policy false
   positives (Phase A) are this mechanism in the wild.
3. **Docs-vs-product divergence:** Bank Account's Low tier exists live and not
   in the published entity definition (fetched same day). Mechanism not
   asserted.
4. **Prediction-miss recorded:** the ABA-checksum assumption (carried in from
   session notes) is contradicted by the SIT docs (`Checksum: No`); test design
   routed around it with a real routing number.
5. **The default posture is notify-and-report:** four of five protection
   actions ship on; the only off one is the only enforcement. "Turn the policy
   On" with untouched defaults would still block nothing.
6. **Scope ≠ instrumentation ≠ mode support:** Devices is in scope with all
   device actions off; On-prem and Instances are in scope, non-functional, and
   unsupported by simulation. Three different ways for an enabled location to
   produce nothing, all shipped by default.

## 6. Validation — Phase D, observed 2026-08-03

**Activation and the first match (P-C2).** First read 06:35–06:48 PDT (~14.5 h
post-creation, inside the 24 h trial ceiling): `Sync completed`, **1 match — the
OneDrive file**, uploaded 24 minutes after policy creation and hours before sync
completed. Simulation scans OneDrive/SharePoint content **at rest**, including
content that predates activation. P-C2 confirmed. (P2 as written was voided by
this design — content was seeded before the first read, deliberately.)

**The three-class scanning model** (Simulation overview, per-location table):
batch at-rest with completion percentages (SharePoint 75 files/10 sites,
OneDrive, both `Completed 100%`); real-time only (Exchange, Teams, Device —
`Scanning in realtime`, no retroactive scan); and the two
simulation-unsupported locations (ThirdPartyApps, OnPremisesScanner) rendering
**`In progress 0%`** — *not applicable* rendered as a scan that never finishes,
while the same card's progress text claims they were "finished scanning."
Failure-mode rule 5's cleanest specimen.

**Match anatomy (P-C4).** Items for review, per-item Match summary: rule
attribution **"matches 1 of 2 policy rules" — Low volume**, per-SIT split **ABA
1 Medium / U.S. Bank Account 2 Medium** — the cross-match exactly as the Test
panel predicted. The Low-confidence column mirrored the counts, confirming
every-tier reporting is the classification engine's behavior, not a Test-panel
quirk. And the panel refused the matched values to Global Administrator: *"The
role 'Data Classification Content Viewer' is required to view the sensitive
info details"* — the fourth measured GA-insufficiency, enforcing this repo's
own sanitization rule by accident.

**The transit leg.** Same payload, email body, admin → labuser, sent 07:06.
Delivered clean at 07:07 — no tip, no wrapper, and the enforcing priority-0
default policy visibly untouched by three Medium financial SIT instances.
Report timeline: **evaluated 07:07 (grid stamp 2:07 PM UTC-unlabelled = send
minute), absent from the report at 07:14, present at 07:18.** "Real-time" is
true of evaluation (~1 min) and the report indexes **8–12 minutes** behind it —
the confident-zero window, measured at both ends. Classification was
location-invariant: identical rule and SIT split as the file.

**The deletion experiment.** File deleted from OneDrive 07:23 (recycle bin,
untouched). At 07:25 both matches persisted unchanged — **the report is a
historical record, not a live-state view (P-D1)**; for two minutes it claimed a
match on content that no longer existed, with no annotation.

**Restart is a destructive rebuild.** `Restart the simulation` 07:27 —
confirmation dialog names zero consequences. At 07:29 nothing had visibly
changed (results still rendered; the restart's confirmation and its observable
effects were disjoint). By 09:06: **81 items scanned, 0 matches, Top-users
empty.** The at-rest rescan found no file and reported none (P-D2 confirmed) —
and the **Exchange match was wiped with it (P-D3 resolved)**: transit events do
not replay, so the real-time history the rebuild destroyed is unrecoverable by
any rescan. The email still exists in the mailbox; its match evidence does not
exist anywhere. An operator who restarts a simulation to "refresh" it silently
deletes every real-time match the policy ever recorded, and no surface warns
them. Two residues recorded unexplained: OneDrive's Matching-items card still
listed the deleted file beside a `0 matching files` counter (stale panel over
rebuilt counters), and files-scanned drifted 5 → 6 / 80 → 81 in the direction
opposite the deletion (cause not assigned).

**Pipeline live after restart.** Third send of the identical payload
(`LAB15 TRIGGER TEST`, 09:11, also serving Lab 15's trigger experiment):
evaluated at the send minute (grid stamp 16:11 UTC), present in Items for
review by 09:34. Real-time evaluation survived the restart; only history died.
And at 09:34 the Items grid (1 item) and the overview CSV export (16:34 GMT,
`Total matches 0`, Exchange blank) **disagreed about the same policy in the
same minute** — the overview aggregates on a slower cadence than the grid
indexes. Fifth distinct rendering of "how many matches exist."

**Timestamp conventions, one solution:** policy list local-unlabelled · CSV
export GMT-labelled · Items grid UTC-unlabelled · (IRM alerts, next lab:
UTC-labelled). Decodable only because wall-clock anchors existed for every
event.

**Sampling caveat, recorded:** the Items-for-review preamble states files
listed are *a sample* (~100 files per site per rule). This tenant's censuses
fit inside the sample; a real tenant's would not.

## 7. Failure Analysis

1. **The ABA-checksum assumption** (§5.4) — carried in from session notes,
   contradicted by the SIT docs (`Checksum: No`), withdrawn; test design routed
   around it with a published institutional routing number.
2. **A refinement prediction missed:** no Low tier was predicted for U.S. Bank
   Account Number (the published definition has none); the live Test panel
   returned one. Recorded as a docs-vs-product divergence, mechanism not
   asserted.
3. **Process failures during the parallel billing commit** (recorded in
   `aed55a4`): a fabricated citation caught by verification, and a paste block
   that extracted into the wrong repository because it assumed an unverified
   path. Both are the transfer document's dominant-failure-mode pattern —
   plausible pattern, untested, shipped.
4. **What the two-read rule prevented, twice:** the 07:14 empty read would have
   called the transit leg broken (it was indexed four minutes later), and the
   07:29 unchanged read would have called the restart a no-op (it was a queued
   destructive rebuild). Both zeros were claims about an index, not an event.
