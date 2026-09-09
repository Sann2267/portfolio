"""Cache-busted static URLs: ``/static/css/base.css?v=<mtime>``."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from flask import current_app, url_for


@lru_cache(maxsize=256)
def _version(path: str, mtime_ns: int) -> str:
    return f"{mtime_ns // 1_000_000:x}"


def static_url(path: str) -> str:
    """URL for a file under ``static/`` with a version query derived from its mtime."""
    static_dir = Path(current_app.static_folder or "")
    target = static_dir / path
    try:
        version = _version(path, target.stat().st_mtime_ns)
    except OSError:
        return url_for("static", filename=path)
    return url_for("static", filename=path, v=version)
