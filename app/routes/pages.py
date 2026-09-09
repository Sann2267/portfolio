"""Room, skills, timeline, contact, health."""

from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, render_template, request, url_for

from app import get_registry
from app.services.project_service import system_lines
from app.services.relation_service import board_links
from app.services.seo_service import build_meta

bp = Blueprint("pages", __name__)


@bp.get("/")
def home():
    registry = get_registry()
    meta = build_meta(
        current_app.config,
        title=current_app.config["SITE_NAME"],
        description=f"{registry.profile.headline}. {current_app.config['SITE_TAGLINE']}.",
        path=request.path,
    )
    return render_template(
        "pages/home.html",
        meta=meta,
        projects=registry.projects,
        counts=registry.counts_by_category(),
        categories=registry.taxonomy.categories,
        terminal=system_lines(registry),
        links=board_links(registry),
    )


@bp.get("/skills")
def skills():
    registry = get_registry()
    groups = [
        {
            "group": group,
            "skills": [
                {"skill": skill, "cases": registry.cases_for_skill(skill)} for skill in group.skills
            ],
        }
        for group in registry.skill_groups
    ]
    meta = build_meta(
        current_app.config,
        title="Skills",
        description="Technologies and capabilities, each linked to the cases that show them.",
        path=request.path,
    )
    return render_template("pages/skills.html", meta=meta, groups=groups)


@bp.get("/timeline")
def timeline():
    registry = get_registry()
    meta = build_meta(
        current_app.config,
        title="Timeline",
        description="Chronology of the cases and the events around them.",
        path=request.path,
    )
    return render_template("pages/timeline.html", meta=meta, events=registry.timeline)


@bp.get("/contact")
def contact():
    registry = get_registry()
    meta = build_meta(
        current_app.config,
        title="Contact",
        description=f"Reach {registry.profile.name} by e-mail or on GitHub.",
        path=request.path,
    )
    return render_template("pages/contact.html", meta=meta)


@bp.get("/healthz")
def healthz():
    registry = get_registry()
    return jsonify({"status": "ok", "cases": len(registry.projects)})


@bp.get("/robots.txt")
def robots():
    site = current_app.config["SITE_URL"]
    body = f"User-agent: *\nAllow: /\nDisallow: /search\nSitemap: {site}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    registry = get_registry()
    site = current_app.config["SITE_URL"]
    paths = [
        url_for("pages.home"),
        url_for("projects.index"),
        url_for("pages.skills"),
        url_for("pages.timeline"),
        url_for("pages.contact"),
    ]
    paths += [url_for("projects.detail", slug=p.slug) for p in registry.projects]
    seen: set[str] = set()
    for name in registry.technologies():
        tech = registry.taxonomy.resolve(name)
        slug = tech.slug if tech else name
        if slug not in seen:
            seen.add(slug)
            paths.append(url_for("projects.technology", name=slug))
    body = render_template("sitemap.xml", site=site, paths=paths)
    return Response(body, mimetype="application/xml")
