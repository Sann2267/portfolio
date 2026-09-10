"""Cache-busted static URLs: ``/static/css/base.css?v=<content hash>``.

The version is a hash of the file's bytes, never its mtime. Deployment platforms such as
Vercel give every file the same constant mtime, so an mtime-based version would be identical
for every file and every deployment while the files are cached for a year: browsers would keep
an old stylesheet forever.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

from flask import current_app, url_for


@lru_cache(maxsize=256)
def _version(target: str, mtime_ns: int, size: int) -> str:
    """Short content hash. ``mtime_ns`` and ``size`` only key the cache so edits recompute."""
    digest = hashlib.sha1(Path(target).read_bytes(), usedforsecurity=False).hexdigest()
    return digest[:10]


def static_url(path: str) -> str:
    """URL for a file under ``static/`` with a version query derived from its content."""
    static_dir = Path(current_app.static_folder or "")
    target = static_dir / path
    try:
        stat = target.stat()
        version = _version(str(target), stat.st_mtime_ns, stat.st_size)
    except OSError:
        return url_for("static", filename=path)
    return url_for("static", filename=path, v=version)
