---
title: Run playbooks on on-premises resources
date: 2026-08-08
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections: []
---

# Run playbooks on on-premises resources

> A boundary guide, and the footnote Lab 19 left open. The template deployed
> there is named `Reset Microsoft Entra ID User Password` — the scope limit is
> in the product name. This evidence note answers the question that name raises: what
> happens when the compromised account's authoritative identity lives in
> on-premises Active Directory. A Logic App connector cannot reach a domain
> controller. Not a permissions problem, not a licensing problem — nothing
> on-premises is listening.

## What was configured

Nothing, and nothing could be. This is the first guide in the project whose
execution was foreclosed by a **missing precondition** rather than by cost or by
judgment: the premise is a machine behind a firewall, and this tenant has none.

## What was established

The chain for an on-premises action is **incident → automation rule → playbook
→ job against an Automation account → runbook → hybrid runbook worker → local
resource**. The playbook orchestrates and passes context; the runbook is the
hands; the worker supplies the network position. Splunk mapping: the hybrid
runbook worker is Splunk SOAR's **automation broker** — on-premises component,
outbound-only, polling for work so that no inbound firewall rule is needed.

Verified against Microsoft Learn 2026-08-08 (not observed in this tenant):

- **Extension-based (V2) is the only supported platform.** Agent-based (V1)
  retired **31 August 2024**; all jobs on V1 workers stopped **1 April 2025**.
  Creating new V1 workers stopped being possible **1 November 2023** — a
  three-stage retirement, not a single date.
- **Arc is the admission ticket.** Non-Azure machines reach the extension
  framework only through the Azure Connected Machine agent, as Arc-enabled
  servers or Arc-enabled VMware vSphere.
- **Polling, not push.** Each active worker polls every **30 seconds**,
  first-come-first-serve; you target a *group*, never a member. If no worker in
  a group has pinged in **30 minutes** the group has no active workers and jobs
  suspend after **three** retry attempts.
- **Worker jobs run as local `System` on Windows, `nxautomation` on Linux.**
  This is the security argument in one line: runbook edit rights in the
  Automation account are SYSTEM on every worker the account dispatches to.
- One machine hosts one worker reporting to one Automation account; 4,000
  workers per account.

Asserted, not verified today: the outbound-HTTPS/443 detail. Learn's overview
defers it to the Automation network-configuration page, which was not read.

Incidental: Learn's own page disagrees with itself on whether Arc-enabled
VMware vSphere is preview — unmarked in the platform table, marked preview in
the scenarios list. One object, two surfaces. Recorded, not chased.

## What was corrected

Nothing shipped from this walkthrough and was disproved.

## What could not be tested

**Cannot be tested here**, not merely untested — three independent blockers:

1. **No on-premises resource exists to reach.** No local AD, no domain
   controller. The source guide's premise is what is missing, not the mechanism.
2. **Arc-enabling the only candidate host is sanitization-hostile.** It would
   project a personal machine into the tenant as a named Azure resource, putting
   a `.pii-terms` term into resource IDs, Activity log, and every subsequent
   capture.
3. **The available substitute inverts the premise.** Installing the extension on
   an existing Azure lab VM — the rejected alternative — would demonstrate
   extension, group and polling, but an Azure VM reaching an Azure resource is
   not reaching *past a firewall*, which is the entire point. Rejected at
   compute cost for a demonstration of the wrong thing.

The boundary is also softer than the source guide implies. With Entra Connect and
password writeback, an Entra-side reset **does** propagate to on-premises AD, so
the runbook path is unnecessary for that specific action. It becomes necessary
where there is no writeback, where on-premises is authoritative, or where the
action is not a password at all — restart a local service, retrieve a file, run
a script on a physical host. Password reset is the weakest example of the
pattern.

## Cost

$0. Nothing was provisioned.

Recorded against the pre-assessment, which gave the skip reason as *infeasible +
metered*: **metered does not hold.** Azure Automation bills process automation
by job runtime above a free monthly allowance, and the Automation account itself
carries no charge to create or maintain — a lab-scale runbook demonstration
costs nothing. The meter, had this been built, would have been the compute the
worker runs on, not Automation. The verdict is unchanged; the reason is
corrected before it shipped.
