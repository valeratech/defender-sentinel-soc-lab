# Lab 19 — Sentinel Playbooks: A Permission Checked Before Anything Ran, and a Credential in Three Places

| Field | Value |
|---|---|
| **Domain** | Response / SOC automation |
| **Objectives** | Deploy a Microsoft-supplied Sentinel playbook (the Sentinel-playbooks guide, G57); establish the four identities a playbook needs and observe what each grant actually buys; trigger it live and read the result at every surface it writes to |
| **Depends on** | Lab 11 (`DET-004` / `LAB-Bruteforce-Failed-Signins` — the detection this playbook responds to), Lab 18 (Orders 1 and 2 on the same analytic rule; this lab adds Order 3), Lab 17 (`POS-074` analyst as assignee) |
| **Status** | ✅ Built and measured — refused, granted, fired, observed across seven surfaces, remediated |
| **Built** | 2026-08-06 → 2026-08-08 |

> The prediction was that the automation rule would create cleanly and the
> playbook would silently never run. **Sentinel refused to create the rule at
> all** — ARM `BadRequest`, missing permissions on the playbook resource,
> validated at *authoring* time. Granting Sentinel's service principal
> `Microsoft Sentinel Automation Contributor` and resubmitting the identical
> form succeeded. Withheld → refused; granted → ran. Then seven failed
> sign-ins produced incident 24, three automation rules fired in order, and
> the playbook reset a user's password in 5.05 seconds. It worked. It also
> wrote that password in plaintext to run history, mailed it from the
> recipient's own account at **Low importance**, logged the account holder's
> phone number alongside it, and recorded its one consequential action in the
> incident audit trail as **`Trigger: Manual`** with no completion status —
> where every cosmetic change beside it reads `Automated` / `Completed`. The
> user then completed the forced change by setting the password back to the
> value the reset had just invalidated.

---

## 1. Objective

The Sentinel-playbooks guide deploys a playbook from Sentinel's template gallery and attaches it
to an automation rule. The nominal lesson is "playbooks are Logic Apps." The
lab's actual subject is **identity**: a playbook is one object with four
identity relationships, and each one is a separate grant that fails
differently when absent.

Three things this lab measures rather than accepts:

1. **What each grant buys.** Four grants were made. The lab withholds one
   deliberately to observe the failure, then applies it and retries the
   identical operation.
2. **Where the credential goes.** A password-reset playbook necessarily
   handles a live secret. The question is how many places it comes to rest,
   and which of them a rotation does not clean.
3. **Whether "Succeeded" means what it says.** At four separate surfaces in
   this lab, a green status answered a different question than the one being
   asked.

Cost: Logic Apps Consumption. One run, eleven actions, two API connections.
Below the free grant at this volume; the meter is open and was opened
knowingly (`POS-084`).

## 2. Predictions

| # | Prediction | Outcome |
|---|---|---|
| P19-1 | The automation rule creates and fires; the playbook silently never runs for want of permission | ❌ **WRONG, and this is the lab's headline** — Sentinel refused to *create* the rule. Row 136 |
| P19-2 | The PIM member picker will not browse service principals; the object ID is required | ✅ Confirmed, mechanism sharper than predicted — the picker's own tab list is a function of the result set. `Enterprise applications` did not exist as a tab until a GUID search returned one |
| P19-3 | `Condition - is manager available` tests whether a manager exists | ⚠️ **REVISED then CONFIRMED** — it tests `statusCode = 200`. Row 144 |
| P19-3a | The lookup returns 200; true branch; no password in the incident comment | ✅ Confirmed — 200, true branch, `False` branch `Skipped` with reason `ActionBranchingCondition` |
| P19-4 | Three resources created; the diagnostic setting is a child object, not a fourth | ✅ Confirmed |
| P19-5 | `Secure inputs`/`Secure outputs` ship Off; the plaintext password reaches run history | ✅ Confirmed — and Off turned out to be **absent, not false**. Row 145 |
| P19-6 | `Initialize variable` / `Set variable` sit outside `For each`; one password for every account entity | ✅ Confirmed statically *and* at runtime — generation completes **two actions before** entity retrieval begins. Row 143 |
| P19-7 | The reset precedes the lookup, so a notification failure still leaves the user reset with no delivered credential | ⬜ **Untested** — nothing failed. Confirmed structurally from the definition; not exercised |
| P19-8 | Incident created; three rules fire serially, lowest order first | ✅ Confirmed at millisecond resolution — and the incident number was read from the run's own `Client tracking ID` suffix, not from the queue |
| P19-9 | `Runs last 24 hours` → 1 successful, 0 failed; run reports `Succeeded` regardless of branch | ✅ Confirmed |
| P19-10 | Security defaults **Enabled**; that is what demanded MFA registration | ❌ **WRONG** — security defaults are Disabled, zero CA policies exist. Row 149 |
| P19-11 | The registration interrupt fires only on successful interactive sign-in | ⬜ **Unfalsifiable as stated** — it was contingent on P19-10's mechanism. Withdrawn rather than retained as a plausible leftover |

