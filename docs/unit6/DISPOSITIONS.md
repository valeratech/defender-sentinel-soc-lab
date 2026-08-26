# Unit 6 — Stage-2 disposition records

Records below follow the project disposition-register shape: ID, DISPOSITION,
SCOPE MEASURED, SCOPE NOT MEASURED, EVIDENCE, MEASUREMENT / DECISION DATE,
REOPENING TRIGGER. Records are append-only. Effective state is the latest
valid transition for a stable ID. A challenge outside SCOPE MEASURED files a
new scoped item; a challenge inside it petitions to reopen and requires an
explicit Reviewer ruling. A scope expansion never silently converts a closed
record back to OPEN.

Records marked PROPOSED are Builder-drafted for Reviewer adoption and carry no
authority until the Reviewer adopts them.

---

## U6-AUTH-001 — Frozen byte-bearing authority for fresh activation  (PROPOSED)

**DISPOSITION**

FRESH ACTIVATION / INTEGRATION VERIFICATION
NOT DEMONSTRABLE WITH CURRENTLY AVAILABLE AUTHORITATIVE BYTES.

This is not a finding that the artifacts never existed or are permanently
destroyed. Historical Reviewer evidence establishes the opposite. It is a
finding that the exact bytes required to open the runtime qualification gate
are unavailable from every governed storage location accessible to Builder and
Reviewer after targeted recovery, and that activation therefore remains
fail-closed and must not be fabricated.

**AUTHORITY CENSUS — classified by role** (Reviewer Stage-2 Exchange-2 item 1)

These artifacts do not all play the same role. Runtime qualification
(`u6/runtime_bind.py` A1/A2/A7) consumes three; the eight detector/engine
members are consumed downstream by `u6/engine_bind.py` after qualification
succeeds; `.gitleaks.toml` is repository configuration; the predecessor
architecture is frozen verification/architecture evidence important to
Stage-2 acceptance but not an executable runtime-qualification member.

```
Fresh Stage-2 activation / integration authority census

Runtime-qualification byte authority     3 absent
Frozen detector/engine members            8 absent
Frozen predecessor architecture           1 absent
Repository gitleaks configuration         1 present

Total census                              13
Present                                    1
Unavailable                               12
```

| class | artifact | expected SHA-256 | status |
|---|---|---|---|
| engine | `msgctl/serialize.py` | `0bfb9cd616010069a10bf094544211de1bce809777e5cd79df0d2a2dbafa20b0` | ABSENT |
| engine | `msgctl/crypto.py` | `ef2fe0662728b243a129b2374eeaf76442676ae43e1e0600366ba23daa170d02` | ABSENT |
| engine | `msgctl/runtime.py` | `8db5da095feeb00b7d3d1074eb5f76197f8a02fd082a7536352d3afb13635a6e` | ABSENT |
| engine | `msgctl/adapter.py` | `03950e3e7b9bae731c6d2489bf196e70701c6f7158c9d5cc2977304ab65ff800` | ABSENT |
| engine | `msgctl/wordlist.py` | `15a1d57e7b308c04698497fb963b6bc20642e69d64d901cd9ce4a85bbac733f8` | ABSENT |
| engine | `msgctl/structural.py` | `c66dcbccccb58f8d696d144ba244279017ebe37432db8e32b768fdb26263285d` | ABSENT |
| engine | `msgctl/identity.py` | `278b8940d4a5bcb06bd43c7940f50b326f5aa3f1c7a35db2ff627f87cc0207d2` | ABSENT |
| engine | `msgctl/baseline.py` | `7f26c4f546aa73481213b5b1724c20a31bd179a1045b028e2502c7fa55090191` | ABSENT |
| runtime-qualification (A7) | `msgctl/u6runtime.py` | `35ee40c3b9d794881f45adbbec20e7e5832c0ec9c533de02f107e15fe494a21a` | ABSENT |
| runtime-qualification (A1) | environment declaration (identity-addressed, no filename asserted) | `009a5ec831dc2dd85865ce96d9deb8aef739777f3d233680d3b960b079538e33` | ABSENT |
| runtime-qualification (A2) | dependency manifest (identity-addressed, no filename asserted) | `46e6c9e79325bb29cc227214fc37b3bfd846d15aa98417038fccf60b4c795eb5` | ABSENT |
| verification/architecture evidence | frozen predecessor architecture | `179747cf8f1c3c1b0e045d1eabb7f10103b9bce7525ffa47fba6fc6fe7a040f9` | ABSENT |
| repository configuration | `.gitleaks.toml` | `c72f1400e16a744704f268350e5a810aa77cd2010bee1ae33d15387b42b12556` | PRESENT (governed base) |

Also unrecovered on the Reviewer side: Gate-A, Gate-B and Gate-C package
bytes and the exact frozen engine source package.

