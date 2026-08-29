# Lab 24 — Licensing Lifecycle: A Subscription Past Its Stated Expiration Date and Still Active

| Field | Value |
|---|---|
| **Domain** | Microsoft 365 admin center billing surfaces / trial subscription lifecycle / licence assignment and entitlement |
| **Objectives** | Determine whether Office 365 E5 was required only to *acquire* Microsoft 365 E5 or is an *ongoing* dependency for retaining it; measure what the tenant's surfaces render across a trial subscription's stated expiration date |
| **Depends on** | `POS-017` (acquisition order, operator-reported), `POS-027` (`analyst` unlicensed by design), `POS-077` (M365 E5 extension consumed), `POS-078` (billing surface state), `POS-079`/`POS-080` (Power Automate Free) |
| **Status** | 🔨 Built, documentation in progress — three reads across three dates, zero cost, no tenant object modified |
| **Built** | 2026-08-12 through 2026-08-14 |
| **Cost** | $0. No provisioning, no consumption meter touched, no subscription control operated. The only actions were reads and one view-filter change |

> On 2026-08-06 the Microsoft 365 E5 trial was extended to 2026-09-14 and the
> Office 365 E5 trial was deliberately **not** extended. That created an isolated
> natural experiment on a one-way state transition: if O365 E5 were an ongoing
> dependency, M365 E5 would degrade when it lapsed.
>
> It did not degrade — but **Office 365 E5 never lapsed either.** The day after
> its stated expiration date the subscription still reports
> `Subscription status: Active` on every billing surface, under a fully widened
> status filter, on a page where one banner says it expired and two others say it
> *will* expire. The stressor the experiment was designed around never arrived.

---

## 1. Objective

The course acquisition path required signing up for Office 365 E5 before
Microsoft 365 E5 could be added. That produces a question the tenant can answer:

> Was Office 365 E5 merely required to **acquire** Microsoft 365 E5, or is it an
> **ongoing** dependency for **retaining** it?

This is not the 2026-09-14 capability cliff, not a broad licensing audit, and not
about provisioning surfaces disappearing. It is one isolated dependency test.

**Isolation is clean because:** `admin` is the only Office 365 E5 holder and also
holds Microsoft 365 E5; `labuser` holds Microsoft 365 E5 **without** Office 365
E5 and is the control; `analyst` is unlicensed by design (`POS-027`); and every
Office 365 workload this repository exercises is also carried by Microsoft 365 E5.

**One claim in the chain is operator-reported, not measured.** `POS-017` records
that the operator *reports* Office 365 E5 had to be signed up for first. The
prerequisite itself was never independently tested — nobody attempted Microsoft
365 E5 first and was refused. The conclusion in §8 is worded to respect that, and
§9 registers a prediction to close it on a future clean tenant.

---

## 2. Predictions

Ten were registered on 2026-08-12 before any surface was read. Six more were
drafted after the 2026-08-13 early read and revised on 2026-08-14 before contact;
`P24-18` and `P24-19` were registered immediately before the two control actions
they describe.

