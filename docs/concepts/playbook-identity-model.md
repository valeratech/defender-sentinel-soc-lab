# Playbook Identity Model — Connections, Connectors, and Who Each Action Runs As

<!-- Committed with Lab 19 (`docs/evidence-notes/sentinel-playbooks.md`); the POS-081+
references resolved when the Lab 19 posture entries landed. Sections marked PREDICTED
were written before the observation phase and are settled in the lab README. -->

**A playbook does not have one identity.** Each connector and each action can
authenticate through a different system, as a different principal, against a
different permission model. That single fact explains why one working
password-reset playbook needs grants in three places, why Microsoft's own
post-deployment instructions are incomplete, and why the guide's closing
observation holds — playbook troubleshooting is almost always permissions
troubleshooting.

This note records the model as understood at the **Connections step of the
deployment wizard**, before any grant was made. It is a reference; the
measurements are in `labs/19-sentinel-playbooks/README.md`.

## The four objects, and why they are four

| Object | What it is | Where it lives |
|---|---|---|
| **logic app workflow** | The step sequence. A JSON definition executed by the Logic Apps runtime | `Microsoft.Logic/workflows` |
| **API connection** | A separate resource holding a credential for one target service | `Microsoft.Web/connections` |
| **Connector** | Microsoft-hosted adapter that owns the endpoint, token handling, and retries | Microsoft's infrastructure, not the tenant |
| **Identity** | Who an action is performed *as* | Managed identity, or a delegated user |

**Naming, pinned down** — four vocabularies describe one object, and they do not
match. The Azure service is **Azure Logic Apps** (plural). A single instance is
**a logic app** (Microsoft styles it lowercase), which the portal labels `Logic app`
and which ARM calls `Microsoft.Logic/workflows`. The RBAC role is
`Logic App Contributor`. Sentinel then adds a fifth term by calling the same object
a **playbook**. This document uses the service name capitalised, the instance
lowercase, and control names exactly as the portal renders them.

"Playbook" names none of these. It is the label Sentinel applies to a logic app
whose trigger belongs to Sentinel — a filtered view, not a resource type. Deploy
the same workflow behind a Recurrence trigger and it stops being a playbook while
the resource is unchanged.

**The connection is a resource, not a setting.** This is the load-bearing
distinction at the wizard's Connections step: the template can create the
connection object before it has any usable authorization. Existence and
authorization are separate states, and the wizard reports the first while the
designer errors on the second.

## Two connections, two identity models

The reset-password template requires two managed connectors, and they do not
authenticate the same way:

| Connection | Purpose | Auth model | Acts as |
|---|---|---|---|
| `azuresentinel` | Read the incident; write comments and status | Managed identity | **The logic app** |
| `office365` | Send the temporary password to the manager | Delegated OAuth | **A human's mailbox** |

**The Sentinel connection acts as a machine.** Enabling the system-assigned
managed identity creates an Entra service principal representing the logic app;
an Azure role granted to that principal is what makes the connection work.
Sentinel **Reader** suffices to receive and read an incident; **Responder** is
required once the playbook writes back. No password exists and nothing expires —
this is the preferred automation model.

**The Outlook connection acts as a person.** It is an interactive work-or-school
sign-in, and the resulting connection holds a delegated authorization for that
account. Mail is genuinely sent *by* that mailbox. Microsoft documents that such
a connection remains authorized until revoked **even if the user later changes
their sign-in credentials** — so a password change does not close it. It can
still fail if the account is disabled, the mailbox or its licence is removed, the
connection is revoked, Conditional Access blocks it, or the token is invalidated.

That licence dependency is why this lab authorizes as `admin`: `admin` holds
Microsoft 365 E5 and therefore keeps a mailbox through the Office 365 E5 lapse on
2026-08-13 (`POS-017`). An O365-E5-only account would have broken the connection
at that date.

## The traffic path

```
logic app workflow
      |
Microsoft-managed connector infrastructure
      |
Sentinel ARM API  /  Exchange Online
```

