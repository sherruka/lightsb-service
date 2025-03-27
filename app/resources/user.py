from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.hashing import Hash
from app.auth.utils import create_jwt_token, get_user_by_token, get_user_id_from_token
from app.database.database import get_db
from app.database.models import UserDB
from app.database.user_db import user_repo
from app.database.user_profile_db import user_profile_repo
from app.exceptions import (
    DuplicateUserError,
    IncorrectPasswordError,
    NoRefreshTokenError,
    PasswordsDoNotMatchError,
    UserNotFoundError,
    UserProfileNotFoundError,
    UserProfileUpdateError,
)
from app.resources.schemas import (
    User,
    UserBase,
    UserLogin,
    UserProfile,
    UserProfileUpdate,
    UserRegister,
)

router = APIRouter(tags=["auth"])


# Регистрация пользователя
@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(request: UserRegister, db: Session = Depends(get_db)):
    if request.password != request.password_confirm:
        raise PasswordsDoNotMatchError()

    if user_repo.get_user_by_username(db, request.username):
        raise DuplicateUserError(username=request.username)

    if user_repo.get_user_by_email(db, request.email):
        raise DuplicateUserError(email=request.email)

    request.password = Hash.hash_password(request.password)

    new_user = user_repo.create_user(db, request)

    return JSONResponse(
        content={"redirect_to": "profile", "user_id": new_user.user_id}, status_code=201
    )


# Вход пользователя
@router.post("/auth/login", status_code=status.HTTP_200_OK)
def login_user(request: UserLogin, response: Response, db: Session = Depends(get_db)):
    if "@" in request.identifier:
        user = user_repo.get_user_by_email(db, request.identifier)
        email = request.identifier
        username = None
    else:
        user = user_repo.get_user_by_username(db, request.identifier)
        email = None
        username = request.identifier

    if not user:
        raise UserNotFoundError(email=email, username=username)

    if not Hash.verify_password(request.password, user.password):
        raise IncorrectPasswordError()

    refresh_expiry = timedelta(days=30) if request.remember_me else timedelta(days=7)

    access_token = create_jwt_token({"sub": user.user_id}, expires_delta=None)
    refresh_token = create_jwt_token(
        {"sub": user.user_id}, expires_delta=refresh_expiry
    )

    response.set_cookie(
        key="refresh_token_lightsb",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=30 * 24 * 60 * 60 if request.remember_me else None,
    )

    return JSONResponse(
        content={
            "access_token_lightsb": access_token,
            "redirect_to": "profile",
        },
        status_code=200,
        headers=response.headers,
    )


# Обновление токена
@router.post("/auth/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token_lightsb")

    if not refresh_token:
        raise NoRefreshTokenError()

    user_id = get_user_id_from_token(refresh_token)

    new_access_token = create_jwt_token({"sub": user_id}, expires_delta=None)

    return JSONResponse(
        content={"access_token_lightsb": new_access_token},
        status_code=200,
    )


# Обновление профиля
@router.post("/profile/update", status_code=status.HTTP_200_OK)
def update_profile(
    request: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_user_by_token),
):
    profile = user_profile_repo.get_user_profile(db, current_user.user_id)

    if not profile:
        raise UserProfileNotFoundError()

    updated_profile = user_profile_repo.update_user_profile(db, profile, request)

    if not updated_profile:
        raise UserProfileUpdateError()

    return JSONResponse(
        content={"redirect_to": "profile"},
        status_code=200,
    )


@router.get("/protected-route")
async def protected_route(current_user: UserDB = Depends(get_user_by_token)):
    return {"message": "Вы авторизованы!", "user": current_user.user_id}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token_lightsb")
    return {"message": "Logged out"}


@router.get("/profile", response_model=UserProfile)
def get_profile(
    db: Session = Depends(get_db), current_user: UserDB = Depends(get_user_by_token)
):
    profile = user_profile_repo.get_user_profile(db, current_user.user_id)

    if not profile:
        raise UserProfileNotFoundError()

    return {
        "profile_id": profile.profile_id,
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "position": profile.position,
        "date_of_birth": profile.date_of_birth,
    }


@router.get("/user", response_model=User)
def get_user(
    db: Session = Depends(get_db), current_user: UserDB = Depends(get_user_by_token)
):

    if not current_user:
        raise UserNotFoundError()

    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "user_id": current_user.user_id,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "is_active": current_user.is_active,
    }
