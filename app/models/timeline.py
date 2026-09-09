"""Timeline events, shared by projects and the global timeline file."""

from __future__ import annotations

import re

from pydantic import Field, field_validator

from app.models.common import ClaimBasis, ContentModel, coerce_date_string

_EVENT_DATE = re.compile(r"^\d{4}(-\d{2}){0,2}$")


class TimelineEvent(ContentModel):
    date: str = Field(description="YYYY, YYYY-MM, or YYYY-MM-DD")
    title: str = Field(min_length=1)
    description: str | None = None
    basis: ClaimBasis = "source"
    project: str | None = Field(default=None, description="slug; set by the loader for case events")

    _coerce_date = field_validator("date", mode="before")(coerce_date_string)

    @field_validator("date")
    @classmethod
    def _check_date(cls, value: str) -> str:
        if not _EVENT_DATE.match(value):
            raise ValueError("date must be YYYY, YYYY-MM, or YYYY-MM-DD")
        return value
