"""The Project model: one case file, loaded from ``content/projects/<slug>/``."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from app.models.common import Claim, ClaimBasis, ContentModel, Link, Period, coerce_claims
from app.models.timeline import TimelineEvent

ProjectStatus = Literal["completed", "active", "experimental", "planned"]
EvidenceKind = Literal[
    "architecture", "screenshot", "diagram", "log", "document", "code", "demo", "note"
]
NodeStatus = Literal["implemented", "planned", "provided", "external", "not_documented"]
"""``provided`` marks components supplied by a module or third party rather than built."""

BREAKDOWN_SECTIONS: tuple[str, ...] = (
    "infrastructure",
    "application",
    "data",
    "security",
    "networking",
    "observability",
    "deployment",
)
NARRATIVE_SECTIONS: tuple[str, ...] = ("the_case", "key_findings", "result", "notes")


class Evidence(ContentModel):
    kind: EvidenceKind
    title: str = Field(min_length=1)
    src: str | None = Field(default=None, description="path under static/, e.g. images/x.webp")
    href: str | None = None
    alt: str | None = None
    caption: str | None = None
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    basis: ClaimBasis = "source"

    @model_validator(mode="after")
    def _check_image(self) -> Evidence:
        if self.src and not self.alt:
            raise ValueError("an evidence item with an image needs alt text")
        if self.href and not self.href.startswith(("http://", "https://", "/")):
            raise ValueError("href must be absolute or site-relative")
        return self


class ArchGroup(ContentModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    label: str
    description: str | None = None


class ArchNode(ContentModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    label: str
    service: str | None = Field(default=None, description="technology or AWS service name")
    category: str | None = None
    status: NodeStatus = "implemented"
    group: str | None = None
    description: str | None = None
    related_cases: list[str] = []


class ArchEdge(ContentModel):
    source: str
    target: str
    label: str | None = None
    direction: Literal["forward", "both", "none"] = "forward"
    protocol: str | None = None


class Architecture(ContentModel):
    groups: list[ArchGroup] = []
    nodes: list[ArchNode] = []
    edges: list[ArchEdge] = []

    @model_validator(mode="after")
    def _check_graph(self) -> Architecture:
        group_ids = [g.id for g in self.groups]
        if len(set(group_ids)) != len(group_ids):
            raise ValueError("duplicate architecture group id")
        node_ids = [n.id for n in self.nodes]
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("duplicate architecture node id")
        for node in self.nodes:
            if node.group is not None and node.group not in group_ids:
                raise ValueError(f"node {node.id!r} references unknown group {node.group!r}")
        for edge in self.edges:
            for end in (edge.source, edge.target):
                if end not in node_ids:
                    raise ValueError(
                        f"edge {edge.source}->{edge.target} references unknown node {end!r}"
                    )
        return self

    def node(self, node_id: str) -> ArchNode | None:
        return next((n for n in self.nodes if n.id == node_id), None)


class Seo(ContentModel):
    description: str | None = Field(default=None, max_length=200)
    og_image: str | None = None


class CaseBody(ContentModel):
    """Rendered HTML from ``case.md``. Populated by the loader, never by YAML."""

    intro: str | None = None
    the_case: str | None = None
    key_findings: str | None = None
    result: str | None = None
    notes: str | None = None
    breakdown: dict[str, str] = {}

    @field_validator("breakdown")
    @classmethod
    def _check_breakdown_keys(cls, value: dict[str, str]) -> dict[str, str]:
        unknown = set(value) - set(BREAKDOWN_SECTIONS)
        if unknown:
            raise ValueError(f"unknown breakdown section(s): {sorted(unknown)}")
        return value


class Project(ContentModel):
    id: str = Field(pattern=r"^case-\d{3}$")
    case_number: int = Field(ge=1, le=999)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    aliases: list[str] = []
    category: str = Field(description="primary category id from taxonomy")
    domains: list[str] = Field(default=[], description="category ids shown on the system monitor")
    project_type: str
    status: ProjectStatus
    role: str | None = None
    context: str | None = Field(default=None, description="origin, e.g. competition module")
    period: Period | None = None
    summary: str = Field(min_length=1, max_length=600)
    technologies: list[str] = []
    aws_services: list[str] = []
    highlights: list[Claim] = []
    challenges: list[Claim] = []
    solutions: list[Claim] = []
    results: list[Claim] = []
    targets: list[Claim] = []
    future_work: list[Claim] = []
    evidence: list[Evidence] = []
    gallery: list[Evidence] = []
    architecture: Architecture | None = None
    repository: Link = Link()
    demo: Link = Link()
    documentation: Link = Link()
    timeline: list[TimelineEvent] = []
    related: list[str] = Field(default=[], description="optional manual override of related slugs")
    seo: Seo | None = None
    body: CaseBody = CaseBody()

    _coerce = field_validator(
        "highlights", "challenges", "solutions", "results", "targets", "future_work", mode="before"
    )(coerce_claims)

    @model_validator(mode="after")
    def _check_case(self) -> Project:
        if int(self.id.split("-")[1]) != self.case_number:
            raise ValueError(f"id {self.id!r} does not match case_number {self.case_number}")
        for name in ("technologies", "aws_services", "aliases", "domains", "related"):
            values = getattr(self, name)
            if len({v.casefold() for v in values}) != len(values):
                raise ValueError(f"duplicate entries in {name}")
        if self.slug in self.related:
            raise ValueError("a project cannot relate to itself")
        for item in self.future_work:
            if item.basis not in ("planned", "not_documented"):
                raise ValueError("future_work items must have basis 'planned' (never completed)")
        return self

    # ---- derived helpers used by services and templates -----------------------------

    @property
    def case_label(self) -> str:
        return f"CASE #{self.case_number:03d}"

    @property
    def has_architecture(self) -> bool:
        return self.architecture is not None and bool(self.architecture.nodes)

    @property
    def breakdown_sections(self) -> list[str]:
        return [key for key in BREAKDOWN_SECTIONS if self.body.breakdown.get(key)]

    @property
    def evidence_kinds(self) -> list[str]:
        """Evidence types that can be shown, in display order."""
        kinds: list[str] = []
        if self.has_architecture or any(e.kind == "architecture" for e in self.evidence):
            kinds.append("architecture")
        if any(e.kind == "screenshot" and e.src for e in self.evidence + self.gallery):
            kinds.append("screenshots")
        if self.documentation.is_public or any(e.kind == "document" for e in self.evidence):
            kinds.append("documentation")
        if self.breakdown_sections:
            kinds.append("technical_breakdown")
        if self.demo.is_public:
            kinds.append("demo")
        if self.repository.is_public or any(e.kind == "code" for e in self.evidence):
            kinds.append("code")
        return kinds

    @property
    def evidence_level(self) -> dict[str, bool]:
        kinds = set(self.evidence_kinds)
        return {
            "documentation": "documentation" in kinds,
            "screenshots": "screenshots" in kinds,
            "repository": self.repository.is_public,
            "live_demo": self.demo.is_public,
        }

    @property
    def search_terms(self) -> list[str]:
        """Names the search and relation services index for this case."""
        terms = [self.title, *self.aliases, self.category, *self.domains, *self.technologies]
        terms += self.aws_services
        if self.architecture:
            terms += [n.label for n in self.architecture.nodes]
            terms += [n.service for n in self.architecture.nodes if n.service]
        return terms

    def to_summary(self) -> dict[str, Any]:
        """Small dict for cards, partials, and JSON endpoints."""
        return {
            "id": self.id,
            "case_label": self.case_label,
            "slug": self.slug,
            "title": self.title,
            "category": self.category,
            "status": self.status,
            "summary": self.summary,
            "technologies": list(self.technologies),
        }
