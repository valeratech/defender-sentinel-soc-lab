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

Enrolment is the precondition for *management* — policy, compliance, configuration authority. It is **not** the precondition for endpoint telemetry. `Device*` tables come from MDE onboarding, which is a separate act on a separate path; Lab 03 takes that path deliberately, onboarding by local script without Intune, because this lab's enrolment never fired (`POS-022`).

The distinction is load-bearing. An unenrolled but onboarded device is watched and not governed — it emits everything and obeys nothing.

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

The configuration verified. The behaviour it was configured to produce did not. That gap is the finding of this lab.

| Check | Method | Expected | Result |
|---|---|---|---|
| Device join permitted | Entra → Devices → Device settings | Set to All | Set at configuration time; **not re-read** — `POS-006` remains asserted, not verified |
| Auto-enrollment scoped | Intune → Devices → Enrollment → Automatic Enrollment | MDM and MAM both All | **Not checked from the Intune side.** Verified instead from the Entra portal *and* independently from the device: `dsregcmd` reports an MDM discovery URL matching the portal value exactly (`POS-007`, `POS-008`, verified 2026-07-17). Two ends of the same setting agreeing is the stronger check; the Intune blade would be a third view of it |
| End-to-end | Join a Windows device with an org account | Device appears in Entra, then Intune inventory | ❌ **Entra yes. Intune never.** Device joined Entra 2026-07-14, still absent from Intune 2026-07-17. Not delayed, not blocked — never attempted (`POS-022`) |

Setting a value is not the same as confirming the platform accepted it, and confirming the platform accepted it is not the same as confirming it does anything. This lab is where the second gap opened.

**G2 states the sequence on first org sign-in:**

1. Device identity registers in Entra ID.
2. Intune registration triggers silently in the background.
3. Baselines, compliance policies, and Defender for Endpoint rules apply.

**Step 1 happened. Step 2 never did. Step 3 therefore cannot.**

The asynchronous-enrollment caveat — inventory lag of several minutes is normal, a manual sync forces it, absence immediately after join is not evidence of failure — is all true, and all of it is why this took three days to see. The lag defence expires. Three days is not lag. What is measured here is not a duration but an absence: no enrolment events (ID 71/72/75/76) anywhere in a log that spans back before the VM existed, and no scheduled tasks under `\Microsoft\Windows\EnterpriseMgmt`. Nothing to time, because nothing started.

Full evidence chain and the join-path hypothesis: `POS-022`, and §7 below.

## 5. Evidence

Evidence here is portal and on-device reads, recorded in the posture register on 2026-07-17 and reproduced sanitized; the endpoint is named by its register identifier, not its directory name.

| Claim | Surface | Observed | Date |
|---|---|---|---|
| Entra join completed | Entra ID → Devices | Device object present, joined | 2026-07-17 |
| MDM user scope | Intune → Enrollment → Automatic enrollment | All | 2026-07-17 |
| Device believes itself eligible | On-device diagnostics | `DeviceEligible : YES`, `AzureAdPrt : YES` | 2026-07-17 |
| Enrolment ever attempted | Event log, enrolment IDs 71/72/75/76 | **Absent**, over a span predating the VM | 2026-07-17 |
| Enrolment scheduled | `\Microsoft\Windows\EnterpriseMgmt` tasks | **None** | 2026-07-17 |
| VM security type | Azure → (VM) → JSON view → `securityProfile` | Standard — block absent; vTPM and Secure Boot absent (`POS-018`) | 2026-07-17 |
| RDP exposure | Azure → (VM) → Networking | TCP 3389 allow, source restricted to operator public IP, was Any (`POS-019`) | 2026-07-17 |
| NLA | VM registry `…\RDP-Tcp\UserAuthentication` + local `.rdp` | Disabled on both sides (`POS-020`) | 2026-07-17 |
| Endpoint sign-in identity | Entra ID → Users; Azure → (VM) → IAM | labuser, no roles, Virtual Machine User Login on the VM only (`POS-021`) | 2026-07-17 |
| GA login right on endpoint | Azure → (VM) → IAM → Role assignments | Global Administrator holds Virtual Machine Administrator Login, scope "This resource" (`POS-024`) | 2026-07-17 |
| Local admin account | Azure → (VM) → Run command | `labadmin`, enabled, renamed built-in Administrator (RID 500), password does not expire (`POS-025`) | 2026-07-17 |
| Auto-shutdown | Azure → (VM) → Operations → Auto-shutdown | Enabled, 23:00 Pacific, email notification (`POS-023`) | 2026-07-17 |

