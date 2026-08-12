# Lab 23 — Purview Audit and eDiscovery: Two Data Planes, and the File Neither One Reports

| Field | Value |
|---|---|
| **Domain** | Microsoft Purview Audit (unified audit log) / Microsoft Purview eDiscovery (content search) / Purview RBAC and case membership |
| **Objectives** | Close the read side of the unified audit pipeline enabled in Lab 09; measure what a content search returns against a known planted population; measure what the eDiscovery access boundary does on grant and on revoke |
| **Depends on** | Lab 09 (`POS-035` unified audit ingestion enabled by cmdlet; `POS-036` Exchange hydration), `POS-027` (`analyst` unlicensed by design), Lab 20 (`POS-091` Copilot capacity torn down), Lab 22 (negative-then-positive control precedent; deliberately-left-evidence precedent) |
| **Status** | ✅ Built and measured — two phases, zero cost, both VMs deallocated throughout |
| **Built** | 2026-08-11 |
| **Cost** | $0. No compute, no consumption meter touched, no capacity provisioned. The only expenditures were a temporary privilege expansion (reverted) and three small files left in place as evidence |

> Sixteen days ago this repository enabled unified audit logging by cmdlet after
> the portal path failed, and then never read it back. Phase A closes that loop:
> **19 records, retrievable, still ingesting.**
>
> Phase B planted three files in one OneDrive account, each containing the same
> invented keyword, and searched for it.
>
> **Two came back.** The plain `.docx` returned, as designed. The **image-only
> PNG returned** — with tenant OCR scanning disabled and greyed behind Syntex
> billing, *and* the case's own OCR unchecked. The plain-ASCII file with an
> unrecognised extension did **not**.
>
> Then the surface that exists to tell you what a search missed reported
> `Partially indexed items: 0`. A rerun with advanced indexing reported
> `Matches from advanced indexing: 0`.
>
> Three surfaces, three zeros, and a readable file sitting in the searched
> location containing the exact term.
>
> The module could not begin at all until a refusal was resolved — and that
> refusal, granted and then revoked, turned out to carry the sharper finding.

---

## 1. Objective

Modules 92, 93 and 94 are one lab and three lesson files. Module 92 is a tier
and licensing read producing no tenant state; modules 93 and 94 are two
investigation surfaces exercised in one continuous session against the same
tenant. Splitting them would separate an audit-log search from the content
search performed twelve minutes later on the same portal by the same identity.
Precedent: Lab 20 combined modules 85, 87 and 88; Lab 22 combined 90 and 91.

The distinction the section rests on, and the reason both surfaces belong in one
lab:

- **Audit search** queries the **activity log** — who did what, when.
- **Content search** queries the **content itself** — what the documents say.

Different data planes, different question, and the repository had touched
neither. Audit tells you an identity accessed a file at 23:27. eDiscovery tells
you what is inside it.

Three things were in scope that no prior lab had covered:

1. **Reading the unified audit log.** `POS-035` established the write side on
   2026-07-26. Nothing had ever consumed it. A pipeline proven to ingest and
   never proven to retrieve is half a control.
2. **Content search against a known population.** Not "does the search work" —
   the interesting question is what it silently omits, which is only answerable
   if you know exactly what should have come back.
3. **The eDiscovery access boundary**, which was not planned scope at all. It
   became scope because Content Search refused, and the refusal was measured
   rather than worked around.

---

## 2. Predictions

Registered before portal contact. Withdrawals and falsifications are recorded on
the record; four of my own predictions were falsified and one was withdrawn.

**Phase A — MOD-93**

| ID | Claim | Result |
|---|---|---|
| `P93-1` | A bounded audit search returns records | **CONFIRMED** — 19 |
| `P93-2` | A submitted job survives browser closure | **PARTIAL** — completed job only; see §6 |
| `P93-3` | A legacy Azure AD-era schema value persists on an Entra-labelled surface | **CONFIRMED**, and on a rendered grid column rather than in a payload |
| `P93-4` | Portal, CSV and raw timestamps reconcile in UTC | **CONFIRMED** — values yes, formats no |
| `P93-5` | Portal and cmdlet return an identifiable common record | **CONFIRMED**, plus an unpredicted count divergence |
| `P93-6` | Ingestion still enabled at 16 days | **CONFIRMED** |
| `P93-7` | The portal labels the raw object something other than `AuditData` | **CONFIRMED** — it labels it nothing |
| `P93-8` | Records exist about `labuser`; about `analyst`, negligible | **NOT TESTED** |
| `P93-9` | The friendly-name vocabulary is not unique | **CONFIRMED** (registered mid-phase) |
| `P93-10` | A submitted job's criteria are not recoverable | **FALSIFIED** (registered mid-phase) |

