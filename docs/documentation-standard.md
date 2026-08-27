# Documentation Standard

The rules every lab writeup and detection spec in this repository follows.

---

## 1. Evidence rules

**Never assert what was not observed.** Unknowns are marked `*(pending)*` rather than inferred. A plausible reconstruction is indistinguishable from a fabrication once committed, and this repository's worth depends on a reader being able to trust what it says.

**Vendor expectations are not results.** "Propagation takes 1–2 hours" is a documented expectation, recorded as something to measure. A measured number replaces it. An unmeasured one stays unmeasured and says so.

**Configuration set is not configuration verified.** Setting a value and confirming the platform accepted it are two events. §4 records which one happened.

**Isolate variables or say you didn't.** Where two changes were made and either could explain the outcome, the writeup says so rather than picking the tidier story.

## 2. Decision rules

**Every decision names a rejected alternative.** A choice with no alternative is a default. Defaults are worth recording — silently inheriting one is itself a finding — but they are labelled as defaults, not dressed up as decisions.

**Lab-only weakenings are named.** Where a setting is loosened for convenience, the production answer is stated beside it, along with what the weakening actually costs. Unmarked, it reads as ignorance. Marked, it reads as judgment.

**Rationale is the artifact.** The click path is not. Portal navigation is vendor-documented, version-fragile, and reproducible by anyone; why a given value was chosen is not.

## 3. Detection rules

No rule ships without a hypothesis, a validation method, a tuning decision, and a named blind spot.

A rule that has never fired on a known-true event is **unvalidated** and does not count as coverage. `docs/attack-coverage.md` enforces this distinction rather than averaging it away.

## 4. Numbering

Labs are numbered in **actual build order**, not exam-blueprint order. Dependencies are real; domains are a filing system. Where the two disagree, the build wins.

Numbers are mutable until a lab is published, and stable afterward. Links are cheaper to keep than to fix.

### 4.1 Four counters, none nested inside another

This repository consumes a course and produces its own artifacts. That is two numbering systems meeting, and they have been conflated at three separate handoffs — always in the same direction, always by inferring a hierarchy that does not exist. The rule is written here rather than in a transfer document because transfer documents are regenerated and this survives in the tree.

| Counter | Labels | Ordered by |
|---|---|---|
| **G{n}** | One course lecture. The handle used when a lecture is discussed, because knowledge-base guide files are renamed from their content | Course order |
| **Lab {n}** | One build-measure-commit unit **in this repository**. Exists only where a guide changed portal state | Build order (§4) |
| **`POS-{n}` / divergence rows** | Findings. Continuous across the whole project, never reset, never renumbered | Discovery order |
| **Incident {n}** | A tenant object, assigned by Defender/Sentinel. **Not ours, not the course's** — the only counter this repo neither sets nor controls | Tenant creation order |

Prediction-ID prefixes (`P26-1`, `P104-1`, and family) are frozen historical identifiers: they echo numbering carried over from the course source material and are never renumbered.

**Incident IDs collide with lab numbers, and the collision has already misfired.** Lab 20 §6 records it: a run sheet step named its target as "a Lab 19 incident" rather than by ID, and the first navigation landed on **incident 19** — which is Lab 17's Responder boundary-test artifact (`POS-074`). Lab 19's incident is **24**. Both exist, both are real, and the wrong one carries the matching number.

Incident IDs are the most dangerous of the four because they are the only counter that **renders in a portal**, where a misread aims a measurement at the wrong evidence rather than merely producing a wrong sentence. **Always name a tenant object by its ID, never by the lab that produced it** — and grep the repo for the ID before navigating.

## 5. Definition of done

The requirements below are **semantic**. They say what a finished lab must contain,
not which section number must contain it.

That distinction is deliberate and was arrived at by measurement. This standard
previously keyed the checklist to fixed section identities — §2 decisions, §3 state,
§4 validation, and so on. Twelve of thirteen published labs put Predictions at §2 and
moved the rest down; the phase-structured labs (21–24) organise §4–§7 by measurement
phase; Labs 25 and 26 use a compact six-section form. Measured on the Stage-3 governed
baseline `291f86fb`: 83 of the 105 `Lab NN §N` cross-references then in the tree
pointed into those labs. That is a frozen measurement, not a live count — the number
moves as references are added, and the argument does not depend on its current value. Enforcing the old fixed
numbering would have meant rewriting thirteen published writeups and invalidating
those references to preserve a rule the labs had already outgrown. The structure was
not drifting; the standard was stale.

