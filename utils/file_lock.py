"""
AccessOps Toolkit - File Lock Helper
------------------------------------
Simple cross-platform lock helper for safer JSON read/write operations.

This helps prevent multiple scripts from writing the same JSON file at the
same time when the GUI, CLI tools, or future API layer are running together.
"""

import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_lock(target_file: Path, timeout: float = 5.0, poll_interval: float = 0.1):
    """
    Create a temporary lock file while working with a target file.

    Example:
        with file_lock(Path("data/tickets.json")):
            # safely read/write tickets.json
            ...

    Args:
        target_file: File being protected.
        timeout: Max seconds to wait for the lock.
        poll_interval: Seconds between lock checks.
    """
    lock_file = target_file.with_suffix(target_file.suffix + ".lock")
    start_time = time.time()

    while lock_file.exists():
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timed out waiting for lock: {lock_file}")
        time.sleep(poll_interval)

    try:
        lock_file.write_text(str(time.time()), encoding="utf-8")
        yield
    finally:
        try:
            lock_file.unlink()
        except FileNotFoundError:
            pass