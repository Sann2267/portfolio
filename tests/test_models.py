"""Unit tests for the content models' own validation rules."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.models import Architecture, Claim, Link, Period, Project, Taxonomy, TimelineEvent
from app.models.common import coerce_claims
from app.models.profile import Profile

BASE_PROJECT = {
    "id": "case-007",
    "case_number": 7,
    "slug": "sample-case",
    "title": "Sample",
    "category": "cloud",
    "project_type": "Test",
    "status": "completed",
    "summary": "Summary.",
}


class TestLink:
    def test_public_link_requires_url(self):
        with pytest.raises(ValidationError, match="needs a url"):
            Link(status="public")

    def test_url_must_be_absolute(self):
        with pytest.raises(ValidationError, match="absolute http"):
            Link(status="public", url="github.com/x")

    def test_unavailable_is_not_public(self):
        link = Link(status="unavailable", note="gone")
        assert not link.is_public
        assert link.state_label == "Unavailable"

    def test_public_with_url(self):
        link = Link(status="public", url="https://example.com", label="Repo")
        assert link.is_public
        assert link.state_label == "Repo"


class TestClaims:
    def test_plain_strings_become_claims(self):
        items = coerce_claims(["done", {"text": "planned", "basis": "planned"}])
        claims = [Claim.model_validate(i) for i in items]
        assert claims[0].basis == "source"
        assert claims[0].basis_label == "Documented"
        assert claims[1].basis_label == "Planned"

    def test_future_work_must_be_planned(self):
        with pytest.raises(ValidationError, match="future_work"):
            Project(**BASE_PROJECT, future_work=["already done"])

    def test_future_work_planned_is_accepted(self):
        project = Project(**BASE_PROJECT, future_work=[{"text": "later", "basis": "planned"}])
        assert project.future_work[0].basis == "planned"


class TestPeriod:
    def test_precision_must_match_value(self):
        with pytest.raises(ValidationError, match="precision"):
            Period(start="2026-08-11", precision="month")

    def test_end_before_start(self):
        with pytest.raises(ValidationError, match="before start"):
            Period(start="2026-08", end="2026-07")

    def test_ongoing_and_date_coercion(self):
        period = Period(start=date(2026, 8, 11), precision="day")
        assert period.start == "2026-08-11"
        assert period.is_ongoing

    def test_year_precision_accepts_int(self):
        assert Period(start=2026, precision="year").start == "2026"


class TestTimelineEvent:
    def test_date_object_is_coerced(self):
        event = TimelineEvent(date=date(2026, 9, 4), title="x")
        assert event.date == "2026-09-04"

    def test_bad_date_rejected(self):
        with pytest.raises(ValidationError, match="YYYY"):
            TimelineEvent(date="04-09-2026", title="x")


class TestArchitecture:
    def test_duplicate_node_id(self):
        with pytest.raises(ValidationError, match="duplicate architecture node"):
            Architecture(nodes=[{"id": "a", "label": "A"}, {"id": "a", "label": "B"}])

    def test_edge_to_unknown_node(self):
        with pytest.raises(ValidationError, match="unknown node 'z'"):
            Architecture(nodes=[{"id": "a", "label": "A"}], edges=[{"source": "a", "target": "z"}])

    def test_node_with_unknown_group(self):
        with pytest.raises(ValidationError, match="unknown group"):
            Architecture(nodes=[{"id": "a", "label": "A", "group": "nope"}])

    def test_planned_status_allowed(self):
        arch = Architecture(nodes=[{"id": "a", "label": "A", "status": "planned"}])
        assert arch.node("a").status == "planned"


class TestProject:
    def test_id_and_case_number_must_agree(self):
        with pytest.raises(ValidationError, match="does not match case_number"):
            Project(**{**BASE_PROJECT, "id": "case-001"})

    def test_unknown_field_is_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            Project(**BASE_PROJECT, tecnologies=["Python"])

    def test_slug_pattern(self):
        with pytest.raises(ValidationError):
            Project(**{**BASE_PROJECT, "slug": "Not A Slug"})

    def test_self_relation_rejected(self):
        with pytest.raises(ValidationError, match="relate to itself"):
            Project(**BASE_PROJECT, related=["sample-case"])

    def test_derived_properties(self):
        project = Project(
            **BASE_PROJECT,
            repository={"status": "public", "url": "https://example.com/repo"},
            architecture={"nodes": [{"id": "a", "label": "A"}]},
        )
        assert project.case_label == "CASE #007"
        assert project.has_architecture
        assert project.evidence_kinds == ["architecture", "code"]
        assert project.evidence_level["repository"] is True
        assert project.evidence_level["live_demo"] is False
        assert project.to_summary()["slug"] == "sample-case"


class TestProfile:
    def test_cutscene_defaults_empty(self):
        assert Profile(name="X", headline="Y").cutscene == []

    def test_cutscene_lines_are_stripped(self):
        profile = Profile(name="X", headline="Y", cutscene=["  Night. Rain.  "])
        assert profile.cutscene == ["Night. Rain."]

    def test_cutscene_rejects_numbers_blank_and_long_lines(self):
        with pytest.raises(ValidationError, match="no numbers"):
            Profile(name="X", headline="Y", cutscene=["99 cases solved"])
        with pytest.raises(ValidationError, match="empty"):
            Profile(name="X", headline="Y", cutscene=["   "])
        with pytest.raises(ValidationError, match="90 characters"):
            Profile(name="X", headline="Y", cutscene=["x" * 91])

    def test_more_than_five_lines_rejected(self):
        with pytest.raises(ValidationError):
            Profile(name="X", headline="Y", cutscene=["a"] * 6)


class TestTaxonomy:
    def test_alias_conflict_is_rejected(self):
        with pytest.raises(ValidationError, match="claimed by both"):
            Taxonomy(
                categories=[],
                groups=[{"id": "g", "label": "G"}],
                technologies=[
                    {"name": "A", "group": "g", "aliases": ["x"]},
                    {"name": "B", "group": "g", "aliases": ["X"]},
                ],
            )

    def test_resolve_is_case_insensitive(self):
        taxonomy = Taxonomy(
            categories=[{"id": "cloud", "label": "Cloud"}],
            groups=[{"id": "aws", "label": "AWS"}],
            technologies=[{"name": "AWS Lambda", "group": "aws", "aliases": ["Lambda"]}],
        )
        assert taxonomy.resolve("lambda").name == "AWS Lambda"
        assert taxonomy.resolve("aws lambda").name == "AWS Lambda"
        assert taxonomy.resolve("nope") is None
        assert taxonomy.category_ids == {"cloud"}
