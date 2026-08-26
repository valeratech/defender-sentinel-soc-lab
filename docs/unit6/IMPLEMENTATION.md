# Unit 6 operational integration (Gate D)

> **Status: INERT AS COMMITTED.** This commit publishes the implementation,
> controls and documentation only. Nothing is wired up: `core.hooksPath` is not
> set (so L1 and L2 do not run), and neither `.pre-commit-config.yaml` nor
> `.github/workflows/scrub.yml` references any of it (so CI behaviour is
> unchanged). Activation is a separate, later, deliberate commit taken only
> once the frozen Unit-6 authority bytes exist — until then every governed
> entry point returns `ERROR/ENV_AUTHORITY_ABSENT` by design, which is why
> activating now would block every commit and push in this repository.

Implementation reference for the commit-message publication controls
integrated into this repository. Architecture and engine are frozen
(Gates A–C, Unit-6 contracts); this document covers only the operational
layer that binds them into the working repository.

## Layout

```text
u6/
  result.py             closed status/code vocabulary; one-line U6_RETURN record (no private digest)
  engine_bind.py        frozen engine bound by SHA-256 before first use; per-layer member sets
  engine_iface.py       every engine call surface in one table
  private_root.py       private-state CONSUMER (L2 only): UID -> account db -> home -> msg-controls
  runlog.py             private run log (0600, symlink-safe, directory-relative) - the only sink for free text
  runtime_bind.py       frozen Unit-6 runtime qualification A1-A7, load-bearing at every governed entry point
  l1_commit_msg.py      L1  native commit-msg
  l2_pre_push.py        L2  native pre-push
  l3_ci_sweep.py        L3  CI structural sweep
  return_channel.py     hardened STOP/error return for governed child runs
  ENGINE-IDENTITIES.txt canonical frozen member set: 9 msgctl/* rows + .gitleaks.toml, no aliases
  RUNTIME-IDENTITIES.txt qualified runtime identities (expected values)
  controls/             Builder test battery, falsification harness, labelled test double, fixtures
  orchestrate/          operator scripts, dependency-ordered (none live without joint lock)
.githooks/              commit-msg, pre-push (git config core.hooksPath .githooks)
docs/current-state/     Reviewer-owned authority pointer (UNBOUND until bound) + history/ copies
scripts/check-current-state.py
msgctl/                 (frozen engine members; placed by operator, verified by identity)
```

## Result contract

Every entry point writes exactly one line to stdout:

```text
U6_RETURN v1 KIND=<layer> STATUS=<PASS|REJECT|ERROR|NOT_RUN|STOP> CODE=<token> RC=<0-3> COUNTS=<k=n,...|->
```

Return codes: PASS/NOT_RUN 0, REJECT 1, ERROR 2, STOP 3. Tokens come from a
closed set (`result.CODES`). The grammar admits no free text and carries no
digest or commitment derived from private material. Finding detail,
exception text and paths exist only in the private run log; that log's
SHA-256 is written to a private sidecar beside it and never transported.

## Runtime qualification (frozen Unit-6 contract)

`runtime_bind.bind_runtime` runs before any governed operation in L1, L2 and
every governed child. It binds the frozen contract, not an approximation of it:

```text
A1 environment declaration  at 009a5ec8…  resolved identity-addressed under msgctl/
A2 dependency manifest      at 46e6c9e7…  identity-addressed, closed over exactly
                            {python, git, gitleaks}, each row
                            <name> <path> <sha256> <version>
A3 assert_extends_frozen    effective environment == declaration (declared order)
                            ++ exactly the two additions (order), values exact;
                            a dropped, extra, reordered or altered variable is refused
A4 effective interpreter    /proc/self/exe is the SAME OBJECT as the qualified
                            path — (st_dev, st_ino) equality — and only then are
                            its bytes hashed. A byte-identical copy fails.
A5 effective git            resolved path == qualified path, bytes == manifest
                            SHA-256, then a harmless capability probe whose
                            version token must match the manifest
A6 effective gitleaks       same three properties
A7 frozen U6 implementation present under msgctl/ at 35ee40c3… (identity-addressed)
```

A declaration value of `*` means host-specific-but-required: membership and
order are governed by the declaration, the objects themselves by the manifest.
Nothing is executed until its path and digest have matched, so a shadowed
`git` earlier on PATH is rejected rather than run; the version probe
(`git --version`, `gitleaks version`) touches no repository, network or state.