| # | Prediction (registered wording) | Outcome |
|---|---|---|
| P24-1 | M365 E5 remains active and assigned after O365 E5 lapses | ◐ holding, not stress-tested |
| P24-2 | O365 E5's acquisition role was not an ongoing dependency | ◐ holding, not stress-tested |
| P24-3 | `admin` retains all M365 E5 service plans, unchanged in count and name | ⚠ **unsupported — never measured** |
| P24-4 | `labuser` is entirely unaffected — the control, holding M365 E5 alone | ◐ holding, not stress-tested |
| P24-5 | The six surfaces will still disagree, and will disagree in *new* ways post-expiry | ✅ confirmed |
| P24-6 | `Next invoice available` remains stale at 8/15/2026, unmoved by the lapse | ◐ partial — stale confirmed, second clause untestable |
| P24-7 | Defender portal renders normally for `admin` — the surviving entitlement is effective, not just assigned | ✅ confirmed |
| P24-8 | O365 E5 disappears from `Your products` rather than persisting as an expired row | ⬜ untestable |
| P24-9 | The row persists with status `Expired` rather than moving to `Deleted` | ⬜ untestable |
| P24-10 | The invisible LRM marks persist in tomorrow's export | ✅ confirmed |
| P24-11 | Banner 1 still reads exactly *"Your Office 365 E5 expires today."* | ❌ **falsified** |
| P24-12 | The `Licenses and apps` banner still reads 8/12/2026 | ✅ confirmed |
| P24-13 | *(withdrawn — see §7.1)* | — |
| P24-14 | CSV carries exactly two U+200E marks in the M365 field, none in O365 | ✅ confirmed |
| P24-15 | `Extend trial end date` live on O365, greyed on M365 | ✅ confirmed |
| P24-16 | Defender left nav renders eighteen sections | ✅ confirmed |
| P24-17 | O365 E5 has moved off `Active` on at least one billing surface, and the surfaces disagree about it | ❌ **falsified** |
| P24-18 | `Refresh` changes no rendered value | ✅ confirmed |
| P24-19 | The widened seven-status filter returns the same 3 items | ✅ confirmed |

**Nine confirmed, three holding-but-not-stress-tested, one partial, one
unsupported, two falsified, two untestable, one withdrawn.**

`P24-1` through `P24-10` are reproduced in their **registered wording**, not
abbreviated. That matters for three of them.

**`P24-1`, `P24-2` and `P24-4` were written against a lapse, though not all in
the same way.** `P24-1` names one in its own text. `P24-2`'s registered falsifier
names one — *"M365 E5 losing service plans or entitlement when O365 lapses."*
`P24-4`'s falsifier, *"any change to `labuser`'s licence state,"* is testable
without a lapse and did not trigger on any read; it is still recorded as not
stress-tested, because *"entirely unaffected"* was registered against a
post-lapse condition that never arrived.

No lapse processed (§6.1). What was observed is that crossing the *stated
expiration date* produced no change, which is not the same claim. All three are
recorded as **holding but not stress-tested**.

**`P24-6` is compound.** `Next invoice available` was confirmed stale at
`8/15/2026` on three surfaces across all three reads. The clause *"unmoved by
the lapse"* is untestable for the same reason.

**`P24-3` is unsupported and was initially scored `confirmed` in error.** No
service-plan census was ever taken. `Apps (175)` is a single aggregate across all
three licences, not a per-plan count or name list, and §9 records the census as
still pending. A prediction about count and name cannot be confirmed by a number
that is neither. Recorded as **not measured**, not as confirmed.

**`P24-8` and `P24-9` are untestable rather than falsified**: both describe what
happens *after* a lapse processes. The pair was also too narrow — neither
contemplated the outcome actually observed, which is the row persisting as
`Active` past its expiration date. A defect in the prediction set, recorded as
one.

---

## 3. What was observed

Six surfaces, read in the same order on each date, with local timestamps and
exact rendered strings:

| # | Surface | Path |
|---|---|---|
| 1 | Licence assignment | `admin.microsoft.com` > Users > Active users > *admin* > Licenses and apps |
| 2 | Product list | `admin.microsoft.com` > Billing > Your products > Products |
| 3 | Machine-readable export | the same page's `Export to CSV` |
| 4 | O365 E5 product page | Your products > Products > Office 365 E5 |
| 5 | M365 E5 product page | Your products > Products > Microsoft 365 E5 |
| 6 | Capability baseline | `security.microsoft.com` — left navigation, advanced hunting |

Surfaces 4 and 5 are a deliberate contrast pair: same template, same account,
same session, one screen apart. If a dependency existed, surface 5 is where a
warning would appear.

Nothing was modified. `Extend trial end date` and `Cancel subscription` were
never operated — either would have replaced a natural expiry with an
operator-caused one and destroyed the observation. The single state change made
anywhere in this lab was widening a view filter (§6.3).

---

## 4. Phase A — pre-lapse baseline, 2026-08-12, 12:14–12:25 PDT

