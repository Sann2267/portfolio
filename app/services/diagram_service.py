"""Deterministic layout for architecture diagrams.

Groups become columns (wrapping into rows after ``MAX_COLUMNS``), nodes stack inside their
group in declaration order, and edges are cubic curves between node anchors. The output is
plain numbers that a Jinja macro turns into inline SVG, so the diagram is readable without
JavaScript and identical on every request.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.project import ArchEdge, Architecture

NODE_W = 172
NODE_H = 58
PAD = 14
LABEL_H = 28
NODE_GAP = 12
COL_GAP = 64
ROW_GAP = 40
MAX_COLUMNS = 4
OTHER_GROUP_ID = "_components"


@dataclass(frozen=True)
class PlacedGroup:
    id: str
    label: str
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class PlacedNode:
    id: str
    label: str
    service: str | None
    status: str
    description: str | None
    group: str
    x: float
    y: float
    w: float = NODE_W
    h: float = NODE_H

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass(frozen=True)
class PlacedEdge:
    id: str
    source: str
    target: str
    path: str
    label: str | None
    label_x: float
    label_y: float
    direction: str
    protocol: str | None


@dataclass(frozen=True)
class Layout:
    width: float
    height: float
    groups: tuple[PlacedGroup, ...]
    nodes: tuple[PlacedNode, ...]
    edges: tuple[PlacedEdge, ...]
    by_id: dict[str, PlacedNode] = field(default_factory=dict, repr=False)

    def connections(self, node_id: str) -> list[PlacedEdge]:
        return [e for e in self.edges if node_id in (e.source, e.target)]

    def neighbours(self, node_id: str) -> list[str]:
        seen: list[str] = []
        for edge in self.connections(node_id):
            other = edge.target if edge.source == node_id else edge.source
            if other != node_id and other not in seen:
                seen.append(other)
        return seen


def build_layout(arch: Architecture, max_columns: int = MAX_COLUMNS) -> Layout:
    groups = [(g.id, g.label) for g in arch.groups]
    members: dict[str, list] = {g.id: [] for g in arch.groups}
    loose = []
    for node in arch.nodes:
        if node.group and node.group in members:
            members[node.group].append(node)
        else:
            loose.append(node)
    if loose:
        groups.append((OTHER_GROUP_ID, "Components"))
        members[OTHER_GROUP_ID] = loose
    groups = [(gid, label) for gid, label in groups if members.get(gid)]

    group_w = NODE_W + 2 * PAD
    placed_groups: list[PlacedGroup] = []
    placed_nodes: list[PlacedNode] = []
    columns = max(1, min(max_columns, len(groups)))
    rows: list[list[tuple[str, str]]] = [
        groups[i : i + columns] for i in range(0, len(groups), columns)
    ]
    y = 0.0
    for row in rows:
        heights = [
            LABEL_H + 2 * PAD + len(members[gid]) * NODE_H + (len(members[gid]) - 1) * NODE_GAP
            for gid, _ in row
        ]
        row_h = max(heights)
        for col, (gid, label) in enumerate(row):
            x = col * (group_w + COL_GAP)
            placed_groups.append(PlacedGroup(gid, label, x, y, group_w, row_h))
            for index, node in enumerate(members[gid]):
                placed_nodes.append(
                    PlacedNode(
                        id=node.id,
                        label=node.label,
                        service=node.service,
                        status=node.status,
                        description=node.description,
                        group=gid,
                        x=x + PAD,
                        y=y + LABEL_H + PAD + index * (NODE_H + NODE_GAP),
                    )
                )
        y += row_h + ROW_GAP
    width = columns * group_w + (columns - 1) * COL_GAP
    height = max(y - ROW_GAP, 0.0)

    by_id = {n.id: n for n in placed_nodes}
    placed_edges = [
        _place_edge(index, edge, by_id[edge.source], by_id[edge.target])
        for index, edge in enumerate(arch.edges)
    ]
    return Layout(
        width, height, tuple(placed_groups), tuple(placed_nodes), tuple(placed_edges), by_id
    )


def _cubic(
    sx: float, sy: float, c1x: float, c1y: float, c2x: float, c2y: float, ex: float, ey: float
) -> str:
    return f"M{sx:.1f} {sy:.1f} C {c1x:.1f} {c1y:.1f}, {c2x:.1f} {c2y:.1f}, {ex:.1f} {ey:.1f}"


def _place_edge(index: int, edge: ArchEdge, s: PlacedNode, t: PlacedNode) -> PlacedEdge:
    if s.id == t.id:  # self loop: a small arc on the right side
        x, y = s.x + s.w, s.cy
        path = _cubic(x, y - 12, x + 40, y - 30, x + 40, y + 30, x, y + 12)
        return PlacedEdge(
            f"e{index}", s.id, t.id, path, edge.label, x + 34, y, edge.direction, edge.protocol
        )
    if t.x >= s.x + s.w:  # target to the right
        sx, sy, ex, ey = s.x + s.w, s.cy, t.x, t.cy
        dx = max(24.0, (ex - sx) / 2)
        path = _cubic(sx, sy, sx + dx, sy, ex - dx, ey, ex, ey)
    elif t.x + t.w <= s.x:  # target to the left
        sx, sy, ex, ey = s.x, s.cy, t.x + t.w, t.cy
        dx = max(24.0, (sx - ex) / 2)
        path = _cubic(sx, sy, sx - dx, sy, ex + dx, ey, ex, ey)
    elif t.y > s.y:  # same column, below
        sx, sy, ex, ey = s.cx, s.y + s.h, t.cx, t.y
        dy = max(16.0, (ey - sy) / 2)
        path = _cubic(sx, sy, sx, sy + dy, ex, ey - dy, ex, ey)
    else:  # same column, above
        sx, sy, ex, ey = s.cx, s.y, t.cx, t.y + t.h
        dy = max(16.0, (sy - ey) / 2)
        path = _cubic(sx, sy, sx, sy - dy, ex, ey + dy, ex, ey)
    label_x = (sx + ex) / 2
    label_y = (sy + ey) / 2 - 6
    return PlacedEdge(
        f"e{index}", s.id, t.id, path, edge.label, label_x, label_y, edge.direction, edge.protocol
    )
