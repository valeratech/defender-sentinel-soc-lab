# Purview DLP — Terms, Mechanisms, and Where Each Was Measured

<!-- DRAFT — commits with Lab 14. POS-059+ references resolve when the Lab 14
posture entries land in the same commit. -->

Every term below was encountered live during Lab 14 (module 66). This is a
reference, not a narrative — the narrative is the lab README. Each section says
what the mechanism is, what the portal showed when it was measured, and where the
observation is recorded. Splunk analogies included where they hold; DLP has fewer
of them than the SIEM layer did, because Splunk has no native equivalent of
content-aware policy enforcement.

## Sensitive information type (SIT)

A pattern-based classifier: a primary pattern (regex or function) plus optional
corroborating evidence (keywords, checksums) plus a proximity window. 327 were
available in the policy wizard's Add dialog on 2026-08-02; Microsoft publishes
every definition at learn.microsoft.com (`sit-defn-*` pages).

Anatomy, using the three SITs in the U.S. Financial Data template:

| SIT | Primary pattern | Corroboration | Validation |
|---|---|---|---|
| Credit Card Number | digit formats | keywords/context for lower tiers | **Luhn check** — High confidence achievable on the number alone plus context |
| U.S. Bank Account Number | regex, 8–17 digits | keyword **required** — the published entity has a single pattern (75) and no keyword-free tier | none — any qualifying digit string passes |
| ABA Routing Number | `Func_aba_routing`, nine digits, first two in 00–12 / 21–32 / 61–72 / 80 | keyword lifts 65 → 75 | **documented as `Checksum: No`** — see correction below |

**Correction recorded during Phase C:** this project's transfer notes asserted ABA
"has its own checksum" as a reason to prefer it for testing. The real-world ABA
check digit exists, but Microsoft's SIT documentation lists the entity as
`Checksum: No`. Whether `Func_aba_routing` validates the check digit is
undocumented either way; the safe test input is a real published institutional
routing number, which passes regardless. Assumption withdrawn, divergence row
recorded.

## Confidence level

Not a dial — a set of discrete pattern tiers inside one entity, each tier a
different evidence requirement. ABA: pattern alone = 65 (Low), pattern + keyword
= 75 (Medium). A policy condition set to Medium matches only items meeting the
75-tier evidence.

**Measured (SIT Test function, 2026-08-02):** the Test panel reports *every* tier
an item qualifies for, not the highest — one routing number returned both a Low
and a Medium result entry. Tiers are cumulative gates, and this was the first
surface in fourteen labs to show a classifier's internals rather than a verdict.

**Also measured, unresolved:** U.S. Bank Account Number returned a Low tier that
its published definition does not contain (single 75-level pattern, nothing
below). Either the cloud entity carries an unpublished tier or the Test panel
renders sub-threshold evidence differently than the entity XML implies. Recorded
as a docs-vs-product divergence, mechanism not asserted.

**Templates mix tiers.** U.S. Financial Data ships Credit Card at High and the
other two at Medium, visible only by opening each SIT row in the condition
editor. "The template's confidence" is not a single value; one template name is
three tuning decisions.

## Instance count

Per-SIT occurrence range on a condition: template default **1 to 9** for all
three SITs. Adjacent mechanism, not the same one: the Protection actions page has
a separate **threshold** toggle ("at least 10 instances of the same SIT")
defaulting to 10. The ranges tile rather than overlap — the SIT condition (1–9)
catches small leaks and compiles into the policy's **Low volume** rule; the
threshold (≥10) catches bulk exposure and compiles into the **High volume** rule.
One template, two rules — confirmed on the Review screen (`Low volume of content
detected …` / `High volume of content detected …`) and the reason the alert
setting says "if **any** of the DLP rules match."

## Cross-matching

One value can satisfy multiple SITs. Measured: the nine-digit routing number
matched U.S. Bank Account Number as well (nine digits sits inside 8–17, and a
qualifying keyword sat within 300 characters), so a two-number test document
produced **three** Medium-confidence instances. The same mechanism behind the
tenant's pre-policy false positives (Poland Passport / DEA / HKID on a tenant
containing neither): weakly-anchored patterns match whatever fits the shape.
Deliberately reproduced with controlled input in Lab 14 Phase C.

## Group operator (`Any of these` / `All of these`)

Boolean across the SITs inside a condition group. Template default: one group
(`Default`), `Any of these` — one instance of any one SIT triggers. Combined
with instance count 1–9, the effective template trigger is **a single instance
of any single SIT**. Broad by design; simulation mode is the counterweight.

## Locations

The seven-plus enforcement points a policy can scope to. Measured defaults
(2026-08-02): **all seven checked, all scoped "All"** — Exchange, SharePoint,
OneDrive, Teams, Devices, Instances (Defender for Cloud Apps), On-premises
repositories; Fabric/Power BI and Managed cloud apps greyed off. Notable:

- The wizard blanket-enables; the course guide says select deliberately. The
  default is the opposite of the guidance.
- Two default-enabled locations could not function in this tenant (On-prem:
  unmet prerequisites; Instances: no MDCA) — and the Policy mode step then named
  exactly those two as **unsupported by simulation mode**. Enabled, inert, and
  excluded from the mode the policy runs in.
- Label drift: the Locations step says "Instances"; the mode-step banner and the
  Review screen say "Microsoft Defender for Cloud Apps." Same location, two
  names, one wizard.
- Instances retires in early 2027 (file-policy retirement) — a location enabled
  by default and already scheduled for removal.
- Cloud-side locations (Exchange/SPO/OD/Teams) are evaluated by the service;
  **Devices** requires the endpoint DLP agent path — scope alone instruments
  nothing (see Device actions below).

## Admin units

