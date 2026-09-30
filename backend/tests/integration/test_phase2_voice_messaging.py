"""Phase 2 Acceptance Tests: Voice ingestion and Messaging Webhooks (Telegram & WhatsApp).

Acceptance Criteria:
- POST /requests/{id}/audio stores audio file, transcribes with STT, creates RequestTranscription,
  processes through full intake pipeline, and marks request as processed.
- POST /webhooks/telegram handles text and voice messages, creating requests with channel=telegram
  and replying with a tracking reference code.
- Acceptance: a Telegram voice note results in a classified request visible in the DB.
- POST /webhooks/whatsapp receives Twilio format webhooks and reuses the shared intake handler.
"""

import io

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import CitizenRequest, ClusterMember, RequestTranscription

client = TestClient(app)


def test_audio_upload_transcription_and_pipeline():
    """Verify POST /requests/{id}/audio runs STT transcription and ingestion pipeline."""
    # 1. Create a request first
    create_res = client.post(
        "/requests",
        json={
            "channel": "text",
            "text": "Water pipeline burst report",
            "location_text": "Demo Village 1",
            "consent_ack": True,
        },
    )
    assert create_res.status_code == 201
    req_id = create_res.json()["request_id"]
    db_id = int(req_id.replace("req_", ""))

    # 2. Upload audio file to /requests/{id}/audio
    fake_audio_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00data\x00\x00\x00\x00"
    audio_file = io.BytesIO(fake_audio_bytes)

    upload_res = client.post(
        f"/requests/{req_id}/audio",
        files={"audio": ("recording.wav", audio_file, "audio/wav")},
    )
    assert upload_res.status_code == 200, upload_res.text
    upload_data = upload_res.json()
    assert upload_data["status"] == "processed"
    assert upload_data["audio_url"].startswith("/static/uploads/audio_")

    # 3. Check DB records
    db = SessionLocal()
    try:
        req = db.query(CitizenRequest).filter(CitizenRequest.id == db_id).first()
        assert req is not None
        assert req.status == "processed"
        assert req.audio_url == upload_data["audio_url"]
        assert req.transcript is not None

        # Verify RequestTranscription is recorded
        transcription = (
            db.query(RequestTranscription).filter(RequestTranscription.request_id == db_id).first()
        )
        assert transcription is not None
        assert transcription.transcript is not None
        assert transcription.stt_model == "whisper-base"

        # Verify cluster membership
        member = db.query(ClusterMember).filter(ClusterMember.request_id == db_id).first()
        assert member is not None
        assert member.cluster is not None
    finally:
        db.close()


def test_telegram_text_webhook():
    """Verify POST /webhooks/telegram handles incoming citizen text messages."""
    payload = {
        "update_id": 9001,
        "message": {
            "message_id": 101,
            "chat": {"id": 12345678, "type": "private"},
            "from": {"id": 12345678, "first_name": "Suresh"},
            "text": "गावात विजेची मोठी समस्या आहे. डीपी जळाली आहे.",
        },
    }

    res = client.post("/webhooks/telegram", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["ok"] is True
    assert data["status"] == "processed"
    assert data["reference_code"].startswith("CP-2026-")
    assert "Tracking Reference:" in data["text"]
    assert data["chat_id"] == 12345678
    assert data["issue_type"] in ["power", "water", "other"]

    # Verify DB
    db = SessionLocal()
    try:
        req_id = int(data["request_id"].replace("req_", ""))
        req = db.query(CitizenRequest).filter(CitizenRequest.id == req_id).first()
        assert req is not None
        assert req.channel == "telegram"
        assert req.status == "processed"
        assert req.raw_text == "गावात विजेची मोठी समस्या आहे. डीपी जळाली आहे."
    finally:
        db.close()


def test_phase2_telegram_voice_note_acceptance():
    """Phase 2 Acceptance: A Telegram voice note results in a classified request visible in DB."""
    payload = {
        "update_id": 9002,
        "message": {
            "message_id": 102,
            "chat": {"id": 87654321, "type": "private"},
            "from": {"id": 87654321, "first_name": "Pooja"},
            "voice": {
                "file_id": "voice_file_abc123",
                "duration": 5,
                "mime_type": "audio/ogg",
            },
        },
    }

    res = client.post("/webhooks/telegram", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["ok"] is True
    assert data["status"] == "processed"
    assert data["reference_code"].startswith("CP-2026-")
    assert data["issue_type"] is not None

    # Database verification
    db = SessionLocal()
    try:
        req_id = int(data["request_id"].replace("req_", ""))
        req = db.query(CitizenRequest).filter(CitizenRequest.id == req_id).first()
        assert req is not None, "CitizenRequest must be visible in DB"
        assert req.channel == "telegram"
        assert req.status == "processed"
        assert req.transcript is not None
        assert req.language is not None

        # Verify transcription record in DB
        transcription = (
            db.query(RequestTranscription).filter(RequestTranscription.request_id == req_id).first()
        )
        assert transcription is not None, "RequestTranscription must be persisted in DB"

        # Verify cluster member in DB
        member = db.query(ClusterMember).filter(ClusterMember.request_id == req_id).first()
        assert member is not None, "Request must be classified into a NeedsCluster"
        assert member.cluster.issue_type is not None
    finally:
        db.close()


def test_whatsapp_webhook_twilio_format():
    """Verify POST /webhooks/whatsapp receives Twilio form data and returns TwiML with tracking ID."""
    form_data = {
        "From": "whatsapp:+919876543210",
        "Body": "Road has deep potholes near the school in Demo Town 2",
        "NumMedia": "0",
    }

    res = client.post("/webhooks/whatsapp", data=form_data)
    assert res.status_code == 200, res.text
    assert "application/xml" in res.headers["content-type"]
    xml_content = res.text
    assert "<Response>" in xml_content
    assert "<Message>" in xml_content
    assert "CP-2026-" in xml_content

    # Verify DB
    db = SessionLocal()
    try:
        req = (
            db.query(CitizenRequest)
            .filter(
                CitizenRequest.channel == "whatsapp",
                CitizenRequest.raw_text == "Road has deep potholes near the school in Demo Town 2",
            )
            .order_by(CitizenRequest.id.desc())
            .first()
        )
        assert req is not None
        assert req.status == "processed"
        assert req.reference_code in xml_content
    finally:
        db.close()
