from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.resources.schemas import UserCreate, UserLogin, UserBase
from app.database.database import get_db
from app.database.user_db import user_repo
from app.exceptions import DuplicateUserError, UserNotFoundError, IncorrectPasswordError

router = APIRouter(prefix="/auth", tags=["auth"])


# Регистрация пользователя
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserBase)
def register_user(request: UserCreate, db: Session = Depends(get_db)):

    # Проверка на существование пользователя
    if user_repo.get_user_by_username(db, request.username):
        raise DuplicateUserError(username=request.username)

    # Проверка на существование пользователя
    if user_repo.get_user_by_email(db, request.email):
        raise DuplicateUserError(email=request.email)

    # Создаём нового пользователя
    user = user_repo.create_user(db, request)
    return user


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
