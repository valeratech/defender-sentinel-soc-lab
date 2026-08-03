# Microsoft Sentinel & Defender XDR — SOC Build Lab

A ground-up build of a Microsoft security operations environment: onboarding, detection engineering, incident response, scoped access, and threat hunting across Microsoft Sentinel and Defender XDR — built live, instrumented, and documented one capability at a time.

This is a working lab, not a course notebook. Every capability here was built, broken, measured, and documented against the [SC-200 exam blueprint](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200). Detections are stored as deployable artifacts. Queries are stored as files, not screenshots. Every finding is dated, gated, and reproducible — and where the environment behaved differently from the vendor's documentation, the difference is the finding.

> Structured coursework alongside this build came from an instructor-led SC-200 course on Udemy — a solid path through the material. Everything in this repo is my own build, structure, measurement, and analysis.

---

## What this repository demonstrates

A synthetic attack travels the full pipeline, and every stage is proven with committed evidence:

```
Endpoint (onboarded sensor)
   → Defender for Endpoint (EDR alert)
   → Defender XDR (incident correlation)
   → Microsoft Sentinel (SecurityIncident, via connector)
```

The recurring theme, and the reason the posture register exists: **configured is not the same as effective.** A status reads healthy while the control does nothing — a connector reads *Available* while device risk never reaches compliance; a role reads *complete* while it enforces nothing; an ASR rule blocks live while the console reports the device *unprotected*. The lab is built to catch that gap and measure it, not to average it away.

---

## Repository Map

| Path | Contents |
|---|---|
| `labs/` | One folder per capability: objective, design decisions, build, validation, evidence, analysis |
| `docs/` | Concept references, navigation index, and the generated posture/coverage/open-items reports |
| `kql/` | Hunting and investigation queries, organized by data source — portable across Defender Advanced Hunting and Sentinel |
| `detections/` | Observed detections as tracked specs with ATT&CK frontmatter |
| `lessons/` | One file per course module — what was configured, established, corrected, and left untestable. Cross-references the labs and register rather than restating them |
| `scripts/` | Sanitization tooling and the generators for the coverage matrix, posture register, lab-coverage, open-items, and lessons reports |
| `posture.yml` | Source of truth for every security-relevant setting and its state |
| [`SANITIZATION.md`](SANITIZATION.md) | Redaction policy, placeholder convention, and public-constant allowlist |
| [`docs/navigation.md`](docs/navigation.md) | Portal path index for every setting configured or verified, with confirmed dates |
| [`docs/posture-register.md`](docs/posture-register.md) | Every security-relevant setting, its state, and whether it needs revisiting — generated |
| [`docs/attack-coverage.md`](docs/attack-coverage.md) | Observed ATT&CK coverage — generated from detection specs |
| [`docs/lab-coverage.md`](docs/lab-coverage.md) | Whether each posture entry is cited in the lab that owns it — generated |
| [`docs/open-items.md`](docs/open-items.md) | Tracked documentation debt — generated |
| [`docs/lessons-index.md`](docs/lessons-index.md) | What each course module taught, indexed by module rather than by lab — generated from [`lessons/`](lessons/) |

---

## Architecture

```
                    ┌─────────────────────────────────┐
                    │   Microsoft Defender Portal     │
                    │     security.microsoft.com      │
                    └─────────────────────────────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
        ┌────────▼─────────┐                ┌──────────▼──────────┐
        │  Defender XDR    │                │  Microsoft Sentinel │
        │  (detect/respond)│───incidents───▶│  (SIEM / data lake) │
        └────────┬─────────┘   ~2 min sync  └──────────┬──────────┘
                 │                                     │
        ┌────────▼─────────┐                ┌──────────▼──────────┐
        │ Endpoint sensor  │                │ Log Analytics       │
        │ (Defender for    │                │ Workspace           │
        │  Endpoint)       │                │ • alerts/incidents  │
        │ • telemetry      │                │   (free ingest)     │
        │ • ASR events     │                │ • raw Device* OFF   │
        │ • detections     │                │   (cost-safe)       │
        └──────────────────┘                └─────────────────────┘
```

Microsoft Sentinel and Microsoft Defender XDR are peer products sharing a console: separate licensing, separate billing, separate data stores. The operating experience converges in the Microsoft Defender portal while the products retain distinct responsibilities. Two architecture distinctions this lab documents explicitly:

