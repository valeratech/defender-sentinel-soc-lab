# Lab 21 — NRT Execution Semantics: The Hour That Never Holds an Hour

| Field | Value |
|---|---|
| **Domain** | Sentinel analytics rules / anomaly rule lifecycle / detection engineering |
| **Objectives** | Test Sentinel's Flighting/Production anomaly-rule lifecycle (module 89, G66); build the course's hour-aggregation NRT rule as a **falsification test** and measure what it actually detects |
| **Depends on** | `POS-046` / `DET-004` (the aggregation limit, reached from `SigninLogs`), `POS-044` + divergence row 41 (anomaly inventory, MOD-61 — reused, not re-measured), `POS-033` (hostname truncation; AMA+DCR collection), Lab 07 (`SecurityEvent` path), MOD-57 (store partitions) |
| **Status** | ✅ Built and measured — two phases, one metered window of 3 h 18 m |
| **Built** | 2026-08-10 |
| **Cost** | VM 2 for 3 h 18 m; one Bastion Developer SKU host created and deleted inside the window. **Bastion charge $0 — no meter rows emitted, confirmed 2026-08-12 (`P89-10` closed, `POS-099`)** |

> The guide teaches a brute-force detector as an NRT rule: count failed logons
> per account **per hour**, alert above a threshold. `POS-046` had already
> rejected that construction three weeks earlier — `DET-004` was built
> **Scheduled** precisely because NRT cannot aggregate over a time window.
>
> So the rule was built **on purpose, to fail measurably**. Two controls, one
> account, one clock hour, eight qualifying failures. Distributed across six
> minutes: **no alert**. Concentrated inside 25 seconds: **alert, reporting a
> count of 4**. A rule genuinely counting per hour would have reported **8**.
>
> `bin(TimeGenerated, 1h)` is decorative. It names a bucket that never holds
> more than one minute of ingested data — and **the authoring surface conceals
> this**, because pre-save validation runs the query against seven days of Log
> Analytics history and returns a satisfying green row. The tool does not fail
> to warn about the defect. It produces positive evidence that the broken rule
> works.

---

## Executive summary

*This lab has a plain-language summary; most do not. See "Why this lab has one"
at the end of this section.*

The course guide taught how to build a brute-force detector in Microsoft
Sentinel as a **near-real-time (NRT) rule**: count failed logins per account per
hour, alert when the count crosses a threshold. Before any portal contact, a
grep of this repository found the construction already ruled out — `POS-046`,
written three weeks earlier, records that `DET-004` was deliberately built as a
**scheduled** rule instead, because NRT cannot aggregate over a time window. The
guide teaches a construction this project had already rejected in writing. So
rather than skip the module, the rule was built **on purpose, to prove exactly
how it fails**.

The first half of the work cost nothing and needed no virtual machine. It
examined Sentinel's built-in anomaly rules — pre-packaged machine-learning
detectors — and the workflow for tuning them. What emerged was a chain of small,
individually reasonable behaviours that combine badly. A built-in rule cannot be
edited; it must be duplicated. **The duplicate arrives switched off**, which no
guidance mentions, so a practitioner following the course would tune a threshold,
wait a day for a comparison, and get nothing. Promoting the tuned copy to
Production **automatically demotes the original** — and deleting the copy
afterwards **leaves the original demoted**, with nothing to put it back. Worst,
the edit screen does not display a rule's real mode: it renders *Production*
regardless of the stored value, so opening a rule and clicking Save silently
changes it. The combined effect is the lab's first finding: **a routine edit can
take a working detection offline while every field on every screen still reads
normal.**

The second half used a live server for about three and a quarter hours. The
first measurement was not the experiment — it was the ruler. How long does log
data take to travel from the machine to the workspace? Roughly 20 to 35 seconds,
and more usefully, on a **fixed 20-second schedule** rather than event by event:
fourteen consecutive observations landed on the same grid, across a guest
reboot. That number is what made the experiment designable, because it
determined how far apart to space the test events.

