"""Holds the loaded registry for the running app and re-reads it when content changes."""

from __future__ import annotations

from pathlib import Path

from app.content.loader import load_registry
from app.content.registry import ContentRegistry


class ContentProvider:
    """Load once; in reload mode, rebuild when any file under ``content_dir`` changes."""

    def __init__(self, content_dir: Path | str, static_dir: Path | str | None, *, reload: bool) -> None:
        self.content_dir = Path(content_dir)
        self.static_dir = Path(static_dir) if static_dir else None
        self.reload = reload
        self._registry: ContentRegistry | None = None
        self._stamp: tuple[int, float] | None = None

    def _current_stamp(self) -> tuple[int, float]:
        files = [p for p in self.content_dir.rglob("*") if p.is_file()]
        newest = max((p.stat().st_mtime for p in files), default=0.0)
        return len(files), newest

    def get(self) -> ContentRegistry:
        if self._registry is None or (self.reload and self._current_stamp() != self._stamp):
            self.refresh()
        assert self._registry is not None
        return self._registry

    def refresh(self) -> ContentRegistry:
        self._registry = load_registry(self.content_dir, self.static_dir)
        self._stamp = self._current_stamp()
        return self._registry
