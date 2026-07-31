---
id: DET-005
name: Brute force attack against Azure Portal (Microsoft template, enabled)
status: active
platform: sentinel
rule_type: scheduled-analytics
severity: medium
tactics:
  - TA0006
techniques:
  - T1110
data_sources:
  - SigninLogs
  - AADNonInteractiveUserSignInLogs
validated: false
---

# DET-005 — Brute force attack against Azure Portal (Microsoft template)

Microsoft's own template, version 2.1.4, enabled from Content Hub with two
tuning changes (`POS-045`, Lab 11). **Deliberately overlapped with `DET-004`** so
that one trigger tests both.

**`validated: false` is the point of this entry.** The rule is enabled, correctly
configured, and has never fired. Under this repository's convention that makes it
**CLAIMED, not COVERED** — and it is why `TA0006` reads PARTIAL rather than
COVERED in the coverage matrix. An enabled rule is a hypothesis until something
proves it.

## 1. Why it did not fire

Presented with 7 failed sign-ins to `Azure Portal` — the exact activity it names —
on 2026-07-31, it produced nothing. The query requires:

| Condition | Query | Trigger produced |
|---|---|---|
| Failure count | `FailureCountBeforeSuccess >= 10` | **7** |
| Session shape | a **success** terminating the failure run | none |
| Deviation | `> 25` vs the user's 7-day failure baseline | not evaluated |

It failed on the first condition, so the deviation logic was never reached. That
part of the prediction is **untested, not confirmed**.

One anticipated objection was eliminated by measurement: `AppDisplayName` logged
as exactly `Azure Portal`, so the template's scope filter matched. It failed on
logic, not on scope.

## 2. Why it may be unable to fire here at all

`Deviation = abs(FailureCountBeforeSuccess - avgFailures) / avgFailures`, where
`avgFailures` is that user's failure *fraction* over 7 days. **Generating the
failures raises the baseline they are measured against.** In a three-identity
tenant with almost no sign-in history, ten failures out of a handful of lifetime
sign-ins produces a deviation near 10, well under the threshold of 25. The rule is
designed for a population.

There is also a control interaction: satisfying it needs 10+ failures *followed by
a success*, and Entra smart lockout activates around 10 attempts — potentially
blocking the very success the rule requires. **Hypothesis, untested** — the
trigger deliberately stopped at 7 to avoid lockout.

## 2b. Its scope is one entry point, not one technique

`AppDisplayName` is a faithful record of *where* a sign-in was attempted —
`portal.azure.com` logs as `Azure Portal`, and a sign-in to the same account
through a different portal logs as something else (`OfficeHome`, measured
2026-07-31). Both were confirmed against `SigninLogs` directly.

So `has "Azure Portal"` is not a redundant filter on a general brute-force rule —
it **defines** the rule. The same account brute-forced through another entry point
is invisible to it. That is correct behaviour for a rule named after the Azure
Portal, and a real constraint on what enabling it covers.

## 3. Half its query reads a table this tenant does not ingest

It unions `SigninLogs` with `AADNonInteractiveUserSignInLogs` — a log type
explicitly declined in Lab 08 (`POS-034`). It does not error only because
`union isfuzzy=true` tolerates missing tables. **The template runs at half
coverage, silently.**

## 4. What the template gave that the authored rule had to build

Enabling it forks Microsoft's KQL into a rule you own — the query is editable, so
it will not track upstream template versions either. Its real value is not the
query:

- **Entity mapping, pre-populated** — two Account entities and an IP, one Account
  keyed on `AadUserId` (strong) and one on `FullName`/`Name`/`UPNSuffix` (weak
  composite), so the entity resolves whichever identifier a source supplies.
- **`| extend timestamp = StartTime`** — a convention `DET-004` lacked, though
  adding it did not produce the expected effect.

Custom details and alert details ship **empty**, so the alert would arrive with
rich entities and a static title.
