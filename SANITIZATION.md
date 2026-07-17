# Sanitization Policy

This repository is public and documents a live Azure tenant. Everything committed here is treated as permanently public from the moment it enters git history, including content later "deleted" — a force-push does not recall a clone.

This document defines what must be redacted, how, and how it is enforced.

---

## 1. Classification

| Class | Items | Exposure |
|---|---|---|
| **Secrets** | Workspace primary/secondary keys, service principal client secrets, Logic App callback URLs, automation webhook URLs, API keys, connection strings, `*.tfstate`, `*.parameters.json` | Direct authentication material. Immediate compromise. |
| **Identifiers** | Tenant ID, subscription ID, workspace ID, resource IDs, DCR immutable IDs, application/object IDs | Not secrets. Real coordinates of the tenant — enable targeted enumeration and phishing. |
| **Attributable** | UPNs, email addresses, display names, device names, resource group names, MAC addresses | PII, and links the lab to a person or organization. |
| **Operational** | Public IPs of lab resources, DNS names, NSG rules, open ports, admin usernames | Describes a reachable, intentionally weak attack surface. |
| **Indirect** | Offensive tooling binaries, C2 configuration, malware samples, payload scripts | Weaponizable regardless of intent. |

---

## 2. Placeholder Convention

Replacements are visibly synthetic and internally consistent. Values are drawn from reserved documentation ranges so they can never resolve to a real asset.

