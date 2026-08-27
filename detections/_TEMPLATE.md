---
# Machine-readable header — consumed by scripts/build-attack-matrix.py
id: DET-000
name: Short detection name
status: proposed          # proposed | built | tuning | active | retired
platform: sentinel        # sentinel | defender-xdr
rule_type: scheduled      # scheduled | scheduled-analytics | nrt | custom-detection | alert-policy | ti | ml | anomaly
severity: medium          # informational | low | medium | high
tactics:
  - TA0006               # MITRE ATT&CK tactic IDs
techniques:
  - T1110.003            # MITRE ATT&CK technique IDs
data_sources:
  - SecurityEvent
validated: false
---

# DET-000 — <Detection Name>

## 1. Hypothesis

The adversary behavior this is intended to surface, stated as a falsifiable claim about observable telemetry.

> If an adversary performs X, then Y will appear in Z within N minutes.

A detection without a hypothesis is a query with an alert attached.

## 2. Data Requirements

| Requirement | Value |
|---|---|
| Table(s) | |
| Connector / ingestion path | |
| Required fields | |
| Ingestion latency | |
| Retention tier | |

**Coverage precondition:** what must be true of the environment for this rule to be capable of firing at all. A rule over a table nothing writes to is not a detection.

## 3. Logic

```kusto
// Rule query
```

**Threshold rationale.** Why this number and not another. If the answer is "it was the default," say so — that is a finding, not a failure.

## 4. Validation

A rule that has never fired on a known-true event is unproven. State how it was made to fire deliberately.

| Step | Method | Expected | Result |
|---|---|---|---|
| Positive test | | Alert fires | |
| Negative test | | No alert | |
| Latency | | | |

**Simulation method:** reference the technique by name and cite a public source (Microsoft built-in simulation, Atomic Red Team test ID, EICAR). Never commit the payload — see `SANITIZATION.md` §6.

## 5. Tuning

| Iteration | Change | Reason | FP rate before → after |
|---|---|---|---|

**Known false positives.** Legitimate activity that trips this rule, and why it was accepted rather than suppressed.

**Known blind spots.** What this rule will not catch. Every detection has an evasion; naming it is the difference between coverage and the appearance of coverage.

## 6. Response

| Field | Value |
|---|---|
| Triage steps | |
| Automated action | |
| Playbook | |
| Escalation criteria | |

## 7. Analysis

What building this revealed about the platform, the data, or the technique.

## 8. References

- MITRE ATT&CK technique page
- Microsoft Learn
