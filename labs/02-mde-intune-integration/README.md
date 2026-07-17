# Lab 02 — Defender for Endpoint ↔ Intune Integration

| Field | Value |
|---|---|
| **Domain** | Manage a security operations environment |
| **Objectives** | Service-to-service connection, risk-based compliance, security configuration enforcement |
| **Depends on** | Lab 00, Lab 01 |
| **Status** | 🔨 Built, documentation in progress |

---

## 1. Objective

Establish the bidirectional bridge between Microsoft Defender for Endpoint and Microsoft Intune: Defender reports device risk to Intune so compliance can act on it, and Intune permits Defender to push endpoint security configuration to enrolled devices.

Without this connection the two products manage the same devices while knowing nothing about each other.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Intune connection in Defender | **On** | Off | Required for risk signal to reach Intune at all. Nothing downstream works without it. |
| Allow MDE to enforce Endpoint Security Configurations | **On** | Off (Intune-only policy authority) | Lets endpoint security policy flow from Defender to enrolled devices. Off would keep configuration authority solely in Intune. |
| Direction of setup | Defender first, then Intune | Intune first | The connection is enabled on the Defender side and accepted on the Intune side. Followed in that order; the reverse was not attempted, so whether it fails or merely reorders the work is **not established**. |

## 3. Build

**Resulting state:**

| Setting | Location | Value |
|---|---|---|
| Microsoft Intune connection | Defender → Settings → Endpoints → Advanced features | On |
| Connection status | Intune → Endpoint security → Microsoft Defender for Endpoint | **Available** |
| Allow MDE to enforce Endpoint Security Configurations | Intune → Endpoint security → Microsoft Defender for Endpoint | On |
| **Connect Windows devices 10.0.15063+ to MDE** | ↳ Compliance policy evaluation | **Off** |
| Connect Android / iOS devices to MDE | ↳ Compliance policy evaluation | Off |
| Enable App Sync / Certificate Sync (iOS) | ↳ Compliance policy evaluation | Off |
| Block unsupported OS versions | ↳ Compliance policy evaluation | Off |
| Connect Android / iOS to MDE (app protection) | ↳ App protection policy evaluation | Off |
| Grant MTD role permissions to MDE | ↳ Mobile Threat Defense role | Off |
| Days until partner is unresponsive | ↳ Shared settings | 7 (default) |

*(build narrative pending)*

## 4. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Connection status | Intune → Endpoint security → Microsoft Defender for Endpoint | Connection established | ✅ **Available** (observed 2026-07-16) |
| Service sync occurring | Last synchronized timestamp | Recent | ✅ `2026-07-16 17:34:32` |
| Propagation time | Elapsed time to reach Available | Vendor-documented 1–2 hours | ❌ **Not measured** — the status page was not revisited between configuration and observation, so no elapsed time exists. The last-sync timestamp reports periodic synchronization, not when the connection was established, and cannot be used to derive it. |
| Risk signal reaches compliance (Windows) | Compliance policy evaluation toggle | On | ❌ **Off** — see §7 |
| Risk signal flows end-to-end | Device risk reflected in Intune compliance | Risk level visible against a device | **Blocked** — requires both an enrolled device (Lab 03) and the toggle above |

The vendor documents 1–2 hours for service-to-service synchronization. **That range is an expectation, not this lab's result**, and no measurement is claimed.

## 5. Evidence

*(pending)*

## 6. Failures & Fixes

Nothing broke. Both toggles saved without error; nothing was greyed out.

Worth noting the dependency that did **not** bite: greyed-out or unsaveable settings in this blade generally trace back to E5 licensing not being fully assigned or provisioned (Lab 00), not to the integration itself. Lab 00's provisioning wait had already completed by this point, which is plausibly why this lab was uneventful — the ordering did the work.

## 7. Analysis

**A connection reading "Available" is not a working integration, and this lab is the proof.**

The service-to-service connection is established and synchronizing. Both toggles from the build are On. And device risk still does not reach Intune compliance for Windows, because the toggle that carries it — *Connect Windows devices version 10.0.15063 and above to Microsoft Defender for Endpoint*, under **Compliance policy evaluation** — is **Off**.

That toggle is what causes Intune compliance policies using the device threat level rule to include MDE risk signals (threat detections, risk scores) in their evaluation. Without it, the *Require the device to be at or under the machine risk score* rule has no signal to read.

**The two On toggles do not do what the connection is usually built for.** Worth separating precisely, because the names invite conflation:

| Toggle | What it actually governs |
|---|---|
| Microsoft Intune connection (Defender side) | Establishes the service-to-service channel. Necessary for everything, sufficient for nothing. |
| Allow MDE to enforce Endpoint Security Configurations | **Security Settings Management** — MDE enforcing security configuration on devices onboarded to MDE but *not enrolled in Intune*. Lab devices are expected to be Intune-enrolled, so this serves a scenario not being built here. |
| Connect Windows devices to MDE (compliance policy evaluation) | **The risk signal path.** Off. |

So the configuration currently has the toggle that is not load-bearing for this lab set On, and the one that is set Off.

**The dependency is invisible from either side.** Neither portal reports that the other matters. From Defender, the connection is on. From Intune, the connection is Available. Nothing anywhere says the risk signal is not flowing — there is no error, because nothing is broken. The integration is simply incomplete in a way that only surfaces when a compliance policy is written and silently never fires.

**This is the mechanism the SC-200 response domain is built on**, and the lesson generalizes past this toggle: *the absence of an error is not evidence that a control works.* The chain is Defender rates the device → Intune marks it non-compliant → Conditional Access denies access. Each link is a separate configuration in a separate blade, and a break in any one degrades silently.

> **Two links are currently missing, not one.** The compliance connector is Off (this lab), and no Conditional Access policies exist while Security Defaults are disabled (Lab 00, `POS-001`/`POS-003`). Until both are closed, the risk → compliance → access chain described above is architecture, not a control demonstrated in this environment.

Both are tracked in [`docs/posture-register.md`](../../docs/posture-register.md) as `POS-011` and `POS-003`.

## 8. References

- [SC-200 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200)