Then the flawed rule was built and two controls were run. **Control A:** four
failed logins spread across six minutes — enough to cross the threshold if the
rule genuinely counted "per hour." **No alert fired.** **Control B:** four
failed logins inside 25 seconds. **An alert fired, reporting a count of four.**
That number is the whole finding. All eight failures occurred on the same
account in the same clock hour, so a rule actually counting per hour would have
reported **eight**. It reported four, because it only ever sees one minute of
data per execution. **The `bin(TimeGenerated, 1h)` instruction is decorative —
it names a bucket that never holds more than a minute.**

The most practically dangerous discovery was in the authoring screen itself.
Testing the query before saving runs it against **the last seven days of
history**, not the way the rule will actually execute. The test returned a
matching row and looked entirely healthy. So the tool does not merely fail to
warn about the flaw — **it produces positive evidence that the broken rule
works**. A separate finding compounds it: with incident creation disabled, alerts
become invisible in two of the three places an analyst would look, so a rule
firing correctly can appear never to have run at all. Only the workspace table
tells the truth.

The lab closed by disabling the test rule rather than deleting it — the
configuration is the evidence — removing the Bastion host, and deallocating both
machines with a confirming second read. The tenant ended in the state it
started. Across both halves: **22 findings, every registered prediction
resolved, and four occasions where a prediction or hypothesis recorded here was
subsequently disproved** — including two authored in this repository and two
proposed mechanisms (propagation, and an MFA theory) that the evidence ruled
out. One question stays open by design: whether the Bastion Developer SKU billed
anything, which resolves on a cost read rather than a guess.

### Why this lab has one

This is the only lab in the repository carrying a plain-language summary, and it
is deliberate rather than the start of a convention.

Every lab README already opens with a thesis blockquote — the analyst-facing
version of the same job. That block assumes the reader knows what an analytics
rule is and what ingestion time means. It is written to be *precise*, not to be
*introductory*, and for twenty labs that has been the right trade.

This lab is denser than the others. It carries two independent investigations —
an anomaly-rule lifecycle and an NRT execution-semantics experiment — across
five distinct portal surfaces, with 22 findings, ten registered predictions, and
a central result that depends on holding three separate timestamps in mind at
once (`TimeGenerated`, `_TimeReceived`, `ingestion_time()`) and understanding
why an alert reporting **4** rather than **8** is the proof. The thesis
blockquote can state that result. It cannot make it *legible* to someone
returning to this file cold in six months.

This repository is a learning record before it is a portfolio piece — the
recurring thesis is *"I built this, observed this, on this date,"* and observing
something is not the same as retaining it. This lab was worked through with
comprehension checks at each step rather than executed as a sequence of pasted
commands, and the summary exists so that understanding survives the session that
produced it.

**It is written by request, for labs where density justifies it. It is not a
required section and should not be backfilled into the other twenty.**

---

## 1. Objective

Module 89 (G66) opens course section 8. Roughly half of it was already
evidenced: MOD-61 measured the anomaly inventory (48 enabled), the `Anomalies`
table (0 rows over 7 days), and the three-surface disagreement — `POS-044`,
divergence row 41, 2026-07-31. **This lab does not repeat that measurement.**

New work, scoped before any portal contact:

1. The composition of the 48 — two rule classes, not one
2. The Flighting/Production lifecycle, end to end
3. NRT execution-window semantics, tested against the course's own query

The guide's rule is **pre-refuted by the repository**. `POS-046` records that
`DET-004` was built Scheduled rather than NRT because NRT cannot aggregate over
a time window, and notes that the course material recommends NRT as a default
without making that point. Rather than skip the module, the rule was built as a
**falsification test**: lab-only name, **no `DET-` id**, disposition recorded,
disabled at teardown. It does not enter the detection catalogue.

