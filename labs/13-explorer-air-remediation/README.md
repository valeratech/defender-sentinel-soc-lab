# Lab 13 — Explorer Investigation and Defender-Native Remediation

| Field | Value |
|---|---|
| **Domain** | Response |
| **Objectives** | Investigate a message whose ground truth is already known; run AIR and a remediation against it; establish what the Action Center actually holds |
| **Depends on** | Lab 12 (the four messages and their measured policy paths), Lab 03 (`docs/evidence-notes/actions-and-submissions.md` — the empty Action Center this lab explains) |
| **Status** | ✅ Built, documented, validated |
| **Built** | 2026-08-01 |

> Built on top of Lab 12 rather than beside it. Four messages with fully known
> provenance — every header read, every policy path proven — used as a controlled
> input to grade the investigation tooling instead of trusting it.
>
> It resolves a thread open since Lab 03, and it produced the sharpest instance
> yet of the repository's **second** through-line: *check whether the surface has
> finished answering.*

---

## 1. Objective

Normally you use Explorer to find out what happened to a message. Here we already
knew: which policy acted, from the `X-MS-Exchange-AtpMessageProperties` header;
what it did, from four independent surfaces; and how long it took, to the
millisecond. That is a rare position, and it makes the tooling gradeable.

Second objective: close `docs/evidence-notes/actions-and-submissions.md`. Lab 03 recorded an empty Action Center after an
automated investigation, cause identified as **no remediable artifact existed**.
An email in a mailbox is a remediable artifact. If the Action Center stayed empty
for an investigation and populated for a remediation, that would settle it.

Zero cost. Everything under the E5 trial, no Azure resource, both VMs deallocated.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Target | **`Lab12-CTRL-01`** | `Lab12-DD-01` | The control message is the least load-bearing of the four for Lab 12's findings. If remediation went wrong we lose the least |
| AIR scope | **Investigate email** | Investigate recipient / sender / Contact recipients | Narrowest scope. Recipient pulls in the whole mailbox, sender pulls in every Gmail message, and *Contact recipients* is not an investigation at all |
| Deletion depth | **Soft delete** | Hard delete | Reversible, and reversibility was itself a prediction. Hard delete would have made the lab destructive for no additional finding |
| Sequencing | **AIR first, remediation second, separately** | Both in one submission | Bundling would have produced one Action Center outcome and no way to attribute it. Two submissions is the controlled comparison |
| Excluded | **Submit to Microsoft** | — | Sends our test message and the external sender address to Microsoft, irreversibly. No finding justifies it |
| Excluded | **Show all response actions** | — | The toggle enables actions the message's current state does not normally permit. Off keeps the observation about default behaviour |

## 3. Build

### Phase A — the email entity page as a sixth surface

`Explorer > All email > Lab12-DD-01 > Open email entity` — six tabs: Timeline,
Analysis, Attachments, URL, Similar emails, Email preview.

### Phase B — Message Header Analyzer

`Analysis > Copy message header` → Microsoft Message Header Analyzer.

### Phase C — Take action

Two submissions against `Lab12-CTRL-01`, separately:

1. `Initiate automated investigation > Investigate email` → `Lab13-AIR-CTRL-01`
2. `Move or delete > Soft deleted items` → `Lab13-SOFTDELETE-CTRL-01`

### Phase D — Action Center and mailbox

`Actions & submissions > Action center` — Pending and History. Then the mailbox,
then `Deleted Items > Recover items deleted from this folder`.

## 4. Validation

| # | Prediction (recorded in advance) | Result |
|---|---|---|
| 1 | The entity page does not name the acting policy | ✅ **CONFIRMED** — but reframed, see §7 |
| 2 | It names the *action* rather than the policy | ✅ **CONFIRMED** |
| 3 | AIR produces an Action Center entry | ❌ **FALSIFIED** |
| 4 | AIR on a benign message ends with no remediation actions | ✅ **CONFIRMED** |
| 5 | Header Analyzer agrees with our manual read | ✅ **CONFIRMED** |
| 6 | Soft delete is reversible | ✅ **CONFIRMED** — and by the mailbox owner |

Prediction 3's falsification is the lab's main result.

## 5. Evidence

### The controlled comparison

| | AIR — *investigate* | Soft delete — *remediate* |
|---|---|---|
| Investigations page | ✅ `f6ab8e` | ✅ `56687b` |
| **Action Center** | ❌ **absent from both tabs** | ✅ **History** |
| Approval ID | none | `6570a3` |
| Confirmation wording | "1 **investigation** actions completed" | "1 action(s) completed" |
| Confirmation links to | investigations page | **action center** |
| Propagation warned? | no | **yes — "several minutes"** |
| Scope | MDO | MDO |

