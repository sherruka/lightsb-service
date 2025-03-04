from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.resources.schemas import UserCreate, UserLogin, UserBase
from app.database.database import get_db
from app.database.user_db import user_repo
from app.exceptions import DuplicateUserError, UserNotFoundError, IncorrectPasswordError

router = APIRouter(prefix="/auth", tags=["auth"])


# Регистрация пользователя
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(request: UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_user_by_username(db, request.username):
        raise DuplicateUserError(username=request.username)

    # Проверка на существование пользователя
    if user_repo.get_user_by_email(db, request.email):
        raise DuplicateUserError(email=request.email)

    user_repo.create_user(db, request)
    # Редирект на страницу профиля после успешной регистрации
    return RedirectResponse(url="/pages/profile", status_code=303)


# Вход пользователя
@router.post("/login", response_model=UserBase)
def login_user(request: UserLogin, db: Session = Depends(get_db)):
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

    # Проверка пароля
    if request.password != user.password_hash:
        raise IncorrectPasswordError

    return user