**Phase B — MOD-94**

| ID | Claim | Result |
|---|---|---|
| `P94-1` | The indexed positive control returns | **CONFIRMED** |
| `P94-2` | Content only in an unindexable file is not returned, silently | **CONFIRMED**, but not by the file predicted |
| `P94-3` | The partially-indexed count is non-zero | **FALSIFIED** — read 0 |
| `P94-4` | Sampling is disabled until statistics have run | **FALSIFIED** — independent jobs |
| `P94-5` | Content search resolves into a system-generated case | **CONFIRMED** |
| `P94-6R` | No separate pre-search reindex operation; any advanced-index controls live inside the search workflow | **CONFIRMED** — two levels deep, opt-in |
| `P94-7` | Two identical runs return identical counts in a quiet tenant | **CONFIRMED** |
| `P94-8` | Estimate and enumeration diverge | **FALSIFIED** — both 2 |
| `P94-11R` | An identical rerun may differ, without assuming a mechanism | **No change measured** |
| `P94-12` | Both Copilot entry points fail or prompt on invocation | **SPLIT** — one ran, one refused |
| `P94-image` | Determine empirically whether an image-only keyword is discoverable; do **not** pre-explain by licensing | **Discoverable.** My pre-explanation was wrong; the caution was correct |

`P94-6R` and `P94-11R` are replacements. The originals were withdrawn before
testing: `P94-6` predicted a control's absence from the guide's framing rather
than from the product, and `P94-11` embedded its own causal mechanism in the
claim. Both are recorded rather than edited away.

---

## 3. What was built

Nothing durable. Two reversible changes and one deliberate residue:

| Item | State at end of lab |
|---|---|
| Audit search job `LAB-AUDIT-MOD93-A` | Retained 30 days by the service; no tenant setting changed |
| Content search `LAB-EDISC-MOD94-A` | Exists in the Content Search case; inaccessible to `admin` after revocation |
| Three control files in one OneDrive account | **Left in place**, deliberately (§8.2) |
| `admin` in `eDiscovery Manager` | **Granted, then removed.** `POS-096` |
| Content Search case | **Created by the grant** (§8.5), not pre-existing |

---

## 4. Phase A — the audit log, read back for the first time

`POS-035` recorded `UnifiedAuditLogIngestionEnabled = True`, set by cmdlet on
2026-07-26 after the portal path failed on a surface that rendered two
simultaneous faults. Sixteen days later, the first read.

**Landing state, before any search.** `Searches completed 0`, `Active searches
0`, `Active unfiltered searches 0`, grid `0 items`, `No search history
available`. This tenant had never run an audit search. Default window
`Aug 10 2026 00:00` → `Aug 11 2026 00:00`. There is no `New search` control —
the form *is* the landing page.

**Field inventory, as rendered:**

| Column | Fields |
|---|---|
| Left | `Date and time range (UTC) Start` *, `Date and time range (UTC) End` *, `Keyword Search`, `Admin Units` |
| Middle | `Activities - friendly names`, `Activities - operation names`, `Record Types`, `Search name` |
| Right | `Users`, `ObjectId (File, folder, or site)`, `Workloads` |

Only the two date ranges are required.

**The submitted search.** Operation name `UserLoggedIn`; one user resolved via
the `Suggested Users` picker; window `Jul 26 2026 00:00` → `Aug 11 2026 00:00`
UTC; name `LAB-AUDIT-MOD93-A`. The end time was left at `00:00`, so the window
covers sixteen full days and **excludes the day of the search** — recorded
precisely so nothing later is attributed to a window it did not cover.

**Job progression:**

| Read | Status | Progress | Search time | Total results | Header |
|---|---|---|---|---|---|
| On submit | `Queued` | — | 8s | 0 | **`2 items`** |
| Refresh | `In progress` | 77.78% | 2m 13s | **8** | `1 item` |
| After return | `Completed` | 100% | 3m 46s | **19** | `1 item` |