**Source distinction, stated because it matters:** `DET-004` queries
`SigninLogs` (Entra). This experiment queries `SecurityEvent` 4625 (Windows, via
AMA+DCR). Different producer, different store. The shared finding is the
aggregation limit, **not shared telemetry** — one structural constraint reached
independently from two stores, three weeks apart.

---

## 2. Predictions

Ten registered before the portal actions they test. Amendments and withdrawals
recorded on the record, never edited away.

| ID | Prediction | Resolution |
|---|---|---|
| P89-1 | The NRT wizard accepts and saves the hour-aggregation query | **Confirmed** |
| P89-2 | In-wizard validation returns 0 results, 0 errors | **Falsified** — 1 row, count 4 |
| P89-3 | Distributed failures do not accumulate across NRT executions | **Confirmed**, three reads |
| P89-4 | `bin(…, 1h)` groups only the rows available to that execution; no state between executions | **Confirmed by demonstration** |
| P89-5a | Promoting a customised anomaly rule demotes the original to Flighting | **Confirmed**, twice |
| P89-5b | Comparing anomaly *output* between versions is untestable here | **Confirmed tenant-blocked** — `Anomalies` holds 0 rows |
| P89-6R | Alert output follows returned rows and grouping, not `DET-004`'s lookback ÷ frequency | **Confirmed** |
| P89-7 | AMA buffers and uploads on a periodic cadence, ~30 s–2 min | **Confirmed and sharpened** — quantised grid |
| P89-8 | Alerts-only rule with incidents off is invisible in the Defender alert surface | **Confirmed, three surfaces** |
| P89-9 | The anomaly Edit wizard does not hydrate Mode; it defaults to Production | **Confirmed** |
| P89-10 | Bastion Developer SKU incurs no hourly charge | **CONFIRMED 2026-08-12**, and sharpened — the SKU emits *no meter rows at all*, not rows priced at zero. `POS-099` |

### Amendments and rejections

**P89-6 rejected before testing** and replaced by **P89-6R**. The original
transferred `DET-004`'s measured `alerts = lookback ÷ frequency` formula to NRT,
predicting at most one alert per qualifying window. The formula does not
transfer: NRT has no configurable alert threshold, and alert count follows
returned rows and event-grouping behaviour. **A correct measurement on a
scheduled rule reads as a platform property until someone applies it to another
rule type.**

**P89-7 loosened before testing.** The original asserted a ~60-second cadence.
Replaced with a prediction of *periodic upload* and a requirement to measure the
actual value from `TimeGenerated`, `_TimeReceived` and `ingestion_time()` rather
than assert one.

**P89-8 amended before testing.** Written as invisibility in the Defender alert
*surface*; the portal's own warning named **two** surfaces — the alerts queue
**and** the `AlertInfo` hunting table. Amended to predict absence from all three
before Control B ran.

### Falsified and withdrawn during the lab

| Claim | Disposition |
|---|---|
| Saving Status **Disabled** + Mode **Production** would be refused or warned | **Falsified** — validation passed clean, no warning |
| Control B's alert would report `CountFailedLogins = 3` | **Falsified** — reported **4**; anchored on the upload slot grid and forgot a one-minute evaluation spans roughly three slots |
| Blue-link styling distinguishes tunable anomaly rules | **Withdrawn** — clicking a UEBA name opened a full pane; styling was a capture artifact |
| UEBA anomaly rules are a separate, untunable class | **Withdrawn** — the UEBA pane exposes Type, Mode, Status, id, threshold, frequency, version and Edit |
| Propagation explains the grid/form Mode disagreement | **Disproved** — state held across a 4-minute two-read and a delete; timestamps did not move |
| MFA explains the Bastion login failure | **Disproved** — local WORKGROUP account, no Entra involvement |
| Guest hostname is 14 characters (`ipconfig`) vs 15 in the workspace | **Closed** — cropped capture clipped the trailing character; no divergence |

