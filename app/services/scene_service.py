"""The case-room scene on the home page: the cutscene script and the clickable objects.

The drawing itself lives in ``templates/partials/scene.svg`` and its behaviour in
``static/js/scene.js``; this module only decides what the narration says and where each object
leads. It has no Flask imports, so the route resolves endpoint names to URLs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from app.content.registry import ContentRegistry

DEFAULT_CUTSCENE: tuple[str, ...] = (
    "Night. Rain on the glass. Somewhere a pipeline is still running.",
    "A case room. Every project here is a case; every architecture is evidence.",
    "Nothing on these walls claims more than the record supports.",
)
CLOSING_LINE = "{cases:02d} cases on file. The investigator is in. Choose an object to begin."
STATUS_LINE = "Click an object in the room, or scroll down to the case files."

HotspotKind = Literal["link", "anchor", "palette", "toggle"]


@dataclass(frozen=True)
class Hotspot:
    key: str
    label: str
    kind: HotspotKind
    target: str
    """Endpoint name for ``link``/``palette``, fragment for ``anchor``, action for ``toggle``."""
    icon: str


HOTSPOTS: tuple[Hotspot, ...] = (
    Hotspot("cabinet", "Evidence kit", "link", "pages.skills", "i-cabinet"),
    Hotspot("rack", "The investigator", "anchor", "#dossier-title", "i-hat"),
    Hotspot("board", "Investigation board", "anchor", "#board-title", "i-board"),
    Hotspot("phone", "Call the office", "link", "pages.contact", "i-phone"),
    Hotspot("folder", "Case files", "link", "projects.index", "i-folder"),
    Hotspot("glass", "Search the evidence", "palette", "search.search", "i-search"),
    Hotspot("typewriter", "Case log", "link", "pages.timeline", "i-typewriter"),
    Hotspot("lamp", "Show object labels", "toggle", "labels", "i-lamp"),
    Hotspot("monitor", "System status", "anchor", "#monitor", "i-monitor"),
)


def cutscene_lines(profile, cases: int) -> list[str]:
    """Narration lines: the profile's own lines (or the defaults) plus the factual closing line."""
    lines = list(profile.cutscene) or list(DEFAULT_CUTSCENE)
    return [*lines, CLOSING_LINE.format(cases=cases)]


def scene_model(registry: ContentRegistry, resolve: Callable[[str], str]) -> dict:
    """Plain view-model for the ``scene`` macro. ``resolve`` maps an endpoint name to a URL."""
    cases = len(registry.projects)
    hotspots = []
    for spot in HOTSPOTS:
        if spot.kind in ("link", "palette"):
            href = resolve(spot.target)
        elif spot.kind == "anchor":
            href = spot.target
        else:
            href = None
        hotspots.append(
            {
                "key": spot.key,
                "label": spot.label,
                "kind": spot.kind,
                "href": href,
                "icon": spot.icon,
                "action": spot.target if spot.kind == "toggle" else None,
            }
        )
    return {
        "captions": cutscene_lines(registry.profile, cases),
        "hotspots": hotspots,
        "status": STATUS_LINE,
    }
