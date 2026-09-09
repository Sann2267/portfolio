"""Phase 08: search, filters, command palette, and technology discovery."""

from __future__ import annotations

import re

import pytest

from app import create_app
from app.services.search_service import get_index


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


def test_search_covers_every_required_field(registry):
    index = get_index(registry)

    def top(query: str) -> tuple[str, str]:
        results = index.search(query)
        assert results, query
        return results[0].kind, results[0].key

    assert top("TechnoDev") == ("case", "technodev-devops-cicd")  # title
    assert top("five-layer data platform")[1] == "nusacommerce-analytics-platform"  # description
    assert top("Terraform")[0] in ("technology", "case")  # technology
    assert any(
        r.key == "multi-tenant-saas-infrastructure" for r in index.search("Aurora")
    )  # AWS service
    assert any(r.key == "esp32-aws-iot-monitoring" for r in index.search("iot"))  # category
    assert any(
        r.key == "technodev-devops-cicd" for r in index.search("Self-hosted runners")
    )  # node
    assert any(r.key == "indonesia-job-scraping" for r in index.search("dedup"))  # keyword, prefix
    assert index.search("") == []
    assert index.search("qwertyuiop") == []


def test_search_results_link_to_cases_technologies_and_pages(client):
    html = client.get("/search?q=kubernetes").get_data(as_text=True)
    assert 'href="/projects/multi-tenant-saas-infrastructure"' in html
    assert 'href="/technologies/kubernetes"' in html
    page = client.get("/search?q=timeline").get_data(as_text=True)
    assert 'href="/timeline"' in page


def test_palette_markup_and_live_results(client, registry):
    html = client.get("/").get_data(as_text=True)
    assert '<dialog class="palette"' in html
    commands = re.findall(r'data-command data-label="([^"]+)"', html)
    for project in registry.projects:
        assert any(project.title.lower() in c for c in commands), project.title
    for label in ("open all cases", "open skills", "open timeline", "contact", "search"):
        assert any(label in c for c in commands), label
    assert 'src="/static/js/palette.js' in html

    fragment = client.get("/search?q=mqtt&partial=palette").get_data(as_text=True)
    assert "<html" not in fragment
    assert 'class="palette__item"' in fragment
    assert 'href="/projects/esp32-aws-iot-monitoring"' in fragment
    empty = client.get("/search?q=qwertyuiop&partial=palette").get_data(as_text=True)
    assert 'class="palette__empty"' in empty


def test_palette_is_not_the_only_navigation(client):
    html = client.get("/projects/esp32-aws-iot-monitoring").get_data(as_text=True)
    nav = re.search(r'<nav id="site-nav"(.*?)</nav>', html, re.S).group(1)
    for href in ("/", "/projects", "/skills", "/timeline", "/contact"):
        assert f'href="{href}"' in nav


def test_quick_filters_and_aws_filter(client):
    html = client.get("/projects").get_data(as_text=True)
    chips = re.search(r'<ul class="quick-filters"(.*?)</ul>', html, re.S).group(1)
    for tech in ("aws", "docker", "terraform", "kubernetes", "python", "aws-lambda"):
        assert f'href="/projects?tech={tech}"' in chips, tech

    aws = client.get("/projects?tech=aws").get_data(as_text=True)
    assert aws.count('<article class="case-card') == 4
    assert 'data-slug="indonesia-job-scraping"' not in aws
    docker = client.get("/projects?tech=Docker").get_data(as_text=True)
    assert docker.count('<article class="case-card') == 2


def test_technology_page_lists_cases_and_neighbours(client):
    html = client.get("/technologies/aws").get_data(as_text=True)
    assert html.count('<article class="case-card') == 4
    lam = client.get("/technologies/aws-lambda").get_data(as_text=True)
    assert 'href="/technologies/amazon-api-gateway"' in lam


def test_category_filter_links_from_the_room_and_case_pages(client):
    html = client.get("/projects/nusacommerce-analytics-platform").get_data(as_text=True)
    assert 'href="/projects?category=data"' in html
    filtered = client.get("/projects?category=data").get_data(as_text=True)
    assert filtered.count('<article class="case-card') == 3
