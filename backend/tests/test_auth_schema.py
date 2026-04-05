import pytest
from pydantic import ValidationError

from db.schema import (
    LogoutRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
    UserCreate,
    UserUpdate,
)


def test_user_create_forbids_extra_fields():
    with pytest.raises(ValidationError):
        UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice",
            password="StrongPass123",
            is_superuser=True,
        )


def test_user_update_forbids_privilege_fields():
    with pytest.raises(ValidationError):
        UserUpdate(is_superuser=True)


def test_password_reset_confirm_enforces_password_length():
    with pytest.raises(ValidationError):
        PasswordResetConfirm(token="a" * 24, new_password="short")


def test_refresh_token_request_requires_token_field():
    with pytest.raises(ValidationError):
        RefreshTokenRequest()


def test_logout_request_forbids_unexpected_fields():
    with pytest.raises(ValidationError):
        LogoutRequest(refresh_token="a" * 24, force=True)
