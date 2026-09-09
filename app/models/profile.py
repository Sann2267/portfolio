"""Investigator profile: who the developer is and how to reach them."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

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

    @property
    def primary_contact(self) -> Contact | None:
        return next((c for c in self.contacts if c.primary), None) or (
            self.contacts[0] if self.contacts else None
        )
