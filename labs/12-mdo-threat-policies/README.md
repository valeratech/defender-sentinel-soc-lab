# Lab 12 — Defender for Office 365 Threat Policies

| Field | Value |
|---|---|
| **Domain** | Response |
| **Objectives** | Read the inherited mail-security baseline; build a scoped Safe Attachments policy; prove by observation which policy acts on a delivered message |
| **Depends on** | Lab 00 (E5 licensing), Lab 10 (`POS-043` — the alert policy whose preventive counterpart is `POS-053`) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-08-01 |

> The first lab in this repository where **a correctly configured control was
> proven to do nothing**. Built-in protection reads `State: Enabled`, applies to
> every recipient with no exclusions, has a real tenant-owned object behind it —
> and left no trace on either message it covered.

---

## 1. Objective

The source guide performs no configuration. It is a tour of the Threat policies
page, and under this repository's triage rule that makes it a concept note.

It was run as a lab anyway, on the argument that **a tenant's inherited mail
security baseline is security-relevant state whether or not anyone chose it**.
Twelve surfaces were read before anything was built.

The build that followed had one job the reading could not do: establish, by
observation rather than by precedence documentation, **which policy actually acts
on a message**. Two mailboxes, one scoped to a custom policy and one not, same
sender, same file, one minute apart.

Zero cost throughout. EOP and MDO under the E5 trial; no Azure resource touched.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Scope object | **Mail-enabled security group** | Microsoft 365 group | An M365 group provisions a SharePoint site and group mailbox as side effects. `POS-055` has Safe Attachments for SharePoint/OneDrive/Teams **on**, so that would add a second protected content surface immediately before measuring the first |
| Scope membership | **`labuser` only** | Both mailboxes; `All Company` | `All Company` auto-enrols every user and is the plausible-looking wrong answer. It would place the control inside the test scope and silently collapse the A/B |
| Control mailbox | **`admin`, deliberately unscoped** | No control | Without it, "the custom policy applied" is unfalsifiable. The control is what makes `POS-048` a finding rather than an assumption |
| Action | **Dynamic Delivery** | Block; Monitor | Block is what Built-in protection already does, so it would make the two paths indistinguishable. Dynamic Delivery is behaviourally distinct and is what Assignment 8 specifies |
| Creation surface | **Portal wizard** | PowerShell `New-SafeAttachmentPolicy` | Prediction 4 was a claim *about the wizard*. PowerShell accepts `Redirect` alongside any action, so a UI-only constraint can only be tested in the UI |
| Test payload | **Benign PDF, then a novel benign PDF** | EICAR; a real sample | No malicious code, even defanged. The measurement is the delivery mechanism, not a verdict — and a detonation verdict was never required to establish which policy acted |
| Redirect | **Left enabled deliberately** | Unchecked for a clean policy | The wizard stated the constraint and accepted the value anyway. Submitting it converts a UI observation into a schema finding. Cost: the shipped policy carries an inert setting, recorded in `POS-054` |

**Predictions were recorded before each phase and are scored in §4.** A negative
result only counts if it was written down in advance; noticing afterwards that
nothing happened is indistinguishable from not looking.

## 3. Build

### Phase A — observation, no configuration

Twelve portal surfaces and one PowerShell block, read before anything changed.
State recorded in `POS-047` through `POS-053` and `POS-055`.

```powershell
Get-EOPProtectionPolicyRule; Get-ATPProtectionPolicyRule   # both return nothing
Get-ATPBuiltInProtectionRule                                # State: Enabled, Priority: 0
Get-SafeAttachmentPolicy | ft Name,Action,Enable,IsBuiltInProtection,IsDefault
Get-SafeAttachmentRule                                      # returns nothing
Get-AntiPhishPolicy | fl Name,Enabled,EnableMailboxIntelligence,EnableTargetedUserProtection,PhishThresholdLevel
Get-HostedContentFilterPolicy | fl BulkThreshold,SpamAction,HighConfidencePhishAction,QuarantineRetentionPeriod
Get-HostedOutboundSpamFilterPolicy | fl AutoForwardingMode
Get-MalwareFilterPolicy | fl ZapEnabled,EnableFileFilter,QuarantineTag
Get-DkimSigningConfig; Get-ArcConfig                        # both return nothing
```

### Phase B — the scope object

`admin.microsoft.com` → Teams & groups → Active teams & groups → **Security
groups** tab → **Add a mail-enabled security group**.

**Not** the default tab. Active teams and groups opens on *Teams & Microsoft 365
groups*, whose primary action creates the wrong object type. See `docs/navigation.md`.