**Six surfaces read `8/13/2026`. One reads `8/12/2026`.**

The outlier is surface 1's banner: *"The trial subscription for Office 365 E5
expires on 8/12/2026. Buy this subscription so they won't lose access when the
trial ends."* It had already read `8/12` on 2026-08-06, so by this point it was
established as a fixed date field rather than a countdown.

All three licences checked on surface 1: Microsoft 365 E5 (23 of 25 available),
Microsoft Power Automate Free (9999 of 10000), Office 365 E5 (24 of 25),
`Apps (175)`. 24 of 25 confirms `admin` as sole O365 E5 holder; 23 of 25 matches
`POS-077`.

Surface 2 rendered three rows, all `✅ Active`. Surface 4 carried **three
banners**; surface 5 carried **zero**. `Extend trial end date` rendered **live**
on surface 4 and **greyed** on surface 5 — `POS-077`'s "extension consumed"
verified by observation, with the O365 page as the positive control proving that
greyed means consumed rather than absent.

Surface 4's third banner is the vendor writing this lab's central test:

> *"This subscription will be canceled when it expires on August 13, 2026 at which
> point users will lose access to the service."*

Surface 6 rendered eighteen navigation sections, advanced hunting loaded, and
`GraphAPIAuditEvents` was present in the schema tree under *Apps & identities*.

---

## 5. Phase B — the expiration date, 2026-08-13, 07:07–07:17 PDT

**The lapse had not processed.** Office 365 E5 `Active` on all three billing
surfaces, `8/13/2026`, assigned 1 / purchased 25 / available 24.

**Banner 1 moved and escalated.** Phase A: *"Your Office 365 E5 expires on
8/13/2026"* with an informational icon. Phase B: **"Your Office 365 E5 expires
today."** with a **red error icon**. Banners 2 and 3 unchanged verbatim.

**Surface 1's banner did not move.** Still `8/12/2026` — now rendering a date
that had passed.

That pairing is the phase's substantive result. Across one interval, on one
subscription, one banner re-rendered relative to the current date and another did
not move at all. The difference is a property of the field, not of the data.

Surface 5 still carried **zero banners** on the morning its supposed prerequisite
was expiring. `Next invoice available` still `8/15/2026`, unmoved (`P24-6`).

The export at 07:16:50 PDT carried **exactly two U+200E marks** wrapping the M365
date and none in the O365 field, plus a UTF-8 BOM — `P24-10` confirmed on a
second consecutive day, promoting the finding from a one-day artifact to a stable
exporter property.

Surface 6: eighteen sections, hunting unimpaired.

---

## 6. Phase C — post-expiry, 2026-08-14, 06:35–06:50 PDT

### 6.1 The subscription outlived its own expiration date

`Office 365 E5` · **`✅ Active`** · `Renewal or expiration date: 8/13/2026` —
the stated expiration date had passed. Assigned 1 / purchased 25 / available 24,
identical to both prior reads. The surface renders a date and no time or
timezone, so nothing here establishes *when* on 8/13 the subscription was due to
expire, and no such time is inferred.

Surface 1: all three licences still **checked**, counts unchanged, Office 365 E5
still `24 of 25`. The subscription is expired by one banner's own words and still
assigned, still counted, still checked.

### 6.2 One page, three tenses

Surface 4 rendered, simultaneously:

1. **"Your Office 365 E5 expired."** — past tense, informational icon
2. *"Your free trial **will expire** on 8/13/2026 and your service **will end**."*
3. *"This subscription **will be canceled when it expires** on August 13, 2026…"*
4. `Subscription status:` **`✅ Active`**

Banner 1 both **moved and de-escalated** — red error on the expiry date,
informational after it. Severity peaked on the date and dropped once it passed.
Banners 2 and 3 remained future tense about a date that had gone.

Surface 1's banner still read **`8/12/2026`** — a fourth reading across a fourth
date, two days stale, still advising the reader to buy *"so they won't lose
access when the trial ends."*

### 6.3 The widened filter