The workflow does not call Exchange directly. The hosted connector owns the
endpoint, the OAuth token, request formatting, response parsing, and retry
behaviour. Consequence for this lab: **no VNet, no firewall rule, no networking
to configure at all**, because nothing traverses tenant network space. Private
resource scenarios are the exception and call for a Standard logic app with VNet
integration — not in scope here.

## The Logic app designer, and what it is not

The designer is a **visual editor over the workflow definition** — the same JSON
visible under `Logic app code view`, rendered as cards. One definition, two views;
an edit in either rewrites the other. It is reached at Azure portal → the logic app
→ left navigation → **Development Tools** → **Logic app designer**.

It is **not a monitoring surface and not a readiness check.** Nothing on the canvas
reports whether the playbook has run, can run, or is permitted to run. Run history
is a separate blade. This is why a freshly deployed playbook with one
unauthenticated connection draws a completely clean canvas: the designer renders
the *definition*, and authorization is not part of the definition.

Health lives in the toolbar, not the canvas — three controls, all easy to miss:

| Toolbar control | What it reports |
|---|---|
| **Errors** | Flow Checker: operation errors and warnings, with counts |
| **Connections** | Per-connector credential state, and which actions use each |
| **Code view** | The underlying JSON |

**Visual grammar.** The coloured bar on each card's left edge encodes operation
type: blue shield = Sentinel connector; purple `{x}` = variable operation; green
globe = HTTP; dark grey header = control flow (`For each`, `Condition`). The `+`
circles on connector lines are insert points for new actions, not workflow steps.
Small coloured dot clusters above a card are its `Run after` configuration — which
upstream outcomes permit it to execute.

## Workflow anatomy — the reset-password template

Reading order is top to bottom; indentation means containment.

| Node | Type | Authenticates as |
|---|---|---|
| `Microsoft Sentinel incident` *(trigger)* | `azuresentinel` connector | Managed identity |
| `Initialize variable` | Built-in | — |
| `Set variable - password` | Built-in — random GUID substring | — |
| `Entities - Get Accounts` | `azuresentinel` connector | Managed identity |
| `For each` | Control flow — iterates account entities | — |
| ↳ `HTTP - reset a password` | Built-in HTTP, Graph `PATCH` | Managed identity, Graph audience |
| ↳ `HTTP - get manager` | Built-in HTTP, Graph `GET` | Managed identity, Graph audience |
| ↳ `Condition - is manager available` | Control flow | — |
| ↳↳ *True:* add comment, send email | Sentinel connector + `office365` | Managed identity + **delegated** |
| ↳↳ *False:* add comment | `azuresentinel` connector | Managed identity |

**The password is generated once, outside the loop.** `Initialize variable` and
`Set variable - password` sit at top level, above `For each`. Every account entity
on a single incident therefore receives **the same temporary password**, emailed to
each user's manager separately. Invisible at n=1; a real property of the template
at any larger incident. Placement relative to a loop is semantic, and reading it
off the diagram requires knowing that.

**The condition tests an HTTP status code, not the existence of a manager.** The
expression is `Status code = 200` from `HTTP - get manager`. Any non-200 —
absent manager (404), insufficient Graph permission (403), propagation lag,
throttling (429) — routes identically to the "manager not available" branch, which
adds a Sentinel comment and reports overall **success**. A permissions failure and
an unassigned manager are indistinguishable at every level above the individual
action's own status code.

That implies a permission the template documents nowhere: reading a user's
`manager` attribute is a different Graph operation from resetting a password. An
identity able to `PATCH` the password but not `GET` the manager produces a green
run, no email, and a comment saying no manager was available.

**Credential logging is on by default.** `HTTP - reset a password` ships with
`Secure inputs` and `Secure outputs` both **Off**, so the request body — containing
the generated plaintext password — is retained in run history, and in the workspace
if diagnostic settings are enabled. Rotating the password afterwards invalidates
the credential but does not remove it from the workspace, where it persists for the
retention period.

## What "manager" refers to

The **`manager` attribute on the Entra ID user object** — a directory field on a
user's record pointing at another user. In the Microsoft 365 admin center it is
Users → Active users → *(account)* → Account → **Manager**, and it reads *None
provided* when unset.

