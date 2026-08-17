---
title: Threat intelligence indicators — a reference dataset nothing was joined to
date: 2026-08-14
artifacts:
  labs: ["25"]
  posture: []
  divergences: [215]
  kql: []
corrections:
  - "Prediction IDs for this lab were registered as P26-n, from a lab number inferred off the reservation note 'MOD-95 is Lab 25'. Lab numbers are allocated in build order and a module number never reserves one. The lab is 25; the prefix stays as registered because a prediction ID is evidence of what was written before portal contact."
  - "P26-3 registered a query within ~60 seconds of creation. The window elapsed before the first query ran, so the condition was never met. Recorded UNTESTABLE with reason, not falsified. Not reopenable on this object."
  - "Claude asserted that TLP and severity 'live inside Data (dynamic)'. That was inference from their absence in the column list, not measurement - neither field was populated on this object. Microsoft documents TLP as AdditionalFields.TLPLevel; severity storage remains unverified here. What is measured is only that neither is a promoted column."
  - "Claude characterised the ingestion cost of manual TI from recollection before measuring, and then described it as 'ordinary ingestion'. The measured claim is narrower: this record carried _IsBillable True and _BilledSize 786. No meter, rate, or comparison to other TI paths is asserted."
---

# Threat intelligence indicators

> The source guide reads as "connect a threat feed." What it is actually about is
> putting a **reference dataset** where the correlation engine can join against
> it — and the tenant's answer was that nothing was joined to it at all.

## What was configured

One STIX indicator created by hand in Intel management: `ti-lab-test.invalid`,
domain-name type, `LAB-TI-Test-Domain`. No connector, no solution, no feed.
Revoked at teardown 2026-08-16 21:27 PDT. Full record in **Lab 25**.

## What was established

**The chain breaks at link two.** Zero active analytics rules reference a TI
table. The indicator existed, was valid, was unrevoked, and was marked billable —
and could never have produced a detection. `configured ≠ effective` demonstrated
end to end.

**This record was marked billable.** `_IsBillable: True`, `_BilledSize: 786`
bytes, measured directly — for an indicator with no description, tags, TLP, or
severity, so a floor rather than a typical size. Which meter applies, at what
rate, and whether other TI ingestion paths behave the same way were not measured
and are not asserted.

**The legacy table exists and is empty.** `ThreatIntelligenceIndicator` is
present, queryable, Analytics tier, 30 days, and returned **zero rows**. Current
Sentinel TI ingestion no longer targets it — data landed in
`ThreatIntelIndicators` — and this workspace was created after that migration.
The Intel management empty state names the legacy table as the destination for TI
data while the same page banners the migration away from it. Divergence 215.

**TLP and severity are not promoted columns.** `getschema`, 2026-08-16: 23
columns, neither present. Both render in the details pane. Where a populated
value is stored was **not established by this object** — both were left unset at
creation, so only their absence from the column list is measured. Microsoft
documents TLP as `AdditionalFields.TLPLevel`; severity storage is unverified
here. Either way, no analytics rule can filter on them as columns.

**Append-only semantics hold.** Revocation wrote a **new row** rather than
mutating the original: two rows, one `Id`, the 2026-08-14 row unchanged at
`IsActive: true`. P26-6 confirmed.

**Object metadata records form-open time, not creation time.** `created`,
`modified`, and `valid_from` all stored 15:30 for an object that came into
existence at 15:45. `Modified` never moved — not on creation, not on revocation
two days later.

**`Id` encodes the source.** `base64("Microsoft Sentinel")---indicator--<uuid>`,
verified both directions. Identical intelligence from a different source escapes
deduplication.

## What was corrected

See `corrections:`. A prefix registered off an inferred lab number, an untestable
prediction recorded as such, a storage claim asserted from absence rather than
measurement, and a cost characterisation stated before it was measured.

## What could not be tested

Whether MDTI-sourced or TAXII-sourced indicators bill differently from manual
creation — the connector paths were deliberately not exercised. Where TLP and
severity are stored when populated. The 27 out-of-the-box TI analytics rules the
portal claims are "currently available in the Analytics blade" do not exist here;
whether they ship with the Threat Intelligence solution is unproven.

## Cost

Effectively $0 at this volume. 786 bytes, marked billable; query execution
unbilled. Scaling arithmetic rather than a priced estimate: a million-indicator
feed is ~786 MB per ingest against a table that appends rather than updates.
