# Lab 20 — Security Copilot: A Better Witness Than the Portal, and Confidently Incomplete

| Field | Value |
|---|---|
| **Domain** | AI-assisted investigation / metered capacity |
| **Objectives** | Provision Security Copilot capacity against a fixed cost ceiling (module 85, G62); interrogate a *previously documented* incident and score the answers against the committed record (module 87, G64); tear down inside one clock hour (module 88, G65) |
| **Depends on** | Lab 19 (incident 24 — the measurement target, documented across seven surfaces), Lab 18 (Orders 1 and 2 still on the incident), Lab 11 (`DET-004`, the detection), `POS-016` (delete-to-stop billing), `POS-033` (Defender for Cloud declined — forecloses module 86), `POS-058` (Azure credit structurally unreachable) |
| **Status** | ✅ Built and measured — provisioned 11:00:07, torn down inside the same clock hour |
| **Built** | 2026-08-09 |
| **Cost** | 1 provisioned SCU, 1 clock hour. **$4 inferred, not yet invoiced** (`P20-11` open) |

> The course teaches Copilot against Microsoft's synthetic sample alerts. This
> lab pointed it at **incident 24 from Lab 19** — an incident whose ground
> truth, *and whose portal defects*, were already committed. That converts a
> walkthrough into a measurement: does Copilot reproduce the portal's errors,
> or the store's truth?
>
> **Both, in the same session.** Asked for entities, it returned **four typed
> identifiers** — `Account Name`, `Azure AD User ID`, `User Principal Name`,
> and a `User SID` that appears on **no** portal surface this project has
> documented in twenty labs — where four Defender surfaces render the single
> truncated string `labuser`. Asked about automation, it correctly described
> the playbook the incident audit trail misfiles as **`Trigger: Manual`** —
> reading past a defect the portal shows. Then, in the same answer, it stated
> **`No other automated investigation or follow-up actions were recorded`**
> while four `Automated` / `Completed` rows sat in the Activities tab. It
> corrected the mislabelled minority and erased the correctly-labelled
> majority, and asserted the absence positively.
>
> The paid hour also cost 14 minutes before the product was usable. A resource
> that bills from creation sits behind a **nine-screen setup wizard** neither
> guide mentions, whose defaults grant Copilot ownership to **seven directory
> roles**, enable telemetry and model-training capture, and leave overage
> **unlimited**.

---

## 1. Objective

Modules 85, 87 and 88 are one build-measure-teardown unit. Module 86 (sample
alerts) is **skipped and pre-refuted** — see §7.

Three things this lab measures rather than accepts:

1. **Whether Copilot is a better witness than the portal.** Lab 19 established
   that four surfaces truncate the account entity while the store carries more.
   Copilot sits above both. Which does it read?
2. **What a metered resource actually costs in wall-clock terms.** Not the
   list price — the time between `Create` and the first useful answer.
3. **What the defaults do when nobody changes them.** Every consent and
   configuration control was captured in its as-shipped state before any
   change.

## 2. Cost discipline

`POS-016` established the category: Security Copilot capacity **bills while it
exists, has no stopped state, and only deletion ends it**. `POS-058`
established that the Azure credit cannot reach this subscription's spend. So
the ceiling was enforced by the clock and by configuration, not by credit.

| Control | Decision | Basis |
|---|---|---|
| Provisioned SCUs | **1** (minimum) | `MOD-83` |
| Overage | **Limited to 0** | `MOD-83`, written before any price was seen |
| Resource group | **dedicated, created empty in advance** | teardown interlock — see §6 |
| Provision time | **on the hour boundary** (11:00:07) | clock-hour billing, `MOD-83` |
| Deletion | **inside the same block** (11:23) | one unit |

**Ceiling $10. Actual: one clock hour.**

## 3. What was built