```powershell
Get-DistributionGroup -Identity "sales-lab" |
  fl Name,GroupType,RecipientTypeDetails,WhenCreated,WhenCreatedUTC
# MailUniversalSecurityGroup · Universal, SecurityEnabled
# WhenCreated 2026-08-01 12:17:32 · WhenCreatedUTC 19:17:32
```

Twenty minutes' propagation before Phase C. Group membership must reach the
transport layer before policy scoping resolves against it, and a policy scoped to
an unreplicated group applies to nobody — a failure indistinguishable from the
precedence prediction being wrong.

### Phase C — the policy

`Defender > Email & collaboration > Policies & rules > Threat policies > Safe
Attachments > + Create` — four steps: Name, Users and domains, Settings, Review.

Scoped to `sales-lab` under **Groups**, Users and Domains left empty. Action
**Dynamic Delivery**. Quarantine policy left at the pre-filled
`AdminOnlyAccessPolicy`. Configuration in `POS-054`.

**The wizard's default action is Off**, not Block. See §7.

### Phase D — trigger

Four messages from one external Gmail sender, two runs two hours apart.

| Run | Sales → `labuser` | Control → `admin` | File |
|---|---|---|---|
| 1 | `Lab12-DD-01` 21:01 UTC | `Lab12-CTRL-01` 21:02 UTC | 57 KB PDF, common |
| 2 | `Lab12-DD-02` 22:58 UTC | `Lab12-CTRL-02` 22:59 UTC | 55 KB PDF, **novel by construction** |

The run-2 file was generated with a GUID nonce and its SHA256 verified identical
on the generating host and independently before sending, so a known-good hash
cache hit was impossible and detonation had to run.

## 4. Validation

| # | Prediction (recorded in advance) | Result |
|---|---|---|
| 1 | Preset rule cmdlets return nothing, not `State: Disabled` | ✅ **CONFIRMED** |
| 2 | `Get-SafeAttachmentPolicy` returns nothing | ❌ **FALSIFIED** — returns Built-in protection |
| 3 | Custom policy applies to Sales only; Built-in to control only | ✅ **CONFIRMED, n=2** |
| 4 | Redirect unavailable when Dynamic Delivery is selected | ❌ **FALSIFIED** — stated, not enforced |
| 5 | No surface reveals which policy applied | ❌ **FALSIFIED** — headers reveal the action |
| 6 | Scan time exceeds one minute | ❌ **FALSIFIED** — 3.2 s and 3.5 s |
| 7 | `Get-SafeAttachmentRule` returns the new rule; Built-in stays invisible | ✅ **CONFIRMED** |
| 8 | Built-in protection's exception fields stay empty after the custom policy exists | ✅ **CONFIRMED** |
| 9 | The stored `Redirect: True` never fires | ✅ **CONFIRMED, n=2** |
| 10 | Novel file delivers with no placeholder | ✅ **CONFIRMED** |
| — | Built-in protection is genuinely active on a trial tenant | ❌ **FALSIFIED** |

Five confirmed, five falsified. **Every falsification produced a better finding
than its confirmation would have.**

One result required a second look rather than a second prediction: Explorer
reported `--` for `Lab12-DD-02` at first export and `Dynamic delivery-Success`
later, from the identical query. See §7.

## 5. Evidence

### The discriminator

`X-MS-Exchange-AtpMessageProperties` — present on both Sales messages, absent
from both controls.

| Message | Policy path | ATP marker | Explorer `Additional actions` | Latency |
|---|---|---|---|---|
| `Lab12-DD-01` | `SA-Sales-DynamicDelivery` | **`SA`** | `Dynamic delivery-Success` | 3.249 s |
| `Lab12-DD-02` | `SA-Sales-DynamicDelivery` | **`SA`** | `Dynamic delivery-Success` ⏱ | 3.454 s |
| `Lab12-CTRL-01` | Built-in protection | absent | `--` | 23.834 s |
| `Lab12-CTRL-02` | Built-in protection | absent | `--` | 4.360 s |

All four: `Delivery action: Delivered`, `Threats` empty, `Detection technologies`
empty, `SFV:NSPM`, `SCL:1`, `compauth=pass reason=100`, SPF/DKIM/DMARC all pass.

Gmail signs its outbound mail correctly, so authentication was clean throughout
and nothing in these results is attributable to spoof handling.

### Five surfaces asked "what happened to this message"

| Surface | Distinguishes the policy path? |
|---|---|
| `Get-MessageTraceV2` `Status` | ❌ `Delivered` for all four |
| `Get-MessageTraceDetailV2` events | ❌ `Receive` and `Deliver` only; no `Action` values |
| Message header `AtpMessageProperties` | ✅ reliably, all four |
| Explorer `Additional actions` | ✅ once propagated — see §7 |
| Delivery latency | ❌ see §6 |

