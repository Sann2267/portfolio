"""Controlled vocabulary: categories, technology groups, technologies and aliases."""

from __future__ import annotations

from functools import cached_property

from pydantic import ConfigDict, Field, model_validator

from app.models.common import ContentModel, slugify


class Category(ContentModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    label: str
    description: str | None = None


class TechGroup(ContentModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    label: str


class Technology(ContentModel):
    name: str = Field(min_length=1)
    group: str
    aliases: list[str] = []
    url: str | None = None

    @property
    def slug(self) -> str:
        return slugify(self.name)


class Taxonomy(ContentModel):
    # cached_property needs a writable __dict__; ignored_types keeps pydantic from
    # treating it as a field.
    model_config = ConfigDict(
        extra="forbid", frozen=True, ignored_types=(cached_property,), str_strip_whitespace=True
    )

    categories: list[Category]
    groups: list[TechGroup]
    technologies: list[Technology]

    @model_validator(mode="after")
    def _check_consistency(self) -> Taxonomy:
        cat_ids = [c.id for c in self.categories]
        if len(set(cat_ids)) != len(cat_ids):
            raise ValueError("duplicate category id")
        group_ids = {g.id for g in self.groups}
        if len(group_ids) != len(self.groups):
            raise ValueError("duplicate group id")
        seen: dict[str, str] = {}
        for tech in self.technologies:
            if tech.group not in group_ids:
                raise ValueError(f"technology {tech.name!r} uses unknown group {tech.group!r}")
            for key in (tech.name, *tech.aliases):
                folded = key.casefold()
                if folded in seen and seen[folded] != tech.name:
                    raise ValueError(
                        f"{key!r} is claimed by both {seen[folded]!r} and {tech.name!r}"
                    )
                seen[folded] = tech.name
        return self

    @cached_property
    def _lookup(self) -> dict[str, Technology]:
        table: dict[str, Technology] = {}
        for tech in self.technologies:
            for key in (tech.name, *tech.aliases):
                table[key.casefold()] = tech
                table[slugify(key)] = tech
        return table

    def resolve(self, name: str) -> Technology | None:
        """Return the canonical technology for a name, alias, or slug, or None."""
        key = name.strip().casefold()
        return self._lookup.get(key) or self._lookup.get(slugify(key))

    def category(self, category_id: str) -> Category | None:
        return next((c for c in self.categories if c.id == category_id), None)

    @property
    def category_ids(self) -> set[str]:
        return {c.id for c in self.categories}
