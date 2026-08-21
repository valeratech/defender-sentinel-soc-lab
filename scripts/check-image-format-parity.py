#!/usr/bin/env python3
"""check-image-format-parity.py — per-surface image-format contract gate.

AUD-007's root cause was independently hardcoded extension lists drifting
apart. This gate re-derives every expectation from the components declared in
scripts/image-formats.sh and fails on any disagreement. It carries no format
knowledge of its own: change the authority and every expectation follows.

Per-surface contracts:
  image-formats.sh        components well-formed, lowercase, disjoint;
                          derived lines are exactly the declared compositions
  audit-pii.sh            sources the authority; no independent enumeration
  check-image-policy.sh   sources the authority; no independent enumeration
  ci-image-census.sh      sources the authority; no independent enumeration
  ci-verify-image-metadata.sh  sources the authority; no independent enumeration
  scrub.yml               invokes the census + metadata scripts; contains no
                          image-extension literals
  .pre-commit-config.yaml strip + OCR hook regexes byte-equal the rendered
                          supported-set regex; policy hook regex byte-equals
                          the rendered any-case routing regex
  .gitattributes          binary image lines byte-equal the rendered pinned
                          superset (supported ∪ rejected raster)
  SANITIZATION.md         fenced image-format-policy block matches components

Exit 0 = all contracts hold. Exit 1 = drift, with each violation named.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        err(f"{rel}: missing — contract cannot be checked")
        return ""
    return p.read_text(encoding="utf-8")


# ── Authority ─────────────────────────────────────────────────────────────
auth_text = read("scripts/image-formats.sh")


def component(name: str) -> list[str]:
    m = re.search(rf'^readonly {name}="([^"]*)"', auth_text, re.M)
    if not m:
        err(f"image-formats.sh: component {name} not found as a literal")
        return []
    return m.group(1).split()


SUPPORTED = component("SUPPORTED_IMAGE_EXTS")
SINGLE_FRAME = component("SINGLE_FRAME_ENFORCED_EXTS")
MIME_MAP_RAW = component("SUPPORTED_IMAGE_MIME_MAP")
REJ_RASTER = component("REJECTED_RASTER_IMAGE_EXTS")
REJ_TEXTUAL = component("REJECTED_TEXTUAL_IMAGE_EXTS")

for label, s in (("SUPPORTED_IMAGE_EXTS", SUPPORTED),
                 ("REJECTED_RASTER_IMAGE_EXTS", REJ_RASTER),
                 ("REJECTED_TEXTUAL_IMAGE_EXTS", REJ_TEXTUAL)):
    if not s:
        err(f"image-formats.sh: {label} is empty")
    for e in s:
        if e != e.lower() or not re.fullmatch(r"[a-z0-9]+", e):
            err(f"image-formats.sh: {label} entry '{e}' is not lowercase-alphanumeric")
    if len(set(s)) != len(s):
        err(f"image-formats.sh: {label} contains duplicates")

mime_map: dict[str, str] = {}
for pair in MIME_MAP_RAW:
    if pair.count("=") != 1:
        err(f"image-formats.sh: malformed MIME map entry '{pair}'")
        continue
    k, v = pair.split("=")
    if k in mime_map:
        err(f"image-formats.sh: MIME map maps '{k}' more than once")
    mime_map[k] = v
if set(mime_map) != set(SUPPORTED):
    err("image-formats.sh: MIME map keys must be exactly the supported set "
        f"({sorted(mime_map)} != {sorted(SUPPORTED)})")
for k, v in mime_map.items():
    if not v.startswith("image/"):
        err(f"image-formats.sh: MIME map value for '{k}' is not an image type: {v}")
if not set(SINGLE_FRAME) <= set(SUPPORTED):
    err("image-formats.sh: SINGLE_FRAME_ENFORCED_EXTS must be a subset of SUPPORTED_IMAGE_EXTS")
if set(SUPPORTED) & (set(REJ_RASTER) | set(REJ_TEXTUAL)):
    err("image-formats.sh: supported and rejected sets are not disjoint")
if set(REJ_RASTER) & set(REJ_TEXTUAL):
    err("image-formats.sh: rejected raster and textual sets are not disjoint")

# Derived lines must be exactly the declared compositions (never edited).
for line in (
    'readonly REJECTED_IMAGE_EXTS="${REJECTED_RASTER_IMAGE_EXTS} ${REJECTED_TEXTUAL_IMAGE_EXTS}"',
    'readonly GITATTRIBUTES_BINARY_IMAGE_EXTS="${SUPPORTED_IMAGE_EXTS} ${REJECTED_RASTER_IMAGE_EXTS}"',
):
    if line not in auth_text:
        err(f"image-formats.sh: derived line altered or missing: {line}")

REJECTED = REJ_RASTER + REJ_TEXTUAL
ALL_EXTS = SUPPORTED + REJECTED
GITATTR_SET = SUPPORTED + REJ_RASTER


def alt(exts: list[str]) -> str:
    return "|".join(exts)


# ── Sourcing consumers: must source authority, no independent enumeration ──
# An "independent enumeration" is 2+ known extensions named together outside
# the authority file, in either historical form:
#   regex alternation:  \.(png|jpg|jpeg|webp)$
#   glob list:          **/*.png **/*.jpg ...   (the original AUD-007 form)
ALT_RE = re.compile(
    r"\(\s*(?:" + alt(sorted(set(ALL_EXTS))) + r")(?:\s*\|\s*(?:" + alt(sorted(set(ALL_EXTS))) + r")){1,}\s*\)",
    re.I,
)
GLOB_TOKEN_RE = re.compile(r"\*\.([A-Za-z0-9]{2,5})\b")
EXT_REGEX_SHAPE_RE = re.compile(r"\\\.\(([A-Za-z0-9]{2,5}(?:\|[A-Za-z0-9]{2,5})+)\)\$")


def independent_enumeration(text: str) -> str | None:
    # P6: detection is generic — an enumeration of extensions the authority has
    # never heard of (jxl, qoi, ...) is still an independent list. Comments are
    # excluded so documentation cannot false-positive.
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    m = ALT_RE.search(code)
    if m:
        return m.group(0)
    m = EXT_REGEX_SHAPE_RE.search(code)
    if m:
        return "extension regex: " + m.group(0)
    globs = {g.lower() for g in GLOB_TOKEN_RE.findall(code)}
    if len(globs) >= 2:
        return "glob list: " + " ".join(sorted("*." + g for g in globs))
    return None


ENUM_ONLY = ("scripts/hook-strip-images.sh", "scripts/hook-ocr-images.sh")
for rel in ENUM_ONLY:
    text = read(rel)
    if text:
        found = independent_enumeration(text)
        if found:
            err(f"{rel}: contains an independent image-extension enumeration ({found})")
        # P18: prove the executable delegation shape, not filename presence.
        # The call must appear on a code line, before any comment character.
        CALL = 'bash "$(dirname "$0")/check-image-policy.sh" "$@"'
        delegated = False
        for ln in text.splitlines():
            stripped = ln.lstrip()
            if stripped.startswith("#"):
                continue
            idx = ln.find(CALL)
            if idx == -1:
                continue
            hash_idx = ln.find("#")
            if hash_idx != -1 and hash_idx < idx:
                continue  # call text lives inside a trailing comment — not code
            delegated = True
            break
        if not delegated:
            err(f"{rel}: no executable delegation to check-image-policy.sh — P13 gating missing or commented out")
for rel in ("scripts/audit-pii.sh", "scripts/check-image-policy.sh",
            "scripts/ci-image-census.sh", "scripts/ci-verify-image-metadata.sh"):
    text = read(rel)
    if not text:
        continue
    code_lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    if not any(re.search(r'(?:^|\s)\.\s+"\$\(dirname "\$0"\)/image-formats\.sh"', ln)
               for ln in code_lines):
        err(f"{rel}: does not source scripts/image-formats.sh (comments do not count)")
    found = independent_enumeration(text)
    if found:
        err(f"{rel}: contains an independent image-extension enumeration ({found})")

# ── detect-animation.py: exists and stays extension-free (content-driven) ──
det = read("scripts/detect-animation.py")
if det:
    det_code = "\n".join(ln for ln in det.splitlines()
                          if not ln.lstrip().startswith("#") and '"""' not in ln)
    if GLOB_TOKEN_RE.search(det_code) or EXT_REGEX_SHAPE_RE.search(det_code):
        err("detect-animation.py: contains extension tokens; it must stay content-driven")