**No surface names the policy.** Three reveal the action. In a tenant with two
Dynamic Delivery policies, Explorer's field would not disambiguate them.

### One policy, three cmdlets, three answers

| Cmdlet | Returns |
|---|---|
| `Get-SafeAttachmentRule` | nothing |
| `Get-SafeAttachmentPolicy` | `Built-In Protection Policy` — Block, Enable True, `IsDefault: False` |
| `Get-ATPBuiltInProtectionRule` | the rule, `State: Enabled`, all scoping fields empty |

Identical for Safe Links. The cmdlet an operator reaches for first — the `Rule`
form, matching every other EOP policy type — reports silence while protection is
enabled and unscoped.

## 6. Failures & Fixes

### A finding stated three times and withdrawn

Run 1 measured 3.2 s on the Safe Attachments path and 23.8 s on the control. This
was written up as **"Safe Attachments processing makes delivery ~7× faster,
confirmed across three independent measurement methods."**

It is withdrawn. `Lab12-CTRL-02` came in at **4.36 s**. The control path is
normally fast; run 1's control was a single outlier.

The error was in the word *independent*. The header `EndToEndLatency`, the
Explorer timestamps, and the message-trace `Receive`→`Deliver` gap are three
**methods** — and they measured **one message**. Three readings of one sample is
not three samples, and describing them as independent made a single observation
sound corroborated.

**What survives:** Safe Attachments adds no measurable delay — 3.25 s and 3.45 s,
tight across two runs. That still contradicts the guide's "detonation adds
latency" and Learn's "typically within 15 minutes."

**What does not:** any claim that scanning made delivery faster.

No amount of re-reading `CTRL-01` would have caught this. **Verification catches
misreadings; replication catches over-generalisation. They are not substitutes.**

### Two deprecated cmdlets that still ship

`Get-MessageTrace` and `Get-MessageTraceDetail` both fail with a notice dated
**2025-09-01** — eleven months prior. Both still load in the current EXO V3
module, bind parameters, and accept pipeline input. They fail only at execution.

The hazard is the failure mode. `$t` came back empty and two subsequent commands
ran cleanly against nothing, producing no output and no error. **A monitoring
script built on these reports zero messages rather than reporting a failure.**

Same shape as the policy findings, one layer down: present, callable, inert.

### A test that could not produce the behaviour under test

Run 1 used a Google Drawings PDF export — about as common a file as exists.
When it delivered with no placeholder, "the policy did not apply" and "the policy
applied and worked correctly" were indistinguishable.

Run 2's novel file resolved it, and three of its four outcomes came from **having
a second run** rather than from the file being novel.

## 7. Analysis

### Configured is not effective — the cleanest instance yet

`POS-048` is the entry this repository exists for.

Prior instances involved a control that was misconfigured, or a status label that
was ambiguous, or two surfaces that disagreed. This one has **no disagreement at
all**. Four surfaces report Built-in protection healthy — the portal, the policy
cmdlet, the rule cmdlet, and its hydration timestamp. All four are consistent.
And the two messages it covers show no sign it touched them.

The portal note beside the toggle offers a candidate explanation: enabled only
for **paid** Defender for Office 365 tenants. This tenant is on trial. That is
**not established** — the prediction recorded in advance was that the policy was
genuinely active, and it was falsified. Testing it would require converting the
subscription.

An analyst inheriting this tenant would find every configuration surface saying
attachments are protected, and would be wrong.

### The wizard states a rule and does not enforce it

`SA-Sales-DynamicDelivery` carries `Redirect: True` and a populated
`RedirectAddress` alongside `Action: DynamicDelivery`.

The Settings step displays, in text, directly above the checkbox: *"Enable
redirect only supports the Monitor action."* Then:

1. The checkbox accepts the tick
2. The address field activates
3. Validation fires on email **format** — not on applicability
4. Selecting Dynamic Delivery afterwards triggers no re-check
5. The **Review page renders both settings with green status dots**, and the
   warning text does not travel with them
6. Submission succeeds and the backend persists it

Six checkpoints, one written rule, zero enforcement. Confirmed inert by
observation: no redirect copy of either Sales message reached the target mailbox.

A green status indicator is an affirmative claim. Here it is made about a setting
the product had already explained would not apply.

### The default is Off

The Safe Attachments creation wizard pre-selects **"Off — attachments will not be
scanned by Safe Attachments."** The guide's action table lists Block as the
default.

Click through this wizard accepting defaults and you ship a policy with a name, a
scope, an entry in the policy list, and `Status: On` — that scans nothing.

### Precedence exists nowhere in the objects

