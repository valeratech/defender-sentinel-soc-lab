---
title: Identify, investigate, and remediate security risks by using Defender for Cloud Apps
date: 2026-08-04
artifacts:
  labs: ["16"]
  posture: [POS-066, POS-067, POS-068, POS-069, POS-070]
  divergences: [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108]
  kql: []
corrections:
  - "File monitoring was claimed to have been ON since provisioning. The MDCA Activity log showed all five of its events originate from Lab 14's DLP policy creation on 2026-08-02, including the monitoring toggle — our own action flipped it. Corrected before it reached a file."
  - "The 17:52 mirror-creation timestamp was read as approximately corresponding to DLP sync completion. Withdrawn: the DLP completion alert self-stamps 16:06 local, leaving 1 h 46 m the inference cannot cover. Mechanism reopened, not re-attributed."
  - "Divergence row 49 revised 'Defender local, Azure UTC' to 'Defender renders UTC'. MDCA's Activity log renders LOCAL inside the same portal, so that revision is itself amended to 'Defender UTC except MDCA'."
---

# The Console That Was Already Configured

> Nominally: build a file policy and see what it catches. Actually: discover
> that the previous lab had already provisioned two file policies and a
> monitoring toggle in this console without anyone opening it — and that both
> of them register nothing.

## What was configured

One policy, in `Lab 16`. `Lab16-FilePolicy-SITMatch` (`POS-069`) — Data
Classification Service inspection against Lab 14's three SITs, both pre-seeded
filters removed, **advanced per-SIT settings left exactly as shipped**, no
governance actions. One trigger: the Lab 14 test file re-uploaded bit-identical.

Everything else in the walkthrough was read-only.

## What was established

**Lab 14's DLP policy created objects here.** Two MIP mirror file policies and
the file-monitoring toggle, all at 2026-08-02 17:52 local, in a console that had
not been opened. The MDCA Activity log holds five events and every one is this
(`POS-067`, row 96). First of two cross-product side-effect provisionings in this
repository; `POS-065` is the second, one lab later.

**And the mirrors are hollow.** Both read 0 matches while their source DLP policy
reads 2 (row 105). Nobody configured them, so nobody has cause to check them.

**23 of 26 built-in policies are `[Disabled]`** by the June 15 2025 dynamic
threat detection model migration. Guide 53's claim that a substantial set ships
enabled is stale — the largest accumulator correction of this arc. The policy
list is not a detection inventory (`POS-066`, row 95).

**The connector is silent behind `Connected`.** Three independent surfaces agree
on zero user telemetry, and the leading suspect — unified audit being off — was
eliminated by direct observation with no replacement found (`POS-068`, row 97).

**The calibration result: divergence, mechanism open.** Purview matched the file
at Medium confidence in minutes; MDCA read 0 at +3 h 30 m and +27 h on identical
bytes (`POS-069`, row 106). A zero cannot be resolved into *below threshold*
versus *never scanned*, and the silent connector makes the second live.

Eight further divergences: the default filter scope excluding private files, 325
SITs against Purview's 327, a pagination mis-render in the unfiltered list, MDCA
rendering local time inside a UTC portal, one page correctly labelling both
conventions, a pre-armed alert for disabled enforcement, the Jan 6 2027
retirement cross-confirming Lab 14's banner with its migration button greyed, and
a pre-checked consent box.

## What was corrected

Three, all in the frontmatter. The first two are the substantive ones: a wrong
attribution caught by reading a log, and an inference withdrawn when a
self-stamping timestamp arrived that it could not accommodate. The third amends
an earlier amendment — row 49 has now been revised twice.

This walkthrough also occasioned two `*(pending)*` markers being added to `Lab 15`,
which had declared none. Those are **debt, not corrections**: two facts that were
never observed and were not declared as unobserved. Nothing in Lab 15 is wrong.

## What could not be tested

**Whether the zero is threshold or absence.** Distinguishing them requires either
a working connector or a documented scan SLA, and neither exists. Not *untested*
— **untestable here** without resolving `POS-068` first.

**Why the connector is silent.** The obvious cause was eliminated. Anything
further would be a guess, and the entry records the elimination rather than a
replacement.

**The MDE-side discovery toggle** (Settings → Endpoints → Advanced features) was
never read, so only one direction of the `POS-070` integration is measured.
Tracked as a pending item in `Lab 16`.

**Governance actions.** Present for OneDrive and SharePoint, deliberately
unselected — a governance action would have changed what the measurement was
measuring.

## Cost

Money: none. MDCA is E5-trial-bound. No Defender for Cloud plan was purchased, so
the Cloud security *Prepare tenant* flow stays blocked.

Wall-clock the money did not buy: **27 hours** to establish a zero against no
published SLA — which is why the two-read rule is doing the work here that a
vendor-stated floor did in Lab 15. And an expiry: this entire surface retires
**2027-01-06**, with the migration path Microsoft names not yet shipped.
