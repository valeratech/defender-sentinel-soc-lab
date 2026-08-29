# Lab 00 — Tenant, Licensing, and Identity Foundation

| Field | Value |
|---|---|
| **Domain** | Manage a security operations environment |
| **Objectives** | Tenant provisioning, licensing activation, identity baseline |
| **Depends on** | — |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | *(pending — see Environment Clock below)* |

> Sections marked `*(pending)*` are work completed but not yet written up.

---

## 0. Provenance

This environment was built by following three setup guides. They are cited throughout
the repository as **G1**, **G2**, **G3** so that instructions taken from them are not
presented as native knowledge, and so that a reader can tell which decisions were
inherited and which were made here.

| Ref | Guide | Covers |
|---|---|---|
| **G1** | Microsoft 365 & Azure Sandbox — regional limitations and Teams activation | Tenant creation, E5 trial acquisition, licence assignment, Azure subscription |
| **G2** | Device Registration and Automatic Intune Enrollment Configuration Guide | Entra device join settings, MDM/MAM scope |
| **G3** | Integrating Microsoft Defender for Endpoint with Intune | Defender↔Intune connection, both directions |

Their content is not reproduced. `docs/configuration-inventory.md` records, per setting,
what the guides instructed and what this environment actually does — including three
points where those disagree. The most consequential:

- **G1 describes an Azure safety net this subscription does not have** (see §3). The
  free-account credit model it assumes — services paused at exhaustion, card never
  auto-charged — does not apply to pay-as-you-go. Budget and deallocation discipline
  exist here because that assumption failed, not because a guide called for them.
- **G3 states the MDE↔Intune connection lets Intune enforce compliance on Defender's
  device risk, then gives two steps that do not enable it.** The toggle that does is
  never mentioned. See Lab 02 and `POS-011`.

Recording provenance is not bookkeeping. A guide that is right about the procedure and
wrong about the outcome is the most expensive kind of documentation to follow, because
nothing errors.

Establish the tenant and licensing baseline every later capability depends on: an Entra ID directory with the E5 security workloads provisioned and assigned, and an Azure subscription capable of hosting a Log Analytics workspace and lab compute.

Nothing in this lab detects anything. It exists because Defender for Endpoint, Defender for Office 365, and Sentinel all gate on licensing and provisioning state, and every failure in the labs that follow traces back to something in this one.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| M365 licensing | Office 365 E5 trial, then **Microsoft 365 E5** trial added on top | M365 E3, Business Premium | Office 365 E5 alone does not carry the endpoint security workloads. Microsoft 365 E5 is the SKU that provisions Defender for Endpoint P2 and Defender for Identity. E3/Business Premium cover most of the exam surface but not the full Defender stack. |
| License assignment | Assigned to the administrator account explicitly | Group-based licensing | A tenant-level subscription is not active on any user until assigned. Group-based licensing is the production answer; a single-user lab does not justify the indirection. |
| Azure subscription | **Pay-as-you-go, funded out of pocket**, under the existing M365 E5 tenant identity | Azure free account ($200 / 30 days) | The free account offer was not available to this account at signup. The subscription still lives in the same Entra directory, which is what lets Sentinel, Entra logs, and the Defender stack share one identity plane; a separate tenant would have imposed a multi-tenant architecture on a single-analyst lab for no benefit. |
| Admin identity model | **Single Global Administrator**, used across Azure, Defender, Intune, and Microsoft 365 admin portals | Separate role-scoped admin accounts; PIM eligible assignments | Lab convenience — one identity, no elevation friction. **This is a deliberate lab-only weakening.** In production this is the anti-pattern the SC-200 environment domain exists to prevent: a single standing Global Admin is one credential away from total tenant compromise, and it makes every action in the audit log indistinguishable from every other. Named here rather than left implicit. |
| Security Defaults | **Disabled** | Leave enabled (the tenant default); disable and replace with Conditional Access | Disabled to remove MFA prompts and legacy-auth blocking from the lab path. **This was an active change, not an inherited state** — tenants created on or after 22 Oct 2019 ship with Security Defaults enabled. Nothing replaced them: no Conditional Access policies exist. The tenant is therefore running with **no baseline identity protection at all**, which is a weaker posture than either supported option. Deliberate, lab-only, and the precondition for the Conditional Access work that Security Defaults would otherwise block. |
| Elevate access to all subscriptions | **Off** | On | Left at default. Governs whether the Global Administrator can assume User Access Administrator across every subscription and management group in the tenant. Recorded as a default rather than a decision. |

## 3. Environment Clock

Both trials expire, and they fail in opposite directions. This is a design constraint on the repository, not a footnote.

| Component | Term | Behavior at expiry | Risk |
|---|---|---|---|
| Microsoft 365 E5 trial | 30 days | **Auto-converts to a paid subscription** unless cancelled in Admin center → Billing → Your products | Billing |
| Azure pay-as-you-go | None — continuous | **Does not expire and does not stop.** Bills for consumption until resources are deallocated or deleted | **Uncapped cost** |

