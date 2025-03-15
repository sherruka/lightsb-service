from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.database.models import UserProfileDB
from app.resources.schemas import UserProfileBase, UserProfileUpdate


class UserProfileRepository:
    @staticmethod
    def create_user_profile(
        db: Session, request: UserProfileBase, user_id: str
    ) -> UserProfileDB:
        # Создаем профиль пользователя
        new_profile = UserProfileDB(
            user_id=user_id,
            full_name=request.full_name,
            position=request.position,
            date_of_birth=request.date_of_birth,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile

    @staticmethod
    def get_user_profile(db: Session, user_id: str) -> UserProfileDB | None:
        # Получаем профиль пользователя по user_id
        return db.query(UserProfileDB).filter(UserProfileDB.user_id == user_id).first()

    @staticmethod
    def update_user_profile(
        db: Session, profile: UserProfileDB, request: UserProfileUpdate
    ) -> UserProfileDB:
        # Обновляем профиль пользователя, исключая те поля, которые не были заданы
        for key, value in jsonable_encoder(request, exclude_unset=True).items():
            setattr(profile, key, value)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile


user_profile_repo = UserProfileRepository()
