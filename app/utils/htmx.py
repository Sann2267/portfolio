"""HTMX request detection: the same route serves a full page or a fragment."""

from __future__ import annotations

from flask import Request


def is_htmx(request: Request) -> bool:
    """True for requests made by htmx (or any client sending ``HX-Request: true``)."""
    return request.headers.get("HX-Request", "").lower() == "true" and not request.headers.get(
        "HX-Boosted"
    )