Two predictions wrong, one withdrawn, one untested. P19-1 being wrong is the
lab; P19-10 being wrong is recorded because it was reasoned from plausibility
rather than read from the tenant, which is the error the repo exists to catch.

## 3. Design Decisions

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Template | `Reset Microsoft Entra ID User Password - Incident Trigger` | The alert-trigger and manual variants | Three templates differ only in `Trigger type`; incident-trigger is the one an automation rule can launch (§6, adjacent-name traps) |
| Automation Contributor | **Withheld on the first attempt**, granted on the second | Grant everything up front | Withholding one grant and retrying the identical form is the only way to isolate causation. It produced the lab's headline |
| Playbook Operator | Not granted | Grant it for completeness | Manual-run is out of scope; the `Run playbook` control renders regardless (§7) |
| Order | 3 | 1 | Joins Lab 18's Orders 1 and 2 on the same analytic rule — three rules on one incident makes serial execution legible |
| Region | West US 3 | West US, matching the RG's 15 other resources | Not a decision. The field is derived from the resource group and locked (§7) |
| First run | `Secure inputs`/`Secure outputs` left Off | Turn them on before triggering | The exposure *is* the finding. Turning them on first would have hidden what a default deployment does |
| `labuser` after the lab | Left as-is, MFA registration outstanding | Create a fresh licensed identity | See §6 — and note the stated reason expired while the decision stayed correct |

## 4. Build

Deployed to `rg-soc-lab`, **West US 3**, diagnostics to `law-lab-01`. Three
resources: the workflow plus two `Microsoft.Web/connections`.

**The four identity relationships** (`POS-081`, `POS-082`, `POS-083`):