---

## 3. What was built

**Phase 1 — anomaly lifecycle.** Zero cost, no VM. `Anomalous Azure operations`
duplicated, threshold moved 0.7 → 0.5, copy promoted to Production, deleted,
original restored. Executed **twice** for independent confirmation. Tenant ended
identical to its starting state: no badge, Enabled, Score 0.7.

**Phase 2–6 — NRT experiment.** Metered window **10:17 → ~13:35 US/Pacific,
≈3 h 18 m**.

| Item | Value |
|---|---|
| Rule | `LAB-NRT-4625-Window-Test`, id `ad6bddd2-…` |
| Type | NRT query rule, Custom Content, Medium, Credential Access |
| Parameters | `baseline = 1; threshold = 2` — **deliberately reduced** from the guide's 5/3 |
| Incidents | **Off** (alerts only) — makes `P89-8` testable, consumes no incident ids |
| Catalogue | **No `DET-` id.** Experimental, disabled at teardown, retained as evidence |

**The parameter reduction is a recorded lab-only change, not a silent edit.**
The guide's 5/3 fires above 15, which is impractical to generate by hand through
Bastion. At 1/2 the rule fires above 2, making Control B three hand-executed
failures. **The semantic under test — concentration versus accumulation — is
unchanged.**

---

## 4. Phase 1 — anomaly rule lifecycle

Navigation verified **2026-08-10** in the **Microsoft Defender portal**:
Microsoft Sentinel → Configuration → Analytics → **Anomalies**. This supersedes
the inherited 2026-07-30/31 Azure-portal path in `docs/navigation.md`; the July
path is superseded and dated, not deleted.

### 4.1 What the tab is, and is not

**The Anomalies tab is a configuration and inventory surface, not an output
surface.** It reports rule state; output lives in the `Anomalies` table, and
nothing downstream happens unless a scheduled or NRT rule queries it. The rule
details pane states this in Microsoft's own words: anomalies are saved to the
`Anomalies` table and **no alerts or incidents are generated by them**.

**The 48 is two populations, not one.** UEBA anomaly rules and customisable ML
anomaly rules sit in one grid, under one Status column, counted in one total.
MOD-61 recorded 48 as a single number. Nothing on the grid distinguishes the
classes except the name.

**Thresholds differ sharply between them.** `UEBA Anomalous Authentication`
carries an anomaly score threshold of **0**, frequency **1 day**, Anomaly
Version 1.0.14. `Anomalous Azure operations` carries **0.7** on a 0–1 slider.
Recorded as observed; no mechanism inferred.

**Enabled does not mean connected.** `Amazon Web Services`, `Okta Single Sign-On
(Preview)` and `GCP Audit Logs` rules all read **Enabled** in a tenant where
none of those connectors exist. Four conditions must hold for an anomaly to
reach the table, and this surface reports only the first:

```
rule Enabled  →  data source connected  →  baseline trained  →  anomaly written
   (this tab)      (Data connectors)        (training period)   (Anomalies table)
```

This is a **second, structurally distinct cause** of MOD-61's zero rows,
independent of the no-baseline cause recorded there. It strengthens `POS-044`
rather than repeating it.

**Microsoft's own empty-state enumerates the same three causes** this project
derived independently: data too new to determine anomalous patterns, required
data source not onboarded, or no anomalous behaviour in range. The three-cause
model is now both measured and vendor-confirmed.

### 4.2 The tuning path

**Built-in configuration cannot be modified.** The Edit wizard's Configuration
step on a built-in rule renders a banner stating exactly that and directing the
user to duplicate via the context menu; the threshold slider is read-only. On a
duplicate the banner is absent, the header changes to *"Customize the definition
of anomalous activity…"*, and the slider is live — moved 0.7 → 0.5 without
objection. **Measured on both sides: refused on the built-in, permitted on the
copy.**

