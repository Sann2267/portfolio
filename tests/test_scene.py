"""The case-room scene: hotspots, cutscene markup, honesty of the narration, decorative art."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app import create_app
from app.services.scene_service import DEFAULT_CUTSCENE, HOTSPOTS, cutscene_lines

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TARGETS = {
    "cabinet": "/skills",
    "rack": "#dossier-title",
    "board": "#board-title",
    "phone": "/contact",
    "folder": "/projects",
    "glass": "/search",
    "typewriter": "/timeline",
    "monitor": "#monitor",
}

FORBIDDEN_CLAIM_WORDS = ("uptime", "99.9", "certified", "certification", "revenue", " sla ")


@pytest.fixture(scope="module")
def home():
    app = create_app("testing")
    registry = app.extensions["content"].get()
    html = app.test_client().get("/").get_data(as_text=True)
    return html, registry


def test_scene_precedes_the_room_and_links_its_assets(home):
    html, _ = home
    assert html.index("data-scene") < html.index("room__dossier")
    for asset in ("css/scene.css", "js/scene.js", "js/audio.js", "css/room.css", "js/room.js"):
        assert f"/static/{asset}" in html, asset


def test_hotspots_are_real_links_with_labels(home):
    html, _ = home
    anchors = re.findall(
        r'<a class="scene__hot scene__hot--([a-z]+)" href="([^"]+)"( data-palette-open)?>'
        r'.*?<span class="scene__label">([^<]+)</span></a>',
        html,
        re.S,
    )
    assert {key: href for key, href, _, _ in anchors} == EXPECTED_TARGETS
    assert all(label.strip() for _, _, _, label in anchors)
    assert [key for key, _, palette, _ in anchors if palette] == ["glass"]
    buttons = re.findall(
        r'<button type="button" class="scene__hot scene__hot--([a-z]+)"'
        r' data-scene-action="([a-z]+)" aria-pressed="false">',
        html,
    )
    assert buttons == [("lamp", "labels")]
    assert len(anchors) + len(buttons) == len(HOTSPOTS) == 9
    assert "focusin" not in html  # behaviour lives in JS; every object is a real link or button


def test_anchor_targets_exist(home):
    html, _ = home
    for target in ('id="monitor"', 'id="board-title"', 'id="dossier-title"'):
        assert target in html, target


def test_controls_have_names_and_states(home):
    html, _ = home
    for action in ("skip", "replay", "sound"):
        assert f'type="button" class="btn btn--sm" data-scene-action="{action}"' in html, action
    assert 'data-scene-action="sound" aria-pressed="false"' in html
    assert 'href="#dossier-title">Enter the room' in html


def test_scene_heading_is_not_a_second_h1(home):
    html, _ = home
    assert '<h2 id="scene-title" class="sr-only">' in html
    assert html.count("<h1") == 1


def test_script_list_and_caption_band(home):
    html, registry = home
    script = re.search(r'<ol class="sr-only" data-scene-script>(.*?)</ol>', html, re.S).group(1)
    items = re.findall(r"<li>(.*?)</li>", script)
    assert items == cutscene_lines(registry.profile, len(registry.projects))
    assert items[-1].startswith(f"{len(registry.projects):02d} cases on file")
    assert '<p class="scene__caption mono" data-scene-caption aria-hidden="true"></p>' in html
    assert "aria-live" not in script


def test_art_is_decorative_and_class_coloured(home):
    source = (ROOT / "templates" / "partials" / "scene.svg").read_text(encoding="utf-8")
    assert 'class="scene__art"' in source and 'aria-hidden="true"' in source
    assert len(source.encode("utf-8")) < 25_000
    assert 'style="' not in source
    for value in re.findall(r'\b(?:fill|stroke)="([^"]+)"', source):
        assert re.fullmatch(r"none|currentColor|url\(#sc-[a-z-]+\)", value), value
    for ident in re.findall(r'\bid="([^"]+)"', source):
        assert ident.startswith("sc-"), ident
    html, _ = home
    rendered = re.search(r'<svg class="scene__art".*?</svg>', html, re.S).group(0)
    assert len(rendered.encode("utf-8")) < 30_000
    assert rendered.count('class="sc-hl__box') == 9


def test_captions_obey_honesty_rules(home):
    _, registry = home
    for line in (*registry.profile.cutscene, *DEFAULT_CUTSCENE):
        assert 0 < len(line) <= 90, line
        assert not any(ch.isdigit() for ch in line), line
        lowered = f" {line.lower()} "
        for word in FORBIDDEN_CLAIM_WORDS:
            assert word not in lowered, (word, line)


def test_scripts_and_styles_are_self_contained():
    scene_js = (ROOT / "static" / "js" / "scene.js").read_text(encoding="utf-8")
    audio_js = (ROOT / "static" / "js" / "audio.js").read_text(encoding="utf-8")
    scene_css = (ROOT / "static" / "css" / "scene.css").read_text(encoding="utf-8")
    assert "sessionStorage" in scene_js and "prefers-reduced-motion" in scene_js
    assert "AudioContext" in audio_js and "localStorage" in audio_js
    for forbidden in ("new Audio(", ".mp3", ".ogg", "fetch("):
        assert forbidden not in audio_js, forbidden
    assert "prefers-reduced-motion: reduce" in scene_css and ":has(" in scene_css
    assert "animation-delay" not in scene_css
