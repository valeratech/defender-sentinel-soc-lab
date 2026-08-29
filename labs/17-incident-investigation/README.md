# Lab 17 — Incident Investigation: the Trap, the Audit Trail, and the Role That Wasn't There Yet

| Field | Value |
|---|---|
| **Domain** | Response / SOC operations |
| **Objectives** | Investigate and triage the queue's richest incident end-to-end (the incident-investigation assignment §2–§6); spring and sidestep §5's classification trap on our own telemetry; demonstrate §1's permission model live — grant Microsoft Sentinel Responder to the scoped analyst and test both sides of the boundary |
| **Depends on** | Lab 03 (the incident under investigation *is* Lab 03's onboarding validation), Lab 11 (`DET-004`, whose incidents are the boundary-test corpus), `POS-027` (the analyst identity), `POS-002` (the gap this lab's grant pattern speaks to) |
| **Status** | 🔨 Built, documentation in progress — classification written, boundary crossed twice, one headline claim withdrawn on its second read |
| **Built** | 2026-08-05 (triage + grant + activation 1) · 2026-08-06 (re-activation + the read that killed the headline) |

> The incident that looked like the queue's scariest item — Medium, multi-stage,
> "Execution & Lateral movement" — was the lab's own hand three times over: two
> detections on the MDE onboarding test script, and one on Azure Run Command
> delivering the onboarding package itself. §5's trap sprung exactly as
> written, and the correct verdict (**Informational, expected activity —
> Security testing**) turned out to be stored and exported under a name the
> selection UI never shows: **Benign Positive**. Then §1's role model went
> under the instrument, and the biggest finding of the lab is one this repo
> had to *withdraw*: the unified portal refused the Responder's documented
> write with "You're missing permissions" — and twelve hours later, on a fresh
> token, performed it. The error message described the cache, not the identity.

---

## 1. Objective

The incident-investigation assignment investigates and manages incidents. This lab treats the source guide as
two instruments:

1. **The classification trap (§5).** Incident 1 was created by Lab 03's
   onboarding validation. If the evidence shows our own test artifacts, the
   only honest verdict is *Informational, expected activity → Security
   testing* — True positive overstates it and False positive is actively
   wrong, because the detections were accurate. The framework was fixed
   *before* the incident page was opened.
2. **The permission boundary (§1).** The guide's table says Microsoft
   Sentinel Responder grants "everything Reader can, plus manage incidents"
   without content-authoring rights. The analyst (`POS-027`) held no Azure
   RBAC at all. The experiment: measure what the analyst sees before the
   grant, grant the role, and test one permitted write and one prohibited
   edit — with the before-state on the record first.

Cost: none. Every surface in this lab is included in existing licensing;
no meter was opened.

## 2. Predictions

Registered before the build (pre-check 2026-08-05 and during assessment):

