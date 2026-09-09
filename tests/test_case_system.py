"""One renderer for every case: section order, omission of empty sections, cross-linking."""

from __future__ import annotations

import re

import pytest

from app import create_app
from app.services.project_service import SECTION_TITLES, sections_for


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


def section_ids(html: str) -> list[str]:
    return re.findall(r'<section class="section case__section" id="([a-z_]+)"', html)


def test_sections_follow_the_shared_order(client, registry):
    order = [key for key, _ in SECTION_TITLES]
    for project in registry.projects:
        html = client.get(f"/projects/{project.slug}").get_data(as_text=True)
        ids = section_ids(html)
        assert ids == [s.key for s in sections_for(project, registry)]
        assert ids == [key for key in order if key in ids]
        assert "links" in ids and "the_case" in ids


def test_sections_without_content_are_omitted(content_tree):
    content_tree.write_project(
        "bare",
        1,
        raw_yaml="""
id: case-001
case_number: 1
slug: bare
title: Bare case
category: cloud
project_type: T
status: completed
summary: Only a summary.
technologies: [Python]
repository: {status: deleted, note: gone}
""",
        case_md="## The Case\n\nText.\n",
    )
    app = create_app("testing", content_dir=content_tree.root)
    html = app.test_client().get("/projects/bare").get_data(as_text=True)
    assert section_ids(html) == ["the_case", "stack", "links"]
    assert "Deleted" in html
    assert '<a class="link-state__value"' not in html


def test_cross_links_from_case_to_technology_and_back(client):
    html = client.get("/projects/multi-tenant-saas-infrastructure").get_data(as_text=True)
    assert 'href="/technologies/kubernetes"' in html
    assert 'id="related"' in html
    assert html.count('class="case-card case-card--compact') >= 1

    tech = client.get("/technologies/Kubernetes").get_data(as_text=True)
    for slug in ("amazon-eks", "helm", "kubernetes-networkpolicy", "terraform"):
        assert f'href="/technologies/{slug}"' in tech, slug
    assert 'data-slug="multi-tenant-saas-infrastructure"' in tech


def test_claim_labels_appear_on_the_page(client):
    saas = client.get("/projects/multi-tenant-saas-infrastructure").get_data(as_text=True)
    assert "Target from specification" in saas
    iot = client.get("/projects/esp32-aws-iot-monitoring").get_data(as_text=True)
    assert "Implemented in project environment" in iot
    assert "Planned, not built" in iot
    assert iot.count("claim__basis--planned") == 3


def test_provided_components_are_described(client):
    devops = client.get("/projects/technodev-devops-cicd").get_data(as_text=True)
    assert "provided by the module" in devops
    nusa = client.get("/projects/nusacommerce-analytics-platform").get_data(as_text=True)
    assert "Scripts provided" in nusa or "provided" in nusa


def test_section_navigation_lists_every_rendered_section(client):
    html = client.get("/projects/nusacommerce-analytics-platform").get_data(as_text=True)
    nav = re.search(r'<nav class="case__nav"(.*?)</nav>', html, re.S).group(1)
    for key in section_ids(html):
        assert f'href="#{key}"' in nav
