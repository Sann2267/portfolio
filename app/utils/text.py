"""Text helpers for search snippets and meta descriptions."""

from __future__ import annotations

import html
import re

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def strip_tags(value: str | None) -> str:
    if not value:
        return ""
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", value))).strip()


def excerpt(value: str | None, limit: int = 160) -> str:
    text = strip_tags(value)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"
