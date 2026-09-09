"""Relationships between cases and technologies, derived from the registry."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.content.registry import ContentRegistry
from app.models.project import Project
from app.models.taxonomy import Technology


@dataclass(frozen=True)
class TechnologyView:
    technology: Technology
    group_label: str
    cases: tuple[Project, ...]
    related_technologies: tuple[tuple[str, int], ...]  # (name, number of shared cases)


def technology_view(registry: ContentRegistry, name: str) -> TechnologyView | None:
    """What a visitor sees when opening a technology: its cases and the technologies beside it."""
    tech = registry.taxonomy.resolve(name)
    if tech is None:
        return None
    cases = registry.projects_for_technology(tech.name)
    if not cases:
        return None
    group_label = next(
        (g.label for g in registry.taxonomy.groups if g.id == tech.group), tech.group
    )
    counts: Counter[str] = Counter()
    for project in cases:
        for other in project.technologies + project.aws_services:
            if other != tech.name:
                counts[other] += 1
    related = tuple(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].casefold()))[:12])
    return TechnologyView(tech, group_label, cases, related)


def board_links(registry: ContentRegistry, per_case: int = 2) -> list[tuple[str, str]]:
    """Undirected connector pairs for the board: each case to its top related cases."""
    pairs: set[tuple[str, str]] = set()
    for project in registry.projects:
        for related in registry.related(project.slug, limit=per_case):
            pair = tuple(sorted((project.slug, related.project.slug)))
            pairs.add(pair)  # type: ignore[arg-type]
    return sorted(pairs)


def shared_terms(a: Project, b: Project) -> list[str]:
    own = {t.casefold(): t for t in a.technologies + a.aws_services}
    return [own[t.casefold()] for t in b.technologies + b.aws_services if t.casefold() in own]
