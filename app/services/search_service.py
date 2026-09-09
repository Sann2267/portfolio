"""Server-side search over cases, technologies, and pages. No external dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.content.registry import ContentRegistry
from app.models.project import Project
from app.utils.text import excerpt, strip_tags

_TOKEN = re.compile(r"[a-z0-9][a-z0-9+#./_-]*")
_MIN_PREFIX = 3

PAGES: tuple[tuple[str, str, str, str], ...] = (
    # (key, title, subtitle, searchable text)
    ("pages.home", "Investigation room", "Home", "room home investigator dossier board monitor"),
    ("projects.index", "All cases", "Case index", "cases projects index filter evidence board"),
    ("pages.skills", "Skills", "Page", "skills technologies capabilities stack"),
    ("pages.timeline", "Timeline", "Page", "timeline history chronology dates events"),
    ("pages.contact", "Contact", "Page", "contact email github reach out hire"),
)


@dataclass(frozen=True)
class SearchResult:
    kind: str  # case | technology | page
    key: str  # slug, technology name, or endpoint
    title: str
    subtitle: str
    snippet: str
    score: float


@dataclass
class _Doc:
    kind: str
    key: str
    title: str
    subtitle: str
    snippet: str
    fields: list[tuple[float, list[str]]] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


class SearchIndex:
    """A small weighted-field index built from a registry."""

    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.docs: list[_Doc] = []
        for project in registry.projects:
            self.docs.append(self._project_doc(project))
        for name in registry.technologies():
            self.docs.append(self._technology_doc(name))
        for key, title, subtitle, text in PAGES:
            self.docs.append(
                _Doc(
                    "page",
                    key,
                    title,
                    subtitle,
                    "",
                    [(3.0, tokenize(title)), (1.0, tokenize(text))],
                )
            )

    def _project_doc(self, project: Project) -> _Doc:
        taxonomy = self.registry.taxonomy
        category = taxonomy.category(project.category)
        category_name = category.label if category else ""
        node_terms: list[str] = []
        if project.architecture:
            for node in project.architecture.nodes:
                node_terms.append(node.label)
                if node.service:
                    node_terms.append(node.service)
                if node.description:
                    node_terms.append(node.description)
        claims = [c.text for c in project.highlights + project.results + project.challenges]
        body = " ".join(
            strip_tags(part)
            for part in (
                project.body.the_case,
                project.body.key_findings,
                project.body.result,
                *project.body.breakdown.values(),
            )
            if part
        )
        return _Doc(
            kind="case",
            key=project.slug,
            title=project.title,
            subtitle=f"{project.case_label} · {category.label if category else project.category}",
            snippet=excerpt(project.summary, 180),
            fields=[
                (8.0, tokenize(project.title)),
                (6.0, tokenize(" ".join(project.aliases))),
                (5.0, tokenize(" ".join(project.technologies + project.aws_services))),
                (4.0, tokenize(" ".join([project.category, *project.domains, category_name]))),
                (3.0, tokenize(" ".join(node_terms))),
                (2.0, tokenize(project.summary + " " + " ".join(claims))),
                (1.0, tokenize(body)),
            ],
        )

    def _technology_doc(self, name: str) -> _Doc:
        tech = self.registry.taxonomy.resolve(name)
        cases = self.registry.projects_for_technology(name)
        group = next(
            (g.label for g in self.registry.taxonomy.groups if tech and g.id == tech.group), ""
        )
        titles = ", ".join(p.title for p in cases)
        aliases = " ".join(tech.aliases) if tech else ""
        return _Doc(
            kind="technology",
            key=tech.name if tech else name,
            title=tech.name if tech else name,
            subtitle=f"Technology · {group}" if group else "Technology",
            snippet=f"Used in {len(cases)} case{'s' if len(cases) != 1 else ''}: {titles}",
            fields=[(7.0, tokenize(name) + tokenize(aliases)), (1.0, tokenize(titles))],
        )

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        terms = tokenize(query)
        if not terms:
            return []
        results: list[SearchResult] = []
        for doc in self.docs:
            score = 0.0
            for term in terms:
                term_score = 0.0
                for weight, tokens in doc.fields:
                    for token in tokens:
                        if token == term:
                            term_score += weight
                        elif len(term) >= _MIN_PREFIX and token.startswith(term):
                            term_score += weight * 0.5
                if term_score == 0.0:
                    score = 0.0
                    break
                score += term_score
            if score > 0.0:
                results.append(
                    SearchResult(doc.kind, doc.key, doc.title, doc.subtitle, doc.snippet, score)
                )
        results.sort(key=lambda r: (-r.score, r.kind, r.title.casefold()))
        return results[:limit]


_CACHE: dict[int, SearchIndex] = {}


def get_index(registry: ContentRegistry) -> SearchIndex:
    """One index per registry instance; rebuilt when the registry is reloaded."""
    key = id(registry)
    index = _CACHE.get(key)
    if index is None or index.registry is not registry:
        _CACHE.clear()
        index = _CACHE[key] = SearchIndex(registry)
    return index