### The AIR investigation, complete

`f6ab8e` — started and ended 17:19 local, duration **9 s**, `No threats found`.

| Log action | Duration | Checks |
|---|---|---|
| Sender IP investigation | 0.15 s | IP reputation, Microsoft ISG |
| Mail cluster identification | 0.34 s | header, body, content, URL clustering |
| **File Hash Reputation** | **5 s** | file-hash anomalies |
| Sender domain investigation | 0.20 s | domain reputation |

`Alerts (1)` · `Mailboxes (1)` · `Evidence (0)` · `Entities (4)` · `Log (4)`

Entities: 1 IP address, 1 email, 2 email clusters — all `No threats found`,
none malicious, none suspicious, none remediated.

**File Hash Reputation consumed 55% of the investigation.** The second
investigation, against `Lab12-CTRL-02` which carried the SHA256-verified novel
PDF, ran **7× longer** — 1 m 11 s and still `Running` at capture. *Inference,
untested:* an unseen hash takes longer to adjudicate. Testable against that
investigation's own Log tab.

### The remediation record

`Approval ID 6570a3` · `Decision: Approved` · `Decided by: admin` ·
`Status: Completed` · `Action source: Manual office action` ·
`Entity type: Email Cluster` · `Email count: 1 (1 Remediable, 0 Non-remediable)` ·
`Action logs: 1 Successful, 0 Failed, 0 Already in destination, 0 Timed out`

Landed in **History**, never in Pending. **The Approval ID is an identifier, not
a gate** — the action executed and was retroactively stamped approved by its own
submitter.

## 6. Failures & Fixes

### A finding stated as settled and walked back the same hour

The entity page's Analysis tab carries a field labelled **`Policy`** reading `-`,
beside `Policy type: Unknown` and `Policy action: -`. This was written up as *the
surface built to name the policy reports Unknown* — a sixth-surface finding
sharper than Lab 12's.

Phase B disproved it. The Message Header Analyzer parses `CAT:NONE` from the raw
header as **Protection Policy Category: NONE**, and the `Policy` field sits in a
cluster with Exchange Transport Rule(s), DLP Rule(s), All Overrides, Primary
Override, Connector, Alert ID and Campaign ID. That cluster is about **verdicts
and overrides** — what decided the message's disposition. Nothing did; it was
clean. `Policy: -` is therefore **correct**, and Safe Attachments running Dynamic
Delivery is reported accurately one panel over as `Additional action`.

**Not a divergence. An open question**, and untestable with what this lab holds —
all four messages were delivered clean, so no message here ever received a
filtering verdict. It resolves only against one that did.

The Lab 12 finding is unchanged: no surface names the acting policy, now six
surfaces deep. But the entity page is not *failing* to; it was never that field.

Seventh instance in two days of fitting an ambiguous observation to a thesis
already in hand. Caught before it reached a file.

## 7. Analysis

### Propagation is a second through-line, and this lab produced its sharpest case

The repository's first through-line is *identify the surface before trusting the
answer*. This is its twin: **check whether the surface has finished answering.**

`Log (0)` → `Log (4)`. Same investigation, same page, no action taken, minutes
apart.

That is the cleanest instance this repository is likely to get. A parenthesised
count is about as unambiguous as a UI gets — not a blank field, not a spinner, a
stated quantity. It was wrong. It corrected itself silently, with no reload
prompt and no staleness indicator.

Five measured instances now, spanning twelve days to a few minutes:

| Surface | Delay | Rendered as |
|---|---|---|
| Exchange hydration (`POS-036`) | 12 days | object absent entirely |
| Group membership → transport (Lab 12) | ~20 min | policy scoped to nobody |
| Threat policy application (Lab 12) | < 1 h (24 h claimed) | — |
| Explorer indexing (Lab 12, row 50) | < ~1 h to unknown | `--`, i.e. no action taken |
| **Investigation Log tab** | **minutes** | **`Log (0)`, i.e. nothing was done** |

The last two are the dangerous kind. They do not render as missing — they render
as **a confident zero**.

**The rule: a zero is a claim about the index, not about the event.** An absence
requires a second identical query before it goes in a file. A presence generally
does not; nothing observed here has appeared and then vanished.

**Microsoft knows.** The soft-delete confirmation says *"It can take several
minutes for data to update in the action center."* No such warning appears on the
Explorer export, the `Log` counter, or group replication. The propagation warning
exists as a UI pattern, is applied inconsistently, and **the surfaces that omit it
are the ones that have produced wrong conclusions here**.