**CONSEQUENCE FOR THE GOVERNED SEQUENCE.** Step 25 (`25-place-engine.sh`)
requires the nine `msgctl/*` members of `u6/ENGINE-IDENTITIES.txt`; step 30
requires the three runtime-qualification inputs. With the byte-bearing
package unavailable, the governed step-25/activation sequence cannot advance.
That is a statement about the sequence, not a claim that any single class is
"required for qualification" in isolation.

**SCOPE MEASURED**

- Builder-side recovery: every regular file in every readable location of the
  Builder workspace (uploads, governed base snapshot, delivered overlay,
  transcripts, outputs), with every archive recursively expanded — 264 files —
  hashed and compared against all thirteen identities above. Result: 1
  present, 12 absent.
- Reviewer-side recovery: targeted search of Reviewer storage (File Library).
  Result: identities, manifests, rulings, and historical procedure evidence
  recovered; byte-bearing transports not recovered.
- Fail-closed behaviour of the integration in the absence of authority,
  measured at both hook entry points on the committed bytes:
  `U6_RETURN v1 KIND=L1 STATUS=ERROR CODE=ENV_AUTHORITY_ABSENT RC=2` and
  `U6_RETURN v1 KIND=L2 STATUS=ERROR CODE=ENV_AUTHORITY_ABSENT RC=2`.
  `u6/runtime_bind.py` steps A1–A7 refuse before any dependency is executed.
- The committed integration at `5f19815d291279d351292a80ece81a39fbaf846c`:
  62/62 exact bytes and 62/62 exact Git modes against tarball
  `5e0c7aaf2bb5642ea63cad3bba00778d563875610bbd562d16ef1bb1dcdb26cc`;
  battery 64/64; falsification 40/40 killed, 0 survived, 0 harness defect,
  0 skip, 0 void; gitleaks 0 findings; pre-commit clean; P10-01 and P10-02
  closed by execution control.

**SCOPE NOT MEASURED**

- Fresh effective Unit-6 qualification against actual frozen authority.
- Phase-2 diagnostic (step 45) and fresh L2 adjudication (step 50).
- Reviewer acceptance and binding of a measured L2 baseline (step 55).
- L1 / L2 activation (`core.hooksPath`) and their effective verification.
- L3 CI wiring and execution.
- Current-state positive control, missing-relationship negative, and
  superseded-authority negative.
- Whether any storage not accessible to Builder or Reviewer holds the bytes.

None of the above is claimed. In particular: **no fresh L1/L2/L3 activation
or integration verification has been demonstrated.**

**EVIDENCE THAT THE ARTIFACTS HISTORICALLY EXISTED**

- The frozen successor transfer records the predecessor architecture at
  `179747cf…040f9` as co-delivered.
- The Reviewer addendum records the successor package containing the accepted
  Rev-4.2 package and frozen records.
- The recovered frozen candidate manifest proves `u6runtime.py` existed at
  exactly `35ee40c3…4a21a`.
- The accepted procedure record describes the three frozen gate packages it
  consumed.
- `u6/ENGINE-IDENTITIES.txt` and `u6/RUNTIME-IDENTITIES.txt` carry the
  identities as Reviewer-verified immutable facts (transfer §8, §9; Reviewer
  Pass-7/9).
- Current-state authority records that an effective U6 composition had
  previously been established and was consistent with the frozen
  composition, at a time when repository L1/L2/L3 integration was still
  unbuilt.

**DISTINCTION PRESERVED**

Historical effective U6 qualification (recorded, consistent with the frozen
composition) is a preserved measurement. It is not transferable to a *new*
repository integration execution: expected digests and historical prose are
identities, not bytes, and a checker must never substitute expected literals
for effective state. The present integration binds by identity and refuses
until bytes matching those identities are placed under `msgctl/`.

**FAIL-CLOSED BEHAVIOUR**

Every governed entry point returns `STATUS=ERROR` with an authority-absent
code. No git process, private-state access, or detector call occurs before
qualification succeeds. Activation is refused, not approximated, and no
authority is reconstructed from prose.

**MEASUREMENT / DECISION DATE**  2026-08-26

**REOPENING TRIGGER**  Exact verified byte-bearing authority becomes
available. Reopening requires the recovered bytes to hash to the identities
above before any governed step runs; identity match is verified by the
integration itself (`u6/runtime_bind.py` A1–A7, `u6/orchestrate/25-place-engine.sh`)
and never asserted from a transfer document.

---

## U6-ORCH-040 — Dormant `40-commit.sh` broad-staging defect  (PROPOSED)

**DISPOSITION**  CORRECTED. Predecessor behaviour NOT AUTHORIZED FOR OPERATOR
USE; prohibition made durable in the Builder battery and the falsification
harness.

**SCOPE MEASURED**

- Defect: the predecessor script staged with `git add -A`. Measured sweeping
  an unrelated uncommitted evidence note into the governed commit: 63 paths
  staged where 62 were governed.
- Correction: the script stages exactly the paths of a caller-supplied
  manifest via per-path `git add --`, refuses on non-empty index, absent path,
  glob, traversal, empty or absent message file, or any staged-set inequality,
  and takes the commit message from a file rather than an embedded heredoc
  (the predecessor's embedded message asserted a CI job the committed state
  does not wire).