**The Azure side has no safety net.** The free account's protective behavior — services disabled when credit runs out, no charge without an explicit upgrade — does not apply here. A pay-as-you-go subscription bills continuously for whatever is running. The spending limit feature exists only on credit-based offers, so it is unavailable on this subscription.

Three lab-specific cost drivers follow directly from later labs, and each is a consumption meter:

| Driver | Introduced by | Behavior |
|---|---|---|
| Log Analytics ingestion + Sentinel surcharge | Lab 04, 06 | Per-GB, continuous. Enabling Sentinel applies its surcharge to the whole workspace. |
| Lab VM compute | Lab 03 | Bills while allocated, whether or not anyone is using it |
| Internet-exposed endpoint farming brute-force traffic | Lab 03, 08 | The telemetry is the point — but volume is billable, and the internet sets the rate |

The third is the one that surprises people: an intentionally weakened box left running is a bill that scales with how interesting the internet finds it.

**Controls to put in place before Lab 03:** an Azure Budget with alert thresholds, VM auto-shutdown schedules, and a deliberate retention/tier decision in Lab 07 rather than a default one.

**Consequence for this repository:** telemetry, incidents, and timelines not committed here before resources are torn down cannot be recovered. Evidence is captured as it is produced.

| Tracked | Value |
|---|---|
| M365 E5 trial term | **2026-07-14 to 2026-09-14** (25 licenses; extended once on 2026-08-06 from 2026-08-13 — `POS-077`) |
| O365 E5 trial term | **2026-07-14 to 2026-08-13** — deliberately not extended (`POS-017`) |
| M365 recurring billing | *(pending — see `POS-017`)* |
| Azure budget, resource-group scope | Configured — `$15/month`, actual alerts at 50/80/100% |
| Azure budget, subscription scope | *(pending — see `POS-015`)* |
| Azure budget, forecasted alert | *(pending — see `POS-015`)* |

**The tenant expires 2026-09-14.** That is the project's clock, not merely a billing date. Evidence must be committed before it, because a lapsed trial takes every incident, timeline and query result with it. Nothing here is reconstructable afterwards. The extension was one-time and is now spent, so this date is a floor rather than a target.

### 3.1 Licensing audit — 2026-08-06

The extension was taken deliberately, to remove schedule pressure from the remaining
build rather than to avoid cost: the conversion was already configured at one licence,
month-to-month, cancellable at any renewal. Auditing the billing surfaces *before*
clicking — because the write is irreversible and overwrites the fields being read —
produced more findings than the extension itself.

**Prediction P77-1, recorded before the click:** one 30-day extension, once only, no
payment method demanded, no duration choice, allocation unchanged at 25, resulting
expiry 2026-09-12. **Five of six held. The arithmetic did not** — the dialog states
*30 days* and the Expiration date moved **32**, from 2026-08-13 to 2026-09-14. The
anchor is not identified and is not guessed at here (`POS-077`, divergence row 132).

Three findings came out of the pre-click audit, none of them the thing being looked for:

- **Four dates for two trials, across five surfaces** — 8/12, 8/13, 8/14, 8/15, all
  inside one admin center, all describing the same pair of expiries. Three of them name
  genuinely different events (expiry, conversion, invoice availability) that a reader
  collapses into "when does the trial end". **This repository collapsed two of them for
  three weeks** — `POS-017` recorded the Recurring billing field's *transition day* as
  the O365 expiry date, and O365 does not expire on the 14th. Corrected. The 8/12 banner
  is still unexplained (`POS-078`, row 134).
- **No portal surface lists all four SKUs in this tenant.** Active users shows three,
  Your products shows a different three, Billing → Licences shows two. Power Automate
  Free appears only where licences are assigned to people; Entra ID Free only where
  products are billed (`POS-079`, row 135).
- **Two SKUs the register had never recorded** after eighteen labs — Power Automate Free,
  assigned to `admin`, and Entra ID Free. Both inherited rather than chosen, which is the
  case the `default` kind exists for (`POS-080`).

**Post-extension, one field did not propagate.** Expiration and the conversion line both
moved 32 days in lockstep, preserving their +1 offset — so they are a derived pair, not
independent values. **Next invoice available did not move at all**, and still reads
8/15/2026: thirty days before the subscription it invoices for begins, stale with no
indication that it is stale, on the same panel as the two that updated correctly
(`POS-077`, row 133).

**Identity, verified rather than asserted.** The same audit closed `POS-002`, the
register's last unverified entry, standing open since 2026-07-16. Users → Active users →
`admin` → Account renders **Roles: Global Administrator**; `labuser` renders *No
administrator access*; `analyst` is unlicensed with no directory role. Three active
member accounts, one standing GA, no PIM and no eligible alternative — corroborated the
same day on a second surface (Entra ID → Users → All users, *3 users found*, all Member,
no guests). The entry was **narrowed** in the course of closing it: the original state
line claimed "across all portals", which a role read can neither confirm nor deny, so
the phrase is dropped rather than left as an unfalsifiable flourish. `revisit` stays
true — verifying a weakening does not remediate it.

