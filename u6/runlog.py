"""Private run log.

Free text (finding detail, exception text, paths, counts with context) is
written ONLY here. The transportable channel (stdout of every Unit-6 entry
point) carries exactly one U6_RETURN record and never any digest or
commitment derived from this log.

Location: <account home>/.defender-sentinel-soc-lab/runs/<kind>-<utc>-<pid>.log
The account home comes from the OS account database for the effective UID
(never $HOME). ``.defender-sentinel-soc-lab`` is a SIBLING parent of the
private root ``msg-controls``; this module never opens, creates or touches
``msg-controls``. The ``runs`` directory is created only if absent, mode
0700, directly under an already-validated parent; the parent itself is
never created here.

Structural safety (Reviewer Pass-5 P5-03): every path component is opened
relative to the previously validated directory descriptor with O_NOFOLLOW
and O_DIRECTORY, then validated by fstat for type, ownership (euid) and mode
(no group/other bits for the two private components). The log file and its
digest sidecar are created with openat(O_CREAT|O_EXCL|O_NOFOLLOW) relative
to the validated ``runs`` descriptor. No pathname is ever opened through a
symlink. If any step fails, the log falls back to memory only; nothing is
written anywhere.

The log's SHA-256 is written to the sidecar <log>.sha256 (0600) beside it
and is PRIVATE-LOCAL: never printed, transported, committed or placed in CI.
"""
from __future__ import annotations

import hashlib
import os
import pwd
import stat
import time

PARENT = ".defender-sentinel-soc-lab"
RUNS = "runs"
_DIR_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_APPEND | getattr(os, "O_CLOEXEC", 0)


def _validated_dir(fd: int, private: bool) -> bool:
    try:
        st = os.fstat(fd)
    except OSError:
        return False
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid():
        return False
    if private and stat.S_IMODE(st.st_mode) & 0o077:
        return False
    return True


def _open_runs_dir():
    """Return a validated fd for <home>/.defender-sentinel-soc-lab/runs or None."""
    try:
        home = pwd.getpwuid(os.geteuid()).pw_dir
    except KeyError:
        return None
    home_fd = parent_fd = runs_fd = None
    try:
        home_fd = os.open(home, _DIR_FLAGS)          # absolute; the account home itself
        if not _validated_dir(home_fd, private=False):
            return None
        try:
            parent_fd = os.open(PARENT, _DIR_FLAGS, dir_fd=home_fd)
        except OSError:
            return None                              # parent is never created here
        if not _validated_dir(parent_fd, private=True):
            return None
        try:
            runs_fd = os.open(RUNS, _DIR_FLAGS, dir_fd=parent_fd)
        except FileNotFoundError:
            try:
                os.mkdir(RUNS, 0o700, dir_fd=parent_fd)
                runs_fd = os.open(RUNS, _DIR_FLAGS, dir_fd=parent_fd)
            except OSError:
                return None
        except OSError:
            return None                              # ELOOP (symlink) lands here
        if not _validated_dir(runs_fd, private=True):
            return None
        out, runs_fd = runs_fd, None
        return out
    except OSError:
        return None
    finally:
        for fd in (home_fd, parent_fd, runs_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass


class RunLog:
    def __init__(self, kind: str):
        self.kind = kind
        self.buf = bytearray()
        self.name: str | None = None
        self._dir_fd = _open_runs_dir()
        self._fd = None
        if self._dir_fd is not None:
            ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            name = f"{kind.lower()}-{ts}-{os.getpid()}-{time.monotonic_ns() % 1_000_000_000:09d}.log"
            try:
                self._fd = os.open(name, _FILE_FLAGS, 0o600, dir_fd=self._dir_fd)
                self.name = name
            except OSError:
                self._fd = None
        self(f"kind={kind} pid={os.getpid()} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

    @property
    def on_disk(self) -> bool:
        return self.name is not None

    def __call__(self, line: str) -> None:
        data = (line.rstrip("\n") + "\n").encode("utf-8", "replace")
        self.buf += data
        if self._fd is not None:
            try:
                os.write(self._fd, data)
            except OSError:
                pass

    def reopen_for_child(self) -> int | None:
        """A second descriptor to the same log for a governed child's fds 1/2.
        Opened relative to the validated directory, no-follow. Caller closes."""
        if self._dir_fd is None or self.name is None:
            return None
        try:
            return os.open(self.name, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
                           dir_fd=self._dir_fd)
        except OSError:
            return None

    def resync_from_disk(self) -> None:
        """Refresh the in-memory buffer from the file (after a child appended)."""
        if self._dir_fd is None or self.name is None:
            return
        try:
            fd = os.open(self.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=self._dir_fd)
        except OSError:
            return
        try:
            data = bytearray()
            while True:
                chunk = os.read(fd, 1 << 16)
                if not chunk:
                    break
                data += chunk
            self.buf = data
        finally:
            os.close(fd)

    def close(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None
        digest = hashlib.sha256(bytes(self.buf)).hexdigest()
        if self._dir_fd is not None and self.name is not None:
            try:
                fd = os.open(self.name + ".sha256", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600,
                             dir_fd=self._dir_fd)
                os.write(fd, (digest + "\n").encode())
                os.close(fd)
            except OSError:
                pass
        if self._dir_fd is not None:
            try:
                os.close(self._dir_fd)
            except OSError:
                pass
            self._dir_fd = None
