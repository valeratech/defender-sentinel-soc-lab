---
# Machine-readable header — consumed by scripts/build-attack-matrix.py
id: DET-002
name: ASR — process creation via PSExec/WMI (audit and block observed)
status: active
platform: defender-xdr
rule_type: custom-detection
severity: medium
tactics:
  - TA0002
techniques:
  - T1047
data_sources:
  - DeviceEvents
  - DeviceProcessEvents
validated: true
---

# DET-002 — ASR: process creation via PSExec/WMI

The Microsoft-defined ASR rule "Block process creations originating from PSExec and
WMI commands" (`d1e49aac-8f56-4280-b9ba-993a6d77406c`), configured on this endpoint
in Lab 06. Recorded because it was **observed firing in both audit and block
states**, and Defender mapped the activity to `T1047` — the second observed ATT&CK
technique in this environment.

## 1. Hypothesis

> If a process is created via WMI (`Win32_Process.Create`), the PSExec/WMI ASR rule
> records a `DeviceEvents` row whose `ActionType` carries the rule's state as a
> suffix — `...Audited` when the rule audits, `...Blocked` when it blocks — and a
> local Defender Operational event (1122 audit / 1121 block).

Confirmed in both states.

## 2. Data Requirements

| Requirement | Value |
|---|---|
| Onboarded sensor, AV Normal | `POS-029`, Lab 03 §4 |
| Rule configured | `POS-031`, `d1e49aac...` |
| Tables | `DeviceEvents` (`ActionType startswith "Asr"`) |

## 3. Trigger

A benign WMI process-create (`Invoke-CimMethod Win32_Process Create` opening
Notepad) — the exact pattern the rule watches (T1047), with no malicious payload.

## 4. Validation — both states observed

| State | ReturnValue | Local event | Cloud ActionType |
|---|---|---|---|
| Audit | `0` (Notepad opened) | 1122 | `AsrPsexecWmiChildProcessAudited` |
| Block | `2` (Notepad refused) | 1121 | `AsrPsexecWmiChildProcessBlocked` |

Same rule, same trigger, one state change, opposite outcome — the audit-vs-block
distinction demonstrated on a single rule.

## 5. Tuning

The rule's `...Audited` and `...Blocked` ActionTypes differ by one word in the same
`DeviceEvents` table. A hunt or dashboard that filters `ActionType startswith "Asr"`
without distinguishing the suffix cannot tell a *blocked* attack from a merely
*watched* one. Always split on the suffix — it is the state.

Note also (Lab 06 §7): a rule set locally via PowerShell does **not** appear in the
Defender ASR report's configuration or detection views, which are scoped to
policy-managed rules. Verify ASR activity in Advanced hunting, not the ASR report.

## 6. Response

None — synthetic, benign. In a real detection this pattern (WMI spawning processes)
is lateral-movement/execution (T1047) and warrants investigating the initiating
account and the spawned child.

## 7. References

- Lab 06 — `labs/06-attack-surface-reduction/README.md`
- `POS-031`, `POS-022` (why deployment is local), `DET-001` (first observed technique)
- Microsoft Learn — Attack surface reduction rules reference
