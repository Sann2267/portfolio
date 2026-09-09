"""Architecture engine: deterministic layout, SVG rendering, node detail partials."""

from __future__ import annotations

import re

import pytest

from app import create_app
from app.models import Architecture
from app.services.diagram_service import NODE_H, NODE_W, PAD, Layout, build_layout


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


def _inside(node, group) -> bool:
    return (
        group.x <= node.x
        and node.x + node.w <= group.x + group.w
        and group.y <= node.y
        and node.y + node.h <= group.y + group.h
    )


def test_layout_places_every_node_inside_its_group_without_overlap(registry):
    for project in registry.projects:
        layout = build_layout(project.architecture)
        assert isinstance(layout, Layout)
        assert layout.width > 0 and layout.height > 0
        assert {n.id for n in layout.nodes} == {n.id for n in project.architecture.nodes}
        groups = {g.id: g for g in layout.groups}
        for node in layout.nodes:
            assert _inside(node, groups[node.group]), (project.slug, node.id)
        for a in layout.nodes:
            for b in layout.nodes:
                if a.id < b.id:
                    overlap = abs(a.x - b.x) < NODE_W and abs(a.y - b.y) < NODE_H
                    assert not overlap, (project.slug, a.id, b.id)
        assert len(layout.edges) == len(project.architecture.edges)
        for edge in layout.edges:
            assert edge.path.startswith("M") and " C " in edge.path


def test_layout_is_deterministic(registry):
    arch = registry.by_slug["nusacommerce-analytics-platform"].architecture
    assert build_layout(arch) == build_layout(arch)


def test_layout_wraps_groups_into_rows_and_handles_loose_nodes():
    arch = Architecture(
        groups=[{"id": f"g{i}", "label": f"G{i}"} for i in range(6)],
        nodes=[{"id": f"n{i}", "label": f"N{i}", "group": f"g{i}"} for i in range(6)]
        + [{"id": "loose", "label": "Loose"}],
        edges=[{"source": "n0", "target": "n5"}, {"source": "n2", "target": "n2"}],
    )
    layout = build_layout(arch, max_columns=4)
    rows = sorted({g.y for g in layout.groups})
    assert len(rows) == 2
    assert [g.id for g in layout.groups][-1] == "_components"
    assert layout.by_id["loose"].x >= PAD
    assert layout.neighbours("n0") == ["n5"]
    self_loop = next(e for e in layout.edges if e.source == e.target)
    assert self_loop.path.startswith("M")


def test_every_case_renders_an_svg_diagram(client, registry):
    for project in registry.projects:
        html = client.get(f"/projects/{project.slug}").get_data(as_text=True)
        assert '<svg class="arch__svg"' in html, project.slug
        assert html.count('class="arch__node ') == len(project.architecture.nodes), project.slug
        assert html.count('class="arch__edge ') == len(project.architecture.edges), project.slug
        assert 'id="arch-detail"' in html
        assert "Text version of the diagram" in html
        for node in project.architecture.nodes:
            assert f'id="node-{node.id}"' in html, (project.slug, node.id)
            assert f'data-detail-url="/projects/{project.slug}/nodes/{node.id}"' in html


def test_planned_nodes_are_marked(client):
    html = client.get("/projects/esp32-aws-iot-monitoring").get_data(as_text=True)
    assert html.count("arch__node--planned") == 3
    assert re.search(r'<text class="arch__node-status"[^>]*>planned</text>', html)


def test_node_detail_partial(client):
    response = client.get(
        "/projects/technodev-devops-cicd/nodes/lambda", headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<html" not in html
    assert 'data-node-detail="lambda"' in html
    assert "Function code provided by the module" in html
    assert 'href="/technologies/aws-lambda"' in html
    assert "Connections" in html and 'data-node-link="rds"' in html

    related = client.get("/projects/indonesia-job-scraping/nodes/dashboard").get_data(as_text=True)
    assert 'href="/projects/job-listing-dashboard"' in related

    assert client.get("/projects/technodev-devops-cicd/nodes/nope").status_code == 404
    assert client.get("/projects/nope/nodes/lambda").status_code == 404


def test_node_detail_without_htmx_is_still_a_fragment(client):
    html = client.get("/projects/esp32-aws-iot-monitoring/nodes/iot_core").get_data(as_text=True)
    assert "<html" not in html
    assert "AWS IoT Core" in html