The `Subscription status` filter's as-found state was **Active, Pending,
Scheduled, Expired, Disabled checked; Deleted and Failed unchecked** — identical
to Phase A. Widening it to all seven and applying returned the **same 3 items**
(`P24-19`).

This matters because every prior read's item count was a statement about the
filter rather than about the tenant. Under the widened view it becomes a real
one: there is no second Office 365 E5 object hiding in a `Deleted` or `Failed`
state.

### 6.4 `Refresh` changed nothing

`P24-18` confirmed. This establishes that the `Active` status was **not merely a
stale pre-refresh client rendering**. It does not independently establish the
backend lifecycle state — only that re-requesting the surface returned the same
answer.

### 6.5 The capability surface is working, not merely rendering

Eighteen navigation sections, exact names and order. Defender home reported
**6/6 connectors healthy, 0 unhealthy**, `Events in previous 24 hours (37)` on
the data-received chart, 3 automation rules, 1 active device. Telemetry continued
to flow across the expiry.

---

## 7. Failures, withdrawals, and one lost read

### 7.1 A read that was planned, missed, and is not reconstructed

The plan called for **two reads on 2026-08-13**, early and late. The early read
was taken; the late read was not. The next read occurred on 2026-08-14 at 06:35
PDT, 23.3 hours after the early read.

**This is recorded as lost, not reconstructed.** What it costs is the ability to
bracket the transition more tightly than a 23-hour window. What it does not cost
is the before/after comparison, because the transition being measured — whether
Microsoft 365 E5 degrades — is a state comparison rather than a timing one.

`P24-13` predicted the lapse would not process *during 2026-08-13*. With no late
read on that date, it can never be tested. It is **withdrawn as untestable**
rather than scored, and rather than quietly reworded into something the
observations happen to satisfy.

### 7.2 A prediction set that was too narrow

`P24-8` and `P24-9` between them assumed the row would either disappear or
persist as `Expired`. It did neither. Both remain formally untestable, but the
framing failure is recorded here rather than smoothed over: the option actually
observed was not among the options considered.

### 7.3 A filter selection that looked applied and was not

On the first attempt at §6.3, all seven status checkboxes were ticked and the
dropdown dismissed without `Apply` arming. The table below rendered normally and
looked like an answer.

The only indicator was the chip label, which still read `Active, Pending,
Scheduled , +2` rather than `+4`. Reading the table at that point would have
produced a correct-looking count from an unwidened view.

This is operator error caught by an existing control, not a platform divergence,
and it is recorded here rather than as an inventory row.

---

## 8. Findings

### 8.1 What the dependency experiment answered — and what it did not

**Answered:**

> Crossing Office 365 E5's stated expiration date caused no observed change to
> Microsoft 365 E5, to its assigned entitlement, or to the Defender portal.
> Office 365 E5 itself remained `Subscription status: Active` on every billing
> surface after the date passed.

**Not answered:**

> Whether Microsoft 365 E5 survives an *actual* Office 365 E5 lapse.

The experiment was designed around a stressor that never arrived. `P24-1` names a
lapse in its own text and `P24-2`'s registered falsifier names one, and no lapse
processed — the row is still present and `Active` under a fully widened
seven-status filter (§6.3). Reporting either as confirmed would claim a result
the tenant never produced.

What the lab did reach is a third state neither the design nor the prediction set
anticipated: **the stated expiration date passed, the page's banners moved into
mutually contradictory past and future tense, and the subscription itself never
transitioned out of `Active`.** See `POS-100`, which carries `revisit: true`
against exactly that.

`labuser` — holding Microsoft 365 E5 alone, without Office 365 E5, and exercising
this repository's Office workloads throughout — is the standing control, and was
unaffected on every read.

### 8.2 Four rendering behaviours on one subscription

| Surface | Behaviour | Evidence |
|---|---|---|
| `Licenses and apps` banner | **stale fixed** — `8/12/2026` unchanged across four readings on four dates | §4, §5, §6.2 |
| Product list / product page date fields | **fixed, correct** — `8/13/2026` throughout | §4, §6.1 |
| Product page banner 1 | **relative** — `expires on 8/13/2026` → `expires today` → `expired` | §5, §6.2 |
| Product page banners 2 and 3 | **fixed, future tense past the date** | §6.2 |

