import asyncio
from uuid import uuid4

import pytest
from fastapi import HTTPException

from lib.auth_context import (
    create_access_token,
    create_reset_token,
    decode_access_token,
    fetch_user_from_db,
    get_current_user,
    is_access_token_revoked,
    revoke_access_token,
)


def test_create_access_token_requires_user_id():
    with pytest.raises(ValueError):
        create_access_token({})


def test_decode_access_token_rejects_reset_token_type():
    reset_token = create_reset_token(str(uuid4()))

    with pytest.raises(HTTPException) as exc:
        decode_access_token(reset_token)

    assert exc.value.status_code == 401


def test_fetch_user_from_db_rejects_invalid_uuid(make_session):
    session = make_session()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(fetch_user_from_db("not-a-uuid", db=session))

    assert exc.value.status_code == 401


def test_fetch_user_from_db_rejects_inactive_user(make_session, make_user):
    inactive_user = make_user(is_active=False)
    session = make_session([inactive_user])

    with pytest.raises(HTTPException) as exc:
        asyncio.run(fetch_user_from_db(str(inactive_user.id), db=session))

    assert exc.value.status_code == 403


def test_get_current_user_rejects_revoked_access_token(make_session, make_user):
    user = make_user()
    access_token = create_access_token({"user_id": str(user.id)})
    revoke_access_token(access_token)

    assert is_access_token_revoked(access_token)

    session = make_session()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(token=access_token, db=session))

    assert exc.value.status_code == 401