# ── scrub.yml: invokes the scripts, zero image-extension literals ─────────
scrub = read(".github/workflows/scrub.yml")
if scrub:
    # An invocation is a real run line, not a substring: commenting out
    # `run: bash scripts/...` must count as removal (review P5d).
    scrub_code = "\n".join(ln for ln in scrub.splitlines()
                            if not ln.lstrip().startswith("#"))
    for needed_re, label in (
        (r"^\s*run: bash scripts/ci-image-census\.sh\s*$", "census step"),
        (r"^\s*run: bash scripts/ci-verify-image-metadata\.sh\s*$", "metadata step"),
        (r"^\s*run: python3 scripts/check-image-format-parity\.py\s*$", "parity step"),
        (r"^\s*bash scripts/ci-image-census\.sh --list0 > ", "OCR list production"),
    ):
        if not re.search(needed_re, scrub_code, re.M):
            err(f"scrub.yml: {label} invocation missing or not a real run line")
    lit = re.compile(r"\*\.(?:" + alt(sorted(set(ALL_EXTS))) + r")\b", re.I)
    for m in lit.finditer(scrub):
        err(f"scrub.yml: image-extension literal present: {m.group(0)}")

# ── .pre-commit-config.yaml: rendered-regex byte equality ─────────────────
pcc = read(".pre-commit-config.yaml")
if pcc:
    expected_supported = r"'\.(" + alt(SUPPORTED) + r")$'"
    expected_routing = r"'(?i)\.(" + alt(ALL_EXTS) + r")$'"

    def hook_block(hook_id: str) -> str | None:
        m = re.search(rf"- id: {re.escape(hook_id)}\n((?:(?!\s*- id: ).*\n)*)", pcc)
        return m.group(1) if m else None

    def hook_files(hook_id: str) -> str | None:
        block = hook_block(hook_id)
        if block is None:
            return None
        m = re.search(r"^\s+files: (.+)$", block, re.M)
        return m.group(1).strip() if m else "<MISSING-FILES-LINE>"

    for hook, expected in (("strip-image-metadata", expected_supported),
                           ("ocr-scan-images", expected_supported),
                           ("image-policy", expected_routing)):
        got = hook_files(hook)
        if got is None:
            err(f".pre-commit-config.yaml: hook '{hook}' missing")
        elif got == "<MISSING-FILES-LINE>":
            err(f".pre-commit-config.yaml: hook '{hook}' has no files: line — hook would run on nothing or everything")
        elif got != expected:
            err(f".pre-commit-config.yaml: hook '{hook}' files regex drifted: {got} != {expected}")
    if "- id: image-format-parity" not in pcc:
        err(".pre-commit-config.yaml: image-format-parity hook missing")
    else:
        expected_trigger = (
            r"'^(\.pre-commit-config\.yaml|\.gitattributes|SANITIZATION\.md|"
            r"\.github/workflows/scrub\.yml|scripts/(image-formats\.sh|"
            r"check-image-format-parity\.py|check-image-policy\.sh|"
            r"hook-strip-images\.sh|hook-ocr-images\.sh|"
            r"detect-animation\.py|ci-image-census\.sh|"
            r"ci-verify-image-metadata\.sh|audit-pii\.sh))$'"
        )
        def hook_entry(hook_id: str) -> str | None:
            block = hook_block(hook_id)
            if block is None:
                return None
            m = re.search(r"^\s+entry: (.+)$", block, re.M)
            return m.group(1).strip() if m else None

        for hook, expected_entry in (
            ("strip-image-metadata", "bash scripts/hook-strip-images.sh"),
            ("ocr-scan-images", "bash scripts/hook-ocr-images.sh"),
            ("image-policy", "bash scripts/check-image-policy.sh"),
        ):
            got_e = hook_entry(hook)
            if got_e != expected_entry:
                err(f".pre-commit-config.yaml: hook '{hook}' entry drifted: "
                    f"{got_e} != {expected_entry} — policy gating (P13) depends on the wrapper")

        got_trigger = hook_files("image-format-parity")
        if got_trigger != expected_trigger:
            err(".pre-commit-config.yaml: image-format-parity trigger drifted from "
                f"the policy-surface list: {got_trigger} != {expected_trigger}")

