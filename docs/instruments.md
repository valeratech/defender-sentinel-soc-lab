# Instrument Contracts

What each gate is invoked as, what it needs before it can measure anything, where
it runs, and — the part that is easy to lose — **what a PASS from it actually
establishes**.

This exists because a successful exit code is not a measurement. An instrument
invoked outside the context it needs can return `0` having examined nothing — or,
worse, having examined a fraction of what it reports examining — and that green
result is indistinguishable from a real one unless someone wrote down what the
real one means. The contexts that matter here turn out to be three: the working
directory, a live Git index, and whether the files named by that index are
actually on disk. `scripts/check-image-policy.sh` is the worked example:
run with no arguments it iterates an empty list and exits `0`, and an audit once
recorded that as a repository-wide pass. It was not one.

**Scope.** The eleven instruments CI invokes, plus `check-image-policy.sh`, which
CI does not invoke but pre-commit does. Helper scripts sourced by these — notably
`scripts/image-formats.sh`, the machine authority for the image format sets — are
not listed separately; they have no independent invocation contract. This table
is not an inventory of every script in `scripts/`.

---

## Generated-document gates

Each regenerates its target and compares. `--check` compares without writing and
fails on any difference; without `--check` it rewrites the target.

| Instrument | Invocation | Preconditions | Surface | A PASS establishes |
|---|---|---|---|---|
| `build-attack-matrix.py` | `python3 scripts/build-attack-matrix.py --check` | none beyond Python 3 | CI, pre-commit | `docs/attack-coverage.md` matches what the detection specs currently say. Not that the coverage claims are true — validation status comes from the specs |
| `build-posture-register.py` | `python3 scripts/build-posture-register.py --check` | PyYAML | CI, pre-commit | `docs/posture-register.md` matches `posture.yml`. Nothing about whether an entry is correctly classified |
| `build-lab-index.py` | `python3 scripts/build-lab-index.py --check` | the `BEGIN`/`END GENERATED LAB INDEX` markers must exist in `README.md` | CI, pre-commit | the README lab table mirrors each lab's own title and Status row. Status text is truncated at the em dash by design, so an elaboration after the dash is not compared |
| `open-items.py` | `python3 scripts/open-items.py --check` | **a live Git index** — the corpus is `git ls-files`, and the script raises rather than falling back to the filesystem | CI, pre-commit | `docs/open-items.md` matches the `*(pending)*` markers in tracked Markdown, **and** no marker opens on a line without closing on it. A split marker fails rather than being dropped |
| `check-lab-coverage.py` | `python3 scripts/check-lab-coverage.py --check` | PyYAML | CI, pre-commit | `docs/lab-coverage.md` is current; every ✅ lab cites each register entry assigned to it; and every lab's status was readable. It does **not** establish that a lab cites its entries meaningfully — citation is a proxy for someone having gone back |

`check-lab-coverage.py --strict` additionally fails on any uncited entry
regardless of lab status. CI does not run `--strict`.

## Validators

Produce no document. There is nothing to regenerate.

| Instrument | Invocation | Preconditions | Surface | A PASS establishes |
|---|---|---|---|---|
| `check-evidence-notes.py` | `python3 scripts/check-evidence-notes.py` | PyYAML; `posture.yml`, `docs/configuration-inventory.md` and `docs/evidence-notes/` must be readable — each fails closed with one stated line if not | CI | every evidence note carries exactly the required frontmatter keys and every cited handle resolves to a real lab, posture ID, divergence row, KQL path, or detection spec. Accepts `--check` as a no-op alias for uniformity |
| `check-current-state.py` | `python3 scripts/check-current-state.py` | none beyond Python 3 | CI, pre-commit | `CURRENT.txt` selects exactly one revision with `status=CURRENT`; supersession is reciprocal; the selected revision binds a Reviewer authority document inside the owned namespace by exact SHA-256. `UNBOUND` fails closed |
| `check-image-format-parity.py` | `python3 scripts/check-image-format-parity.py` | none beyond Python 3 | CI, pre-commit | every surface naming image extensions agrees with `scripts/image-formats.sh`, and the policy scripts source that authority rather than enumerating independently. It compares **declarations**, not images, and holds whether or not any image exists |

