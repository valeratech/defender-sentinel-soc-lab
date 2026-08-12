# Lab 22 — Endpoint Prevention and Automated Investigation: What Audit Mode Did Not Audit

| Field | Value |
|---|---|
| **Domain** | Defender for Endpoint prevention controls / automated investigation and response (AIR) / incident investigation surfaces |
| **Objectives** | Exercise endpoint prevention on a live client (modules 90–91); capture the **Defender for Endpoint AIR standalone experience before its 2026-09-01 retirement**; measure what each surface reports about the same two files |
| **Depends on** | Lab 03 (EDR detection test, onboarding latencies), Lab 06 (ASR audit-vs-block already isolated), Lab 13 (**MDO** AIR — a different product, explicitly not the capability being retired), Lab 17 (incident workflow), `POS-033` (hostname truncation), `POS-019`/`POS-020` (RDP exposure on this VM) |
| **Status** | ✅ Built and measured — four phases, one metered window of 68 minutes |
| **Built** | 2026-08-10 |
| **Cost** | `LAB-WIN11-01` compute only, 16:25 → 17:33. No Bastion. Public IP billing continues past teardown — see §9 and `POS-094`, closed on the mechanism 2026-08-12 at $0.12/day on 29 of 29 days. `P89-10` closed the same day (`POS-099`) |

> Two files were downloaded to the same machine, the same way, minutes apart.
>
> **EICAR** — blocked before it reached disk. Toast, event 1116, event 1117,
> threat object, file gone.
>
> **A PUA test file** — `PUAProtection` set to **2 (audit)**. It downloaded, it
> persisted, and the endpoint recorded **nothing**: no threat object, no 1116,
> no 1117, with real-time protection on and cloud reporting enabled.
>
> Audit mode's entire deliverable is the audit trail. There was no audit trail.
>
> The file was not unrecorded everywhere. Twenty minutes later a cloud
> investigation, sweeping the device for recently modified executables, found a
> copy Edge had left behind and adjudicated it **Malicious** — a verdict the
> local engine never reached about a file sitting in front of it.

---

## 1. Objective

Modules 90 and 91 cover endpoint prevention and the investigation of what it
produces. They are one lab and two lesson files, because **module 90 generates
the evidence module 91 consumes**; splitting them would make one lab's evidence
depend on the other's generation. Precedent: Lab 20 combined modules 85, 87 and
88.

Three things were in scope that prior labs had not covered:

1. **PUA protection**, which Lab 06 never touched — ASR was isolated there, and
   the Office rules were rejected for absent Office.
2. **Defender for Endpoint AIR as a standalone investigation experience.** From
   **2026-09-01** this no longer runs as a separate investigation and no longer
   supports manual triggering (message center **MC1411577**, verified against
   four Microsoft Learn pages on 2026-08-10). Detection and remediation stay
   embedded in the antivirus stack; on-demand investigation becomes "run a full
   antivirus scan"; results consolidate into the unified investigation page.
   **This applies to Defender for Endpoint only. AIR for Defender for Office 365
   remains available, so Lab 13's findings are unaffected and must not be
   assumed to expire.**
3. **Whether the endpoint and the cloud agree** about the same two files. They
   did not, and that disagreement is the lab.

A negative check was run before scoping: `labs/18`, `labs/19` and `detections/`
were grepped for any committed playbook or automation invoking MDE AIR. There is
none. **The retirement has no known automation dependency in this repository.**

---

## 2. Predictions

Registered before portal contact, in the order written.

| ID | Prediction | Result |
|---|---|---|
| **P90-1** | `PUAProtection` reads `1` (block) | **FALSIFIED** — reads **2 (audit)** |
| **P90-2** | The PUA file downloads successfully | **FALSIFIED twice, for two different reasons** — see §6 |
| **P90-3** | EICAR is blocked before reaching disk | **CONFIRMED** |
| **P90-4** | `.vbs` → PowerShell is a behavioural detection, not an ASR block | **CONFIRMED** |
| **P90-5** | Device name truncates per `POS-033` | **CONFIRMED**, and extended — see §8.8 |
| **P90-6** | `Initiate Automated Investigation` is offered and functional | **CONFIRMED, with its interpretation corrected** — see §8.5 |
| **P90-7** | MDE detections produce AIR, unlike `DET-004`'s Sentinel alerts | **CONFIRMED** |
| **P91-1** | The Copilot pane is absent, capacity having been torn down at MOD-88 | **CONFIRMED** on two reads |
| **P91-2** | VirusTotal shows EICAR at a high detection ratio with an old first-seen | **CONFIRMED** — 57/64, first seen 2013-03-04 |
| **P89-10** | Bastion Developer SKU bills $0 | **CONFIRMED 2026-08-12** — and stronger than predicted: no meter rows emitted at all, against Sentinel's daily zero-cost rows as control. `POS-099` |