After the custom policy was created, Built-in protection's `ExceptIfSentTo`,
`ExceptIfSentToMemberOf` and `ExceptIfRecipientDomainIs` remained **empty**, and
its `WhenChanged` was unmoved. The service does not materialise an exclusion.

So both rules claim every recipient in their own schema, and the ordering that
resolves the overlap is evaluated at mail-flow time. **Read the two rules cold
from an export and you would conclude both apply.** Both also read `Priority: 0`,
on two scales that are not comparable, neither labelled.

### Absence and disabled render identically

Three separate configurations in this tenant render as a portal row or toggle
reading "off" for an object that **does not exist**:

- Standard and Strict presets — `Get-EOPProtectionPolicyRule` returns nothing
- DKIM — `Get-DkimSigningConfig` returns nothing, status `NoDKIMKeys`
- Safe Attachments rules before this lab — `Get-SafeAttachmentRule` returns nothing

Enabling any of them does not change a setting. It creates one.

### Explorer is eventually consistent, and says nothing about it

At first export, `Lab12-DD-02` carried the `SA` header and Explorer recorded
`--` — same policy, same recipient, same configuration as `Lab12-DD-01`, which
Explorer had already recorded correctly.

**Re-exporting the identical query later returned `Dynamic delivery-Success` on
both.** The field had not been withheld conditionally; it had not been written
yet.

The lag is bounded but not measured. The first export was taken within roughly an
hour of the send and showed `--`; a later export showed the value. Export times
were not recorded, which is the method error — **two identical queries and no
timestamps on either, so the window is known only to the hour**.

The direction of the error is what matters operationally. Explorer showed
**absence where there was action**, on the surface an analyst is most likely to
trust, with no indication the row was incomplete. Nothing in the UI, the export,
or the column header distinguishes *"no action was taken"* from *"the action has
not been indexed yet"*.

This is the fourth propagation delay recorded in this tenant and the first that
produces a **wrong answer** rather than a missing one:

| Surface | Delay | What it looked like |
|---|---|---|
| Exchange hydration (`POS-036`) | 12 days | default policy object absent |
| Group membership → transport | ~20 min | policy scoped to nobody |
| Threat policy creation | up to 24 h claimed; ~0 observed | n/a — applied in under an hour |
| **Explorer indexing** | **< ~1 h to some later point** | **`--`, indistinguishable from no action** |

The general rule this tenant keeps teaching: **in this ecosystem a surface
reporting nothing may not have finished writing.** An empty field is a claim about
the index, not about the event — and only the message header, which is stamped at
delivery, is immediately authoritative.

### Label and export disagree on the same field

The Explorer UI renders `Dynamic delivery-Succeeded`; the CSV export of the same
row renders `Dynamic delivery-Success`. One field, one value, two strings — which
matters for anyone matching on it programmatically.

Explorer does get one thing right that the policy panes do not: **both its
renderings are labelled.** The UI column reads `Timestamp (UTC -07:00)` and shows
local; the export column reads `Email date (UTC)` and shows UTC. Two zones from
one tool, and neither is ambiguous. Against row 49, that is the counterexample.

### Detection without prevention

`POS-053` records `AutoForwardingMode: Automatic`. Lab 10 built a detective
control for attacker-created mail forwarding, and a built-in policy fired on the
same activity — two detections for one behaviour. The preventive setting
governing whether that forwarding delivers had never been examined.

Nothing is misconfigured. The gap was in the documentation: an alert was built,
committed and cross-referenced for a behaviour whose enabling setting was never
recorded.

### What a normal user would never see

Neither Sales message displayed a Dynamic Delivery placeholder, including the
one with a globally novel file. Detonation completes ahead of the delivery
decision, so there is nothing to hold back.

The guide frames Dynamic Delivery around a salesperson waiting on a signed
contract. That scenario requires latency this tenant does not produce. The
configuration is correct, active, and its user-visible purpose is invisible in
normal operation.

## 8. References

- [Preset security policies in EOP and Microsoft Defender for Office 365](https://learn.microsoft.com/en-us/defender-office-365/preset-security-policies)
- [Set up Safe Attachments policies](https://learn.microsoft.com/en-us/defender-office-365/safe-attachments-policies-configure)
- [Order and precedence of email protection](https://learn.microsoft.com/en-us/defender-office-365/how-policies-and-protections-are-combined)
- [Configuration analyzer for protection policies](https://learn.microsoft.com/en-us/defender-office-365/configuration-analyzer-for-security-policies)
- [`Get-ATPBuiltInProtectionRule`](https://learn.microsoft.com/en-us/powershell/module/exchange/get-atpbuiltinprotectionrule)
- [`Get-MessageTraceV2`](https://learn.microsoft.com/en-us/powershell/module/exchange/get-messagetracev2)
