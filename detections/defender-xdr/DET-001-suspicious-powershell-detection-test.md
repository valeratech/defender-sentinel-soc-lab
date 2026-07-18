---
# Machine-readable header — consumed by scripts/build-attack-matrix.py
id: DET-001
name: Suspicious PowerShell command line (EDR detection test)
status: active
platform: defender-xdr
rule_type: ml
severity: medium
tactics:
  - TA0002
techniques:
  - T1059.001
data_sources:
  - DeviceProcessEvents
  - DeviceEvents
validated: true
---

# DET-001 — Suspicious PowerShell command line (EDR detection test)

This is not a rule this project authored. It is Microsoft Defender for Endpoint's
own built-in behavioural detection, recorded here because it is the **first
detection observed firing in this environment** — the one that proved the
sensor onboarded in Lab 03 actually reports detections, not just telemetry. It
is tracked so `docs/attack-coverage.md` reflects *observed* coverage of
`T1059.001`, not merely planned coverage.

## 1. Hypothesis

> If a process launches PowerShell with evasion flags (hidden window,
> execution-policy bypass) and a download-and-execute pattern, Defender for
> Endpoint raises a "Suspicious PowerShell command line" alert mapped to
> `T1059.001`, and it reaches the portal within ~10 minutes.

Falsified on the latency — it arrived in ~2 minutes, not 10 (Lab 03 §4).
Confirmed on everything else.

## 2. Data Requirements

| Requirement | Value |
|---|---|
| Onboarded sensor | `POS-029` — LAB-WIN11-01, Active |
| Tables | `DeviceProcessEvents`, `DeviceEvents` |
| Licence | Plan 2 (E5) — full incident graph and timeline, confirmed present |

## 3. Trigger

Microsoft's published EDR detection test — hidden PowerShell attempting a
`WebClient` download of a benign file from `127.0.0.1` and executing it. The
command is **not reproduced here** (project no-malicious-code rule); it lives in
Microsoft's documentation. The mechanism is described in Lab 03 §7.

## 4. Validation — observed, not asserted

Ran the test; the detection fired. Evidence from the incident:

| Signal | Observed |
|---|---|
| Alert | "Suspicious PowerShell command line", **Medium** |
| ATT&CK mapping | `T1059.001` (Execution) — Defender-assigned |
| Second alert | "[Test Alert] Suspicious PowerShell commandline", Informational — Defender fingerprinting the *known test*, distinct from the behavioural detection |
| Detection source | EDR |
| Correlation | Both alerts grouped into one incident; correlation reason **"same user credentials"** (`labadmin`, same device, same window) |
| Process lineage | Full tree reconstructed: `userinit.exe → explorer.exe → cmd.exe → powershell.exe → script execution` |
| Auto-extracted evidence | 4 entities, each verdict **Suspicious**: `cmd.exe`, `powershell.exe`, the download URL, and the IP `127.0.0.1` |
| Attribution | `labadmin` throughout |

## 5. Tuning — a real false-positive class, observed

Defender rendered a **Suspicious** verdict on the IP `127.0.0.1` — loopback,
which cannot be attacker infrastructure. It was flagged only because it appeared
in a malicious-looking download. Any custom IOC pipeline that promotes
auto-extracted "suspicious" IPs to indicators (Defender → Cloud Apps →
indicator auto-add, per the module 29 settings reference) would need to exclude
loopback and RFC 1918 space, or it would generate block indicators against
addresses that mean nothing. Recorded as the first concrete member of the same
false-positive family as the `senseir.exe` benign-PowerShell pattern
(`kql/advanced-hunting/senseir-benign-powershell.kql`): the platform surfaces
things that *look* like the query's target and are not.

## 6. Response

None taken — synthetic test. No automated attack disruption fired, correct for a
Medium test detection; the platform chose not to contain (Lab 03 §5). In a real
detection of this shape the response is process termination and device
isolation, gated on confirming the download source and payload are genuinely
hostile rather than a sanctioned red-team or admin action.

## 7. References

- Lab 03 — `labs/03-endpoint-onboarding/README.md` (§4 validation, §7 analysis)
- `POS-029` (sensor), `POS-011` / `senseir` (the false-positive family)
- Microsoft Learn — Run a detection test on a newly onboarded device