Every zero and every intermediate figure in that table is **unpopulated rather
than empty**. `Total results 0` at `Queued` is a column that has not been
written; the `8` is a live count on an incomplete job; the `2 items` corrected
itself on second read. Three opportunities to record a wrong number as an
answer, in one job.

---

## 5. Phase B — three files, one keyword, one search

**The controls, validated before upload.** Each file contained the keyword
`ZARQON-MOD94-CTRL` — lab-invented, non-attributable, no real-world collision,
and safe to commit. The keyword appears in **no filename**, which would have
matched independently and destroyed the control.

| File | Type | Keyword location | Pre-upload validation |
|---|---|---|---|
| `mod94-positive.docx` | Word 2007+ | Body text | `docProps/core.xml` empty — no title/author/keyword leakage |
| `mod94-negA.png` | PNG 900×220 RGB | **Rendered pixels only** | **No tEXt/iTXt/zTXt chunks; literal string absent from file bytes** |
| `mod94-negB.labx` | Plain ASCII, renamed extension | Body text | Content trivially readable; extension unrecognised |

The PNG validation is load-bearing. Had the keyword survived in a metadata
chunk, a match could have occurred with no text extraction at all and the
result would have been uninterpretable. It did not — the only occurrence was
pixels.

All three were uploaded to one OneDrive account at 1:12 PM local. The search
completed at 2:57 PM, so **indexing latency is ruled out** as an explanation for
anything that missed.

**The query.** Data source scoped to one person, `Mailboxes and sites` left at
its shipped default. Condition builder `Keywords` / `Equal`, emitting
`Query: ((ZARQON-MOD94-CTRL))` — the literal survived unquoted, with the `Equal`
operator producing nothing visible in the KeyQL. Entering one keyword spawned an
`OR` slot, making multi-keyword logic structural rather than syntactic.

---

## 6. Failures, withdrawals, and three authoring errors

**One withdrawal.** The audit job list rendered `2 items` beside a single row on
submit and `1 item` on the next read. Transient settling of an async job, not a
standing surface disagreement — **withdrawn** rather than published at the
stronger reading. Same shape as Lab 22's Action Center propagation withdrawal.

**One method error.** An absence was pursued by scrolling a long dropdown. That
surface cannot establish absence, and the conclusion "no Entra sign-in friendly
name exists" is **not established** and is not written as though it were. The
authoritative enumeration — a `View list of operation names` link — was not
visited.

**Three authoring errors, all Claude's, all consequential:**

1. Exchange Online cmdlets issued with **no connection step**, so
   `Get-AdminAuditLogConfig` did not exist in the shell. The run produced no
   measurement.
2. A literal placeholder `<labuser UPN>` left inside a runnable command block.
   Parser error; no measurement.
3. **A fabricated timestamp.** A clock value was stated in a table of measured
   marks as though it had been reported. It had not been asked for or supplied.
   Caught by the operator, corrected on the record, and noted here because an
   invented measurement among real ones is the worst failure available to this
   project.

Errors 1 and 2 forced the browser-closure clock to be restarted, which is why
`P93-2` resolves only partially: the job had completed roughly 1h45m before the
browser was finally closed. **A completed job persists across full browser
termination and is discoverable on return.** Whether a *running* job survives
closure is untested and is not claimed.

**Four falsifications of my own predictions** are recorded in §8 where each was
measured, rather than collected here: `P94-3`, `P94-8`, `P94-image`'s
pre-explanation, and two claims about the case lifecycle in §8.5.

---

## 7. Findings — Phase A, the audit log

### 7.1 The cost model has three mechanisms, not one

`MOD-92`'s guide places auditing on the per-user licensing side, with no
consumption charge for enabling or searching. The Audit solution's own left
navigation carries **`Pay-as-you-go usage report`**, and
`Settings → Roles and scopes → Optical character recognition (OCR)` states that
OCR scanning is **charged per use and requires Microsoft Syntex billing**. Three
distinct mechanisms inside one product: E5-family per-seat entitlements, a
pay-as-you-go audit meter, and a Syntex consumption meter.

### 7.2 `POS-035`'s read side is closed

19 records over sixteen days, `Completed`, `100%`, `3m 46s`. `Get-AdminAuditLogConfig`
still reads `UnifiedAuditLogIngestionEnabled : True`. The pipeline ingests, has
been ingesting, and retrieves. Recorded at **`POS-095`**.