Three of these were visible simultaneously on 2026-08-14, two of them on adjacent
lines of the same panel. Divergence rows `210` and `211`.

### 8.3 The export is deterministic across a state change it does not reflect

The 2026-08-13 and 2026-08-14 exports are **byte-identical** — SHA256
`f152168ecb89ea246c93cf4c331c04b6f94874fc99529abd2b268e38e5f04960`, 1,121 bytes
each, identical BOM and line endings — taken 23.3 hours apart and spanning the
subscription's expiration date, during which a banner on the same page describing
the same subscription changed **once** (*expires today* → *expired*). The earlier
*expires on 8/13/2026* → *expires today* transition happened before the first of
these two exports.

**This is an observation about the exporter's output, not an inference about
backend processing.** What is measured is that the file did not change; why it
did not is outside what these surfaces can answer.

It is deliberately **not** recorded as a divergence row. No exported field
changed over that interval — `Subscription status` stayed `Active` and the date
stayed `8/13/2026` — so a byte-identical export is the correct result, not a
contradiction. The element that moved was a rendered banner, which is not an
exported field. Recording it as a divergence would assert a mismatch that was
never demonstrated.

### 8.4 Invisible formatting controls inside a data field

Both exports carry exactly **two U+200E left-to-right marks** wrapping the date
inside the Microsoft 365 E5 `Renewal or expiration date` field:
`Renews on \u200e9/14/2026\u200e with 1 paid license`. The Office 365 E5 field, a
bare date, carries none. Verified programmatically on three separate exports.

Invisible in every viewer, and enough to break a naive date parse or an
exact-match comparison. Divergence row `212`.

### 8.5 A default filter that governs every absence reading

The `Your products` status filter ships showing five of seven statuses, excluding
**Deleted** and **Failed** (`POS-101`). Any conclusion drawn from a subscription's
absence on that page is a statement about the filter until the filter is widened.
This is the repository's recurring *unpopulated is not empty* shape on a billing
surface.

---

## 9. What this cost, and what was left behind

**Cost: $0.** No resource provisioned, no consumption meter touched, no
subscription control operated.

**Left in the tenant deliberately** — if any is ever actioned, record the state
first:

- **Office 365 E5 not extended.** Its one trial extension has never been used and
  `Extend trial end date` remains live (`P24-15`). The lapse is a standing choice.
- **The pending PUA quarantine** on Investigation #2 (`f_000045`) — still
  unapproved and uncancelled, confirmed present on 2026-08-14.

**Not captured, and cheap only until Office 365 E5 goes:**

*(pending — per-licence service-plan expansion, and whether `Apps (175)` moves when Office 365 E5 is removed; capturable only while all three licences are present)*

**Registered prediction, to be tested on a future clean tenant:**

> **Registered 2026-08-14, before contact with any fresh tenant.** Microsoft 365
> E5 trial acquisition will succeed on a clean tenant with no prior Office 365 E5
> subscription. Falsified by any refusal or gating that requires a qualifying
> prior subscription.

If confirmed, `POS-017`'s operator-reported prerequisite was a path artifact or a
course convention rather than a platform requirement. The Microsoft Sentinel
Training Lab tenant is a separate portfolio piece with no connection to this
repository, so the result lands there and is cross-referenced back.

*(pending — acquisition-order prediction resolves on a future clean tenant, not in this repository)*

---

## 10. References

- `POS-017` — acquisition order, operator-reported
- `POS-027` — `analyst` unlicensed by design
- `POS-077` — Microsoft 365 E5 trial extension consumed
- `POS-078` — billing surface state
- `POS-079`, `POS-080` — Microsoft Power Automate Free
- `POS-100` — Office 365 E5 past expiry, lapse not processed
- `POS-101` — `Your products` default status filter
- Divergence rows `210`–`212`
