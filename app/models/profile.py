"""Investigator profile: who the developer is and how to reach them."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.models.common import ContentModel

ContactKind = Literal["email", "github", "linkedin", "website", "whatsapp", "instagram", "other"]


class Contact(ContentModel):
    kind: ContactKind
    label: str
    url: str | None = None
    value: str | None = Field(default=None, description="display value, e.g. the email address")
    primary: bool = False

    @model_validator(mode="after")
    def _check_target(self) -> Contact:
        if not self.url and not self.value:
            raise ValueError("a contact needs a url or a value")
        return self


class Specialization(ContentModel):
    category: str = Field(description="category id from taxonomy")
    label: str
    description: str


class Profile(ContentModel):
    name: str = Field(min_length=1)
    handle: str | None = None
    headline: str = Field(min_length=1, max_length=160)
    focus: list[str] = Field(default=[], description="short focus areas shown in the dossier")
    location: str | None = None
    languages: list[str] = []
    specializations: list[Specialization] = []
    contacts: list[Contact] = []
    intro: str | None = Field(default=None, description="HTML from intro.md, set by the loader")
    cutscene: list[str] = Field(
        default=[],
        max_length=5,
        description="opening narration of the home-page intro: 1-90 characters a line, no digits",
    )

    @field_validator("cutscene")
    @classmethod
    def _check_cutscene(cls, lines: list[str]) -> list[str]:
        cleaned = []
        for line in lines:
            text = line.strip()
            if not text:
                raise ValueError("cutscene lines must not be empty")
            if len(text) > 90:
                raise ValueError(f"cutscene line is longer than 90 characters: {text[:40]}...")
            if any(ch.isdigit() for ch in text):
                raise ValueError(
                    "cutscene lines carry no numbers; the case count is added from the "
                    f"registry: {text}"
                )
            cleaned.append(text)
        return cleaned

    @property
    def primary_contact(self) -> Contact | None:
        return next((c for c in self.contacts if c.primary), None) or (
            self.contacts[0] if self.contacts else None
        )
