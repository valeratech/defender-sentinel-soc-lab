# Lab 18 — Sentinel Automation Rules: Two Doors, One Trigger, and a Duplicate Only the Audit Log Saw

| Field | Value |
|---|---|
| **Domain** | Response / SOC automation |
| **Objectives** | Build automation rules from both creation surfaces to observe their constraint models (module 79); verify serial execution, ordering, and non-retroactivity against a live trigger; confirm the decision-layer concepts of module 78 in the tenant |
| **Depends on** | Lab 11 (`DET-004` / `LAB-Bruteforce-Failed-Signins` — the rule these automations condition on), Lab 17 (`POS-074` analyst as assignee; the Activities-tab audit trail this lab reads at millisecond resolution) |
| **Status** | ✅ Built and measured — both rules fired on one trigger, retroactivity verified, one audit-only anomaly surfaced |
| **Built** | 2026-08-06 |

> Two automation rules, built through two different doors on purpose. The
> Automation page's builder arrives **empty and free**; the analytics-rule
> path arrives **pre-populated and locked** to a rename-safe `Current rule`
> token. Same feature, two binding models — the lab's whole point. Then seven
> failed sign-ins as `labuser` triggered both rules on one incident, in order,
> ~11 seconds after creation. The queue, the header, and the tag chip all read
> clean. The **millisecond-resolution audit log** showed something they
> couldn't: Rule B, whose only action is Assign owner, logging a second copy
> of Rule A's tag 3 ms after its own assignment. Correct outcome, phantom
> write, visible only where no one looks.

---

## 1. Objective

Modules 78 (concepts) and 79 (building a rule) describe Sentinel's decision
layer. This lab builds it and measures three things the guide asserts:

1. **The two creation surfaces differ.** The Automation page and the
   analytics-rule page both create automation rules — the lab's thesis is
   that they impose *different constraint models*, and the point is to
   observe both rather than take either on faith.
2. **Ordering and serial execution are real.** Two rules, Orders 1 and 2,
   should fire lowest-first on one incident.
3. **Nothing is retroactive.** The rules must touch only incidents created
   after they exist — verified by diffing the queue before and after.

Cost: none. Automation rules are free; no playbook (Logic Apps) was built,
so no consumption meter was opened. (Playbooks are G57.)

## 2. Predictions

| # | Prediction | Outcome |
|---|---|---|
| P79-1 | Automation page shows 0 rules at baseline | ✅ Confirmed — the tenant's first automation rules were built here |
| P79-2 | The rules act only on incidents created after them; 22 prior incidents untouched | ✅ Confirmed by byte-diff (`POS-076`) |
| P79-6 | The analytics-rule path creates a **Standard** rule with Order + Expiration | ✅ Confirmed — Standard, Order 2, Indefinite |
| P79-7 | That path's condition is pre-populated and **locked** to `Current rule` | ✅ Confirmed verbatim — operator and value both greyed (row 126) |
| P79-8 | (trigger default) | Resolved across four surfaces — see row 125; the pre-check's incident-created default belonged only to the analytics-rule wizard |
| new | Automation audit entries are performer-attributed to the rule, `Automated` | ✅ Confirmed — `Automation rule-<name>` / `Automated` (row 130) |

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Two entry points | Rule A from the Automation page (free condition), Rule B from the analytics-rule page (locked condition) | Build both the same way | The constraint-model contrast *is* the lab — one door asks, the other dictates |
| Distinct actions | A tags, B assigns | Both do the same thing | Different fields make serial execution legible in the result and the audit log |
| Rule B's assignee | `analyst` | `admin` | Keeps the boundary-test narrative coherent (the identity that triages Sentinel incidents, `POS-074`) |
| Trigger | DET-004 by name / `Current rule` | The guide's `Severity Equals Medium,High` | The guide's worked example would never fire here — every DET-004 incident is Low. Conditioning on rule name is the correct adaptation (and itself a divergence, §7) |
| One volley | 7 failed sign-ins, once | Repeat to be sure | DET-004 suppresses one hour after firing; a second volley inside the hour proves nothing |

## 4. Build

Portal-only (paths in `docs/navigation.md`). Both rules (`POS-075`) live at
**Defender → Microsoft Sentinel → Configuration → Automation → Automation rules → Standard rules.**

**Rule A (Automation page, free):** Create → Automation rule (arrives stamped
`Rule type: Standard`) → name `LAB-AutoTag-Bruteforce-Incidents` → trigger
*When incident is created* → condition `Analytic rule name / Contains /
LAB-Bruteforce-Failed-Signins` (chosen from a picker that enumerated three
analytic rules including Fusion) → action *Add tags* `auto-tagged-ruleA` →
Indefinite → **Order 1**.

