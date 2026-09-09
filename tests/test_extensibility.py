"""Adding a case is a content change only, and broken content fails with a clear location."""

from __future__ import annotations

import pytest

from app.content import ContentError, load_registry


def test_new_project_directory_is_enough(content_tree):
    content_tree.write_project("first-case", 1)
    assert [p.slug for p in content_tree.load().projects] == ["first-case"]

    content_tree.write_project("second-case", 2, category="data", services="Amazon S3")
    registry = content_tree.load()
    assert [p.slug for p in registry.projects] == ["first-case", "second-case"]
    related = registry.related("second-case")
    assert [r.project.slug for r in related] == ["first-case"]
    assert related[0].shared_technologies == ("Python",)


def test_projects_are_ordered_by_case_number_not_directory_name(content_tree):
    content_tree.write_project("zeta", 1)
    content_tree.write_project("alpha", 2)
    assert [p.slug for p in content_tree.load().projects] == ["zeta", "alpha"]


def test_aliases_resolve_to_canonical_names(content_tree):
    content_tree.write_project("aliased", 1, services="Lambda, S3")
    project = content_tree.load().projects[0]
    assert project.aws_services == ["AWS Lambda", "Amazon S3"]


def test_manual_related_override(content_tree):
    content_tree.write_project("one", 1)
    content_tree.write_project("two", 2)
    content_tree.write_project("three", 3, extra="related: [one]")
    registry = content_tree.load()
    assert [r.project.slug for r in registry.related("three")] == ["one"]


def test_case_sections_are_rendered(content_tree):
    content_tree.write_project(
        "sections",
        1,
        case_md="Intro.\n\n## The Case\n\nWhy.\n\n## Security\n\n- tls\n\n## Result\n\nDone.\n",
    )
    body = content_tree.load().projects[0].body
    assert "<p>Intro.</p>" in body.intro
    assert "Why." in body.the_case
    assert "<li>tls</li>" in body.breakdown["security"]
    assert body.breakdown.keys() == {"security"}


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ("technologies: [Python, Rust]", "unknown technology 'Rust'"),
        ("aws_services: [Python]", "not an AWS service"),
        ("category: nope", "unknown category 'nope'"),
        ("related: [ghost]", "related case 'ghost' does not exist"),
        ("body: {intro: x}", "generated from case.md"),
        (
            "evidence:\n  - {kind: screenshot, title: S, src: images/missing.webp, alt: x}",
            "not found",
        ),
    ],
)
def test_broken_project_names_the_file(content_tree, extra, message):
    project_dir = content_tree.write_project("broken", 1, extra=extra)
    with pytest.raises(ContentError) as info:
        content_tree.load()
    assert message in str(info.value)
    assert str(project_dir / "project.yaml") in str(info.value)


def test_unknown_case_section_is_rejected(content_tree):
    project_dir = content_tree.write_project("odd", 1, case_md="## Marketing\n\nx\n")
    with pytest.raises(ContentError, match="unknown section '## marketing'") as info:
        content_tree.load()
    assert str(project_dir / "case.md") in str(info.value)


def test_slug_must_match_directory(content_tree):
    yaml_text = """
id: case-001
case_number: 1
slug: other-name
title: X
category: cloud
project_type: T
status: completed
summary: S
"""
    content_tree.write_project("dir-name", 1, raw_yaml=yaml_text)
    with pytest.raises(ContentError, match="must equal directory name"):
        content_tree.load()


def test_duplicate_case_number_is_rejected(content_tree):
    content_tree.write_project("one", 1)
    content_tree.write_project("two", 1)
    with pytest.raises(ContentError, match="already used by 'one'"):
        content_tree.load()


def test_validation_error_reports_field_path(content_tree):
    content_tree.write_project("typo", 1, extra="statuss: done")
    with pytest.raises(ContentError) as info:
        content_tree.load()
    assert "statuss" in str(info.value)
    assert "Extra inputs" in str(info.value)


def test_missing_content_dir(tmp_path):
    with pytest.raises(ContentError, match="content directory not found"):
        load_registry(tmp_path / "nowhere")


def test_evidence_check_is_skipped_without_static_dir(content_tree):
    content_tree.write_project(
        "img", 1, extra="evidence:\n  - {kind: screenshot, title: S, src: images/x.webp, alt: x}"
    )
    registry = load_registry(content_tree.root)  # no static_dir
    assert registry.projects[0].evidence[0].src == "images/x.webp"
    (content_tree.static / "images" / "x.webp").write_bytes(b"RIFF")
    assert content_tree.load().projects[0].evidence_kinds == ["architecture", "screenshots"]
