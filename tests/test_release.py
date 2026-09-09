"""Phase 10 release checks: production config, extensibility end to end, secrets, safe links."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app import create_app

ROOT = Path(__file__).resolve().parents[1]

FAKE_PROJECT = """
id: case-007
case_number: 7
slug: temp-fake-case
title: Temporary Fake Case
category: cloud
domains: [cloud, devops]
project_type: Extensibility check
status: experimental
role: Test author
context: Created by the release test suite in a temporary directory.
period: {start: 2026-09, precision: month}
summary: A seventh case in a temporary content directory; the renderer needs no change.
technologies: [Python, Docker]
aws_services: [AWS Lambda, Amazon S3]
highlights:
  - Exists only inside a pytest temporary directory.
results:
  - {text: "Rendered through the unchanged case template.", basis: code}
repository: {status: archived, note: "Archived on purpose."}
architecture:
  groups:
    - {id: a, label: Alpha}
    - {id: b, label: Beta}
  nodes:
    - {id: n1, label: First, service: Python, group: a}
    - {id: n2, label: Second, service: AWS Lambda, group: b, status: planned}
  edges:
    - {source: n1, target: n2, label: calls}
timeline:
  - {date: 2026-09-09, title: "Fake case added by the test suite", basis: code}
"""

FAKE_CASE_MD = """## The Case

Temporary.

## Deployment

Nowhere.

## Result

Rendered.
"""


def test_fake_project_renders_everywhere_without_template_changes(tmp_path):
    content = tmp_path / "content"
    shutil.copytree(ROOT / "content", content)
    fake = content / "projects" / "temp-fake-case"
    fake.mkdir()
    (fake / "project.yaml").write_text(FAKE_PROJECT, encoding="utf-8")
    (fake / "case.md").write_text(FAKE_CASE_MD, encoding="utf-8")

    app = create_app("testing", content_dir=content)
    client = app.test_client()

    detail = client.get("/projects/temp-fake-case")
    assert detail.status_code == 200
    html = detail.get_data(as_text=True)
    assert "CASE #007" in html and "Temporary Fake Case" in html
    assert 'id="architecture"' in html and html.count('class="arch__node ') == 2
    assert "Archived" in html and 'id="deployment"' not in html  # breakdown lives under one id
    assert "breakdown-deployment" in html

    assert client.get("/").get_data(as_text=True).count('<article class="case-card') == 7
    assert 'data-slug="temp-fake-case"' in client.get("/projects?tech=docker").get_data(
        as_text=True
    )
    assert "temp-fake-case" in client.get("/search?q=temporary").get_data(as_text=True)
    assert "/projects/temp-fake-case" in client.get("/sitemap.xml").get_data(as_text=True)
    assert "Fake case added" in client.get("/timeline").get_data(as_text=True)
    assert client.get("/healthz").get_json()["cases"] == 7
    # the real registry is untouched
    assert create_app("testing").test_client().get("/healthz").get_json()["cases"] == 6


def test_production_config_requires_environment(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("SITE_URL", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY, SITE_URL"):
        create_app("production")

    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    monkeypatch.setenv("SITE_URL", "https://example.org/")
    app = create_app("production")
    assert not app.debug and not app.testing
    assert app.config["SECRET_KEY"] == "x" * 32
    assert app.config["SITE_URL"] == "https://example.org"
    response = app.test_client().get("/projects/technodev-devops-cicd")
    assert response.status_code == 200
    assert '<link rel="canonical" href="https://example.org/projects/technodev-devops-cicd">' in (
        response.get_data(as_text=True)
    )
    assert "Content-Security-Policy" in response.headers
    assert (
        "max-age=31536000"
        in app.test_client().get("/static/css/tokens.css").headers["Cache-Control"]
    )


def test_unknown_environment_is_rejected():
    with pytest.raises(RuntimeError, match="unknown APP_ENV"):
        create_app("staging")


SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(password|passwd|secret|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"),
]

ALLOWED_SECRET_LIKE = {"development-only-key", "testing-key", "ci-only-secret-key"}


def test_no_secrets_in_tracked_files():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    offenders = []
    for name in tracked:
        path = ROOT / name
        if path.suffix in {".png", ".webp", ".jpg", ".ico", ".woff2", ".pdf"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                if not any(allowed in match.group(0) for allowed in ALLOWED_SECRET_LIKE):
                    offenders.append((name, match.group(0)[:40]))
    assert not offenders, offenders
    assert ".env" not in tracked and "docs/sources/Modul - DevOps Automation.pdf" not in tracked


def test_external_links_open_safely():
    client = create_app("testing").test_client()
    for path in ("/", "/projects/technodev-devops-cicd", "/contact", "/skills"):
        html = client.get(path).get_data(as_text=True)
        for anchor in re.findall(r"<a [^>]*href=\"https?://[^>]*>", html):
            assert 'rel="noopener noreferrer"' in anchor, (path, anchor)


FORBIDDEN_CLAIM_WORDS = ("uptime", "99.9", "certified", "certification", "revenue", " sla ")


def test_no_unsupported_claims_in_content(registry):
    for project in registry.projects:
        texts = [project.summary, *(c.text for c in project.highlights + project.results)]
        for text in texts:
            lowered = f" {text.lower()} "
            for word in FORBIDDEN_CLAIM_WORDS:
                assert word not in lowered, (project.slug, word, text)


def test_sitemap_covers_every_public_route():
    app = create_app("testing")
    client = app.test_client()
    xml = client.get("/sitemap.xml").get_data(as_text=True)
    excluded = {"static", "pages.healthz", "pages.robots", "pages.sitemap", "search.search"}
    for rule in app.url_map.iter_rules():
        if rule.arguments or rule.endpoint in excluded or "GET" not in rule.methods:
            continue
        assert f"<loc>https://example.test{rule.rule}</loc>" in xml, rule.rule


def test_release_files_are_in_place():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert (
        "wsgi:app" in dockerfile and "USER portfolio" in dockerfile and "HEALTHCHECK" in dockerfile
    )
    assert "tests" in (ROOT / ".vercelignore").read_text(encoding="utf-8")
    assert 'entrypoint = "wsgi:app"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pytest" in ci and "ruff" in ci and "app.content" in ci
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in (
        "Local setup",
        "Project structure",
        "Adding a case",
        "Adding an architecture diagram",
        "Adding images",
        "Tests and checks",
        "Running in production",
    ):
        assert heading in readme, heading
    assert (ROOT / ".env.example").is_file()
    assert (ROOT / "docs" / "build" / "00_MASTER_BUILD.md").is_file()
