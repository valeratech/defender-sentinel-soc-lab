# Lab 16 — MDCA File Policy: Two Products, One Engine, One File

| Field | Value |
|---|---|
| **Domain** | Data protection / cloud app security |
| **Objectives** | Census MDCA's shipped policy state before building anything; build a file policy using Data Classification Service inspection with advanced settings left as shipped; re-trigger with the exact file Purview already matched; compare two products' default calibrations on identical bytes |
| **Depends on** | Lab 14 (the file, the three SITs, and the DLP policy whose creation provisioned half of what this lab found), Lab 15 (`POS-065`, the sibling cross-product grant) |
| **Status** | ✅ Built and measured — divergence confirmed, mechanism open |
| **Built** | 2026-08-04 (census, build, trigger) · 2026-08-04 – 2026-08-05 (observation) |

> The lab was designed as a calibration experiment: point two products' shipped
> defaults at the same 243 bytes and see whether they agree. They did not —
> Purview matched at Medium confidence in minutes, MDCA read zero at 27 hours.
> But the census phase found something larger before the policy was ever built.
> **Lab 14's DLP policy had already reached into MDCA and created two file
> policies and flipped a monitoring toggle, in a console nobody had opened** —
> and those two auto-created policies read zero while the policy that spawned
> them reads two.

---

## 1. Objective

The MDCA file-policy assignment's material is an instructor demo; this lab was built live by decision.
Four questions:

1. **What ships enabled?** (Phase A census — `POS-066`)
2. **What is already here that we did not put here?** (the Activity log —
   `POS-067`, and the finding that reframed the lab)
3. **Does a default-configured DCS file policy match content Purview already
   matched?** (`POS-069`)