### The Action Center holds remediations, not investigations

`docs/evidence-notes/actions-and-submissions.md` recorded an empty Action Center in Lab 03 and attributed it to no
remediable artifact existing. That was right, and this lab confirms it
independently from a second product scope.

The two objects are distinct:

- **Investigations page** — every investigation, threat or not
- **Action Center** — only remediations, with approval and decision state

An investigation that finds nothing has nothing to send there. Lab 03's empty
Action Center was never a fault or a mystery.

The Action Center's own columns say so: Approval ID, Action type, Decision,
Decided by, Status. Every one is about a remediation's approval lifecycle. None
is about an investigation.

### Every action generates the next artifact

Submitting an investigation **created an alert** — `Admin triggered manual
investigation of email`, Informational, `Category: Probing`, Status `Resolved`,
no Incident ID. AIR needs an alert to attach to, so the act of investigating
manufactured one.

Submitting a remediation **created another investigation** — `56687b`, with
`Automated investigation details: Running` on the soft-delete record.

So: investigate → alert. Remediate → investigate. Anyone auditing this tenant's
alert volume later will find alerts that describe administrative activity rather
than threats, and `Category: Probing` on an admin action is an odd label for it.

### The same four, counted three ways

`Action count: 4` (investigations grid) · `Entities analyzed (4)` (graph) ·
`Log (4)` (tab). Plus `Entities (4)` — 1 IP, 1 email, 2 clusters.

Two different fours that happen to coincide: four *entities examined* and four
*log actions executed*. The grid column reads "Action count" and shows the entity
count. **Only the Log tab states what was actually done.**

### "How long did this take" has four answers

For `Lab12-DD-01`, one message:

| Surface | Value | Actually measures |
|---|---|---|
| Header `EndToEndLatency` | 3.25 s | Microsoft-side only |
| Header Analyzer headline | **4 s** | inter-hop delays summed |
| Message trace `Receive`→`Deliver` | 5 s | transport events |
| Header Analyzer's own hop timestamps | **18 s** | creation → delivery |

The analyzer reports "Delivered after 4 seconds" while its own table shows
creation at 14:00:57 and final hop at 14:01:15. It sums inter-hop delays
(0+1+0+3) and silently drops **14 seconds** of sender-side queueing.

This vindicates Lab 12's withdrawn finding from the other direction. Three of
these were called "independent measurement methods" there; they are not
independent and they do not measure the same interval. They differ by nearly 6×
on one message, and **the tool's headline figure is the one that omits the most**.

### Microsoft's analyzer cannot parse Microsoft's headers

Two `Unknown fields`: `DIR:INB` and the entire `ARA:` rule-attribution list —
both emitted by Exchange Online Protection.

And in the analyzer's `Other` section, values appear stripped of their field
names. **`SA` sits there as a bare string** — the single most decisive field in
Lab 12, the one that distinguished the two policy paths across four messages, is
to this tool an unlabelled value with no key.

### Remediation is reversible by the person it was taken against

`POS-057`. The Action Center reads Approved and Completed; the mailbox owner
restores the message from their own client in two clicks, with no notification to
the operator.

Correct behaviour — soft delete is documented as recoverable and that is its
purpose. The gap is that the wizard presents four adjacent radio buttons and
neither it nor the guide says **who** can recover. In the case remediation exists
for, a compromised or complicit mailbox, that is the difference between a control
and a gesture.

### The all-powerful account cannot read the message

`POS-056`. Global Administrator cannot preview or download delivered mail —
`Email & collaboration content (read)` is a separate Unified RBAC permission.

Every prior entry treats the single standing Global Administrator as a **risk**.
This one shows it is also **insufficient**. Without a second scoped role, part of
the email investigation surface is unavailable to the only identity this tenant
has.

## 8. References

- [Threat Explorer and Real-time detections](https://learn.microsoft.com/en-us/defender-office-365/threat-explorer-real-time-detections-about)
- [Email entity page](https://learn.microsoft.com/en-us/defender-office-365/mdo-email-entity-page)
- [Remediate malicious email](https://learn.microsoft.com/en-us/defender-office-365/remediate-malicious-email-delivered-office-365)
- [Automated investigation and response in Microsoft Defender for Office 365](https://learn.microsoft.com/en-us/defender-office-365/air-about)
- [Action center](https://learn.microsoft.com/en-us/defender-xdr/m365d-action-center)
