"""Markdown rendering and the ``## Section`` splitting used by ``case.md``."""

from __future__ import annotations

import re

import markdown as _markdown

from app.models.project import BREAKDOWN_SECTIONS, NARRATIVE_SECTIONS

_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "toc", "attr_list"]
_H2 = re.compile(r"^## +(.+?) *#* *$", re.MULTILINE)
_SLUG = re.compile(r"[^a-z0-9]+")

SECTION_ALIASES: dict[str, str] = {
    "the-case": "the_case",
    "case": "the_case",
    "key-findings": "key_findings",
    "findings": "key_findings",
    "result": "result",
    "results": "result",
    "notes": "notes",
    **{name: name for name in BREAKDOWN_SECTIONS},
}


def render_markdown(text: str) -> str:
    """Render trusted, repository-controlled Markdown to HTML."""
    if not text.strip():
        return ""
    return _markdown.markdown(text, extensions=_EXTENSIONS, output_format="html")


def slugify_heading(heading: str) -> str:
    return _SLUG.sub("-", heading.strip().casefold()).strip("-")


def split_sections(text: str) -> tuple[str, dict[str, str]]:
    """Split Markdown on level-2 headings.

    Returns ``(intro, {heading_slug: body})``. Heading slugs are matched against
    ``SECTION_ALIASES`` by the loader; unknown headings are a content error there.
    """
    matches = list(_H2.finditer(text))
    intro = text[: matches[0].start()] if matches else text
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        key = slugify_heading(match.group(1))
        if key in sections:
            raise ValueError(f"duplicate section heading {match.group(1)!r}")
        sections[key] = text[match.end() : end]
    return intro, sections


def known_section_keys() -> tuple[str, ...]:
    return NARRATIVE_SECTIONS + BREAKDOWN_SECTIONS
