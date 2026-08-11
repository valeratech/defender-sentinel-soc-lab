---
module: 91
title: Investigating endpoint detections — automated investigation and response
section: Respond to alerts and incidents identified by Microsoft Defender for Endpoint
verdict: lab
date: 2026-08-10
artifacts:
  labs: [22]
  posture: [POS-093, POS-094]
  divergences: [176, 177, 178, 179, 180, 181, 183]
  kql: []
corrections:
  - "Guide: clicking Initiate Automated Investigation starts an automated investigation. On this tenant the investigation had already been created automatically 53 seconds after the antivirus detection, three minutes before the manual click. The click registered as its own alert and joined a run already in flight."
  - "Guide treats the alert title 'Automated investigation started manually' as a description of why the investigation exists. It describes the analyst action only; the investigation's own triggering alert is the antivirus detection, detection source DetectionEngine."
  - "Guide directs the reader to a standalone automated-investigations page in the left navigation. No such entry exists in the Investigation & response subtree at this read; the investigation page is reachable only through an incident or through Action center."
  - "Guide: the incident's Evidence and Response tab shows the incident's evidence. It shows a narrower set than the incident's own investigation — 1 entity against 2 — and the omitted entity is the one awaiting approval. Nothing on the narrower surface signals the omission."
  - "Guide: investigation duration reports how long the investigation took. It reports elapsed wall time including time spent waiting for human approval. Ten minutes of analysis read as 2:31h."
  - "Guide: the Action Center is where pending approvals are found. A pending approval was absent from the Pending tab while the investigation rendered it; a later read with no filters set showed it present. The first null was propagation, and is indistinguishable from an empty queue."
  - "Guide: pivot to VirusTotal for third-party reputation. No pivot is needed — the VirusTotal detection ratio is rendered inside the Defender entity flyout, alongside tenant-scoped and worldwide prevalence for the same object."
  - "Guide: deallocating the VM ends the charges for the lab. A Standard, statically assigned public IP continues to bill for as long as the resource exists, regardless of VM power state."
---

# Module 91 — Investigating endpoint detections

> Nominally: open the incident the last module produced and work it. Actually:
> the cloud reached a verdict the endpoint never reached, an alert title
> misattributes why an investigation exists, and two tabs with the same name
> disagree about what counts as evidence.
>
> Captured **22 days before the Defender for Endpoint AIR standalone experience
> retires on 2026-09-01.** Unrepeatable afterwards.

## What was configured

Nothing. The whole module is portal reads at zero cost with both VMs
deallocated. The pending quarantine on Investigation #2 was **deliberately left
unapproved and uncancelled** — it is the evidence several findings rest on.

## What was established

**The cloud adjudicated a file the endpoint ignored** (Lab 22 §8.2). MOD-90's
PUA artefact — retained on disk by Edge, unrecorded by the local engine — appears
in the investigation's Evidence tab as `f_000045`, verdict **Malicious**,
remediation **Pending approval**. Its detection origin is a *log step*,
`Find recently created or modified executable files`: the investigation found it
by sweeping, not by being told. Without MOD-90's unrelated EICAR test there
would have been no investigation, and the file would still be unrecorded
everywhere.

**The manual trigger did not start the investigation** (Lab 22 §8.5,
divergence 176). Four surfaces agree the incident and investigation were created
at 5:15:41 PM, 53 seconds after the antivirus detection, with triggering alert
`'EICAR_Test_File' malware was prevented` and detection source `DetectionEngine`.
The manual click three minutes later produced its own alert — categorised
**Suspicious activity** — and joined the run. The response action is carried in
the incident's exported `Detection sources` field.

**Two Evidence tabs, two scopes, one omission** (Lab 22 §8.6, divergence 177).
Incident scope holds 1 entity; that incident's investigation holds 2, both
Malicious. The omitted one is the entity awaiting a human decision. Same tab
name, same page position, different objects — and the narrower surface's own
left rail reads `All evidence (1) / Files (1)`, confirming its completeness
within its scope and signalling nothing.

**The action lifecycle is poorly instrumented at both ends** (Lab 22 §8.7,
divergences 179–181). Duration counts queue time, not work. A pending action
renders no creation time on any surface. A completed action's CSV export carries
`Completed` with an empty `EndTime`. One state carries three labels —
`Pending action`, `Pending approval`, `Pending` — across three surfaces.

**A transient null on the approval queue** (Lab 22 §8.7, divergence 178). The
Action Center's Pending tab read `0 items / No actions found` while the
investigation rendered `Pending actions (1)`; a re-read hours later with no
filters set showed the item present and unchanged. Propagation, not permanent
divergence — recorded at that narrower strength after an earlier, stronger claim
was withdrawn. Operationally the consequence survives the correction: a
transient null is indistinguishable from an empty queue.

**VirusTotal is embedded, not a pivot** (Lab 22 §7.5). The entity flyout renders
detection ratio **57/64**, `Virus:DOS/EICAR_Test_File`, reputation Malicious
(100/100), and a prevalence split of **1 organization device against 3,740
worldwide** — first seen here 2026-08-10, first seen worldwide **2013-03-04**.
The scope split is the useful primitive: *new here, ancient everywhere* triages
differently from *new everywhere*.

**AIR pre-retirement state, captured** (`POS-093`). One investigation on one
quiet lab client analysed **2,713 entities** — 1,516 files, 439 drivers, 295
services, 277 persistence methods, 173 processes, 13 IP addresses — across 30 log
steps, to find one malicious file and remediate it. From 2026-09-01 this no
longer runs as a separate investigation experience and no longer supports manual
triggering. **The change is Defender for Endpoint only; AIR for Defender for
Office 365 remains available, so Lab 13's findings are unaffected.** A grep of
`labs/18`, `labs/19` and `detections/` found no committed automation invoking
MDE AIR.

**Deallocation stops compute, not the IP meter** (Lab 22 §9, `POS-094`,
divergence 183). Both VMs read `Stopped (deallocated)`; the client VM's public
IP is SKU **Standard**, assignment **Static**, still associated, and bills
continuously for as long as it exists. MOD-84's mechanism, caught from
configuration before the invoice rather than inferred from billing afterwards.

## Confirmed absences

**Copilot pane — absent**, two reads, incident flyout and full incident page,
plus the portal's global toolbar. Capacity was torn down at MOD-88 (Lab 20). The
surface renders normally and the pane is not on it. This is a positive absence
on a working surface, **not** a foreclosed scenario in the shape of MOD-86.

**No alert for the `.vbs`** (Lab 22 §7.4). It appears only as log steps —
read at 5:21 PM, then analysed by external services for 3:19m. Not blocked, not
alerted, collected and analysed anyway.

**No standalone automated-investigations navigation entry** (Lab 22 §7.1).
Recorded as an observation; whether it prefigures the 2026-09-01 consolidation
is not established by one navigation read.

**Attack story playback produced no animation** — two alerts, two nodes, one of
them an analyst action. Recorded as a limit of this lab's telemetry, not as a
finding about the product, and not to be repeated.

## Cross-references

Lab 22 §7, §8.2, §8.5, §8.6, §8.7, §8.8, §9 · `POS-093` · `POS-094` ·
`POS-033` · Lab 13 (**MDO** AIR — a different product, unaffected) ·
Lab 17 (incident workflow) · Lab 20 (Copilot teardown) ·
`DET-004` (Sentinel scheduled alerts receive no automated investigation)
