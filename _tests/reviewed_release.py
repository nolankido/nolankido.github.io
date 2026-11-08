"""Read immutable, hash-checked Git fixtures for historical release tests.

Historical assertions describe the files approved in their original release,
not the site files after later, independently reviewed improvements. This
module is test-only and does not change historical predecessor adapters.
"""

from functools import lru_cache
from hashlib import sha1
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}\Z")


@lru_cache(maxsize=None)
def read(commit: str, path: str, expected_blob: str) -> bytes:
    """Get an explicitly pinned release blob or fail on any mismatch."""
    if not SHA.fullmatch(commit) or not SHA.fullmatch(expected_blob):
        raise ValueError("Historical release commit and blob must be full Git SHAs")
    name = PurePosixPath(path)
    if (not path or path.startswith("/") or "\\" in path
            or ".." in name.parts or name.as_posix() != path):
        raise ValueError("Historical fixture must use a repository-relative path")
    body = subprocess.check_output(["git", "show", commit + ":" + path], cwd=ROOT)
    actual = sha1(b"blob " + str(len(body)).encode("ascii") + b"\x00" + body).hexdigest()
    if actual != expected_blob:
        raise AssertionError("Historical fixture differs from the original ledger: " + path)
    return body