On a built-in, only **Status** and **Mode** are live on the General step; Name,
ID, Description and Tactics are greyed. **They remain greyed on the duplicate**
— the copy is not fully editable either. For this model the customisation
surface is exactly **one parameter**: Thresholds → Score.

**A duplicate lands `FLGT` / Disabled.** Observed on three separate
duplications. Enabling it is a separate explicit act that no guidance mentions —
the guide's claim that both versions write to the table for a 24-hour comparison
omits it entirely.

### 4.3 The lifecycle hazard

**Status and Mode are orthogonal.** A rule can hold Mode **Production** while
Status **Disabled**; the wizard reported *Validation passed* with no warning.
**Mode describes how output would be tagged, not that the rule is live.** "No
badge" means labelled Production, not running.

**Promotion demotes the counterpart atomically** — both rows' `Last modified`
written to the same minute:

| Rule | Before | After |
|---|---|---|
| `… - Customized` | `FLGT`, Disabled | no badge (Production), Disabled |
| `Anomalous Azure operations` (built-in) | no badge, Enabled | **`FLGT`**, Enabled |

**The resulting state is the hazard.** After promotion the tenant held
Production = the customised rule, **Disabled, not running**; and Flighting = the
built-in, **Enabled**, tagging its output `Flighting`. A single save moved the
only *executing* version of this model into Flighting while the version holding
Production did nothing.

**Deletion does not restore.** Deleting the promoted copy left the built-in
still in Flighting, `Last modified` unmoved — confirmed on two trials. After
deletion the model had **no Production version at all**: one Enabled rule tagged
Flighting, nothing above it, and a grid reading entirely normal.

**The Edit form does not hydrate Mode.** Opening Edit on a rule whose grid badge
reads `FLGT` shows **Production** selected. Measured on a duplicate created
minutes earlier and never modified, so its stored state was unambiguous.
Consequences: the Edit wizard is unreliable as a *read* surface for Mode; any
save from it silently writes Production; **the grid badge is authoritative.**

**Mode has no column.** Status renders as text in its own column; Mode renders
as a `FLGT` badge fused to the Name. Two properties of one object in two visual
registers, one easy to miss entirely.

Composed:

```
Edit + Save on any rule        →  silently writes Production
Promotion                      →  silently demotes counterpart
Deletion of the promoted rule  →  does not restore
Mode's only honest surface     →  a badge with no column
Production ≠ running           →  Mode is orthogonal to Status
```

**A routine edit can take a production detection offline, and every field on
every surface will read normal afterwards.** Recorded as `POS-090`.

### 4.4 Incidental

The Edit wizard embeds a **product-feedback survey** as step 3 of 4 — six
questions plus free text and a "Microsoft may contact me" checkbox, with its own
Submit button, non-blocking. Skipped deliberately: the free-text field and
contact opt-in are exactly where tenant-identifying detail leaks by habit.

`Incident correlation` on the NRT blade reads *Tenant default (currently
disabled)* — a tenant-level setting surfaced on a rule blade, not previously
captured.

---

## 5. Phase 2 — the ruler

The first measurement is not the experiment. Without it, a null in Control A is
ambiguous between "the rule did not fire" and "no data arrived", and a fire in
Control B is ambiguous between window semantics and upload batching.

**Boot to first telemetry: ≤ 17 minutes**, lower bound not established. Lab 07's
working expectation was ~5. Heartbeat cadence once running is **exactly 60
seconds**, AMA 1.43.0.0. **The heartbeat interval is not the event upload
cadence** — heartbeat is a fixed liveness ping; event data is buffered
separately. Recorded explicitly because 60 seconds is the number a reader would
mistake for the batch interval.

**`POS-033`'s truncation, read directly from stored data.** `Heartbeat` over 30
days returned one machine, **15 characters**, 135 rows, last seen 2026-07-25 —
the Lab 07 verification session. First confirmation of the NetBIOS truncation
from a stored value in a fresh session rather than a citation. An exact-match
filter on the 19-character Azure name returns nothing, silently.

