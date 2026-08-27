# Lab NN — <Capability>

| Field | Value |
|---|---|
| **Domain** | Environment / Response / Hunting |
| **Objectives** | Blueprint objectives exercised |
| **Depends on** | Lab NN |
| **Status** | Planned / Building / Complete |
| **Built** | YYYY-MM-DD |

---

> **This is the default structure, not a required one.** `docs/documentation-standard.md`
> §5 states the requirements semantically: a finished lab must discharge each of them
> under whatever heading it uses. Several published families depart from the numbering
> below — prediction-led labs register Predictions at §2, phase-structured labs organise
> the middle sections by measurement phase, and the compact form ends on *What this lab
> does not establish*. See §5.0 of the standard. Depart deliberately, not accidentally.

## 1. Objective

What capability this adds to the SOC, in one paragraph. Stated as a capability the environment gains, not as a task performed.

## 2. Design Decisions

Choices made before building, and the alternatives rejected. This section is the point of the lab — the clicking is not.

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|

## 3. Build

Steps taken, as commands and configuration rather than prose where possible. Portal-only steps noted as such, since portal paths change and CLI does not.

```bash
# az / PowerShell / KQL
```

## 4. Validation

How the build was proven to work rather than assumed to work. A capability that has not emitted a verifiable signal is not built.

| Check | Method | Expected | Result |
|---|---|---|---|

## 5. Evidence

Sanitized output per `SANITIZATION.md`. Tables preferred over screenshots.

## 6. Failures & Fixes

What broke, the error, the cause, the fix. Kept deliberately — the failure path is the part that transfers to production.

## 7. Analysis

What this reveals about how the platform actually works. Where the documentation and the behavior diverge. What an analyst inherits from this design.

## 8. References

- Microsoft Learn links

---

## Optional sections

Used by published labs where the work warrants them. Not required, and not to be
added to reach a section count.

**Predictions** — registered *before* portal contact, each with a falsifier, and each
closed, withdrawn, or recorded as unmeasured by the end of the lab. Where a lab has
this section, the standard requires the dispositions.

**Teardown / cost** — what was decommissioned, what was left running, and what the
lab cost. Required in substance wherever a metered resource was opened.

**What this lab does not establish** — the boundary of the measurement. Preferred over
letting a reader infer conclusions the lab never reached.
