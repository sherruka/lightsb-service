import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.hashing import Hash
from app.auth.utils import create_jwt_token, get_user_by_token, get_user_id_from_token
from app.database.database import get_db
from app.database.user_db import user_repo
from app.database.user_profile_db import user_profile_repo
from app.database.user_stat_db import user_stats_repo
from app.main import app
from app.resources.schemas import UserRegister

client = TestClient(app)


@pytest.fixture
def mock_db():
    """Fixture for mock database."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_user():
    """Mock user object."""
    user = MagicMock()
    user.user_id = "test_user_id"
    user.username = "testuser"
    user.email = "test@example.com"
    user.role = "admin"
    user.created_at = "1990-01-01"
    user.updated_at = "1991-01-01"
    user.is_active = True
    return user


@pytest.fixture
def mock_profile():
    """Mock user profile."""
    profile = MagicMock()
    profile.profile_id = "profile_123"
    profile.user_id = "test_user_id"
    profile.full_name = "John Doe"
    profile.position = "Developer"
    profile.date_of_birth = "1990-01-01"
    return profile


@pytest.fixture
def mock_stats():
    """Mock user statistics."""
    stats = MagicMock()
    stats.stat_id = "1"
    stats.user_id = "1"
    stats.usage_count = 10
    stats.images_count = 5
    stats.last_used = "2025-04-01T12:00:00"
    stats.avg_usage_time = 30.5
    return stats


def test_register_user_success(mock_db, monkeypatch):
    """Test successful user registration."""
    monkeypatch.setattr(user_repo, "get_user_by_username", lambda db, username: None)
    monkeypatch.setattr(user_repo, "get_user_by_email", lambda db, email: None)
    monkeypatch.setattr(
        user_repo, "create_user", lambda db, request: MagicMock(user_id="test_user_id")
    )

    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        },
    )

    assert response.status_code == 201
    assert response.json()["redirect_to"] == "profile"
    assert response.json()["user_id"] == "test_user_id"


def test_register_user_password_mismatch():
    """Test error when passwords do not match."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "wrongpassword",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match."


def test_register_user_duplicate_username(mock_db, monkeypatch, mock_user):
    """Test error when username already exists."""
    monkeypatch.setattr(
        user_repo, "get_user_by_username", lambda db, username: mock_user
    )

    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with username testuser already exists."


def test_register_user_duplicate_email(mock_db, monkeypatch, mock_user):
    """Test error when email already exists."""
    monkeypatch.setattr(user_repo, "get_user_by_username", lambda db, username: None)
    monkeypatch.setattr(user_repo, "get_user_by_email", lambda db, email: mock_user)

    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"] == "User with email test@example.com already exists."
    )


def test_register_user_password_hashed(mock_db, monkeypatch):
    """Test that password is hashed before saving."""

    def mock_create_user(db, request):
        assert request.password != "testpassword"
        return MagicMock(user_id="test_user_id")

    monkeypatch.setattr(user_repo, "get_user_by_username", lambda db, username: None)
    monkeypatch.setattr(user_repo, "get_user_by_email", lambda db, email: None)
    monkeypatch.setattr(user_repo, "create_user", mock_create_user)
    monkeypatch.setattr(Hash, "hash_password", lambda password: "hashedpassword")

    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "password_confirm": "testpassword",
        },
    )

    assert response.status_code == 201


