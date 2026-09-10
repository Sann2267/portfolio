"""SEO and performance budget: metadata, sitemap, robots, asset weight, no third-party assets."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    return create_app("testing").test_client()


def test_every_page_has_complete_metadata(client, registry):
    paths = ["/", "/projects", "/skills", "/timeline", "/contact", "/search"]
    paths += [f"/projects/{p.slug}" for p in registry.projects]
    for path in paths:
        html = client.get(path).get_data(as_text=True)
        assert re.search(r"<title>[^<]+</title>", html), path
        assert '<meta name="description" content="' in html, path
        assert (
            f'<link rel="canonical" href="https://example.test{path if path != "/" else "/"}">'
            in html
        ), path
        for prop in ("og:type", "og:title", "og:description", "og:url", "og:image", "og:site_name"):
            assert f'property="{prop}"' in html, (path, prop)
        assert '<link rel="icon"' in html, path
        assert '<meta name="theme-color"' in html, path


def test_project_pages_use_project_specific_metadata(client, registry):
    project = registry.by_slug["esp32-aws-iot-monitoring"]
    html = client.get(f"/projects/{project.slug}").get_data(as_text=True)
    assert f"<title>{project.case_label} {project.title} · " in html
    assert project.seo.description in html
    assert 'property="og:type" content="article"' in html


def test_search_results_are_noindex_but_search_page_is_not(client):
    assert 'content="noindex"' in client.get("/search?q=x").get_data(as_text=True)
    assert 'content="noindex"' not in client.get("/search").get_data(as_text=True)


def test_sitemap_and_robots(client, registry):
    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert robots.mimetype == "text/plain"
    assert "Sitemap: https://example.test/sitemap.xml" in robots.get_data(as_text=True)

    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert sitemap.mimetype == "application/xml"
    xml = sitemap.get_data(as_text=True)
    for path in ("/", "/projects", "/skills", "/timeline", "/contact"):
        assert f"<loc>https://example.test{path}</loc>" in xml, path
    for project in registry.projects:
        assert f"<loc>https://example.test/projects/{project.slug}</loc>" in xml
    assert "<loc>https://example.test/technologies/aws-lambda</loc>" in xml
    assert "/search" not in xml


def test_og_image_exists_and_is_served(client):
    path = ROOT / "static" / "images" / "og-default.png"
    assert path.is_file()
    assert path.stat().st_size < 400_000
    assert client.get("/static/images/og-default.png").status_code == 200


def test_asset_budget_and_no_third_party_assets():
    css = sum(p.stat().st_size for p in (ROOT / "static" / "css").glob("*.css"))
    js_own = sum(p.stat().st_size for p in (ROOT / "static" / "js").glob("*.js"))
    htmx = (ROOT / "static" / "js" / "vendor" / "htmx.min.js").stat().st_size
    assert css < 80_000, css
    assert js_own < 40_000, js_own
    assert htmx < 60_000, htmx
    for template in (ROOT / "templates").rglob("*.html"):
        text = template.read_text(encoding="utf-8")
        assert not re.search(r'<(script|link)[^>]+(src|href)="https?://', text), template


def test_static_assets_are_cacheable(client):
    response = client.get("/static/css/tokens.css?v=abc")
    assert response.status_code == 200
    assert "max-age=" in response.headers.get("Cache-Control", "")


def test_static_versions_follow_file_content(client):
    """Vercel gives every file the same mtime, so the version must come from the bytes."""
    import hashlib

    html = client.get("/").get_data(as_text=True)
    versions = dict(re.findall(r'/static/((?:css|js)/[a-z]+\.(?:css|js))\?v=([0-9a-f]+)', html))
    assert len(versions) >= 6
    assert len(set(versions.values())) == len(versions)  # no two files share a version
    for name, version in versions.items():
        digest = hashlib.sha1((ROOT / "static" / name).read_bytes()).hexdigest()
        assert version == digest[:10], name
