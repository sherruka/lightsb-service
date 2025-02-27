from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database.models import UserDB
from resources.schemas import UserCreate, UserUpdate


class UserRepository:
    @staticmethod
    def create_user(db: Session, request: UserCreate) -> UserDB:
        # Создаем нового пользователя
        new_user = UserDB(
            email=request.email,
            password_hash=request.password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=request.is_active,
            role=request.role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_user(db: Session, user_id: str) -> UserDB | None:
        # Получаем пользователя по user_id
        return db.query(UserDB).filter(UserDB.user_id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> UserDB | None:
        # Получаем пользователя по email
        return db.query(UserDB).filter(UserDB.email == email).first()

    @staticmethod
    def get_users(db: Session) -> list[UserDB]:
        # Получаем всех пользователей
        return db.query(UserDB).all()

    @staticmethod
    def update_user(db: Session, user: UserDB, request: UserUpdate) -> UserDB:
        # Обновляем поля пользователя, исключая те, что не были заданы
        for key, value in jsonable_encoder(request, exclude_unset=True).items():
            setattr(user, key, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        # Удаляем пользователя по user_id
        user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False


user_repo = UserRepository()
