from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import SessionDB
from app.resources.schemas import SessionBase


class SessionRepository:
    @staticmethod
    def create_session(db: Session, request: SessionBase, user_id: str) -> SessionDB:
        # Создаем сессию
        new_session = SessionDB(
            login_time=datetime.utcnow(),
            user_id=user_id,
            ip_address=request.ip_address,
            device_info=request.device_info,
            logout_time=request.logout_time,
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    @staticmethod
    def get_session(db: Session, session_id: str) -> SessionDB | None:
        # Получаем сессию по session_id
        return db.query(SessionDB).filter(SessionDB.session_id == session_id).first()

    @staticmethod
    def get_sessions(db: Session) -> list[SessionDB]:
        # Получаем все сессии
        return db.query(SessionDB).all()

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        # Удаляем сессию по session_id
        session = db.query(SessionDB).filter(SessionDB.session_id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False


session_repo = SessionRepository()
