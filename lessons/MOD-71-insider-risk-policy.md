---
module: 71
title: Generating an insider risk policy
section: Respond to alerts and incidents in Microsoft Defender XDR
verdict: lab
date: 2026-08-03
artifacts:
  labs: ["15"]
  posture: [POS-063, POS-064, POS-065]
  divergences: [83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94]
  kql: []
corrections:
  - "The policy-health `last updated` stamp reading 9:08 and then 9:09 across two near-simultaneous screenshots was nearly written up as a live-recomputing field. A read the next day showed an ordinary refresh (04:38); the delta was two reads spanning a minute. Recorded as unremarkable rather than as a finding."
  - "P15-1's text did not survive a session transfer. Reconstructing it after the outcome was known would have produced an unfalsifiable prediction; it is withdrawn from the record instead."
---

# Module 71 — A Trigger the Selector Accepts and the Runtime Ignores

> Nominally: create an insider risk policy. Actually: discover that IRM's
> first-class triggering event can be wired to a DLP policy that cannot satisfy
> it, saved, reported `Healthy`, and left to produce nothing for 49 hours
> without any surface saying why.

## What was configured

Three things, all in `Lab 15`.

The standing GA was added to the full **Insider Risk Management** role group at
07:50 (`POS-061`, amended in Lab 14's commit) — and two minutes later an
automated Microsoft principal assigned an **Entra directory role** nobody
requested (`POS-065`).

Org-level indicators were enabled through the wizard's forced dialog, accepting
Microsoft's pre-selected recommended set verbatim — 45 of 103, from a baseline of
**all 103 off** (`POS-063`).

The policy itself: Data leaks template, all users, Lab 14's three SITs as
priority content, triggering event scoped to `Lab14-USFinancial-Simulation` only
(`POS-064`).

## What was established

**A simulation-mode DLP match does not function as an IRM triggering event** —
measured across three independent surfaces at +25 h and +49 h, the latter double
Microsoft's own stated floor. The precondition provably occurred: Lab 14's report
carries the trigger email as a match at Aug 3 4:11 PM UTC. Nothing downstream
followed, and nothing reported a reason. Four candidate blockers, none
distinguishable from any surface (`Lab 15` §5, rows 83–84).

**IRM ships with every indicator off** — the exact inverse of DLP's seven
blanket-enabled locations two labs earlier. Two Purview solutions, one
provisioning window, opposite defaults (`POS-063`).

**The health evaluator reports what it can enumerate, not what is broken.** Live
across two days, it flagged an unconfigured badge-reader connector on every pass
and never mentioned zero users in scope or an unfirable trigger (row 87).

**One screen, two contradictory scope claims** — grid `Users in scope: 0` against
a flyout congratulating the operator for covering all active users (row 83).

**Second cross-product side-effect provisioning in this repository** — a Purview
role-group add producing an Entra directory-role assignment outside PIM, notified
by neither of the two products involved (row 93, `POS-065`). Lab 16 holds the
first instance.

Nine further divergences: the unenforced High-severity requirement, three
disagreeing indicator taxonomies, IRM's doubled latency warning against DLP's
silence, a stale banner outliving its condition, `Select all` meaning *all
selectable*, a pay-as-you-go footnote on the default trigger path, a guide
undercounting the role-group family by two, a settings summary omitting the
triggering event, and two notification subsystems behind one label.

## What was corrected

Both entries are in the frontmatter. Neither changed a finding; both changed what
this repository is willing to claim.

## What could not be tested

**Which blocker is operative.** Four candidates, and the product exposes no
surface that distinguishes them — this is a limit of the platform, not of the
lab. Isolating (a) would require re-running against an enforcement-mode DLP
policy with High-severity incident reports configured, which is a second lab and
was not built.

**Whether `Users in scope` ever populates.** Zero at 49 h is structural, but the
mechanism that would populate it — Analytics, or a scored user population — was
left off by decision.

**Role separation.** `POS-002` is still open, so every grant in this lab went to
the same identity that made it. IRM's entire premise is separation between the
operator who configures and the analyst who investigates, and a single-identity
tenant cannot exercise it. Not *untested* — **untestable here**.

## Cost

Money: none. IRM is E5-trial-bound and the one metered path — exfiltration
trigger activities (row 90) — was not taken.

Wall-clock the money did not buy: **49 hours** of observation to establish a
null, against a vendor-stated floor of 24 that bounded nothing, because the
blocker was never temporal. Analytics would have supplied the greyed-out
recommended threshold at a cost of a 48 h first scan; it stays off.
