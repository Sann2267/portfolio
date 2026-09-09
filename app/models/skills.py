"""Skills, grouped by domain. Cases per skill are derived by the registry."""

from __future__ import annotations

from pydantic import Field, model_validator

from app.models.common import ContentModel


class Skill(ContentModel):
    name: str = Field(min_length=1)
    technologies: list[str] = Field(default=[], description="taxonomy names this skill covers")
    note: str | None = None


class SkillGroup(ContentModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    label: str
    category: str | None = Field(default=None, description="category id when the group maps to one")
    description: str | None = None
    skills: list[Skill]

    @model_validator(mode="after")
    def _check_names(self) -> SkillGroup:
        names = [s.name.casefold() for s in self.skills]
        if len(set(names)) != len(names):
            raise ValueError(f"duplicate skill name in group {self.id!r}")
        return self
