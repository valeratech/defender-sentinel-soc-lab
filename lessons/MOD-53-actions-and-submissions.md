---
module: 53
title: Manage actions and submissions
section: Configure Detections
verdict: concept
date: 2026-07-27
artifacts:
  labs: ["03", "09"]
  posture: [POS-040]
  divergences: [20, 21, 22]
  kql: []
corrections:
  - "Lab 03 — an empty Action center was never explained; the standard troubleshooting list omits the cause that actually applies."
  - "Lab 09 — '0% users reported' was ambiguous between 'did not' and 'could not' until the Report button was confirmed present."
---

# Module 53 — Actions and Submissions

> The lightest-looking module in the section, and it produced three findings
> that outlast the tenant. Nothing was configured — except by looking.

## What was configured

**Nothing, deliberately.** Every observation was read-only.

Except one, which *is* the finding: **opening the User reported settings page
created a tenant configuration object.** `DefaultReportSubmissionPolicy` did not
exist before the visit and does now. Nothing was saved; there is no Save for
what was done. `POS-040`, divergence row 22.

## What was established

**An alert is not an action.** Lab 03's detection ran an automated investigation
on a device under Full automation and logged zero remediation actions. Not a
misconfiguration — the test downloads from `127.0.0.1` where nothing is served,
so no supported action has an object to act on. Detection coverage and
remediation coverage are separate measurements, and `docs/attack-coverage.md`
measures only the first. Lab 03 §7, divergence row 20.

**The standard troubleshooting list is incomplete.** It gives two causes for an
empty Action center, both misconfigurations. The third — no remediable artifact
— is the one that applies, and following the list sends an analyst hunting a
fault that does not exist.

**Blank is not unset.** Report routing shows an empty mailbox field, which is
the documented default and resolves to the global admin's mailbox — displayed
nowhere until someone reports. The policy says *send to a customised address*
while the rule defining that address does not exist. The only way to learn where
reports go is to send one. `POS-040`, divergence row 21.

**Four inherited defaults, all silent on success** — no confirmation prompt, no
success message, no results email, positive reinforcement off. Correct reporting
behaviour receives nothing.

## What was corrected

**Lab 03** — the empty Action center had never been examined; it now carries the
explanation and the missing third cause.

**Lab 09** — "0% users reported" is confirmed behavioural, not structural. The
Outlook Report button is present with both options. And the exclusion is now
verified from both sides: platform denominators *and* an empty admin mailbox.
Platform-reported and independently observed are different grades of evidence.

## What could not be tested

The reporting mailbox is not a SecOps mailbox, which Microsoft flags as
important specifically when Attack simulation training is in use. Testing the
interaction would have falsified Lab 09's committed 0%.

## Cost

Zero. No VM, no Bastion, no ingestion.