**Why the template wants it.** The design intent is to reset a compromised user's
password without telling the compromised user. Emailing a temporary password to the
account that was just compromised hands it to whoever compromised it. Sending it to
the user's manager instead puts it with a human who can verify the person
out-of-band before handing it over. The attribute is how the playbook discovers who
that human is at runtime, so nothing has to be hardcoded per user.

Mechanically, `HTTP - get manager` issues
`GET https://graph.microsoft.com/v1.0/users/{id}/manager`. Graph follows the
relationship and returns the manager's user object, including a mail address, which
the email step then targets.

**Which is why the branch label misleads.** "Manager not available" names only one
of the situations that reach it — see the condition note above. A genuinely
unassigned manager, an identity without permission to read the relationship,
propagation lag on a recently-set attribute, and throttling all produce the same
branch, the same comment, and the same overall success.

**Lab-specific artifact worth stating rather than hiding:** in a three-account
tenant the manager set for testing is `admin`, which is also the mailbox the
`office365` connection authenticates as. The temporary password therefore arrives
in the same inbox that sent it. That is a property of the lab's identity model, not
of the template, and no conclusion about notification routing should be drawn from
it.

**Splunk frame:** a directory lookup resolved at execution time — nearer to
`| lookup users.csv user OUTPUT manager` than to anything fixed in the alert
action's configuration.

## Authorizing is not saving

**The designer does not persist connection changes until `Save` is pressed, and
nothing on screen says so.** After authorizing the Outlook connection every signal
reads complete: the card's error indicator clears, the Flow Checker drops to zero,
the `Connections` flyout loses its red dot, and the parameters pane reads
`Connected to <account>`. The canvas becomes indistinguishable from a saved,
fully-working workflow.

The only indication of unsaved state is the **`Save` button changing from greyed to
enabled** in the designer toolbar — a control the operator is not looking at, at the
moment their attention is on the card that just went green. There is no dirty-state
marker on the canvas, no asterisk in the blade title, and navigating away discards
the binding with no confirmation prompt.

This is the project's recurring failure mode inside the workflow editor itself:
**every affordance reports success for work that has not been committed.** An
operator who authorizes the connection, watches the error clear, and moves on to
the next grant has done nothing — and will later debug a permissions problem that
is actually a persistence problem.

Treat `Save` as the final step of every designer change, and re-open the blade to
confirm the state survived.

## Sentinel validates the launch permission at rule-creation time

**Observed 2026-08-07.** Attaching this playbook to an automation rule failed —
before any incident existed, before any run — with an ARM `BadRequest`:

> *Missing required permissions for Microsoft Sentinel on the playbook resource
> `.../providers/Microsoft.Logic/workflows/<playbook>`*

The rule was not created. This is **not a user error and not a misconfiguration of
the form**: every field was valid, the playbook was selected from Sentinel's own
dropdown, and the missing grant — Microsoft Sentinel Automation Contributor on the
playbook's resource group — is one the operator had deliberately withheld to see
what would happen.

**Three prior expectations died here.** The prediction on record was that the rule
would be created, would fire on an incident, and the playbook would silently never
run. Wrong on all three. Microsoft's own documentation supported two readings —
that a playbook *"can be used only within the subscription to which it belongs,
unless you specifically grant Microsoft Sentinel permissions to the playbook's
resource group"*, and separately that the Sentinel service account *"must have"*
Automation Contributor on that resource group. The first reading is now disproven
for this path: **same subscription and same resource group, still refused.**

**The finding is a contradiction inside a single form.** The `Run Logic Apps
playbook` dropdown offered the playbook — not greyed, no warning — directly above an
inline note reading *"If a playbook appears unavailable, it means Microsoft Sentinel
does not have explicit permissions to run it."* The plain implication is that
available means permitted. It does not. Two permission checks in one blade seconds
apart, disagreeing: the dropdown filters on **trigger type**, while the create path
validates **authorization**.

