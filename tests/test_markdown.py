"""Markdown rendering and the case.md section splitter."""

from __future__ import annotations

import pytest

from app.content.markdown import (
    SECTION_ALIASES,
    known_section_keys,
    render_markdown,
    slugify_heading,
    split_sections,
)

SAMPLE = """Intro paragraph.

## The Case

Problem text.

## Key Findings

- one
- two

## Infrastructure

VPC details.
"""


def test_split_sections_keeps_intro_and_bodies():
    intro, sections = split_sections(SAMPLE)
    assert intro.strip() == "Intro paragraph."
    assert list(sections) == ["the-case", "key-findings", "infrastructure"]
    assert "Problem text." in sections["the-case"]
    assert "VPC details." in sections["infrastructure"]


def test_every_split_heading_maps_to_a_known_section():
    _, sections = split_sections(SAMPLE)
    for heading in sections:
        assert SECTION_ALIASES[heading] in known_section_keys()


def test_duplicate_heading_is_an_error():
    with pytest.raises(ValueError, match="duplicate section heading"):
        split_sections("## Result\n\na\n\n## Result\n\nb\n")


def test_slugify_heading():
    assert slugify_heading("  The Case ") == "the-case"
    assert slugify_heading("Key  Findings!") == "key-findings"


def test_render_markdown_tables_and_code():
    html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |\n\n```text\nx\n```\n")
    assert "<table>" in html
    assert "<code" in html


def test_render_markdown_empty():
    assert render_markdown("   \n") == ""
