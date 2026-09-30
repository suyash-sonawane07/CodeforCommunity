"""Phase 1 Acceptance Tests: Marathi citizen intake pipeline (FR-001..009).

Acceptance Criterion:
A Marathi sentence about no water supply returns:
- language=mr
- issue=water
- resolved location
- status=processed
- immutable raw_text storage
- extracted entities (location, urgency, etc.)
- consent_ack enforcement
"""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import CitizenRequest, ExtractedEntity

client = TestClient(app)


def test_phase1_marathi_water_intake_acceptance():
    """Verify Phase 1 acceptance criterion:

    Citizen submits a Marathi sentence about drinking water shortage in Demo Village 1:
    - language detected as 'mr'
    - issue classified as 'water'
    - location resolved to Demo Village 1
    - status marked as 'processed'
    - raw_text stored immutably
    - extracted entities persisted
    """
    marathi_text = "गावात पिण्याच्या पाण्याचा पुरवठा नाही. डेमो गाव 1 मध्ये 3 आठवड्यांपासून नळ बंद आहे."

    # 1. Post request with consent
    response = client.post(
        "/requests",
        json={
            "channel": "text",
            "text": marathi_text,
            "consent_ack": True,
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["status"] == "processed"
    assert data["issue_type"] == "water"
    assert "Demo Village 1" in str(data["location"]) or "डेमो गाव 1" in str(data["location"])
    assert data["reference_code"].startswith("CP-2026-")
    req_id = data["request_id"]
    ref_code = data["reference_code"]

    # 2. Check submission status by reference_code (FR-005)
    status_by_ref = client.get(f"/requests/{ref_code}")
    assert status_by_ref.status_code == 200
    ref_data = status_by_ref.json()
    assert ref_data["status"] == "processed"
    assert ref_data["language"] == "mr"
    assert ref_data["issue_type"] == "water"
    assert "Demo Village 1" in str(ref_data["location"]) or "डेमो गाव 1" in str(ref_data["location"])

    # 3. Check submission status by request_id
    status_by_id = client.get(f"/requests/{req_id}")
    assert status_by_id.status_code == 200
    id_data = status_by_id.json()
    assert id_data["status"] == "processed"
    assert id_data["language"] == "mr"
    assert id_data["issue_type"] == "water"

    # 4. Verify DB persistence: immutable raw_text and extracted entities
    db = SessionLocal()
    try:
        db_id = int(req_id.replace("req_", ""))
        req_row = db.query(CitizenRequest).filter(CitizenRequest.id == db_id).first()
        assert req_row is not None
        assert req_row.raw_text == marathi_text  # Immutable raw text
        assert req_row.consent_ack is True
        assert req_row.language == "mr"
        assert req_row.status == "processed"

        # Check extracted entities
        entities = db.query(ExtractedEntity).filter(ExtractedEntity.request_id == db_id).all()
        assert len(entities) > 0
        entity_types = {e.entity_type for e in entities}
        # Should have extracted location and/or urgency
        assert "location" in entity_types or "place" in entity_types
    finally:
        db.close()


def test_consent_ack_enforced():
    """Verify that requests without consent_ack are rejected (FR-005)."""
    response = client.post(
        "/requests",
        json={
            "channel": "text",
            "text": "There is a severe water leak near the municipal pump.",
            "consent_ack": False,
        },
    )
    assert response.status_code == 422
