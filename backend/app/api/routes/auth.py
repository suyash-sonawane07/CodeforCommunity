from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import create_access_token, get_password_hash, verify_password, get_current_user
from app.schemas.api import ErrorBody, LoginRequest, LoginResponse, SignupRequest, UserResponse
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new user",
)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.scalar(select(User).where(User.email == body.email.lower()))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "EMAIL_IN_USE", "message": "Email already in use"}},
        )
    user = User(
        email=body.email.lower(),
        name=body.name,
        hashed_password=get_password_hash(body.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorBody}},
    summary="Login",
)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    email_clean = body.email.lower()
    from app.core.security import DEMO_USERS

    user = db.scalar(select(User).where(User.email == email_clean))

    # 1. Registered database user with verified password
    if user and user.hashed_password and verify_password(body.password, user.hashed_password):
        access_token = create_access_token(user.email, user.role)
        return LoginResponse(
            access_token=access_token,
            role=user.role,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
            ),
        )

    # 2. Demo accounts support (e.g. analyst@civicpulse.dev)
    if email_clean in DEMO_USERS:
        role = DEMO_USERS[email_clean]
        if not user:
            user = User(email=email_clean, name=email_clean.split("@")[0].title(), role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
        access_token = create_access_token(user.email, user.role or role)
        return LoginResponse(
            access_token=access_token,
            role=user.role or role,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role or role,
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": {"code": "BAD_CREDENTIALS", "message": "Invalid email or password"}},
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
    )
