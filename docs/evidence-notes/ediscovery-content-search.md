---
title: Content search in eDiscovery — the file the safety net does not catch
date: 2026-08-11
artifacts:
  labs: [23]
  posture: [POS-096, POS-097, POS-098]
  divergences: [193, 194, 195, 196, 197, 198, 200, 201, 202]
  kql: []
corrections:
  - "Guide: sampling options only become available after statistics have been generated. Statistics and Sample are mutually exclusive radio buttons chosen before the run, and the Sample tab is always reachable, always renders empty until its own Generate sample results action is invoked. Two independent jobs against one query; neither gates the other."
  - "Guide presents three partially-indexed options as peers on the search screen. Include partially indexed items ships unchecked, and checking it reveals two further nested options — one of them advanced indexing — plus a third-level warning about runtime. The advanced-indexing control cannot be discovered without first checking a box that is off by default."
  - "Guide: advanced indexing is the reprocessing pass that shows how much a search would have missed. It ran and reported Matches from advanced indexing 0 against a file that was present, plainly readable, and absent from the results. The remediation mechanism does not consider extension-excluded content to be a gap."
  - "Claude predicted the image-only control would be missed because OCR applies only after review-set collection. Falsified: the PNG returned while tenant OCR scanning was unchecked and greyed behind Syntex billing AND the case's own Enable OCR was unchecked. Text was extracted from image pixels by a path neither visible OCR setting governs."
  - "Claude predicted a non-zero partially-indexed count. Falsified: the count read 0 while a file containing the keyword sat unreturned in the searched location."
  - "Claude claimed the Content Search case pre-existed and was merely invisible, reading a blank Created column as evidence. Falsified by Case settings: the case was created 8/11/2026 8:51:57 PM +00:00, three minutes before the first search, i.e. on first access after the role grant."
  - "Claude claimed access persisting after role-group removal was explained by a direct case membership. The backend contradicted it — a write attempt returned 'you're not a member of this compliance case' while the Permissions page listed that membership. The persistence was a stale client view over a service that had already revoked."
---

# Content search in eDiscovery

> Nominally: run a keyword search across mailboxes and sites. Actually: three
> files were planted in one location containing one keyword, **two came back**,
> and the surface built specifically to tell you what a search missed reported
> that nothing was missed.
>
> Also, unavoidably, an RBAC lab — because the walkthrough could not begin until a
> refusal was resolved, and the refusal turned out to be more interesting than
> the search.

## What was configured

Two deliberate, reversible changes, both recorded as posture actions rather than
setup steps:

1. **Three control files** planted in one OneDrive account, containing one
   lab-invented keyword. **Left in place** as committed evidence, matching Lab
   22's pending-quarantine precedent — deleting them would make the central
   finding unreproducible.
2. **A temporary privilege expansion**: `admin` added to the `eDiscovery
   Manager` role group at the Manager tier, then removed. Recorded at `POS-096`
   as a posture weakening, not as a prerequisite.

## What was established

**The control pair, and what it caught** (Lab 23 §8.2, divergence 200). Three
files, same account, same keyword, keyword never in a filename:

| Control | Keyword lives in | Returned |
|---|---|---|
| `.docx` | Ordinary body text | **Yes** |
| `.png` | Rendered pixels only | **Yes** |
| `.labx` (plain ASCII, unrecognised extension) | Body text | **No** |

The positive control is what makes the miss conclusive rather than an
unsupported absence — the same logic as Lab 22's EICAR run against the PUA
silence. Without it, "the search found nothing" is a claim about the search.
With it, the search demonstrably works and one file is invisible to it.

**Three surfaces, three zeros, one file that plainly exists** (Lab 23 §8.4,
divergence 201, `POS-098`). The `.labx` was absent from the results; the
`Partially indexed items` card read **0 (0 B)**; a rerun with **advanced
indexing** enabled read `Matches from advanced indexing 0` and `Indexed after
advanced indexing 0 items`. The advanced-indexing pass demonstrably executed —
the card set changed and the run took roughly six minutes against one — and
found nothing.

The guide's warning is that a keyword search is silently incomplete unless you
account for partially indexed items. **Measured: accounting for them, and then
reindexing them, still misses it.** Extension-based exclusion sits outside the
partially-indexed model entirely, so it is not a gap the tooling is built to
report and no amount of opting in reveals it.

