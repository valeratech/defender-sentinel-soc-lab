# Lab 06 — Attack Surface Reduction Rules

| Field | Value |
|---|---|
| **Domain** | Configure protections and detections |
| **Objectives** | Configure ASR rules; demonstrate audit vs block on one rule; measure trip→telemetry latency; confirm across CLI, hunting, timeline, and the ASR report |
| **Depends on** | Lab 03 (onboarded sensor, AV mode), Lab 05 (remediation level) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-19 |

---

## 1. Objective

Add behavioural blocking to the endpoint. ASR rules watch for the *techniques*
attackers reuse — Office spawning children, WMI creating processes, credential
theft patterns — and either **audit** (log, allow) or **block** (log, stop) them.
This lab configures two rules, demonstrates the audit-vs-block distinction on a
single rule with an identical trigger, measures how fast the events reach the
cloud, and — the part that matters most — confirms where that activity is and is
**not** visible in the Defender consoles. *(§7 amended 2026-07-27: it is not one
console but two, and they disagree.)*

The lab is only safe to run because of two earlier findings: Defender AV is in
**Normal** mode (Lab 03 §4 — ASR does nothing in passive mode), and the device is
on **Semi** remediation (Lab 05 — a block will not be auto-quarantined before it
can be observed). Both were preconditions, established labs ago, that this lab
depends on.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Deployment method | **Local PowerShell (`Add-MpPreference`)** | Intune ASR policy; Group Policy; **MDE security settings management** | Intune requires an enrolled device — `POS-022`, enrolment never fires. GPO requires AD; this tenant is Entra-only. ~~PowerShell is the only available path.~~ **Corrected 2026-07-27 (`POS-041`): a third path existed and was not checked** — MDE security settings management enforces configuration on devices *not enrolled in Intune*, and was simply switched off. The door was closed, not absent. This choice has a consequence the console makes visible — see §7. |
| Elevation | **Bastion as `labadmin`** | Run Command as SYSTEM | Run Command does not service extensions on this VM (`POS-028`). Same forced-local path as onboarding. |
| Rules chosen | **WMI persistence (block); PSExec/WMI process-creation (block)** | Office-child-process rules | The Office rules need Office installed; this VM has none (`Get-AppxPackage *office*` empty). The two WMI rules need nothing installed and are triggerable benignly. |
| Test approach | **One rule, identical trigger, audit then block** | Trigger two different rules | Changing only the rule *state* between two runs of the same command isolates the audit-vs-block difference to a single variable — the cleanest possible demonstration. |

## 3. Build

Set in an elevated `labadmin` session (Bastion). `Add-MpPreference` **appends** to
the ASR rule set; `Set-MpPreference` would **replace** it — using `Set` twice
silently discards the first rule. Append is correct for building a rule set.

```powershell
Add-MpPreference -AttackSurfaceReductionRules_Ids e6db77e5-3df2-4cf1-b95a-636979351e5b -AttackSurfaceReductionRules_Actions Enabled   # WMI persistence -> Block
Add-MpPreference -AttackSurfaceReductionRules_Ids d1e49aac-8f56-4280-b9ba-993a6d77406c -AttackSurfaceReductionRules_Actions Enabled   # PSExec/WMI      -> Block
```

**Verify by positional pairing, never by entry order** (see §7 trap):

```powershell
$asr = Get-MpPreference
for ($i=0; $i -lt $asr.AttackSurfaceReductionRules_Ids.Count; $i++) {
  "{0} = {1}" -f $asr.AttackSurfaceReductionRules_Ids[$i], $asr.AttackSurfaceReductionRules_Actions[$i]
}
# d1e49aac... = 1   (Block)
# e6db77e5... = 1   (Block)
```

Action codes: `0` disabled · `1` block · `2` audit · `6` warn.

End state: **both rules Block (1).** Audit was demonstrated during testing (below);
either rule can be flipped to `AuditMode` later — noted so the register and the box
stay in sync.

Hunting queries: [`kql/advanced-hunting/asr-audit-vs-block.kql`](../../kql/advanced-hunting/asr-audit-vs-block.kql).

## 4. Validation

The audit-vs-block distinction, demonstrated on **one rule** (`d1e49aac`) with an
**identical trigger** (a benign WMI process-create that opens Notepad — the exact
pattern the PSExec/WMI rule watches), run once in each state:

