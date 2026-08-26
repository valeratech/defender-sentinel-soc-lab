# u6 — Unit-6 operational layer (inert as committed)

Commit-message publication controls for this repository: L1 (native
`commit-msg`), L2 (native `pre-push`), L3 (CI structural sweep), a hardened
return channel for governed child runs, and the frozen Unit-6 runtime
qualification that gates all of them.

**Nothing here runs until it is deliberately activated.** `core.hooksPath` is
not set by this commit and no CI workflow or pre-commit hook references this
directory. Activation additionally requires the frozen Unit-6 authority
artifacts (environment declaration `009a5ec8…`, dependency manifest
`46e6c9e7…`, implementation `35ee40c3…`, and the eight engine members named in
`ENGINE-IDENTITIES.txt`), none of which are present: every governed entry point
returns `ERROR/ENV_AUTHORITY_ABSENT` until they are.

Read `../docs/unit6/IMPLEMENTATION.md` first. Controls and how to run them:
`controls/README.md`. Operator sequence: `orchestrate/README.md`.
