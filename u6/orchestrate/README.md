# Operator orchestration — Unit 6 / Stage 2

Ordered scripts. NONE is live. A script becomes live only when a message
carries ⚠️ after Builder AND Reviewer have locked that exact action.
Every script: repository guard first — `remote_guard`, which reads the remote
URL textually from `.git/config` and does **not** execute git, because an
unqualified or shadowed git must not run before the runtime contract has
established authority (Reviewer Pass-10 P10-02), `( … )` subshell wrapping recommended when pasted, no bare
`exit` reachable from an operator paste, structured output lines only.
Governed children are referenced by exact frozen identity and are never
modified or repackaged by the Builder.

The order is **executable from the admitted 137-file base** (Reviewer Pass-7
P7-02): nothing before step 20 may reference `u6/`, because `u6/` does not
exist until step 20 installs it, and nothing before step 25 may require a
frozen member under `msgctl/`.

| # | script | needs | class | mutates | output |
|---|--------|-------|-------|---------|--------|
| 00 | `00-preflight.sh` | base only (manifest path optional) | read-only | nothing | pasteable |
| 10 | `10-live-head-compat.sh` | base only | read-only | nothing | pasteable |
| 20 | `20-apply-candidate.sh` | overlay tarball | mutating (working tree) | extracts overlay, sets hooks path; stages/commits nothing | pasteable |
| 25 | `25-place-engine.sh` | 20 (`u6/ENGINE-IDENTITIES.txt`) + Reviewer-verified exact frozen package | mutating (working tree) | stages **outside the repository**, verifies all 9 `msgctl/*` members, then places; never deletes | pasteable |
| 30 | `30-u6-runtime-qualify.sh` | 20 + 25 (`msgctl/u6runtime.py`) | governed run | nothing; the frozen implementation derives EFFECTIVE runtime state | 🚨 log local; one U6_RETURN line with STATE pasteable |
| — | Reviewer binds `docs/current-state/CURRENT.txt` + revision (Reviewer-owned) | | | | |
| 35 | `35-verify.sh` | 20, 25, 30, bound state | verification only | nothing; failure evidence left in place | pasteable |
| 40 | `40-commit.sh` | 35 ok=1 + explicit path manifest + message file | mutating (index + one local commit) | stages **exactly** the manifest paths, refuses otherwise; broad `git add -A` is NOT AUTHORIZED (Stage-2 ruling) | pasteable |
| 45 | `45-phase2-diag.sh` | frozen diagnostic + `<rundir>` | governed run | reads private root | 🚨 log local; one U6_RETURN line with STATE pasteable |
| 50 | `50-adjudication.sh` | frozen wrapper | governed run | private processing | 🚨 log local; one U6_RETURN line pasteable |
| — | Reviewer accepts the current L2 expected baseline (Reviewer-owned ruling) | | | | |
| 55 | `55-commit-baseline.sh` | accepted artifact + its identity | mutating (index + one local commit) | commits `u6/committed-baseline` | pasteable |
| 60 | `60-l2-verify.sh` | 55 | verification only | nothing (dry-run push exercises L2) | pasteable (U6_RETURN line) |
| 70 | `70-push.sh` | 60 PASS | mutating (remote) | final governed push through L2 | pasteable |

Negative control, not a step: `N-prebaseline-push.sh` shows that a push
before 55 is refused with `ERROR/BASELINE_UNRESOLVED` (dry-run).

Dependency facts worth stating once: step 25 places the **nine** `msgctl/*`
members named in `u6/ENGINE-IDENTITIES.txt` — the eight engine modules and
`u6runtime.py` (`35ee40c3…`). The Gate-A environment declaration (`009a5ec8…`)
and the dependency manifest (`46e6c9e7…`) belong in the same exact frozen
package but are **not** manifest rows, because their digests are recovered
authority while their filenames are not; `u6/runtime_bind.py` finds them by
identity anywhere under `msgctl/`. Until all eleven artifacts are present at
their identities, qualification refuses and every governed entry point returns
ERROR. No push precedes the Phase-2 diagnostic, the fresh
adjudication, the Reviewer's baseline acceptance and the L2 verification.
Installation (20), verification (35) and commit (40) are separate so each is
separately observable; no verifier commits, pushes or merges.
