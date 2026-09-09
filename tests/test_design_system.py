"""Design system contract: tokens exist, no raw colours outside tokens.css, macros render."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "static" / "css"
TEMPLATES = ROOT / "templates"

REQUIRED_TOKENS = [
    "--color-background",
    "--color-surface",
    "--color-surface-elevated",
    "--color-border",
    "--color-text-primary",
    "--color-text-secondary",
    "--color-text-muted",
    "--color-accent-active",
    "--color-accent-success",
    "--color-accent-warning",
    "--color-accent-danger",
    "--shadow-md",
    "--radius-md",
    "--space-4",
    "--text-base",
    "--dur-base",
    "--font-mono",
]

RAW_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")


def test_tokens_define_the_required_custom_properties():
    text = (CSS / "tokens.css").read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TOKENS if f"{token}:" not in text]
    assert not missing, missing


@pytest.mark.parametrize("name", ["base.css", "components.css"])
def test_no_raw_colours_outside_tokens(name):
    text = (CSS / name).read_text(encoding="utf-8")
    offenders = [line for line in text.splitlines() if RAW_COLOUR.search(line)]
    assert not offenders, offenders


def test_reduced_motion_is_supported():
    text = (CSS / "base.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in text
    assert "animation-duration: 0.001ms" in text


def test_templates_have_no_inline_styles_or_raw_colours():
    for path in TEMPLATES.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert 'style="' not in text, path
        assert not RAW_COLOUR.search(text), path


@pytest.fixture(scope="module")
def env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )


def render(env, source, **context):
    return env.from_string(source).render(**context)


def test_case_card_renders_evidence_and_badges(env, registry):
    project = registry.by_slug["technodev-devops-cicd"]
    html = render(
        env,
        '{% from "components/case_file.html" import case_card %}'
        "{{ case_card(project, '/projects/x', category_label='DevOps', tech_limit=3) }}",
        project=project,
    )
    assert 'data-slug="technodev-devops-cicd"' in html
    assert "CASE #003" in html
    assert 'data-evidence="code"' in html
    assert "status--completed" in html
    assert html.count('class="badge') >= 4  # three badges plus the +N overflow
    assert "badge--dim" in html


def test_badges_and_claims(env, registry):
    project = registry.by_slug["esp32-aws-iot-monitoring"]
    html = render(
        env,
        '{% from "components/badges.html" import claim_list, tech_badge, evidence_tag %}'
        "{{ claim_list(project.future_work) }}{{ tech_badge('ESP32', href='/t/ESP32') }}"
        "{{ evidence_tag('architecture') }}",
        project=project,
    )
    assert "claim__basis--planned" in html
    assert 'href="/t/ESP32"' in html
    assert "Architecture" in html


def test_link_or_state_never_renders_a_broken_anchor(env, registry):
    from app.models import Link

    macro = '{% from "components/links.html" import link_or_state %}'
    public = render(
        env,
        macro + "{{ link_or_state(link, 'Repo') }}",
        link=registry.by_slug["technodev-devops-cicd"].repository,
    )
    assert 'href="https://github.com/Sann2267/devops-learner-lab"' in public
    private = render(
        env, macro + "{{ link_or_state(link, 'Repo') }}", link=Link(status="private", note="n")
    )
    assert "href=" not in private
    assert "Private" in private


def test_terminal_metric_timeline_and_overlays(env, registry):
    html = render(
        env,
        '{% from "components/panels.html" import terminal_panel, metric_card, technical_note %}'
        '{% from "components/timeline.html" import timeline_node %}'
        '{% from "components/overlays.html" import command_palette, drawer %}'
        "{{ terminal_panel([{'key': 'STATUS', 'value': 'ONLINE', 'tone': 'ok'}], typing=True) }}"
        "{{ metric_card('Cases', 6, tone='active') }}"
        "{{ technical_note('Note', '<p>x</p>'|safe, tone='warning') }}"
        "<ul>{{ timeline_node(event) }}</ul>"
        "{{ command_palette([{'label': 'Open Skills', 'href': '/skills', 'kind': 'page'}],"
        " '/search') }}"
        "{% call drawer('d', 'Node') %}body{% endcall %}",
        event=registry.timeline[0],
    )
    for marker in (
        "terminal__value--ok",
        "cursor",
        "metric--active",
        "note--warning",
        "timeline__node",
        "data-palette",
        "drawer",
    ):
        assert marker in html, marker


def test_nav_marks_the_active_link(env):
    html = render(
        env,
        '{% from "components/nav.html" import nav %}'
        "{{ nav([{'key': 'home', 'label': 'Room', 'href': '/'},"
        " {'key': 'cases', 'label': 'Cases', 'href': '/projects'}], 'cases', handle='Sann2267') }}",
    )
    assert html.count('aria-current="page"') == 1
    assert "@Sann2267" in html