### Corrections recorded on the record

**P90-6 is confirmed but was framed wrongly.** The prediction — that the manual
trigger control is offered and functional — holds. The session's working note
that the click at 17:18 *produced* Investigation #2 does not. Four surfaces say
otherwise (§8.5). The claim is corrected rather than quietly restated, and the
session transfer that carried it forward is superseded by this section.

**P91-1's shape was corrected before it was tested.** An earlier framing called
it "structurally pre-refuted, same shape as MOD-86." That is wrong. MOD-86 was a
scenario foreclosed before contact — nothing could run, so nothing was observed.
P91-1 is a *positive absence on a live surface*: the incident page renders
normally and the pane is not on it. "Structurally unavailable" and "torn down and
therefore absent" are different claims, and only the second is what happened.

---

## 3. What was built

Nothing persistent. No policy was changed, no rule created, no setting altered.

Two files were introduced to `LAB-WIN11-01` and one script was written:

- **EICAR test file**, retrieved by `Invoke-WebRequest` — the industry-standard
  antivirus test string, not malware.
- **A PUA test file**, retrieved from AMTSO's public test suite over HTTPS.
- **A `.vbs` script** invoking PowerShell, written on the desktop. Described in
  prose only; not vendored, per `SANITIZATION.md` §6.

`PUAProtection` was **read, not set.** Changing it would have required a
`labadmin` session (§8.9), and the finding depends on the shipped value.

Device state at the start, captured before the VM was started and therefore
free: risk *No known risks*, exposure *Medium*, health *Inactive*, *Onboarded*,
Defender AV mode **Active**, last full scan **never**, security intelligence
`1.455.332.0`, Sense `10.8830`, Endpoint DLP Disabled, `Managed by: Unknown`,
292 vulnerabilities (35 Critical, 71 High).

---

## 4. Phase A — endpoint prevention, measured at the endpoint

Connected by **direct RDP as `labuser`**, an Entra identity. That is correct for
this VM and wrong for the other one: `LAB-SRV-DEFENDER-01` is WORKGROUP-joined
and reachable only by Bastion as local `labadmin`. Two VMs, two access models,
recorded because confusing them costs a session.

### 4.1 The configuration read

```
PUAProtection            : 2      # audit, not block
DisableRealtimeMonitoring: False
MAPSReporting            : 2
SubmitSamplesConsent     : 1
```

`P90-1` predicted `1`. The shipped value is `2`. Real-time protection on, cloud
protection on, sample submission on — every precondition for detection satisfied,
and PUA handling set to observe rather than block.

### 4.2 The PUA download

`Invoke-WebRequest` retrieved the test file. It completed. The file persisted on
disk. Then:

- **no threat object** on the device
- **no event 1116** (malware detected)
- **no event 1117** (action taken)
- **no toast**

Audit mode observed nothing. Not "observed and allowed" — *observed nothing*,
by every local surface available.

### 4.3 The positive control that makes it conclusive

The same machine, the same session, the same `Invoke-WebRequest` method, minutes
later, against EICAR:

- immediate **Threats found** toast
- **1116 and 1117**
- threat object `Virus:DOS/EICAR_Test_File`, SeverityID 5, `IsActive False`
- file removed from disk

The detection and logging pipeline demonstrably works on this machine at this
moment. **The PUA silence is therefore real, not an artefact of a broken
pipeline.** This is the negative-then-positive control pattern applied to a
measurement rather than a fix, and without it §8.1 would be an unsupported
absence.

### 4.4 The `.vbs`

Executed cleanly. No block, no dialog, no SmartScreen prompt, no alert.
Consistent with Lab 06 having enabled only the WMI-persistence and PSExec/WMI
rules — `P90-4` confirmed. What the endpoint did not do, the cloud did: see §7.4.

---

