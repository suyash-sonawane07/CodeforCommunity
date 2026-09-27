"""Auth routes — demo-login boundary (PRD §5, §10.1 #1).

SCAFFOLD: issues a role-scoped demo JWT. NOT production authentication.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.security import create_access_token
from app.schemas import ErrorBody, LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USERS = {
    # Dev-only demo accounts (PRD §5 personas). TODO(PRD FR-058+): replace with real auth.
    "analyst@civicpulse.dev": "analyst",
    "reviewer@civicpulse.dev": "reviewer",
    "decision@civicpulse.dev": "decision_maker",
    "admin@civicpulse.dev": "admin",
}


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorBody}},
    summary="Demo login — returns role-scoped token",
)
def login(body: LoginRequest) -> LoginResponse:
    role = DEMO_USERS.get(body.email.lower())
    # Any password accepted in scaffold mode — demo boundary only.
    if role is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": {"code": "BAD_CREDENTIALS", "message": "Unknown demo user"}},
        )
    return LoginResponse(access_token=create_access_token(body.email, role), role=role)