The full evidence chain for the enrolment absence, including counter-evidence considered, is `POS-022`.

## 6. Failures & Fixes

**Nothing errored. Something broke.** Those are different sentences, and the distance between them is this lab.

Configuration applied without error, no greyed-out settings, no retries. The portal accepted every value, reported every scope as All, and the device agreed with it. Auto-enrolment then never fired (`POS-022`), and no surface anywhere — Entra, Intune, or the device's own event log — said so. A failure that raises no error is not discovered; it is eventually noticed.

Recorded deliberately: the absence of friction here is itself informative. Both scopes were set to **All** on a single-user tenant, which is the path of least resistance. A production rollout scoped by security group is where this configuration actually gets difficult, and none of that difficulty was encountered or is claimed.

## 7. Analysis

**"Users may join devices = All" is the most consequential setting in this lab, and it is the convenient one.** Device identity is an authentication surface. This control decides who is permitted to mint one. Set to All, any user credential — including a compromised one — can register an attacker-controlled device into the directory, and that device identity then inherits whatever trust the environment extends to "managed" devices. The production answer is **Selected**, scoped to a security group, precisely because the population that legitimately needs to join devices is almost never "everyone."

**Auto-enrollment is where management authority attaches.** The MDM scope is what converts a registered device identity into a device the tenant can push policy to. Join and enrol are separate steps, and the gap between them is a device that exists in the directory but obeys nothing.

**That gap is not theoretical here. It is the state of this environment** (`POS-022`).

Every precondition for enrolment is satisfied and individually verified: MDM user scope All in the portal, the matching MDM discovery URL on the device, `DeviceEligible : YES`, `AzureAdPrt : YES`. Enrolment does not occur. It is not blocked and not deferred — it is never attempted, and because nothing is attempted, nothing fails, and no error exists to find.

**MDM scope is necessary and not sufficient.** Something has to *trigger* enrolment. The hypothesis — stated as a hypothesis, not a conclusion — is the join path: this device's Entra join was performed by the `AADLoginForWindows` extension at deployment, not by a user through OOBE or Settings. G2 describes user-driven join behaviour and is correct about it. G5 builds a VM that does not join that way and is correct about that. Neither guide is wrong. Followed together they produce a device that will never enrol, and the seam between them is invisible from either side.

**What is established is the observation, not the cause:** preconditions met, behaviour absent, silent. `POS-022` carries the full evidence chain and the counter-evidence considered.

**The reusable part is the diagnostic order.** The temptation was to reason from documentation about what *should* enrol. `DeviceEligible : YES` ended that in one line: the device says it qualifies, so ineligibility is not the explanation. Eligible-and-untriggered is not the same as ineligible. Ask the device.

**Left unenrolled deliberately.** Lab 03 onboards to Defender via local script and does not require Intune. The available force (`deviceenroller.exe /c /AutoEnrollMDM`) needs local administrator and enrols in the calling user's context, so running it as Global Admin would bind the device to the exact account `POS-021` exists to keep off the endpoint. The fix is worse than the gap; the gap is better documentation.

**The VM build itself is a ledger of trades, and the register prices each one** (`POS-018`–`POS-021`, `POS-023`–`POS-025`). Two entries harden: RDP scoped from Any down to one operator address, and a dedicated no-role sign-in identity for the endpoint. Two weaken by choice: Standard security type where Trusted Launch is the portal default — no vTPM, no Secure Boot, accepted silently from the deployment template — and NLA disabled on both sides, the price paid to reach Entra credentials over RDP. One weakens by accumulation: at the measured state (2026-07-17), the identity holding Global Administrator also held Virtual Machine Administrator Login, scope "This resource", on the same endpoint `POS-021` scopes the unprivileged identity to (`POS-024`). And one entry is load-bearing out of proportion to its size: the 23:00 auto-shutdown was the documented automatic control that deallocated the VM without operator intervention, limiting VM compute exposure — budgets themselves only report, and per `POS-016`'s 2026-08-01 correction deallocation ends compute spend while disks and public IPs bill until deleted (`POS-023`, `POS-015`). Individually each trade is defensible; the register is where they stop being individual.

## 8. References

- [SC-200 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200)
