from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from database.models import UserStatsDB
from resources.schemas import UserStatsBase, UserStatsUpdate


class UserStatsRepository:
    @staticmethod
    def create_user_stats(db: Session, request: UserStatsBase, user_id: str) -> UserStatsDB:
        # Создаем статистику пользователя
        new_stats = UserStatsDB(
            user_id=user_id,
            usage_count=request.usage_count,
            last_used=request.last_used,
            avg_usage_time=request.avg_usage_time,
        )
        db.add(new_stats)
        db.commit()
        db.refresh(new_stats)
        return new_stats

    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> UserStatsDB | None:
        # Получаем статистику пользователя по user_id
        return db.query(UserStatsDB).filter(UserStatsDB.user_id == user_id).first()

    @staticmethod
    def update_user_stats(db: Session, stats: UserStatsDB, request: UserStatsUpdate) -> UserStatsDB:
        # Обновляем статистику пользователя, исключая те поля, которые не были заданы
        for key, value in jsonable_encoder(request, exclude_unset=True).items():
            setattr(stats, key, value)
        db.add(stats)
        db.commit()
        db.refresh(stats)
        return stats


user_stats_repo = UserStatsRepository()
