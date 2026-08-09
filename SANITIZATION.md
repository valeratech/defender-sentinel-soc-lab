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
| Device name (client) | `LAB-WIN11-01` | Generic, non-attributable |
| Device name (server) | `LAB-SRV-DEFENDER-01` | Generic. **19 characters by design** — the NetBIOS-truncation finding (`POS-033`, divergence row 13) depends on the name exceeding 15 chars and truncating to `LAB-SRV-DEFENDE`. A shorter placeholder destroys the finding silently |
| Resource group | `rg-soc-lab` | Generic |
| Log Analytics workspace | `law-lab-01` | Generic. Deliberately *not* in the `-soc-lab` family, which the real workspace name resembled closely enough to read as a placeholder |
| Data collection rule | `dcr-winsec-lab` | Generic |
| Resource group (Copilot lab) | `rg-copilot-lab` | Generic. **Keeps the `rg-` prefix by design** — Lab 20 §6's near-miss depends on `NetworkWatcherRG` being the alphabetically first group in the tenant; a placeholder sorting ahead of it would silently erase the finding, the same failure mode as shortening `LAB-SRV-DEFENDER-01` |
| Security Copilot capacity | `copilotlab` | Generic. **Hyphen-free by design** — the Create form accepts lowercase letters and numbers only (Lab 20 §5, MOD-85); a hyphenated placeholder would contradict the finding recorded beside it |
| Security Copilot workspace | `copilotlab-ws` | Generic, derived from the capacity placeholder. The hyphen constraint applies to the capacity name field only, not to workspaces |
| IPv4 (external) | `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | RFC 5737 TEST-NET-1/2/3 |
| IPv6 | `2001:db8::/32` | RFC 3849 |
| Public IP of lab endpoint | **Omitted entirely — not placeholdered** | — |

**Rows added 2026-08-09** for the three resource-name classes Lab 20
introduced. The placeholders were applied in content before the Lab 20 commit
— `0ffbc7d` carries them uniformly — but this table gained no rows, so the
convention existed in content and not in policy. Closed here as the first item
of the completion audit, ahead of everything else, because both placeholders
carry shape constraints (noted in their rows) that a future rename would break
without any gate firing.

**Terms added to `.pii-terms` on 2026-08-08** (the file is gitignored; this is
the record that they were added, not the values). Lab 19 surfaced three classes
of real value the wordlist did not cover: the **tenant GUID**, the **lab
endpoint's public IPv4**, and a **business phone number** returned by Graph and
persisted into Logic Apps run history. The list stands at 16 terms, one of them
a GUID.

Two values were considered and **deliberately not added**: the subscription
GUID and the administrator's object ID. Both were exposed in working sessions
and both are attributable; the judgement was that the tenant GUID is the value
whose presence in history would force a rewrite, and that a wordlist earns its
usefulness by every line mattering. Recorded so the omission reads as a
decision rather than an oversight.

**Terms added 2026-08-09, and two exclusions reaffirmed.** Four candidates
surfaced by Lab 20 were decided together, and the decision doubles as the
wordlist's admission policy:

- **Lab 20's three real resource names — added.** This is the exact failure
  mode the wordlist exists for, and it is now measured rather than argued: a
  sanitized name re-entered through freshly authored prose while every
  shape-based gate stayed green, and the wordlist caught it (see §4, the
  2026-08-09 reintroduction event). Names of this class have demonstrated
  both the leak path and the control that closes it.
- **The Entra User SID — added.** Attributable to a real tenant identity, and
  returned by a surface (Security Copilot, divergence row 158) that no portal
  blade renders, so it can reappear in transcribed output without ever having
  been authored. No scanner in the chain has a rule for the `S-1-*` shape —
  verified against `audit-pii.sh` and both gitleaks configs on 2026-08-09 —
  so this wordlist line is currently the *only* control on the class, not a
  second layer. A structural SID rule is a candidate for the permanent
  scanners; until one exists, the exact value on the list is what stands.
- **Subscription GUID and admin object ID — exclusion reaffirmed.** Both are
  GUID-class values the structural gate already catches by shape, in
  `audit-pii.sh` and CI alike. Adding their exact values would duplicate a
  class under permanent enforcement, and no measurement shows the GUID gate
  being bypassed. The 2026-08-08 rationale stands, now with a sharper rule
  attached.

**The admission policy that falls out:** each layer holds what only it can
hold. Structural scanners own everything with an invariant to grip — GUIDs,
IP shapes, emails, known identifier formats. Exact-value allowlists own
intentional public constants. `.pii-terms` owns attributable values structural
rules cannot know — real resource names and identity-specific strings — and
exact identifiers already under structural enforcement stay off it unless
measurement demonstrates a bypass. The list stands at **20 terms** after these
additions.

**The phone number is the one worth dwelling on.** It reached a log because a
workflow read one field from an object Graph returned whole, and no `$select`
narrowed it (`POS-084`). No placeholder convention would have caught it — the
value was never authored, only logged.

**Two corrections to this section's own first draft**, kept rather than edited
away. It originally claimed five classes were added and named the tenant's
technical-contact address among them; that address was already covered by an
existing token, so the true count is three. And the check used to verify the
additions tested for `@domain`-shaped entries when the file's convention is
bare distinctive tokens — an instrument that reported ABSENT for a term that
was present. Both errors were of the same kind this document exists to catch:
a claim about a control, stated before the control was read.

**Lab 19's new resource names need no placeholder, and this is stated rather
than left implicit.** The playbook/logic app name and both
`Microsoft.Web/connections` names are Microsoft template-derived — they are
what the gallery produces for anyone who deploys that template, carry no
information about this environment, and are non-attributable. They are
committed as-is.

Distinct real values map to distinct placeholders (`analyst@`, `admin@`, `svc-ama@`) so relationships in the data survive redaction and queries remain readable.

### Public constants — allowlisted by exact value, not redacted

A few GUID- and IP-shaped values are published Microsoft/Azure constants,
identical for every tenant, carrying zero information about this environment.
They are documentation, not identifiers, and are allowlisted by **exact value**
in `.gitleaks.toml` and `audit-pii.sh` — a real tenant/subscription/object ID or
a real public IP is still caught; only these specific published values pass.

| Value | What it is |
|---|---|
| `d1e49aac-8f56-4280-b9ba-993a6d77406c` | Public ASR rule GUID — block process creations from PSExec/WMI |
| `e6db77e5-3df2-4cf1-b95a-636979351e5b` | Public ASR rule GUID — block WMI event-subscription persistence |
| `168.63.129.16` | Azure WireServer — fixed virtual platform IP, same in every Azure VNet |

The gate flagged all three on first commit (Lab 06) as REVIEW items — correctly,
since they share the shape of the private values it guards. Clearing them was a
decision recorded here, not a suppression: each is safe *because* it is a public
constant, and the allowlist entry names why.

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
| **Device / computer name** | Reliable | **No — no rule exists, in either config** |

The cause is structural, and it decides which of these can be caught at all. Tesseract's language model assists word-shaped tokens and actively harms high-entropy strings, and in small UI text it routinely eats periods. What survives that is an **anchor** — an invariant the pattern can grip. Emails keep their `@`; domains keep the literal string `onmicrosoft`. Both are recoverable despite the damage.

**An IP address has no anchor.** Strip its dots and `203.0.113.135` becomes `2030113.135`, indistinguishable in principle from a version string, a timestamp, or an order number. There is no rule that catches it without also firing on every four-digit number in every screenshot — and a gate that always warns is a gate nobody reads. So IPs get a heuristic at warning tier and nothing more.

This is the limitation stated plainly rather than papered over: **the OCR gate does not reliably catch IP addresses in images.** It was found the only way such things are found — a real screenshot that the gate passed while an address sat in plain view.

### Two further gaps, found the same way — a real screenshot, 2026-07-17

**Device names have no rule.** Section 2 assigns them a placeholder; section 5 says hostnames of live endpoints are never published in any form, placeholdered or not. Tesseract reads them cleanly off a portal title bar. Neither `.gitleaks.toml` nor `.gitleaks-ocr.toml` has a rule for one, and cannot easily have a useful one: an arbitrary computer name has no invariant to grip, which is the same structural problem as the IPv4 row above. (`azure-vm-public-dns` catches `*.cloudapp.azure.com` — a DNS name, not a machine name. Do not mistake one for the other.) The thing that *could* catch it is `.pii-terms`, which is the second gap.

**`.pii-terms` never reaches an image.** `audit-pii.sh` checks the operator's own identifiers — tenant name, device names, personal terms — against source text. Nothing checks them against recovered OCR text. The two gates have different notions of what is sensitive, and the image gate has the smaller one.

That matters because **both documented anchors can fail on the same string at once.** On 2026-07-17 a portal screenshot rendered an administrator UPN with the `@` eaten *and* `onmicrosoft` corrupted to a near-miss that the literal-word rule does not match — both anchors in this table gone, in a single line, in an image whose other three instances of the same UPN rendered cleanly and were caught. One bad render is enough. What survived that line intact was the **tenant name** — the one string in it that only `.pii-terms` knows about, and the one thing the image gate never consults.

The ceiling here is structural, not an implementation gap: `.pii-terms` is gitignored, so neither GitHub push protection nor CI can ever run this check. It can exist only at pre-commit — the layer section 1 lists as bypassable. A `.pii-terms`-aware OCR check is worth having and must not be mistaken for a gate.

### A third gap, found the same way — a repo grep, 2026-08-06

**Five real resource names sat in committed source for weeks, and every gate passed.**
Found incidentally while checking a resource-group scope for an unrelated lab: the
repository contained the live resource group (9 uses), Log Analytics workspace (30),
server VM (15, plus 5 of its truncated hostname), Win11 VM prefix (2), and data
collection rule (10). Section 2 assigned placeholders for two of those five categories
and had no row at all for the other three.

**Why every gate passed.** `.gitleaks.toml` has no rule for a resource name — the same
structural problem as the IPv4 row above, an arbitrary name having no invariant to grip.
`audit-pii.sh` checks emails, GUIDs, IPs, domains and Azure resource IDs, none of which
these are. The one mechanism that *could* have caught them is `.pii-terms`, which ran and
reported clean **because the names were never on the list**. The gate was working; its
wordlist was incomplete. That distinction matters: nothing here needed building, only
populating.

**The worst instance was a documentation choice, not an omission.** `labs/05` published
the mapping directly — a membership-rule row giving the real device prefix alongside its
placeholder in the same cell, to be transparent about the substitution. That one
parenthetical de-anonymized all 15 uses of `LAB-WIN11-01` elsewhere in the repository. A
placeholder printed next to its real value is not a placeholder. Removed, along with a
second, milder instance in `labs/17` describing what the placeholder stood for.

**Section 2 and section 5 contradicted each other**, and this is the resolution. Section 5
states hostnames of live endpoints are never published *in any form, including
placeholdered*; section 2 assigns device names a placeholder. Both cannot hold. Section 5
is now read as governing **real** hostnames, DNS names, and public IPs — never published
in any form. Placeholders for devices are permitted and required, per section 2. Section 5
is amended below to say so rather than leaving the reader to pick.

**History was not rewritten, and that is a decision rather than an oversight.** The names
were introduced between the Lab 04 and Lab 07 commits; a rewrite removing them would touch
**45 of 47 commits**, invalidating every published SHA and every cross-reference in the
commit log, on a repository whose whole premise is a dated, verifiable record. Weighed
against a leak consisting of resource names in a disposable single-analyst tenant holding
no real data — the same mitigating control named in Lab 00 §7 — the rewrite costs more
than it buys. **Commits before `02737e7` therefore contain real resource names.** Stated
here plainly so a reader finds it in the document that claims the repository is sanitized,
rather than discovering it in `git log`.

**Rejected alternative:** `git-filter-repo` plus a force push. Rejected on the ratio above,
not on difficulty. It remains the correct answer if a *credential*, tenant GUID, or public
IP is ever found in history — those are not resource names and the calculus inverts.

**The sweep itself was scoped wrong first time, and the gate caught it.** The initial
substitution pass walked `.md`, `.yml`, `.yaml` and `.toml` — a curated extension list,
chosen by assuming documentation was where names live. `audit-pii.sh` then fired on
`kql/sentinel/store-partition-diff.kql`, a query file carrying the workspace name in a
navigation comment. Query files, scripts, and detection artifacts are all plausible
carriers; the corrected pass walks every readable file except `.git`. Recorded because the
error was in the search scope rather than the search terms, and a clean result from a
narrow sweep reads identically to a clean result from a complete one.

**The durable fix is the wordlist, not this edit.** All five names are added to
`.pii-terms`, which is gitignored and therefore local-only and pre-commit-only — the layer
section 1 lists as bypassable. That ceiling is unchanged and is the reason this took weeks
to surface.

### The wordlist firing on a reintroduction — 2026-08-09

The paragraph above asserted the wordlist is the durable fix. During Lab 20 it
was measured. Writing MOD-88's teardown prose, a resource-group name already
on `.pii-terms` was reintroduced into new content — not copied from an old
file, authored fresh, which is the path no substitution sweep revisits. Every
shape-based gate passed, for the reasons this section already records: gitleaks
has no invariant to grip on an arbitrary name, and `audit-pii.sh`'s structural
checks (emails, GUIDs, IPs, domains, resource IDs) do not cover one. The
`Personal terms` check caught it — twice, independently, on the build container
and on the WSL working copy — before the content reached the tree.

Two things follow. The third gap's closing claim is no longer an assertion:
the wordlist is the only control in the chain that fires on this class, and it
has now fired on it. And sanitized names are not removed once — they are
removed continuously, because the documentation keeps naming its subjects.
The leaks come from documenting the leaks.

**Therefore: a green hook result is not proof that an image is sanitized.** Every image requires manual visual review after cropping and redaction, even when the metadata hook, the gitleaks scan, and the OCR scan all pass. The automation exists to catch the screenshot committed at the end of a long session, not to replace the look.

---

## 5. Live Lab Endpoints

Lab endpoints are deliberately weakened to generate telemetry. They are real, reachable, and owned by me.

- **Real** public IPs, DNS names, and hostnames of live endpoints are **never published**,
  in any form. Public IPs are omitted entirely rather than placeholdered; hostnames take
  the section 2 placeholders. Amended 2026-08-06 — as originally written this line read
  "including placeholdered", which contradicted section 2's device-name row. See the
  third gap in section 4.
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

## 7a. Transport — how the working copy is moved

The repository is authored in a container and delivered as a tarball for the
operator to verify, extract, gate, and commit. That transport is part of the
sanitization system, because one of the files it carries is the thing that
keeps `.pii-terms` out of history.

**Build tarballs with `--exclude=.git`. Never `--exclude-vcs`.**

GNU tar's VCS-exclusion list is not a `.git*` wildcard. It removes `.git/`,
**`.gitignore`**, **`.gitattributes`** and `.gitmodules`, while leaving
everything else beginning with `.git` in place. Measured against this working
tree on 2026-08-08:

| Invocation | `.gitleaks.toml` | `.gitleaks-ocr.toml` | `.github/` | `.gitignore` | `.gitattributes` |
|---|---|---|---|---|---|
| `--exclude-vcs` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `--exclude=.git` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Why it stayed invisible.** Every tarball in this project was built with
`--exclude-vcs`, and none of them ever surfaced the defect, because they are
always extracted *over an existing working tree* where both files survive from
the prior state. A spot-check of "did the security tooling make it across"
passes every time — both gitleaks configs and the workflow directory are
present. The one file that keeps `.pii-terms` uncommitted is the one silently
dropped.

**Why it matters here specifically.** `.pii-terms` is the wordlist gate. It is
deliberately gitignored, because a list of the exact strings that must never
appear in this repository is the worst possible file to publish. On a clean
extract with no `.gitignore`, the next `git add -A` stages it. The failure
chain is: a tar flag drops an ignore file, an ignore file stops excluding a
wordlist, and a wordlist of real values enters history — from a command whose
stated purpose is to *exclude* version-control metadata.

**This is `d5d3d3d`'s shape applied to the delivery mechanism.** The check and
the gap did not overlap: everything an operator would think to verify was
present, and the mechanism reported healthy while the specific thing that
mattered was gone. *Configured ≠ effective*, one layer below the tenant.

## 8. Enforcement

**Pre-commit** — `gitleaks` with the custom Azure/Sentinel rule set in `.gitleaks.toml`. Blocks the commit.

**Image OCR scan** — `scripts/scan-image-text.sh` via pre-commit. Blocks on recovered values; warns on portal chrome labels. See section 4 for limits.

**Pre-push manual audit** — `git diff --cached` reviewed against Section 1 before every push. Automation catches patterns; it does not catch judgment.

**Server-side** — GitHub secret scanning with push protection enabled.

**Ignored by default** — see `.gitignore`: `.azure/`, `*.tfstate*`, `*.parameters.json`, `*.publishsettings`, `.env`, `*.pfx`, `*.key`.

---

### `gitleaks dir` reports a standing 2 — and it is correct to

Scanning the working directory rather than the index, `gitleaks dir` reads
gitignored files. `.pii-terms` holds real values by design, so as of
2026-08-08 it produces exactly two findings — `azure-guid-any` and
`public-ipv4-review`, both on the wordlist's own lines.

**These are true positives on a file that is out of scope.** The rules fired
correctly; the file will never enter history. Verified 2026-08-08: findings
intersected against `git ls-files` gives **0 in tracked files**, and
`git check-ignore` confirms the exclusion.

Recorded because a check that always reports the same non-finding is a check
people learn to skim — the same reasoning that keeps the OCR IP heuristic at
warning tier (§4). The number to read is not gitleaks' total; it is the
intersection with tracked files. If that is ever non-zero, it is real.


## 9. If Something Leaks

1. Rotate first, scrub second. A revoked key is harmless in history; a scrubbed-but-live key is not.
2. Revoke the credential, rotate workspace keys, regenerate the Logic App callback.
3. Treat the value as permanently public. Assume it was cloned.
4. Rewrite history only after rotation, and only with `git-filter-repo`.
5. Record the incident in this file's changelog. Handling a leak transparently is a stronger signal than pretending it never happened.

### Changelog

| Date | Event |
|---|---|
| 2026-07-16 | **Invented IOC committed and scrubbed from history.** A public IPv4 address was written into a lab writeup as an example attacker IOC. It was not observed in this environment and not sourced from threat intelligence — it was generated, and it labelled a live, routable allocation as attacker infrastructure. No tenant data was exposed and nothing required rotation. Removed from history with `git-filter-repo`; the address is treated as permanently public per §9.3 regardless. **Cause:** the address was produced while drafting documentation, which is the same path that produced every other near-miss this repo has had — an operator email in code comments (×4) and a lab public IP in prose (×2), all caught pre-commit. The gates catch leaks; the gates do not catch invention. §7 was written afterwards and is the control: this document deliberately does not print a real IOC. |

**On the scope of this table.** Nothing of the tenant's has leaked. This entry is here because §9.5 says to record incidents and the commit graph shows a history rewrite, and a changelog that reads "no incidents" beside a `git-filter-repo` in the log is the one line in this document a reader can falsify for themselves. The near-misses above are not listed as incidents because they never entered history — the gates held. That distinction is the point of keeping the table at all.
