from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm.session import Session

from app.auth.settings import settings
from app.database.database import get_db
from app.database.user_db import user_repo
from app.exceptions import (
    TokenPayloadError,
    ExpiredTokenError,
    InvalidTokenError,
    UserNotFoundError,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = data.copy()
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user_from_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError()
    except jwt.JWTError:
        raise InvalidTokenError()

    user_id = payload.get("sub")

    if not user_id:
        raise TokenPayloadError()

    return user_id


def get_user_by_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id = get_current_user_from_token(token)
    user = user_repo.get_user_by_email(db, user_id)
    if not user:
        raise UserNotFoundError()
    return user

