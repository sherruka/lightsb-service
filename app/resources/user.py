from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.resources.schemas import UserRegister, UserLogin, UserBase
from app.database.database import get_db
from app.database.user_db import user_repo
from app.exceptions import (
    DuplicateUserError,
    UserNotFoundError,
    IncorrectPasswordError,
    NoRefreshTokenError,
    PasswordsDoNotMatchError,
)
from app.auth.hashing import Hash
from app.auth.utils import create_jwt_token, get_user_by_token
from fastapi.responses import JSONResponse
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


# Регистрация пользователя
@router.post("/register", status_code=status.HTTP_201_CREATED)
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
@router.post("/login", status_code=status.HTTP_200_OK)
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

    access_token = create_jwt_token({"sub": user.user_id}, expires_delta=None)
    refresh_token = create_jwt_token(
        {"sub": user.user_id}, expires_delta=timedelta(days=7)
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True, 
        secure=True, 
        samesite="None", 
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "redirect_to": "profile",
        },
        status_code=200,
        headers=response.headers,
    )

# Обновление токена
@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise NoRefreshTokenError()

    user = get_user_by_token(refresh_token, db)

    new_access_token = create_jwt_token({"sub": user.user_id}, expires_delta=None)

    return JSONResponse(
        content={"access_token": new_access_token},
        status_code=200,
    )
