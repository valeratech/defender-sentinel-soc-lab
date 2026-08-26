"""Private-state resolution. CONSUMER ONLY.

Frozen derivation (Reviewer transfer §6):

    effective UID -> OS account database -> account home
                  -> .defender-sentinel-soc-lab/msg-controls

Never from $HOME, cwd, XDG variables, repository configuration, a CLI-selected
root, or a hard-coded username. Root is opened O_NOFOLLOW|O_DIRECTORY and
validated for type, ownership and mode. Consumers never create, chmod, chown,
repair, replace, migrate or regenerate anything below the root.

This module is in the L2 reachable set only. It is NOT in L3_MEMBERS and the
L3 sweep module contains no import of it (enforced by controls/check_l3_isolation.py).
"""
from __future__ import annotations

import os
import pwd
import stat
from pathlib import Path

from . import result as R

REL = (".defender-sentinel-soc-lab", "msg-controls")
KEY = "baseline.key"
BASELINE = "private-baseline"
KEY_LEN = 32  # exactly 32 RAW bytes; never hex/base64/PEM/text


def resolve_root_path() -> Path:
    uid = os.geteuid()
    home = pwd.getpwuid(uid).pw_dir  # account database, not $HOME
    return Path(home).joinpath(*REL)


def open_root(kind: str):
    """Return (dir_fd, None) or (None, Result[ERROR]). Caller closes the fd."""
    root = resolve_root_path()
    try:
        fd = os.open(root, os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0))
    except OSError:
        return None, R.error(kind, "PRIVATE_ROOT_UNOPENABLE")
    try:
        st = os.fstat(fd)
    except OSError:
        os.close(fd)
        return None, R.error(kind, "PRIVATE_ROOT_UNOPENABLE")
    if not stat.S_ISDIR(st.st_mode):
        os.close(fd)
        return None, R.error(kind, "PRIVATE_ROOT_NOT_DIR")
    if st.st_uid != os.geteuid():
        os.close(fd)
        return None, R.error(kind, "PRIVATE_ROOT_OWNER")
    if stat.S_IMODE(st.st_mode) & 0o077:
        os.close(fd)
        return None, R.error(kind, "PRIVATE_ROOT_MODE")
    return fd, None


def read_member(kind: str, dir_fd: int, name: str, exact_len: int | None = None):
    """Read a member relative to the open root fd. Returns (bytes, None) or (None, Result)."""
    try:
        mfd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0), dir_fd=dir_fd)
    except FileNotFoundError:
        return None, R.error(kind, "PRIVATE_MEMBER_ABSENT")
    except OSError:
        return None, R.error(kind, "PRIVATE_MEMBER_UNREADABLE")
    try:
        st = os.fstat(mfd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or stat.S_IMODE(st.st_mode) & 0o077:
            return None, R.error(kind, "PRIVATE_MEMBER_UNREADABLE")
        data = b""
        while True:
            chunk = os.read(mfd, 1 << 16)
            if not chunk:
                break
            data += chunk
    except OSError:
        return None, R.error(kind, "PRIVATE_MEMBER_UNREADABLE")
    finally:
        os.close(mfd)
    if exact_len is not None and len(data) != exact_len:
        return None, R.error(kind, "PRIVATE_MEMBER_UNREADABLE")
    return data, None


def wordlist_path(kind: str):
    """The private wordlist is the gitignored repository-root ``.pii-terms``.
    Its presence is required for any wordlist-consuming layer (L1, L2).
    Returns (Path, None) or (None, Result)."""
    from .engine_bind import REPO_ROOT
    p = REPO_ROOT / ".pii-terms"
    if not p.is_file():
        return None, R.error(kind, "WORDLIST_ABSENT")
    if not os.access(p, os.R_OK):
        return None, R.error(kind, "WORDLIST_UNREADABLE")
    return p, None