**What the 2026-08-13 O365 lapse now costs: nothing that matters.** `admin` is the only
holder of an Office 365 E5 licence (1/25) and also holds M365 E5; `labuser` holds M365 E5
alone. Every Office 365 workload this lab exercises — Exchange, OneDrive, SharePoint,
MDO Plan 2, Purview DLP, Insider Risk — is carried by M365 E5 independently. Not
extending O365 E5 therefore leaves `POS-017`'s open acquisition-dependency question
testable in isolation, on a date when nothing else happens.

## 4. Build

*(pending — configuration state recorded below; narrative to follow)*

**Resulting state:**

| Setting | Value |
|---|---|
| Tenant type | Single Entra ID tenant |
| Tenant region | United States |
| Security Defaults | Disabled |
| Conditional Access policies | None |
| Elevate access to all subscriptions | Off (default) |
| M365 subscription | Microsoft 365 E5 (trial) |
| E5 license assigned to admin | Yes |
| Azure subscription | Pay-as-you-go, same directory |
| Sentinel workspace | Not yet created (Lab 03) |

## 5. Validation

*(pending)*

| Check | Method | Expected | Result |
|---|---|---|---|
| Security Defaults state | Entra ID → Overview → Properties | Known, either way | **Disabled** — confirmed by inspection |
| E5 provisioned and assigned | Admin center → Billing → Licenses | E5 assigned to admin user | |
| Azure subscription active in tenant | Azure portal → Subscriptions | Free Trial subscription, expected directory | |
| Defender Endpoints workload present | Defender portal → Settings → Endpoints | Endpoints section renders | |
| Credit balance | Cost Management + Billing → Azure credits | ~$200 remaining | |

## 6. Failures & Fixes

Nothing broke. Two behaviors are worth recording because both look like faults and neither is one.

**Defender portal Endpoints section absent after E5 assignment.**

| | |
|---|---|
| Observed | The **Endpoints** section did not appear in the Defender portal immediately after the E5 license was assigned. |
| Measured delay | **Over 1 hour.** |
| Resolution | Backend provisioning completed. A **sign-out and sign-in** was also performed before the section rendered. |
| Misdiagnosis risk | Reads as a licensing or permissions fault. It is neither — it is asynchronous provisioning. |

Because both the wait and the re-authentication happened, the two are not isolated from each other: it is not established which one made the section appear, or whether both were required. See §7.

**Azure free credit unavailable.**

Not a failure of the build. The free account offer was not available to this account, so the subscription was created pay-as-you-go. Recorded because it removes the cost safety net every lab guide assumes is present (§3).

**Security Defaults** — confirmed **disabled**. Entra ID → Overview → Properties reports *"Your organization is not protected by security defaults."* Undocumented at build time and recovered by inspection rather than from notes, which is itself the finding: an identity-posture change that nobody wrote down is indistinguishable from an accident six weeks later.

## 7. Analysis

**Licensing is a capability gate, not an administrative formality.** The SKU decides which tables exist, which blades render, and which detections are possible at all. A rule written over a table the license never provisioned is not a detection — it is a query that will never fire. This is why the licensing lab precedes every detection lab rather than being a footnote to them.

**Tenant-level purchase and per-user assignment are separate operations.** A subscription added to the tenant is inert until assigned. The gap between those two states produces "the portal is broken" reports that are, on inspection, unassigned licenses.

**Portal state is not configuration state.** For some period after a licensing change, the portal renders something that is neither the old configuration nor the new one. An analyst who treats the UI as authoritative during that window will misdiagnose. The operational rule: after a licensing or provisioning change, absence of a feature is not evidence of misconfiguration until the propagation window has passed.

**Candidate explanation for the sign-out/sign-in (§6) — *not established*.** Entitlement changes are reflected in claims carried by the access token, and an existing session continues presenting the token it already holds. Under that model, backend provisioning could complete while the signed-in session still renders the pre-license view until re-authentication issues a fresh token. This is consistent with what was observed but was **not isolated** — the wait and the re-auth were not tested independently, so it remains a hypothesis rather than a finding.

> **Open validation.** Testing this properly needs a second licensing change with the two variables separated: wait without re-authenticating and observe, then re-authenticate and observe. Worth doing opportunistically at the next license assignment rather than manufacturing one.

**The identity posture is the weakest thing in this environment, and it is weak by accumulation rather than by any single choice.** Three defensible-in-isolation decisions compound: a single standing Global Administrator (§2), Security Defaults disabled with nothing replacing them (§2), and no Conditional Access. Individually each is a reasonable lab shortcut. Together they describe a tenant where one credential, unprotected by MFA, holds total authority over the directory and every subscription in it — and where the audit trail cannot distinguish that identity's actions from any other's, because there is no other.

This is worth stating plainly rather than burying, for two reasons. It is the exact posture the SC-200 environment domain exists to interrogate, so naming it demonstrates the understanding the certification is testing. And a reader who spots it unaided will conclude it was not noticed. The mitigating control here is not technical: it is that the tenant holds no real data and is disposable.

## 8. References

- [Avoid charges with your Azure free account](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/avoid-charges-free-account)
- [SC-200 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200)