Capacity `copilotlab` — 1 SCU, `Prompt evaluation location` **US**,
`crossGeoCompute` **NotAllowed**, `overageState` **Limited** / `overageAmount`
**0**, in dedicated resource group `rg-copilot-lab` (West US). Capacity
region **East US**, not selectable. Workspace `copilotlab-ws`, its own data
storage location, created in a different portal.

**Trigger:** three prompts against incident 24 in the standalone portal,
2026-08-09 11:10–11:15 PDT.

## 4. Predictions

Written before provisioning. Withdrawals recorded, never edited away.

| id | prediction | result |
|---|---|---|
| P20-1 | No Default capacity exists — trial E5 does not satisfy the *paid licence* formula | ✅ confirmed on three surfaces |
| P20-2 | Blade named `Microsoft Security Compute Capacities` | ❌ renders `Microsoft Security compute capacities` — sentence case |
| P20-3 | Estimate ~$2,900/month for 1 SCU | ✅ `$2920/month` — $4 × **730** h, the average-month convention |
| P20-4 | Provisioning completes < 2 min, no quota gate | ✅ deployment succeeded, no approval |
| P20-5 | Copilot returns the full UPN, not the truncated `Name` | ✅ **exceeded** — returned four typed identifiers including a SID |
| P20-6 | Copilot does not surface the `Trigger: Manual` misfiling | ❌ **inverted** — it surfaced the playbook correctly and lost the other four rows |
| P20-7 | At least one detail contradicted by the committed record | ✅ twice — `detected on`, and a false absence |
| P20-8 | Session consumption well under 1 SCU-hour | ❌ **1.5 units** against 1 provisioned |
| P20-9 | Usage dashboard lags; not visible at T+30 | ❌ near-live (`Last updated` within a minute) |
| P20-10 | RG deletion removes capacity; workspace survives | ✅ workspace, session transcript **and usage history** all survive |
| P20-11 | Final bill: 1 clock hour, $4 | ⏳ **open** — cost analysis reports nothing yet |
| P20-12 | ≥1 field named differently from the guide | ✅ several — see §5 |

## 5. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Inclusion active? | Copilot portal / Message center / capacities blade | none (trial ≠ paid) | ✅ `Showing 1 - 0 of 0`, unfiltered |
| Capacity name constraint | Create form | guide's `copilot-demo` | ❌ lowercase letters and numbers only, **no hyphens** — the guide's example is invalid |
| Capacity region selectable | Create form | choose closest | ❌ **static text**, `US East`, no control — though ARM accepts `location` as a parameter |
| Overage disengageable | Create form | toggle off | ❌ toggle will not disable; **`Limited` + amount 0** is the only zero |
| Submitted configuration | `View automation template` → Parameters | matches form | ✅ `crossGeoCompute: NotAllowed`, `overageState: Limited`, `overageAmount: 0`, `geo: US`, `location: eastus` |
| Time to first answer | Wall clock from `Create` | ~2 min | ❌ **14 min** — nine setup screens |
| Entity identifiers | Prompt 2 | full UPN | ✅ **four**: Account Name, Azure AD User ID, UPN, **User SID** |
| Automation reported | Prompt 3 | 5 rows | ❌ **1 of 5** — playbook found, four `Automated` rows omitted |
| Playbook trigger characterised | Prompt 3 | portal says `Manual` | ✅ described as **automated** — read past the portal's misfiling |
| Detection timestamp | Prompt 1 vs incident page | 18:57:27Z | ❌ reported `detected on … 18:47:30 UTC` — that is **first activity**, ten minutes earlier |
| Session consumption | Usage monitoring | < 1 | ❌ **1.5**, `Overage units used 0 of 0` |
| Overrun billed? | At-capacity tooltip | overage | ❌ **absorbed** — *we won't charge you for the extra units it took to finish your last operation* |
| Capability attribution | `3 steps completed` expansion | one plugin | ❌ prompts 1–2 `Chose Incident Analysis`; prompt 3 `Chose Microsoft Defender XDR`; dashboard rolls all three up as `Microsoft Defender XDR` |
| Teardown scope | Delete dialog | 1 resource | ✅ *all dependent resources, including hidden types, are shown* — 1 |
| Billing stopped | Capacities blade | 0 | ✅ capacity and RG both gone |

