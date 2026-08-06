# Lab 03 — Endpoint Onboarding and First Alerts

| Field | Value |
|---|---|
| **Domain** | Configure protections and detections |
| **Objectives** | Onboard a Windows endpoint to Defender for Endpoint; verify sensor health and telemetry; observe the detection→alert→incident chain |
| **Depends on** | Lab 00, Lab 01, Lab 02 |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-18 |

---

## 1. Objective

Give the SOC its first endpoint. Onboarding installs and activates the Defender
for Endpoint sensor on `LAB-WIN11-01`, which is what turns a device that merely
*exists* in the directory into one that *emits* — process events, registry
changes, network connections, and the behavioural signals detections are built
on. Before this lab the `Device*` advanced-hunting tables are empty; after it,
they are the data plane every later lab reads from.

Onboarding is deliberately separate from Lab 01's enrolment. Enrolment is
*management* authority (policy, compliance); onboarding is *telemetry*. They
travel different paths and, in this environment, only one of them works —
`POS-022` records that Intune enrolment never fires, so the scalable
Intune-driven onboarding path (module 26) is foreclosed and the local-script
path is the only one available. That is not a preference. See §2.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Onboarding method | **Local script** | Intune EDR policy (module 26); Group Policy | The Intune path requires an Intune-enrolled device. `POS-022`: enrolment never fires here, so it is structurally unavailable — see the foreclosure table below. GPO requires AD-join; this is Entra-only. Local script is what remains. |
| Elevation for the script | **Azure Run Command as SYSTEM — *attempted, unavailable*** → fell back to interactive `labadmin` via Bastion | RDP as `labadmin` (guide's method) | SYSTEM was chosen to keep an interactive privileged session off the endpoint (`POS-021`). Run Command and the VMAccess extension both hang without completing on this VM despite a Ready agent (`POS-028`), so SYSTEM was **not available**. The interactive `labadmin` path was forced, not preferred — and `labadmin` is the RID-500 local admin `POS-025` flags. |
| Connectivity type | **Streamlined** | Standard | Default since 2024-05-08; consolidates service URLs under one domain. The VM has unrestricted egress, so either works; the choice is recorded and verified applied (`DeviceInfo.ConnectivityType`). |
| Detection validation | **Microsoft's built-in detection test** | Wait for organic activity | A synthetic, benign trigger produces a known, timeable signal. Organic activity on a lab VM is sparse and unpredictable. |

### Module 26 (Intune mass onboarding) — foreclosed, with the chain that breaks it

The scalable pattern chains three independent layers. This environment breaks
the chain at all three, each break already a verified posture entry:

| Guide layer | Requirement | This environment |
|---|---|---|
| **1. Entra → Intune auto-enrolment** | Device auto-enrols on first sign-in | ❌ `POS-022` — every precondition verified, enrolment never attempted |
| **2. Intune ↔ Defender connector** | Service-to-service link exchanges packages and risk | ✅ works — `POS-009`, `POS-010` On |
| **3. Onboarding policy → device** | Assigned EDR policy pushes the package | ⛔ moot — no enrolled device to target; and device-risk→compliance is off (`POS-011`) |

Fixing layer 1 alone would not produce a working control: the risk-back path
(`POS-011`) is independently off, and `POS-018` (no vTPM) means the device could
not satisfy a risk/attestation check even if it reached one. Three independent
breaks. The local-script method is the only structurally available onboarding
path in this tenant, and module 26 is documented rather than executed.

## 3. Build

Portal step (paths change; recorded as portal-only):
`security.microsoft.com` → System → Settings → Endpoints → Onboarding →
OS **Windows 10 and 11** → Connectivity **Streamlined** → Deployment method
**Local script** → **Download onboarding package**.

The package extracts to `WindowsDefenderATPLocalOnboardingScript.cmd`. It was
run in an elevated context on the device (see §6 for how that context was
obtained). The script self-checks for administrative privilege, performs the
onboarding operations, and starts the SENSE service:

```
Starting Microsoft Defender for Endpoint onboarding process...
Testing administrator privileges
Script is running with sufficient privileges
Performing onboarding operations
Starting the service, if not already running
Finished performing onboarding operations
Waiting for the service to start
Successfully onboarded machine to Microsoft Defender for Endpoint
```

That final line is **T0** for the latency measurements in §4.

**Do not repackage the onboarding package** — repackaging is unsupported, can
trigger tamper alerts, and breaks updates.

The hunting queries used to validate this build are stored under
[`kql/advanced-hunting/`](../../kql/advanced-hunting/) rather than inlined here.

## 4. Validation

A capability that has not emitted a verifiable signal is not built. Every row
below was observed, not assumed.

| Check | Method | Expected | Result |
|---|---|---|---|
| Device in inventory | Defender → Assets → Devices | Appears after onboard | ✅ `LAB-WIN11-01`, AAD-joined, Workstation |
| Sensor streaming | `DeviceEvents` returns rows | Non-empty | ✅ 72 events in first ~14 min |
| Connectivity applied | `DeviceInfo.ConnectivityType` | Streamlined | ✅ Streamlined; OnboardingStatus Onboarded |
| Attribution | `AccountName` on process events | The account that acted | ✅ `labadmin` on the test process |
| Detection→alert→incident | Run detection test, watch Incidents | Alert, correlated to an incident | ✅ "Suspicious PowerShell command line" (Medium), grouped into "Execution incident on one endpoint" (priority 35) |
| **Device-side onboard** (module 27) | `Get-ItemProperty ...\Windows Advanced Threat Protection\Status` in `labadmin`'s session | `OnboardingState = 1` | ✅ `OnboardingState 1`; `OrgId` populated (correct tenant — value not reproduced) |
| **Defender AV mode** | `Get-MpComputerStatus` → `AMRunningMode` | Normal (AV primary, no third-party) | ✅ **Normal**, `AntivirusEnabled True` — matters for module 33 ASR enforcement |
| **ATT&CK mapping** (module 30) | Incident → alert summary | A technique, Defender-assigned | ✅ **`T1059.001` PowerShell** (Execution) — first *observed* coverage, tracked as `DET-001` |
| **Investigation surface** | Incident graph + Process tree + Alert timeline | Full Plan 2 experience | ✅ Full graph, complete process lineage — **Plan 2 confirmed active** (E5) |
| **Remediation actions logged** *(added 2026-07-27)* | Action center → History | *(expected ≥1)* | ⚠️ **"No actions found"** — investigation ran, nothing was remediable. See §7 |

### The four latencies — measured, against vendor expectations

All times normalised to **UTC** (see the timestamp trap in §7 — this was not
trivial and got it wrong once before it got it right).

| Latency | Vendor number | Measured |
|---|---|---|
| Onboard → device in inventory | 5–30 min (module 25 guide); ~10 min (guide 3) | **~2 min** |
| Onboard → first telemetry ingested | not stated | **~3.5 min** (FirstEvent 08:30:16 → FirstIngest 08:33:52) |
| Detection test → alert visible | "a few minutes" | **~2 min** |

Every measured latency is at or under the vendor floor. **These are the finding
of this lab** — the numbers Microsoft's documentation cannot give, because they
are this tenant's, on this date. The vendor ranges are recorded beside them so
the comparison is legible; they are not the result.

## 5. Evidence

Sanitised per `SANITIZATION.md`. Device name normalised to `LAB-WIN11-01`
throughout; object IDs, tenant ID, and the onboarding blob are never reproduced.

Telemetry window on first onboard: FirstEvent `08:30:16Z`, FirstIngest
`08:33:52Z`, LastEvent `08:44:02Z`, 72 events. Event→ingest gap ~3.5 min,
consistent across rows — a live stream, not a backfill (confirmed by comparing
`Timestamp` against `ingestion_time()`; see §7).

Alerts raised (both EDR detection source, both attributed to `labadmin`):
one **Medium** "Suspicious PowerShell command line", one **Informational**,
same asset, correlated into a single incident. No automated attack disruption
fired — correct for a Medium synthetic test; the platform chose not to contain.

## 6. Failures & Fixes

The failure path is kept because it transfers. One item here is a durable
property of the environment; the rest were incident noise and are omitted per
the project's rule that only reproducible constraints are documented.

**Durable — Run Command / VMAccess do not service extensions on this VM.**
Both the intended SYSTEM onboarding and a later password-reset attempt hung
indefinitely (`InProgress`, never completing) while the VM's guest agent
reported **Ready 2.7.41491.1216** and control-plane reads returned instantly.
A Ready agent is not evidence the extension channel works — the same shape as
`POS-011`'s "Available". Recorded as `POS-028`. The practical consequence:
the SYSTEM elevation path for onboarding was unavailable, forcing the
interactive `labadmin` route via Azure Bastion, which is itself the documented
divergence in §2 and the divergence table in `configuration-inventory.md`.

Bastion note: the Developer SKU rejects `domain\username` / `.\username`
format in its portal fields; the local account is entered as bare `labadmin`.

## 7. Analysis

**Onboarding is telemetry, not management, and the distinction is load-bearing.**
`LAB-WIN11-01` is now watched but still ungoverned: it emits everything and
obeys nothing, because enrolment (`POS-022`) never gave Intune authority over
it. An analyst inheriting this environment sees a fully reporting endpoint and
could reasonably assume it is managed. It is not. Visibility and control arrived
by different paths and only one of them completed.

**The timestamp trap — `DeviceEvents`/`DeviceInfo` render in the portal's
configured timezone, and latency computed against a local wall-clock reads
wildly wrong until converted.** During this lab an apparent 14-hour gap between
event time and onboarding time was read as evidence of a "backfill" of
pre-onboarding history. It was not: `ingestion_time()` compared against
`Timestamp` showed a consistent ~3.5-minute gap — a live stream. The 14 hours
was purely a UTC-vs-local display artifact. **Confirm the portal timezone before
computing any latency**, and prefer `ingestion_time()` over `Timestamp` when the
question is "when did MDE receive this," because `Timestamp` answers "when did it
happen on the device" — an adjacent question the column name does not warn you
about. Added to the diagnostic traps register.

**The sensor backfills nothing but attributes everything.** First telemetry
included routine pre-existing device activity (Defender platform scheduled
tasks, memory-protection API calls) captured live as the sensor came online,
each correctly attributed to an account and process lineage. The synthetic test
was captured with `labadmin` as the actor — the attribution chain that makes
endpoint telemetry worth having.

**A benign-but-suspicious pattern surfaced in the first minutes and is worth
allowlisting in any hunt built on this data:** `senseir.exe` (the MDE
live-response / automated-investigation sensor) invoking signed PowerShell as
SYSTEM from a `DataCollection` path. It looks like PowerShell abuse and is not;
the discriminators are the `senseir.exe` parent, the `system` account, and the
`AllSigned` execution policy. Recorded so a later detection does not fire on
Defender investigating itself.

**On the detection test itself:** it triggers EDR by running hidden PowerShell
that attempts a `WebClient` download of a benign file from localhost and
executes it — a deliberate imitation of a dropper, harmless because the source
is `127.0.0.1` and nothing is served. Per this project's no-malicious-code rule
the command is **not reproduced** in this repository; the mechanism is described
here and the canonical command lives in Microsoft's documentation (§8). It maps
to the same behavioural signals a SIEM hunt would flag — hidden window,
execution-policy bypass, download-and-execute — which is why it fires cleanly.

**Verified from the device, not just the cloud (module 27).** Everything above
is cloud-side (portal, hunting). The onboard was also confirmed from the box
itself: the registry `Status\OnboardingState` reads `1` and `OrgId` is populated
with this tenant's ID, proving the sensor installed, registered, and joined the
*correct* tenant — a device-onboarded-to-the-wrong-tenant would show a different
`OrgId`. Read in `labadmin`'s interactive session, deliberately **not** via Run
Command / SYSTEM: `POS-028` makes Run Command unavailable here anyway, and the
`dsregcmd` trap (SSO state is per-user; SYSTEM reports falsely) means device
identity reads must run in the user's session regardless.

A small trap surfaced doing this: **`OnboardingState` exists in two places and
they disagree.** The registry `Status\OnboardingState` read `1`; the same-named
field from `Get-MpComputerStatus` was blank on this confirmed-onboarded device.
The registry value is authoritative; the cmdlet's onboarding field is
AV-centric and unreliable. Same name, two sources, no warning which to trust —
added to the diagnostic traps register.

**Walking the incident (module 30) turned the synthetic alert into the first
observed ATT&CK coverage.** Defender mapped it to `T1059.001` (PowerShell,
under Execution) and reconstructed the full process lineage from logon shell
(`userinit.exe → explorer.exe → cmd.exe → powershell.exe`) down to the script.
Two alerts correlated into one incident with the visible reason **"same user
credentials"** — the behavioural Medium detection and an Informational
`[Test Alert]` where Defender additionally *fingerprinted the known test*, so
the sensor both detects the behaviour and recognises the specific sanctioned
string. The full incident graph, process tree, and timeline all rendered,
confirming the **Plan 2** investigation surface is active on this E5 tenant
(resolving whether the mid-course vulnerability-licence activation had left the
tenant on a reduced surface — it had not). This detection is tracked as
`DET-001`; `docs/attack-coverage.md` now shows `T1059.001` as observed rather
than planned.

**The Evidence tab auto-extracted four IOCs and mis-verdicted one — a real
false-positive class.** Defender pulled `cmd.exe`, `powershell.exe`, the
download URL, and the IP `127.0.0.1` from the incident, each marked *Suspicious*.
Loopback cannot be attacker infrastructure; it was flagged only for appearing in
a malicious-looking download. Any indicator pipeline that auto-promotes
extracted "suspicious" IPs to block indicators would need to exclude loopback
and RFC 1918 — the same false-positive family as the `senseir.exe`
benign-PowerShell pattern, and now the first concrete case. Captured in
`DET-001` §5.

**The endpoint watches the operator too.** The process tree captured the
investigator's own later commands — a `tzutil.exe /g` run while diagnosing the
timezone trap appears in the timeline as its own script event. Harmless, but a
reminder that once a device is onboarded, *everything* done on it as any account
is telemetry, including the work of investigating it — the same lesson as the
`senseir.exe` self-collection pattern.

**An alert is not an action — the Action Center is empty, correctly** *(observed
2026-07-27, during module 53).* `Action center → History` reads **"No actions
found"** for this detection, and that is not a fault. An automated investigation
demonstrably *did* run: the `senseir.exe` self-collection above is AIR gathering
evidence in the first minutes. The device sat under **Full** automation
(`POS-030`; Microsoft Learn also confirms new tenants default to full
automation). Both preconditions the documentation names were met.

Nothing was remediable. Match the detection against the supported remediation
actions — quarantine a file, remove a registry key, stop a service, disable a
driver, remove a scheduled task, isolate/contain/restrict a device — and none has
an object to act on. The test attempts a `WebClient` download from `127.0.0.1`
where nothing is served: no file lands, no persistence is written, nothing runs
that could be stopped. The behaviour was detected; there was nothing to undo.
(Defender additionally fingerprinted the sanctioned test string — the
Informational `[Test Alert]` in §5 — which plausibly contributes, but the
structural explanation stands without it.)

This matters because the standard troubleshooting for an empty Action Center
gives two causes, both misconfigurations: submitted-item analysis has not
returned, or the device group is set to *No automated response*. Neither
applies here, and following that list would send an analyst hunting a fault
that does not exist. A third cause belongs on it: **the detection produced no
remediable artifact.**

`POS-011` reads a healthy status over a dead control. This is the mirror — a
legitimately empty surface that the documentation teaches you to read as a
fault. Detection coverage and remediation coverage are separate measurements,
and this repo's `docs/attack-coverage.md` measures only the first.

**And nothing would have told anyone.** `POS-042`: Defender XDR ships with **no
email notification rules at all** — Incidents, Actions and Threat analytics tabs
are all empty. The incident this lab produced on 07-18 sat in the queue until
someone looked. Meanwhile this project's Azure *budget* alert path is verified
working: an alert fired and was received. The cost control notifies; the security
controls do not, and both are defaults rather than decisions.

Worth recording while it is still observable: AIR ceases to be a separate,
manually-triggerable investigation experience for Defender for Endpoint on
**2026-09-01** (Microsoft Learn; Defender for Office 365 AIR is unaffected).
This tenant expires **2026-09-14** (extended once on 2026-08-06 from 2026-08-13,
`POS-077`), so everything above is necessarily a pre-retirement observation and
cannot be re-checked here against the after-state. The extension does not change
that: 2026-09-01 still falls inside the tenant's life, so the retirement itself
is now *observable* here where it previously was not — but the after-state window
is a fortnight, and no second onboarded device exists to observe it with.

## 8. References

- Microsoft Learn — Onboard Windows devices using a local script
- Microsoft Learn — Run a detection test on a newly onboarded device
- Microsoft Learn — Onboarding using Microsoft Intune (module 26 path)
- `POS-022`, `POS-011`, `POS-018`, `POS-021`, `POS-025`, `POS-028`, `POS-029`
