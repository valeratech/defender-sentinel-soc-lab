---
title: Using policies to remediate threats with Email, Teams, SharePoint & OneDrive
date: 2026-08-01
artifacts:
  labs: ["12"]
  posture: [POS-047, POS-048, POS-049, POS-050, POS-051, POS-052, POS-053, POS-054, POS-055]
  divergences: [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]
  kql: []
corrections:
  - "A latency finding stated three times and withdrawn — three measurement methods applied to one message were described as three independent confirmations."
  - "Predicted that Configuration analyzer needs custom policies to report anything; it returned 18 recommendations against the defaults. The guide makes the same error."
  - "Explorer reporting no action on a message was read as a possible logging behaviour; re-running the identical export returned the value. The surface was behind, not selective."
---

# Defender for Office 365 Threat Policies

> A guide that configures nothing, run as a lab anyway. It produced the clearest
> instance this repository has of a control that is correctly configured,
> reported healthy by every surface, and demonstrably inert.

## What was configured

One policy: `SA-Sales-DynamicDelivery`, Dynamic Delivery, scoped to a
mail-enabled security group containing `labuser` (`POS-054`). One group created
to scope it. Four messages sent from an external Gmail address across two runs.

Everything else in this walkthrough was **reading**. Twelve portal surfaces and one
PowerShell block, recorded as `POS-047` through `POS-053` and `POS-055` before
anything changed — on the argument that a tenant's inherited mail security
baseline is security-relevant state whether or not anyone chose it.

Zero cost. EOP and MDO under the E5 trial; no Azure resource touched.

## What was established

**Built-in protection is enabled and does nothing** (`POS-048`, row 47). Four
surfaces agree it is healthy — `State: Enabled`, `Action: Block`, every scoping
field empty so it applies to everyone, a real hydration timestamp, portal
`Status: On`. Two messages to the one mailbox it covers carry **no**
`X-MS-Exchange-AtpMessageProperties`; the two to the scoped mailbox both do. n=2
each side, two hours apart.

There is no surface disagreement here. That is what makes it the strongest
version of this repository's thesis so far — prior instances were two consoles
contradicting each other, and this is four consoles agreeing and being wrong.
The portal's own note says Built-in protection is enabled only for **paid**
tenants and this one is on trial; whether that is the cause is **not
established**, and the prediction that it was genuinely active was falsified.

**A wizard that states a constraint and does not enforce it** (`POS-054`, row 43).
*"Enable redirect only supports the Monitor action"* appears in text directly
above the checkbox that accepts it. The address field activates, format
validation fires but applicability validation does not, the Review page renders
both settings with **green status dots**, and the backend persists
`Redirect: True` alongside `Action: DynamicDelivery`. Confirmed inert — no
redirect copy of either message arrived.

**The wizard's default action is Off, not Block** (row 44). Accept the defaults
and you ship a named, scoped policy with `Status: On` that scans nothing.

**Precedence exists nowhere in the objects** (row 48). Creating the custom policy
did not write an exclusion into Built-in protection — every exception field stayed
empty, `WhenChanged` unmoved. Both rules claim every recipient in their own
schema, both read `Priority: 0` on incomparable scales, and the ordering is
resolved at mail-flow time. An audit by export would conclude both apply.

**One policy, three cmdlets, three answers.** `Get-SafeAttachmentRule` returns
nothing while protection is enabled and universal; `Get-SafeAttachmentPolicy`
returns the policy; `Get-ATPBuiltInProtectionRule` returns the rule. The cmdlet an
operator reaches for first is the one that reports silence — and it does so in
exactly the state every tenant occupies before its first custom policy.

**Absence and disabled render identically** in this portal. Three configurations
show a toggle or row reading "off" for an object that does not exist — the two
presets, DKIM (`POS-052`), and Safe Attachments rules pre-lab. Enabling them
creates the object rather than changing a value.

**The Defender portal renders UTC unlabelled; the M365 admin center renders
local** (row 49). Proven on single objects carrying both forms rather than
inferred across two. This **withdraws** the ten-occurrence generalisation that
Defender renders local — the accurate statement is that Defender is inconsistent
with itself, since the Tenant Allow/Block page stamps `(UTC-07:00)` while the
policy panes label nothing.

**The default anti-phishing policy is on and inert for its headline capability**
(`POS-049`). Impersonation protection off with zero senders and zero domains,
mailbox intelligence **on** but its impersonation consumer off, and all three
impersonation actions set to take no action. The EOP half — DMARC handling, spoof
intelligence — is live. So: EOP spoof protection works out of the box; MDO
impersonation protection ships inert.

