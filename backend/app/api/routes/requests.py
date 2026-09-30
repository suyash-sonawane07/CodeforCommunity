"""Citizen request intake routes (PRD §10.1 #2–4, FR-001–009)."""

import base64
from pathlib import Path
from typing import Optional, Union
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_optional_user
from app.models.user import User
from app.repositories import RequestRepository
from app.schemas import (
    AudioUploadResponse,
    NotImplementedResponse,
    RequestCreate,
    RequestCreateResponse,
    RequestStatusResponse,
)
from app.services.ai_runtime import ingest_citizen_request

router = APIRouter(prefix="/requests", tags=["citizen-requests"])


class RequestAudioUpload(BaseModel):
    audio_base64: str


@router.post(
    "",
    response_model=RequestCreateResponse,
    responses={201: {"model": RequestCreateResponse}, 501: {"model": NotImplementedResponse}},
    status_code=status.HTTP_201_CREATED,
    summary="Submit a citizen request (text or voice) — FR-001/002",
)
def create_request(
    body: RequestCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> RequestCreateResponse:
    """Intake endpoint: runs STT, language detection, classification, NER, geocoding and clustering."""
    req, processed, loc_name = ingest_citizen_request(
        db=db,
        channel=body.channel,
        text=body.text,
        language_hint=body.language_hint,
        audio_base64=body.audio_base64,
        location_text=body.location_text,
        consent_ack=body.consent_ack,
    )

    if current_user and hasattr(req, "user_id"):
        req.user_id = current_user.id
        db.commit()

    return RequestCreateResponse(
        request_id=f"req_{req.id}",
        status=req.status,
        reference_code=req.reference_code,
        issue_type=processed.issue_type,
        location=loc_name,
    )


@router.post(
    "/{request_id}/audio",
    summary="Upload/attach audio for transcription — FR-002",
)
async def upload_audio(
    request_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Accepts citizen audio recording (either multipart file or JSON base64)."""
    req_repo = RequestRepository(db)
    req = req_repo.get_by_id_or_reference(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Request {request_id} not found"}},
        )

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body = await request.json()
        audio_base64 = body.get("audio_base64", "")
        file_name = f"audio_{uuid.uuid4().hex[:8]}.wav"
        uploads_dir = Path(__file__).resolve().parents[2] / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        audio_url = f"/static/uploads/{file_name}"
        if audio_base64:
            try:
                (uploads_dir / file_name).write_bytes(base64.b64decode(audio_base64))
            except Exception:
                pass
    else:
        form = await request.form()
        audio_file = form.get("audio") or form.get("file")
        if not audio_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_AUDIO", "message": "Missing audio file"}},
            )
        audio_bytes = await audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        file_name = f"audio_{uuid.uuid4().hex[:8]}_{getattr(audio_file, 'filename', 'recording.wav')}"
        uploads_dir = Path(__file__).resolve().parents[2] / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        (uploads_dir / file_name).write_bytes(audio_bytes)
        audio_url = f"/static/uploads/{file_name}"

    updated_req, _, _ = ingest_citizen_request(
        db=db,
        channel="voice",
        audio_base64=audio_base64,
        audio_url=audio_url,
        language_hint=req.language,
        existing_request_id=req.id,
    )

    return {
        "request_id": request_id,
        "audio_url": audio_url,
        "status": updated_req.status,
    }


@router.get(
    "/{request_id}",
    response_model=RequestStatusResponse,
    summary="Citizen checks own submission status (reference ID) — FR-005",
)
def get_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> RequestStatusResponse:
    """Look up submission status by reference code or ID."""
    req_repo = RequestRepository(db)
    req = req_repo.get_by_id_or_reference(request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Request {request_id} not found"}},
        )

    # Check ownership if caller is authenticated as a regular "user" and request has a user_id
    if current_user and current_user.role == "user" and req.user_id and req.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "You do not own this request"}},
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


@router.get(
    "",
    summary="List citizen requests (mine=true)",
)
def list_requests(
    mine: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    from app.models.request import CitizenRequest

    query = select(CitizenRequest)
    if mine or (current_user and current_user.role == "user"):
        if current_user:
            query = query.where(CitizenRequest.user_id == current_user.id)
        else:
            query = query.where(CitizenRequest.user_id.is_(None))

    reqs = db.scalars(query).all()
    items = []
    for r in reqs:
        items.append({
            "request_id": f"req_{r.id}",
            "reference_code": r.reference_code,
            "status": r.status,
            "issue_type": r.status or "Unclassified",
            "location": r.raw_text[:30] if r.raw_text else "Unknown",
        })
    return {"items": items}
