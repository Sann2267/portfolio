"""Errors raised by the content loader, always naming the file at fault."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError


class ContentError(Exception):
    """A content file is missing, malformed, or inconsistent with the rest of the content."""

    def __init__(self, path: Path | str, message: str, location: str | None = None) -> None:
        self.path = Path(path)
        self.location = location
        self.message = message
        where = f"{self.path}" + (f" [{location}]" if location else "")
        super().__init__(f"{where}: {message}")

    @classmethod
    def from_validation_error(cls, path: Path | str, exc: ValidationError) -> ContentError:
        lines = []
        for err in exc.errors():
            loc = ".".join(str(part) for part in err["loc"]) or "<root>"
            lines.append(f"{loc}: {err['msg']}")
        return cls(path, "\n  " + "\n  ".join(lines))
