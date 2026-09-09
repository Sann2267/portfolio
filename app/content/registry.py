"""An immutable, in-memory view of all content plus the indices derived from it."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from app.models.profile import Profile
from app.models.project import Project
from app.models.skills import Skill, SkillGroup
from app.models.taxonomy import Taxonomy
from app.models.timeline import TimelineEvent

AWS_UMBRELLA = "AWS"  # the umbrella technology: matches any case that uses an AWS service
SHARED_TECHNOLOGY_WEIGHT = 1.0
SHARED_SERVICE_WEIGHT = 1.5
SAME_CATEGORY_WEIGHT = 1.0
SHARED_DOMAIN_WEIGHT = 0.5


def _freeze(table: dict[str, list[str]]) -> Mapping[str, tuple[str, ...]]:
    return MappingProxyType({key: tuple(value) for key, value in table.items()})


@dataclass(frozen=True)
class RelatedCase:
    project: Project
    score: float
    shared_technologies: tuple[str, ...]
    shared_services: tuple[str, ...]


@dataclass(frozen=True)
class ContentRegistry:
    """Everything the site knows, built once by :func:`app.content.loader.load_registry`."""

    projects: tuple[Project, ...]
    profile: Profile
    skill_groups: tuple[SkillGroup, ...]
    timeline: tuple[TimelineEvent, ...]
    taxonomy: Taxonomy
    by_slug: Mapping[str, Project] = field(init=False, repr=False)
    by_technology: Mapping[str, tuple[str, ...]] = field(init=False, repr=False)
    by_service: Mapping[str, tuple[str, ...]] = field(init=False, repr=False)
    by_category: Mapping[str, tuple[str, ...]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.projects, key=lambda p: p.case_number))
        object.__setattr__(self, "projects", ordered)
        object.__setattr__(self, "by_slug", MappingProxyType({p.slug: p for p in ordered}))
        tech: dict[str, list[str]] = defaultdict(list)
        service: dict[str, list[str]] = defaultdict(list)
        category: dict[str, list[str]] = defaultdict(list)
        for project in ordered:
            for name in project.technologies:
                tech[name].append(project.slug)
            for name in project.aws_services:
                service[name].append(project.slug)
            category[project.category].append(project.slug)
            for domain in project.domains:
                if domain != project.category:
                    category[domain].append(project.slug)
        object.__setattr__(self, "by_technology", _freeze(tech))
        object.__setattr__(self, "by_service", _freeze(service))
        object.__setattr__(self, "by_category", _freeze(category))

    # ---- lookups -----------------------------------------------------------------------

    def get(self, slug: str) -> Project | None:
        return self.by_slug.get(slug)

    def projects_for_technology(self, name: str) -> tuple[Project, ...]:
        tech = self.taxonomy.resolve(name)
        canonical = tech.name if tech else name
        if canonical == AWS_UMBRELLA:
            return tuple(p for p in self.projects if p.aws_services)
        slugs = self.by_technology.get(canonical, ()) + self.by_service.get(canonical, ())
        return tuple(self.by_slug[s] for s in dict.fromkeys(slugs))

    def projects_for_category(self, category_id: str) -> tuple[Project, ...]:
        return tuple(self.by_slug[s] for s in self.by_category.get(category_id, ()))

    def technologies(self) -> tuple[str, ...]:
        """Every technology or service used by at least one case, alphabetical."""
        names = set(self.by_technology) | set(self.by_service)
        return tuple(sorted(names, key=str.casefold))

    def cases_for_skill(self, skill: Skill) -> tuple[Project, ...]:
        found: dict[str, Project] = {}
        for name in skill.technologies:
            for project in self.projects_for_technology(name):
                found[project.slug] = project
        return tuple(sorted(found.values(), key=lambda p: p.case_number))

    # ---- relationships -----------------------------------------------------------------

    def related(self, slug: str, limit: int = 3) -> tuple[RelatedCase, ...]:
        """Cases related to ``slug``; a manual ``related`` list wins over the derived score."""
        project = self.by_slug[slug]
        if project.related:
            return tuple(
                RelatedCase(self.by_slug[s], 0.0, (), ())
                for s in project.related
                if s in self.by_slug
            )
        scored: list[RelatedCase] = []
        own_tech = {t.casefold(): t for t in project.technologies}
        own_svc = {s.casefold(): s for s in project.aws_services}
        for other in self.projects:
            if other.slug == slug:
                continue
            shared_t = tuple(
                own_tech[t.casefold()] for t in other.technologies if t.casefold() in own_tech
            )
            shared_s = tuple(
                own_svc[s.casefold()] for s in other.aws_services if s.casefold() in own_svc
            )
            score = len(shared_t) * SHARED_TECHNOLOGY_WEIGHT + len(shared_s) * SHARED_SERVICE_WEIGHT
            if other.category == project.category:
                score += SAME_CATEGORY_WEIGHT
            score += SHARED_DOMAIN_WEIGHT * len(set(other.domains) & set(project.domains))
            if score > 0:
                scored.append(RelatedCase(other, score, shared_t, shared_s))
        scored.sort(key=lambda r: (-r.score, r.project.case_number))
        return tuple(scored[:limit])

    # ---- summaries used by the room ----------------------------------------------------

    def counts_by_category(self) -> dict[str, int]:
        return {c.id: len(self.by_category.get(c.id, ())) for c in self.taxonomy.categories}

    def stats(self) -> dict[str, int]:
        return {
            "cases": len(self.projects),
            "technologies": len(self.by_technology),
            "aws_services": len(self.by_service),
            "timeline_events": len(self.timeline),
        }
