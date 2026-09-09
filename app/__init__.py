"""Flask application factory.

Layers: routes (blueprints) -> services -> content registry / models -> templates.
The content registry is loaded once at startup (and re-read on change in development)
and exposed through :func:`get_registry`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask, current_app, render_template, request

from app.content.errors import ContentError
from app.content.provider import ContentProvider
from app.content.registry import ContentRegistry
from config import ProductionConfig, get_config

NAV_ITEMS: tuple[tuple[str, str, str], ...] = (
    # (key, label, endpoint)
    ("home", "Room", "pages.home"),
    ("cases", "Cases", "projects.index"),
    ("skills", "Skills", "pages.skills"),
    ("timeline", "Timeline", "pages.timeline"),
    ("contact", "Contact", "pages.contact"),
)

THEME_COLOR = "#0b0c0e"  # browser chrome colour; kept out of templates on purpose

NAV_KEY_BY_BLUEPRINT = {
    "pages.home": "home",
    "projects": "cases",
    "pages.skills": "skills",
    "pages.timeline": "timeline",
    "pages.contact": "contact",
    "search": "search",
}


def create_app(
    config_name: str | None = None,
    *,
    content_dir: str | Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> Flask:
    config = get_config(config_name)
    if config is ProductionConfig:
        config.validate()

    app = Flask(
        __name__,
        template_folder=str(config.TEMPLATES_DIR),
        static_folder=str(config.STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_object(config)
    if content_dir is not None:
        app.config["CONTENT_DIR"] = Path(content_dir)
    if overrides:
        app.config.update(overrides)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    provider = ContentProvider(
        app.config["CONTENT_DIR"],
        app.config["STATIC_DIR"],
        reload=bool(app.config["CONTENT_RELOAD"]),
    )
    provider.get()  # fail fast: a broken content file must not reach a running server
    app.extensions["content"] = provider

    _register_blueprints(app)
    _register_errors(app)
    _register_context(app)
    _register_headers(app)
    return app


def get_registry() -> ContentRegistry:
    """The current content registry (re-read in development when files change)."""
    return current_app.extensions["content"].get()


# ---- wiring -----------------------------------------------------------------------------


def _register_blueprints(app: Flask) -> None:
    from app.routes.pages import bp as pages_bp
    from app.routes.projects import bp as projects_bp
    from app.routes.search import bp as search_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(search_bp)


def _register_errors(app: Flask) -> None:
    from app.services.seo_service import build_meta

    @app.errorhandler(404)
    def not_found(error):
        meta = build_meta(
            app.config,
            title="Case not found",
            description="No such file.",
            path=request.path,
            robots="noindex",
        )
        return render_template("errors/404.html", meta=meta, path=request.path), 404

    @app.errorhandler(500)
    def server_error(error):
        meta = build_meta(
            app.config,
            title="Investigation interrupted",
            description="Server error.",
            path=request.path,
            robots="noindex",
        )
        return render_template("errors/500.html", meta=meta), 500

    @app.errorhandler(ContentError)
    def content_error(error: ContentError):
        app.logger.error("content error: %s", error)
        meta = build_meta(
            app.config,
            title="Investigation interrupted",
            description="Content error.",
            path=request.path,
            robots="noindex",
        )
        return render_template(
            "errors/500.html", meta=meta, detail=str(error) if app.debug else None
        ), 500


def _register_context(app: Flask) -> None:
    from flask import url_for

    from app.services.project_service import category_label
    from app.utils.assets import static_url
    from app.utils.text import strip_tags

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        registry = get_registry()
        endpoint = request.endpoint or ""
        blueprint = request.blueprint or ""
        current = NAV_KEY_BY_BLUEPRINT.get(endpoint) or NAV_KEY_BY_BLUEPRINT.get(blueprint, "")
        return {
            "site": {
                "name": app.config["SITE_NAME"],
                "short_name": app.config["SITE_SHORT_NAME"],
                "tagline": app.config["SITE_TAGLINE"],
                "url": app.config["SITE_URL"],
            },
            "profile": registry.profile,
            "nav_links": [
                {"key": key, "label": label, "href": url_for(endpoint)}
                for key, label, endpoint in NAV_ITEMS
            ],
            "current_nav": current,
            "static_url": static_url,
            "tech_href": lambda name: url_for(
                "projects.technology", name=_tech_slug(registry, name)
            ),
            "category_label": lambda category_id: category_label(registry.taxonomy, category_id),
            "case_href": lambda slug: url_for("projects.detail", slug=slug),
            "registry_stats": registry.stats(),
            "registry_case": registry.get,
            "theme_color": THEME_COLOR,
        }

    app.jinja_env.filters["strip_tags"] = strip_tags


def _tech_slug(registry: ContentRegistry, name: str) -> str:
    from app.models.common import slugify

    tech = registry.taxonomy.resolve(name)
    return tech.slug if tech else slugify(name)


def _register_headers(app: Flask) -> None:
    @app.after_request
    def security_headers(response):
        if not app.config.get("SECURITY_HEADERS", True):
            return response
        headers = response.headers
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if not app.debug:
            headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                "font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
                "form-action 'self'",
            )
        return response
