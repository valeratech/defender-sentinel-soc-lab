---
title: Identify and remediate risks with Microsoft Secure Score
date: 2026-07-27
artifacts:
  labs: ["06"]
  posture: [POS-031]
  divergences: [23, 24]
  kql: []
corrections:
  - "POS-031 / Lab 06 — 'invisible to the console' was too broad; Secure Score is a Defender console and sees the locally-set ASR rules perfectly."
---

# Microsoft Secure Score

> Two independent assessments of the same tenant existed for the first time —
> this repository's posture register, and Microsoft's own scoring of the
> identical configuration. Where they disagreed was the whole value.

## What was configured

Nothing. Secure Score is an instrument you read. Nothing was set, planned, or
risk-accepted; the queue was left untouched at 114 to address.

## What was established

**Baseline 2026-07-27:** 44.68%, 509.33/1140. Identity 16.49%, Data 77.78%,
Device 49.07%, Apps 40%. Peer comparison 44.68 against 46.75. A thirteen-day-old
lab tenant with no MFA, no Conditional Access and no compliance policies scores
**two points below organisations of similar size** — which says more about the
baseline than about this tenant. `configuration-inventory.md` §12.9.

**Identity at 16.49% corroborates `POS-001`** from an independent direction —
Security Defaults off with nothing replacing it, and both top recommendations by
impact are MFA. The register said the identity posture was weak; Microsoft's own
instrument agrees.

**The score is a ratio, and the denominator moves.** It fell from 46.2% to 44.7%
on 07-19 with `Regressed = 0`. Nothing drifted — 56 further recommendations
became relevant that day as Defender for Office 365 came into scope. **A falling
Secure Score can be a licensing event rather than a security event**, and the
course guide's "regresses if configuration drifts" framing offers no way to tell
them apart. Read `Regressed` before reading the trend. Divergence row 23.

**The largest movement was discovery, not hardening.** 118 of 185 history
entries are dated 07-18, the day Lab 03 onboarded the endpoint — Defender
Antivirus 10/10, real-time protection 10/10, firewall 10/10, SmartScreen 9/9 and
a long tail besides. **Stock Windows 11 defaults being found, not work
performed.**

**Most of this project is invisible to it.** Labs 07 and 08 (ingestion) and Lab
09 (simulation) produced no movement at all. Correct — they are not
configuration controls in its model — but it bounds what the number measures.

**`Last synced` is per-recommendation**, and the page's blanket "up to 24 hours"
describes no particular row. One recommendation was still reporting against a
2026-07-25 evaluation two days after the underlying control changed. A status of
*To address* means the control is absent **or** the source product has not
re-read since it was added. Lab 09 §7.

## What was corrected

**`POS-031` and Lab 06 said locally-set ASR rules are "invisible to the
console."** Too broad, and disproved by counterexample. Secure Score is a
Defender console, names Defender for Endpoint as its product, and shows both
rules **Completed at 9/9**. Its history recorded the transition — 0/9 "has
become relevant" on 07-18, 9/9 "points gained by completing… Great work!" on
07-19, the day Lab 06 was built.

That transition also **settled the scope-versus-lag question by elimination**,
by a different route than the two verifications that had been pending: if the
configuration had never reached the Defender cloud, Secure Score could not have
logged it changing.

**The corrected finding is stronger than the original.** Not one console blind
to a local rule, but **two consoles in the same product, reading the same
configuration, disagreeing completely** — one reporting 18 rules off and zero in
block, the other awarding full points and timestamping the moment they were set.
Divergence row 24.

## What could not be tested

Whether Secure Score credits the audit-logging change (`POS-035`) — the
recommendation has not been re-evaluated since before the change was made, so
the prediction is not yet falsifiable rather than falsified.

## Cost

Zero.