**The `Manage playbook permissions` link beside that note is documentation, not a
control.** It opens `learn.microsoft.com`. There is no permission grant reachable
from the rule-creation form; the label promises an action verb and delivers reading
material.

**The error is nearly unrecoverable by design of the surfaces, not by intent.** It
appeared as a transient toast that auto-dismissed. The Defender portal's own
notification panel then read *"No notifications to show — new notifications from the
current session will appear here"*, retaining nothing. The message survives only in
the **Azure Activity log**, as an operation named `Update Automation Rules` (not
"Create" — Sentinel writes the whole rules collection), and only in its **JSON**
tab; the summary line names no cause. An operator who blinked has a failed
operation, no rule, and no explanation available anywhere in the portal they were
working in.

**Which principal is missing the grant matters.** Automation Contributor is held by
**Sentinel's own service principal** (`Azure Security Insights`), not by the logic
app's managed identity. It is the only role in the playbook permission model whose
sole purpose is letting automation rules launch playbooks — Microsoft's role table
states it *"isn't used for any other purpose"*, and notes that Sentinel Responder
explicitly *"doesn't allow you to run the playbook."* All three managed-identity and
connection grants can be perfect, as they were here, and the rule still cannot be
created.

## Two grants, two scope models

The two managed-identity grants in this lab are held by **one** service principal
and look superficially alike — same identity, both "assign a role." They are
governed by different systems, and the word *scope* does not mean the same thing
in each.

### Grant 1 — Microsoft Sentinel Responder

| | |
|---|---|
| System | **Azure RBAC** |
| Scope | Resource group |
| Granted at | logic app → Settings → Identity → System assigned → `Azure role assignments` |
| Grants | Read and write on Sentinel incidents — comments, status, ownership |
| Bounded by | The scope chosen. Nothing outside the resource group is reachable |

Azure RBAC scope is a **position in a hierarchy**: management group → subscription
→ resource group → resource. A grant applies at its scope and everything beneath
it. Resource group was chosen here; the narrower alternative was the workspace
resource itself, the wider was the subscription. Because the workspace is the only
Sentinel resource in this resource group, RG scope and workspace scope are
functionally identical in this tenant — and RG is the level the portal steers
toward. `POS-072` placed the analyst's Responder grant at RG scope for the same
reason.

This grant confers **nothing in Entra**. The identity holding it cannot read a user
object, let alone reset a password.

### Grant 2 — Password Administrator

| | |
|---|---|
| System | **Entra directory role**, assigned through PIM |
| Scope | **Directory** — tenant-wide |
| Granted at | `entra.microsoft.com` → Roles and administrators → *(role)* → Assignments |
| Grants | Reset passwords for non-administrators and other Password Administrators |
| Bounded by | The role definition. Not by anything the operator sets |

The asymmetry is the point. Azure RBAC offered four scope levels and the operator
picked one. The directory role offers `Scope type: Directory` and, in principle, an
**administrative unit** — which this tenant does not have. The grant is therefore
tenant-wide by construction, not by choice.

Its limit is the **role definition**, not the scope: *non-administrators and
Password Administrators*. A Global Administrator is out of reach because Microsoft
built that boundary into the role, not because the assignment was narrowed. The
same boundary prevents the playbook resetting a GA's password if an incident ever
names one.

### The comparison

| | Sentinel Responder | Password Administrator |
|---|---|---|
| System | Azure RBAC | Entra directory role |
| Scope model | Hierarchical, four levels | Directory-wide, or admin unit |
| Operator chooses the scope | **Yes** | **No** |
| Bounded by | Where it was placed | What the role can do |
| Expiry offered | None | Permanent, or time-bound |
| Least privilege achieved by | Narrowing the scope | Choosing a narrow role |

**One identity, two audiences.** `management.azure.com` for the Sentinel
connector; `graph.microsoft.com` for the password reset. Granting either confers
nothing in the other, and neither assignment appears in the other's list.

**Consequence for this lab, stated plainly:** the Sentinel grant is genuinely
least-privilege — it reaches one resource group and no further. The Entra grant is
not, and cannot be made so here. It is a **privileged, permanent, tenant-wide role
held by a service principal**, granted through a wizard whose defaults never prompt
reconsideration. That is not a misconfiguration; it is the only shape the tenant
offers.

