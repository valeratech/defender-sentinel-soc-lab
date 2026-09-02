# Lab 11 — Sentinel Analytics Rules

| Field | Value |
|---|---|
| **Domain** | Detection |
| **Objectives** | Enable a Microsoft template and author a rule against the same technique; trigger both once; measure what firing reveals that building cannot |
| **Depends on** | Lab 08 (`SigninLogs` ingestion — the table both rules read), Lab 09 (`POS-035`, audit logging) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-30 / 2026-07-31 |

> Two rules on one technique. One fired twelve times for a single event, then once
> after a one-setting change. The other has never fired at all — and both outcomes
> are the lab.

---

## 1. Objective

The wizard is not the lab. `docs/attack-coverage.md` distinguishes CLAIMED from
COVERED, so a rule that has never fired is a hypothesis — and the course material
for this section describes creating rules across two guides without firing one.

Second objective, chosen deliberately after Lab 10: **check what already covers
the activity before authoring.** Lab 10 produced duplicate alerting because a
built-in policy already covered the chosen activity and nobody looked. Here the
template search came first, found three brute-force templates, and the design
changed as a result.

Third: **no live endpoint required.** Both rules read `SigninLogs`, and failed
sign-ins are self-triggerable. Both VMs stayed deallocated.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Check templates first | **Yes** | Author blind | Lab 10's lesson, applied one guide later. Found `Brute force attack against Azure Portal` covering exactly the intended activity |
| Enable *and* author | **Both** | One or the other | Converts Lab 10's accidental overlap into a designed comparison — Microsoft's logic beside a naive threshold rule, one trigger testing both |
| Rule type | **Scheduled** ×2 | NRT | NRT cannot aggregate over a window, and counting failures across an hour is exactly that. NRT is structurally unsuitable for brute force, which the guide does not say while calling it the recommended default for high-priority detections |
| Distinguishing field | **Severity** — Medium vs **Low** | Name only | Severity is what separated the custom and built-in alerts in Lab 10; and Low is honest, a raw count being lower fidelity than deviation logic |
| Trigger account | **`labuser`** | admin | Locking out the account you administer from would be self-inflicted. Seven failures, under Entra smart lockout's ~10 |
| Template tuning | **Frequency only, plus incidents** | Ship as-is | At 1 day/run it could not produce an observable result inside the tenant's life |

## 3. Build

`Microsoft Sentinel > Configuration > Analytics`. Baseline before either rule:
**0 active rules** — the workspace was ingesting data with no detections running.

Both rules recorded in full: `POS-045` (template) and `POS-046` (authored).

Both baselined with **`Test with current data`** before saving — flat zero across
50 evaluations. A measured starting point Lab 10 did not have.

## 4. Validation

| Check | Expected | Result |
|---|---|---|
| Custom rule fires | yes | ✅ all four runs |
| Alert templating resolves | yes | ✅ `LAB-Bruteforce: 7 failed sign-ins to Azure Portal` |
| Entity mapping populates | yes | ✅ `Accounts: labuser`, every alert |
| Template fires | **no** | ✅ correctly did not (`DET-005`) |
| One alert per event | yes | ❌ **12** (run 1) |
| Incidents correlate | uncertain | ❌ **12 incidents** |
| Activity span correct | yes | ❌ 60 min → ✅ fixed, runs 3–4 |
| Suppression deduplicates | yes | ✅ **12 → 1** |
| Suppressed alert is accurate | *(unexamined)* | ❌ **5 of 7** |

## 5. Evidence — four runs

| Run | Trigger (UTC) | Suppression | Alerts | Incidents | Span |
|---|---|---|---|---|---|
| 1 | 03:13–03:15 | off | **12** | **12** (IDs 3–14) | 60 min |
| 2 | 14:23–14:24 | 1 h | **1** | **1** (ID 15) | 60 min |
| 3 | 15:33–15:36 | 1 h | 1 | — | **point** `15:34:40` |
| 4 | 18:18–18:21 | 1 h | 1 | — | **point** `18:19:42` |

Run 1's twelve alerts arrived at exactly five-minute intervals — `03:16:11`
through `04:11:11` — then stopped when the failures aged out. All failures logged
`ResultType 50126`.

## 6. Failures & Fixes

**Alerts = lookback ÷ frequency.** `60 ÷ 5 = 12`, observed exactly. Event grouping
deduplicates *within* a run; only suppression deduplicates *across* runs, and they
are configured in different places on the same page. With alert grouping disabled,
**incidents = alerts**.

**The mechanism had already been explained before the rule was built** — *"each
event gets evaluated roughly twelve times; deduplication is what suppression and
event grouping are for"* — and the rule was then built with suppression
unconfigured. Understanding a failure mode is not designing against it.

