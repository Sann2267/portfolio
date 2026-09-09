"""Validate the content layer from the command line: ``python -m app.content [content_dir]``."""

from __future__ import annotations

import sys
from pathlib import Path

from app.content.errors import ContentError
from app.content.loader import load_registry


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[2]
    content_dir = Path(argv[1]) if len(argv) > 1 else root / "content"
    static_dir = root / "static" if (root / "static").is_dir() else None
    try:
        registry = load_registry(content_dir, static_dir)
    except ContentError as exc:
        print(f"CONTENT ERROR\n{exc}", file=sys.stderr)
        return 1

    print(f"content ok: {content_dir}")
    for project in registry.projects:
        related = ", ".join(r.project.slug for r in registry.related(project.slug))
        kinds = ", ".join(project.evidence_kinds) or "-"
        print(
            f"  {project.case_label}  {project.slug:<32} {project.status:<10} "
            f"repo={project.repository.status:<11} evidence=[{kinds}]"
        )
        if related:
            print(f"           related: {related}")
    stats = registry.stats()
    print(
        f"  {stats['cases']} cases, {stats['technologies']} technologies, "
        f"{stats['aws_services']} AWS services, {stats['timeline_events']} timeline events"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
