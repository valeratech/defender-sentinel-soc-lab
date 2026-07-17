# Microsoft Sentinel & Defender XDR — SOC Build Lab

A ground-up build of a Microsoft security operations environment: ingestion, detection engineering, incident response, and threat hunting across Microsoft Sentinel and Defender XDR.

This is a working lab, not a course notebook. Every capability here was built, broken, instrumented, and documented against the [SC-200 exam blueprint](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200) (April 2026 revision). Detections are stored as deployable artifacts. Queries are stored as files, not screenshots. Findings are reproducible.

> Structured coursework alongside this build came from John Christopher's SC-200 course on Udemy — a solid instructor-led path through the material and worth the time if you're starting from zero. Everything in this repo is my own build, structure, and analysis.

---

## Repository Map

| Path | Contents |
|---|---|
| `docs/` | Concept references — architecture, product boundaries, terminology, KQL |
| `labs/` | One folder per capability: objective, build, validation, evidence, analysis |
| `kql/` | Hunting and investigation queries, organized by data source |
| `detections/` | Analytics rules and custom detection rules as exported JSON/YAML |
| `playbooks/` | Logic App definitions for automated response |
| `infra/` | Infrastructure-as-code for lab resources |
| `scripts/` | Scrub tooling and generators for the coverage matrix, posture register, and open-items report |
| `SANITIZATION.md` | Redaction policy and placeholder convention for this repo |
| [`docs/documentation-standard.md`](docs/documentation-standard.md) | Evidence, decision, and detection rules |
| [`docs/open-items.md`](docs/open-items.md) | Tracked documentation debt — generated |
| [`docs/posture-register.md`](docs/posture-register.md) | Every security-relevant setting, its state, and whether it needs revisiting — generated from `posture.yml` |

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
        │  (detect/respond)│───incidents───▶│  (data platform)    │
        └────────┬─────────┘                └──────────┬──────────┘
                 │                                     │
        ┌────────▼─────────┐                ┌──────────▼──────────┐
        │ First-party      │                │ Log Analytics       │
        │ sensors          │                │ Workspace           │
        │ • Endpoint       │                │ • Analytics tier    │
        │ • Identity       │                │ • Data lake tier    │
        │ • Office 365     │                │ • Custom tables     │
        │ • Cloud Apps     │                └─────────────────────┘
        └──────────────────┘                           ▲
                                                       │
                                          ┌────────────┴────────────┐
                                          │ AMA + DCR │ Syslog/CEF  │
                                          │ Azure Activity │ Entra  │
                                          └─────────────────────────┘
