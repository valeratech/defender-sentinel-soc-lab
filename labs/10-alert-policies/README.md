# Lab 10 — Microsoft 365 Alert Policies

| Field | Value |
|---|---|
| **Domain** | Detection |
| **Objectives** | Author a detection rather than run a vendor's; trigger it deliberately; measure the full path from activity to alert to incident to notification |
| **Depends on** | Lab 09 (`POS-035` — unified audit logging; without it there is nothing to detect on), Lab 00 (E5 licensing) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-28 |

> The first detection **authored** in this environment rather than supplied.
> `DET-001` was Microsoft's endpoint test, `DET-002` a Microsoft-defined ASR rule.
> This one was designed, built, fired, and measured — and the trigger immediately
> disproved part of its own design.

---

## 1. Objective

Three of the guide's eight sections describe creating an alert policy. None
describes firing one. This repository's `docs/attack-coverage.md` draws exactly
that line — a rule that has never fired is **CLAIMED**, not **COVERED** — so the
lab is the trigger, not the wizard.

Secondary objective, chosen for cost: an activity that could be triggered by hand
with **both VMs deallocated**. Alert policies watch Microsoft 365 activity rather
than endpoints, so the whole cycle runs at zero cost.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Mechanism | **Alert policy** | Custom detection rule; Sentinel analytics rule | The other two need KQL over endpoint data, and a live endpoint to fire against. Alert policies reach only Microsoft 365 activity — which is exactly why this one is free to trigger |
| Activity | **`Created mail forward/redirect rule`** | `User submitted email` | Self-triggerable, genuine BEC persistence, and maps to a **new ATT&CK tactic**. The alternative would have resolved `POS-040`'s open routing question instead — deferred, not discarded |
| Trigger logic | **Every time an activity matches** | Threshold (pre-selected); unusual volume | The portal pre-selects **threshold at 15 activities in 60 minutes**, which in a three-identity tenant would never fire. A deliberate single trigger needs first-occurrence firing |
| Conditions | **None** | Scope by user | Three identities; nothing to narrow. An unconditioned policy is the cleaner test — and the worse production choice, see §7 |
| Recipient | **Admin only** | Admin + `labuser` | `labuser` is the test subject. Alerting the observed party contaminates the mailbox under observation and is the wrong shape operationally |
| Notification limit | **No limit** (inherited) | A daily cap | A cap could suppress the very notification being measured. Recorded as an inherited default, not endorsed |
| Enabled on creation | **Yes** | Create disabled | An off policy is a claim |

## 3. Build

`Email & collaboration > Policies & rules > Alert policy > New alert policy` —
a **four-step wizard** (Name, Alert settings, Recipients, Review), where the guide
describes eight sequential items. Configuration recorded in `POS-043`.

**Licensing confirmed by observation.** All three trigger types rendered —
every-time, threshold, and unusual volume. The latter two require E5 or an add-on,
so their presence is a live confirmation of entitlement rather than an inference
from the SKU.

## 4. Validation

| Check | Expected | Result |
|---|---|---|
| Policy created and enabled | Listed, Custom, On | ✅ 19:09, Custom, Medium, enabled |
| Activity recorded | `MailRedirect` | ✅ `2026-07-29 02:15:00 UTC` |
| Alert generated | 1 | ❌ **2** — a built-in policy fired on the same activity |
| Incident created | ≥1 | ✅ **1** — correlation absorbed the duplicate |
| Notification delivered | 1 email | ❌ **2 emails** |
| End-to-end latency | *(unmeasured)* | ✅ **~4 minutes** |

Two rows failed against the design, and both are the findings.

## 5. Evidence

| Event | Time (local, UTC-07:00) |
|---|---|
| Alert policy created and enabled | 19:09 |
| Inbox rule saved by `labuser` | 19:14 |
| Activity recorded (`02:15:00 UTC`) | 19:15 |
| Both notification emails delivered | 19:18 |

Incident **ID 2**, `LAB-BEC-Forwarding-Rule-Created`, Medium, `Active`, service
source Office 365, detection source MDO, one active alert, categorised
`Initial access`.

**It reached Sentinel too** *(verified 2026-07-29)*. A workspace census the
following day returned `SecurityAlert: 2` and `SecurityIncident: 1`, timestamped
02:18–02:19 UTC — minutes after the trigger. So the detection travelled the full
path: Purview activity → Defender alert → XDR incident → Sentinel, over the
connector Lab 04 established.

That is also a **third independent confirmation of the duplicate**: two alerts and
one incident, seen in the portal, in the two notification emails, and now in the
workspace tables — three surfaces agreeing. And it costs nothing to carry;
`SecurityAlert` and `SecurityIncident` are not billable (Lab 08 §7).

