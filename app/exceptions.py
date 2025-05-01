from http import HTTPStatus

from fastapi import HTTPException


class DuplicateUserError(HTTPException):
    def __init__(self, email: str = None, username: str = None):
        self.email = email
        self.username = username
        self.status_code = HTTPStatus.CONFLICT
        if self.email:
            self.detail = f"User with email {self.email} already exists."
        elif self.username:
            self.detail = f"User with username {self.username} already exists."
        else:
            self.detail = "User with the provided credentials already exists."


class UserNotFoundError(HTTPException):
    def __init__(self, email: str = None, username: str = None):
        self.email = email
        self.username = username
        self.status_code = HTTPStatus.NOT_FOUND
        if self.email:
            self.detail = f"User with email {self.email} not found."
        elif self.username:
            self.detail = f"User with username {self.username} not found."
        else:
            self.detail = "User not found."


class UserProfileNotFoundError(HTTPException):
    def __init__(
        self,
    ):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = "User profile not found."


class UserStatsNotFoundError(HTTPException):
    def __init__(
        self,
    ):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = "User stats not found."


class UserProfileUpdateError(HTTPException):
    def __init__(self):
        self.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.detail = "Failed to update profile."


class IncorrectPasswordError(HTTPException):
    def __init__(self):
        self.status_code = HTTPStatus.UNAUTHORIZED
        self.detail = "Incorrect password."


class PasswordsDoNotMatchError(HTTPException):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Passwords do not match."


class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid authentication token"
        )


class ExpiredTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Token has expired"
        )


class TokenPayloadError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token payload"
        )


class NoRefreshTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED, detail="No refresh token provided"
        )


class NoGeneratedImagesError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to generate images.",
        )
