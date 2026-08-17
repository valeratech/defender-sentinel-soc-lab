---
title: Endpoint prevention controls — PUA protection, EICAR, and script execution
date: 2026-08-10
artifacts:
  labs: [22]
  posture: [POS-092]
  divergences: [173, 174, 175, 182]
  kql: []
corrections:
  - "Guide: PUA protection is enabled and blocking by default. This tenant ships PUAProtection = 2 (audit), not 1 (block). The value must be read, never assumed."
  - "Guide: audit mode detects and logs without blocking, so the file downloads and the detection appears in the logs. The download happened; the detection did not. No threat object, no event 1116, no event 1117, with real-time protection, MAPS reporting and sample submission all on."
  - "Guide follows AMTSO's test logic — if the file downloads, the configuration is wrong. That test cannot distinguish three different outcomes: PUA blocking the file, the browser blocking the save, and audit mode allowing it while recording nothing."
  - "Guide treats the browser download attempt and a command-line retrieval as equivalent ways to fetch the test file. Edge refused the download and left the complete payload on disk as an orphaned .crdownload; Invoke-WebRequest succeeded silently. The two methods test different things."
  - "Guide does not mention that on an Entra-joined device the Entra identity is a standard user, so the natural RDP session cannot run Set-MpPreference. Changing PUA protection requires the local administrator account."
---

# Endpoint prevention controls

> Nominally: turn on PUA protection, download a test file, confirm it was
> blocked. Actually: a control set to *audit* that audited nothing, and a test
> design that cannot tell the difference between working, untested, and silent.

## What was configured

**Nothing.** Every value in this walkthrough was **read, not set**. `PUAProtection`
was found at `2` (audit) and deliberately left there — the finding depends on
the shipped value, and changing it would have required a `labadmin` session that
the Entra RDP identity cannot open.

Two files were introduced to `LAB-WIN11-01` and one script written: an EICAR
test file, a PUA test file from AMTSO's public suite, and a `.vbs` invoking
PowerShell. Nothing persisted; nothing was vendored into the repository.

## What was established

**Audit mode produced no audit trail** (Lab 22 §8.1, `POS-092`). The PUA file
downloaded, persisted on disk, and generated no threat object, no event 1116 and
no event 1117 — with `DisableRealtimeMonitoring: False`, `MAPSReporting 2`,
`SubmitSamplesConsent 1`. The setting's entire deliverable is the record, and
there was no record.

**The EICAR control is what makes that conclusive** (Lab 22 §4.3). Same machine,
same session, same retrieval method, minutes apart: toast, 1116, 1117, threat
object `Virus:DOS/EICAR_Test_File`, file removed. The pipeline demonstrably
works, so the PUA silence is a property of the control and not of a broken path.
This is the negative-then-positive control pattern applied to a measurement
rather than to a fix — without it, §8.1 would be an unsupported absence.

**Three outcomes are indistinguishable at the browser** (Lab 22 §8.4,
divergence 175). PUA blocking the file, Edge blocking the save, and audit mode
allowing it while recording nothing all present identically. Both
`Invoke-WebRequest` calls returned silently to the prompt; only a corner toast
differed.

**A browser "block" that kept the whole file** (Lab 22 §8.3, divergence 174).
Edge refused with `"PotentiallyUnwanted.exe can't be downloaded securely"` and
left the complete 33 KB payload as an orphaned `.crdownload` in the Edge cache.
The block is of the save, not of the transfer. That retained copy is the one the
cloud investigation later adjudicated Malicious (`docs/evidence-notes/investigating-endpoint-detections.md`).

**Script execution was not blocked, and this was predicted** (Lab 22 §4.4). The
`.vbs` invoking PowerShell ran with no block, dialog or SmartScreen prompt —
consistent with Lab 06 having enabled only the WMI-persistence and PSExec/WMI
ASR rules. A behavioural surface, not an ASR surface. What the endpoint did not
do, the cloud did; that half belongs to `docs/evidence-notes/investigating-endpoint-detections.md`.

**Truncation is carried as data** (Lab 22 §8.8; cf. `POS-033` for the
separately measured server-hostname truncation). `LAB-WIN11-DEFEN` at 15
characters on six surfaces, including the machine-readable Action Center CSV
export. The export is not rendering a display name.

## What this walkthrough does not establish

Whether PUA protection *blocks* correctly when set to `1`. That was not tested,
because the shipped value was the finding and changing it would have destroyed
it. The measurement here is about audit mode only.

Why Edge's message names transport security for an HTTPS URL. An initial
mixed-content diagnosis was **withdrawn** (Lab 22 §6). What Edge did is
recorded; why it said what it said is not resolved on this evidence.

## Cross-references

Lab 22 §4, §6, §8.1, §8.3, §8.4, §8.8, §8.9 · `POS-092` · `POS-033` ·
Lab 06 (ASR rule scope) · Lab 03 (EDR detection test)