### 7.3 A mid-run count is not a partial answer

`Total results` populated during the run — `8` at 77.78%, `19` at completion.
Not proportional. `Progress` rendered exactly `77.78%`, which is 7/9, so the job
steps a fixed unit count rather than estimating. An analyst reading the
in-progress figure would have been wrong by more than half.

### 7.4 One field, three representations

| Surface | `RecordType` |
|---|---|
| Portal results grid | `AzureActiveDirectoryStsLogon` |
| Portal record flyout | `15` |
| CSV export column | `15` |
| `Search-UnifiedAuditLog` | `AzureActiveDirectoryStsLogon` |
| Raw payload `Workload` | `AzureActiveDirectory` |

The flyout agrees with the export; the grid agrees with the cmdlet. **The Azure
AD-era vocabulary is a rendered grid column**, not a buried payload value, on a
2026 Purview surface for a product renamed more than two years ago.

### 7.5 The cmdlet returns a wrong row count, silently

Portal export 19; `Search-UnifiedAuditLog` **21**, identical scope and bounds.
The sets were diffed rather than estimated:

| | |
|---|---|
| In cmdlet, not in export | two timestamps, both already present once |
| In export, not in cmdlet | none |

`Identity` settles it — the same record GUID at two `ResultIndex` positions
(9 and 12; 14 and 17), `ResultCount 21`. **Nineteen distinct records; two
emitted twice.** No error, no warning. An analyst counting rows overcounts by
ten percent unless they deduplicate on `Identity`.

### 7.6 `UserLoggedIn` does not mean a human logged in

The record examined in detail carried:

```
RequestType    OAuth2:Token
UserAgent      Windows-AzureAD-Authentication-Provider/1.0
ClientIP       (Microsoft address space)
```

A non-interactive token acquisition, rendered in the grid as `User logged in`,
indistinguishable from the interactive sign-ins in the same result set. The
direct analogue of this repository's `4624 does not mean a human logged in`,
now measured on a second product.

### 7.7 Seven renderings of one timestamp

| Surface | Rendering | Zone stated? |
|---|---|---|
| Query header | `Sun, 26 Jul 2026 00:00:00 GMT` | GMT |
| Results grid column | `Aug 10, 2026 11:27 PM` | `Date (UTC)` |
| Job list column | `Aug 11, 2026 9:24 AM` | `Creation time (UTC-07:00)` |
| CSV `CreationDate` | `2026-08-10T23:27:39.0000000Z ` *(trailing space inside the quoted value)* | `Z` |
| Raw JSON `CreationTime` | `2026-08-10T23:27:39` | **No** |
| Cmdlet `CreationDate` | `8/10/2026 11:27:39 PM` | **No** |
| Record flyout | `2026-08-10T23:27:39` under `Date (UTC)` | Label only |

All reconcile to the same instant. **The authoritative object is the only one
that never says what timezone it is in.** A statistics page later rendered
`August 11, 2026, 15:35 PM` — 24-hour hour with a `PM` suffix — for an eighth
form.

### 7.8 Labels that do not describe their contents

The flyout's `Users` field renders the subject's **object GUID**; the UPN
appears further down as `UserId`, while the grid's `User` column rendered the
UPN. `Item` renders a well-known first-party **application ID** under a label
that reads as a document. And the flyout **never names the raw object** — the
container the CSV calls `AuditData` has no label on the surface displaying it.

### 7.9 The friendly-name vocabulary is not a query key

Two duplication classes on one surface: identical labels **across** activity
groups, and identical labels repeated **within** a single group. The selected
chip drops the group qualifier, so the field then displays a value that no
longer identifies what was chosen. `Activities - operation names` takes the
schema string and is what the search ran on.

### 7.10 A production surface leaking format tokens

The completed job's `Search Query Information` header renders
`, , {9} {10} {11} {12}` — positional format-string indices standing in for the
empty optional criteria. Customer-facing, on a Microsoft security product.

---

## 8. Findings — Phase B, content search

### 8.1 Global Administrator is refused, by design

`eDiscovery Manager` held **0 users, 0 security groups**. Content Search
rendered two **stacked** modals: a `Client Error` reading only *"Missing
required permissions to view case"*, and beneath it a `Permission Error`
carrying the cause and the remedy in full.

**The useless one renders on top.** A user who dismisses the first and navigates
away never sees the actionable one.