**Rule B (analytics-rule page, locked):** Microsoft Sentinel → Configuration →
Analytics → `LAB-Bruteforce-Failed-Signins` → Edit → **Automated response** tab
→ Add new → name `LAB-AutoAssign-Bruteforce-Analyst` → trigger pre-selected
*When incident is created* → condition pre-populated and **locked** to
`Analytic rule name / Contains / Current rule` (greyed) → action *Assign owner*
`analyst` → Indefinite → **Order 2** → Review + create (re-saves the analytics
rule; expected on this path).

## 5. Validation

Trigger: 7 failed `labuser` sign-ins to `portal.azure.com`, 2026-08-06 11:00 PDT.

| Check | Method | Expected | Result |
|---|---|---|---|
| Both rules fire on one incident | Incident 23 row | tag AND owner set | ✅ `Tags: auto-tagged-ruleA`, `Assigned to: analyst` |
| Serial order | Activities audit log | A (Order 1) before B (Order 2) | ✅ A `18:12:25.140Z`, B `18:12:27.983Z` |
| Attribution | Audit `Performed by` | the rule, `Automated` | ✅ `Automation rule-<name>` / `Automated` |
| Automation latency | creation → last automation write | seconds | ✅ created `18:12:16Z`, done `18:12:27Z` (~11 s) |
| Non-retroactivity | diff queue before/after | 22 prior rows unchanged | ✅ byte-identical (bar incident 19's Lab-17 write, already in baseline) |

## 6. Failures & Fixes

No build failures. One course correction: **Rule A was first attempted as an
Enhanced rule** (the Automation page's Create path stamps Enhanced by default),
whose wizard offers only the `When alert is created` trigger — the plan needs
incident-created, which lives on the **Standard** side. Cancelled, switched to
the Standard-rules view, rebuilt. The detour *is* the finding (row 123): the
Enhanced/Standard split is two engines, unnamed in the guide.

## 7. Analysis

**The two doors impose different bindings, and both are defensible.** The
Automation page enumerates existing rules and asks you to pick — a rule you
name is a rule you chose, and if that rule is later renamed the condition
(matching on the old name) silently stops matching. The analytics-rule path
locks the condition to `Current rule`, a late-bound token that resolves at
runtime and survives renames — safer, but scoped to exactly one detection with
no choice offered. An operator who never sees both surfaces would assume the
one they used is how automation rules work. (Row 126.)

**"Limited conditions" is a generous label.** The tab calls Standard rules
limited, yet their condition picker offers ~40 entity properties — process
command line, registry key, mailbox sender, IoT device model — across incident,
alert, and entity tiers, with nested And/Or grouping. The picker also
enumerated **Fusion**, a detection the Analytics management list does not show
(row 126) — the third surface in this repo to disagree about how many
detections run here.

**Serial execution is exactly as documented, and the audit log is honest to a
fault.** Orders 1 then 2, ~2 seconds apart, lowest first — the guide's claim,
confirmed. But the same log records a write that, on the face of it, did not
happen: Rule B logging Rule A's tag 3 ms after its own assignment, under Rule
B's identity, though Rule B has no tag action (row 130, `POS-076`). The
benign, likely mechanism — a second-in-order rule re-commits the incident's
full managed-state post-image, which by then includes Rule A's tag — means the
audit log is faithfully recording a serial re-save that produces no visible
change. The tag is idempotent; the queue, header, and chip show one clean tag.
The duplicate exists only at millisecond resolution. It is the repository's
recurring shape turned on the automation engine itself: **the outcome is
correct, the record shows work that did not happen, and it is visible only at
a resolution nobody normally reads.**

**Non-retroactivity holds against our own instrument.** The 22 pre-existing
incidents diffed byte-identical after the rules fired. Microsoft's "nothing
retroactive" is true here, verified rather than trusted.

**Three surfaces still cannot agree on this rule's settings.** Suppression
reads `Stop for 1 hour` on the Azure pane and the wizard Review, blank on the
Lab 17 unified pane (row 128). Grouping/correlation collapses to `Disabled` on
one surface, splits into `Alert grouping: Disabled` + `Incident correlation:
Tenant default` on another (row 129). And the priority score for an identical
detection is 1 today where it was 3 in July and 72 (benign) for incident 1
(row 131) — an oddity now spanning two labs, mechanism unchased.

## 8. References

- [Automation rules in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules)
- [Create and use automation rules](https://learn.microsoft.com/en-us/azure/sentinel/create-manage-use-automation-rules)
- [Standard vs. enhanced automation rules](https://learn.microsoft.com/en-us/azure/sentinel/automation/automation-rules)
