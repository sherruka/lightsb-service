import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime

class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False)

    sessions = relationship("SessionDB", back_populates="user")
    stats = relationship("UserStatsDB", back_populates="user", uselist=False)
    profile = relationship("UserProfileDB", back_populates="user", uselist=False)

class SessionDB(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=False)
    device_info = Column(String, nullable=True)

    user = relationship("UserDB", back_populates="sessions")

class UserStatsDB(Base):
    __tablename__ = "user_stats"

    stat_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    avg_usage_time = Column(Integer, nullable=True)

    user = relationship("UserDB", back_populates="stats")

class UserProfileDB(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    full_name = Column(String, nullable=False)
    position = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    user = relationship("UserDB", back_populates="profile")
