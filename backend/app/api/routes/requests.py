from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.api import RequestCreate, RequestCreateResponse, RequestStatusResponse, ErrorBody
from pydantic import BaseModel
from app.core.security import require_user
from app.models.user import User

class RequestAudioUpload(BaseModel):
    audio_base64: str

router = APIRouter(prefix="/requests", tags=["citizen-requests"])

@router.post("", response_model=RequestCreateResponse)
def create_request(payload: RequestCreate, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    from app.models.request import CitizenRequest
    import random
    
    new_req = CitizenRequest(
        user_id=current_user.id,
        reference_code=f"REQ-{random.randint(1000, 9999)}",
        channel=payload.channel,
        raw_text=payload.text,
        language=payload.language_hint,
        consent_ack=payload.consent_ack,
        status="received"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return RequestCreateResponse(
        request_id=f"req_{new_req.id}", 
        reference_code=new_req.reference_code, 
        status=new_req.status,
        issue_type="Unclassified",
        location=payload.location_text
    )

@router.post("/{request_id}/audio")
def upload_audio(request_id: str, payload: RequestAudioUpload, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    return {"status": "success", "message": "Audio received (mocked)"}

@router.get("/{request_id}", response_model=RequestStatusResponse)
def get_status(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    from app.models.request import CitizenRequest
    req_id = int(request_id.replace("req_", ""))
    req = db.scalar(select(CitizenRequest).where(CitizenRequest.id == req_id))
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if current_user.role == "user" and req.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "You do not own this request"}}
        )
        
    return RequestStatusResponse(
        request_id=request_id,
        reference_code=req.reference_code,
        status=req.status,
        timeline=[],
        issue_type="Unclassified",
        location="Unknown"
    )

@router.get(
    "",
    summary="List citizen requests (mine=true)",
)
def list_requests(mine: bool = False, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    from app.models.request import CitizenRequest
    
    query = select(CitizenRequest)
    if mine or current_user.role == "user":
        query = query.where(CitizenRequest.user_id == current_user.id)
        
    reqs = db.scalars(query).all()
    items = []
    for req in reqs:
        items.append({
            "request_id": f"req_{req.id}",
            "reference_code": req.reference_code,
            "status": req.status,
            "issue_type": "Unclassified",
            "location": "Unknown"
        })
    return {"items": items}