| | Audit run | Block run |
|---|---|---|
| `Invoke-CimMethod` ReturnValue | `0` (success) | `2` (access denied) |
| Notepad | **opened** | **did not open** |
| User-visible | nothing (silent) | **block notification** |
| Local event (Defender Operational log) | **1122** (audited) | **1121** (blocked) |
| Cloud `ActionType` (`DeviceEvents`) | `AsrPsexecWmiChildProcessAudited` | `AsrPsexecWmiChildProcessBlocked` |

Both local event IDs coexist in one query, minutes apart, same rule — the only
durable difference is the ID. Both cloud ActionTypes coexist in one `DeviceEvents`
query — the only difference is the `Audited`/`Blocked` suffix.

### Latency

| Secure Score credit *(added 2026-07-27)* | Both rules **Completed, 9/9**, with the 0/9 → 9/9 transition logged on this lab's build date — see the §7 amendment |

| Latency | Measured |
|---|---|
| Trigger → local event log | seconds (near-instant) |
| Trigger → cloud `DeviceEvents` | same-second (UTC-adjusted) |

Security-relevant ASR events reach the cloud far faster than routine device
telemetry (which took ~3.5 min at onboarding, Lab 03). The pipeline prioritises
them. Note: local and cloud timestamps appear ~offset hours apart until the
UTC-vs-local display is reconciled — the timestamp trap, seen a fourth time
(`configuration-inventory.md`).

## 5. Evidence

Device timeline reconstructed the block with MITRE mapping, in sequence:

```
powershell.exe executed WMI ExecMethod for Win32_Process     [T1047 WMI]
WmiPrvSE.exe was blocked by the attack surface reduction rule [T1047 WMI]
WmiPrvSE.exe created a thread remotely inside notepad.exe     [T1055.001 injection]  (blocked at this stage)
```

Defender mapped the benign test to **T1047 (Windows Management Instrumentation)** —
a second *observed* technique for the coverage matrix (`DET-002`), the block landing
at the remote-thread-creation step.