| # | Grant | System | Principal | Scope |
|---|---|---|---|---|
| 1 | Microsoft Sentinel Responder | Azure RBAC | logic app managed identity | `rg-soc-lab` |
| 2 | Password Administrator | Entra directory role, via PIM | logic app managed identity | Directory, Active, Permanent |
| 3 | Office 365 Outlook | Delegated OAuth | `admin`'s mailbox | n/a |
| 4 | Sentinel Automation Contributor | Azure RBAC | `Azure Security Insights` (Sentinel's SP) | `rg-soc-lab` |

Grants 1–3 first. Automation rule `LAB-AutoReset-Bruteforce-Password`, Order 3,
trigger *When incident is created*, condition `Analytic rule name` **Contains**
`LAB-Bruteforce-Failed-Signins`, action `Run Logic Apps playbook`. **Create
failed.** Grant 4, resubmit the identical form, created.

`labuser`'s manager set to `admin` on 2026-08-06; the empty state
(`None provided`) was captured first.

**Trigger:** 7 failed sign-ins as `labuser` at `portal.azure.com`,
2026-08-08 11:45 PDT / 18:45 UTC.

## 5. Validation

| Check | Method | Expected | Result |
|---|---|---|---|
| Rule creation without grant 4 | Azure Activity log, `Update Automation Rules`, JSON tab | Rule creates | ❌ ARM `BadRequest` — *missing required permissions for Microsoft Sentinel on the playbook resource* (row 136) |
| Rule creation with grant 4 | Identical form, resubmitted | Rule creates | ✅ Created |
| Playbook executed | Overview → `Runs last 24 hours` | 1 successful | ✅ 1 successful, 0 failed; run 11:57:47 PDT, **5.05 s** |
| Latency, volley → run | Wall clock | ~10 min (Lab 18) | ✅ 12 m 47 s |
| Serial ordering | Incident 24 Activities, ms resolution | Orders 1, 2, 3 | ✅ correlate `18:57:27.173Z` → O1 `.38.533` → O2 `.42.180`/`.42.183` → playbook `.51.909` |
| Incident identity | Run's `Client tracking ID` | — | ✅ suffix `_24` — the join key between a Logic Apps run and a Sentinel incident |
| Manager lookup | `HTTP - get manager` Outputs | 200 | ✅ 200, on the **managed identity** (`POS-081`) |
| Branch taken | Condition expansion | True | ✅ True (3 actions green); `False` **Skipped**, reason `ActionBranchingCondition` |
| Password reset | `HTTP - reset a password` Outputs | success | ✅ **204 No Content** — not 200 (row 144) |
| Iterations | `For each` | 1 | ✅ `1 of 1` — one account entity |
| Credential in run history | Action Inputs | plaintext | ✅ plaintext, 10 chars, `substring(guid(),0,10)` shape (`POS-084`) |
| Credential in mail | `admin`'s Inbox | delivered | ✅ 11:57, plaintext in body, **From = To**, `Low importance` (`POS-083`) |
| Credential in incident comment | Incident 24 Activities | absent on true branch | ✅ absent — comment names the manager, not the password |
| Forced change | `labuser` sign-in | prompt | ✅ `50055` expired-password, ceremony completed |
| Remediation effective | Old password at sign-in | rejected | ✅ `50126` — the reset **did** invalidate it |
| Remediation durable | New password chosen | — | ❌ the **old value was accepted as the new password** (row 148) |

## 6. Failures & Fixes

**The rule would not create.** Diagnosed only from Azure Activity log →
operation `Update Automation Rules` (not "Create") → **JSON** tab. The toast
auto-dismissed; the Defender bell retained nothing. Fixed by grant 4 (row 137).

**The designer hid the one deployment error** two levels down, inside
`For each` → `Condition` → True branch. An earlier claim that "the guide is
wrong, the canvas is clean" was **withdrawn** — the canvas was collapsed, not
clean (row 138).

**Authorizing a connection is not saving.** Clearing the card error emptied
the Flow Checker and dropped the Connections red dot without persisting
anything. The only tell is `Save` un-greying (row 138).

**MFA registration was demanded mid-remediation** and not completed. Chased
through four surfaces to `Authentication methods → Registration campaign`,
`State: Microsoft managed` (row 149, `POS-085`).

**`labuser` left in limbo, deliberately** (`POS-086`). The account keeps its
role as the tenant's failed-signin generator: the registration interrupt fires
only on *successful* interactive sign-in, and `labuser` never successfully
authenticates in normal lab use. **The stated reason for not creating a
replacement has already expired** — it was originally the 8/14 licence cliff,
and by the time this shipped the decision stood on better grounds: `labuser`
carries eleven labs of telemetry continuity from `First Seen 7/17`, and a new
identity would fork that for no gain. Recorded this way on purpose, per
`POS-058`'s pattern — a decision whose reason expired while the decision
stayed correct is the kind a future reader inherits wrongly.

## 7. Analysis

**The permission is checked before anything runs, and two checks in one blade
disagree.** The `Run Logic Apps playbook` dropdown *offered* the playbook —
directly above static text reading that an unavailable playbook means Sentinel
lacks permission to run it. The dropdown filters on trigger type; the create
path validates authorization. An operator reading that blade sees an available
playbook and an explanation of unavailability side by side, and neither is the
check that will actually decide (row 136). `Manage playbook permissions`,
which sounds like the remedy, opens learn.microsoft.com (row 137).

**Over-permission is what kept the credential out of the incident.** Grant 2
was made so the `PATCH` would succeed. Two actions later `HTTP - get manager`
reads `/users/{upn}/manager` on the *same* managed identity, a directory read
nobody granted with that in mind — and it returned 200. Had the role been
narrower, the run would still have reported `Succeeded`, taken the `False`
branch, and **written the plaintext password into the incident comment**,
where anyone with Sentinel Reader can see it and where it outlives run
history's 90 days. The degraded path is the leaky path (row 144). A
least-privilege improvement to grant 2, made without reading the template,
would have created a credential disclosure. That is not an argument against
least privilege; it is an argument that the template's failure mode is
inverted, and that scoping a role without reading what rides on it is
guesswork.

**The template's success test is disproved by its own sibling.** The condition
is `statusCode = 200`. The `PATCH` two actions earlier returned **204**. Graph
success is not one number, and the workflow hardcodes one (row 144).

**One credential, three resting places, one rotation.** Run history (90 days),
`admin`'s Inbox *and* Sent Items, and the account itself. Rotation cleans the
third only. `Secure inputs`/`Secure outputs` were not *disabled* — the
`runtimeConfiguration` block is **absent**; the designer renders toggles for a
property that does not exist until set. Nobody turned the protection off;
nobody turned it on (`POS-084`, row 145). And the credential is not the only
secret logged: `HTTP - get manager` carries no `$select`, so Graph returned the
full user object — display name, mail, and the account holder's **phone
number** — all persisted for the same 90 days to satisfy a workflow that reads
one field.

**The delegated connection makes the tenant owner the sender.**
`From: Lab Administrator` → `To: Lab Administrator`. Security notification mail
arrives from its own
recipient, lands in Sent Items, passes SPF/DKIM/DMARC as a legitimate internal
send, and attributes the action to a human in the audit trail. The Office 365
connector offers no managed-identity option, so this is not a design choice in
the template — it is a connector limitation inherited silently (`POS-083`,
row 147). Microsoft ships it at `Low importance`.

**The one consequential action is the one the audit trail misfiles.** Three
automation rules wrote tags and an owner; all three read `Trigger: Automated`,
`Activity status: Completed`. The playbook — which changed a user's credential
— reads **`Trigger: Manual`**, performer `Playbook-Reset-…` (a fifth name for
this object), with `Activity status` and `Policy status` **empty**. An
operator auditing "what did automation do to this incident" and filtering on
`Automated` loses exactly the row that mattered (row 146).

**A reset that the user can undo in one step.** The old password was correctly
rejected at authentication (`50126`) — the reset worked. The forced-change
ceremony then accepted that same just-invalidated value as the new password.
In the threat model this playbook exists for, the account holder completing
the ceremony may be the attacker, and they satisfy `Current password` with the
temp credential they already have. The automation's reported outcome and the
tenant's end state diverge completely (row 148). Which of three mechanisms
permits it — history depth, forced-change bypass, or an admin `PATCH` that
never writes history — is **not established and not asserted**.

**Nothing in the tenant required MFA, and MFA was required.** Security
defaults `Disabled`, zero Conditional Access policies, `Conditional Access:
Not Applied` on all 28 sign-in rows. The requirement came from
`Authentication methods → Registration campaign`, `State: Microsoft managed` —
a control whose on/off state the tenant does not own and whose dependent
fields are greyed (`POS-085`, row 149). This inverts the repo's usual shape.
The recurring finding has been *configured, and ineffective*. This is
**unconfigured, and in force**.

**One object, now nine names.** Azure Logic Apps (service), a logic app
(instance), `Logic app` (portal), `Microsoft.Logic/workflows` (ARM), playbook
(Sentinel), managed identity / Enterprise application / service principal
(identity surfaces), and `Playbook-Reset-…` (incident audit trail). The
concept doc opened at seven; the runtime added two.

**Four surfaces rendered a truncated entity and agreed with each other.**
Incident grid, graph node, alert list, `Impacted assets` — all showed
`labuser`. The `SecurityAlert` entity object carries `Name`, `UPNSuffix`,
`UserPrincipalName`, `DisplayName` and `AccountName`. They agreed because
they all render the same field, not because they were right (row 152). The
template then rebuilds the UPN with `concat(Name, '@', UPNSuffix)` — with a
casing inconsistency repeated five times — while a complete `UserPrincipalName`
sits unused in the same object. The reconstruction is the only thing that could
produce a malformed URI, and a malformed URI routes to the leaky branch.

**Region is derived, not chosen.** The RG is West US 3, its 15 pre-existing
resources are West US, and all three new resources inherited West US 3 through
a locked field. Confirmed independently at runtime from two non-portal
sources: the Logic Apps **scale-unit host** fronting the run-history links (a
shared Azure infrastructure name, region-stamped) and Graph's
`x-ms-ags-diagnostic` response header, which reads `DataCenter: West US 3`.
Neither is the `Location` field, which is where the value was set.

## 8. References

- [Tutorial: Respond to threats using playbooks](https://learn.microsoft.com/en-us/azure/sentinel/tutorial-respond-threats-playbook)
- [Automate threat response with playbooks](https://learn.microsoft.com/en-us/azure/sentinel/automate-responses-with-playbooks)
- [Authenticate playbooks to Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/authenticate-playbooks-to-sentinel)
- [Microsoft Entra registration campaign](https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-mfa-registration-campaign)