A lab is not `✅` until it contains, **under whatever heading it uses**:

- [ ] a decisions record covering every **material discretionary** choice the lab
      introduced: the option chosen, the genuine rejected alternative **where one
      existed**, and the rationale. A portal constraint, a source-guide requirement,
      or any other imposed condition is not a discretionary decision and is not given
      an invented alternative — recording it as a constraint is the accurate move
- [ ] a state or build record matching the live environment
- [ ] a validation record carrying a **result**, not an expectation
- [ ] all evidence it does carry sanitized per `SANITIZATION.md` — a property of the
      evidence, not a demand for a section named Evidence
- [ ] every failure, withdrawal, method error, or broken execution path **actually
      encountered** recorded with its disposition. A lab that encountered none owes no
      statement to that effect: asserting an absence that was never itself measured is
      the error §1 exists to prevent
- [ ] an analysis or findings record saying something that is not in the vendor's
      documentation
- [ ] where predictions were registered, their disposition — closed, withdrawn, or
      unmeasured — for each one
- [ ] No `*(pending)*` markers remain

A section may carry more than one requirement, and a requirement may be split across
sections, provided each is discharged somewhere and can be found.

### 5.0 Legitimate lab structures

These are descriptions of what published labs do, not a permitted-list that closes.
A new shape is legitimate when it discharges §5; the point of naming these is that a
reader meeting an unfamiliar lab can tell which family it belongs to.

| Family | Labs | Shape |
|---|---|---|
| **Build-order eight-section** | 01–06, 09–13 | The template as written: Objective, Design Decisions, Build, Validation, Evidence, Failures & Fixes, Analysis, References |
| **Topic-structured** | 00, 07, 08 | Sections named for the thing examined rather than the phase. Lab 00 opens at §0 Provenance; 07 and 08 carry a cost or connector-tier section as the analytical through-line |
| **Prediction-led** | 14–20 | Predictions registered at §2, before build, with falsifiers. Everything after shifts by one |
| **Phase-structured** | 21–24 | Prediction-led, with §4 onward organised by measurement phase (Phase A, B, C) rather than by document role. Findings and teardown carry their own sections |
| **Compact measurement** | 25, 26 | Six sections: Objective, Predictions, Build, Measurements, Teardown, **What this lab does not establish**. Validation and analysis live inside Measurements |

The last of those is load-bearing rather than an abbreviation. Ending on *what this
lab does not establish* records the boundary of the measurement instead of implying
conclusions the lab never reached, which is §1's rule applied to the shape of the
document. Any lab may adopt it.

`labs/_TEMPLATE.md` remains the **default** starting structure. It is where a lab
begins, not proof that a finished lab must look identical.

### 5.1 Executive summary — by request, not by default

A lab README may carry an unnumbered **Executive summary** section between the
thesis blockquote and `§1 Objective`. It is a plain-language account of what the
lab did and found, written for a reader returning cold rather than for an
analyst reading for precision.

**It is optional and exceptional.** The thesis blockquote is the default summary
surface and remains sufficient for almost every lab. An executive summary is
warranted only where a lab's density would otherwise make its own record hard to
re-enter — multiple independent investigations in one lab, a result that depends
on several interacting measurements, or a finding whose significance is not
apparent from the numbers alone.

Rules:

- The section states, in its first line, that most labs do not have one.
- It ends with a short **"Why this lab has one"** subsection giving the specific
  reason. A summary without that justification is a convention forming by
  accident.
- It introduces no findings, numbers, or claims absent from the lab body. It is
  a re-presentation, never a source.
- It is **not** backfilled into existing labs and does not become part of §5's
  definition of done.

As of this writing, **Lab 21 is the only lab carrying one.**

### 5.2 Cross-references are lab-local

`Lab 22 §8` means the section numbered 8 **in that lab**, not a globally fixed role.
A reference resolves against the target lab's own headings. This is why renumbering a
published lab is expensive and why the numbers are stable after publication (§4).

`scripts/open-items.py` reports outstanding markers, and CI fails if the report drifts from the writeups. Documentation debt is tracked, not remembered.

## 6. Status vocabulary

| Marker | Meaning |
|---|---|
| 🔜 | Not built |
| 🔨 | Built, documentation in progress — **the work is done, the writeup is not** |
| ✅ | Built, documented, validated |
| `*(pending)*` | This fact is unknown to the writeup, not unknown to the environment |

The gap between 🔨 and ✅ is load-bearing. Marking work complete before it is documented is a claim the repository cannot support.
