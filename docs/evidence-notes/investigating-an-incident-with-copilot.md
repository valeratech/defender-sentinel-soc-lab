---
title: Investigating an incident with a Security Copilot prompt
date: 2026-08-09
artifacts:
  labs: ["20"]
  posture: []
  divergences: [158, 159, 160, 161]
  kql: []
corrections:
  - "P20-5 confirmed and exceeded. Copilot returned four typed identifiers for one entity - Account Name, Azure AD User ID, User Principal Name, and a User SID that appears on no portal surface documented in twenty labs - where four Defender surfaces render the single string `labuser`."
  - "P20-6 inverted. Predicted Copilot would inherit the portal's `Trigger: Manual` misfiling. It read past the defect and described the playbook correctly, then asserted no other automated actions existed while four `Automated`/`Completed` rows sat in the Activities tab."
  - "Withdrawn: the claim that `Plugins used: Microsoft Defender XDR` in usage monitoring confirmed the data source for all three prompts. It is a session-level rollup. Per-prompt expansion shows `Chose Incident Analysis` on prompts 1-2 and `Chose Microsoft Defender XDR` on prompt 3 - so the data path behind the four identifiers is not established."
---

# Investigating an incident with a prompt

> The measurement guide, and the only one in this project where the subject
> under test is an **answer** rather than a configuration. Pointing Copilot at
> a previously documented incident — ground truth *and* known portal defects
> already committed — is what converts the course's walkthrough into something
> falsifiable.

## What was configured

Nothing in the tenant. Three prompts against **incident 24** in the standalone
portal, 11:10–11:15 PDT.

## What was established

**Copilot read identifiers the portal does not render.** Asked to list entities
with full identifiers, it returned a typed table: `Account Name` `labuser`,
`Azure AD User ID`, `User Principal Name`, and **`User SID`** (`S-1-12-1-…`,
Entra-issued). Row 152 established that four Defender surfaces agree on
`labuser` because they render the same weak identifier, not because they are
right. Copilot is not bound by that display choice.

Framing that survives beyond this product: an **entity** is a typed object with
several identifiers, strong and weak. `labuser` is weak — ambiguous across
tenants. The portal displays the weak one; the store holds four. The Splunk
analogue is CIM normalization plus the Asset & Identity framework, and Sentinel
makes the binding explicit in an analytics rule's entity mapping.

**The correction and the erasure arrived in one answer.** Prompt 3 described
the playbook as an automated action triggered by the detection — contrary to
the incident audit trail, which files that one consequential action as
`Trigger: Manual` with empty status (row 146) while four cosmetic changes read
`Automated` / `Completed`. It then stated **`No other automated investigation or
follow-up actions were recorded`**. Four such rows exist. **It corrected the
mislabelled minority and erased the correctly-labelled majority**, and asserted
the absence positively rather than leaving it open.

**A status word answering a different question, at a new layer.** `detected on
… 18:47:30 UTC` is a correct conversion of **First activity**. Detection was
`18:57:27Z`. The ten-minute latency Lab 19 measured to the millisecond is
collapsed into the field an analyst reads as an SLA.

**`Export to Excel` sits on every table**, including the four-identifier one —
a one-click path from an AI answer to a file containing an object ID and a SID.

## What was corrected

Three, in frontmatter: P20-5 exceeded, P20-6 inverted, and the plugin-
attribution claim withdrawn.

## What could not be tested

**Whether the answers generalise.** One incident, one tenant, three prompts.
The entity result is strong because it contradicts four committed surfaces; the
omission result is one observation of one question.

**How Copilot reached the identifiers.** `Chose Incident Analysis` is a
capability name, not a data path. Whether it queries the same store the portal
renders from is unestablished, and the usage dashboard's rollup cannot answer
it.

**Whether the omission is deterministic.** Re-running prompt 3 would cost
another clock hour and was not attempted.

`(multiple runs)` on the playbook row is unexplained — the repo records one
execution.

## Cost

Three prompts consumed **1.5 SCU** against 1 provisioned; the excess was
absorbed, not billed (`POS-087`, row 156).