**Detection without prevention** (`POS-053`). `AutoForwardingMode: Automatic`.
Lab 10 authored a detective control for attacker-created forwarding and a
built-in fired alongside it — two detections for one behaviour — while the
preventive setting governing whether that forwarding delivers had never been
examined.

**Five surfaces, and the most-reached-for one is the least informative** (row 50).
Headers distinguish the policy path reliably and immediately; Explorer does too
**once it has indexed**; message trace cannot at all, because transport succeeded
identically. No surface names the policy.

**Propagation is the tenant's most repeated lesson, and this is its fourth
instance** (row 50). Exchange hydration took 12 days (`POS-036`), group
membership took ~20 minutes to reach transport, threat policy application took
under an hour against a claimed 24, and Explorer indexing took somewhere under an
hour to some unrecorded later point. This one is the worst of the four because it
produces a **wrong answer rather than a missing one** — an empty `Additional
actions` is indistinguishable from no action having been taken, and nothing marks
the row as incomplete. In this ecosystem, a surface reporting nothing may simply
not have finished writing. The message header, stamped at delivery, is the only
immediately authoritative one.

**Two deprecated cmdlets that still ship and fail silently** (row 51).
`Get-MessageTrace` and `Get-MessageTraceDetail` carry a deprecation date eleven
months past, still load, still bind parameters, and fail only at execution —
returning empty rather than erroring, so downstream commands run cleanly against
nothing.

**One field, two strings** (row 52). Explorer's UI renders
`Dynamic delivery-Succeeded` and its CSV export renders
`Dynamic delivery-Success`. Its timestamps differ too — UI local, export UTC —
but **both are labelled**, which makes Explorer the counterexample to row 49
rather than another instance of it.

**Where surfaces agreed.** The anti-phish detail pane matches the schema exactly
on every field checked, and Configuration analyzer's four anti-spam
recommendations match `Get-HostedContentFilterPolicy` including the one action it
does *not* flag. Recorded deliberately: a register full of disagreements implies
disagreement is the norm.

## What was corrected

**A latency finding stated three times and withdrawn.** Run 1 measured 3.2 s on
the scanned path against 23.8 s on the control, and this shipped as *"Safe
Attachments makes delivery ~7× faster, confirmed across three independent
measurement methods."* Run 2's control came in at **4.36 s**. The run-1 control
was an outlier.

The error was the word *independent*. The header latency, the Explorer
timestamps, and the message-trace event gap are three **methods** measuring **one
message**. Three readings of one sample is not three samples.

What survives is narrower and holds: Safe Attachments adds no measurable delay —
3.25 s and 3.45 s across two runs — which still contradicts the guide's
"detonation adds latency" and Learn's "typically within 15 minutes."

**Verification catches misreadings; replication catches over-generalisation.**
Re-reading `CTRL-01` would never have found this. Only a second sample could.

**Configuration analyzer analyses defaults, not just custom policies** (row 45).
Predicted it would have nothing to report in a tenant with no custom policies; it
returned 18 recommendations against the shipped defaults. The guide states the
same thing wrongly.

## What could not be tested

**Foreclosed by the tenant.** Whether Built-in protection activates on a paid
Defender for Office 365 tenant. Testing it means converting the subscription.

**Foreclosed by the audit window.** What triggered the 2026-07-26 hydration event
that instantiated the default anti-phishing policy twelve days after the tenant
was created. Unified audit logging was enabled ~90 minutes after it. The
correlation with Lab 09's simulation launch ten minutes earlier is **inference**.

**Closed during write-up.** Explorer's `--` on the second Sales message was
indexing lag, not conditional logging — the identical export re-run later
returned the value on both. Recorded as a correction rather than an open item,
and the lag window is bounded only to the hour because export times were never
noted. That is the method error: two runs of the same query, no timestamp on
either.

**Untested, not foreclosed.** `ActionOnError` is blank in the schema and the
wizard never offered it. `Dynamic delivery-Success` implies a failure branch
exists; it is undocumented and unobserved here. And `RecipientLimitExternalPerHour`
reads `0`, which in EOP conventionally means "service default" rather than zero —
deliberately not transcribed until confirmed.

**n=1 remains n=1.** `CTRL-01`'s 23.8 s is unexplained. Two samples established
that it is not characteristic; nothing established what it was.

## Cost

Zero. Both VMs stayed deallocated. Every capability exercised in this walkthrough is
covered by the E5 trial, which ends 2026-09-14 (extended once on 2026-08-06 from
2026-08-13).
