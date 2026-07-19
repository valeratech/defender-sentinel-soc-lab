# Lab 05 — Device Groups, Automation, and Scoped Access

| Field | Value |
|---|---|
| **Domain** | Configure protections and detections |
| **Objectives** | Create a rule-based device group; set an automation/remediation level; delegate scoped access to a role identity; measure membership propagation |
| **Depends on** | Lab 00, Lab 03 (an onboarded device to scope) |
| **Status** | 🔨 Built, documentation in progress |
| **Built** | 2026-07-19 |

> Numbered 05 rather than 04 to avoid renumbering `labs/04-sentinel-workspace`.
> Course-module order (device groups precede Sentinel) and repo lab-number order
> diverge here by one; the lab number is an opaque handle, not a sequence claim —
> the same rule that keeps guide handles stable (see `configuration-inventory.md`).

---

## 1. Objective

Turn the flat single-device inventory into a *scoped* one. A device group is two
things at once: a **policy boundary** (its automation/remediation level governs
every member) and an **access boundary** (only assigned identities can manage its
members). This lab builds one group, binds the scoped analyst identity from
`POS-027` to it through an Entra security group, and measures how long membership
takes to actually take effect — because "the rule matches" and "the device is a
member" turn out to be different facts separated by a propagation window.

## 2. Design Decisions

The automation level was the real decision; everything else was mechanics. This
was assessed by an independent reviewer working from the public repo alone, whose
three calls are adopted here — noted because the reasoning, not the authority, is
what made them right.

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Remediation level | **Semi — approval required for non-temporary folders** | Full remediation; No automated response | This tenant's only endpoint is also its detection-test rig. Full auto-remediation could quarantine a test artifact before it is observed (Lab 03's whole method depends on watching the chain). No-automated-response was rejected because it *also* removes the device from automatic attack disruption — too blunt. Semi lets Defender auto-clean transient temp-folder junk while gating everything persistent behind approval: response capability retained, evidence preserved. |
| Membership rule | **Name starts with `WIN11-DEFENDER-`** (repo: `LAB-WIN11-`) | Full-hostname exact match | A prefix rule proves *dynamic* membership — a future second endpoint joins automatically. A full-hostname rule is a static assignment wearing a rule's clothing and demonstrates nothing about the mechanism. |
| Delegation | **Create an Entra security group (`SOC Device Admins`) even at n=1** | Skip delegation on a single-operator tenant | Exercising the full identity→group→device-group chain validates the whole RBAC model rather than leaving half of it theoretical. It also set up the lab's central test (below). |

**The central prediction, and its resolution.** The scoped analyst (`POS-027`) draws
its permission from **Unified RBAC** (`POS-026`), while device-group scoping is the
**legacy** MDE model, and the analyst account is **unlicensed**. Whether those
compose was genuinely uncertain — the prediction was that they might not. **They
did.** The analyst, via `SOC Device Admins` bound to the device group, resolves the
endpoint as a scoped member of `Lab Client Machines`. Recorded because it was a
real open question answered by observation, not assumption.

## 3. Build

Two portals, by design — the access model has a *who* half and a *what* half:

1. **Who** — `entra.microsoft.com` → Groups → New group → Security, `SOC Device
   Admins`, assigned membership, member: the `POS-027` analyst account.
2. **What** — `security.microsoft.com` → Settings → Endpoints → Permissions →
   Device groups → Add device group:
   - Name `Lab Client Machines`; remediation **Semi — non-temporary folders**
   - Rule: **Name starts with `WIN11-DEFENDER-`**
   - User access: **`SOC Device Admins`**
   - Submit → **Apply changes** (this is T0)

The wizard ships a four-condition AND rule (Name, Domain, Tag, OS); only Name was
given a value. The three empty rows cannot be removed — delete icons appear only
on conditions *added beyond* the defaults. They are ignored in evaluation (Preview
confirmed a match with them empty), so this is a cosmetic-but-alarming default, not
a functional blocker. Noted so a future reader does not chase it.