## 5. Phase A′ — the perishable capture

`Initiate Automated Investigation` was triggered from the device page at
**17:18**. This is the capability retiring on 2026-09-01; the capture has 22 days
of margin and is unrepeatable afterwards.

**Investigation #2**, *'EICAR_Test_File' malware was prevented*, detection source
Antivirus, category Malware, severity Informational.

Scale of a single automated investigation on one quiet lab client:

| Entity class | Count |
|---|---|
| Files | 1,516 |
| Persistence methods | 277 |
| Services | 295 |
| Drivers | 439 |
| Processes | 173 |
| IP addresses | 13 |
| **Total analysed** | **2,713** |
| Malicious | 1 |
| Remediated | 1 |

**30 log steps**, two of them `Skipped`. The skip semantics are visible in the
step description: `Find files by name` is marked Skipped and describes
`Find 0 files…` — *nothing to do*, not *declined to run*.

The EICAR quarantine completed automatically: Action Center History records
Investigation ID 2, **File quarantine**, `c:\users\labuser\downloads\eicar.com`,
decided by **Microsoft Defender AV**, source **Automated device action**,
**Completed**, `ActionAutomationType: Automated Investigation`, `undo: undoable`.

---

## 6. Failures & Fixes — and three withdrawals

**P90-2 was falsified twice, for two different reasons, and this is the lab's
most useful accident.** The first attempt was made in Edge, which refused the
download. The second, by `Invoke-WebRequest`, succeeded. The prediction was
wrong both times, and the two failures are not the same failure.

**Withdrawn — the mixed-content diagnosis.** Edge's refusal
(`"PotentiallyUnwanted.exe can't be downloaded securely"`) was initially
diagnosed as an insecure-transport or mixed-content block. The URL is HTTPS
(`amtso.eicar.org`). The diagnosis was wrong and is withdrawn. What the message
means is unresolved on the evidence gathered; what Edge *did* is recorded in
§8.3 and stands on its own.