## 6. Failures & Fixes

**The Create form defaulted the resource group to `NetworkWatcherRG`** — the
alphabetically first group, not the one created for this lab. Uncorrected, the
capacity would have landed there and module 88's *delete the resource group*
teardown would have targeted it. Caught by capturing defaults before filling
the form. **The dedicated resource group is the safety interlock for the
teardown step, not a tidiness preference.**

**Navigating to the wrong incident.** Step 0.3 of the run sheet named the
target as "a Lab 19 incident" rather than by ID. Lab 19's incident is **24**;
**incident 19** is Lab 17's Responder boundary-test artifact (`POS-074`). The
number collision aimed the first navigation at the wrong evidence. Caught
before any prompt ran, at zero cost, by grepping the repo. **Incident IDs are
a fifth counter** — now recorded in `docs/documentation-standard.md` §4.1.

**A deletion dialog that emptied itself.** After `Delete`, the confirmation
dialog remained open showing zero resources where it had shown one. Read as
propagation, confirmed by re-reading the capacities blade rather than clicking
`Delete` a second time on a stale dialog. **Two-read rule.**

**The list-level resource-group toolbar has no Delete.** Selecting a group's
checkbox enables nothing; `Delete resource group` exists only inside the
group's own Overview blade.

## 7. Module 86 — skipped, and pre-refuted rather than declined

Module 86 populates a tenant with Defender for Cloud **sample alerts**.
Generating them requires selecting the Defender plans to generate for, and
those alerts exist only where a plan is enabled. **This subscription has none**
— `POS-033` records Defender for Cloud declined at Lab 04, and names the
consequence already being paid: no Defender for Servers P2, therefore no
500 MB/day/server allowance, therefore the DCR tier as the only cost lever.

So the skip is not a cost preference. A recorded architectural decision
forecloses the module, and reversing it would have opened a **second meter on a
different billing basis** inside the paid hour.

**It was never load-bearing.** Module 87 needs an *incident ID*, not Microsoft's
synthetic alerts — and using a real, already-documented incident is what made
the measurement possible at all.

This is the second instance in two sessions of a committed finding
**pre-refuting a later module's advice** (`POS-058` did it to `MOD-84`).

## 8. Findings

**Copilot read identifiers the portal does not render.** Four Defender surfaces
show `labuser`; Copilot returned Account Name, Azure AD User ID, UPN and a
**User SID** (`S-1-12-1-…`, an Entra-issued SID) in a typed table with an
`Export to Excel` control. The entity is one object with multiple identifiers,
strong and weak; the portal displays the weak one. **The truncation is a
display choice, and the layer above it is not bound by that choice.**

*How* it reached them is **not established.** Prompts 1 and 2 expanded to
`Chose Incident Analysis` — a Copilot-native capability — while only prompt 3
read `Chose Microsoft Defender XDR`. The usage dashboard attributes the entire
session to `Microsoft Defender XDR`. An earlier claim that the dashboard
confirmed the source for all three prompts is **withdrawn**: it is a
session-level rollup naming one plugin where two capabilities ran.

**The correction and the erasure arrived together.** Prompt 3 characterised the
playbook as an automated action with the detection as its trigger — correct,
and contrary to the incident audit trail, which files that single consequential
action as `Trigger: Manual` with empty status while four cosmetic changes beside
it read `Automated` / `Completed`. Copilot then asserted no other automated
actions existed. **Reading past a defect and inventing an absence are the same
answer here**, and the absence is stated positively rather than left open.

**A status word answering a different question**, again. `detected on
2026-08-08 at 18:47:30 UTC` is a correct UTC conversion of **first activity**.
Detection — incident creation — was `18:57:27Z`. The ten-minute latency Lab 19
measured to the millisecond is silently collapsed into the field an analyst
reads as an SLA.

