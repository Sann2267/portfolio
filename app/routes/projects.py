"""Case index, the reusable case file renderer, and technology pages."""

from __future__ import annotations

from flask import Blueprint, abort, current_app, render_template, request, url_for

from app import get_registry
from app.services.diagram_service import build_layout
from app.services.project_service import (
    Filters,
    filter_options,
    filter_projects,
    quick_filters,
    sections_for,
    stack_groups,
)
from app.services.relation_service import technology_view
from app.services.seo_service import build_meta, project_meta
from app.utils.htmx import is_htmx

bp = Blueprint("projects", __name__)


@bp.get("/projects")
def index():
    registry = get_registry()
    filters = Filters.from_args(request.args)
    projects = filter_projects(registry, filters)
    context = {
        "projects": projects,
        "filters": filters,
        "options": filter_options(registry),
        "quick_filters": quick_filters(registry),
        "tech_label": _tech_label(registry, filters.tech),
        "total": len(registry.projects),
    }
    if is_htmx(request):
        return render_template("partials/project_grid.html", **context)
    meta = build_meta(
        current_app.config,
        title="Cases",
        description="Every case file: cloud, DevOps, backend, data, and IoT systems with evidence.",
        path=request.path,
    )
    return render_template("projects/index.html", meta=meta, **context)


@bp.get("/projects/<slug>")
def detail(slug: str):
    registry = get_registry()
    project = registry.get(slug)
    if project is None:
        abort(404)
    layout = build_layout(project.architecture) if project.has_architecture else None
    return render_template(
        "projects/detail.html",
        meta=project_meta(current_app.config, project, request.path),
        project=project,
        sections=sections_for(project, registry),
        related=registry.related(project.slug),
        stack=stack_groups(project, registry.taxonomy),
        layout=layout,
        node_detail_url=lambda node_id: url_for("projects.node_detail", slug=slug, node_id=node_id),
    )


@bp.get("/projects/<slug>/nodes/<node_id>")
def node_detail(slug: str, node_id: str):
    """Server-rendered fragment for one architecture component (drawer content)."""
    registry = get_registry()
    project = registry.get(slug)
    if project is None or not project.has_architecture:
        abort(404)
    arch = project.architecture
    node = arch.node(node_id)
    if node is None:
        abort(404)
    connections = []
    for edge in arch.edges:
        if edge.source == node.id and edge.target != node.id:
            connections.append((edge, arch.node(edge.target), True))
        elif edge.target == node.id and edge.source != node.id:
            connections.append((edge, arch.node(edge.source), False))
    group_label = next((g.label for g in arch.groups if g.id == node.group), "Component")
    related = [registry.by_slug[s] for s in node.related_cases if s in registry.by_slug]
    return render_template(
        "partials/node_detail.html",
        project=project,
        node=node,
        group_label=group_label,
        connections=connections,
        related=related,
    )


@bp.get("/technologies/<name>")
def technology(name: str):
    registry = get_registry()
    view = technology_view(registry, name)
    if view is None:
        abort(404)
    meta = build_meta(
        current_app.config,
        title=view.technology.name,
        description=f"{view.technology.name} appears in {len(view.cases)} case(s): "
        + ", ".join(p.title for p in view.cases),
        path=request.path,
    )
    return render_template("projects/technology.html", meta=meta, view=view)


def _tech_label(registry, name: str | None) -> str | None:
    if not name:
        return None
    tech = registry.taxonomy.resolve(name)
    return tech.name if tech else name