Neither authority artifact has an asserted filename: its expected digest is
recovered authority, its name is not, so both are located by scanning `msgctl/`
for the file whose bytes hash to the frozen digest. The authority bytes are
absent from every delivered bundle and are never reconstructed. Until they are placed, every governed entry point returns
`ERROR/ENV_AUTHORITY_ABSENT` and refuses activation. Composition of the
EFFECTIVE U6 runtime ID (expected `cfc42cb4…`) is performed by the frozen
implementation itself via `30-u6-runtime-qualify.sh`; this module does not
reimplement it.

The native hooks derive the repository root from their own location
(`.githooks/<hook>`) and exec `/usr/bin/python3.12` by absolute path: no git
process runs before qualification. L2 likewise parses the ref-update stream
(steps 1–2) before qualification (step 3) and starts its first git process
only afterwards.

## Engine binding

`engine_bind.bind(kind, members)` verifies every requested member against
`ENGINE-IDENTITIES.txt` and refuses to import any of them if one differs.
Member sets:

| layer | members |
|---|---|
| L1 | serialize, runtime, adapter, structural, wordlist |
| L2 | serialize, crypto, runtime, adapter, structural, wordlist, identity, baseline |
| L3 | serialize, runtime, adapter, structural |

The engine bytes are not part of this package (they were not in the
successor bundle) and are not reconstructed. They enter `msgctl/` only as
recovered exact bytes whose identities match this manifest
(`15-place-engine.sh` refuses otherwise). Until then the layers return
`ERROR/ENGINE_MEMBER_ABSENT` — an error, not a pass. The engine source is
not private authority; `.pii-terms`, keys, private baseline, term values
and adjudication material remain outside the repository.

## L1 — commit-msg

Reads the message file git passes, byte for byte. Binds the L1 engine set,
requires `.pii-terms` (presence only; contents never logged), runs
`adapter.extract_l1`, `structural.scan_message`, then the wordlist scan.
Wordlist findings reject before structural findings. No baseline is read.

## L2 — pre-push  (PROVISIONAL PENDING EXACT-ORDER COMPARISON)

The frozen seven-step load-bearing order is held in predecessor §§8–9
(`179747cf…040f9`), which was not recoverable. The order below is
Builder-ordered from the transfer text and is not claimed as the exact
frozen order; L2 activation waits on that comparison (Reviewer Pass-3, D-2).