Two incidental observations from the same timeline, both benign-self-activity worth
allowlisting in future hunts: `taskhost.exe attempted to decrypt/encrypt
credentials [T1555.003]` (Defender's own automated investigation), and repeated
connections to `168.63.129.16` (the Azure platform WireServer — the fabric that
device discovery in `configuration-inventory.md` never surfaces as a device).

## 6. Failures & Fixes

No configuration failure. The forced-local deployment path (§2) is the only
constraint, and it is environmental (`POS-022` + `POS-028`), not a fault.

## 7. Analysis

**The headline finding: the Defender ASR console cannot see locally-set rules, and
reports the device as unprotected while it actively blocks.** The Configuration tab
of the ASR report showed this device as **"Rules off"** — 0 in block mode, 0 in
audit, 18 turned off — including the two rules that were, at that moment, blocking a
live trigger. The Detections report showed **0 audited, 0 blocked** with all filters
set to Any. Yet Advanced hunting, the device timeline, and the local event log all
carried the events.

The cause is scope, not lag or filtering: **the ASR report is built around
policy-managed rules** (Intune / MDM — the console's own "Add to policy" button is
the intended path). Rules set locally with `Add-MpPreference` enforce on the
endpoint but are invisible to **that report's** configuration and detection views.
An analyst reviewing that dashboard would conclude the endpoint is unprotected and
re-deploy — while protection is already running.

### Amended 2026-07-27 — it is two consoles, and they disagree

This section originally said locally-set rules are "invisible to the console."
**That was too broad, and it is disproved by counterexample.** Microsoft Secure
Score is a Defender console, names Defender for Endpoint as its product, and shows
both rules **Completed at 9/9 points**. Its history recorded the transition:

| Date | Secure Score entry | Points |
|---|---|---|
| 07-18 | *Block process creations originating from PSExec and WMI* — **has become relevant** | 0/9 |
| 07-18 | *Block persistence through WMI event subscription* — **has become relevant** | 0/9 |
| **07-19** | *points gained by **completing** Block process creations…* — **Great work!** | **9/9** |
| **07-19** | *points gained by **completing** Block persistence…* — **Great work!** | **9/9** |

07-19 is the day this lab was built. Secure Score watched the rules go on and
credited them the same day. Tamper Protection behaved identically — 0/8 on 07-18,
8/8 on 07-19.

**That transition also settles scope-vs-lag by elimination.** If the configuration
had never reached the Defender cloud, Secure Score could not have logged it
changing. The ASR report's blindness is therefore a property of that report's
scope, not of data availability — which is what this section claimed, now
established rather than inferred, and by a different route than the two checks that
were pending.

**The corrected finding is stronger than the original.** Not one console blind to a
local rule, but **two consoles in the same product, reading the same configuration,
disagreeing completely** — one reporting 18 rules off and zero in block, the other
awarding full points and timestamping the moment they were set. An analyst cannot
tell which is right without going to the endpoint.

*Caveat:* Secure Score read Completed on 2026-07-27 with both VMs deallocated, so it
reports last-known configuration rather than live state.

### Corrected 2026-07-27 — the foreclosure was incomplete

§2 recorded local PowerShell as *the only available path* for deploying these rules.
**That was asserted, not verified, and it is wrong.** Settings → Endpoints →
Configuration management → **Enforcement scope** offers MDE security settings
management, which the portal describes as applying "to devices that are not yet
enrolled to Intune" — precisely this tenant's situation. It is **off**, and off is
the shipped default (`POS-041`). Nobody tried it.

The consequence is larger than a rationale. Policy-deployed ASR rules are exactly
the class the ASR report can see. **So the headline finding above exists because a
switch was off and openable, not because a path was closed.** A different starting
configuration would have produced a different lab and, quite possibly, no finding at
all. The finding itself stands — everything observed on 07-19 remains true — but its
*cause* is one layer further back than this section originally claimed.

Untested deliberately: enforcing policy needs a device that can check in, and both
VMs are deallocated. When tested, it is a direct test of this section's mechanism —
deploy the same two rules as policy and see whether the ASR report begins reporting
them. Note in advance that policy-managed ASR may conflict with the locally-set
rules already present on the endpoint.
*(pending — MDE security settings management path untested; `POS-041`)*

This is the most consequential instance of the repository's recurring pattern
(configured-vs-effective, `POS-011`), and it is a **direct downstream consequence of
`POS-022`**: because Intune enrolment never fires, the only available way to set ASR
here is local PowerShell — precisely the way the reporting UI cannot see. A defect
found in Lab 01 silently determines the visibility of every ASR rule set in Lab 06.

**ASR blocks are recorded as telemetry, not raised as alerts.** Neither the audit
nor the block appeared in Incidents & Alerts — that queue held only Lab 03's
detection-test alerts. A successful block is treated as resolved (the defence did
its job; nothing to escalate), so it lands in the timeline and `DeviceEvents` but
does not page anyone. This is *recorded vs surfaced* — a cousin of configured vs
effective. Where to look depends on the question:

| Question | Surface |
|---|---|
| Is something attacking this box that needs attention? | Incidents & Alerts |
| What happened on this device, step by step? | Device timeline |
| Is ASR firing, and how often? | Advanced hunting *(the ASR report has the blind spot above)* |
| Hunt a pattern across devices? | Advanced hunting (`DeviceEvents`) |

An analyst who watches only the alert queue misses ASR activity entirely — blocks
and audits both stay silent there.

**Two PowerShell literacy traps, both `POS-011`-family at the tool layer:**

- **`Get-MpPreference` does not return ASR rules in entry order.** The `_Ids` and
  `_Actions` arrays are index-aligned *to each other* but not to the order you added
  them. Reading actions in entry order inverts every rule's state — Block reads as
  Audit. State must be confirmed by positional pairing within the returned arrays.
- **Audit is invisible from the endpoint.** In audit mode the action succeeds and no
  user-facing signal appears; only telemetry knows. "The rule fired" and "the action
  was stopped" are independent facts — the first was true, the second false, and
  nothing on the box said so.

**Preconditions that paid off:** AV Normal mode (Lab 03) made the rules enforce
rather than silently no-op; Semi remediation (Lab 05) kept the block from being
auto-quarantined mid-observation. Two earlier decisions became this lab's
foundations — the register compounding.

## 8. References

- `POS-031` (this ruleset + the reporting finding), `POS-022` (the root that forces
  local deployment), `POS-028` (Run Command), `POS-011` (the configured-vs-effective
  family)
- `DET-002` — T1047 observed via the ASR block
- Microsoft Learn — Attack surface reduction rules reference
- Microsoft Learn — Enable ASR rules with PowerShell
