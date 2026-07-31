---
id: DET-004
name: Failed Entra sign-in burst (authored scheduled rule)
status: active
platform: sentinel
rule_type: scheduled-analytics
severity: low
tactics:
  - TA0006
techniques:
  - T1110
data_sources:
  - SigninLogs
validated: true
---

# DET-004 — Failed Entra sign-in burst

`LAB-Bruteforce-Failed-Signins` (`POS-046`, Lab 11). The first **Sentinel**
detection authored here — `DET-003` was a Microsoft 365 alert policy with no query;
this one is KQL over a workspace table, with entity mapping and alert templating
done by hand.

Fired twice under controlled conditions, once before and once after a
configuration fix, which is what makes Lab 11 a before-and-after rather than a
demonstration.

## 1. Hypothesis

> Five or more failed Entra sign-ins by one account, to one app, from one IP,
> within a rolling hour, indicate a credential-guessing attempt worth alerting on.

## 2. Data Requirements

| Requirement | Value |
|---|---|
| Table | `SigninLogs` — billable, connector-fed (`POS-034`) |
| Log type | Interactive sign-ins only, as selected in Lab 08 |
| Threshold | `FailureCount >= 5` |
| Schedule | Every 5 min, 1-hour lookback |

## 3. Trigger

Seven deliberate failed sign-ins as `labuser` at `portal.azure.com` with a known
wrong password. `ResultType 50126` (invalid username or password) on all seven.
No lockout, no CA prompt. Run twice: **2026-07-31 03:13–03:15 UTC** and
**14:23–14:24 UTC**.

## 4. Validation — four runs

| Run | Trigger (UTC) | Suppression | Alerts | Incidents | Reported span |
|---|---|---|---|---|---|
| 1 | 03:13–03:15 | off | **12** | **12** (IDs 3–14) | 60 min |
| 2 | 14:23–14:24 | 1 h | **1** | **1** (ID 15) | 60 min |
| 3 | 15:33–15:36 | 1 h | 1 | — | **point** |
| 4 | 18:18–18:21 | 1 h | 1 | — | **point** |

Runs 1–2 tested suppression. Runs 3–4 tested the activity-span fix after the
query changed.

Run 1's alerts arrived at exactly five-minute intervals — `03:16:11` through
`04:11:11` — twelve consecutive, no gaps — then stopped when the failures aged
out of the lookback.

## 5. What firing revealed that building did not

**Alerts = lookback ÷ frequency.** A 1-hour lookback at 5-minute frequency
re-evaluates the same events twelve times, and without suppression each
evaluation raises a fresh alert. `60 ÷ 5 = 12`, observed exactly. Event grouping
deduplicates *within* a run; only suppression deduplicates *across* runs, and the
two are configured in different places on the same page.

**With alert grouping disabled, incidents = alerts.** Twelve identical incidents,
each `Active alerts: 1`, none auto-closing. Twelve items to triage for one
92-second event.

**Suppression fixed it: 12 → 1.** Same rule, same trigger, one setting.

**But suppression freezes a mid-burst snapshot.** Run 4 produced seven failures
between 18:19:42 and 18:21:17; the alert reads **5**. The rule ran after five had
been ingested and before the last two, and suppression then blocked the corrected
count a later run would have produced. **The alert you keep is the earliest and
least complete one** — a 29% undercount on the number an analyst uses to judge
severity. That is the cost of the fix, and it is not obvious from the setting.

**The reported activity span was the query window, and the fix is now known.**
Runs 1–2 reported 60 minutes for events lasting ~90 seconds — a 39×
overstatement. `| extend timestamp = StartTime`, the convention Microsoft's own
template carries, **changed nothing**. `| extend TimeGenerated = StartTime`
**works**, confirmed twice: run 3's alert stamped `15:34:40.294` and run 4's
`18:19:42.226`, each matching `StartTime` and landing inside its own burst.

The `timestamp` idiom is stale; `TimeGenerated` is the live convention. But it
yields a **point, not a range** — a summarized row has one `TimeGenerated`, so the
alert reports a 0-second span for an event lasting ~90 seconds. Neither 60 minutes
nor zero is correct. Whether an alert can carry an event *range* from a summarized
result is untested.

**Sentinel scheduled alerts get no automated investigation.** All incidents read
`Investigation state: Unsupported alert type`, where Lab 10's MDO incident reads
`Queued`. So a Sentinel-authored detection produces no AIR, no investigation and
no Action Center entry — narrowing Lab 03's "an alert is not an action" to *for
Sentinel rules there is no action path at all*.

**Incident creation lags alert generation by ~5 minutes**, consistently.

## 6. Tuning

Suppression **on, 1 hour** — matched to the lookback, the minimum that fully
deduplicates without blinding the rule to a genuinely new burst afterwards.
Measured: **12 alerts → 1, 12 incidents → 1**, at the cost of the undercount above.

Final query line: `| extend TimeGenerated = StartTime`.

Still untuned: no automated response attached, and the alert carries a point
rather than the event's duration.
