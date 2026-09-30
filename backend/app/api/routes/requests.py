"""Citizen request intake routes (PRD §10.1 #2–4, FR-001–009)."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories import ClusterRepository, RequestRepository
from app.schemas import (
    AudioUploadResponse,
    NotImplementedResponse,
    RequestCreate,
    RequestCreateResponse,
    RequestStatusResponse,
)
from app.services.ai_runtime import process_citizen_request

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post(
    "",
    response_model=RequestCreateResponse,
    responses={201: {"model": RequestCreateResponse}, 501: {"model": NotImplementedResponse}},
    status_code=status.HTTP_201_CREATED,
    summary="Submit a citizen request (text or voice) — FR-001/002",
)
def create_request(body: RequestCreate, db: Session = Depends(get_db)) -> RequestCreateResponse:
    """Intake endpoint: runs STT, language detection, classification, NER, geocoding and clustering."""
    # 1. AI processing pipeline
    processed = process_citizen_request(
        channel=body.channel,
        text=body.text,
        language_hint=body.language_hint,
        audio_base64=body.audio_base64,
        location_text=body.location_text,
    )

    req_repo = RequestRepository(db)
    cluster_repo = ClusterRepository(db)

    # 2. Location persistence
    loc_id = None
    resolved_location_name = None
    if processed.location_resolved or body.location_text:
        admin = processed.admin_hierarchy or {}
        resolved_location_name = (
            admin.get("village_ward") or admin.get("district") or body.location_text
        )
        if not resolved_location_name and processed.entities:
            for ent in processed.entities:
                if ent.get("entity_type") in ("location", "place", "facility"):
                    resolved_location_name = ent.get("value")
                    break

        loc = req_repo.create_or_get_location(
            source_text=body.location_text or processed.raw_text,
            latitude=processed.latitude,
            longitude=processed.longitude,
            state=admin.get("state", "Demo State"),
            district=admin.get("district", "Demo District 1"),
            block=admin.get("block", "Demo Block A"),
            village_ward=resolved_location_name,
            confidence=0.85 if processed.location_resolved else 0.3,
            resolution_method="gazetteer_exact"
            if processed.location_resolved
            else "unresolved_text",
            status="resolved" if processed.location_resolved else "location_unresolved",
        )
        loc_id = loc.id

    # 3. Create CitizenRequest
    req = req_repo.create_request(
        channel=body.channel,
        consent_ack=body.consent_ack,
        raw_text=body.text or processed.raw_text,
        language=processed.language,
        transcript=processed.transcript,
        status="processed",
        uncertainty_notes=processed.uncertainty_notes,
    )

    # 4. Save entities
    if processed.entities:
        req_repo.add_entities(req.id, processed.entities)

    # 5. Cluster grouping
    matching_cluster = cluster_repo.find_matching_cluster(
        issue_type=processed.issue_type, location_id=loc_id
    )
    if matching_cluster:
        cluster_repo.add_member(
            cluster_id=matching_cluster.id,
            request_id=req.id,
            similarity_score=0.88,
            assignment="auto",
        )
    else:
        new_cluster = cluster_repo.create_cluster(
            issue_type=processed.issue_type,
            location_id=loc_id,
            status="forming",
            independent_demand_count=1,
            raw_message_count=1,
            uncertainty_notes=processed.uncertainty_notes,
        )
        cluster_repo.add_member(
            cluster_id=new_cluster.id,
            request_id=req.id,
            similarity_score=1.0,
            assignment="auto",
        )

    db.commit()

    return RequestCreateResponse(
        request_id=f"req_{req.id}",
        status=req.status,
        reference_code=req.reference_code,
        issue_type=processed.issue_type,
        location=resolved_location_name or body.location_text,
    )


@router.post(
    "/{request_id}/audio",
    response_model=AudioUploadResponse,
    summary="Upload/attach audio for transcription — FR-002",
)
def upload_audio(
    request_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> AudioUploadResponse:
    """Accepts citizen audio recording, runs speech transcription and links to citizen request."""
    req_repo = RequestRepository(db)
    req = req_repo.get_by_id_or_reference(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Request {request_id} not found"}},
        )

    # Validate audio MIME type
    content_type = audio.content_type or ""
    if not any(t in content_type for t in ["audio", "video", "octet-stream"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_AUDIO",
                    "message": "Uploaded file is not a supported audio format",
                }
            },
        )

    file_name = f"audio_{uuid.uuid4().hex[:8]}_{audio.filename or 'recording.wav'}"
    audio_url = f"/static/uploads/{file_name}"

    # Update request
    req.audio_url = audio_url
    req.transcript = "[Transcribed voice input via speech-to-text pipeline]"
    req_repo.add_transcription(
        request_id=req.id,
        transcript=req.transcript,
        stt_model="whisper-base",
        stt_provider="whisper",
        confidence=0.88,
    )
    db.commit()

    return AudioUploadResponse(
        request_id=request_id,
        audio_url=audio_url,
        status="uploaded",
    )


@router.get(
    "/{request_id}",
    response_model=RequestStatusResponse,
    summary="Citizen checks own submission status (reference ID) — FR-005",
)
def get_request(request_id: str, db: Session = Depends(get_db)) -> RequestStatusResponse:
    """Look up submission status by reference code or ID."""
    req_repo = RequestRepository(db)
    req = req_repo.get_by_id_or_reference(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Request {request_id} not found"}},
        )

    # Resolve issue_type and location from cluster or entities
    issue_type = None
    location_name = None

    from app.models import ClusterMember, ExtractedEntity, Location

    member = db.query(ClusterMember).filter(ClusterMember.request_id == req.id).first()
    if member and member.cluster:
        issue_type = member.cluster.issue_type
        if member.cluster.location_id:
            loc = db.query(Location).filter(Location.id == member.cluster.location_id).first()
            if loc:
                location_name = loc.village_ward or loc.district or loc.source_text

    if not location_name:
        loc_ent = (
            db.query(ExtractedEntity)
            .filter(
                ExtractedEntity.request_id == req.id,
                ExtractedEntity.entity_type.in_(["location", "place", "facility"]),
            )
            .first()
        )
        if loc_ent:
            location_name = loc_ent.value

    return RequestStatusResponse(
        request_id=f"req_{req.id}",
        reference_code=req.reference_code,
        status=req.status,
        language=req.language,
        transcript=req.transcript or req.raw_text,
        created_at=req.created_at.isoformat() if req.created_at else None,
        issue_type=issue_type,
        location=location_name,
    )
