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

## 5. Definition of done

A lab is not `✅` until:

- [ ] §2 decisions table has no blank rationale
- [ ] §3 state table matches the live environment
- [ ] §4 validation records a **result**, not an expectation
- [ ] §5 evidence is sanitized per `SANITIZATION.md`
- [ ] §6 records what broke, or explicitly states that nothing did
- [ ] §7 says something that is not in the vendor's documentation
- [ ] No `*(pending)*` markers remain

`scripts/open-items.py` reports outstanding markers, and CI fails if the report drifts from the writeups. Documentation debt is tracked, not remembered.

## 6. Status vocabulary

| Marker | Meaning |
|---|---|
| 🔜 | Not built |
| 🔨 | Built, documentation in progress — **the work is done, the writeup is not** |
| ✅ | Built, documented, validated |
| `*(pending)*` | This fact is unknown to the writeup, not unknown to the environment |

The gap between 🔨 and ✅ is load-bearing. Marking work complete before it is documented is a claim the repository cannot support.
