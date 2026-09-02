# Lab 15 — Insider Risk Management: a Trigger That Never Fires

| Field | Value |
|---|---|
| **Domain** | Data protection / insider risk |
| **Objectives** | Build an IRM policy from the Data leaks template; measure the org-level indicator baseline before enabling anything; wire the policy's triggering event to Lab 14's simulation-mode DLP policy; determine whether a simulation-mode DLP match functions as an IRM triggering event |
| **Depends on** | Lab 14 (the DLP policy this lab's trigger points at, and the SITs used as priority content), `POS-002` (the identity this lab expands), `POS-061` (the role-group grant that made the alert surfaces readable) |
| **Status** | 🔨 Built, documentation in progress — null verdict, confirmed twice on three surfaces |
| **Built** | 2026-08-03 (build) · 2026-08-04 – 2026-08-05 (observation) |

> The lab was built to answer one question and it answered it: **a
> simulation-mode DLP match does not function as an IRM triggering event.**
> The finding is not the absence. The finding is that every precondition
> demonstrably occurred — Purview recorded the match, timestamped, in its own
> report — and 49 hours later three independent surfaces show nothing, while a
> live health evaluator reports the policy's only problem as an unconfigured
> badge reader. **Selector accepts, runtime rejects, no feedback anywhere.**

---

## 1. Objective

The insider-risk assignment creates an insider risk policy. This lab treats the assignment as an
instrument, and the instrument is the *trigger*: IRM policies do nothing until a
triggering event fires, and the wizard offers "User matches a DLP policy" as the
first-class option. Lab 14 had just produced a DLP policy. Pointing one at the
other is the obvious build — and the wizard's own fine print says it should not
work.

Three questions:

1. **What does IRM ship with?** (the indicator baseline before anything is
   enabled — `POS-063`)
2. **What does the Data leaks template configure, and what does the trigger
   selector let through?** (`POS-064`)
3. **Does it fire?** (49 hours of observation across three surfaces —
   *configured is not the same as effective*, and this lab does not get to claim
   either until the reads land)

Cost: none. IRM is E5-trial-bound. The one metered path — exfiltration trigger
activities carrying a pay-as-you-go banner — was not taken (divergence row 90).
Analytics was left OFF by decision; its cost is a 48 h first scan, not money.

## 2. Predictions

**Recording gap, stated rather than papered over:** this lab's pre-build
predictions were made in a prior session and only `P15-2` survived into the
session that observed the results. `P15-1` existed and its text is lost. It is
not reconstructed here, because a prediction rewritten after seeing the outcome
is not a prediction.

| # | Prediction | Status |
|---|---|---|
| P15-1 | *text not preserved across session transfer* | withdrawn from the record rather than reconstructed |
| P15-2 | The trigger does **not** fire, with two independent candidate blockers — (a) simulation-mode matches do not count; (b) the wizard's stated High-severity incident-report requirement is unmet, since ours carries template defaults. A null is the expected result and is publishable as *"selector accepts, runtime rejects, no feedback anywhere."* If an alert **did** fire, the fine print is wrong-or-looser-than-written — the bigger finding | ✅ **CONFIRMED** — null at +25 h and +49 h on all three surfaces. Two further blockers surfaced during observation and are recorded in §5 |

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Role-group grant | Full **Insider Risk Management** group (17 roles) to the standing GA | Narrower groups (Analysts, Investigators); expiring assignment | The alert surfaces are the measurement; a narrower grant risked confounding a null result with a permission failure. Expiration existed and was declined — the grant is recorded permanently in `POS-061` instead. The cost of this choice is `POS-065` |
| Org indicators | Microsoft's **pre-selected recommended set**, accepted verbatim | Hand-select; enable everything; enable nothing | The wizard forces the dialog and pre-selects; accepting is the default-operator path, which is what this repository measures. `POS-063` |
| Analytics | **OFF** | On | It would supply the greyed-out RECOMMENDED threshold option. Cost measured: 48 h first scan. Left off deliberately, and the consequence — thresholds fall back to Microsoft-provided — is recorded rather than avoided |
| Trigger scope | `Lab14-USFinancial-Simulation` **only** | All five tenant DLP policies; a different policy | One trigger, one variable. Scoping to the simulation-mode policy is the entire experiment |
| Insider risk settings | **Skipped** | Configure | Microsoft's own checklist marks it REQUIRED. Skipping it is recorded as an omission (`POS-064`), not presented as a choice that was fine |

## 4. Build

Portal-only; IRM exposes no CLI surface for policy creation. All times PDT
2026-08-03.

| Time | Action |
|---|---|
| 07:50 | Admin added to the **Insider Risk Management** role group. Seven-group family measured, all empty before (divergence row 91) |
| 07:52 | **Unrequested**: `PurviewRoleAssignmentMigrator` assigns the Entra directory role `Purview Workload Content Reader`, outside PIM (`POS-065`, row 93) |
| ~08:0x | Propagation check — stale banner still rendering (row 88) |
| ~08:45 | Org indicator enablement via the wizard's forced dialog — 45 of 103 accepted as pre-selected (`POS-063`). *Exact minute never captured; approximate by acknowledgement* |
| 08:52 | Policy created: `Lab15-DataLeaks-DLPTrigger` (`POS-064`) |
| 09:11 | Trigger email sent — subject `LAB15 TRIGGER TEST`, admin → labuser, the standard six-line synthetic payload |

Policy configuration as built: template **Data leaks**; all users, no exclusions;
priority content = the three Lab 14 SITs (ABA Routing, Credit Card, US Bank
Account); scoring = all activity (default); trigger = **User matches a DLP
policy** → `Lab14-USFinancial-Simulation` only; indicators 39/103 auto-selected
from the org set and kept; thresholds Microsoft-provided; notifications
first-alert **ON**, high-severity off, weekly off.

Policy listed within ~1 min — the wizard's "few minutes" claim beaten — with
`Status: Healthy`.

## 5. Validation

A policy in a list is configuration. An alert is evidence.

| Check | Method | Expected | Result |
|---|---|---|---|
| Trigger precondition occurred | Lab 14 simulation report, Items for review grid | The trigger email matches the DLP policy | ✅ **`LAB15 TRIGGER TEST.eml`**, Exchange, **Aug 3 2026 4:11 PM UTC** (= 09:11 PDT), Low volume rule, U.S. Bank Account +1 more |
| IRM alert raised — surface (a) | IRM → Users → Alerts (preview) | Per `P15-2`: nothing | ❌ **0 items**, both reads. `Time detected (UTC)` filter chip confirms a labelled surface |
| IRM alert raised — surface (b) | Admin mailbox, first-alert notification (toggle ON) | Per `P15-2`: nothing | ❌ **No IRM notification**, Focused and Other, both reads. Mailbox took zero delivery in the 20 h between reads — genuine non-delivery, not needle-in-noise |
| IRM alert raised — surface (c) | IRM → Policies grid + flyout | Per `P15-2`: nothing | ❌ `Active alerts` **0**, `Last alert` **"No alerts yet"**, both reads |
| Two-read rule | Reads at +25 h and **+49 h** — double Microsoft's stated 24 h floor | Second read confirms or overturns | ✅ Confirmed on all three surfaces, every field byte-identical between reads |

**Verdict: `P15-2` holds.** A simulation-mode DLP match does not function as an
IRM triggering event.

### The candidate causes — one null, four candidates, not four rejections

The null is one event. These are candidate **causes**, not a stack of
independent rejections — and they are not co-equal, because at least one would
**preempt** the others:

| # | Candidate | Status |
|---|---|---|
| (c) | **`Users in scope` = 0** — persistent across 49 h | **LEADING.** If the policy had no scored population, the trigger was never evaluated, and (a) and (b) never got the chance to reject anything. Discovered during observation, not predicted (row 83) |
| (a) | Simulation-mode matches do not count as triggering events | Predicted (`P15-2`). Only reachable if (c) is false |
| (b) | The wizard's stated **High-severity incident report** requirement is unmet | Predicted (`P15-2`). The selector never enforced it (row 84). Only reachable if (c) is false |
| (d) | Non-evaluation upstream of all three | Cannot be distinguished from (c) from any available surface |

**And (c) itself is not certain.** The grid reads `Users in scope: 0` while the
flyout on the same screen reports coverage of *all active users* at High (row
83). Two surfaces, one field, and this repository has no third surface to break
the tie. So the leading candidate rests on choosing which of two contradictory
readings to believe — the persistent one, over 49 h, on the field named for the
question — and that choice is recorded here as a choice.

**Resolved by read, 2026-09-01:** the IRM **Users** page renders **0 items**, empty state "You don't have any risky users yet", with columns for insider risk severity, active alerts, confirmed violations, case and policy — a **risk-activity list, not a scope roster**. The contradiction resolves definitionally: zero rows and "all active users covered" describe different populations, and both historical readings stand. The question as originally posed — whether that page enumerates
the scoped population directly — is answered: it does not. The historical contradiction
(policy scope reading all active users, the Users page showing zero rows) was two
surfaces describing different populations, not a malfunction, and no further read is
required.

What is not in doubt: the trigger's precondition occurred, and nothing
downstream followed. The mechanism is open.

## 6. Failures & Fixes

Nothing broke. Two method errors, recorded:

- **The org-indicator save minute was never captured.** `POS-063` carries
  `~08:45 PDT, approximate` and says so. Wall-clock capture at the moment of
  each state change is not optional; it was skipped once here and the entry is
  permanently weaker for it.
- **`P15-1` was lost across a session transfer.** Reconstructing it after the
  fact would have produced a prediction that could not fail. It is withdrawn
  instead.

One near-miss corrected in the session: the observation reads were nearly
stamped from conversation position rather than from wall clock. They carry
`~10:35 PDT 2026-08-05, approximate — derived from a stated wall clock, not
captured per-read`.

## 7. Analysis

**The null is the strong result, and only because the precondition is
provable.** An empty alerts grid on its own is weak evidence — the match might
never have happened. Lab 14's report closes that hole: the trigger email matched,
at a timestamped minute, under a named rule, with per-SIT attribution. So the
sequence is not *nothing happened*. It is: the event occurred, was recorded by
the product that recorded it, and the product downstream of it produced nothing
and reported no reason.

**Three surfaces, and the one that talks is wrong.** Alerts (preview) says
nothing because there is nothing. The mailbox says nothing for the same reason.
The Policies grid *does* speak — and what it says is that the policy's problem is
an unconfigured physical badging connector. The health job is live; its
last-updated stamp moved between reads. It has evaluated this policy repeatedly
across two days and each time reported the one thing it can enumerate rather
than any of the four things that are actually wrong (row 87).

**The same page contradicts itself about the only number that matters.** The
grid reads `Users in scope: 0`; the flyout, on the same screen, congratulates the
operator for covering *all active users* with the gauge on High (row 83). Fifty
hours of stasis makes the 0 structural rather than propagation, which promotes it
from candidate to leading explanation — and means the celebratory message is
attached to a policy with no population.

**`Policy alert effectiveness: 0%`** completes the picture: a computed metric
over an empty set, rendered as a definite number, on a policy that never had the
opportunity to be effective.

**What an analyst inherits.** A policy that passes every configuration-time
check — valid template, valid scope, valid trigger, `Healthy` on save, listed in
under a minute — and cannot fire. IRM warned about latency twice (row 86) and was
correct and insufficient: the stated 24 h floor bounded nothing, because the
blocker was never temporal. The one warning the product does raise is about a
feature nobody enabled.

**Two patterns extended.** The cross-product side-effect grant at 07:52
(`POS-065`) is the second instance of one product provisioning state in another
without being asked — Lab 16 holds the first. And the GA-insufficiency family
gained a member that runs the other way: an automated process *added* privilege
that still does not satisfy the role Purview demands elsewhere.

**Converted to a decision, 2026-09-01** (`PC-REM-01`, Reviewer-locked). The premise changed under measurement: the role-group store no longer carries the recorded names (69-group census), while `Purview Workload Content Reader` exists in the **Entra directory-role** store and is already held by the admin identity — which also holds Global Administrator, confounding any visibility comparison. An unconfounded read would require a role mutation on a non-GA identity. **Scope measured:** current role-group census; Entra role-store presence; the admin assignment; the GA confounding state. **Scope not measured:** the visibility effect of that role alone on an unprivileged identity. **Reopening trigger:** a separately authorized role-isolation test on a non-GA identity with assignment/removal and restoration controls. The question as originally posed — whether holding `Purview Workload Content Reader` changes what
the DLP match detail renders. Lab 14's Match summary demanded `Data
Classification Content Viewer` for sensitive-info details; the auto-granted role
is a different one. Whether the two are related or merely similarly named is not established; per the 2026-09-01 conversion above, the unconfounded comparison is not pursued in this repository.

**Retained as a measurement, not as a control.** `POS-064` is not a working
insider-risk capability and is not represented as one.

## 8. References

- Microsoft Learn — [Insider risk management policies](https://learn.microsoft.com/en-us/purview/insider-risk-management-policies)
- Microsoft Learn — [Insider risk management settings: policy indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators)
- Microsoft Learn — [Get started with insider risk management](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure)
