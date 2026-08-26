# Native hooks (Unit 6 L1 / L2)

Activate once per clone:

    git config core.hooksPath .githooks

`commit-msg` -> `u6.l1_commit_msg` (verbatim message bytes; structural + private wordlist; no baseline)
`pre-push`   -> `u6.l2_pre_push`   (complete prospective published union; structural + wordlist + accepted baseline)

Both print one `U6_RETURN` line and nothing else. Detail is written to a
private run log under the account home and is never shown. `pre-commit`
hooks (content scanning) remain in `.pre-commit-config.yaml`; these native
hooks cover the commit-message publication surface that pre-commit cannot.
