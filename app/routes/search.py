"""Global search: full page, or a results fragment for htmx and the command palette."""

from __future__ import annotations

from flask import Blueprint, current_app, render_template, request

from app import get_registry
from app.services.search_service import get_index
from app.services.seo_service import build_meta
from app.utils.htmx import is_htmx

bp = Blueprint("search", __name__)

MAX_QUERY = 100


@bp.get("/search")
def search():
    registry = get_registry()
    query = (request.args.get("q") or "").strip()[:MAX_QUERY]
    results = get_index(registry).search(query) if query else []
    context = {"query": query, "results": results}
    if is_htmx(request) or request.args.get("partial") == "1":
        return render_template("partials/search_results.html", **context)
    meta = build_meta(
        current_app.config,
        title=f"Search: {query}" if query else "Search",
        description="Search cases by title, technology, AWS service, category, or node.",
        path=request.path,
        robots="noindex" if query else None,
    )
    return render_template("pages/search.html", meta=meta, **context)
