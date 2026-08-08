---
module: 80
title: Sentinel playbooks — deploy, authorize, and trigger
section: Configure Sentinel / automation
verdict: lab
date: 2026-08-08
artifacts:
  labs: ["19"]
  posture: [POS-081, POS-082, POS-083, POS-084, POS-085, POS-086]
  divergences: [136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153]
  kql: []
corrections:
  - "P19-1 predicted the automation rule would create cleanly and the playbook would silently never run. Sentinel refuses to create the rule at all — the permission is validated at authoring time (row 136)."
  - "P19-10 predicted Security Defaults were enabled and were what demanded MFA registration. They are Disabled and no Conditional Access exists; the requirement came from a Microsoft-managed registration campaign (row 149, POS-085). Reasoned from plausibility rather than read from the tenant."
  - "Claimed the playbook's SAS-signed callback URL could not be reached from the portal because it lives inside the Sentinel connection. It is two clicks away in Trigger history under a read-scoped link (row 139)."
  - "Claimed the pre-reset password still authenticated after the playbook's reset, and built a grace-behaviour finding on it. The old password was correctly rejected (50126). The real finding is that the forced-change ceremony accepted that same value as the new password (row 148)."
  - "Attributed a transient Client Error modal to an MDI/UEBA sub-component failing behind a generic handler. It did not reproduce on a second read; recorded as transient, cause unknown."
---

# Module 80 — Sentinel playbooks

> Nominally "playbooks are Logic Apps." Actually a lab about **identity**: one
> object with four identity relationships, each a separate grant that fails
> differently when absent — and about where a credential comes to rest once
> automation touches one.

## What was configured

One Consumption logic app in `rg-soc-lab` (West US 3, derived and locked from
the resource group), from the Microsoft template *Reset Microsoft Entra ID
User Password - Incident Trigger*. Three resources: the workflow and two
`Microsoft.Web/connections`. Diagnostics to `law-lab-01`.

Four grants: Sentinel Responder and Password Administrator to the workflow's
managed identity (`POS-081`), delegated Office 365 OAuth as `admin`
(`POS-083`), and Sentinel Automation Contributor to the `Azure Security
Insights` service principal (`POS-082`). Automation rule
`LAB-AutoReset-Bruteforce-Password` at Order 3, joining Lab 18's Orders 1 and
2 on the same analytic rule.

## What was established

**The launch permission is validated at authoring time.** Withholding
Automation Contributor did not produce a silent no-op at run time — Sentinel
refused to create the automation rule, ARM `BadRequest`. The identical form
resubmitted after the grant succeeded. Clean causal isolation, and the lab's
headline (row 136, `POS-082`). The same blade's playbook dropdown offered the
playbook anyway, directly above text explaining what unavailability would
mean: two checks disagreeing in one form.

**Over-permission kept a credential out of an incident.** `HTTP - get manager`
rides the same managed identity granted Password Administrator for the reset;
nobody granted directory read for it. It returned 200, so the true branch ran.
Had the role been narrower the run would still have read `Succeeded` and the
`else` branch would have written the plaintext password into the Sentinel
incident comment (row 144, `POS-081`). The degraded path is the leaky path.

**One credential, three resting places, one rotation.** Run history at 90 days,
`admin`'s Inbox *and* Sent Items, and the account. `Secure inputs`/`Secure
outputs` are absent rather than false, and Graph returned the full user object
— including a phone number — for want of a `$select` (row 145, `POS-084`).
Rotation cleans the account only, which is why Lab 19 §5 records the rotation
and the exposure separately.

**The audit trail misfiles the one action that mattered.** Three automation
rules read `Automated`/`Completed`; the playbook's comment reads `Manual` with
no status (row 146). **And the remediation is reversible in one step** — the
forced-change ceremony accepted the password the reset had just invalidated
(row 148).

**Unconfigured and in force.** Security Defaults off, zero CA policies, and
MFA registration demanded anyway by a Microsoft-managed registration campaign
whose state the tenant does not own (row 149, `POS-085`). The repository's
usual shape is *configured and ineffective*; this is its inverse.

Six further surface findings — three run-history views, a permanently `--`
`Workflow URL`, a `Fired: False / Succeeded` registration row, an 11-vs-4
action count, four surfaces truncating one entity, and seven sign-ins under
three request IDs — are rows 139–142, 152, 153.

## What was corrected

Five, listed in `corrections:` above. Two were predictions written before
measurement and disproved by it, which is the mechanism working. Three were
claims made *during* the session with more confidence than the evidence
carried — the callback-URL reachability claim, the old-password reading, and
the modal attribution. Those three are the ones worth noticing: each was
plausible, none was read from the tenant before being stated.

## What could not be tested

**P19-7** — that a notification failure still leaves the user reset with no
delivered credential. Structurally confirmed from the definition; not
exercised, because nothing failed. **Row 143's multi-account case** — the
shared-password defect is latent, and this incident carried one account
entity. **Row 148's mechanism** — three candidates, none isolated, and
isolating them means deliberately cycling passwords on a live account.
**`POS-084`'s generator weakness** — the ~1.5% all-numeric complexity failure
is arithmetic, and n=1. **Playbook Operator** — never granted; manual-run
remains out of scope, though the `Run playbook` control renders regardless.

## Cost

Logic Apps Consumption: one run, eleven actions, two API connections — below
the free grant at this volume. The meter is open and was opened knowingly.
The wall clock: two days across two sessions, of which the measurable part was
**5.05 seconds** of execution and **12 m 47 s** from trigger to run start.
