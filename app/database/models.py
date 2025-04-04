import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False)

    stats = relationship("UserStatsDB", back_populates="user", uselist=False)
    profile = relationship("UserProfileDB", back_populates="user", uselist=False)


class UserStatsDB(Base):
    __tablename__ = "user_stats"

    stat_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    usage_count = Column(Integer, default=0)
    images_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    avg_usage_time = Column(Integer, nullable=True)

    user = relationship("UserDB", back_populates="stats")


class UserProfileDB(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    full_name = Column(String, nullable=True)
    position = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)

    user = relationship("UserDB", back_populates="profile")
