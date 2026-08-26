# Builder test battery — not a replacement control architecture

`test_u6.py` (64 assertions) and `falsify.py` (40 mutants) are the **Builder
test battery** for the operational integration. They are construction
evidence. They do not add governance controls and do not replace the frozen
control identities, which remain as ruled:

```text
C1  C2  C3  C4  C5     N4     N-empty     N-privacy
```

plus the Reviewer-required current-state relationship controls:

```text
CS-POS   valid current state passes
CS-NEG1  required current-state relationship removed -> fails
CS-NEG2  superseded state in the current-authority position -> fails
```

The frozen definitions of C1–C5 / N4 / N-empty / N-privacy live in the
predecessor architecture §§8–9 (`179747cf…040f9`), which is not in the
successor bundle. The table below lists which battery tests exercise the
same *subject* as each identity so the Reviewer can map them; it is not a
Builder claim that any test *is* the frozen control.

| frozen identity | subject | battery tests touching the subject |
|---|---|---|
| N-empty | empty ref-update stream is not a failure | `TestL2.test_empty_stream_not_run` (M03) |
| N-privacy | private material unreachable from CI/L3; private sink never followed through a symlink | `TestL3.*`, `check_l3_isolation.py`, `TestRunLog.*` (M05, M16, M20, M21, M24) |
| N4 | (definition in frozen §§8–9) | not mapped |
| C1–C5 | (definitions in frozen §§8–9) | not mapped |
| CS-POS | | `TestCurrentState.test_positive_valid_current_state` |
| CS-NEG1 | | `test_negative_required_relationship_removed`, `test_negative_authority_binding_removed`, `test_shipped_tree_is_unbound_and_fails_closed` (M09, M17) |
| CS-NEG2 | | `test_negative_superseded_state_in_current_position`, `..._with_forged_status`, `test_negative_orphan_superseded_revision` (M08) |

Run:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest u6.controls.test_u6 -v
PYTHONDONTWRITEBYTECODE=1 python3 u6/controls/falsify.py
PYTHONDONTWRITEBYTECODE=1 python3 u6/controls/check_l3_isolation.py
```

`PYTHONDONTWRITEBYTECODE=1` is not cosmetic: `gitleaks dir` reads gitignored
`__pycache__`, and a `.pyc` of this battery produced the `upn-email` finding
recorded in the Pass-4 gates transcript (Reviewer Pass-5 P5-05). The
publication-safety evidence is taken on a tree with no bytecode present.
