"""Building blocks shared by every content model.

Every model is ``extra="forbid"`` so a typo in a YAML key fails at load time
instead of silently disappearing, and ``frozen=True`` so the registry can hand
out instances without defensive copies.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LinkStatus = Literal["public", "private", "archived", "deleted", "unavailable"]
"""Source-code availability states from SETTING.md."""

ClaimBasis = Literal["source", "code", "user_statement", "target", "planned", "not_documented"]
"""What a statement rests on. Anything other than ``source``/``code`` is rendered with a label."""

CLAIM_BASIS_LABELS: dict[str, str] = {
    "source": "Documented",
    "code": "Verified in code",
    "user_statement": "Implemented in project environment",
    "target": "Target from specification",
    "planned": "Planned",
    "not_documented": "Not documented",
}

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """URL slug: lowercase, non-alphanumerics collapsed to single hyphens."""
    return _SLUG_STRIP.sub("-", value.casefold()).strip("-")


_DATE_PATTERNS = {
    "day": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "month": re.compile(r"^\d{4}-\d{2}$"),
    "year": re.compile(r"^\d{4}$"),
}


class ContentModel(BaseModel):
    """Base class: unknown keys are errors, instances are immutable."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Link(ContentModel):
    """A repository, demo, or documentation link with an availability state."""

    status: LinkStatus = "unavailable"
    url: str | None = None
    label: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _check_url(self) -> Link:
        if self.status == "public" and not self.url:
            raise ValueError("a link with status 'public' needs a url")
        if self.url and not self.url.startswith(("http://", "https://")):
            raise ValueError("url must be an absolute http(s) URL")
        return self

    @property
    def is_public(self) -> bool:
        return self.status == "public" and bool(self.url)

    @property
    def state_label(self) -> str:
        return self.label or self.status.capitalize()


class Claim(ContentModel):
    """A statement about a project together with what it is based on."""

    text: str = Field(min_length=1)
    basis: ClaimBasis = "source"
    note: str | None = None

    @property
    def basis_label(self) -> str:
        return CLAIM_BASIS_LABELS[self.basis]


def coerce_claims(value: Any) -> list[Any]:
    """Allow plain strings in YAML lists of claims (``basis`` defaults to ``source``)."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list")
    return [{"text": item} if isinstance(item, str) else item for item in value]


def coerce_date_string(value: Any) -> Any:
    """YAML parses ``2026-08-11`` as a date and ``2026`` as an int; keep them as strings."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return value


class Period(ContentModel):
    """When a project happened. ``end`` omitted means ongoing."""

    start: str
    end: str | None = None
    precision: Literal["day", "month", "year"] = "month"
    source: str | None = None

    _coerce_dates = field_validator("start", "end", mode="before")(coerce_date_string)

    @model_validator(mode="after")
    def _check_dates(self) -> Period:
        pattern = _DATE_PATTERNS[self.precision]
        for name in ("start", "end"):
            value = getattr(self, name)
            if value is not None and not pattern.match(value):
                raise ValueError(f"{name} {value!r} does not match precision {self.precision!r}")
        if self.end is not None and self.end < self.start:
            raise ValueError("end is before start")
        return self

    @property
    def is_ongoing(self) -> bool:
        return self.end is None
