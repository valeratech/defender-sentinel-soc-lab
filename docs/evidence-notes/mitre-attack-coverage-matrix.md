---
title: The MITRE ATT&CK coverage matrix — a page whose numbers are a function of its filters
date: 2026-08-14
artifacts:
  labs: []
  posture: [POS-045, POS-046]
  divergences: [213, 214]
  kql: []
corrections:
  - "P104-3 was scored `unsupported - never measured` on a first read. Its registered falsifier read 'Falsified if it renders any other version, or no version at all' - absence was inside the falsification criterion from the start. Two errors stacked: an absence recorded on a first observation, and scored against a category never registered. Re-read 2026-08-16 in a separated sitting: still no version string anywhere. P104-3 is FALSIFIED."
  - "P104-5 registered four options including 'one further Microsoft-supplied category such as Fusion or Microsoft security rules'. The fourth is `Active custom detection rules` - not Fusion, and not Microsoft-supplied at all; custom detections are customer-authored Defender XDR objects. The miss was in kind, not wording. Scored Partial under the compound-verdict convention; read literally the registered falsifier would have said Falsified."
  - "Claude stated 'POS-045 and POS-046 confirmed Enabled' from a pane reading `2 Active scheduled query rules` - an aggregate, not an identification. Two known repo rules plus a count of two is inference. Corrected by following the pane's `View` control to a filtered Analytics page that named both rules; only then was the refresh observation."
  - "docs/attack-coverage.md reports 2 detections on T1110 where the portal reports 7. Not a divergence: the generated doc counts detection specs in detections/, the portal counts deployed analytics-rule populations including five anomaly rules with no specs here. Two documents counting different universes. No change made to build-attack-matrix.py or docs/attack-coverage.md."
  - "Prediction IDs for this module are module-scoped (P104-n) and match no repo counter. Adopted deliberately after the Lab 25 prefix error, to avoid naming a lab number before one could be allocated."
---

# The MITRE ATT&CK coverage matrix

> Nominally a page showing which attacker techniques your detections cover.
> Actually a page whose every number moves with a filter it does not advertise,
> rendered on a colour scale whose thresholds are published nowhere.

## What was configured

Nothing. There is no writable control on this page. That is why the walkthrough earns
no lab and no new posture entry despite producing two divergence rows — it is a
read surface reporting on objects configured elsewhere.

## What was established

**The default population is broader than the documentation states.** `Active
rules` ships at `4 selected` — scheduled query, NRT query, anomaly query, and
**custom detection** rules. `sentinel/mitre-coverage.md` (`ms.date: 06/16/2025`)
says scheduled and NRT. Custom detection rules are Defender XDR objects, so this
is not a Sentinel-only view. Divergence 213.

**Recommended coverage renders a count, not a ratio.** `Active coverage (7)`
decomposing to 2 scheduled + 5 anomaly, alongside `Simulated coverage (0)`. No
products dimension, no denominator. Divergence 214.

**`POS-045` and `POS-046` re-verified by name** on 2026-08-14 via the technique
pane's `View` control into a filtered Analytics page. Both had carried
`revisit: true` since 30–31 July.

**The legend has no published semantics.** Four bands — None, Low, Medium, High —
no thresholds anywhere, and the `Legend` icon is non-interactive with no tooltip.
The count driving the colour moves with `Active rules`. The colour is therefore a
property of filter state, not of posture.

**The default view truncates on both axes with no extent indicator.** Confirmed
twice. With the details pane empty it consumes the horizontal budget for two
tactic columns that carry active coverage; with the pane populated and the matrix
scrolled, columns are cut off in the other direction. Roughly ten rows render
against headers claiming up to 47 techniques.

**Simulated coverage spans three populations** — `Analytics rule templates`,
`Hunting queries`, `Anomaly rules` — which places `docs/evidence-notes/hunts.md` / `docs/evidence-notes/hunting-queries.md` inside this page
rather than downstream of it.

**Fingerprint, stable across two sittings:** 250 techniques across 14 tactics at
`Matrices type view : 13 selected`.

**No framework version string and no Preview label**, on two separated reads
(2026-08-14, 2026-08-16), after checking the page title, the `Legend` control,
the `Simulated rules` ⓘ, and both dropdowns. The docs assert ATT&CK v18 and carry
an IMPORTANT preview banner; the portal states neither.

## What was corrected

See `corrections:`. Two scoring errors of my own — an absence recorded on a first
read, and a posture refresh stated as observation when it was inference — plus a
prediction whose miss was in kind rather than wording.

## What could not be tested

The framework version cannot be established from this surface at all; the 250/14
fingerprint is indirect and depends on the matrix filter. Whether the legend's
bands correspond to any published threshold is unanswerable from the product.

## Cost

$0. Read-only surface, no billable operation.
