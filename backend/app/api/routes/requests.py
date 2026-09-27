"""Citizen request intake routes (PRD §10.1 #2–4, FR-001–009).

SCAFFOLD: schemas are real and validated; business logic returns 501.
"""

from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse

from app.schemas import (
    AudioUploadResponse,
    NotImplementedResponse,
    RequestCreate,
    RequestCreateResponse,
    RequestStatusResponse,
)

router = APIRouter(prefix="/requests", tags=["requests"])


def _not_implemented() -> JSONResponse:
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)


@router.post(
    "",
    response_model=RequestCreateResponse,
    responses={201: {"model": RequestCreateResponse}, 501: {"model": NotImplementedResponse}},
    status_code=status.HTTP_201_CREATED,
    summary="Submit a citizen request (text or voice) — FR-001/002",
)
def create_request(body: RequestCreate) -> JSONResponse:
    """TODO(PRD FR-001–009, Member B Phase 1): persist intake, run STT/langdetect pipeline."""
    return _not_implemented()


@router.post(
    "/{request_id}/audio",
    response_model=AudioUploadResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Upload/attach audio for transcription — FR-002",
)
def upload_audio(request_id: str, audio: UploadFile = File(...)) -> JSONResponse:
    """TODO(PRD FR-002): file-type/size validation then storage; STT stays behind provider."""
    return _not_implemented()


@router.get(
    "/{request_id}",
    response_model=RequestStatusResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Citizen checks own submission status (reference ID) — FR-005",
)
def get_request(request_id: str) -> JSONResponse:
    """TODO(PRD FR-005): return status for the caller's own submission only."""
    return _not_implemented()