**AMA uploads on a quantised slot grid.** Fourteen consecutive 4625
observations, spanning a guest reboot:

| Cohort | `SecToReceived` (s) | `_TimeReceived` seconds |
|---|---|---|
| Pre-Control A (6) | 20, 27, 28, 33, 24, 22 | :17, :37, :17, :17, :17, :17 |
| Control A (4) | 18, 18, 36, 36 | :17, :57, :57, :17 |
| Control B (4) | 27, 29, 22, 22 | :37, :57, :57, :57 |

**All fourteen `_TimeReceived` values are ≡ 17 (mod 20).** The delays are not a
smooth distribution across the predicted band — they are *quantised*, which is
what a fixed-slot uploader produces: an event waits for the next slot rather
than starting its own timer. Workspace availability adds a further 3–10 seconds.
Consistent with a **20-second upload grid**; fourteen points across a reboot is
strong, not conclusive.

A one-minute NRT evaluation therefore spans roughly **three slots** — which set
Control A at ≥ 90 s spacing and Control B inside ~30 s.

---

## 6. Failures & Fixes

**Identity namespace collision.** Bastion authentication failed repeatedly
against `labuser`, an **Entra** identity. The VM is WORKGROUP-joined; its local
administrator is **`labadmin`**. No path exists by which a cloud identity
resolves to a local logon on this host, so the rejection was correct behaviour.
Lab 03 had already recorded the convention — *the local account is entered as
bare `labadmin`* — noted at the time precisely because other portal fields use
UPN format. **Three Entra identities and one local admin with similar names is a
collision waiting to happen.**

An MFA hypothesis was raised and **disproved**: Bastion had already
authenticated the Azure session; the credentials in the connection form are the
guest's local Windows account, with no relationship to Entra MFA.

Byproduct: the failed attempts produced genuine 4625 events, LogonType 3, with
`Account` rendered `-\labuser` — the `-` domain confirming WORKGROUP membership.
One attempt passed a full UPN to a machine with no concept of one.

**Generation method.** `runas /user:… cmd` returned directly to the prompt with
no password challenge and no error, and **generated no 4625**. An attempt that
produces nothing is not an attempt that fails, and must not be counted.
`net use \\localhost\C$ /user:nosuchuser <wrong>` returned **System error 86**
and reliably produced one 4625 — with one double-log noted in §7.

**Console latency.** The Bastion session was slow enough that hand-executed
timing carried several seconds of imprecision. This is why generation wall-clock
was treated as approximate and all spacing was read from `TimeGenerated`.

---

## 7. Validation — the two controls

### Control A — distributed, expect no alert

Four `net use` attempts, four 4625 events, one per attempt:

| # | `TimeGenerated` | Gap |
|---|---|---|
| 1 | 13:03:59 | — |
| 2 | 13:06:39 | 160 s |
| 3 | 13:08:21 | 102 s |
| 4 | 13:09:41 | 80 s |

All gaps exceed the one-minute evaluation width. All four fall in the **same
clock hour** and therefore the same `bin(TimeGenerated, 1h)` bucket, where they
aggregate to 4 against a threshold of 2.

**Result: no alert.** `SecurityAlert` read three ways — filtered by rule name;
filtered again two minutes later; then **unfiltered across all providers over
2 hours**. The third read removes any dependence on how the alert would have
been named.

