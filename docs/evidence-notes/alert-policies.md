---
title: Configure and manage custom detections and alerts
date: 2026-07-28
artifacts:
  labs: ["10"]
  posture: [POS-043]
  divergences: [29, 30, 31, 32]
  kql: []
corrections:
  - "Design error caught by the trigger — the chosen activity was already covered by a built-in policy, and no check was made before authoring a redundant one."
---

# Alert Policies

> The first detection **authored** here rather than supplied. It fired in four
> minutes, and immediately disproved part of its own design.

## What was configured

`LAB-BEC-Forwarding-Rule-Created` — a Microsoft 365 alert policy on the
`MailRedirect` activity, Medium, unconditioned, all users, every-time trigger,
admin recipient, enabled on creation (`POS-043`).

Then triggered by hand: `labuser` created an Outlook rule forwarding to the admin
address. **No VM, no Bastion, no cost** — alert policies watch Microsoft 365
activity, not endpoints, which is why the whole cycle runs free.

## What was established

**A rule that has never fired is a hypothesis.** The guide devotes three of eight
sections to creating a policy and none to firing one. `docs/attack-coverage.md`
draws exactly that line, so the lab is the trigger, not the wizard. `DET-003` is
the first detection in this repository that was designed here rather than supplied
by Microsoft — and the first ATT&CK tactic beyond Execution: **Collection
(`TA0009`), `T1114.003`**.

**Measured end to end: ~4 minutes.** Policy enabled 19:09, rule saved 19:14,
activity recorded 19:15, both emails delivered 19:18. The guidance says "give it
time"; this is the number.

**The tenant's first working security notification path.** `POS-042` records
Defender XDR with no notification rules at all — the real incident from Lab 03
told nobody. Alert policies are a separate Purview-side mechanism, so this does
not contradict that finding, it sharpens it: **the capability exists in this
tenant, just not where the incident queue lives.**

**Licensing confirmed by observation** — all three trigger types rendered, and two
of them require E5 or an add-on.

**Three inherited defaults, all consequential.** The threshold trigger is
pre-selected at 15 activities in 60 minutes, which in a three-identity tenant can
never fire (row 30). The daily notification limit defaults to none, making an
unconditioned every-time policy an unmetered mail generator (`POS-043`). And the
policy description reaches nobody — both emails carry identical activity-level
text, so **severity is the only field a custom policy actually changes** (row 32).

**Friendly labels are not schema values.** The picker says *Created mail
forward/redirect rule*; the policy stores `MailRedirect`, and that is what appears
in the alert and the audit log. Third instance of name-depends-on-surface, after
`POS-034`'s two stores and the attack-simulation guide's PowerShell endpoint trap (row 31).

**The scope boundary is visible as an empty list.** Seven activity headers, and
*Common endpoint user activities* is empty despite two devices onboarded to MDE
since Lab 03. Hypothesis, unverified: Purview endpoint activities need a separate
Purview onboarding.

## What was corrected

**A built-in policy already covered the chosen activity.** *Creation of
forwarding/redirect rule* fired at Informational alongside the authored policy —
same activity, same user, same timestamp, **two alerts and two emails for one
action**. This tenant carries 49 alert policies, **48 of them built-in**, and the
guide lists them in its §5. The design read that section and did not act on it.

That is the more useful result. **Duplicate alerting appeared on the very first
custom policy created in this tenant** — which is how alert fatigue actually
starts: not from bad policies, but from unexamined overlap with the ones already
present. The missed step is trivial and now explicit: search the built-ins before
authoring.

The duplication stops at the mailbox — correlation produced one incident, and it
took the custom policy's name and severity over the built-in's.

## What could not be tested

**Deferred, not foreclosed:** `User submitted email` was the alternative activity
and would have resolved `POS-040`'s standing question about where reported mail
actually routes. Still available.

**Open:** whether Purview device onboarding explains the empty endpoint activity
group. And the tactic mapping disagreement — MITRE places `T1114.003` under
Collection with Microsoft among the contributors, while Defender categorised the
incident *Initial access*. `DET-003` follows MITRE; whether Defender's `Categories`
field is a MITRE mapping at all is **not established**.

## Cost

Zero. Both VMs stayed deallocated throughout.
