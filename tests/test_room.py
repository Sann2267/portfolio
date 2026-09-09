"""The investigation room: composition, board data attributes, monitor, terminal."""

from __future__ import annotations

import re

import pytest

from app import create_app
from app.services.relation_service import board_links


@pytest.fixture(scope="module")
def home():
    app = create_app("testing")
    registry = app.extensions["content"].get()
    html = app.test_client().get("/").get_data(as_text=True)
    return html, registry


def test_room_has_the_four_zones(home):
    html, _ = home
    for zone in ("room__dossier", "room__board", "room__monitor", "room__desk"):
        assert zone in html, zone
    assert 'rel="stylesheet" href="/static/css/room.css' in html
    assert 'src="/static/js/room.js' in html


def test_dossier_states_who_and_what(home):
    html, registry = home
    assert registry.profile.name in html
    assert registry.profile.headline in html
    for item in registry.profile.focus:
        assert item in html
    assert "Open the case files" in html


def test_board_lists_every_case_with_relationship_data(home):
    html, registry = home
    cards = re.findall(r'<article class="case-card[^"]*"\s+data-slug="([^"]+)"', html)
    assert cards == [p.slug for p in registry.projects]
    assert html.count('data-tech="') >= len(registry.projects)
    connectors = re.findall(r'class="board__line" data-from="([^"]+)" data-to="([^"]+)"', html)
    assert connectors == board_links(registry)
    assert len(connectors) >= 5
    assert 'data-board-status' in html


def test_cards_are_plain_links_not_a_puzzle(home):
    html, registry = home
    for project in registry.projects:
        assert f'href="/projects/{project.slug}"' in html


def test_monitor_and_terminal(home):
    html, registry = home
    counts = registry.counts_by_category()
    for category in registry.taxonomy.categories:
        if counts[category.id]:
            assert f'href="/projects?category={category.id}"' in html
            assert f"{counts[category.id]:02d}" in html
    for line in ("SYSTEM STATUS", "ONLINE", "CASES FOUND", "06", "PRIMARY DOMAIN", "INVESTIGATION"):
        assert line in html