Behind both, the page chrome rendered fully — `Case settings`, `Process
manager`, `Summarize this case`, and the descriptive text — while every
data-bearing element was withheld. The defect is narrower and more precise than
"chrome renders on refusal": **case-scoped action buttons render without the
case being readable**, which is what makes them misleading. Recorded at
**`POS-096`**.

### 8.2 Two of three files returned — and not the two expected

| File | Returned |
|---|---|
| `mod94-positive.docx` | Yes |
| `mod94-negA.png` | **Yes** |
| `mod94-negB.labx` | **No** |

`Total matches 2 (11 KB)`, `Locations 1/2`, `Site 2 items`, `Mailbox 0 items` —
correct, since nothing was mailed. The sample enumeration named the two files
and agreed with the statistics estimate exactly.

The `.labx` is plain ASCII containing the keyword in body text. **It is not a
format the service cannot read; it is an extension the service does not index.**
The PNG, which is genuinely unreadable without text extraction, came back.

### 8.3 The image was extracted with every visible OCR control disabled

Two OCR surfaces, both off:

| Surface | State |
|---|---|
| `Settings → Roles and scopes → Optical character recognition (OCR)` | `OCR scanning` **unchecked and greyed**, blocked behind Microsoft Syntex billing. PNG is explicitly in its supported-formats list |
| `Case settings → Search & analytics → Optical character recognition` | `Enable OCR` **unchecked** |

The keyword existed in the PNG **only as rendered pixels** — verified before
upload. It returned anyway. Text extraction from images happens on a path
neither visible setting governs. Recorded at **`POS-098`**.

This falsifies a claim I made before measuring: that the image would be missed
because OCR applies only after review-set collection. A reviewer flagged the
pre-explanation as improper before the test ran, and the tenant then disproved
it.

### 8.4 Three surfaces, three zeros, one readable file

| Run | Configuration | `Total matches` | Gap reported |
|---|---|---|---|
| 1 | Defaults, all statistics sub-options unchecked | 2 | *no gap surface offered* |
| 2 | `Include partially indexed items` ✓ | 2 | `Partially indexed items: 0 (0 B)`; `Indexed 2 / Partially indexed 0` |
| 3 | ✓ plus `Perform advanced indexing` ✓ | 2 | `Matches from advanced indexing: 0 (0 B)`; `Indexed after advanced indexing: 0 items` |

Run 3 demonstrably executed rather than being skipped — the card set changed
(`Partially indexed items` was replaced by `Matches from advanced indexing`, and
the Indexing status qualifier moved from *"without advanced indexing"* to
*"indexed items and advanced indexed items"*), and it took roughly six minutes
against one for the earlier runs. Different cards, same numbers.

**The guide's thesis is that a keyword search is silently incomplete unless you
account for partially indexed items. Measured: accounting for them, and then
reindexing them, still misses it.** Extension-based exclusion sits outside the
partially-indexed model entirely, so no amount of opting in reveals it.

The gap surface is also **off by default**, and checking it reveals two further
nested options — one of them advanced indexing — plus a third-level runtime
warning. The advanced-indexing control **cannot be discovered without first
checking a box that ships unchecked**.

Without `mod94-positive.docx` returning, none of this would be a finding. The
positive control is what converts "the search found nothing" into a defensible
statement — the same logic as Lab 22's EICAR run against the PUA silence.

### 8.5 The access boundary, granted and revoked

```
eDiscovery Manager empty          → Content Search refused; Cases list 0 items
+ eDiscovery Manager (Manager)    → case visible and Active within ~5 minutes,
                                    with no sign-out and no token refresh
− eDiscovery Manager              → 0 users on three surfaces;
                                    UI still fully permitted, two reads 15 min apart
[write attempt: remove a member]  → backend refuses —
                                    "you're not a member of this compliance case"
[immediately after]               → Cases list back to 0 items
```

**Only attempting an operation revealed the true state.** Three role-management
surfaces and the case's own `Permissions` page all rendered a state the service
did not honour. This is `configured ≠ effective` on the **revocation** side —
the more dangerous direction, because an administrator would remove the role,
verify it on exactly the surfaces built for that question, and reasonably
conclude the boundary had closed. Recorded at **`POS-097`**.

Two claims of mine were falsified here and are recorded rather than removed:

- **The case did not pre-exist.** I read a blank `Created` column as evidence
  that it did. `Case settings` gives `Case created: 8/11/2026 8:51:57 PM
  +00:00` — three minutes before the first search, i.e. **created on first
  access after the grant**.
- **Persisting access was not explained by direct case membership.** I proposed
  that mechanism from the `Permissions` page listing the user. The backend
  contradicted it in the same minute, refusing a write on the grounds that no
  such membership existed. The persistence was a **stale client view over a
  service that had already revoked**.

The refusal surfaced a raw `Microsoft.Exchange.Management.Tasks.ComplianceCaseMemberTaskException`
and a case GUID directly in a customer-facing dialog, under the same generic
`Client Error` title used for the unrelated refusal in §8.1.

### 8.6 Two Copilot integrations, two provisioning states

| Entry point | Behaviour |
|---|---|
| `Draft a query with Copilot` (Preview) | Controls enabled on input; rendered `Generating KeyQL…`; **declined on the prompt's content** |
| `Summarize this search` | **Refused** — *"Copilot hasn't been set up yet. To get Copilot, contact Security/Global Administrator."* |

Same session, same identity, same page. The first is a content-level failure
after a successful invocation; the second is an availability refusal.

**This narrows `POS-091`.** MOD-88 tore down Security Copilot capacity, and
`POS-091` recorded the missing Defender pane as *"torn down and therefore
absent."* The summarizer here is consistent with that. The KeyQL drafter is
**not gated on that capacity** and ran without it. The earlier framing remains
correct for the surface it described and **must not be generalised** to every
surface bearing the Copilot logo.

The refusal pane also rendered a `Using Microsoft Learn documentation` input —
a degraded documentation fallback offered inside the refusal.

### 8.7 Structural observations

- **Content Search is a peer of `Cases` in the left navigation** but resolves
  into a case, with breadcrumb `Cases > Content Search`.
- **The source picker cannot be browsed** — `No items yet. Please search first.`
  You cannot enumerate sources; you must know who you are looking for.
- **Attaching a source never displays a location.** The panel shows workload
  icons (Exchange, OneDrive) and no site URL anywhere on the path.
- **`New search` is a two-field modal** — name and description only. Sources and
  query come after, so the object exists before it is configured.
- **`Statistics` and `Sample` are independent jobs**, chosen before the run and
  each requiring its own invocation. Neither gates the other.
- **The sample grid uses mail-shaped column headers** — `Subject/Title`, `Date`,
  `Sender/Author` — for a result set containing only files. `Sender/Author`
  renders the UPN of the file's owner.

---

## 9. What this cost, and what was left behind

**$0.** No VMs were started; both remained deallocated for the entire session.
No consumption meter was touched. `Try for free` on the OCR estimation trial was
deliberately **not** selected — it starts a 30-day clock and is mutually
exclusive with enabling scanning, and nothing here required it.

**Left in the tenant deliberately:**

- **The three control files**, in one OneDrive account. They are the physical
  evidence behind §8.2 and §8.4, they cost nothing, and deleting them would make
  the central finding unreproducible. Precedent: Lab 22's pending PUA
  quarantine. If anything ever acts on them, the state gets read before it is
  actioned.
- **The `Content Search` case and the `LAB-EDISC-MOD94-A` search.** Created by
  the grant; now inaccessible to `admin` following revocation.

**Reverted:** `admin`'s `eDiscovery Manager` membership. `eDiscovery Manager`
holds 0 users and 0 security groups, verified on three surfaces and confirmed
functionally by a refused write and a `0 items` Cases list.

**Discovered incidentally, and open.** A role-group export taken while reading
defaults showed **`Insider Risk Management` holding one user** — `admin`,
17 roles, `Organization` scope, **no expiry**. It is the only populated role
group of 69 in the tenant, it predates this lab, and no committed lab records
granting it. The *export* revealed it; reading role groups one flyout at a time
would not have. Carried as an open item.

---

## 10. References

- Microsoft Learn — *Search the audit log*
- Microsoft Learn — *Export, configure, and view audit log records*
- Microsoft Learn — *Turn auditing on or off*
- Microsoft Learn — *Learn about eDiscovery*, §*Notable changes in eDiscovery*
- Microsoft Learn — *Manage audit log retention policies*
- `SANITIZATION.md` §2 — device-name placeholders, including the
  `LAB-WIN11-DEFEN` truncation alias originating in this lab's audit payloads