**Withdrawn — the empty Action Center reading.** The Pending tab's `0 items /
No actions found` was initially read as structurally correct under full
automation, citing the CSV export as confirmation. Wrong surface: the CSV was of
History, not Pending. Withdrawn.

**Withdrawn — and replaced by a narrower claim.** The replacement reading, that
the Action Center and the investigation graph *disagree* about pending actions,
was itself too strong. A second read hours later, with no filters set, showed
the item present and unchanged. The divergence was real and observed, but
**transient**. The surviving claim is in §8.7 and is smaller than the one it
replaces.

**Unfixed — the clipboard.** Restarting `rdpclip` did not restore clipboard
sharing. Native RDP shares the host clipboard with no UI and no fallback when
the bridge fails; Bastion has a clipboard panel because it tunnels through a
browser. This cost significant session time and is the practical argument for
Bastion on the next client-VM lab — pending `P89-10`, which may show the
Developer SKU bills nothing.

---

## 7. Phase C — the portal reads, at zero cost

Conducted with both VMs deallocated. Nothing in this phase required the machine.

**The pending quarantine was deliberately left unapproved and uncancelled**
throughout. It is evidence, and approving it would have destroyed the state
§8.6 and §8.7 depend on.

### 7.1 Navigation, as walked

`docs/navigation.md` row 33 already carried
*Incidents → (incident) → Investigations tab → (row)*, dated 2026-08-05, and it
is still correct. Re-verified 2026-08-10.

**New negative observation:** the `Investigation & response` subtree offers
`Incidents & alerts`, `Hunting`, `Actions & submissions` and `Partner catalog` —
and **no direct entry for automated investigations**. The investigation page is
reachable only through an incident or through Action center. Recorded as an
observation, not a conclusion about the 2026-09-01 consolidation, which it may or
may not prefigure.

### 7.2 Investigation #2, on the following day

| Field | Value |
|---|---|
| Status | `Running — Pending action` |
| Duration | 2:31h |
| Waiting for | 2:25h |
| Last completed analysis step | 5:25 PM |

Roughly ten minutes of work; everything after that is time spent waiting for a
human. See §8.7.

### 7.3 Alerts — two, and neither is the `.vbs`

| Alert | Category | Time |
|---|---|---|
| `'EICAR_Test_File' malware was prevented` | Malware | 5:14 PM |
| `Automated investigation started manually` | **Suspicious activity** | 5:18 PM |

The analyst's own response action is an alert, categorised as suspicious
activity, correlated into the same incident. Incident 27's exported
`Detection sources` field reads `Antivirus, Automated investigation` — the
response action is carried as a detection source.

### 7.4 The `.vbs`, found without being alerted on

No alert. It appears only as log steps:
`Read file "c:\users\labuser\desktop\test.vbs"` at 5:21 PM, followed by
`Analyze file contents using external services`, 3:19m.

Three tiers of visibility for one file: **not blocked, not alerted, collected
and analysed anyway.**

### 7.5 The file entity, and the VirusTotal pivot

The pivot is not a link out — VirusTotal is embedded in the entity flyout.

| Field | Value |
|---|---|
| VirusTotal detection ratio | **57/64** |
| Malware detected | `Virus:DOS/EICAR_Test_File` |
| Entity reputation | Malicious (100/100) |
| File size | 70 b, unsigned |
| Organization devices | **1** |
| Worldwide devices | **3,740** |
| First seen (organization) | 2026-08-10 5:14:48 PM |
| First seen (worldwide) | **2013-03-04 3:02:03 AM** |

`P91-2` confirmed on both limbs. The more useful observation is the **scope
split**: one flyout carries tenant-scoped and global-scoped counts for the same
object, each labelled. *New here, ancient everywhere* is a different triage story
from *new everywhere*, and this is the surface that distinguishes them.

The flyout renders SHA1, SHA256 and MD5 with copy buttons, and a
**`Download file`** action — an affordance to pull a known-malicious sample out
of the tenant. Noted, not used.

**Hygiene note.** EICAR's hashes are published global constants and are safe to
commit and safe to submit to third-party services. The same flyout on the PUA
entity renders *tenant* hashes, which are neither. The surface is identical; the
disclosure risk is not.

### 7.6 Attack story playback — attempted, nothing to observe

The play control on the incident's Attack story tab produced no animation in the
incident graph; it revealed a row of transport controls and re-rendered the alert
list. Two alerts four minutes apart, two nodes, one of them an analyst action.

**Not recorded as a finding.** A playback feature given nothing to play back is a
statement about this lab's telemetry, not about the product. Recorded here so the
attempt is on the record and is not repeated.

---

## 8. Findings

### 8.1 Audit mode produced no audit trail

`PUAProtection = 2` is documented as detect-and-log without blocking. On this
machine it logged nothing: no threat object, no 1116, no 1117, with real-time
protection, MAPS reporting and sample submission all on. The EICAR control
minutes later produced all three on the same machine in the same session.

Audit mode's only deliverable is the record. A blocking control that silently
fails still, sometimes, blocks. **An auditing control that silently fails
produces exactly the same evidence as an environment with nothing to audit.**

This is `configured ≠ effective` in its purest form yet recorded here: the
setting is present, is at a documented value, and the thing the value promises
did not happen. `POS-092`.

### 8.2 The cloud reached a verdict the endpoint never reached

The investigation's Evidence tab lists the PUA artefact as `f_000045`, verdict
**Malicious**, remediation status **Pending approval**, first seen 5:19 PM.

Its **detection origin is a log step** —
`Find recently created or modified executable files` — not an alert. The
artefact entered evidence through routine enumeration, not through detection.
The investigation found it by sweeping, not by being told.

Two engines, one file, opposite records: local silence, cloud verdict of
Malicious. And note the dependency — **without the EICAR test there would have
been no investigation, and without the investigation this file would still be
unrecorded on every surface.** The unrelated positive control is the only reason
the PUA finding exists at all.

`f_000045` is an Edge cache filename. The entity carries no original filename on
any surface.

### 8.3 A browser block that kept the whole file

Edge refused the download with
`"PotentiallyUnwanted.exe can't be downloaded securely"` and left the **complete
33 KB payload** on disk as an orphaned `.crdownload` in
`\appdata\local\microsoft\edge\`.

The block is of the *save*, not of the *transfer*. The bytes arrived and stayed.
This is the copy the cloud investigation later adjudicated Malicious — the
"blocked" file is the one still on the machine.

### 8.4 Three outcomes, indistinguishable at the console

At the browser, these look the same:

1. PUA protection blocks the file → **protected**
2. Edge blocks the save → **looks protected; PUA was never tested**
3. Audit mode allows it → **looks unprotected; actually detecting nothing**

AMTSO's own test logic — *if it downloads, your configuration is wrong* — cannot
separate them. Nor can the console: both `Invoke-WebRequest` calls returned
silently to the prompt, and only a corner toast differed.

A test whose pass condition is "the file did not appear" cannot distinguish a
working control from a different control from no control at all.

### 8.5 The manual trigger did not start the investigation

Four surfaces agree:

| Surface | Value |
|---|---|
| Incident, Attack story | `Creation time 5:15:41 PM` |
| Incident, Investigations tab | `Start date 5:15 PM`, `Triggering alert: 'EICAR_Test_File' malware was prevented`, `Detection source: DetectionEngine` |
| Investigation, Log tab | first executed step `Check machine coverage`, 5:15 PM; **no step corresponding to a manual trigger** |
| Incident export (CSV) | `Creation time 2026-08-11T00:15:41.230Z` |

The antivirus detection fired at 5:14:48. The incident and investigation were
created at 5:15:41 — **53 seconds later, automatically**. The manual click at
17:18 registered as its own alert at 5:18:30 and joined a run already in flight.

**The alert titled `Automated investigation started manually` names the analyst
action, not the cause of the investigation.** An operator reading that title on
the queue would conclude the investigation exists because a human asked for it.
On this evidence, it does not.

`P90-6` stands: the control was offered and it functioned. What it did was join,
not create.

### 8.6 Two Evidence tabs, two scopes, one omission

| Surface | Count | Contents |
|---|---|---|
| Incident → `Evidence and Response` | **1** | `eicar.com`, Malicious, **Prevented** |
| That incident's investigation → `Evidence` | **2** | `eicar.com` (Malicious, Prevented) **and** `f_000045` (Malicious, **Pending approval**) |

Same tab name, same position on the page, two different objects, two different
scopes. The incident's left rail confirms its own completeness —
`All evidence (1) / Files (1)` — so nothing signals an omission.

**The entity the narrower surface omits is the one still awaiting a human
decision.** An analyst working the incident as their unit of work sees one
malicious file, already prevented: a closed-looking picture, with an approval
outstanding on a second file that the same incident's own investigation
adjudicated Malicious.

The incident view is not wrong. It is narrower, and unlabelled.

### 8.7 The action lifecycle is poorly instrumented at both ends

Four observations that compose:

**Duration counts queue time.** `2:31h` at read, against a last completed
analysis step ten minutes after start. An investigation whose approval waits
three days will report a duration of three days. The field measures elapsed wall
time, not work.

**A pending action has no creation time.** The Pending actions tab renders
`File created date` — a property of the *file*. The Log tab's pending row renders
no execution start time. The only absolute anchor anywhere is the Action
Center's `Action update time` (5:22 PM), which is not labelled as a creation
time and should not be recorded as one.

**A completed action has no end time.** The Action Center CSV export carries
`ActionStatus: Completed` with an empty `EndTime`.

**A transient null on the approval queue.** The Pending tab read
`0 items / No actions found` while the investigation rendered
`Pending actions (1)`. A re-read hours later, no filters set, showed the item
present and unchanged. Propagation, not permanent divergence — and operationally
the same problem either way: an analyst working the Action Center as their queue
sees nothing to approve while an approval is pending elsewhere, and a transient
null is indistinguishable from an empty queue.

One state also carries three labels: `Pending action` (investigation header),
`Pending approval` (Investigations list), `Pending` (Action Center).

### 8.8 Absences and renderings, confirmed on two reads

**Copilot pane — absent.** No pane on the incident page, no entry in the
command bar, no icon in the portal's global toolbar. Two reads, incident flyout
and full incident page. Capacity was torn down at MOD-88 (Lab 20); the surface
renders normally and the pane is not on it. `P91-1` confirmed.

**Greyed ≠ state-dependent.** `Action center` and `Policy sync` in the device
`···` menu were greyed with the VM off **and** greyed with the VM running, an
EICAR remediation complete and an investigation in flight. Two reads,
hypothesis not supported.

**Truncation is data, not display.** `LAB-WIN11-DEFEN` — 15 characters —
appears on
six surfaces: the device page, the alert queue's Impacted assets column, the
investigation graph's device node, the Pending actions tab, the incident
flyout, and the **Action Center CSV export**. The export is machine-readable;
it is not rendering a display name, it is carrying the truncated value as data.
`P90-5` confirmed and extended: at minimum, this is the device identity MDE
holds. Cf. `POS-033` for the separately measured server-hostname truncation —
that one is natural NetBIOS truncation of a 19-character name, and this client
placeholder is a synthetic evidence-preserving alias per `SANITIZATION.md` §2,
not evidence of the same mechanism.

**UTC and local, one labelled.** The VM clock runs UTC; the portal renders
Pacific. The Action Center CSV export renders UTC
(`08/11/2026 00:15:44`) while the pane renders local
(`Aug 10, 2026 5:15 PM`) — the same event, two renderings, one of them labelled.
The incident export carries explicit `Z` suffixes; the pane carries none.

### 8.9 Least privilege, discovered incidentally

On an Entra-joined device the Entra user is a **standard user**; the local
account holds administrator. Correct least-privilege shape — and it means the
natural RDP identity cannot alter Defender settings. `Set-MpPreference` on
`PUAProtection` would have required a `labadmin` session, which is why §4.1 is a
read.

---

## 9. Teardown, cost, and what did not stop

RDP disconnected, VM stopped. **Two reads** of the deallocation state, per the
MOD-84 precedent that IP hours have billed against machines the portal reported
stopped:

**Read 1** — Azure portal, Virtual machines list: both `LAB-SRV-DEFENDER-01` and
`LAB-WIN11-01` `Stopped (deallocated)`. The Win11 row still renders a public IP
address.

**Read 2** — the public IP resource itself (`LAB-WIN11-01-ip` → Overview →
Essentials), which is the probative surface:

| Field | Value |
|---|---|
| SKU | **Standard** |
| Tier | Regional |
| Assignment | **Static** |
| Associated to | the VM's NIC |

**Standard + Static bills continuously for as long as the resource exists**,
regardless of VM state. Deallocating stopped compute; it did not stop the IP
meter. Approximately **$0.005/hr — ~$0.12/day, ~$3.65/month.**

This is MOD-84's mechanism, and this time it was caught **from configuration
before the invoice** rather than inferred from billing afterwards. `POS-094`.

The 2026-08-12 cost read should show the Standard static public IP meter
accruing continuously across the 08-10 boundary, independent of the 68-minute
compute window. A decision follows from that read and is deliberately deferred
to it: keep the IP for direct-RDP convenience at ~$3.65/month, or delete it and
move this VM to Bastion — which is only clearly cheaper if `P89-10` confirms the
Developer SKU bills nothing.

**Read taken 2026-08-12; both questions resolved.** The IP meter billed
**$0.12/day on 29 of 29 days** from creation on 07-15, while the compute meter
appears on only **9** of them — twenty days of charge with no VM running.
$3.40 accrued. `P89-10` confirmed: the Developer SKU emits no meter rows at all.

**The decision went the other way from the cost logic, deliberately.** The IP is
**retained** through the 2026-09-14 E5 window and reassessed at teardown.
Remaining exposure is ~$4; deleting the resource would convert `POS-019` and
`POS-020` from currently observable state into historical findings needing a
state-transition annotation. The network architecture is not changed mid-project
for $4. `POS-094`, `POS-099`.

**Metered window:** 16:25 → 17:33, **68 minutes**, `LAB-WIN11-01` compute only,
no Bastion.

**Left in place deliberately:** the pending PUA quarantine on Investigation #2,
unapproved and uncancelled. It is the evidence §8.6 and §8.7 rest on.

---

## 10. References

- `POS-092` — PUA protection audit mode without an audit trail
- `POS-093` — Defender for Endpoint AIR, pre-retirement state
- `POS-094` — Standard static public IP billing past VM deallocation
- `POS-033` — hostname truncation
- `POS-019`, `POS-020` — RDP exposure on this VM
- Divergence rows **173–183**
- `lessons/MOD-90-endpoint-prevention-controls.md`,
  `lessons/MOD-91-investigating-endpoint-detections.md`
- Lab 03 (EDR detection test), Lab 06 (ASR), Lab 13 (**MDO** AIR — unaffected by
  the 2026-09-01 change), Lab 17 (incident workflow), Lab 20 (Copilot capacity
  teardown, MOD-88)
- Message center **MC1411577**; four Microsoft Learn pages, verified 2026-08-10
