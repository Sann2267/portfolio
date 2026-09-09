"""Every route resolves, templates render from the content layer, errors are case-file pages."""

from __future__ import annotations

import pytest

from app import create_app

EXPECTED_SLUGS = [
    "indonesia-job-scraping",
    "job-listing-dashboard",
    "technodev-devops-cicd",
    "nusacommerce-analytics-platform",
    "multi-tenant-saas-infrastructure",
    "esp32-aws-iot-monitoring",
]


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.parametrize(
    "path",
    ["/", "/projects", "/skills", "/timeline", "/contact", "/search", "/search?q=lambda"],
)
def test_core_routes_render(client, path):
    response = client.get(path)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<html" in html
    assert 'id="main"' in html


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "cases": 6}


@pytest.mark.parametrize("slug", EXPECTED_SLUGS)
def test_every_case_renders_through_one_template(client, app, slug):
    response = client.get(f"/projects/{slug}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    project = app.extensions["content"].get().by_slug[slug]
    assert project.title in html
    assert project.case_label in html
    for anchor in ("the_case", "architecture", "breakdown", "result", "stack", "links"):
        assert f'id="{anchor}"' in html, (slug, anchor)


def test_unknown_case_is_a_case_file_404(client):
    response = client.get("/projects/does-not-exist")
    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "CASE NOT FOUND" in html
    assert '<meta name="robots" content="noindex">' in html


def test_500_renders_the_interrupted_page():
    app = create_app("testing")
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.route("/__boom")
    def boom():
        raise RuntimeError("boom")

    response = app.test_client().get("/__boom")
    assert response.status_code == 500
    assert "INVESTIGATION INTERRUPTED" in response.get_data(as_text=True)


def test_technology_pages(client):
    response = client.get("/technologies/Kubernetes")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "multi-tenant-saas-infrastructure" in html
    assert "Seen alongside" in html
    assert client.get("/technologies/Lambda").status_code == 200  # alias resolves
    assert client.get("/technologies/Cobol").status_code == 404


def test_filters_narrow_the_index(client):
    def slugs(query: str) -> list[str]:
        html = client.get(f"/projects?{query}").get_data(as_text=True)
        return [s for s in EXPECTED_SLUGS if f'data-slug="{s}"' in html]

    assert slugs("category=iot") == ["esp32-aws-iot-monitoring"]
    assert slugs("tech=Kubernetes") == ["multi-tenant-saas-infrastructure"]
    assert slugs("tech=lambda") == [
        "technodev-devops-cicd",
        "nusacommerce-analytics-platform",
        "multi-tenant-saas-infrastructure",
    ]
    assert slugs("status=active") == ["indonesia-job-scraping", "job-listing-dashboard"]
    assert slugs("q=nusa") == ["nusacommerce-analytics-platform"]
    assert slugs("category=nope") == []
    assert "No case matches" in client.get("/projects?category=nope").get_data(as_text=True)


def test_htmx_requests_get_fragments(client):
    full = client.get("/projects?category=iot").get_data(as_text=True)
    fragment = client.get("/projects?category=iot", headers={"HX-Request": "true"}).get_data(
        as_text=True
    )
    assert "<html" in full
    assert "<html" not in fragment
    assert 'data-slug="esp32-aws-iot-monitoring"' in fragment

    results = client.get("/search?q=mqtt", headers={"HX-Request": "true"}).get_data(as_text=True)
    assert "<html" not in results
    assert "esp32-aws-iot-monitoring" in results


def test_search_page_and_empty_states(client):
    html = client.get("/search?q=zzzzzz").get_data(as_text=True)
    assert "No evidence found" in html
    assert client.get("/search?q=" + "x" * 500).status_code == 200


def test_meta_and_security_headers(client):
    response = client.get("/projects/technodev-devops-cicd")
    html = response.get_data(as_text=True)
    assert (
        '<link rel="canonical" href="https://example.test/projects/technodev-devops-cicd">' in html
    )
    assert 'property="og:title"' in html
    assert 'property="og:image" content="https://example.test/static/images/og-default.png"' in html
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Frame-Options"] == "DENY"


def test_static_assets_are_versioned_and_served(client):
    html = client.get("/").get_data(as_text=True)
    assert "/static/css/tokens.css?v=" in html
    assert client.get("/static/css/tokens.css").status_code == 200
    assert client.get("/static/js/vendor/htmx.min.js").status_code == 200


def test_links_never_render_broken_repositories(client):
    html = client.get("/projects/esp32-aws-iot-monitoring").get_data(as_text=True)
    assert "monitoring-suhu-dan-kelembapan" not in html
    assert "Unavailable" in html
