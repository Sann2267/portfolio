"""Case index, the reusable case file renderer, and technology pages."""

from __future__ import annotations

from flask import Blueprint, abort, current_app, render_template, request

from app import get_registry
from app.services.project_service import (
    Filters,
    filter_options,
    filter_projects,
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
    return render_template(
        "projects/detail.html",
        meta=project_meta(current_app.config, project, request.path),
        project=project,
        sections=sections_for(project, registry),
        related=registry.related(project.slug),
        stack=stack_groups(project, registry.taxonomy),
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