# ── .gitattributes: binary lines byte-equal the rendered pinned superset ──
ga = read(".gitattributes")
if ga:
    got_lines = [ln.strip() for ln in ga.splitlines()
                 if re.match(r"\*\.\S+\s+binary$", ln.strip())]
    expected_lines = [f"*.{e}   binary" for e in GITATTR_SET]
    if got_lines != expected_lines:
        err(".gitattributes: binary image lines differ from the derived pinned "
            f"superset.\n  expected: {expected_lines}\n  found:    {got_lines}")

# ── SANITIZATION.md fenced policy block ───────────────────────────────────
san = read("SANITIZATION.md")
if san:
    m = re.search(r"```image-format-policy\n(.*?)```", san, re.S)
    if not m:
        err("SANITIZATION.md: fenced image-format-policy block missing")
    else:
        block = dict(
            (k.strip(), v.split())
            for k, v in (ln.split(":", 1) for ln in m.group(1).strip().splitlines())
        )
        for key, comp in (("supported", SUPPORTED),
                          ("rejected-raster", REJ_RASTER),
                          ("rejected-textual", REJ_TEXTUAL),
                          ("single-frame", SINGLE_FRAME),
                          ("mime-binding", MIME_MAP_RAW)):
            if block.get(key) != comp:
                err(f"SANITIZATION.md: policy block '{key}' != authority: "
                    f"{block.get(key)} != {comp}")

# ── Verdict ───────────────────────────────────────────────────────────────
if ERRORS:
    print("image-format parity: FAIL")
    for e in ERRORS:
        print(f"  DRIFT  {e}")
    sys.exit(1)
print("image-format parity: PASS — all surfaces agree with scripts/image-formats.sh")
