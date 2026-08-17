---
title: Auditing in Microsoft Purview — Standard, Premium, and what the tier boundary actually gates
date: 2026-08-11
artifacts:
  labs: []
  posture: []
  divergences: [199]
  kql: []
corrections:
  - "Guide: auditing sits on the per-user licensing side of the cost model, and enabling or searching it generates no consumption charge. The Audit solution's own left navigation carries a Pay-as-you-go usage report, and tenant-level OCR scanning inside Purview is billed per-use against Microsoft Syntex. Purview carries at least three distinct cost mechanisms, not one."
  - "Guide: audit log ingestion is enabled by default for organizations with a qualifying subscription. Microsoft's current documentation explicitly exempts unmanaged tenants using free trials of enterprise licences. Whether this tenant fell in that class is not established — POS-035 measured ingestion disabled and enabled it by cmdlet, but the mechanism recorded there was a dehydrated Exchange organisation, not trial status."
---

# Auditing in Microsoft Purview

> The tier guide. It produces no tenant state and its retention numbers cannot
> be tested here at all. Its contribution is one distinction that the next two
> guides keep running into: **Premium is per-user and assignment-gated**, so
> owning E5 at the tenant level does nothing for a user until the licence lands
> on their account.

## What was configured

Nothing. The source guide is descriptive, and the one setting it describes —
unified audit log ingestion — was already enabled by cmdlet on 2026-07-26 and
is recorded at `POS-035`. Re-enabling it here would have duplicated an existing
posture entry rather than adding evidence.

## What was established

**The tier boundary is licensing and retention, not capability.** Both tiers
expose the same retrieval surfaces — the Audit search tool, the
`Search-UnifiedAuditLog` cmdlet, the Audit Search Graph API, CSV export, and the
Office 365 Management Activity API. Premium adds more history, policy control
over that history, high-value events, and API throughput. It does not add a
retrieval method.

**Premium is per-user and assignment-gated.** Premium audit events are generated
for a user only after the qualifying licence is assigned to that account. A
tenant-level E5 entitlement produces nothing for a user who does not hold it,
and unlicensed users and guests fall back to 180-day retention regardless.

This is the source guide's one durable contribution to the rest of the section, and
it generalises: the same shape appears in `docs/evidence-notes/ediscovery-content-search.md`, where Global Administrator —
the highest tenant privilege — grants no content-search access at all, because
that access is gated on a role-group assignment rather than inherited from
tenant ownership. **Entitlement is not assignment**, on two different axes, in
two consecutive guides.

**Retention figures, recorded as documented and not measured.** Standard retains
180 days; Premium raises the default to one year; ten years requires a separate
per-user add-on. Premium also ships an unmodifiable default retention policy of
one year for Exchange, SharePoint, OneDrive and Microsoft Entra records, and
non-user records are retained a fixed one year that is not configurable.

## What could not be tested

**Every retention figure in the guide, without exception.** Unified audit
ingestion was enabled on 2026-07-26; the search in `docs/evidence-notes/purview-audit-log-search.md` ran on 2026-08-11.
Sixteen days of history cannot test 180 days, one year, or ten. These are not
"not yet tested" — they are **not testable in this tenant's lifetime**, and the
distinction matters because a future reader should not expect a later lab to
close them.

The one 30-day figure that *is* testable belongs to a different object. Audit
**search jobs** are retained 30 days; the **records** they search have their own
licensing-based retention. Same word, two clocks. `docs/evidence-notes/purview-audit-log-search.md` exercised the job side.

**Whether Premium-attributable behaviour is observable here at all** is also
unresolved and now perishable. The E5 trial converts on 2026-09-15 to a single
paid licence. Any Premium-tier observation has to be captured before then or it
stops being available.

## What was corrected

Two claims, both about cost and both recorded in the frontmatter above.

The guide's cost framing — auditing is per-user licensing, not per-resource
consumption — collapsed on first contact with the portal. The Audit solution
renders a **Pay-as-you-go usage report** in its own left navigation, and
`Settings → Roles and scopes → Optical character recognition (OCR)` warns that
OCR scanning is charged per use and requires Microsoft Syntex billing. Three
cost mechanisms inside one product: E5-family per-seat entitlements, a
pay-as-you-go audit meter, and a Syntex-billed consumption meter.

The unmanaged-trial exemption is recorded as a **qualification, not a
confirmation**. Microsoft's current documentation exempts unmanaged tenants on
free enterprise trials from default-on auditing, and this tenant did measure
auditing disabled. But `POS-035` and `POS-036` recorded a different mechanism —
a dehydrated Exchange organisation — and this tenant has held an `admin`
identity since creation, which is not obviously the "unmanaged" class Microsoft
means. Adopting the doc's explanation would substitute a plausible mechanism for
the one actually measured.

## Cost

$0. No configuration, no VMs, no consumption. The source guide's only cost content is
the discovery that the guide's cost model was incomplete.

## Cross-references

`POS-035` (unified audit ingestion enabled by cmdlet, Lab 09) · `POS-036`
(Exchange organisation hydration) · Lab 23 §7.1 · `docs/evidence-notes/purview-audit-log-search.md` · `docs/evidence-notes/ediscovery-content-search.md` (the
assignment-gating shape, on the RBAC axis)
