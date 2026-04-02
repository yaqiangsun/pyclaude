"""
Lockfile utilities.

File-based locking for concurrent access.
"""

import os
import time
from typing import Optional
from contextlib import contextmanager


class Lockfile:
    """File-based lock."""

    def __init__(self, path: str, timeout: float = 10.0):
        self.path = path
        self.timeout = timeout
        self._acquired = False

    def acquire(self) -> bool:
        """Acquire the lock.

        Returns:
            True if acquired
        """
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively
                fd = os.open(self.path + ".lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                os.close(fd)
                self._acquired = True
                return True
            except FileExistsError:
                if time.time() - start_time > self.timeout:
                    return False
                time.sleep(0.1)
            except Exception:
                return False

    def release(self) -> None:
        """Release the lock."""
        if self._acquired:
            try:
                os.remove(self.path + ".lock")
            except Exception:
                pass
            self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


@contextmanager
def lock(path: str, timeout: float = 10.0):
    """Context manager for locking.

    Args:
        path: File to lock
        timeout: Timeout in seconds

    Yields:
        Lockfile instance
    """
    lockfile = Lockfile(path, timeout)
    try:
        if lockfile.acquire():
            yield lockfile
        else:
            raise TimeoutError(f"Could not acquire lock for {path}")
    finally:
        lockfile.release()


__all__ = [
    "Lockfile",
    "lock",
]