- Positive control with unrelated dirt present: `staged=2 exact_match=YES`,
  committed set equals manifest, unrelated file remains untracked.
- Six negative controls, each refusing and leaving index and history
  untouched.
- Durability: battery test
  `test_commit_step_stages_only_an_explicit_manifest` (source assertions plus
  an execution control) and falsification mutant M41 (reintroduces
  `git add -A`), which the test kills.

**SCOPE NOT MEASURED**  Behaviour under an activated L1 hook (the commit path
through `commit-msg`), which cannot be exercised until U6-AUTH-001 reopens.

**EVIDENCE**  This commit; `u6/orchestrate/README.md` row 40; battery and
falsification results attached to this commit's CI run.

**MEASUREMENT / DECISION DATE**  2026-08-26

**REOPENING TRIGGER**  NONE for the broad-staging defect: the prohibited
construct is absent from the script and its reintroduction is a killed mutant.
Basis for permanence: the control is exercised on every battery run.

---

## U6-MSG-001 — Published commit-message policy surface  (PROPOSED)

**DISPOSITION**  Prior state `COMMIT_MESSAGE_POLICY=NOT_MEASURED`. A local,
private measurement instrument (`scripts/measure-message-policy.sh`) is
provided; the measured result is recorded by the Reviewer from the operator's
bounded output, not by the Builder.

**SCOPE MEASURED**  The instrument's exposure contract: stdout carries counts
and commit SHAs only; the detail sink is written outside the repository at
mode 0600 and records term indices, never terms or message text; it refuses
if the wordlist is absent or tracked; it performs no repository write and no
history rewrite. Case semantics follow the wordlist admission policy
(all-lowercase entries case-insensitive, entries carrying uppercase exact).

**SCOPE NOT MEASURED**  The governed verdict. The frozen wordlist detector
(`msgctl/wordlist.py`, `15a1d57e…`) is absent, so this instrument is a
measurement, not an L1/L2 policy result. The instrument does not implement the
frozen structural rules.

**MEASUREMENT / DECISION DATE**  Instrument 2026-08-26; measurement date to
be recorded by the Reviewer on receipt of the operator's bounded output.

**REOPENING TRIGGER**  U6-AUTH-001 reopens (governed detector becomes
available), or the wordlist changes.

---

## U6-TEST-010 — Step-10 shadow-git control assumed an unqualified environment  (PROPOSED)

**DISPOSITION**  CORRECTED. The control now branches on the measured identity
of `/usr/bin/git` against step 10's own bound literal; the load-bearing
assertion (a PATH-shadowed git is never executed) is unconditional in both
branches.

**SCOPE MEASURED**

- Defect: `test_step10_refuses_shadow_git_without_executing_it` in the
  `5f19815d…` checkpoint asserted `GIT_UNQUALIFIED` / `REFUSED_UNQUALIFIED_GIT`
  unconditionally, on the assumption that the test environment's
  `/usr/bin/git` is not the qualified object. On the operator machine, where
  `/usr/bin/git` IS `f54a87f6…` / 2.54.0, step 10 correctly reported
  `GIT_QUALIFIED path=/usr/bin/git` and proceeded by absolute path; the test
  failed while its load-bearing assertion (shadow marker absent) passed.
  Measured at Stage-2 Exchange-4 execution, 2026-08-26: the locked block
  halted at `BATTERY_FAILED` after extraction and staging; the tree was
  unwound to clean state; nothing was committed or pushed.
- Consequence for prior evidence: the 64/64 battery result attached to
  `5f19815d…` (and the 65/65 and 68/68 results for the Exchange-1 and
  Exchange-3 deltas) was environment-conditional. It could pass only where
  the qualified git is absent — the Builder and Reviewer containers — and
  could not pass on the operator machine as written. The other 63 tests are
  not affected: every other `*_UNQUALIFIED` assertion drives the labelled
  double with a deliberately constructed environment rather than assuming
  the ambient one (census of the battery source, 2026-08-26).
- Correction: unqualified branch executed in the Builder container (PASS);
  qualified branch assertions replayed against the operator's actual step-10
  stdout captured in the failure traceback (PASS); step-10 mutants M38 and
  M39 remain killed.

**SCOPE NOT MEASURED**  Execution of the qualified branch by the battery
itself on the operator machine. That occurs when the corrected delta's
battery runs inside the locked operator block, which precedes commit; a
second failure halts before commit exactly as the first did.

**MEASUREMENT / DECISION DATE**  2026-08-26

**REOPENING TRIGGER**  NONE for this assumption: the branch is selected by
measurement, not assumed. Basis for permanence: the control is exercised on
every battery run in both environment classes. Builder notes for the record
that the container's unqualified git was flagged as an evidence limitation in
every prior handoff without this test's inverted assumption being connected
to it; that is a Builder miss.