**Fixed: 12 → 1** on both counts. **And the fix has a cost that was not
anticipated:** run 4's seven failures spanned 18:19:42–18:21:17, and the alert
reads **5**. The rule ran mid-burst and suppression then blocked the corrected
count a later run would have produced. **The alert you keep is the earliest and
least complete one** — a 29% undercount on the number used to judge severity.

**The span fix took two attempts, and the first was inference.**
`| extend timestamp = StartTime` was copied from Microsoft's template on the
reasoning that the template had it and this rule didn't. It changed nothing.
`| extend TimeGenerated = StartTime` **works** — confirmed twice, each alert
stamped at `StartTime` inside its own burst. The template's idiom is stale.

But it yields a **point, not a range**: one `TimeGenerated` per summarized row, so
a 0-second span for a 90-second event. Neither 60 minutes nor zero is right.
**Resolved by read, 2026-09-01 — configured ≠ effective, both halves measured.** *Configured:* the committed rule computes distinct event-range columns from the summarized source events, `StartTime = min(TimeGenerated)` and `EndTime = max(TimeGenerated)`. *Effective:* an existing fired alert from this rule renders **First activity and Last activity identical to the second** — a zero-second displayed span, on two independent surfaces (incident panel and alert details), for a burst of seven sign-ins. The rule also re-projects `TimeGenerated = StartTime`; whether that re-projection, platform field mapping, or another rendering rule causes the collapse **was not isolated** (NOT MEASURED), and nothing here generalizes beyond this rule and alert.

**Two calls made during this lab were wrong.** Run 3 was read as contaminated by
an artifact alert; it had succeeded. And when run 4 reported *"5 failed sign-ins
to OfficeHome"*, the proposed explanation was that `AppDisplayName` splits one
burst across apps below threshold — wrong; that run used a different portal, and a
subsequent `portal.azure.com` run logged all seven as `Azure Portal`, confirmed
against `SigninLogs`. **The variance was in the test, not the platform.**

## 7. Analysis

**An enabled rule is a hypothesis.** `DET-005` is enabled, correctly configured,
and has never fired — which is why the coverage matrix reads **Credential Access
PARTIAL (1/2)**, the first PARTIAL here. One rule proven, one asserted.

**Microsoft's template could not fire on the activity it names.** It needs 10+
failures *followed by* a success terminating the sequence; the trigger produced 7
with no trailing success, so the deviation logic was never reached — that part of
the prediction is **untested rather than confirmed**. Full account in `DET-005`,
including why a three-identity tenant may be unable to satisfy its deviation
threshold, and how it runs at half coverage over a table this tenant declined.

**And its scope is one entry point, not one technique.** `AppDisplayName` faithfully
records where a sign-in was attempted, so `has "Azure Portal"` *defines* the rule
rather than merely narrowing it. The same account attacked through another portal
is invisible to it — correct for a rule named after the Azure Portal, and a real
constraint on what enabling it covers.

**A template's value is not the query.** The query is editable and could be
written. What it embeds is domain knowledge: two Account entities keyed on a
strong identifier and a weak composite, so the entity resolves whichever a source
supplies. Custom details and alert details ship empty. **And one of its
conventions is stale** — copying `timestamp` from it produced nothing.

**Frequency and lookback are coupled**, and the guide presents them as
independent. Lookback ≥ 2 days forces frequency ≥ 1 hour, discoverable only as a
validation error.

**Two surfaces disagreed about incident creation.** The template detail pane read
Disabled; the wizard defaulted Enabled, confirmed by a from-scratch rule. Had the
pane been authoritative, the rule would have produced alerts that never reached
the incident queue.

**Sentinel scheduled alerts receive no automated investigation.** All incidents
read `Unsupported alert type`, where Lab 10's MDO incident reads `Queued`. The actions-and-submissions guide
established that an alert is not an action; **for Sentinel-authored rules there
is no action path at all**.

**Twelve incidents is worse than twelve notifications.** Lab 10's duplicate cost
mailbox noise. This cost twelve queue items for one 92-second event, each needing
individual triage. Same lesson, higher price — and the fix for it introduced an
undercount, which is the trade this lab actually measured.

## 8. References

- `POS-045` (template, tuned), `POS-046` (authored rule, corrected)
- `DET-004` — validated; `DET-005` — **unvalidated**, and the reason `TA0006`
  reads PARTIAL
- Lab 10 — the duplicate-alerting lesson this lab applied in advance
- Lab 08 — `SigninLogs` ingestion, and the declined log type `DET-005` silently needs
