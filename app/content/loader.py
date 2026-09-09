"""Load ``content/`` into validated models and build the :class:`ContentRegistry`.

Layout expected under ``content_dir``::

    taxonomy.yaml
    profile/profile.yaml + intro.md
    skills/skills.yaml
    timeline/timeline.yaml
    projects/<slug>/project.yaml + case.md

Every failure is a :class:`ContentError` naming the file and, where possible, the field.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from app.content.errors import ContentError
from app.content.markdown import SECTION_ALIASES, render_markdown, split_sections
from app.content.registry import ContentRegistry
from app.models.profile import Profile
from app.models.project import BREAKDOWN_SECTIONS, CaseBody, Project
from app.models.skills import SkillGroup
from app.models.taxonomy import Taxonomy
from app.models.timeline import TimelineEvent

PROJECT_FILE = "project.yaml"
CASE_FILE = "case.md"

M = TypeVar("M", bound=BaseModel)


# ---- low-level helpers -----------------------------------------------------------------


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ContentError(path, "file not found")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ContentError(path, f"invalid YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ContentError(path, "top level must be a mapping")
    return data


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _validate(model: type[M], data: dict[str, Any], path: Path) -> M:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ContentError.from_validation_error(path, exc) from exc


# ---- pieces ----------------------------------------------------------------------------


def load_taxonomy(content_dir: Path) -> Taxonomy:
    path = content_dir / "taxonomy.yaml"
    return _validate(Taxonomy, _read_yaml(path), path)


def load_profile(content_dir: Path) -> Profile:
    path = content_dir / "profile" / "profile.yaml"
    data = _read_yaml(path)
    intro = _read_text(content_dir / "profile" / "intro.md")
    if "intro" in data:
        raise ContentError(path, "put the introduction in profile/intro.md, not in profile.yaml")
    data["intro"] = render_markdown(intro) or None
    return _validate(Profile, data, path)


def load_skill_groups(content_dir: Path) -> tuple[SkillGroup, ...]:
    path = content_dir / "skills" / "skills.yaml"
    data = _read_yaml(path)
    groups = data.get("groups")
    if not isinstance(groups, list):
        raise ContentError(path, "expected a top-level 'groups' list")
    result = tuple(_validate(SkillGroup, g, path) for g in groups)
    ids = [g.id for g in result]
    if len(set(ids)) != len(ids):
        raise ContentError(path, "duplicate skill group id")
    return result


def load_global_timeline(content_dir: Path) -> tuple[TimelineEvent, ...]:
    path = content_dir / "timeline" / "timeline.yaml"
    if not path.is_file():
        return ()
    data = _read_yaml(path)
    events = data.get("events", [])
    if not isinstance(events, list):
        raise ContentError(path, "'events' must be a list")
    return tuple(_validate(TimelineEvent, e, path) for e in events)


def _build_case_body(case_path: Path) -> CaseBody:
    text = _read_text(case_path)
    try:
        intro, sections = split_sections(text)
    except ValueError as exc:
        raise ContentError(case_path, str(exc)) from exc
    fields: dict[str, Any] = {"breakdown": {}}
    if intro.strip():
        fields["intro"] = render_markdown(intro)
    for heading_slug, body in sections.items():
        key = SECTION_ALIASES.get(heading_slug)
        if key is None:
            known = ", ".join(sorted(SECTION_ALIASES))
            raise ContentError(case_path, f"unknown section '## {heading_slug}'. Known: {known}")
        html = render_markdown(body)
        if not html:
            continue
        if key in BREAKDOWN_SECTIONS:
            fields["breakdown"][key] = html
        else:
            fields[key] = html
    return _validate(CaseBody, fields, case_path)


def _resolve_names(names: list[str], taxonomy: Taxonomy, path: Path, field: str) -> list[str]:
    resolved: list[str] = []
    for name in names:
        tech = taxonomy.resolve(name)
        if tech is None:
            raise ContentError(path, f"unknown technology {name!r}; add it to taxonomy.yaml", field)
        if field == "aws_services" and tech.group != "aws":
            raise ContentError(path, f"{name!r} is not an AWS service (group {tech.group!r})", field)
        if tech.name not in resolved:
            resolved.append(tech.name)
    return resolved


def load_project(project_dir: Path, taxonomy: Taxonomy, static_dir: Path | None = None) -> Project:
    path = project_dir / PROJECT_FILE
    data = _read_yaml(path)
    if "body" in data:
        raise ContentError(path, "'body' is generated from case.md and must not appear in YAML")
    data["technologies"] = _resolve_names(
        list(data.get("technologies") or []), taxonomy, path, "technologies"
    )
    data["aws_services"] = _resolve_names(
        list(data.get("aws_services") or []), taxonomy, path, "aws_services"
    )
    data["body"] = _build_case_body(project_dir / CASE_FILE).model_dump()
    project = _validate(Project, data, path)

    if project.slug != project_dir.name:
        raise ContentError(
            path, f"slug {project.slug!r} must equal directory name {project_dir.name!r}"
        )
    if project.category not in taxonomy.category_ids:
        raise ContentError(path, f"unknown category {project.category!r}", "category")
    for domain in project.domains:
        if domain not in taxonomy.category_ids:
            raise ContentError(path, f"unknown domain {domain!r}", "domains")
    if static_dir is not None:
        for item in project.evidence + project.gallery:
            if item.src and not (static_dir / item.src).is_file():
                raise ContentError(path, f"evidence file not found: static/{item.src}", "evidence")
    if project.architecture:
        for node in project.architecture.nodes:
            if node.service and taxonomy.resolve(node.service) is None:
                raise ContentError(
                    path, f"node {node.id!r} uses unknown service {node.service!r}", "architecture"
                )
    return project


def discover_project_dirs(content_dir: Path) -> list[Path]:
    root = content_dir / "projects"
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / PROJECT_FILE).is_file())


# ---- entry point -----------------------------------------------------------------------


def load_registry(content_dir: Path | str, static_dir: Path | str | None = None) -> ContentRegistry:
    """Load everything under ``content_dir`` and return a registry, or raise ContentError."""
    content_dir = Path(content_dir)
    static_path = Path(static_dir) if static_dir is not None else None
    if not content_dir.is_dir():
        raise ContentError(content_dir, "content directory not found")

    taxonomy = load_taxonomy(content_dir)
    projects = [load_project(d, taxonomy, static_path) for d in discover_project_dirs(content_dir)]
    _check_project_set(projects, content_dir)

    profile = load_profile(content_dir)
    for spec in profile.specializations:
        if spec.category not in taxonomy.category_ids:
            raise ContentError(
                content_dir / "profile" / "profile.yaml",
                f"unknown category {spec.category!r}",
                "specializations",
            )

    skill_groups = load_skill_groups(content_dir)
    skills_path = content_dir / "skills" / "skills.yaml"
    for group in skill_groups:
        if group.category and group.category not in taxonomy.category_ids:
            raise ContentError(skills_path, f"unknown category {group.category!r}", group.id)
        for skill in group.skills:
            for name in skill.technologies:
                if taxonomy.resolve(name) is None:
                    raise ContentError(skills_path, f"unknown technology {name!r}", skill.name)

    slugs = {p.slug for p in projects}
    events = list(load_global_timeline(content_dir))
    for event in events:
        if event.project and event.project not in slugs:
            raise ContentError(
                content_dir / "timeline" / "timeline.yaml", f"unknown project {event.project!r}"
            )
    for project in projects:
        events += [e.model_copy(update={"project": project.slug}) for e in project.timeline]
    events.sort(key=lambda e: (e.date, e.project or ""), reverse=True)

    return ContentRegistry(
        projects=tuple(projects),
        profile=profile,
        skill_groups=skill_groups,
        timeline=tuple(events),
        taxonomy=taxonomy,
    )


def _check_project_set(projects: list[Project], content_dir: Path) -> None:
    seen: dict[str, dict[Any, str]] = {"id": {}, "slug": {}, "case_number": {}}
    for project in projects:
        for key in seen:
            value = getattr(project, key)
            if value in seen[key]:
                raise ContentError(
                    content_dir / "projects" / project.slug / PROJECT_FILE,
                    f"{key} {value!r} already used by {seen[key][value]!r}",
                )
            seen[key][value] = project.slug
    slugs = {p.slug for p in projects}
    for project in projects:
        path = content_dir / "projects" / project.slug / PROJECT_FILE
        for slug in project.related:
            if slug not in slugs:
                raise ContentError(path, f"related case {slug!r} does not exist", "related")
        if project.architecture:
            for node in project.architecture.nodes:
                for slug in node.related_cases:
                    if slug not in slugs:
                        raise ContentError(
                            path,
                            f"node {node.id!r} relates to unknown case {slug!r}",
                            "architecture",
                        )