### Assignment mechanics observed 2026-08-07

- The Entra path routes through **PIM** when P2 is present. The blade subtitle
  reads `Privileged Identity Management | Microsoft Entra roles` and the tabs are
  Eligible / Active / Expired — not the plain "Add assignment" the course
  material describes.
- **Applications are allowed for active assignments only.** A service principal
  cannot hold an eligible assignment, since nothing about it can perform an
  activation. The `Eligible` radio is nevertheless selectable on the Setting tab;
  the restriction is stated on the Membership tab and presumably enforced at
  submit. Not tested.
- **The member picker's tab list is a function of the result set.** Unfiltered it
  shows All / Users / Groups and the managed identity is absent. Searching by
  object ID materialises a fourth tab, **Enterprise applications**, and returns it.
  The absence of a tab therefore proves nothing about what is selectable — read
  twice before concluding a principal type is unsupported.
- **`Permanently assigned` ships checked**, while the greyed `Assignment ends`
  field renders a populated date roughly 180 days out. The checkbox governs — the
  resulting row reads `End time: Permanent` — but the configuring screen implies an
  expiry the confirming screen contradicts.
- **The two systems differ on propagation display.** The Azure RBAC assignment
  rendered immediately. The Entra assignment required an explicit **Refresh**
  before the row appeared. An operator who assigned and glanced would have read an
  empty list as a failed grant.
- **Vocabulary count.** Across the two grants this one object is called: managed
  identity, system-assigned managed identity, Enterprise application, application,
  member, service principal, and — in the Azure RBAC list — the logic app's own
  display name. `Principal name` renders `-`, since a service principal has no UPN.

## Selectable is not runnable

The automation-rule form's playbook dropdown and the permission that lets a playbook
execute are **governed by two different things**, and the form's own inline note
invites the wrong inference.

Microsoft's documentation separates them explicitly. Dropdown **availability** is a
function of subscription membership: a playbook can be used only within the
subscription it belongs to, unless Sentinel is specifically granted permissions to
the playbook's resource group. **Runnability** is a separate matter — Sentinel uses
a *service account* to run playbooks on incidents, and that account needs the
**Microsoft Sentinel Automation Contributor** role on the resource group where the
playbook resides.

The form does not check the second. Its note reads *"If a playbook appears
unavailable, it means Microsoft Sentinel does not have explicit permissions to run
it"* — which reads as though availability implies runnability. A same-subscription
playbook with no Automation Contributor grant is **selectable, attachable, and will
not execute**.

**There is also no in-portal path from this form to fix it.** The inline
`Manage playbook permissions` link opens Microsoft Learn documentation, not a
permissions blade. The grant is made in Azure RBAC on the resource group.

### The full role model

Five roles, and the distinctions between them are finer than "permission to use
playbooks":

| Role | What it permits |
|---|---|
| **Owner** | Grant access to playbooks in the resource group |
| **Microsoft Sentinel Contributor** | Attach a playbook to an analytics or automation rule |
| **Microsoft Sentinel Responder** | Open an incident in order to run a playbook manually — **but not to run it** |
| **Microsoft Sentinel Playbook Operator** | Run a playbook manually |
| **Microsoft Sentinel Automation Contributor** | Allow **automation rules** to run playbooks. Used for nothing else |

Consumption logic apps add their own: **Logic App Contributor** (edit, manage, run —
but not grant access) and **Logic App Operator** (read, enable, disable — not edit).

Two things follow. **Responder does not confer the ability to run a playbook**,
despite being the role granted to the managed identity for incident read/write —
manual execution needs Playbook Operator, and that is a different grant to a
different principal. And **Automation Contributor exists for exactly one purpose**,
is required for that purpose, and appears in neither the template's post-deployment
instructions nor the deployment summary. Granting it requires Owner or User Access
Administrator; running the playbooks additionally requires Logic App Contributor on
the resource group.

## Three permission questions, possibly four

