---
# Machine-readable header — consumed by scripts/build-attack-matrix.py
id: DET-003
name: Inbox forwarding/redirect rule created (authored alert policy)
status: active
platform: defender-xdr
rule_type: alert-policy
severity: medium
tactics:
  - TA0009
techniques:
  - T1114.003
data_sources:
  - MailRedirect
validated: true
---

# DET-003 — Inbox forwarding/redirect rule created

The first detection **authored in this environment** rather than supplied by a
vendor. `DET-001` was Microsoft's own endpoint detection test; `DET-002` was a
Microsoft-defined ASR rule. This one was designed, built, triggered, and verified
end to end — `LAB-BEC-Forwarding-Rule-Created`, a Microsoft 365 alert policy
(`POS-043`, Lab 10).

It is also the **first ATT&CK tactic beyond Execution** observed here.

## 1. Hypothesis

> If a user creates an inbox rule that forwards or redirects mail, the alert
> policy fires on the `MailRedirect` activity, generates an alert, correlates
> into an incident, and delivers an email to the configured recipient.

Confirmed in full, end to end, in **~4 minutes**.

## 2. Data Requirements

| Requirement | Value |
|---|---|
| Unified audit logging enabled | `POS-035` — enabled 2026-07-27, without it the activity is not recorded |
| Alert policy, enabled | `POS-043` |
| Licensed mailbox to act as subject | `labuser`, Lab 09 |
| Activity | `MailRedirect` |

**The audit dependency is load-bearing and was discovered in Lab 09.** Had audit
logging still been off, this detection would have had nothing to fire on.

## 3. Trigger

`labuser` creates an Outlook inbox rule with the action **Forward to** the admin
address. No malicious payload, no exfiltration — the rule forwards internally to
a mailbox in the same tenant. The technique is the *rule creation*, not the mail.

## 4. Validation — measured, 2026-07-28

| Event | Time (local, UTC-07:00) |
|---|---|
| Alert policy created and enabled | 19:09 |
| Inbox rule saved by `labuser` | 19:14 |
| Activity recorded (`2026-07-29 02:15:00 UTC`) | 19:15 |
| Notification emails delivered | 19:18 |
| **End to end** | **~4 minutes** |

Incident **ID 2**, Medium, `Active`, service source Office 365, detection source
MDO, one active alert.

## 5. What the trigger revealed that the design did not anticipate

**A built-in policy already covered this activity.** A Microsoft policy named
*"Creation of forwarding/redirect rule"* fired at Informational on the same
activity, same user, same timestamp. **Two alerts and two emails for one action.**
The tenant carries 49 alert policies, 48 of them built-in, and no check was made
before authoring a redundant one.

**Correlation absorbed the duplication.** One incident, not two — and it took the
*custom* policy's name and Medium severity rather than the built-in's
Informational. So the redundancy costs mailbox noise, not queue noise.

**The custom policy changed exactly one thing: severity.** Same activity, same
detection, same notification text. `Details` in both emails is identical, so that
string is a property of the **activity**, not of the policy — the authored
description carrying the MITRE reference appears nowhere in the notification and
exists only in the portal.

## 6. Tactic mapping — and a disagreement

MITRE places `T1114.003` under **Collection (TA0009)**, version 1.4, last modified
October 2025, with **Microsoft Security and MSTIC among the listed contributors**.

Defender categorised the resulting incident as **Initial access**.

This matrix follows MITRE. The disagreement is recorded rather than resolved:
Defender's incident `Categories` field may not be a MITRE tactic mapping at all —
"Initial access" is a MITRE tactic name, which makes it look like one, but it may
be Microsoft's own kill-chain taxonomy borrowing the vocabulary. **The labels
disagree; whether that is a mapping disagreement or two taxonomies sharing words
is not established.**

Both readings are defensible on the behaviour: a forwarding rule is frequently
*established* during initial access and *serves* collection thereafter.

## 7. Tuning

Not tuned, deliberately — the policy is unconditioned and scoped to All users so
that a single deliberate trigger would fire it. In production this is exactly the
policy §8 of the source guidance warns against: unconditioned, all-user, every-time,
with **no daily notification limit** (`POS-043`). Scope by user or condition, cap
the notifications, and check the built-in policies before authoring a custom one.
