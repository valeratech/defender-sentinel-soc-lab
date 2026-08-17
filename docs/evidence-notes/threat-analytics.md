---
title: Analyze threat analytics
date: 2026-07-27
artifacts:
  labs: ["06", "03"]
  posture: [POS-041, POS-042]
  divergences: [25, 26, 27, 28]
  kql: []
corrections:
  - "Lab 06 §2 — 'PowerShell is the only available path' was an asserted absence; MDE security settings management is a second path and was simply switched off."
  - "Working hypothesis withdrawn — threat analytics is not a third console with an opinion on device configuration; its Recommended actions tab is Secure Score, filtered."
---

# Threat Analytics

> Nominally a reading exercise. It produced a correction to the deployment
> rationale behind this repository's most consequential finding, and a feature
> that a trial tenant structurally cannot reach.

## What was configured

Nothing. Two toggles were found off and **deliberately left off** — see below.

## What was established

**Threat analytics is not a third console.** Its *Recommended actions* tab is
Secure Score, filtered to the recommendations relevant to a given threat —
identical columns, identical rank numbers from the same global list, same
`Last synced`. It agrees with Secure Score because it *is* Secure Score. The
ASR disagreement remains two-way, not three-way.

`Misconfigured devices: 1` is explained by that tab: two of four
threat-relevant recommendations unmet on one device. Both unmet items are
ASR-family and both are **different rules** from the two Lab 06 configured — so
no contradiction, consistent with Secure Score.

**Threat analytics IOCs are structurally unreachable in a trial tenant.** The
guide describes tenant verification as a one-time administrative wait of "at
least an hour." It is in fact a **business identity check** demanding
incorporation documents, domain ownership records, and government-issued ID,
framing the operator as the organisation's legal representative. Not a licensing
gate and not a configuration gate — a legal-entity gate a lab has nothing to
satisfy. **Not started**, and the decision not to submit personal identity
documents to unlock a lab feature is itself the record. Divergence row 26.

**The guide's threat categories are the wrong field.** It lists eight —
ransomware, extortion, phishing, hands-on-keyboard and so on. The portal's
categories are seven and different: Activity, Actor, Core threat, Technique,
Tool, Vulnerability, OSINT. The guide's list is the **Threat tags** column.
Divergence row 27.

**Exposure level is ternary and recency-bound**, not the gradient the "Highest
exposure threats" panel implies. Values observed: `Not available`, `0 - Low`,
`30 - Medium`. Everything carrying a value was published in Jul 2026; the
unassessed block is the 2023–2025 back catalogue. **The panel ranks a recent
slice, and most of the 3,150-item library is not scored at all.** Divergence
row 28.

**Endpoints exposure is only half of what the guide describes.** It covers
missing updates — "no trackable vulnerabilities" here — while the configuration
half lives on a different tab. Two halves of one described feature, split.

**Defender XDR ships with zero notification rules** (`POS-042`). Incidents,
Actions and Threat analytics tabs are all empty. Nobody is emailed when an
incident is created, when a remediation action needs approval, or when a
relevant threat is published. Lab 03 produced a real incident on 07-18 and
nothing told anyone. The contrast worth keeping: the **Azure budget** alert path
is verified working. The cost control notifies; the security controls do not.

**Only two of a dozen-plus table columns are filterable** — Category and Threat
tags. An analyst wanting "everything targeting my industry" or "everything with
exposure above zero" cannot ask.

## What was corrected

**Lab 06 §2 asserted that local PowerShell was "the only available path"** for
deploying ASR rules, with Intune foreclosed by `POS-022` and no AD for GPO.
**Wrong, and never checked.** Settings → Endpoints → Enforcement scope offers
MDE security settings management, which applies to devices "not yet enrolled to
Intune" — this tenant exactly. It is off, and off is the shipped default
(`POS-041`).

The consequence is larger than a rationale. Policy-deployed rules are the class
the ASR report *can* see, so **`POS-031`'s headline finding exists because a
switch was off and openable, not because a path was closed.** A different
starting configuration would have produced no finding at all. Divergence row 25.

**A working hypothesis was withdrawn mid-walkthrough.** Threat analytics was expected
to be a third opinion on device configuration, resolving or extending the
Secure-Score-versus-ASR-report disagreement. It is not an independent opinion at
all. Recorded because a hypothesis that survives only until it is checked is
worth the same as one that survives — the checking is the point.

## What could not be tested

**Deferred deliberately**, not foreclosed: enabling Enforcement scope and
deploying the two ASR rules as policy is a direct test of `POS-031`'s mechanism.
It needs a device that can check in, and both VMs are deallocated, so it batches
with custom detections (`docs/evidence-notes/alert-policies.md`) and analytics rules (`docs/evidence-notes/analytics-rules.md`). Predict
before testing: policy-managed ASR may conflict with the locally-set rules
already on the endpoint.

**Structurally foreclosed:** threat analytics IOCs, per above.

## Cost

Zero. The only thing declined on cost grounds was nothing; the thing declined
was personal identity disclosure.
