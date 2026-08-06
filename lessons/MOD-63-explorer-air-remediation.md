---
module: 63
title: Investigate, respond, and remediate threats with Defender for Office 365
section: Respond to alerts and incidents in Microsoft Defender XDR
verdict: lab
date: 2026-08-01
artifacts:
  labs: ["13"]
  posture: [POS-056, POS-057]
  divergences: [53, 54, 55, 56, 57, 58, 59]
  kql: []
corrections:
  - "The email entity page's empty Policy field was written up as a sixth-surface failure; the header's CAT:NONE shows the field is correctly empty. Withdrawn to an open question."
  - "Log (0) on a completed investigation was nearly recorded as a finding; the counter read Log (4) minutes later with no action taken."
---

# Module 63 — Explorer, AIR, and What the Action Center Holds

> Built on Lab 12's four messages rather than beside them. Known provenance
> turned an investigation tool into something gradeable — and grading it closed a
> thread open since Lab 03.

## What was configured

Nothing persistent. Two response actions submitted against one message and then
undone: an automated investigation, and a soft delete that was restored.

The tenant ended where it started. Two investigations and one Action Center
record remain as immutable history — investigations are not user-deletable, which
is correct for a forensic artifact and worth knowing before creating test ones.

Zero cost.

## What was established

**The Action Center holds remediations, not investigations** (`POS-056` context,
row 53). AIR ran, appeared on the investigations page, and produced **no Action
Center entry on either tab**. A soft delete against the same message produced one
immediately — Approval ID, Decision, Decided by, Status.

That closes `MOD-53`. Lab 03's empty Action Center was attributed to *no
remediable artifact existed*, and this confirms it independently from a second
product scope: **an investigation that finds nothing has nothing to send there.**
Not a fault, not a mystery. Prediction 3 was falsified and the falsification is
the result.

**PROPAGATION IS A SECOND THROUGH-LINE** (row 55). The first is *identify the
surface before trusting the answer*. This is its twin: **check whether the
surface has finished answering.**

`Log (0)` → `Log (4)`, same investigation, same page, no action taken, minutes
apart. A parenthesised count is about as unambiguous as a UI gets — not a blank,
not a spinner, a stated quantity — and it was wrong, and it corrected itself
silently.

Five instances now, twelve days to a few minutes: Exchange hydration
(`POS-036`), group membership to transport, threat policy application, Explorer
indexing (row 50), and this. The last two are the dangerous kind. They do not
render as missing; they render as **a confident zero**.

**The rule: a zero is a claim about the index, not about the event.** An absence
needs a second identical query before it goes in a file. And Microsoft *knows* —
the soft-delete confirmation warns "several minutes"; the Explorer export, the
`Log` counter and group replication warn nothing. The pattern exists and is
applied inconsistently, and the surfaces that omit it are the ones that have
produced wrong conclusions here.

**Every action generates the next artifact.** Submitting an investigation created
an alert (`Admin triggered manual investigation of email`, Informational,
`Category: Probing`, Resolved, no incident). Submitting a remediation created a
second investigation. Anyone auditing this tenant's alert volume later will find
alerts describing administrative activity rather than threats.

**The Approval ID is an identifier, not a gate** (row 53). The remediation landed
in **History**, never Pending, already `Approved` and `Completed`, `Decided by`
its own submitter. `Action source: Manual office action` is presumably what
separates it from an AIR-proposed action that would await a decision.

**Remediation is reversible by the person it was taken against** (`POS-057`,
row 59). Soft delete executed, Action Center read Completed, and the mailbox
owner restored the message from their own Outlook client in two clicks with no
notification to the operator. Documented behaviour, correct behaviour — but the
wizard offers four adjacent radio buttons and neither it nor the guide says
**who** can recover. In the case remediation exists for, a compromised mailbox,
that is the difference between a control and a gesture.

**The all-powerful account cannot read the message** (`POS-056`). Global
Administrator cannot preview or download delivered mail; that requires a separate
Unified RBAC permission. Every prior entry treats the single standing GA as a
**risk** — this shows it is also **insufficient**, which is an argument the
register has not made before.

**"How long did this take" has four answers** (row 57). One message:
`EndToEndLatency` 3.25 s, Header Analyzer headline 4 s, message trace 5 s, and
the analyzer's own hop timestamps 18 s. The headline sums inter-hop delays and
silently drops 14 seconds of sender-side queueing. This vindicates Lab 12's
withdrawn latency finding from the other direction — those were never independent
measurements and they do not measure the same interval.

**The same four counted three ways** (row 56). `Action count: 4` in the grid is
`Entities analyzed (4)` in the graph, alongside `Log (4)` — two different fours
that coincide. Only the Log tab states what was actually done: four reputation
lookups, of which **File Hash Reputation consumed 55% of a 9-second
investigation**.

**Microsoft's header analyzer cannot parse Microsoft's headers** (row 58).
`DIR:INB` and the entire `ARA:` list return as `Unknown fields`, and in the
`Other` section values appear stripped of their names — **`SA`, the single most
decisive field in Lab 12, sits there as a bare unlabelled string.**

## What was corrected

**The entity page's `Policy` field.** It reads `-`, beside `Policy type: Unknown`,
and was written up as *the surface built to name the policy reports Unknown* — a
sixth-surface finding sharper than Lab 12's.

The Message Header Analyzer disproved it within the hour: it parses `CAT:NONE`
from the raw header as **Protection Policy Category: NONE**, and the `Policy`
field sits among Exchange Transport Rule(s), DLP Rule(s), overrides and connector
— a cluster about *verdicts and dispositions*, not about which scanner ran.
Nothing decided this message's fate because it was clean, so the field is
**correctly empty**.

Withdrawn to an open question, and untestable here: all four messages were
delivered clean, so none ever received a filtering verdict. Lab 12's finding is
unchanged — no surface names the acting policy, six deep now — but the entity
page is not *failing* to.

Seventh instance in two days of fitting an ambiguous observation to a thesis
already in hand. **Having a strong thesis makes every empty field look like
evidence for it.**

**`Log (0)`** was flagged as odd and nearly recorded. See above.

## What could not be tested

**Foreclosed by clean inputs.** Whether the entity page's `Policy` field
populates for a message that received an actual filtering verdict. Every message
this repository holds was delivered clean.

**Open, testable.** Whether the second investigation's 7× longer run is
attributable to `File Hash Reputation` on a globally novel file — its own Log tab
answers this, and it would be the Lab 12 novelty variable reappearing in an
unrelated subsystem.

**Open.** Whether an AIR-*proposed* remediation lands in **Pending** rather than
History, which would make the approval workflow real rather than a retroactive
stamp. Requires an investigation that actually finds something.

**Untested.** `Verdict: Suspicious` on the soft-delete record, against AIR's
`No threats found` on the same message nine minutes earlier. Most likely the
verdict describes the administrator's assertion rather than a detection — but
that needs a case where AIR itself found something.

**Deferred by design.** `docs/architecture/response-paths.md` now has its
Defender-native branch fully measured. It stays unwritten until modules 78–80
test the Sentinel-native branch, per the decision recorded in module 62.

## Cost

Zero. Both VMs stayed deallocated. Everything here is E5-trial capability,
expiring 2026-09-14 (extended once on 2026-08-06 from 2026-08-13).