- **Sensor vs connector** — a sensor *produces* telemetry (on-device, the source); a connector *moves* it (cloud-to-cloud, no software). Missing data from a device is a sensor problem; data in Defender but not Sentinel is a connector problem.
- **Defender Advanced Hunting vs Sentinel Logs** — same KQL, different stores. Defender's free raw lake (`Device*` tables, column `Timestamp`) versus the billed Log Analytics workspace (only forwarded data, column `TimeGenerated`). This is the whole ingestion cost model, and the reason `kql/` queries are portable across both.

### Terminology

Product names are used precisely throughout. "Defender" alone is avoided wherever the specific product matters.

| Term | Scope |
|---|---|
| **Microsoft Defender XDR** | Unified detection and incident experience |
| **Microsoft Defender for Endpoint** | Endpoint sensor, telemetry, alerts, response |
| **Microsoft Sentinel** | SIEM — data ingestion, analytics, SOAR |
| **Microsoft Defender portal** | Shared operating interface (`security.microsoft.com`) |

---

## Environment

| Component | State |
|---|---|
| Tenant | Single Entra tenant, lab-only, created 2026-07-14 |
| Licensing | M365 E5 trial + Defender for Endpoint Plan 2 / Vulnerability Management |
| Identity | Global Administrator + subscription Owner; scoped read-only analyst identity created (Unified RBAC) |
| Endpoints | Windows 11 VM onboarded to Defender (local script, sensor Active); Windows Server VM added for agent-based ingestion (inbound None + no public IP, Bastion access — a tighter posture than the Win11 box) |
| Device management | Entra device join configured; **Intune auto-enrolment never fires** — every precondition verified (`POS-022`). Forecloses all Intune-managed paths |
| Device groups | Rule-based group, Semi remediation, scoped to the analyst via an Entra group |
| ASR | Two rules enforcing via local PowerShell (the only available path here) |
| Sentinel | Workspace `law-soc-lab` (West US, PAYG); Sentinel enabled |
| Ingestion | Four paths, each a different tier of source: Defender XDR connector (same-platform, auto-connected, alerts/incidents only — raw `Device*` streaming OFF, cost-safe); Windows Security Events via AMA + a Common-tier DCR (`SecurityEvent`); Azure Activity via diagnostic setting (`AzureActivity`); Entra ID connector (`SigninLogs`/`AuditLogs`/risk) |

**The environment is ephemeral, and three clocks bound its life:**

| Clock | Behavior at expiry |
|---|---|
| **M365 Defender trial** | 2026-07-14 → **2026-08-13** — **the binding constraint**; ends the telemetry source |
| **Azure pay-as-you-go** | Never expires, never stops — bills continuously for whatever runs (no free-credit safety net; the offer was unavailable) |
| **Sentinel 31-day trial** | 2026-07-19 → 2026-08-19, 10 GB/day free on both Sentinel and Log Analytics |

Two consequences shape how this repository is written:

1. **Evidence is captured as it is produced.** When the trials lapse, every incident, timeline, and query result not already committed here is gone. The repository is designed to outlive the tenant that produced it.
2. **Queries, specs, and measured findings are the durable artifacts.** Portal state is not. Anything that cannot be redeployed or re-derived from this repository is treated as lost by default.

Teardown is a single action: everything lives in one resource group, so `az group delete` on it stops all Azure spend at once.

---

## Lab Index

Labs are numbered in build order. Where build order and the exam blueprint disagree, the build wins — the dependencies are real.

| # | Lab | Domain | Status |
|---|---|---|---|
| [00](labs/00-tenant-licensing-identity/) | Tenant, licensing, identity, and Unified RBAC | Environment | 🔨 Built, documenting |
| [01](labs/01-device-registration-intune-enrollment/) | Device registration and Intune enrolment | Environment | 🔨 Built, documenting |
| [02](labs/02-mde-intune-integration/) | Defender for Endpoint ↔ Intune integration | Environment | 🔨 Built, documenting |
| [03](labs/03-endpoint-onboarding/) | Endpoint onboarding, first detection, and investigation | Response | 🔨 Built, documenting |
| [04](labs/04-sentinel-workspace/) | Sentinel workspace and the endpoint-to-SIEM pipeline | Environment | 🔨 Built, documenting |
| [05](labs/05-device-groups-scoped-access/) | Device groups, automation levels, and scoped access | Environment | 🔨 Built, documenting |
| [06](labs/06-attack-surface-reduction/) | Attack surface reduction rules | Response | 🔨 Built, documenting |
| [07](labs/07-windows-security-events/) | Windows Security Events via AMA — agent-based ingestion | Ingestion | 🔨 Built, documenting |
| [08](labs/08-entra-azure-activity-connectors/) | Entra ID and Azure Activity connectors | Ingestion | 🔨 Built, documenting |
| [09](labs/09-attack-simulation-training/) | Attack simulation training — phishing campaign and what it does not prove | Response | 🔨 Built, documenting |
| [10](labs/10-alert-policies/) | Alert policies — the first detection authored here, and the built-in that already covered it | Detection | 🔨 Built, documenting |
| [11](labs/11-sentinel-analytics-rules/) | Sentinel analytics rules — twelve alerts from one event, and a template that never fired | Detection | 🔨 Built, documenting |
| [12](labs/12-mdo-threat-policies/) | Defender for Office 365 threat policies — a control that reads healthy on four surfaces and did nothing | Response | 🔨 Built, documenting |
| [13](labs/13-explorer-air-remediation/) | Explorer, AIR, and what the Action Center actually holds | Response | 🔨 Built, documenting |

