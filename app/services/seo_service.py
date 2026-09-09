"""Page metadata: title, description, canonical URL, Open Graph."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.models.project import Project
from app.utils.text import excerpt

DEFAULT_OG_IMAGE = "images/og-default.png"


@dataclass(frozen=True)
class PageMeta:
    title: str
    full_title: str
    description: str
    canonical: str
    og_image: str
    og_type: str = "website"
    robots: str | None = None


def build_meta(
    config: Mapping[str, object],
    *,
    title: str,
    description: str,
    path: str,
    image: str | None = None,
    og_type: str = "website",
    robots: str | None = None,
) -> PageMeta:
    site_name = str(config["SITE_NAME"])
    site_url = str(config["SITE_URL"]).rstrip("/")
    canonical_path = path.split("?", 1)[0] or "/"
    return PageMeta(
        title=title,
        full_title=f"{title} · {site_name}" if title != site_name else site_name,
        description=excerpt(description, 160),
        canonical=f"{site_url}{canonical_path}",
        og_image=f"{site_url}/static/{image or DEFAULT_OG_IMAGE}",
        og_type=og_type,
        robots=robots,
    )


def project_meta(config: Mapping[str, object], project: Project, path: str) -> PageMeta:
    description = (
        project.seo.description if project.seo and project.seo.description else None
    ) or project.summary
    image = project.seo.og_image if project.seo and project.seo.og_image else None
    return build_meta(
        config,
        title=f"{project.case_label} {project.title}",
        description=description,
        path=path,
        image=image,
        og_type="article",
    )
