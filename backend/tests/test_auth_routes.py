import asyncio
from uuid import uuid4

from lib.auth_context import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_reset_token,
    is_access_token_revoked,
    verify_password,
)


def test_register_user_success(client, make_session, override_db):
    session = make_session([None])
    override_db(session)

    payload = {
        "username": "new-user",
        "email": "new-user@example.com",
        "full_name": "New User",
        "password": "StrongPass123",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["message"] == "User registered successfully"
    assert body["user"]["email"] == payload["email"]
    assert "hashed_password" not in body["user"]
    assert body["access_token"]
    assert body["refresh_token"]

    assert len(session.added) == 1
    assert session.commit_count == 1


def test_register_user_duplicate_email_conflict(client, make_session, make_user, override_db):
    existing = make_user(email="existing@example.com")
    session = make_session([existing])
    override_db(session)

    payload = {
        "username": "another-user",
        "email": "existing@example.com",
        "full_name": "Another",
        "password": "StrongPass123",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_login_invalid_credentials(client, make_session, make_user, override_db):
    existing = make_user(password="CorrectPass123")
    session = make_session([existing])
    override_db(session)

    response = client.post(
        "/auth/login",
        json={"email": existing.email, "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_rejects_inactive_user(client, make_session, make_user, override_db):
    inactive = make_user(password="CorrectPass123", is_active=False)
    session = make_session([inactive])
    override_db(session)

    response = client.post(
        "/auth/login",
        json={"email": inactive.email, "password": "CorrectPass123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user account"


def test_login_rate_limit_blocks_excess_attempts(client, make_session, make_user, override_db):
    existing = make_user(email="rate-limited@example.com", password="CorrectPass123")
    session = make_session([existing, existing, existing, existing, existing])
    override_db(session)

    payload = {"email": existing.email, "password": "WrongPass123"}

    for _ in range(5):
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    blocked = client.post("/auth/login", json=payload)
    assert blocked.status_code == 429


def test_login_lockout_blocks_account_after_repeated_failures_across_ips(
    client,
    make_session,
    make_user,
    override_db,
):
    existing = make_user(email="account-lockout@example.com", password="CorrectPass123")
    session = make_session([existing, existing, existing, existing, existing, existing])
    override_db(session)

    payload = {"email": existing.email, "password": "WrongPass123"}

    for i in range(5):
        response = client.post(
            "/auth/login",
            json=payload,
            headers={"x-forwarded-for": f"10.0.0.{i + 1}"},
        )
        assert response.status_code == 401

    sixth_attempt = client.post(
        "/auth/login",
        json=payload,
        headers={"x-forwarded-for": "10.0.0.99"},
    )
    assert sixth_attempt.status_code == 423
    assert "temporarily locked" in sixth_attempt.json()["detail"]

    locked_attempt = client.post(
        "/auth/login",
        json=payload,
        headers={"x-forwarded-for": "10.0.0.100"},
    )
    assert locked_attempt.status_code == 423


def test_get_profile_defaults_to_authenticated_user(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user()
    session = make_session([current_user])
    override_db(session)
    override_current_user(current_user)

    response = client.get("/auth/profile")
    assert response.status_code == 200

    body = response.json()
    assert body["user"]["id"] == str(current_user.id)
    assert body["user"]["email"] == current_user.email


def test_get_profile_forbidden_for_other_user_without_superuser(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user(is_superuser=False)
    other_user_id = str(uuid4())

    session = make_session([])
    override_db(session)
    override_current_user(current_user)

    response = client.get(f"/auth/profile?user_id={other_user_id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this profile"


def test_update_profile_updates_name_and_password(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user(password="OldPass123")
    stored_user = make_user(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        password="OldPass123",
    )

    session = make_session([stored_user])
    override_db(session)
    override_current_user(current_user)

    response = client.put(
        "/auth/profile",
        json={"full_name": "Updated Name", "password": "NewPass123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["full_name"] == "Updated Name"
    assert verify_password("NewPass123", stored_user.hashed_password)
    assert session.commit_count == 1


def test_update_profile_rejects_empty_payload(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user()
    stored_user = make_user(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
    )

    session = make_session([stored_user])
    override_db(session)
    override_current_user(current_user)

    response = client.put("/auth/profile", json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "No updatable fields provided"


def test_logout_revokes_current_token(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user()
    session = make_session([])
    override_db(session)
    override_current_user(current_user)

    token = create_access_token({"user_id": str(current_user.id)})
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User logout successful"
    assert asyncio.run(is_access_token_revoked(token))


def test_refresh_session_rotates_tokens(client, make_session, make_user, override_db):
    user = make_user()
    session = make_session([user])
    override_db(session)

    refresh_token = create_refresh_token(str(user.id))
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Session refreshed successfully"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["refresh_token"] != refresh_token


def test_refresh_token_reuse_is_rejected(client, make_session, make_user, override_db):
    user = make_user()
    session = make_session([user])
    override_db(session)

    refresh_token = create_refresh_token(str(user.id))

    first_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert first_response.status_code == 200

    second_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert second_response.status_code == 401
    assert second_response.json()["detail"] == "Refresh token has already been used"


def test_reset_password_request_returns_token(
    client,
    make_session,
    make_user,
    override_db,
):
    user = make_user()
    session = make_session([user])
    override_db(session)

    response = client.post(
        "/auth/reset-password/request",
        json={"email": user.email},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"]
    assert body["reset_token"]

    claims = decode_reset_token(body["reset_token"])
    assert claims["sub"] == str(user.id)


def test_reset_password_request_rate_limit_blocks_excess_attempts(
    client,
    make_session,
    make_user,
    override_db,
):
    user = make_user(email="reset-limit@example.com")
    session = make_session([user, user, user, user, user])
    override_db(session)

    payload = {"email": user.email}

    for _ in range(5):
        response = client.post("/auth/reset-password/request", json=payload)
        assert response.status_code == 200

    blocked = client.post("/auth/reset-password/request", json=payload)
    assert blocked.status_code == 429


def test_reset_password_legacy_endpoint_keeps_compatible_response(
    client,
    make_session,
    make_user,
    override_db,
):
    user = make_user()
    session = make_session([user])
    override_db(session)

    response = client.post(f"/auth/reset-password?email={user.email}")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"message"}


def test_reset_password_confirm_updates_password(
    client,
    make_session,
    make_user,
    override_db,
):
    user = make_user(password="OldPass123")
    token = create_reset_token(str(user.id))
    session = make_session([user])
    override_db(session)

    response = client.post(
        "/auth/reset-password/confirm",
        json={"token": token, "new_password": "BrandNewPass123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password has been reset successfully"
    assert verify_password("BrandNewPass123", user.hashed_password)
    assert session.commit_count == 1


def test_reset_password_confirm_rejects_same_password(
    client,
    make_session,
    make_user,
    override_db,
):
    user = make_user(password="SamePass123")
    token = create_reset_token(str(user.id))
    session = make_session([user])
    override_db(session)

    response = client.post(
        "/auth/reset-password/confirm",
        json={"token": token, "new_password": "SamePass123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "New password must be different"


def test_reset_password_confirm_lockout_blocks_repeated_invalid_token_attempts(
    client,
    make_session,
    override_db,
):
    session = make_session([])
    override_db(session)

    payload = {
        "token": "invalid-reset-token-12345",
        "new_password": "BrandNewPass123",
    }

    for _ in range(7):
        response = client.post("/auth/reset-password/confirm", json=payload)
        assert response.status_code == 401

    eighth_attempt = client.post("/auth/reset-password/confirm", json=payload)
    assert eighth_attempt.status_code == 423
    assert "temporarily locked" in eighth_attempt.json()["detail"]

    locked_attempt = client.post("/auth/reset-password/confirm", json=payload)
    assert locked_attempt.status_code == 423


def test_delete_account_deactivates_user_and_revokes_token(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user(password="DeleteMe123")
    session = make_session([])
    override_db(session)
    override_current_user(current_user)

    token = create_access_token({"user_id": str(current_user.id)})
    response = client.request(
        "DELETE",
        "/auth/delete-account",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirm": True, "email": current_user.email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User account deactivated successfully"
    assert current_user.is_active is False
    assert not verify_password("DeleteMe123", current_user.hashed_password)
    assert session.commit_count == 1
    assert asyncio.run(is_access_token_revoked(token))


def test_delete_account_rejects_email_mismatch(
    client,
    make_session,
    make_user,
    override_db,
    override_current_user,
):
    current_user = make_user()
    session = make_session([])
    override_db(session)
    override_current_user(current_user)

    token = create_access_token({"user_id": str(current_user.id)})
    response = client.request(
        "DELETE",
        "/auth/delete-account",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirm": True, "email": "other@example.com"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Email does not match the authenticated user"