Naming the outbound connections accounts for only part of the model. The
complete set:

1. **Can Sentinel start the playbook?** Sentinel → the logic app trigger. A
   permission held by *Sentinel*, not by the playbook. Absent from the
   template's post-deployment instructions entirely — see `P19-1`.
2. **Can the playbook read or update Sentinel?** Managed identity → workspace.
   Sentinel Reader or Responder.
3. **Can the playbook send email?** The `office365` connection → a mailbox.
   Delegated.
4. **Can the playbook reset a password?** *(PREDICTED, unsettled at the time of
   writing.)* A directory operation, not an Azure resource operation, so it
   cannot be granted from the Identity blade's Azure role assignments. The
   template's instructions name Password Administrator as an Entra directory
   role on the managed identity. Whether the underlying call is a managed-identity
   Graph request, an HTTP action, or something else is **not established** — the
   Connections step lists only managed API connections, so a Graph call would not
   appear there as a third `Microsoft.Web/connections` object. Settled by reading
   the designer in Lab 19 Phase 2.

Note also that **Password Administrator cannot reset an administrator's
password** — by design, and independent of any grant above.

## What each grant actually does

The logic app holds no permissions. **Its managed identity does** — a service
principal created in Entra when the system-assigned identity is enabled. When an
action authenticates as that identity, Entra issues a token and the target service
checks what the identity is allowed to do. Permissions are what let the workflow
*talk to* each service.

| Grant | Actions that need it | Failure without it |
|---|---|---|
| **Sentinel Responder** (Azure RBAC) | `Microsoft Sentinel incident` (trigger), `Entities - Get Accounts`, both `Add comment` actions | Trigger cannot read the incident; entity extraction fails; comments cannot be written |
| **Password Administrator** (Entra directory role) | `HTTP - reset a password` (Graph `PATCH`), `HTTP - get manager` (Graph `GET`) | Graph returns **403**; reset and manager lookup both fail |
| **Office 365 Outlook connection** (delegated) | `Send an email - to manager with password details` | No token, no mailbox — the only error the designer reports on deployment |

**Two refinements that matter more than the table.**

*These grants let the playbook act. None of them lets it start.* Nothing above
gives Sentinel permission to **invoke** the logic app — that is a fourth grant,
held by a different principal entirely. All three can be perfect and the playbook
still never runs.

*A failure here does not look like a failure.* `HTTP - get manager` feeds a
condition testing `Status code = 200`. A missing Password Administrator grant
returns 403, the condition takes the "manager not available" branch, a comment is
written, and the run reports **success**. The permission gap becomes a wrong answer
rather than an error — which is why playbook troubleshooting is permissions
troubleshooting, and why the hard part is noticing rather than fixing.

## Security consequence of a delegated connection

An earlier framing in this project overstated the exposure as *"anyone with write
access to the logic app can now send mail as `admin`."* **Narrowed:** someone who
can modify the workflow *and* use its existing Outlook connection may be able to
add actions that send mail from the authorized mailbox. Write access to the
workflow alone does not automatically bypass connection-resource access controls.

The correction does not soften the operational point. The effective security
boundary is not the workflow but the set:

```
workflow definition + API connection + connection access policy
+ authorized mailbox + Azure RBAC
```

Logic App Contributor, or broad resource-group access, should therefore be
treated as privileged — the workflow can reference powerful existing connections
that its editor never had to authenticate.

**Reuse is conditional, not automatic.** A connection can be referenced by other
workflows when they are permitted to reference it, it is available in the
applicable scope and region, and access policies allow it. It does not become
available to every playbook merely by sharing a resource group. But it can become
shared infrastructure, which is why connection ownership belongs in the record
rather than in someone's memory.

**Teardown.** Deleting a workflow does not delete its connections. A
`Microsoft.Web/connections` object holding a delegated credential for a real
mailbox survives the playbook it was created for. Teardown of this lab must
enumerate both resource types — the single-resource-group `az group delete`
covers it, but a targeted playbook deletion would not.

## Splunk frame