```

Microsoft Sentinel and Microsoft Defender XDR are peer products sharing a console: separate licensing, separate billing, separate data stores. The operating experience converges in the Microsoft Defender portal while the products retain distinct responsibilities — the seam between them is where much of this lab's interesting work happens.

### Terminology

Product names are used precisely throughout this repository. "Defender" alone is avoided wherever the specific product matters.

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
| Tenant | Single Entra tenant, lab-only |
| Licensing | M365 E5 trial + Defender for Endpoint / Vulnerability Management |
| Sentinel workspace | *(Lab 04 — not yet created)* |
| Device management | Entra device join + Intune auto-enrollment (Lab 01) |
| Endpoint security | Defender for Endpoint ↔ Intune integrated (Lab 02) |
| Endpoints | *(Lab 03 — in progress)* |
| Data connectors | *(in progress)* |

**The environment is ephemeral, and the two halves expire in opposite directions.**

| Component | Term | At expiry |
|---|---|---|
| Microsoft 365 E5 trial | 30 days | Auto-converts to a **paid** subscription unless cancelled |
| Azure pay-as-you-go | None | Does not expire, does not stop — **bills continuously** for whatever is running |

The free-account safety net (services disabled, no charge without an explicit upgrade) does not apply: the free credit offer was unavailable, so Azure runs pay-as-you-go and consumption is uncapped. Ingestion volume, running compute, and an internet-exposed endpoint are all meters. Budget alerts and VM auto-shutdown are prerequisites, not hygiene.

Two consequences shape how this repository is written:

1. **Evidence is captured as it is produced, not afterwards.** When the trial lapses, every incident, timeline, and query result not already committed here is gone. The repository is designed to outlive the tenant that produced it.
2. **Queries, rules, and IaC are the durable artifacts.** Portal state is not. Anything that cannot be redeployed from this repository is treated as lost by default.

Full build details in `labs/`.

---

## Lab Index

Labs are numbered in build order. The domain and objective columns map each one to the current exam blueprint.

| # | Lab | Domain | Status |
|---|---|---|---|
| [00](labs/00-tenant-licensing-identity/) | Tenant, licensing, and identity foundation | Environment | 🔨 Built, documenting |
| [01](labs/01-device-registration-intune-enrollment/) | Device registration and Intune auto-enrollment | Environment | 🔨 Built, documenting |
| [02](labs/02-mde-intune-integration/) | Defender for Endpoint ↔ Intune integration | Environment | 🔨 Built, documenting |
| [03](labs/03-endpoint-onboarding/) | Endpoint onboarding and first alerts | Environment | 🔜 Next |
| [04](labs/04-sentinel-workspace/) | Sentinel workspace design and deployment | Environment | 🔜 |
| 05 | RBAC and role scoping (URBAC) | Environment | 🔜 |
| 06 | Data connectors and ingestion (AMA/DCR) | Environment | 🔜 |
| 07 | Retention tiering — Analytics / Data lake / XDR | Environment | 🔜 |
| 08 | Attack simulation and alert generation | Response | 🔜 |
| 09 | Detection engineering — analytics rules | Response | 🔜 |
| 10 | Incident investigation and response actions | Response | 🔜 |
| 11 | Automation rules and playbooks (SOAR) | Response | 🔜 |
| 12 | Threat hunting — Advanced Hunting + Sentinel | Hunting | 🔜 |
| 13 | ATT&CK coverage analysis | Hunting | 🔜 |

Numbering follows actual build order, not the exam blueprint's order. Where the two disagree, the build wins — the dependencies are real and the domains are a filing system.

---

## Detection Catalog

Each detection is specified before it is built, using [`detections/_TEMPLATE.md`](detections/_TEMPLATE.md). No rule ships without a hypothesis, a validation method, a documented tuning decision, and a named blind spot.

A rule that has never fired on a known-true event is recorded as **unvalidated** and does not count as coverage.

---

## ATT&CK Coverage

[`docs/attack-coverage.md`](docs/attack-coverage.md) — generated from detection frontmatter by `scripts/build-attack-matrix.py`, and CI-enforced to stay in sync with the specs it describes.

The table separates **COVERED** (every mapped rule proven to fire) from **PARTIAL** and **CLAIMED** (rules written but unproven). The gap between what the lab ingests data for and what it can actually detect is the interesting part, so the matrix is built to expose it rather than average it away.

```bash
python3 scripts/build-attack-matrix.py          # regenerate
python3 scripts/build-attack-matrix.py --check  # CI staleness check
```

---

## Local Setup

This repository enforces sanitization at commit time. The hooks fail closed — install the dependencies before the first commit.

```bash
# Dependencies
brew install gitleaks exiftool tesseract        # macOS
# apt-get install -y exiftool tesseract-ocr     # Debian/Ubuntu; gitleaks: see upstream releases

pip install pre-commit
```

Verify:

```bash
gitleaks version
exiftool -ver
tesseract --version
pre-commit --version
```

Install and run:

```bash
pre-commit install
pre-commit run --all-files
```

**Operational note:** the image hooks modify files in place — `strip-image-metadata` rewrites the image and re-stages it, so the first commit attempt after adding a screenshot will stop and report a modification. Review the modified image, then commit again. That is deliberate: a hook that silently rewrites and proceeds gives you no opportunity to check what it did.

---

## Security Posture

A lab accumulates weakenings. Each is defensible when made and invisible three weeks later.

[`docs/posture-register.md`](docs/posture-register.md) tracks every security-relevant setting observed in the environment: its state, whether it was chosen or inherited, the production answer where they differ, and whether it must be reconsidered before this project is called done. Generated from [`posture.yml`](posture.yml) and CI-enforced to stay in sync.

The register separates **verified** (observed in a portal view) from **asserted** (recorded on the operator's word), because the difference matters and blurring it is how a register becomes decoration.

```bash
python3 scripts/build-posture-register.py          # regenerate
python3 scripts/build-posture-register.py --check  # CI staleness check
```

---

## Notes on Sanitization

This repository is public and describes a live cloud environment. Every commit is audited before push against the policy in [`SANITIZATION.md`](SANITIZATION.md). No tenant identifiers, no live endpoint addresses, no unredacted query output, no offensive tooling artifacts.

Automated enforcement: `gitleaks` pre-commit hook with Azure-specific rules, plus GitHub push protection.

---

## License

MIT — see [`LICENSE`](LICENSE).
