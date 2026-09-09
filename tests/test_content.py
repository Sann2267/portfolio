"""The real site content: every case loads, validates, and satisfies the honesty rules."""

from __future__ import annotations

from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parents[1] / "content"

EXPECTED_SLUGS = [
    "indonesia-job-scraping",
    "job-listing-dashboard",
    "technodev-devops-cicd",
    "nusacommerce-analytics-platform",
    "multi-tenant-saas-infrastructure",
    "esp32-aws-iot-monitoring",
]


def test_six_cases_in_order(registry):
    assert [p.slug for p in registry.projects] == EXPECTED_SLUGS
    assert [p.case_number for p in registry.projects] == [1, 2, 3, 4, 5, 6]


def test_slug_matches_directory(registry):
    for project in registry.projects:
        assert (CONTENT_DIR / "projects" / project.slug / "project.yaml").is_file()
        assert (CONTENT_DIR / "projects" / project.slug / "case.md").is_file()


def test_every_case_has_the_required_narrative(registry):
    for project in registry.projects:
        assert project.summary
        assert project.highlights, project.slug
        assert project.body.the_case, f"{project.slug} needs a '## The Case' section"
        assert project.body.result, f"{project.slug} needs a '## Result' section"
        assert project.breakdown_sections, f"{project.slug} needs a technical breakdown"
        assert project.role and project.context and project.period, project.slug


def test_every_case_has_a_data_driven_architecture(registry):
    for project in registry.projects:
        assert project.has_architecture, project.slug
        arch = project.architecture
        assert len(arch.nodes) >= 5, project.slug
        assert len(arch.edges) >= 4, project.slug
        for node in arch.nodes:
            if node.service:
                assert registry.taxonomy.resolve(node.service), (project.slug, node.service)


def test_technologies_are_canonical_taxonomy_names(registry):
    names = {t.name for t in registry.taxonomy.technologies}
    for project in registry.projects:
        for name in project.technologies + project.aws_services:
            assert name in names, (project.slug, name)
        for name in project.aws_services:
            assert registry.taxonomy.resolve(name).group == "aws", (project.slug, name)


def test_link_states_follow_setting_md(registry):
    by_slug = registry.by_slug
    assert by_slug["technodev-devops-cicd"].repository.is_public
    assert by_slug["technodev-devops-cicd"].repository.url.startswith("https://github.com/")
    for slug in EXPECTED_SLUGS:
        project = by_slug[slug]
        for link in (project.repository, project.demo, project.documentation):
            if link.status != "public":
                assert link.note, f"{slug}: non-public links should explain themselves"
        assert not project.demo.is_public


def test_evidence_kinds_reflect_availability(registry):
    by_slug = registry.by_slug
    assert "code" in by_slug["technodev-devops-cicd"].evidence_kinds
    assert "code" not in by_slug["multi-tenant-saas-infrastructure"].evidence_kinds
    for project in registry.projects:
        assert "architecture" in project.evidence_kinds
        assert "technical_breakdown" in project.evidence_kinds
        assert "screenshots" not in project.evidence_kinds, "no screenshot assets exist yet"


def test_honesty_labels(registry):
    by_slug = registry.by_slug
    iot = by_slug["esp32-aws-iot-monitoring"]
    assert all(item.basis == "planned" for item in iot.future_work)
    assert any(item.basis == "user_statement" for item in iot.results)
    saas = by_slug["multi-tenant-saas-infrastructure"]
    assert {item.basis for item in saas.targets} == {"target"}
    planned_nodes = [n for n in iot.architecture.nodes if n.status == "planned"]
    assert len(planned_nodes) == 3


def test_cross_links_from_phase_06_examples(registry):
    def slugs(name: str) -> set[str]:
        return {p.slug for p in registry.projects_for_technology(name)}

    assert slugs("Kubernetes") == {"multi-tenant-saas-infrastructure"}
    assert {"technodev-devops-cicd", "nusacommerce-analytics-platform"} <= slugs("Lambda")
    assert "esp32-aws-iot-monitoring" in slugs("IoT Core")
    assert len(slugs("Python")) >= 4


def test_related_cases_exclude_self(registry):
    for project in registry.projects:
        related = registry.related(project.slug)
        assert 1 <= len(related) <= 3
        assert project.slug not in {r.project.slug for r in related}


def test_profile_and_skills(registry):
    profile = registry.profile
    assert profile.name == "Ibnu Adzim"
    assert profile.primary_contact.kind == "email"
    assert profile.intro and "<p>" in profile.intro
    category_ids = registry.taxonomy.category_ids
    assert {s.category for s in profile.specializations} <= category_ids
    for group in registry.skill_groups:
        for skill in group.skills:
            assert registry.cases_for_skill(skill), f"skill {skill.name!r} has no case evidence"


def test_timeline_is_merged_and_sorted(registry):
    dates = [e.date for e in registry.timeline]
    assert dates == sorted(dates, reverse=True)
    assert any(e.project is None for e in registry.timeline)
    assert {e.project for e in registry.timeline if e.project} <= set(EXPECTED_SLUGS)


def test_registry_stats(registry):
    stats = registry.stats()
    assert stats["cases"] == 6
    assert stats["aws_services"] >= 30
    counts = registry.counts_by_category()
    assert set(counts) == registry.taxonomy.category_ids
    assert counts["cloud"] >= 4