The Sentinel connection is a service account. The Outlook connection is nearer to
a stored user credential in `passwords.conf`: it acts as the person who set it up,
indefinitely, and nothing in the workflow indicates whose mailbox is behind it.
The workflow definition itself is `savedsearches.conf` — declarative text — and
the Logic Apps runtime is the scheduler that reads and dispatches it.

The structural difference from Splunk is that a Splunk alert action runs as the
platform, which already holds credentials. Here the automation engine is a
stranger to the SIEM: Sentinel must be granted permission to *invoke* it, and it
must be separately granted permission to *act*. Neither inherits from the other,
and that is the origin of every grant in this lab.

---

## What the run confirmed — 2026-08-08

Everything above was written from the definition and the portal, before the
playbook had ever executed. One run at 11:57:47 PDT, 5.05 seconds, eleven
actions. What it changed:

**Two principals in one run, verified.** `HTTP - reset a password` and
`HTTP - get manager` both carried
`"authentication": {"type": "ManagedServiceIdentity", "audience": "https://graph.microsoft.com"}`
in their run-history inputs. The mail action ran on the delegated Office 365
connection and the message arrived **From `admin` To `admin`** — the recipient
is the apparent sender. The identity split described above is not a design
choice in the template; the Office 365 connector offers no managed-identity
option, so it is a connector limitation inherited silently (`POS-083`,
row 147).

**The Sentinel-invokes-the-playbook grant is checked before anything runs.**
This document argued that invocation and action are separately granted and
neither inherits from the other. Sharper than that: the invocation grant is
validated at **rule-creation time**. Without `Microsoft Sentinel Automation
Contributor` on the `Azure Security Insights` service principal, the automation
rule does not create — ARM `BadRequest` — so the predicted failure mode of a
rule that fires into silence cannot occur (row 136, `POS-082`).

**And the registration runs the other way.** Trigger history holds a row dated
two days before any incident: `Fired: False`, `Status: Succeeded`. That is the
workflow *subscribing* to Sentinel through the connection, which rides grant 1
(Sentinel Responder, logic app → Sentinel). Invocation rides grant 4
(Automation Contributor, Sentinel → logic app). **A green registration proves
nothing about whether the playbook can be launched** — the two directions have
different principals, different scopes, and different failure surfaces
(row 140).

**The permission granted for the write also bought the read.** Grant 2 exists
so the `PATCH` succeeds. `HTTP - get manager` reads `/users/{upn}/manager` on
the same identity and returned **200** — a directory read nobody granted with
that call in mind. Section *Three permission questions, possibly four* left the
fourth open; the run answers it: there *is* a fourth question, Password
Administrator happens to cover it, and nothing in the grant surface said so.
The consequence is uncomfortable and belongs here rather than in the lab: a
least-privilege improvement to grant 2, made without reading the workflow
definition, would route the manager lookup to the `else` branch and **publish
the plaintext password into the Sentinel incident comment** (row 144,
`POS-081`).

**The template rebuilds an identifier it was handed.** The `SecurityAlert`
entity object carries a complete `UserPrincipalName`. Every Graph URI in this
workflow is built instead as `concat(items('For_each')?['Name'], '@', items('for_each')?['UPNSuffix'])`
— five times, with the casing inconsistency shown, resolving only because the
expression engine is case-insensitive on action-name references. The
reconstruction is the only thing in the workflow that can produce a malformed
URI, and a malformed URI is a non-200, and a non-200 is the leaky branch
(row 152).

**Graph success is not one number.** The condition tests `statusCode = 200`.
The `PATCH` two actions earlier returned **204 No Content**. The workflow
hardcodes a success value that its own sibling action disproves (row 144).

**And the object acquired two more names.** The incident audit trail attributes
the playbook's comment to `Playbook-Reset-Microsoft-Entra-ID-User-Password---Incident-Trigger`,
a string that appears on no other surface, with `Trigger: Manual` where the
three automation rules beside it read `Automated` (row 146). Counting the
Logic Apps **scale-unit host** that fronts the run-history links, the section
above opened at seven vocabularies for one object and the runtime closed at
nine.