Order: ref-update stream → ref namespace (tags and non-`refs/heads/*` refuse)
→ runtime qualification A1–A7 → single `origin` endpoint, the first git
invocation (fetch and push URLs must be one URL equal to the hook's `$2`)
→ engine binding →
private state (root opened `O_NOFOLLOW|O_DIRECTORY`, owner = euid, mode
without group/other bits; `baseline.key` exactly 32 raw bytes;
`private-baseline`) → committed baseline (`u6/committed-baseline`) →
`load_committed` / `parse_private` / `c4_validate` → union.

Prospective published head set = the live `origin` head set queried in the
same run (`git ls-remote --heads origin`) with the outgoing update tuples
applied (create/update/delete). Union = every commit reachable from every
head of that resulting set, so a violation on a published branch this push
does not touch still rejects. A published head not present locally is
`ERROR/REMOTE_HEAD_NOT_LOCAL` (fetch first; `50-l2-verify.sh` does). Each
message is evaluated structurally and against the
wordlist; findings the private baseline exempts are counted, not rejected.
An empty ref-update stream is `NOT_RUN/NO_REF_UPDATES`, rc 0.

### Baseline binding

The current L2 expected baseline is **not established**. The binding is the
file `u6/committed-baseline`, read by `baseline.load_committed`. While it is
absent L2 returns `ERROR/BASELINE_UNRESOLVED` and the push is refused. The
value is supplied by a future Reviewer-accepted adjudication and committed
in a separate governed commit; nothing in this layer guesses it, and the
historical five-item Audit-3 set is not serialized anywhere in the tree.

## L3 — CI structural sweep

Job `commit-msg-structural` in `.github/workflows/scrub.yml`, run on every
branch and tag push. Corpus: the sweep queries origin at run time
(`git ls-remote --heads --tags origin`) and walks every commit reachable
from every advertised `refs/heads/*` — the complete published branch-head
union. Not HEAD, not an event range, not the pushed commits. Any advertised
tag fails the job closed (`ERROR/TAG_REF_REFUSED`). Engine members are
bound before the first detector call. Findings become `::warning`
annotations naming commit and detector id only; the job passes. Mechanism
failure (member absent/altered, zero heads, zero commits, git failure) is
rc 2 and fails the job.

Isolation by construction, proven by `u6/controls/check_l3_isolation.py`:
the L3 module closure imports no private-root resolver, contains none of
the private artifact names outside docstrings, binds exactly `L3_MEMBERS`,
and calls no wordlist/baseline surface; the workflow names none of them;
and a fresh interpreter that runs L3 ends with no private engine member in
`sys.modules`.

## Hardened return channel

`python3 -m u6.return_channel [--categorical] <KIND> <expected-sha256> <child> [args]`

The channel is one-way with respect to private material: nothing the child
writes, and nothing derived from it, reaches the transportable line — with
one deliberate, grammar-bounded exception in categorical mode.

Categorical mode exists for frozen instruments whose result IS one
privacy-safe line (the Phase-2 diagnostic returns rc 0 whether ready or not
and states its classification on that line). The parent reads the child's
last stdout line from the private log and relays it in `STATE=` only if
every token matches `[A-Z][A-Z0-9_]*=[A-Z0-9_]+` (at most eight tokens, ASCII,
no paths, no lowercase, no free text); anything else is
`ERROR/CATEGORICAL_MALFORMED` and nothing is relayed. `PHASE2_STATE=READY`
and an ordinary non-ready rc-0 state therefore produce mechanically distinct
records. The instrument is never modified. Adjudication does not use this
mode.

The child is started only when a validated private sink exists
(`ERROR/PRIVATE_SINK_UNAVAILABLE` otherwise), through a descriptor opened
relative to that sink with no-follow semantics.

The child is hash-bound before exec, started with stdin closed and stdout
and stderr pointing at the private run log. It has no descriptor to the
terminal. Categorical outcome is exit code plus an optional status file
(`U6_STATUS_FILE`, one line `CODE=<token>`). The parent prints one
`U6_RETURN` line built from validated tokens only; a malformed or unknown
status collapses to a generic `ERROR` token, never to relayed text. The
frozen diagnostic and
adjudication wrappers need no modification to run under it; children that
never write a status file are mapped by exit code (1/2/3 → `STOP_RC_n`).

This replaces the human-only "do not paste below this line" marker whose
failure is recorded as PRIV-002.

## Current-state authority

`docs/current-state/CURRENT.txt` is Reviewer-owned. As shipped it reads
`UNBOUND`: the successor-handoff authority (`35d92347…`) has already been
partly superseded in the governed thread, so no Builder-authored mirror is
promoted. `scripts/check-current-state.py` fails closed on `UNBOUND` (P0)
and never selects a copy from `history/`. Once the Reviewer binds a
revision, the checker verifies the relationship (P1–P6): one CURRENT
revision, named by the pointer, superseded by nothing, from which every
SUPERSEDED revision is reachable. It reads no state value of its own.
Historical mentions of old revision ids anywhere else are allowed. The
check runs in pre-commit (`generated-docs-fresh`) and in CI
(`attack-matrix` job); until the Reviewer binds, both fail by design.

## Private run log

Free text goes only to `<account home>/.defender-sentinel-soc-lab/runs/`.
The home comes from the account database; every component is opened
relative to the previously validated descriptor with `O_NOFOLLOW|O_DIRECTORY`
and checked for type, owner and mode; files and the digest sidecar are
created with `openat(O_CREAT|O_EXCL|O_NOFOLLOW)`. A symlinked or
mis-owned component means memory-only fallback and, for governed children,
refusal to run. The parent directory is never created by a consumer.

## Builder test battery

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest u6.controls.test_u6   # 64 assertions
PYTHONDONTWRITEBYTECODE=1 python3 u6/controls/falsify.py            # 40 mutants, each must be killed
PYTHONDONTWRITEBYTECODE=1 python3 u6/controls/check_l3_isolation.py
```

This is construction evidence, not a control architecture; the frozen
control identities (C1–C5, N4, N-empty, N-privacy) and the Reviewer-required
current-state controls are preserved as named in `u6/controls/README.md`.
The battery runs against the labelled test double in `u6/controls/double/`
(own identity manifest) and patch the private-root resolver, run-log home
and repository root in-process; they never touch the operator's real
private root, wordlist or clone. The falsification harness applies one
defect per mutant to a temporary copy and requires the suite to fail.

## Operator sequence

See `u6/orchestrate/README.md`. Nothing is live until a ⚠️ joint lock.
Order (executable from the admitted 137-file base, which has no `u6/`):
00 preflight → 10 live-HEAD compatibility → 20 apply overlay → 25 place the
the nine manifest members (plus the two identity-addressed authority artifacts) → 30 U6 runtime qualification by the frozen
implementation → Reviewer binds the current-state authority → 35 verify →
40 local commit → 45 Phase-2 diagnostic (with its required `<rundir>`) →
50 fresh adjudication → Reviewer accepts the baseline → 55 commit baseline →
60 L2 verification (dry-run push) → 70 final governed push. A push before the
accepted baseline exists only as the named negative control
`N-prebaseline-push.sh`. Verification never commits; failure evidence is left
in place, and placement never deletes.
