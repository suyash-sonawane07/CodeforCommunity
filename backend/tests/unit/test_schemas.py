"""Unit tests for the API contract schemas (request/response validation rules)."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    RequestCreate,
    ReviewActionCreate,
    SimulationCreate,
    EvidencePanel,
    NotImplementedResponse,
)


def test_request_create_happy_path_text():
    req = RequestCreate(channel="text", text="no bus after 5pm", consent_ack=True)
    assert req.channel == "text"


def test_request_create_rejects_missing_consent():
    with pytest.raises(ValidationError):
        RequestCreate(channel="text", text="hello", consent_ack=False)  # FR-005


def test_request_create_rejects_empty_text():
    with pytest.raises(ValidationError):
        RequestCreate(channel="text", text="   ", consent_ack=True)  # FR-006


def test_request_create_voice_requires_audio():
    with pytest.raises(ValidationError):
        RequestCreate(channel="voice", consent_ack=True)  # FR-006


def test_request_create_rejects_unknown_channel():
    with pytest.raises(ValidationError):
        RequestCreate(channel="fax", text="hello", consent_ack=True)


def test_request_create_rejects_bad_language_hint():
    with pytest.raises(ValidationError):
        RequestCreate(channel="text", text="x", language_hint="fr", consent_ack=True)


def test_review_action_requires_valid_action_and_note():
    ReviewActionCreate(action="approve", note="verified with field data")  # ok
    with pytest.raises(ValidationError):
        ReviewActionCreate(action="maybe", note="x")  # FR-059 tri-state only
    with pytest.raises(ValidationError):
        ReviewActionCreate(action="approve", note="")  # note required


def test_simulation_sector_allocations_accepted():
    sim = SimulationCreate(sector_allocations={"roads": 10.0, "water": 0})
    assert sim.sector_allocations["roads"] == 10.0


def test_evidence_panel_defaults_are_empty_not_fabricated():
    panel = EvidencePanel(
        cluster_id=1, issue_type="transport", independent_demand_count=0, raw_message_count=0
    )
    assert panel.uncertainty_notes == []
    assert panel.infrastructure_context is None  # no invented numbers (FR-052)


def test_not_implemented_envelope_shape():
    body = NotImplementedResponse().model_dump()
    assert body["error"]["code"] == "NOT_IMPLEMENTED"
