#!/usr/bin/env bash
# LOCAL / PRIVATE commit-message policy measurement.  READ-ONLY.  No push,
# no commit, no history rewrite, no repository write of any kind.
#
# Why this exists: COMMIT_MESSAGE_POLICY=NOT_MEASURED. The frozen wordlist
# detector (msgctl/wordlist.py, 15a1d57e...) is absent, so the governed L1/L2
# detectors cannot run. This measures the SAME published surface using the
# operator's local .pii-terms, which never leaves the machine and is gitignored.
# It is a MEASUREMENT INSTRUMENT, not a governed control: it does not implement
# the frozen structural rules and its result is not an L1/L2 verdict.
#
# EXPOSURE CONTRACT:
#   * stdout carries COUNTS and COMMIT SHAs only.
#   * no wordlist term is ever printed, to stdout or to the private detail.
#   * no commit message text is ever printed to stdout.
#   * private detail (<sha> term_index=<n> count=<n>) goes ONLY through the
#     accepted hardened private run log (u6/runlog.py): account home from the
#     OS account database for the effective UID (never $HOME), every path
#     component opened relative to a validated descriptor with O_NOFOLLOW,
#     parent type/owner/mode validated, file created O_EXCL|O_NOFOLLOW at
#     mode 0600. If no safe disk sink can be established the detail stays
#     memory-only and is discarded; stdout reports which happened.
#   * a term index is meaningless without .pii-terms, which is never committed.
#
# Executables are the qualified objects by absolute path, never PATH-resolved.
#
# 🚨 The private detail is LOCAL-ONLY. Do not paste it into chat.
#
# Usage: bash scripts/measure-message-policy.sh [--all | --since <sha>]
set -u
PY=/usr/bin/python3.12
GIT=/usr/bin/git
[ -x "$PY" ]  || { echo "MSGPOLICY result=REFUSED reason=QUALIFIED_PYTHON_ABSENT"; exit 1; }
[ -x "$GIT" ] || { echo "MSGPOLICY result=REFUSED reason=QUALIFIED_GIT_ABSENT"; exit 1; }

cd ~/defender-sentinel-soc-lab 2>/dev/null || { echo 'MSGPOLICY result=REFUSED reason=WRONG_DIR'; exit 1; }
[ -d u6 ] && [ -f u6/runlog.py ] || { echo 'MSGPOLICY result=REFUSED reason=RUNLOG_MODULE_ABSENT'; exit 1; }

RANGE=HEAD
case "${1:-}" in
  --since) RANGE="${2:?}..HEAD" ;;
  --all|"") RANGE=HEAD ;;
  *) echo "usage: measure-message-policy.sh [--all | --since <sha>]"; exit 2 ;;
esac

PYTHONDONTWRITEBYTECODE=1 "$PY" - "$GIT" "$RANGE" <<'PY'
import os, subprocess, sys
sys.dont_write_bytecode = True
git, rng = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.getcwd())
from u6.runlog import RunLog          # accepted hardened private sink (P5-03)

WORDLIST = ".pii-terms"
if not os.path.isfile(WORDLIST):
    print("MSGPOLICY result=REFUSED reason=WORDLIST_ABSENT"); sys.exit(1)
tracked = subprocess.run([git, "ls-files", "--error-unmatch", WORDLIST],
                         capture_output=True).returncode == 0
if tracked:
    print("MSGPOLICY result=REFUSED reason=WORDLIST_IS_TRACKED (publication risk)"); sys.exit(1)

terms = []
with open(WORDLIST, encoding="utf-8", errors="replace") as f:
    for line in f:
        t = line.strip()
        if t and not t.startswith("#"):
            terms.append(t)
if not terms:
    print("MSGPOLICY result=REFUSED reason=WORDLIST_EMPTY"); sys.exit(1)

shas = subprocess.run([git, "log", "--format=%H", rng],
                      capture_output=True, text=True, check=True).stdout.split()

# Case semantics follow the wordlist admission policy: an all-lowercase entry
# matches case-insensitively; an entry carrying any uppercase matches exactly.
prepared = [(i, t, t.islower()) for i, t in enumerate(terms)]

log = RunLog("msgpolicy")
log("# term-index only. Indices are meaningless without .pii-terms.")
log("# NEVER paste this file into chat.")

commits_with_hits = 0
total_hits = 0
per_commit = []
for sha in shas:
    body = subprocess.run([git, "log", "-1", "--format=%B", sha],
                          capture_output=True, text=True, check=True).stdout
    low = body.lower()
    hits = [(idx, (low.count(term.lower()) if ci else body.count(term)))
            for idx, term, ci in prepared]
    hits = [(idx, n) for idx, n in hits if n]
    if hits:
        commits_with_hits += 1
        total_hits += sum(n for _, n in hits)
        per_commit.append((sha, len(hits)))
        for idx, n in hits:
            log(f"{sha} term_index={idx} count={n}")
log.close()

print(f"MSGPOLICY commits_scanned={len(shas)}")
print(f"MSGPOLICY wordlist_terms={len(terms)}")
print(f"MSGPOLICY commits_with_matches={commits_with_hits}")
print(f"MSGPOLICY total_matches={total_hits}")
for sha, k in per_commit:
    print(f"  MATCH_COMMIT {sha} distinct_terms={k}")
print(f"MSGPOLICY detail_sink={'DISK_PRIVATE_0600' if log.on_disk else 'MEMORY_ONLY_DISCARDED'}")
print("MSGPOLICY result=MEASURED")
PY
rc=$?
echo "🚨 private detail (if on disk) is LOCAL-ONLY - do not paste it"
exit $rc