The two emails are from `Office365Alerts@microsoft.com`: one Medium carrying the
authored policy name, one Informational carrying the built-in's name. **Same
activity, same user, same timestamp, identical `Details` text.**

## 6. Failures & Fixes

**The detection already existed.** A built-in policy — *"Creation of
forwarding/redirect rule"* — covers this exact activity and fired alongside the
authored one. The tenant holds **49 alert policies, 48 of them built-in**, and no
check was made before authoring a redundant one. The guide lists built-in policies
in its §5; the design read that section and did not act on it.

That is the more useful outcome. The tenant now generates **duplicate
notifications for a single action**, which is precisely the alert-fatigue problem
the guide's own guidance warns about, arrived at from the opposite direction:
not by writing a noisy policy, but by writing a *redundant* one.

**The duplication stops at the mailbox.** One incident, not two — and it took the
custom policy's name and Medium severity rather than the built-in's Informational.
Correlation is doing real work here.

**The authored description reaches nobody.** `Details` is identical in both
emails, so that string is a property of the **activity**, not the policy. The
description written for this policy — carrying the MITRE reference — exists only
in the portal. **Severity is the only field the custom policy actually changed.**

## 7. Analysis

**A rule that has never fired is a hypothesis.** The guide creates a policy and
stops; three of its eight sections are configuration and none is validation. The
distinction is the whole basis of `docs/attack-coverage.md`, and this lab is the
first time this repository has authored the rule as well as fired it.

**Check what already fires before authoring what fires.** Forty-eight built-in
policies were active in this tenant from day one, and the guide's §5 names them.
The design step that was missed is trivial — search the existing policies for the
activity — and its absence produced duplicate alerting on the very first custom
policy in the tenant. In a real SOC this is how alert fatigue starts: not from bad
policies, but from unexamined overlap with the ones already there.

**The pre-selected trigger would have produced a silent policy.** Threshold is
selected by default at 15 activities in 60 minutes. In a three-identity tenant no
threshold policy on any activity will ever fire, and the guide's own §8 notes that
most reports of "the alert policy isn't working" are timing or aggregation rather
than misconfiguration. A default that produces a policy which cannot fire, on a
page whose warning about that failure mode is three sections away, is a trap.

**Friendly labels are not schema values.** The picker offers *"Created mail
forward/redirect rule"*; the stored condition reads `Activity is MailRedirect`,
and `MailRedirect` is what appears in the alert and in the audit log. The label is
UI sugar over a schema value, and the schema value is the one you hunt on. Nothing
in the wizard tells you this — it surfaces only on the review page and in the
alert body.

**The scope boundary is visible in an empty list.** The activity picker offers
seven headers, and **"Common endpoint user activities" is empty** despite two
devices onboarded to Defender for Endpoint since Lab 03. Working hypothesis, not
established: Purview endpoint activities require devices onboarded to *Purview*,
which is a separate onboarding from MDE's. If so it is `POS-011`'s shape again — a
capability present, listed, and unreachable because a second thing nobody
mentioned was never done.
*(pending — Purview device onboarding state not checked)*

**This is the tenant's first working security notification path.** `POS-042`
records that Defender XDR has no notification rules at all: incidents, actions and
threat analytics tabs are empty, and the real incident Lab 03 produced on 07-18
told nobody. Alert policies are a separate, Purview-side mechanism, so this does
not contradict that finding — it sharpens it. **The capability exists in this
tenant; it just does not exist where the incident queue lives.**

**Tactic mapping, and a disagreement left open.** MITRE places `T1114.003` under
**Collection (TA0009)** — version 1.4, October 2025, with Microsoft Security and
MSTIC among the contributors. Defender categorised the incident **Initial access**.
`DET-003` follows MITRE. Whether Defender's `Categories` field is intended as a
MITRE tactic mapping at all is **not established** — "Initial access" is a MITRE
tactic name, which makes it look like one, but it may be Microsoft's own
kill-chain taxonomy borrowing the vocabulary. Both readings fit the behaviour: a
forwarding rule is often *established* during initial access and *serves*
collection thereafter.

## 8. References

- `POS-043` (the policy and its inherited defaults), `POS-035` (audit logging —
  the dependency without which this detects nothing), `POS-042` (the notification
  gap this sits against)
- `DET-003` — the detection spec; first ATT&CK tactic beyond Execution
- Lab 09 — where the audit-logging dependency was discovered
- MITRE ATT&CK `T1114.003`, Email Forwarding Rule (Collection, `TA0009`)
