from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date
from typing import Optional


# Схема для создания нового пользователя
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    password_confirm: str


# Схема для входа пользователя
class UserLogin(BaseModel):
    identifier: str
    password: str
    remember_me: bool = False


# Схема для обновления данных пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Схема для отображения данных пользователя
class UserBase(BaseModel):
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True


# Схема для пользователя, включая дополнительную информацию
class User(UserBase):
    user_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


# Схема для статистики пользователя
class UserStatsBase(BaseModel):
    usage_count: Optional[int] = None
    images_count: Optional[int] = None
    last_used: Optional[datetime] = None
    avg_usage_time: Optional[float] = None


class UserStats(UserStatsBase):
    stat_id: str
    user_id: str

    class Config:
        orm_mode = True


# Схема для обновления статистики пользователя
class UserStatsUpdate(BaseModel):
    usage_count: Optional[int] = None
    images_count: Optional[int] = None
    last_used: Optional[datetime] = None
    avg_usage_time: Optional[float] = None

    class Config:
        orm_mode = True


# Схема для профиля пользователя
class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserProfile(UserProfileBase):
    profile_id: str
    user_id: str

    class Config:
        orm_mode = True


# Схема для обновления профиля пользователя
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    date_of_birth: Optional[date] = None

    class Config:
        orm_mode = True
        from_attributes = True