Entra administrative units used to scope a policy to a directory subset. Default:
**Full directory**. The wizard warns that admin units aren't supported for all
locations — scoping to one **silently removes** unsupported locations (Fabric,
Copilot) from the next step, with no indication at the Locations step of what
disappeared. Related standing observation: Entra → Administrative units in this
tenant is expected empty (unverified; open item), which would pair with the
role-groups finding as a second empty delegation dimension.

## Roles vs role groups, and the precedence rule

Purview permissions are Entra-independent: **role groups** (containers) hold
**roles** (capabilities) and take members. Measured 2026-08-01 (CSV export, Lab
14 Phase A): **70 built-in role groups, zero users and zero security groups in
every one** — Organization Management holds 47 roles with 0 members; Compliance
Administrator 46 with 0. Everything Purview does in this tenant runs on Global
Administrator's implicit access: `POS-002`'s Purview dimension, quantified.

The precedence rule that makes fixing it non-trivial (guide 65 §5): **broad Entra
roles override scoped Purview assignments.** Populating a role group produces a
scoped identity only if that identity holds no overriding Entra role. And GA is
simultaneously insufficient elsewhere — it cannot preview delivered mail
(`POS-056`), and the policy-creation confirmation page showed **"Permission
required"** on communication compliance *to a Global Administrator*. The same
account is too much and not enough, measured three ways.

## Policy templates

Pre-assembled SIT bundles under regulatory names. Categories: Enhanced,
Financial, Medical and health, Privacy, Custom — **Enhanced is both a top-level
category and a per-template suffix** (GLBA Enhanced appears in two places).
Financial holds 13 templates, four U.S.-specific; "the U.S. financial template"
is a selection among overlapping regimes. The template description can drift
from its SIT list (U.S. Financial Data's description mentions debit card
numbers; its SIT list has none). A `Select location` dropdown filters the
template *list* by region and looks exactly like policy scope; it is not.

## Policy mode / simulation

Three modes at creation: simulation (preselected), on immediately, off.
Simulation evaluates and reports without enforcing. Sub-options, both default
unchecked: policy tips during simulation, and **auto-enable after fifteen days
unedited** — the one wizard default this lab was prepared to override (it would
have fired 2026-08-17, four days after the E5 trial's death) and did not need
to. The policy-list Mode column encodes the tips sub-option in its label:
`In simulation with notifications` vs `without`.

Simulation timing on trial tenants: course guide claims 30–60 minutes, up to 24
hours on trials. The creation confirmation page warns of **nothing** — the
surface most likely to precede a premature "it's broken" carries no propagation
warning. Measured (Lab 14 Phase D): simulation runs a **three-class scanning
model** — batch at-rest for SharePoint/OneDrive (including content predating
activation), real-time-only for Exchange/Teams/Devices (transit evaluation at
the send minute, no retroactive scan), and the simulation-unsupported locations
rendering as a permanent `In progress 0%`. The report indexes **8–12 minutes**
behind evaluation. **Restart the simulation is a destructive rebuild**: at-rest
results regenerate from current state, real-time history is wiped and cannot be
recreated (transit events do not replay) — behind a confirmation dialog that
names no consequences. The report is a historical record (deleted content's
matches persist until a restart), the Items grid and the overview counters
aggregate on different cadences, and match value details require the Data
Classification Content Viewer role even for Global Administrator.

## Protection actions and device actions

Template defaults measured 2026-08-02: policy tips ON, incident reports ON
(recipients: "you and your global admin" — the same person in this tenant),
alerts ON, **restrict/encrypt OFF**. Four of five ship enabled; the only
disabled one is the only enforcement. Incident reports cover **four** of the
seven in-scope locations (Exchange/SPO/OD/Teams only — Devices matches generate
no incident mail).

The access/override page's device section ships **entirely off** — master
checkbox unchecked, every sub-action `Audit only`, file activities "Don't
restrict." Devices in scope + device actions off = scope without
instrumentation. The block/encrypt action's three branches: block everyone,
block external only, or (email only) **encrypt via Purview Message Encryption**
— protected delivery rather than denial; Encrypt-only vs Do Not Forward decide
what the recipient can do after opening.

## Zero change management

Microsoft's term (Classifiers overview) for classification running before any
policy or configuration exists. Measured: a two-week-old tenant with no DLP
configuration showed 17 classified items and three exotic SIT matches on the
Home Featured-insights tile — a false-positive baseline that predates the first
policy, recorded as a `default`-kind posture entry in the same family as Lab
12's Built-in protection.

## Trainable classifiers, EDM, fingerprinting

The three non-pattern classification mechanisms, none exercised in Lab 14:
**trainable classifiers** (ML models trained on samples — the "Test" capability
used in Phase C also serves these), **exact data match** (hash-indexed lookup of
actual data values uploaded by the org), **document fingerprinting** (template
matching from a seed document). Recorded here for the boundary: everything Lab
14 measured is the *pattern* path.

## Pay-as-you-go DLP features

A billing banner on the Policies page requires linking an Azure subscription for
"some" DLP features. Measured: the metered path is **non-Microsoft 365 data
sources** (the Locations step names it); the classic M365 locations bill
nothing extra. The usage report (`DLP → Pay-as-you-go usage report`) is readable
without linking — 0 items over 3 months in this tenant — and exposes its schema
(`Date / Feature / Workload / Unit Of Measure / Consumed Units`) while empty.

## Timestamp rendering

The Purview DLP policy list renders **local time** (creation at 16:04 PDT wall
clock rendered `Aug 2, 2026 4:04 PM`). Third decoded surface: Defender portal
UTC-unlabelled, M365 admin center local, Purview local. Retroactively decodes
the four pre-seeded policies' `Jul 14, 2026 9:39 PM` provisioning stamp as
Pacific evening.