| # | Prediction | Outcome |
|---|---|---|
| P77-3 (rev.) | Investigations tab populated on incident 1, empty on Sentinel incidents | ✅ Confirmed — one AIR run on incident 1; absence unrepresented elsewhere (row 117) |
| P77-4 | Assets sparse for the visibility-gap reason, not containment | ✅ Confirmed — 1 device, 2 users, all else zero; the estate is one sensor wide |
| P77-6 | All managed fields write cleanly, no propagation warning, queue reflects immediately | ✅ Confirmed as amended — **six** pane fields, not seven; Comments live elsewhere (row 111) |
| P77-9 | The `Active alerts` UI-vs-CSV discrepancy resolves as the export carrying the total | ✅ Confirmed + mechanism — AIR had resolved 1 of 3 (rows 115, 119) |
| P77-10 | Incident 1 carries zero system tags | ✅ Confirmed — none in queue, header, or Manage pane |
| P77-11 | Threat-analytics link absent on incident 1 (test artifacts match no named pattern) | ❌ **Falsified** — "Technique Profile: Malicious use of PowerShell" present; the profile matches behavior, not attribution |
| P77-12 | The analyst's queue omits all Sentinel incidents pre-grant | ✅ Confirmed — 5 incidents at a 6-month window, zero `Microsoft Sentinel` rows, with all 17 inside the window by date |
| P79-3 | The owner picker lists all identities; licensing doesn't gate | ✅ Confirmed and exceeded — it enumerates DLs and security groups too (row 121) |

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Classification framework | Fixed in advance: TP if unexpected, Security testing if the tree shows Lab 03's artifacts, FP is the wrong answer | Decide at the page | Prevents the verdict from being fitted to the evidence after the fact |
| Order of operations | Read every tab before the first write | Triage immediately | All seven fields were untouched across 19 incidents; every change had to be attributable |
| Responder scope | **Resource group** (`rg-soc-lab`) | Workspace (`law-lab-01`) | Sentinel is a resource family — playbooks, workbooks, automation live beside the workspace; G57's Playbook Operator composes at the same layer. Trade-off recorded in `POS-072`: least privilege argues workspace scope; the RG delta is LAW read/query visibility plus automatic inheritance by future resources |
| Assignment state | **Kept the accidental Eligible time-bound**, activated via PIM | Convert to Active permanent | The wizard's Assignment type tab silently produced the *production* pattern `POS-002` has named since Lab 00 — eligible, justified, time-boxed, audited. The richer demonstration, kept deliberately |
| Boundary-test subject | ID 19, not incident 1 | Reuse incident 1 | Incident 1's triage state is the classification artifact; it stays clean |
| The T+17 min refusal | **Parked 12 h and re-read** rather than shipped | Commit the headline same-day | The zero (a greyed button) had one read, minutes after activation, in a repo whose walls are covered in propagation lessons. The re-read killed the claim — see §6 |

## 4. Build

Portal-only throughout (paths in `docs/navigation.md`). Condensed sequence:

1. **Baseline** — queue export: 19 incidents, all `Active`/`Unassigned`/`Not
   set`. Incident 1 priority score 72; the other eighteen all exactly 3.
