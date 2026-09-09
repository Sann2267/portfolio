"""Shared fixtures: the real content registry and a builder for throwaway content trees."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.content import ContentRegistry, load_registry

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"

MINIMAL_TAXONOMY = """
categories:
  - {id: cloud, label: Cloud}
  - {id: data, label: Data}
groups:
  - {id: language, label: Languages}
  - {id: aws, label: AWS services}
technologies:
  - {name: Python, group: language, aliases: [py]}
  - {name: AWS Lambda, group: aws, aliases: [Lambda]}
  - {name: Amazon S3, group: aws, aliases: [S3]}
"""

MINIMAL_PROFILE = """
name: Test Person
headline: Tester
specializations:
  - {category: cloud, label: Cloud, description: Cloud things}
contacts:
  - {kind: email, label: Email, value: test@example.com, primary: true}
"""

MINIMAL_SKILLS = """
groups:
  - id: cloud
    label: Cloud
    category: cloud
    skills:
      - {name: Serverless, technologies: [AWS Lambda]}
"""

PROJECT_TEMPLATE = """
id: case-{number:03d}
case_number: {number}
slug: {slug}
title: {title}
category: {category}
project_type: Test project
status: completed
summary: A test project.
technologies: [Python]
aws_services: [{services}]
highlights:
  - A highlight.
repository: {{status: unavailable}}
architecture:
  nodes:
    - {{id: a, label: A}}
    - {{id: b, label: B, service: AWS Lambda}}
  edges:
    - {{source: a, target: b}}
{extra}
"""

CASE_TEMPLATE = """
## The Case

Why this exists.

## Result

What happened.
"""


@dataclass
class ContentTree:
    """A temporary ``content/`` directory that tests can extend one project at a time."""

    root: Path
    static: Path

    def write_project(
        self,
        slug: str,
        number: int,
        *,
        title: str | None = None,
        category: str = "cloud",
        services: str = "AWS Lambda",
        extra: str = "",
        case_md: str = CASE_TEMPLATE,
        raw_yaml: str | None = None,
    ) -> Path:
        project_dir = self.root / "projects" / slug
        project_dir.mkdir(parents=True, exist_ok=True)
        text = raw_yaml or PROJECT_TEMPLATE.format(
            number=number,
            slug=slug,
            title=title or slug.replace("-", " ").title(),
            category=category,
            services=services,
            extra=textwrap.dedent(extra),
        )
        (project_dir / "project.yaml").write_text(text, encoding="utf-8")
        (project_dir / "case.md").write_text(case_md, encoding="utf-8")
        return project_dir

    def load(self) -> ContentRegistry:
        return load_registry(self.root, self.static)


@pytest.fixture
def content_tree(tmp_path: Path) -> ContentTree:
    root = tmp_path / "content"
    (root / "profile").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "timeline").mkdir()
    (root / "projects").mkdir()
    (root / "taxonomy.yaml").write_text(MINIMAL_TAXONOMY, encoding="utf-8")
    (root / "profile" / "profile.yaml").write_text(MINIMAL_PROFILE, encoding="utf-8")
    (root / "profile" / "intro.md").write_text("Hello **there**.\n", encoding="utf-8")
    (root / "skills" / "skills.yaml").write_text(MINIMAL_SKILLS, encoding="utf-8")
    static = tmp_path / "static"
    (static / "images").mkdir(parents=True)
    return ContentTree(root=root, static=static)


@pytest.fixture(scope="session")
def registry() -> ContentRegistry:
    """The real site content, loaded once per test session."""
    return load_registry(CONTENT_DIR, STATIC_DIR if STATIC_DIR.is_dir() else None)