| Real value | Placeholder | Source |
|---|---|---|
| Tenant / subscription / workspace / object GUID | `00000000-0000-0000-0000-000000000000` | Nil UUID |
| Domain | `contoso.onmicrosoft.com` | Microsoft doc convention |
| User principal name | `analyst@contoso.com` | — |
| Device name | `LAB-WIN11-01` | Generic, non-attributable |
| Resource group | `rg-soc-lab` | Generic |
| IPv4 (external) | `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | RFC 5737 TEST-NET-1/2/3 |
| IPv6 | `2001:db8::/32` | RFC 3849 |
| Public IP of lab endpoint | **Omitted entirely — not placeholdered** | — |

Distinct real values map to distinct placeholders (`analyst@`, `admin@`, `svc-ama@`) so relationships in the data survive redaction and queries remain readable.

### Not redacted

Threat intelligence, attacker-controlled IPs observed in the wild, public IOCs, and Microsoft-published sample data. These are already public and their removal would gut the analysis.

---

## 3. Query Output

The KQL is safe. The results are not.

- Query text: commit freely.
- Query results: redact source IPs belonging to the lab, all UPNs, all device names, all resource IDs before committing.
- Row counts, timestamps, aggregate statistics, and attacker-side IPs: retain.

Preferred format for results is a markdown table with placeholder substitution applied, not a screenshot. Tables are diffable, searchable, and cannot leak the chrome around them.

---

## 4. Screenshots

Screenshots are the highest-risk artifact in this repository. Portal chrome carries tenant identity in at least seven places: directory switcher, breadcrumb, subscription dropdown, account avatar and its tooltip, resource blade header, browser tab title, and bookmarks bar.

**Rules:**

1. Crop to the content pane only. Never capture full browser or full desktop.
2. Redact with **opaque fills**, then flatten. Blur and pixelation on text are reversible.
3. Strip EXIF/metadata before commit.
4. Prefer a table or code block over a screenshot wherever the information is textual. Screenshot only where the visual itself is the point — attack graph, timeline, investigation UI.

### Limits of automated scanning

> **Automated scanning does not reliably inspect text embedded in screenshots.** gitleaks reads bytes, not pixels — a tenant ID, UPN, subscription ID, or lab public IP rendered into an image passes every textual scan, because the identifier is image data rather than text.

`scripts/scan-image-text.sh` partially closes this gap by OCR-ing each staged image and re-scanning the recovered text against `.gitleaks-ocr.toml`. It is a net, not a guarantee, and its failure mode is specific and measured:

| Content | OCR recovery | Caught by scan? |
|---|---|---|
| Email / UPN | Degraded — periods dropped | Yes — the `@` survives and anchors the match |
| `*.onmicrosoft.com` domain | Degraded — separators dropped | Yes — the literal word survives and anchors it |
| GUID / tenant ID | **Poor** (`72f988bf` → `7 2(988bf`) | Only via fuzzy + despaced pass |
| **IPv4** | **Poor** (`203.0.113.135` → `2030113.135`) | **Warning tier only — not reliably** |
| Identifier labels ("Tenant ID") | Reliable | Warning tier |

The cause is structural, and it decides which of these can be caught at all. Tesseract's language model assists word-shaped tokens and actively harms high-entropy strings, and in small UI text it routinely eats periods. What survives that is an **anchor** — an invariant the pattern can grip. Emails keep their `@`; domains keep the literal string `onmicrosoft`. Both are recoverable despite the damage.

**An IP address has no anchor.** Strip its dots and `203.0.113.135` becomes `2030113.135`, indistinguishable in principle from a version string, a timestamp, or an order number. There is no rule that catches it without also firing on every four-digit number in every screenshot — and a gate that always warns is a gate nobody reads. So IPs get a heuristic at warning tier and nothing more.

This is the limitation stated plainly rather than papered over: **the OCR gate does not reliably catch IP addresses in images.** It was found the only way such things are found — a real screenshot that the gate passed while an address sat in plain view.

**Therefore: a green hook result is not proof that an image is sanitized.** Every image requires manual visual review after cropping and redaction, even when the metadata hook, the gitleaks scan, and the OCR scan all pass. The automation exists to catch the screenshot committed at the end of a long session, not to replace the look.

---

## 5. Live Lab Endpoints

Lab endpoints are deliberately weakened to generate telemetry. They are real, reachable, and owned by me.

- Public IPs, DNS names, and hostnames of live endpoints are **never published**, in any form, including placeholdered.
- NSG rules and exposed port configurations are described in prose ("RDP exposed to the internet to farm authentication failures"), never as committable rule exports.
- Weakened endpoints are deallocated when the lab is idle and rebuilt from `infra/` on demand.

---

## 6. Offensive Artifacts

Alert generation requires triggering behavior Defender considers malicious.

- Reference tooling **by name and version**. Describe **what** was executed and **why**.
- Never commit binaries, payloads, C2 configs, encoders, or malware samples.
- For reproducibility, cite public sources — Microsoft's built-in simulations, EICAR, Atomic Red Team test IDs — rather than vendoring the artifact.
- Commit the **telemetry and the detection**, which is the actual portfolio value. The payload is not.

---

## 7. Intentional Friction

Two rules fire on content that is sometimes legitimate. This is by design, and neither should be weakened into a blanket exception.

### Every non-placeholder GUID fails

`azure-guid-any` flags any GUID that is not the nil UUID — including legitimate public GUIDs from Microsoft documentation, product definitions, and sample content.

That is acceptable, because it forces a deliberate choice at each occurrence:

- replace it with the nil UUID,
- add a narrowly scoped allowlist entry, or
- document why the public identifier must remain.

**Do not add a general GUID exception.** The rule's value is that it cannot distinguish your tenant ID from a documentation GUID — which is exactly why a human has to.

### Public threat-intelligence IPs fail

Policy permits retaining attacker-controlled public IPs for analytical reproducibility, but the scanner cannot determine ownership. Every retained IOC needs a local exception.

Use a nearby inline allow directive, never a global one:

```kusto
// gitleaks:allow
// Public attacker-controlled IOC retained for analytical reproducibility.
// Verified as not belonging to the lab environment.
| where RemoteIP == "<observed-attacker-ip>"
```

The literal address replaces the placeholder in real usage; `gitleaks:allow` is what lets it past `public-ipv4-review`.

**This document deliberately does not print a real IOC.** Annotating a live, routable address as attacker infrastructure is a factual claim about whoever holds that allocation, and a public repository publishes it. Documentation examples are also copied without their context, so an invented "example" IP propagates as though it were sourced. An address is only labelled here once it is genuinely observed and attributed in a lab writeup.

Adding IOCs to `.gitleaks.toml` permanently would erode the rule until a lab IP eventually slips through under cover of the exception list.

---

## 8. Enforcement

**Pre-commit** — `gitleaks` with the custom Azure/Sentinel rule set in `.gitleaks.toml`. Blocks the commit.

**Image OCR scan** — `scripts/scan-image-text.sh` via pre-commit. Blocks on recovered values; warns on portal chrome labels. See section 4 for limits.

**Pre-push manual audit** — `git diff --cached` reviewed against Section 1 before every push. Automation catches patterns; it does not catch judgment.

**Server-side** — GitHub secret scanning with push protection enabled.

**Ignored by default** — see `.gitignore`: `.azure/`, `*.tfstate*`, `*.parameters.json`, `*.publishsettings`, `.env`, `*.pfx`, `*.key`.

---

## 9. If Something Leaks

1. Rotate first, scrub second. A revoked key is harmless in history; a scrubbed-but-live key is not.
2. Revoke the credential, rotate workspace keys, regenerate the Logic App callback.
3. Treat the value as permanently public. Assume it was cloned.
4. Rewrite history only after rotation, and only with `git-filter-repo`.
5. Record the incident in this file's changelog. Handling a leak transparently is a stronger signal than pretending it never happened.

### Changelog

| Date | Event |
|---|---|
| — | No incidents recorded. |
