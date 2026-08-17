---
title: What is Microsoft Security Copilot
date: 2026-08-08
artifacts:
  labs: []
  posture: []
  divergences: []
  kql: []
corrections: []
---

# What is Microsoft Security Copilot

> The vocabulary guide. It produces no tenant state, but every term the
> remaining guides spend — SCU, provisioned capacity, inclusion, agent,
> promptbook — is defined here. Its practical contribution to this project is
> a single unanswered question it makes askable: whether this tenant already
> holds capacity it did not provision.

## What was configured

Nothing. The source guide is descriptive throughout.

## What was established

**One product, two names.** Generally available April 2024 as *Microsoft
Copilot for Security*, since renamed *Microsoft Security Copilot*. Both names
circulate in current documentation and refer to the same product — expect the
older form in older material and in some portal strings.

**Two experiences, one capacity.** The standalone portal
(`securitycopilot.microsoft.com`) carries the full chat canvas, promptbooks and
session sharing; embedded surfaces appear inside Defender, Entra, Intune,
Purview and Sentinel. Embedded is not a separate licence — both draw on the same
capacity. Agents (phishing triage, access review, and others, several in
preview) draw on it too.

**Copilot inherits the analyst's permissions.** It authenticates on-behalf-of
the user and cannot reach past a boundary the user could not cross. It widens
what an analyst can *process*, not what they are *permitted to see* — so RBAC
state directly bounds Copilot's usefulness per analyst. This is the fact that
connects the source guide to the rest of the repo: every scoped-access finding already
recorded is also a Copilot finding.

**Generated KQL is a draft.** Natural-language-to-KQL lowers the floor for query
authorship without removing the need to read the query, confirm it targets the
right tables, and catch confident errors. Recorded because the failure mode —
trusting a fluent query against the wrong table — is the same shape as the
surface-identification problem this project keeps hitting.

**Billing, verified against Microsoft 2026-08-08 (not observed in this tenant):**

- Provisioned SCUs bill at **$4 per SCU per hour**, overage at **$6**, minimum
  one provisioned SCU. Continuous operation of a single SCU is roughly
  **$2,900/month**.
- Billing runs in **clock-hour blocks against provisioned capacity**, not
  elapsed 60-minute periods, with a one-hour minimum. Any usage inside an hour
  bills as a full unit regardless of start or stop time, and provisioning twice
  within one clock hour bills twice.
- **M365 E5 / E7 inclusion:** 400 SCUs per month for every 1,000 **paid** user
  licences, capped at 10,000, scaling down proportionally below 1,000. Eligible
  tenants are auto-provisioned with no Azure setup. The pool resets monthly and
  does not roll over.
- The inclusion capacity is a tenant-wide **Default Security Copilot Capacity**:
  created automatically with a default workspace, **not modifiable**, not billed
  hourly, and any cost values the UI shows against it are **informational, not
  charges**.

## What was corrected

Nothing shipped from this walkthrough and was disproved.

Noted before it shipped: the guide states that exhausting the included pool
means throttling until reset. Microsoft's current wording is weaker — usage
beyond the allocation *will be* throttled at a future date, with a $6-per-SCU
pay-as-you-go option available then and 30 days' advance notice. The present
consequence of overrun is undocumented rather than defined.

## What could not be tested

**The inclusion question is open, and it is a tenant question, not a
documentation question.** Microsoft's eligibility FAQ states that all E5 and E7
customers qualify with no minimum licence count, while the capacity formula is
denominated in **paid** licences. This tenant's E5 is a trial. The documentation
does not address trial licences either way.

Inference, labelled as such: no inclusion is expected here. Not recorded as a
finding until read at a surface.

Three documented detection surfaces, carried from Microsoft's FAQ and **not yet
walked** — paths to be replaced with observed ones when checked: the standalone
portal (a Default capacity already present versus a prompt to provision), a
Message Center post in the Microsoft 365 admin center, and in-product banners in
Defender, Entra, Intune or Purview.

The answer changes later guides rather than this one. If a Default capacity
exists, provisioning duplicates it and the deletion ceremony is
contraindicated — Microsoft advises existing customers who qualify for inclusion
**not** to delete capacity they previously provisioned.

## Cost

$0. Nothing was provisioned and no capacity was allocated.
