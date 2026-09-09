"""Case catalog: filtering, filter options, section lists, stack grouping, room status."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

from app.content.registry import ContentRegistry
from app.models.project import Project
from app.models.taxonomy import Taxonomy

# Order of sections on a case page. Each renders only when `has_section` says it has content.
SECTION_TITLES: tuple[tuple[str, str], ...] = (
    ("the_case", "The Case"),
    ("evidence", "Evidence"),
    ("architecture", "Architecture"),
    ("breakdown", "Technical Breakdown"),
    ("key_findings", "Key Findings"),
    ("challenges", "Challenges and Solutions"),
    ("result", "Result"),
    ("stack", "Stack"),
    ("links", "Repository, Demo, Documentation"),
    ("related", "Related Cases"),
)

STATUS_LABELS = {
    "completed": "Completed",
    "active": "Active",
    "experimental": "Experimental",
    "planned": "Planned",
}


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    index: str


def has_section(project: Project, key: str, registry: ContentRegistry | None = None) -> bool:
    body = project.body
    match key:
        case "the_case":
            return bool(body.the_case or body.intro)
        case "evidence":
            return bool(project.evidence or project.gallery)
        case "architecture":
            return project.has_architecture
        case "breakdown":
            return bool(project.breakdown_sections)
        case "key_findings":
            return bool(body.key_findings or project.highlights)
        case "challenges":
            return bool(project.challenges or project.solutions)
        case "result":
            return bool(body.result or project.results or project.targets or project.future_work)
        case "stack":
            return bool(project.technologies or project.aws_services)
        case "links":
            return True
        case "related":
            return registry is not None and bool(registry.related(project.slug))
    return False


def sections_for(project: Project, registry: ContentRegistry | None = None) -> list[Section]:
    sections: list[Section] = []
    for key, title in SECTION_TITLES:
        if has_section(project, key, registry):
            sections.append(Section(key, title, f"{len(sections) + 1:02d}"))
    return sections


# ---- filtering ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Filters:
    category: str | None = None
    tech: str | None = None
    status: str | None = None
    q: str | None = None

    @classmethod
    def from_args(cls, args: Mapping[str, str]) -> Filters:
        def clean(name: str) -> str | None:
            value = (args.get(name) or "").strip()
            return value[:80] or None

        return cls(
            category=clean("category"), tech=clean("tech"), status=clean("status"), q=clean("q")
        )

    @property
    def active(self) -> bool:
        return any((self.category, self.tech, self.status, self.q))

    def as_dict(self) -> dict[str, str]:
        return {k: v for k, v in vars(self).items() if v}


def filter_projects(registry: ContentRegistry, filters: Filters) -> list[Project]:
    projects = list(registry.projects)
    if filters.category:
        wanted = filters.category.casefold()
        projects = [p for p in projects if wanted == p.category or wanted in p.domains]
    if filters.tech:
        tech = registry.taxonomy.resolve(filters.tech)
        wanted = (tech.name if tech else filters.tech).casefold()
        projects = [
            p
            for p in projects
            if any(name.casefold() == wanted for name in p.technologies + p.aws_services)
        ]
    if filters.status:
        projects = [p for p in projects if p.status == filters.status.casefold()]
    if filters.q:
        needle = filters.q.casefold()
        projects = [
            p
            for p in projects
            if any(needle in term.casefold() for term in [p.summary, *p.search_terms])
        ]
    return projects


def filter_options(registry: ContentRegistry, *, tech_limit: int = 24) -> dict[str, list]:
    categories = [
        {"id": c.id, "label": c.label, "count": len(registry.by_category.get(c.id, ()))}
        for c in registry.taxonomy.categories
        if registry.by_category.get(c.id)
    ]
    counts: Counter[str] = Counter()
    for project in registry.projects:
        counts.update(project.technologies)
        counts.update(project.aws_services)
    technologies = [
        {"name": name, "count": count}
        for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].casefold()))
    ][:tech_limit]
    statuses = Counter(p.status for p in registry.projects)
    return {
        "categories": categories,
        "technologies": technologies,
        "statuses": [
            {"id": status, "label": STATUS_LABELS.get(status, status), "count": count}
            for status, count in sorted(statuses.items())
        ],
    }


# ---- presentation helpers ----------------------------------------------------------------


def category_label(taxonomy: Taxonomy, category_id: str) -> str:
    category = taxonomy.category(category_id)
    return category.label if category else category_id


def stack_groups(project: Project, taxonomy: Taxonomy) -> list[tuple[str, list[str]]]:
    """Technologies and services grouped by taxonomy group, in taxonomy order."""
    by_group: dict[str, list[str]] = {}
    for name in project.technologies + project.aws_services:
        tech = taxonomy.resolve(name)
        group_id = tech.group if tech else "other"
        by_group.setdefault(group_id, []).append(tech.name if tech else name)
    labels = {g.id: g.label for g in taxonomy.groups}
    ordered = [g.id for g in taxonomy.groups if g.id in by_group]
    ordered += [g for g in by_group if g not in labels]
    return [(labels.get(g, "Other"), by_group[g]) for g in ordered]


def system_lines(registry: ContentRegistry) -> list[dict[str, str]]:
    """Terminal panel content for the room."""
    stats = registry.stats()
    active = sum(1 for p in registry.projects if p.status == "active")
    primary = max(registry.counts_by_category().items(), key=lambda kv: (kv[1], kv[0]))[0]
    return [
        {"key": "SYSTEM STATUS", "value": "ONLINE", "tone": "ok"},
        {"key": "CASES FOUND", "value": f"{stats['cases']:02d}", "tone": None},
        {
            "key": "PRIMARY DOMAIN",
            "value": category_label(registry.taxonomy, primary).upper(),
            "tone": None,
        },
        {"key": "AWS SERVICES", "value": f"{stats['aws_services']:02d} catalogued", "tone": None},
        {"key": "INVESTIGATION", "value": "ACTIVE" if active else "ARCHIVED", "tone": "active"},
    ]
