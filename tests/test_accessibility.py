"""Accessibility checks over the rendered HTML of every page (stdlib parser, no browser)."""

from __future__ import annotations

from html.parser import HTMLParser

import pytest

from app import create_app

PAGES = [
    "/",
    "/projects",
    "/projects?category=iot",
    "/projects/technodev-devops-cicd",
    "/projects/esp32-aws-iot-monitoring",
    "/technologies/aws-lambda",
    "/skills",
    "/timeline",
    "/contact",
    "/search",
    "/search?q=lambda",
    "/nope",
]


class Audit(HTMLParser):
    """Collects the facts the assertions need."""

    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.lang = None
        self.imgs_without_alt: list[str] = []
        self.inputs: list[dict] = []
        self.labels_for: set[str] = set()
        self.label_depth = 0
        self.wrapped_inputs = 0
        self.buttons: list[dict] = []
        self.anchors: list[dict] = []
        self.current: dict | None = None
        self.text_stack: list[list[str]] = []
        self.aria_current = 0
        self.has_main = False
        self.has_skip = False
        self.svg_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img" and not a.get("alt"):
            self.imgs_without_alt.append(a.get("src", "?"))
        elif tag == "input" and a.get("type") != "hidden":
            self.inputs.append(
                {"id": a.get("id"), "wrapped": self.label_depth > 0, "aria": a.get("aria-label")}
            )
        elif tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        elif tag == "svg":
            self.svg_depth += 1
        elif tag in ("button", "a") and self.svg_depth == 0:
            self.current = {
                "tag": tag,
                "aria": a.get("aria-label"),
                "href": a.get("href"),
                "text": [],
            }
            self.text_stack.append(self.current["text"])
        elif tag == "main" and a.get("id") == "main":
            self.has_main = True
        if a.get("aria-current") == "page":
            self.aria_current += 1
        if tag == "a" and a.get("class", "").startswith("skip-link"):
            self.has_skip = True

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth -= 1
        elif tag == "svg":
            self.svg_depth -= 1
        elif tag in ("button", "a") and self.current and self.current["tag"] == tag:
            self.text_stack.pop()
            (self.buttons if tag == "button" else self.anchors).append(self.current)
            self.current = None

    def handle_data(self, data):
        if self.text_stack:
            self.text_stack[-1].append(data)


@pytest.fixture(scope="module")
def client():
    return create_app("testing").test_client()


@pytest.mark.parametrize("path", PAGES)
def test_page_structure(client, path):
    html = client.get(path).get_data(as_text=True)
    audit = Audit()
    audit.feed(html)
    assert audit.lang == "en"
    assert audit.h1 == 1, f"{path}: expected one h1, found {audit.h1}"
    assert audit.has_main and audit.has_skip, path
    assert not audit.imgs_without_alt, (path, audit.imgs_without_alt)
    for control in audit.inputs:
        labelled = control["wrapped"] or control["aria"] or control["id"] in audit.labels_for
        assert labelled, (path, control)
    for button in audit.buttons:
        assert button["aria"] or "".join(button["text"]).strip(), (path, "button without a name")
    for anchor in audit.anchors:
        assert anchor["href"], (path, "anchor without href")
        assert anchor["aria"] or "".join(anchor["text"]).strip(), (
            path,
            "link without a name",
            anchor["href"],
        )
    if path not in ("/nope", "/technologies/aws-lambda", "/search", "/search?q=lambda"):
        assert audit.aria_current == 1, (path, audit.aria_current)


def test_interactive_elements_have_keyboard_equivalents(client):
    html = client.get("/projects/technodev-devops-cicd").get_data(as_text=True)
    # diagram nodes are anchors (focusable) with accessible names, not bare <g> elements
    import re

    nodes = re.findall(r'<a class="arch__node[^>]*>', html)
    assert nodes and all("aria-label=" in node and 'href="#node-' in node for node in nodes)
    assert 'tabindex="-1"' in html  # main is programmatically focusable for the skip link
    assert html.count('<details class="fold" open>') >= 8  # sections collapse on small screens
    home = client.get("/").get_data(as_text=True)
    assert "focusin" not in home  # behaviour lives in JS, but every card is a real link
    assert home.count('class="case-card__title"><a href=') == 6


def test_reduced_motion_and_focus_styles_exist():
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "static" / "css" / "base.css").read_text(
        encoding="utf-8"
    )
    assert ":focus-visible" in css
    assert "prefers-reduced-motion: reduce" in css
