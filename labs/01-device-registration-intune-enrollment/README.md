# Lab 01 — Device Registration and Intune Auto-Enrollment

| Field | Value |
|---|---|
| **Domain** | Manage a security operations environment |
| **Objectives** | Entra ID device settings, MDM scope, automatic enrollment |
| **Depends on** | Lab 00 |
| **Status** | 🔨 Built, documentation in progress |

---

## 1. Objective

Make the directory capable of accepting Windows device joins and enrolling them into Intune automatically, so that a device signing in with an organizational account becomes a managed, policy-bearing, telemetry-emitting asset without per-device work.

This is the precondition for endpoint telemetry. No enrollment, no `Device*` tables, no endpoint detections.

## 2. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Who may join devices | **All** users | **Selected** — scoped to security groups | Lab convenience. In production this is scoped: unrestricted device join means any compromised user credential can register an attacker-controlled device into the directory and inherit whatever that device identity is trusted for. Recorded here as a deliberate lab-only weakening. |
| MDM user scope | **All** | Some / None | Every joined device should enroll. "Some" exists to stage MDM rollouts by group; irrelevant at one user. |
| WIP / MAM user scope | **All** | Some / None | Set alongside MDM scope. Surfaces as *WIP user scope* or *MAM user scope* depending on portal version. |
| Configuration path | **Entra portal** — Mobility (MDM and WIP) → Microsoft Intune | Intune admin center — Devices → Enrollment → Automatic Enrollment | Both portals write the same configuration; either is sufficient. Configured via the Entra path only. **The Intune-side view was not used to independently verify the result** — see §4. |

## 3. Build

**Resulting state:**

| Setting | Location | Value |
|---|---|---|
| Users may join devices to Microsoft Entra ID | Entra ID → Devices → Device settings | All |
| MDM user scope | Entra ID → Mobility (MDM and WIP) → Microsoft Intune | All |
| WIP / MAM user scope | Entra ID → Mobility (MDM and WIP) → Microsoft Intune | All |

*(build narrative pending)*

## 4. Validation

Configuration was set but **not independently verified**, and the end-to-end test belongs to Lab 03.

| Check | Method | Expected | Result |
|---|---|---|---|
| Device join permitted | Entra → Devices → Device settings | Set to All | Set at configuration time; not re-read |
| Auto-enrollment scoped | Intune → Devices → Enrollment → Automatic Enrollment | MDM and MAM both All | **Not checked.** Configured via the Entra path; the Intune view would confirm the same setting from the other side |
| End-to-end | Join a clean Windows device with an org account | Device appears in Entra, then Intune inventory | **Deferred to Lab 03** — this is the real proof, and no device existed yet |

Setting a value is not the same as confirming the platform accepted it. The cheap independent check is to read the same configuration back from the Intune admin center, which renders the identical scopes; disagreement between the two views would be the finding.

**Expected enrollment sequence on first org sign-in (unverified until Lab 03):**

**Expected enrollment sequence on first org sign-in:**

1. Device identity registers in Entra ID.
2. Intune registration triggers silently in the background.
3. Baselines, compliance policies, and Defender for Endpoint rules apply.

Enrollment is asynchronous — inventory lag of several minutes is documented as normal, and a manual sync from Windows settings forces it. Absence from inventory immediately after join is not evidence of failure. **Record the actual observed lag in Lab 03**; the measured number is worth more than the documented expectation.

## 5. Evidence

*(pending — sanitized per SANITIZATION.md; device names are attributable, see §1)*

## 6. Failures & Fixes

Nothing broke. Configuration applied without error, no greyed-out settings, no retries.

Recorded deliberately: the absence of friction here is itself informative. Both scopes were set to **All** on a single-user tenant, which is the path of least resistance. A production rollout scoped by security group is where this configuration actually gets difficult, and none of that difficulty was encountered or is claimed.

## 7. Analysis

**"Users may join devices = All" is the most consequential setting in this lab, and it is the convenient one.** Device identity is an authentication surface. This control decides who is permitted to mint one. Set to All, any user credential — including a compromised one — can register an attacker-controlled device into the directory, and that device identity then inherits whatever trust the environment extends to "managed" devices. The production answer is **Selected**, scoped to a security group, precisely because the population that legitimately needs to join devices is almost never "everyone."

**Auto-enrollment is where management authority attaches.** The MDM scope is what converts a registered device identity into a device the tenant can push policy to. Join and enrol are separate steps, and the gap between them is a device that exists in the directory but obeys nothing.

*(further analysis pending)*

## 8. References

- [SC-200 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200)