## 4. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Rule matches | Group → Preview devices | Device previews | ✅ 1 device, **immediately** at T0 |
| Membership commits | Devices column on group row | 0 → 1 | ✅ committed by T1 |
| Policy boundary applied | Remediation level in effect | Semi, not the default Full | ✅ once a member; **Full while Ungrouped** (see §7) |
| Access boundary (inclusive) | Analyst → Assets → Devices | Device visible, tagged with group | ✅ analyst sees it as a member of `Lab Client Machines` |
| Access boundary (exclusive) | Analyst denied a device *outside* the group | Denied | ⛔ **un-runnable** — one device, in the group; nothing to be denied from. `revisit` when a second device exists. |
| Group as inventory dimension | Assets → Devices → Filter | `Group` filter lists the group | ✅ |

### The propagation latency — T0/T1

| Latency | Vendor number | Measured |
|---|---|---|
| Apply → membership committed | 30–60 min (guide §7) | **≤ 28 min** (T0 06:11 → observed committed 06:39) |

At or under the vendor floor, consistent with every latency this tenant has
produced. The measured number is the finding; the vendor range is comparison only.

## 5. Evidence

Sanitised per `SANITIZATION.md`; device name normalised to `LAB-WIN11-01`, all
`*Id` GUIDs masked.

At T0 the group row read `Devices: 0` while `Ungrouped devices (default)` read `1`.
At T1 (~28 min later) this flipped: `Lab Client Machines: 1`, `Ungrouped: 0`. The
analyst inventory export at T1 carried `Group: Lab Client Machines`, and the
device header rendered the group as a tag alongside `Active` / `Medium`.

## 6. Failures & Fixes

No configuration failure. One **operator** failure, kept because it is instructive:
a redacted CSV's `Last device update` timestamp (a device *check-in* time) was
misread as the group *configuration* time, turning ~28 minutes of normal
propagation into an apparent ~30-hour outage. Three failure theories (case
sensitivity, empty-AND conditions, a stuck recalc à la `POS-028`) were built on
that phantom before the real elapsed time was confirmed and the membership simply
committed on schedule. The fix was to *stop theorising and confirm the clock*.
Both traps are recorded in `configuration-inventory.md`.

## 7. Analysis

**"Rule matches" and "device is a member" are different facts, separated by the
propagation window — and the gap has teeth.** Preview matched the device instantly
at T0; committed membership lagged ~28 minutes. For that entire window the device
was **not** in `Lab Client Machines` — it sat in `Ungrouped devices (default)`,
which runs **Full remediation**. So during propagation the endpoint was governed by
the *opposite* of the automation level deliberately chosen for it: a detection or
ASR test run in that window would have faced Full auto-remediation while the
operator believed Semi was in force. This is the `POS-011` family — configuration
present, effect absent — but the sharpest instance yet, because the fallback does
not do *nothing*, it does the specific thing the design chose to avoid. **Do not
test against a device until its group membership has committed**, not merely until
the rule previews as matching.

**Scoped access is provable only by exclusion, and a single-device tenant cannot
exercise it.** The inclusive half (analyst sees the in-group device) confirms the
grant. The exclusive half (analyst *denied* an out-of-group device) is what
actually proves the boundary *bounds* — and it is structurally un-runnable with one
device, because there is nothing outside the group to be denied. `POS-011`'s lesson
turned on access control: a scope that has never excluded anything has not been
shown to scope. Held as `revisit` pending a second, deliberately out-of-group
device.

**Unified RBAC and legacy device-group delegation compose.** The open question of
the lab — whether an unlicensed, Unified-RBAC identity gains legacy device-group
scoped access — resolved yes, by observation. Worth recording as the answer to a
real uncertainty, not a foregone conclusion.

## 8. References

- `POS-030` (this device group), `POS-027` (analyst), `POS-026` (Unified RBAC),
  `POS-011` (the configuration-vs-effect family)
- Microsoft Learn — Create and manage device groups
- Microsoft Learn — Automation levels in automated investigation and remediation