**Unconfigured, and in force — four times in fourteen minutes.** Overage
defaulted to `Allow Unlimited Overage Capacity`. Cross-geo prompt evaluation is
labelled *recommended for optimal performance*. Telemetry capture and
security-AI-model training both defaulted **on**, covering user prompts, the
security information accessed, and Copilot's responses, for **human review**.
M365 service-data access is presented with **no control at all** — a single
`Continue`, with the opt-out relocated to an `Owner settings` page not yet
seen. One default ran the other way: Purview logging of Customer Data defaults
**off**, which falsifies the easy generalisation and thins the audit trail as
its price (`POS-089`).

**Seven directory roles are made Copilot owners by default** (`POS-088`). Global
Administrator, Security Administrator, **Intune Administrator**, **Conditional
Access Administrator**, and three Purview roles — granted owner rights over
usage monitoring, plugin management and role assignment, with no control on the
screen to remove any of them. The grant is to *roles*, so anyone who ever holds
Intune Administrator inherits Copilot ownership silently. `MOD-82`'s claim that
Copilot inherits the analyst's permissions holds for **data** and not for
**control**: service ownership is Copilot-native and was assigned by default.

**Demand exceeded provisioned capacity and was absorbed, not billed** (`POS-087`).
1.5 units against 1 provisioned, with `Overage units used 0 of 0`. The at-capacity
tooltip states Microsoft does not charge for the extra units needed to finish an
in-flight operation. **This is documented in none of guides 60–65.** An earlier
claim that the unlimited-overage default *would have* billed $6 for that 0.5 is
**withdrawn** — the evidence does not support it, and what the cap prevented on
this session is unknown. The `MOD-83` decision stands on its own reasoning.

**The throttle condition is only legible after the fact.** No warning fired at
1.0. A warning triangle sat on the capacity tab with **no tooltip and no
target** while capacity existed. The explanatory tooltip and the red overrun
segment on the chart both became readable only *after* the capacity was
deleted — the visual that would have warned was unavailable while it could
still be acted on.

**Billing evidence outlives the billed resource.** Deleting the resource group
destroyed the capacity; `copilotlab-ws`, the full session transcript, and the
usage history with its 1.5-unit row all survive. Guide 62 claims the workspace
persists; it does not mention that the consumption record does. Inverse of
`POS-084`, where run history retained what nobody wanted kept.

**Four names for one object.** `Microsoft Security compute capacities` (blade),
`Set up your Copilot capacity` (create form), `Copilot capacity` (prose),
`Microsoft.SecurityCopilot/capacities` (ARM). The residency control renders as
*allow Copilot to evaluate prompts anywhere in the world* (Basics),
`Cross-region compute: Not allowed` (Review), and `crossGeoCompute: "NotAllowed"`
(ARM) — three strings, and only the third is submitted. The GA product
provisions through apiVersion **`2024-11-01-preview`**.

**Empty states that misreport themselves.** An empty resource group reads
`No resources match your filters` under `Type equals all` / `Location equals
all`. Usage monitoring offers a page 2 that holds nothing. A Message center
search for `Security Copilot` returns **five items, none about Security
Copilot** — four Purview agent notices matched because those agents *run on*
SCUs, which is `MOD-83`'s correction seen from the other side.

## 9. References

- [What is Microsoft Security Copilot](https://learn.microsoft.com/en-us/copilot/security/microsoft-security-copilot)
- [Get started with Microsoft Security Copilot](https://learn.microsoft.com/en-us/copilot/security/get-started-security-copilot)
- [Manage capacity](https://learn.microsoft.com/en-us/copilot/security/manage-usage)
- [Security Copilot inclusion with Microsoft 365 E5](https://learn.microsoft.com/en-us/copilot/security/security-copilot-inclusion)
- [Validate alerts in Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/alert-validation)