## Image-policy instruments

| Instrument | Invocation | Preconditions | Surface | A PASS establishes |
|---|---|---|---|---|
| `ci-image-census.sh` | `bash scripts/ci-image-census.sh` · `--list0` to emit clean paths NUL-delimited | a live Git index; **invocation from the repository root**; **every tracked path materialized in the worktree**; `file`; `python3` for the frame check (all four below) | CI | every tracked file that was both visible from the caller's directory **and present on disk** was examined for an image-like extension, image content, content/extension agreement, and — for supported images — a single-frame container. A zero-image census is a real result only if the corpus was the whole repository and the whole repository was on disk |
| `ci-verify-image-metadata.sh` | `bash scripts/ci-verify-image-metadata.sh` | ExifTool, digest-pinned in CI; a live Git index; **invocation from the repository root** (see below); `python3` for the self-proof fixture | CI | the oracle was first proved able to fail on this toolchain — a tag is planted on a generated fixture and must be detected — and then no image **in the enumerated corpus** carried metadata. The self-proof is why this step means something even when the tree holds no images |
| `scan-image-text.sh` | `bash scripts/scan-image-text.sh <path>…` | `tesseract`; `gitleaks`; `python3`; an OCR config at `${GITLEAKS_OCR_CONFIG:-.gitleaks-ocr.toml}` — the default is **relative to the caller's directory**, so the CI form runs from the repository root; **arguments must exist on disk** or they are skipped before being counted | CI, and via `hook-ocr-images.sh` in pre-commit | the OCR text recovered from the images **actually admitted to its loop** carried no gitleaks finding, under the config that was actually resolved. Its own totals count admitted images, not arguments supplied. Given no paths it scans nothing. CI guards this by hard-checking census output first, so an empty list means an empty tree rather than a failed enumeration |
| `check-image-policy.sh` | `bash scripts/check-image-policy.sh <path>…` | `file`; `python3` for the frame check; **arguments must exist on disk** for the content and frame checks to run | **pre-commit only** — CI does not invoke it | each path given as an argument carries a lowercase-exact supported extension, **and** — for arguments that exist as files — its content matches that extension and contains one frame. Extension policy is checked unconditionally; content and frame policy covers existing paths only |

### `check-image-policy.sh` is argument-driven

It iterates `"$@"` and exits with the count of blocked files. Pre-commit supplies
the staged filenames through `pass_filenames: true`, which is the only invocation
under which it measures anything.

> **A bare `bash scripts/check-image-policy.sh` returns `0` having evaluated
> nothing. That is not a repository-wide pass and must never be recorded as one.**

To exercise it deliberately, pass fixtures and check both directions: a valid
lowercase image returns `0`, and a mis-cased extension, a rejected format, or
content disagreeing with its extension each return `1` with a stated reason.

The repository-wide equivalent of this policy is `ci-image-census.sh`, which
applies the same layers across every tracked file. Both source their format sets
from `scripts/image-formats.sh`, and `check-image-format-parity.py` enforces that
neither enumerates independently.

## History scan

The gitleaks history scan lives inline in `.github/workflows/scrub.yml` rather
than in a script. Its assertion is a relationship, not a value: the scan summary
must parse, commits scanned must be non-zero, and bytes scanned must be non-zero.
A count is deliberately not fixed anywhere — it moves with every commit, and
commits with no content diff are not scanned or counted, so no literal stays true.

---

## Two preconditions worth stating on their own

**A live Git index.** `open-items.py`, `ci-image-census.sh` and
`ci-verify-image-metadata.sh` take their corpus from `git ls-files`. Run against
an extracted archive with no `.git`, they fail rather than silently substituting
a filesystem walk — a census that quietly changes corpus is worse than one that
stops. Any audit working from a source archive must supply an index-backed work
tree and say that it did.

**Working directory — and it is not uniform.** The instruments split into two
groups, and the difference is load-bearing rather than cosmetic.

*CWD-independent.* Every Python instrument here derives the repository root from
its own file location (`__file__`), so the corpus it measures does not move with
the caller:

```text
build-attack-matrix.py     build-lab-index.py       build-posture-register.py
open-items.py              check-lab-coverage.py    check-current-state.py
check-evidence-notes.py    check-image-format-parity.py
```