Lab numbers are opaque, append-only handles — `04` is Sentinel because that folder existed as a stub before device groups were built, and renumbering corrupts cross-references. Course-module order and repo lab order diverge by design; the number is a filing handle, not a sequence claim.

---

## Observed ATT&CK Coverage

[`docs/attack-coverage.md`](docs/attack-coverage.md) — generated from detection frontmatter and CI-enforced to stay in sync.

**COVERED** means every rule mapped to that tactic has been *proven to fire on a known-true event*. A rule that has never fired is **unvalidated** and does not count as coverage — the distinction is the point.

| Tactic | Techniques | Detections | State |
|---|---|---|---|
| Execution (`TA0002`) | T1059.001 (PowerShell), T1047 (WMI) | `DET-001`, `DET-002` | **COVERED (2/2)** |
| Credential Access (`TA0006`) | T1110 (Brute Force) | `DET-004`, `DET-005` | **PARTIAL (1/2)** |
| Collection (`TA0009`) | T1114.003 (Email Forwarding Rule) | `DET-003` | **COVERED (1/1)** |

Four of five were observed firing live. **`DET-005` is the reason `TA0006` reads PARTIAL** — a Microsoft rule template, enabled and correctly configured, presented with the exact activity it names, which produced nothing. It is recorded as unvalidated rather than quietly counted.

*Table is a snapshot; [`docs/attack-coverage.md`](docs/attack-coverage.md) is authoritative and CI-enforced.*

```bash
python3 scripts/build-attack-matrix.py          # regenerate
python3 scripts/build-attack-matrix.py --check  # CI staleness check
```

---

## Security Posture

A lab accumulates weakenings. Each is defensible when made and invisible three weeks later.

[`docs/posture-register.md`](docs/posture-register.md) tracks every security-relevant setting: its state, whether it was chosen or inherited, the production answer where they differ, and whether it must be reconsidered before this project is called done. **58 entries** (57 verified) across four kinds — hardened, default, gap, and weakening. Generated from [`posture.yml`](posture.yml) and CI-enforced.

The register separates **verified** (observed in a portal view) from **asserted** (recorded on the operator's word), because blurring that is how a register becomes decoration.

**The register is not the writeup.** Every entry names the lab it belongs to, and [`docs/lab-coverage.md`](docs/lab-coverage.md) checks the lab cites it back — because a finding can pass every gate and still never reach the document it belongs to. `POS-022` did exactly that for three days while `labs/01` went on printing the vendor claim it disproves.

```bash
python3 scripts/build-posture-register.py --check   # posture register staleness
python3 scripts/check-lab-coverage.py --check       # every published lab cites its entries
python3 scripts/open-items.py --check               # documentation debt
```

---

## Sanitization

This repository is public and describes a live cloud environment. Every commit is audited before push against the policy in [`SANITIZATION.md`](SANITIZATION.md): no tenant identifiers, no live endpoint addresses, no unredacted query output, no offensive tooling artifacts, no committed images.

Enforcement is layered and fails closed — a `gitleaks` pre-commit hook with Azure/Sentinel rules, an auditing script that flags GUIDs, routable IPs, and personal terms for human decision, and CI that re-scans full history. Public constants that share the shape of the things the gate guards (Microsoft's own ASR rule GUIDs, the Azure WireServer IP) are cleared by documented exact-value allowlist, verified by a negative control that confirms real identifiers are still caught.

```bash
# macOS
brew install gitleaks
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## License

MIT — see [`LICENSE`](LICENSE).