2. **Read phase, incident 1** — Attack story (3 alerts, graph, details),
   Alerts, **Activities** (undocumented tab; the incident's audit log),
   Assets, Investigations, Evidence and Response, Summary. Per-tab CSV
   exports where offered.
3. **Write phase** — Manage incident: rename (`LAB-Onboarding-Validation:
   MDE test detections + Azure RunCommand onboarding (Security testing)`),
   severity Medium → Informational, 3 custom tags, assign to admin, Active →
   In Progress, classification *Informational, expected activity — Security
   testing*. Comment via Activities → `Add comment`. Then In Progress →
   Resolved. (`POS-071`)
4. **Analyst before-state** — sign in as analyst (clean; dormant 19 days,
   no reset): 5 incidents visible, zero Sentinel, at any time window.
5. **Grant** — RG IAM → Add role assignment → Microsoft Sentinel Responder →
   analyst. A workspace-scope attempt was caught at the breadcrumb and backed
   out. Result (read from the Role assignments grid, not the wizard):
   **Eligible time-bound**, end 2027-08-05. (`POS-072`)
6. **Activation 1** (2026-08-05 ~21:00 PDT) — PIM → My roles → Azure
   resources → Activate. MFA registration forced en route (`POS-073`).
   8 h window, reason recorded. Read path arrived in ~2 min: queue 5 → 22,
   full nav rail. Write path refused at T+17 min (§6).
7. **Azure-side write** (same night) — Sentinel → Threat management →
   Incidents → ID 19 → Owner → analyst. Succeeded, 21:12 PDT. (`POS-074`)
8. **Expiry observed** (overnight) — role self-expired; queue back to 5, nav
   collapsed, Sentinel service page rendering its no-subscription empty state
   to a merely-expired identity.
9. **Activation 2** (2026-08-06 06:59 PDT) — re-activate; Defender portal
   required a manual sign-out/in this time. Queue 22 confirmed (the control),
   then **ID 19 → Manage incident: the pane opened.** Status → In Progress →
   Save, 07:06 PDT. The member alert followed to `In progress`. Role
   **self-deactivated ~07:20** — ~21 minutes used of the 8 h window, the
   just-in-time model run to completion rather than left to expire.
   (`POS-074`)
10. **Prohibited-edit read** — Detection Rules (unified portal) as analyst:
    both analytics rules readable in full (query, logic, schedule); the
    detail pane's toolbar carries no edit control.
    *(pending — whether an edit control exists on this pane for an identity that holds authoring rights has not been read; until the admin-side comparison is made, the bare toolbar is a description, not a boundary)*

## 5. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Classification evidence | Process trees, all 3 alerts | Lab 03 artifacts | ✅ Test script (loopback download, `test-WDATP-test` path) twice; Azure Run Command delivering the onboarding package (`WindowsAzureGuestAgent → RunCommandExtension → powershell -File script10.ps1`) |
| Triage writes land | Fresh queue export post-save | All fields reflected | ✅ Same artifact carries `Benign Positive` / `Security testing` — the vocabulary finding (row 109) |
| Write isolation | Diff post-triage export vs baseline | 18 rows byte-identical | ✅ One incident touched |
| Pre-grant boundary | Analyst queue, 6-month window | Zero Sentinel rows | ✅ 5 incidents; P77-12 |
| Role effect (read) | Same queue, role active | Sentinel rows appear | ✅ 5 → 22 within ~2 min of activation |
| Role effect (write) | Manage incident under active role | Pane opens, write saves | ✅ On the **second** read (T+12 h, fresh token); refused on the first (§6) |
| Role expiry | Analyst surfaces post-window | Everything retracts | ✅ Queue 22 → 5, nav collapsed, no revocation step performed |

## 6. Failures & Fixes — and four withdrawals

The corrections ledger, recorded rather than edited away:

1. **The 7 h 37 m "orphan alert" inference — withdrawn.** The Activities log
   showed the RunScript alert correlated 7 h 37 m after its activity, and this
   was written up as correlation latency. The Investigation flyout's
   `Generated on` timestamp showed the alert *did not exist* until then — the
   latency is XDR-layer detection, and correlation happened at birth (row 118).
2. **"Auto-resolved at 5:33 AM" — withdrawn.** An activity timestamp was read
   as a resolution timestamp. The actual chain: alert generated + AIR launched
   13:10 PDT, 12 m 34 s run, resolution writing the incident's 13:23 stamp.
3. **"The filter is hiding the comment" — withdrawn before it reached a
   file.** After saving a comment, the Activities badge read 11 while the grid
   showed 10 rows without it; a pre-seeded filter was hypothesized. The
   mechanism was a stale grid — one Refresh reconciled. The badge and grid
   update independently; the two-read rule caught the wrong mechanism (row 113).
4. **The write-path-divergence headline — withdrawn on its second read.**
   At T+17 min post-activation, Manage incident was greyed with *"You're
   missing permissions to manage this incident"* on Sentinel and MDO incidents
   alike, while the same activation's read path was demonstrably live and the
   Azure blade permitted the same write. This was provisionally framed as the
   unified portal checking URBAC for writes regardless of source — a serious
   architectural claim. The scheduled T+12 h re-read (fresh activation, fresh
   token) opened the pane and saved the write. What survives is bounded and
   operational (row 122): read and write arrived on different clocks, the
   refusal's error message attributed to the identity what was only true of
   the cache, and the honest caveat stands — the morning session came through
   a sign-out/in, so hours-scale propagation and token staleness cannot be
   fully separated. The lesson is identical either way: **a refused write
   with a permissions error, minutes after activation, is not yet evidence
   about permissions.**

## 7. Evidence

Sanitized per `SANITIZATION.md` — UPNs to `@contoso.com`, device to
`LAB-WIN11-01`, tenant GUIDs to the
nil UUID, public IPs omitted, the rule GUID and workspace GUID not reproduced.

**Incident 1 chronology (UTC):**

| Time | Event |
|---|---|
| Jul 18 16:01:16 | First test-script activity (Lab 03 validation, run 1) |
| Jul 18 16:02:50.730 | Incident created — 23 ms before its first correlation entry; the incident *is* the first correlation |
| Jul 19 12:33:08 | Azure Run Command activity (the onboarding delivery itself) |
| Jul 19 20:05:09 | Test run 2 — aggregated into the *existing* alerts, no new queue items |
| Jul 19 20:10:35 | XDR alert generated + correlated + AIR launched, same second |
| Jul 19 20:23 | AIR complete: `No threats found`, alert resolved, incident stamp written |
| Aug 6 00:07:35 | Six-field triage save (seven audit entries) |
| Aug 6 00:19 | Comment — did **not** advance the update stamp |
| Aug 6 00:24:20 | Resolved; member alerts 2/3 → 0/3 |

**The boundary test (analyst, `POS-074`):**

| Read | Surface | Result |
|---|---|---|
| Pre-grant | Unified queue, 6-month window | 5 incidents, zero Sentinel |
| T+2 min (act. 1) | Unified queue | 22 incidents, full nav |
| T+17 min | Manage incident (ID 19 and ID 2) | **Refused** — "You're missing permissions to manage this incident" |
| Same night | Azure Sentinel blade, ID 19 | Owner → analyst, saved |
| Overnight | All analyst surfaces | Role expired; everything retracted |
| T+12 h (act. 2, fresh token) | Manage incident, ID 19 | **Pane opened; Status → In Progress saved** |

## 8. Analysis

**The trap is real and the product half-springs it for you.** The incident's
title ("Execution & Lateral movement"), its Medium severity, and its 72
priority score all argue for treating it as hostile — and its "lateral
movement" is Azure Run Command installing the sensor. Every entity in the
evidence grid reads `Suspicious`, including `127.0.0.1`, because entity
verdicts are inherited from the detection, not assessed. The honest verdict
required reading process trees, and the honest verdict is then *stored under
a different name than the one selected* (row 109). Priority score, for its
part, never moved: a known-benign, resolved incident still outranks every
live incident 72-to-3, and an analyst sorting by score works it first.

**§1 is true with an asterisk the guide doesn't carry.** Sentinel Responder
does grant incident management in the unified portal — eventually, on a token
minted after the grant is fully live. The role model itself behaved exactly
as documented on both portals. What the documentation nowhere says: the
grant's *visibility* and *writability* arrive separately, and the interim
error message misattributes the gap to permissions. In production that
message sends an analyst to an admin to fix a grant that was never broken.

**The accidental Eligible was the best thing that happened to this lab.**
One unread wizard tab produced `POS-002`'s production pattern — eligible
assignment, justified activation, per-elevation MFA stronger than the tenant
baseline, bounded window, self-expiry, optional early deactivation, every
step audited. The forget-to-revoke failure mode — the exact "defensible when
made, invisible three weeks later" problem this register exists to catch —
is structurally deleted. `POS-002` stays open (the Global Administrator still
does the work), but its production column now points at something this
tenant has demonstrably run.

**The queue is per-identity arithmetic all the way down.** The Multi-alert
metric read 29% to the 5-incident analyst and 8% to the 22-incident admin,
flipping in sympathy with each activation and expiry. The Workspaces export
column renders a name for one identity and a GUID for another. Three MDO
incidents (auto-created by Lab 15/16-era admin actions, auto-resolved,
verdict-less — row 119) were visible to the analyst before they were noticed
on any admin export, and the mechanism is now unprovable because the exports'
filter-chip state was never recorded (row 114). The export-discipline rule
that falls out — capture the chips with every export — is this lab's process
contribution.

## 9. References

- [Microsoft Sentinel roles and permissions](https://learn.microsoft.com/en-us/azure/sentinel/roles)
- [Investigate incidents in the unified portal](https://learn.microsoft.com/en-us/defender-xdr/investigate-incidents)
- [PIM: activate Azure resource roles](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-activate-your-roles)
- [Alert classification / determination](https://learn.microsoft.com/en-us/defender-xdr/alerts-queue)