*Repository root required.* `ci-image-census.sh` and `ci-verify-image-metadata.sh`
call bare `git ls-files` with no `-C` and no root binding. `git ls-files` is
scoped to the current directory, so the corpus follows the caller — and the gate
still exits 0 over the smaller corpus. Measured on this repository:

| Invoked from | `ci-image-census.sh` corpus | Exit |
|---|---|---|
| repository root | 218 tracked files | 0 |
| `docs/` | 85 tracked files | 0 |
| `labs/` | 28 tracked files | 0 |
| `scripts/` | 19 tracked files | 0 |

A green census therefore asserts nothing about the repository unless it was run
from the root. CI satisfies this because a workflow `run:` step starts in the
workspace root, and pre-commit likewise runs hooks from the repository root — so
the governed invocations are correct today. The precondition is nonetheless real
and is recorded here because it is invisible at the call site: nothing in
`run: bash scripts/ci-image-census.sh` shows that the line depends on where it
starts.

`scan-image-text.sh` shares the shape through its config default rather than
through enumeration: `${GITLEAKS_OCR_CONFIG:-.gitleaks-ocr.toml}` resolves
relative to the caller, so the same invocation from a subdirectory would fail to
find the rules it is meant to scan under. Set `GITLEAKS_OCR_CONFIG` explicitly
if calling it from anywhere but the root.

## A third precondition: the files have to be there

A live index and a root invocation are still not sufficient for
`ci-image-census.sh`. Being **tracked** and being **present on disk** are
different facts, and the census reads the first while depending on the second.

`file(1)` reports an unreadable path on *stdout* and exits 0:

```text
$ file --brief --mime-type -- missing/README.md
cannot open `missing/README.md' (No such file or directory)
$ echo $?
0
```

The census fails closed on `rc != 0` or empty output. This is neither, so the
diagnostic string is consumed as though it were a MIME type. It matches no
`image/*` case, the file is passed over, and the tracked-file counter still
increments. Measured against an index carrying 218 tracked paths of which 50
were absent from the worktree:

```text
census: tracked files: 218 · supported clean images: 0
census: no images in the tracked tree — nothing further to scan.
census: PASS        rc=0
```

Fifty tracked paths were never examined and the count says 218. **A census PASS
must not be described as repository-wide when it ran against a sparse or
reconstructed worktree that deliberately omits tracked paths** — which is
exactly the shape of an audit fixture built from a source archive under the
Unit-6 boundary, where `u6/` is indexed but not materialized.

`ci-verify-image-metadata.sh` does **not** share this: its oracle begins with
`cp -- "$img"`, so an absent tracked image fails the copy and returns
`METADATA-CHECK-FAILED`. That is fail-closed. (Established by reading the
source — ExifTool was unavailable where this was checked, so it was not run.)

### The same class on the argument-driven surfaces

```text
$ bash scripts/check-image-policy.sh /definitely/missing.png
$ echo $?
0
```

Its content and frame checks sit behind `[ -f "$f" ]`, so a nonexistent path
reaches neither. The extension checks are unconditional and still fire —
`/definitely/MISSING.PNG` returns 1 on the casing rule alone — so the accurate
statement is narrow: **extension policy covers every argument; content and frame
policy covers the arguments that exist.**

`scan-image-text.sh` skips a nonexistent argument with `[ -f "$img" ] || continue`
*before* incrementing `TOTAL`, so such an argument is absent from its own
accounting rather than reported as unscanned. Its totals describe images
admitted to the loop, not arguments handed to it.

None of this is repaired in code. It is the current implementation boundary,
recorded so a PASS is not read as covering more than it did.

A normal `actions/checkout` or a working clone materializes every tracked path,
so the governed CI and pre-commit invocations are the case these preconditions
are expected to satisfy. That expectation has not itself been measured here, and
it is not a guarantee — it is the reason the boundary usually goes unnoticed,
which is also why it is worth writing down.

These are statements about the instruments as they are written today, not a
recommendation to leave them that way. Rooting the shell instruments, or making
the census fail closed on an unreadable tracked path, would remove these
preconditions rather than document them; both are changes to the instruments
themselves and need their own scope.