def test_login_user_success_username(mock_db, mock_user, monkeypatch):
    """Successful login using username"""
    monkeypatch.setattr(
        user_repo, "get_user_by_username", lambda db, username: mock_user
    )
    monkeypatch.setattr(Hash, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(
        "app.resources.user.create_jwt_token",
        lambda data, expires_delta: "mock_access_token",
    )
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testuser",
            "password": "correctpassword",
            "remember_me": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token_lightsb"] == "mock_access_token"
    assert response.json()["redirect_to"] == "profile"
    assert response.headers["set-cookie"].startswith("refresh_token_lightsb=")


def test_login_user_success_email(mock_db, mock_user, monkeypatch):
    """Successful login using email"""
    monkeypatch.setattr(user_repo, "get_user_by_email", lambda db, email: mock_user)
    monkeypatch.setattr(Hash, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(
        "app.resources.user.create_jwt_token",
        lambda data, expires_delta: "mock_access_token",
    )

    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "test@example.com",
            "password": "correctpassword",
            "remember_me": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token_lightsb"] == "mock_access_token"
    assert response.json()["redirect_to"] == "profile"
    assert response.headers["set-cookie"].startswith("refresh_token_lightsb=")


def test_login_user_not_found(mock_db, monkeypatch):
    """Error when user does not exist"""
    monkeypatch.setattr(user_repo, "get_user_by_username", lambda db, username: None)
    monkeypatch.setattr(user_repo, "get_user_by_email", lambda db, email: None)

    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "unknownuser",
            "password": "randompassword",
            "remember_me": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User with username unknownuser not found."


def test_login_user_incorrect_password(mock_db, mock_user, monkeypatch):
    """Error when incorrect password is provided"""
    monkeypatch.setattr(
        user_repo, "get_user_by_username", lambda db, username: mock_user
    )
    monkeypatch.setattr(Hash, "verify_password", lambda plain, hashed: False)

    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testuser",
            "password": "wrongpassword",
            "remember_me": False,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password."


def test_refresh_token_success(mock_db, monkeypatch):
    """Successful token refresh"""
    monkeypatch.setattr(
        "app.resources.user.get_user_id_from_token", lambda token: "test_user_id"
    )
    monkeypatch.setattr(
        "app.resources.user.create_jwt_token",
        lambda data, expires_delta: "mock_access_token",
    )

    response = client.post(
        "/api/auth/refresh",
        cookies={"refresh_token_lightsb": "mock_refresh_token"},
    )

    assert response.status_code == 200
    assert response.json()["access_token_lightsb"] == "mock_access_token"


def test_refresh_token_missing():
    """Error when refresh token is missing"""
    response = client.post("/api/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "No refresh token provided"


def test_refresh_token_invalid(monkeypatch, mock_db):
    """Error when refresh token is invalid"""
    response = client.post(
        "/api/auth/refresh", cookies={"refresh_token_lightsb": "invalid_token"}
    )

    assert response.status_code == 401


def test_update_profile_success(mock_db, mock_user, monkeypatch):
    """Successful profile update"""

    app.dependency_overrides[get_user_by_token] = lambda: mock_user

    monkeypatch.setattr(
        user_profile_repo, "get_user_profile", lambda db, user_id: mock_user
    )
    monkeypatch.setattr(
        user_profile_repo,
        "update_user_profile",
        lambda db, profile, request: MagicMock(),
    )

    response = client.post(
        "/api/profile/update",
        json={
            "full_name": "John Doe",
            "position": "Developer",
            "date_of_birth": "1990-01-01",
        },
        headers={"Authorization": "Bearer mock_access_token"},
    )

    assert response.status_code == 200
    assert response.json()["redirect_to"] == "profile"

    app.dependency_overrides.clear()


def test_update_profile_not_found(mock_db, mock_user, monkeypatch):
    """Error when user profile is not found"""
    app.dependency_overrides[get_user_by_token] = lambda: mock_user
    monkeypatch.setattr(user_profile_repo, "get_user_profile", lambda db, user_id: None)

    response = client.post(
        "/api/profile/update",
        json={
            "full_name": "New Name",
            "position": "Developer",
            "date_of_birth": "1990-01-01",
        },
        headers={"Authorization": "Bearer mock_access_token"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_update_profile_error(mock_db, mock_user, monkeypatch):
    """Error during profile update"""
    app.dependency_overrides[get_user_by_token] = lambda: mock_user
    monkeypatch.setattr(
        user_profile_repo, "get_user_profile", lambda db, user_id: MagicMock()
    )
    monkeypatch.setattr(
        user_profile_repo, "update_user_profile", lambda db, profile, request: None
    )

    response = client.post(
        "/api/profile/update",
        json={
            "full_name": "New Name",
            "position": "Developer",
            "date_of_birth": "1990-01-01",
        },
        headers={"Authorization": "Bearer mock_access_token"},
    )

    assert response.status_code == 500
    app.dependency_overrides.clear()


def test_protected_route_success(mock_user):
    """Successful access to protected endpoint"""
    app.dependency_overrides[get_user_by_token] = lambda: mock_user

    response = client.get(
        "/api/protected-route", headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Вы авторизованы!", "user": "test_user_id"}

    app.dependency_overrides.clear()


def test_protected_route_unauthorized():
    """Error when user is unauthorized"""
    response = client.get("/api/protected-route")

    assert response.status_code == 401


def test_logout():
    """Successful user logout"""
    response = client.post("/api/logout")

    assert response.json() == {"message": "Logged out"}


def test_get_profile_success(monkeypatch, mock_user, mock_profile):
    """Successful profile retrieval"""
    app.dependency_overrides[get_user_by_token] = lambda: mock_user

    monkeypatch.setattr(
        user_profile_repo, "get_user_profile", lambda db, user_id: mock_profile
    )

    response = client.get(
        "/api/profile", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "profile_id": "profile_123",
        "user_id": "test_user_id",
        "full_name": "John Doe",
        "position": "Developer",
        "date_of_birth": "1990-01-01",
    }

    app.dependency_overrides.clear()


def test_get_profile_not_found(monkeypatch):
    """Error if profile not found"""
    monkeypatch.setattr(user_profile_repo, "get_user_profile", lambda db, user_id: None)

    response = client.get(
        "/api/profile", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"


def test_get_user_success(monkeypatch, mock_user):
    """Test successful user retrieval"""
    app.dependency_overrides[get_user_by_token] = lambda: mock_user

    response = client.get("/api/user", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["user_id"] == "test_user_id"

    app.dependency_overrides.clear()


def test_get_user_not_authenticated(monkeypatch):
    """Test error when no token is provided"""
    app.dependency_overrides[get_user_by_token] = lambda: None

    response = client.get("/api/user")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."

    app.dependency_overrides.clear()


def test_get_stats_success(monkeypatch, mock_db, mock_user, mock_stats):
    """Test successful user stats retrieval"""
    monkeypatch.setattr(
        user_stats_repo, "get_user_stats", lambda db, user_id: mock_stats
    )
    monkeypatch.setattr(
        app,
        "dependency_overrides",
        {
            get_user_by_token: lambda: mock_user,
            get_db: lambda: mock_db,
        },
    )

    response = client.get("/api/stats", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json() == {
        "stat_id": "1",
        "user_id": "1",
        "usage_count": 10,
        "images_count": 5,
        "last_used": "2025-04-01T12:00:00",
        "avg_usage_time": 30.5,
    }

    app.dependency_overrides.clear()


def test_get_stats_user_not_found(monkeypatch, mock_db):
    """Test error if user not found"""
    monkeypatch.setattr(
        app,
        "dependency_overrides",
        {
            get_user_by_token: lambda: None,
            get_db: lambda: mock_db,
        },
    )

    response = client.get("/api/stats", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."

    app.dependency_overrides.clear()


def test_get_stats_not_found(monkeypatch, mock_db, mock_user):
    """Test error if user stats not found"""
    monkeypatch.setattr(user_stats_repo, "get_user_stats", lambda db, user_id: None)
    monkeypatch.setattr(
        app,
        "dependency_overrides",
        {
            get_user_by_token: lambda: mock_user,
            get_db: lambda: mock_db,
        },
    )

    response = client.get("/api/stats", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User stats not found."

    app.dependency_overrides.clear()