4. **Is the connector actually carrying data?** (`POS-068` — asked last,
   answered first, and it changes how question 3's answer must be read)

Cost: none. MDCA is E5-trial-bound. No Defender for Cloud plans were enabled;
the Cloud security *Prepare tenant* flow remains blocked behind a paid plan and
was not purchased.

## 2. Predictions

Registered before the census and before the trigger.

| # | Prediction | Status |
|---|---|---|
| P16-1 | A substantial set of built-in policies ships enabled, per the guide | ❌ **REFINED** — 23 of 26 `[Disabled]` by the June 15 2025 dynamic-model migration; 3 OAuth/TI policies survive active |
| P16-2 | File monitoring is off until enabled | ❌ **WRONG, and the correction is the finding** — monitoring was ON, but auto-enabled 2026-08-02 by *our own* Lab 14 action, not by provisioning |
| P16-3 | An Office 365 connector exists without being requested | ✅ CONFIRMED — Jul 15 2026 |
| P16-4 | The Activity log carries user telemetry | ❌ **AS INTENDED** — 5 events, all administrative, zero user activity |
| P16-5 | `CloudAppEvents` holds data | **ANSWERED: empty** over 7 days — three surfaces agree on genuine no-flow |
| P16-6 | Cloud Discovery is unconfigured; MDE enforcement is off | ✅ **BOTH** — pristine first-run splash; `Enforce app access` unchecked |
| P16-7 | Unified audit being off explains the silence | ✅ **AUDIT IS ON** — the leading suspect is eliminated and no replacement was found |
| P16-8 | The SIT catalogue is consistent across products | 〜 **325 in MDCA vs 327 in Purview**, twice |
| P16-9 | *Framed as genuinely open:* Purview matched this file at Medium with advanced settings shipped as-is. MDCA runs the same engine with its own untouched defaults. **Agreement or divergence is the finding either way** | ✅ **RESOLVED — divergence.** 0 at +3 h 30 m and +27 h |
| P16-10 | The re-uploaded file appears as a fresh OneDrive row in Lab 14's rebuilt report | ✅ **CONFIRMED to the minute** — Aug 4 2:14 PM UTC = 07:14 PDT, Low volume rule, U.S. Bank Account +1 more |

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Build vs. watch | **Build live** | Follow the instructor demo | The demo's triggered example appeared pre-populated by an earlier policy. A live build on a known-clean tenant is the only way to know what a first policy actually does |
| Advanced settings | **Untouched, as shipped** | Tune per-SIT confidence and instance counts | Defaults-as-shipped *is* the experiment. Tuning would have made the comparison about our choices instead of about the products' |
| Pre-seeded filters | **Both removed** | Accept as presented | The defaults scope to `Public/External` plus a modified-after cutoff — which excludes private files, i.e. the content the policy exists to find (row 98) |
| Trigger file | **Bit-identical re-upload** — same 243 bytes, name, and path | A fresh synthetic file | Content identity is the controlled variable. It also armed `P16-10` as a true repeat measurement rather than a new one |
| Governance actions | **None selected** | Quarantine, notify, apply label | Observe-only. A governance action would have changed what the measurement was measuring |

## 4. Build

Portal-only. All times PDT 2026-08-04.

**Phase A — census** (~04:30–06:00, read-only): 29 policies (`POS-066`); the
Activity log's five events (`POS-067`); connector state and `CloudAppEvents`
(`POS-068`); MDE integration page (`POS-070`); Cloud Discovery first-run splash;
Audit page confirming unified audit ON.

**Phase B — build** (07:08): `Lab16-FilePolicy-SITMatch` (`POS-069`) — file
policy, severity Low, category DLP, both pre-seeded filters removed, zero
filters, all files and owners, **Inspection: Data Classification Service** with
Credit Card / US Bank Account / ABA Routing, match `Any`, advanced settings
untouched, alert per matching file with a daily limit of 5, no governance.
Created and listed within the same minute — 3 of 3 file policies.

Observed at build: the SIT picker offers **325** (row 99); DCS exposes all four
classification mechanisms (SIT, EDM, fingerprint, trainable); `Inspect protected
files` is **greyed pending an Entra permission grant to the MDCA application** —
application-consent, not GA-insufficiency, and distinct from the
`POS-002` family; the feedback box arrives pre-checked with the admin UPN
pre-filled (row 108).

**Phase C — trigger** (07:14): `lab14-dlp-test.txt` re-uploaded to admin OneDrive
root, bit-identical.

## 5. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Purview still matches the file | Lab 14 Items for review grid | Fresh OneDrive row at the upload minute | ✅ **Aug 4 2:14 PM UTC**, Low volume rule, U.S. Bank Account +1 more |
| MDCA matches the file — read 1 | Policies, `Type: File policy` filtered | Open question (`P16-9`) | **0 matches** at +3 h 30 m |
| MDCA matches the file — read 2 | Same, filtered view | Two-read rule on any zero | **0 matches** at **+27 h** |
| MIP mirrors match the file | Same page, same read | Unexamined until observed | **0 matches each**, against their source policy's **2** (row 105) |
| Connector is carrying data | Activity log · `CloudAppEvents` · Last activity | One surface would be weak | ❌ **Three surfaces agree: no flow** (`POS-068`) |

### How the zero must be read

A zero cannot be resolved into *scanned and below threshold* versus *never
scanned*, and `POS-068` makes the second live: the connector reports `Connected`
and carries no telemetry on any surface. **Recorded as divergence with mechanism
open, not as a calibration result.**

What survives either reading: **content Purview flags at Medium confidence is
invisible to a default-configured MDCA file policy at 27 hours.**

*(pending)* — the MDE-side discovery toggle (Settings → Endpoints → Advanced
features) was never read, so only one direction of the `POS-070` integration is
measured. Reading it would establish whether the endpoint feed is off at both
ends or only at the MDCA end.

## 6. Failures & Fixes

**One wrong claim, corrected in-session.** File monitoring was written up as
having been ON since provisioning. The Activity log showed all five of its events
originate from Lab 14's policy creation on 2026-08-02, including the monitoring
toggle. Our own action flipped it. Corrected before it reached a file
(`POS-067`).

**One inference withdrawn on evidence.** The 17:52 mirror-creation timestamp was
read as approximately corresponding to DLP sync completion — plausible at the
time, since it sat 1 h 48 m after policy creation. The DLP simulation-completion
alert email then self-stamped **16:06 local**, leaving a 1 h 46 m gap the
inference cannot cover. Withdrawn, mechanism reopened, recorded rather than
edited away.

**One census caught by a filter.** The unfiltered policy list rendered 27
policies with one MIP mirror; the `Category: DLP` filtered view showed both.
Caught only because the mirror pair was already known from the Activity log
(row 100).

## 7. Analysis

**The census outranked the experiment.** The lab was built to compare two
classification engines. Before the policy existed, the Activity log showed that
Lab 14 had already provisioned two file policies and a monitoring toggle here —
five events in the log, all of them that. An operator who never opens MDCA has
objects in it that a different product created on their behalf.

**And those objects are hollow.** Both mirrors read 0 while their source reads 2
(row 105). This is worse than a policy someone configured badly: **nobody
configured these**, so nobody has cause to check them. An operator auditing MDCA
sees two DLP-category policies covering their financial data, correctly named,
correctly severitied, one carrying an alert bell — and no indication that they
have never matched anything.

**The policy list is not a detection inventory.** 23 of 26 built-ins are
`[Disabled]` by a platform migration, standing in for a dynamic model that runs
somewhere this page does not show (`POS-066`). Guide 53's claim that a
substantial set ships enabled is the largest accumulator correction of the arc.

**Three surfaces agreeing is what made the connector finding usable.** Any one of
them alone — an empty log, an empty table, a dash in a column — is arguable. All
three, plus the leading suspect eliminated by verifying unified audit is ON,
makes `Connected` a status label rather than a data-flow claim (`POS-068`). It
also disciplines the headline result: the zero in `POS-069` cannot be attributed
to calibration while this is unexplained.

**The timestamp finding corrects a correction.** Row 49 revised *"Defender local,
Azure UTC"* to *"Defender renders UTC"*. MDCA's Activity log renders **local**,
inside the same portal — decoded only by causality violation, since a UTC reading
would place the mirror creation before the policy that caused it. Three
conventions under one shell, and one page in the same product labels both of its
own (row 102), which is what makes this a criticism rather than a complaint.

**Everything here has an expiry date.** The Policies page states file policies
retire **January 6, 2027** — the same day as Lab 14's Instances banner, to the
day — and the `Migrate (Coming Soon)` button is greyed. The migration path
Microsoft directs operators to has not shipped, five months out.

## 8. References

- Microsoft Learn — [File policies in Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/data-protection-policies)
- Microsoft Learn — [Connect Microsoft 365 to Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/connect-office-365)
- Microsoft Learn — [Anomaly detection policies](https://learn.microsoft.com/en-us/defender-cloud-apps/anomaly-detection-policy)