**The surface was proven live before the null was accepted.** An initial
`SecurityAlert` query returned nothing across 24 hours for all producers, which
would have made the null uninterpretable. Widening to 30 days returned **40
alerts across four providers** — `ASI Scheduled Alerts` (DET-004's family),
`MDATP`, `OATP` — most recent 2026-08-08. Only then was the null recorded.

**P89-3 confirmed.**

### Control B — concentrated, expect an alert

Three attempts inside ~25 seconds produced **four** 4625 events; one attempt
double-logged. The actual count is recorded, not the intended one.

| `TimeGenerated` | `_TimeReceived` | `ingestion_time()` |
|---|---|---|
| 13:19:10 | 13:19:37 | 13:19:47 |
| 13:19:28 | 13:19:57 | 13:20:03 |
| 13:19:35 | 13:19:57 | 13:20:03 |
| 13:19:35 | 13:19:57 | 13:20:03 |

**Alert fired at 13:22:30**, provider **`ASI NRT Alerts`**, Medium,
`Event Grouping: AlertPerEvent`, `Alert generation status: Full alert created`,
`Entities` empty (no mapping configured). The evidence record is
zlib-compressed in `ExtendedProperties`; decompressed:

```
TimeGenerated: 13:00:00   Account: -\nosuchuser   CountFailedLogins: 4   Anomaly: 1
```

---

## 8. Findings

### 8.1 The hour bin preserves no state between executions

**`P89-4` confirmed by demonstration, not inference.**

Control A's four events and Control B's four events are on the **same account**,
in the **same clock hour**, and therefore in the **same `bin(TimeGenerated, 1h)`
bucket** — the bucket this alert reports, labelled `13:00:00`.

**If the bin accumulated state across executions, the count would read 8. It
reads 4.**

The hour label is cosmetic: a bucket name applied to one minute of ingested
data. The syntax says "per hour"; the execution model delivers "per evaluation."
A reader of the query cannot tell the difference — **and neither can the
wizard**.

`POS-046` reached the same structural constraint from `SigninLogs` three weeks
earlier, by design decision rather than by measurement. This lab measures it
from `SecurityEvent`. Two stores, one constraint.

### 8.2 The validation surface produces evidence for the wrong conclusion

**`P89-2` falsified**, and the falsification is the finding. Validation returned
**one row** — count 4, `Anomaly` true, binned to the 10:00 hour — aggregating
failed logons generated earlier in the session.

The panel states its own mechanism: the query runs against **Log Analytics
data**, over the panel's range, which was **Last 7 days**. The rule runs over
**one minute**.

**The query passes validation *because* the hour bin works over seven days of
history — the very condition that never obtains at runtime.** A practitioner
sees a matching row, concludes the detection works, and ships a rule that cannot
fire as intended. **A confidently wrong yes is worse than a silent zero.**

The guide anticipates a null result and explains it correctly. It does not
anticipate a **positive** result from a history-scoped validation surface, which
is what any lab with prior 4625 activity will actually see.

### 8.3 Three surfaces, one alert, two silences

**`P89-8` confirmed.** A known-positive alert:

| Surface | Reading |
|---|---|
| `SecurityAlert` (workspace) | **Present** — 13:22:30, `ASI NRT Alerts` |
| `AlertInfo` (XDR) | **Absent** — while holding 21 rows with `ServiceSource: Microsoft Sentinel` |
| Defender **Alerts** queue | **Absent** — 0 alerts, 1 Day |

The `AlertInfo` reading closes the loophole: the table is **not quiet**. It
received 21 Sentinel-authored alerts within retention. It simply does not have
this one, because incident creation is off.

**An analyst checking either Defender surface would conclude the rule never
fired.** Both nulls are indistinguishable from failure; only the workspace table
tells the truth. This extends MOD-57's store-partition finding — the two stores
disagree about the same alert, **by configuration rather than by fault**.

The portal warns about this on the Incident settings step. **The Review + create
summary does not restate it** — the last screen before commit is silent about
the most consequential setting on the rule.

Provider strings separate the rule types cleanly: **`ASI NRT Alerts`** versus
**`ASI Scheduled Alerts`**.

### 8.4 The alert's self-reported query window contradicts its own result

`ExtendedProperties` records `Query Start Time UTC: 2026-08-10 08:22:26Z` and
`Query End Time UTC: 2026-08-10 20:20:27Z` — a **~12-hour window** on a rule
documented to run once per minute with a one-minute lookback. The end time is
~2 minutes before generation, consistent with the documented delay; the start
time is twelve hours earlier.

**The metadata contradicts the alert's own result.** Over twelve hours this
account has at least eight qualifying failures. The rule counted four. The
reported window disagrees not only with the documented execution model but with
the evidence record attached to the same alert.

Candidate explanation, unverified: `08:22:26Z` is exactly twelve hours before
`20:22:26Z`, and the alert was generated at `20:22:30Z` — consistent with the
start time being the generation instant rendered with an AM/PM error rather than
a real lookback. **Not isolated.** Recorded with both readings; not reconciled
by preferring one.

### 8.5 A measured fix does not transfer across rule types

Suppression was deliberately **not** applied. `POS-046` records suppression
fixing `DET-004`'s 12→1 alert storm — but that rule had a 12:1
lookback-to-frequency ratio. **NRT's is 1:1, so there is nothing to suppress.**

Same shape as the `P89-6` rejection: a correct measurement on one rule type
reads as a platform property until someone applies it to another. **Two
instances in one lab of the same class of error.**

### 8.6 The NRT edit wizard hydrates where the anomaly wizard defaults

The NRT rule's Edit wizard is headed **"Edit existing NRT rule"**, shows the rule
name as a subtitle, and renders fields **live and correctly populated**,
including Status. Direct contrast with §4.3, where the anomaly Edit wizard is
headed *"Create an analytics rule…"* and renders Mode at a **default** rather
than the stored value.

**Two edit surfaces in the same portal section, one trustworthy for reading
state and one not.**

---

## 9. Teardown and cost

- Rule set to **Disabled** at 13:35, confirmed on the Active rules grid. **Not
  deleted** — the configuration is the evidence.
- Bastion session ended and the **Bastion host deleted**. Confirmed by
  observation: the Bastion blade reverted to the *"Creating new Bastion
  Developer SKU"* prompt, which renders only when no host exists.
- Both VMs confirmed **Stopped (deallocated)**, two reads.
- Metered window closed ~13:35. **≈3 h 18 m.**

**`P89-10` open.** A Bastion **Developer SKU** host was created and deleted
inside this window, so any Bastion charge is bounded by it. Whether the Developer
SKU bills at $0 resolves on a Cost analysis read. This matters beyond the
invoice: the standing *"Bastion bills more than the VM"* note from Lab 07 was
written against a different SKU and drove teardown discipline for this and
future labs. **If Developer is free, that note is SKU-specific rather than
general and should be amended.**

**Resolved 2026-08-12.** A per-meter daily cost export across the subscription's
full usage history returned **no Bastion meter row of any kind** — not a row
priced at zero. The same export carries Sentinel's daily zero-cost rows, which
is what makes the absence readable as a property of the SKU rather than of the
export. The Lab 07 note is therefore **SKU-specific and has been amended**;
teardown discipline stands for Basic and Standard and is not required by cost
for Developer. `POS-099`.

Standing state, not acted on: the Win11 VM holds a **public IP while
deallocated** — the exact configuration behind MOD-84's finding that IP hours
bill against machines the portal reports as stopped.

---

## 10. References

- `POS-046` / `DET-004` — the aggregation limit, reached from `SigninLogs`
- `POS-044`, divergence row 41 — anomaly inventory and the three-surface
  disagreement (MOD-61, reused not repeated)
- `POS-033` — hostname truncation; AMA+DCR collection
- `POS-090`, `POS-091` — this lab
- Divergence rows 168–172 — this lab
- `lessons/MOD-89-nrt-execution-semantics.md`
- Lab 03, Lab 07 — `labadmin` convention, `SecurityEvent` path
- MOD-57 — store partitions