**The image was extracted with every visible OCR control disabled** (`POS-098`,
divergence 202). Tenant-level `OCR scanning` at
`Settings → Roles and scopes → Optical character recognition (OCR)` is
**unchecked and greyed**, blocked behind Microsoft Syntex billing, with PNG
explicitly in its supported-formats list. The case's own
`Search & analytics → Enable OCR` is also **unchecked**. The keyword existed in
`mod94-negA.png` only as rendered pixels — verified before upload with no
tEXt/iTXt/zTXt chunks and the literal string absent from the file bytes. It
returned anyway. **Text extraction from images happens on a path that neither
visible OCR setting governs.**

**Global Administrator does not inherit content-search access** (`POS-096`,
divergence 193). `eDiscovery Manager` held **0 users and 0 security groups** by
default; Content Search refused with a `Permission Error` explaining that
content searches are part of an eDiscovery case and that the identity is not a
member. This is separation of duties working as designed: a tenant
administrator can manage everything and still not read the organisation's mail
and documents. It is also the licensing trap from `docs/evidence-notes/purview-audit-tiers-and-licensing.md` on a second axis —
**entitlement is not assignment**.

**The RBAC cycle, measured end to end** (`POS-097`, Lab 23 §8.5):

```
eDiscovery Manager empty        → refused; Cases list 0 items
+ eDiscovery Manager (Manager)  → case visible and Active within ~5 min,
                                  no sign-out, no token refresh
− eDiscovery Manager (0 users,
  confirmed on three surfaces)  → UI still fully permitted, two reads 15 min apart
[write attempt]                 → backend refuses: "you're not a member of
                                  this compliance case"
[immediately after]             → Cases list back to 0 items
```

**Only attempting an operation revealed the true state.** Three role-management
surfaces and one case-permissions surface all rendered a state the service did
not honour. This is `configured ≠ effective` on the **revocation** side, which
is the more dangerous direction: an administrator would remove the role, verify
it on the surfaces built for exactly that question, and reasonably conclude the
boundary had closed.

**Two Copilot integrations on one page, two provisioning states** (divergence
198). `Draft a query with Copilot (Preview)` opened, enabled its controls on
input, rendered `Generating KeyQL…`, and declined on the prompt's content.
`Summarize this search` refused outright: *"Copilot hasn't been set up yet."*
Same session, same identity, same page. **This narrows what `POS-091`'s
"torn down and therefore absent" can be claimed to explain** — the summarizer is
consistent with the `docs/evidence-notes/tearing-down-copilot-capacity.md` capacity teardown, the KeyQL drafter is not gated on
it, and the earlier framing must not be generalised to every surface bearing the
Copilot logo.

## What was corrected

Four guide claims and **four falsifications of my own predictions**, all in the
frontmatter above. The four self-falsifications are the useful part of this
walkthrough's record: I pre-explained the image control's outcome from licensing
before measuring it, predicted a partial-index count that read zero, read a
blank `Created` column as evidence that a case pre-existed, and proposed a
mechanism for persisting access that the backend directly contradicted. A
reviewer flagged the first before it was tested; the rest were caught by the
tenant.

## What could not be tested

**Why the `.labx` is excluded** — extension, content sniffing, or an indexer
policy — is not established. Only that it is, and that neither the
partially-indexed report nor advanced indexing surfaces it.

**Why `Add to review set` stayed greyed.** Initially read as licensing; `Case
settings` then showed `License: eDiscovery (Premium)` with the toggle **on**, so
licensing is ruled out and the cause is unknown. Recorded as unknown.

**Whether the removal refusal would have succeeded from an eDiscovery
Administrator.** The diagnostic payload behind the `Client Error` dialog was not
captured, and the state is not reproducible from this identity now that access
has closed.

## Cost

$0. No VMs, no consumption meters touched. `Try for free` on the OCR estimation
trial was deliberately not selected — it starts a 30-day clock and is mutually
exclusive with enabling scanning, and nothing here needed it.

## Cross-references

Lab 23 §8 · `POS-096` · `POS-097` · `POS-098` · `POS-091` (Copilot teardown —
narrowed by this walkthrough) · Lab 20 (`docs/evidence-notes/tearing-down-copilot-capacity.md` capacity teardown) · Lab 22 (the
negative-then-positive control precedent, and the deliberately-left evidence
precedent) · `docs/evidence-notes/purview-audit-tiers-and-licensing.md` (entitlement is not assignment, licensing axis) ·
`SANITIZATION.md` §2 (the `LAB-WIN11-DEFEN` alias originates in this walkthrough's
audit payloads)
