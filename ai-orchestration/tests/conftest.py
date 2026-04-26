import os
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure settings-dependent modules can be imported in tests.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://compass:compass@localhost:5432/compass_test",
)
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "compass_test_secret_key_that_is_long_enough_12345",
)

from api.auth import router as auth_router  # noqa: E402
from db.db import get_db  # noqa: E402
from db.models import Deployment, Environment, Service, User  # noqa: E402
from lib.auth_context import get_current_user, hash_password  # noqa: E402
from lib.security_store import security_store  # noqa: E402


class DummyScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class DummySession:
    def __init__(self, execute_values=None):
        self.execute_values = list(execute_values or [])
        self.added = []
        self.commit_count = 0
        self.refreshed = []

    async def execute(self, _query):
        if not self.execute_values:
            raise AssertionError("No execute value configured for this DB call")
        return DummyScalarResult(self.execute_values.pop(0))

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, obj):
        self.refreshed.append(obj)
        now = datetime.now(timezone.utc)
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        if getattr(obj, "created_at", None) is None:
            obj.created_at = now
        obj.updated_at = now
        if getattr(obj, "is_active", None) is None:
            obj.is_active = True
        if getattr(obj, "is_superuser", None) is None:
            obj.is_superuser = False
        if getattr(obj, "is_google_auth", None) is None:
            obj.is_google_auth = False


@pytest.fixture(autouse=True)
def clear_revoked_tokens():
    asyncio.run(security_store.clear_test_state())
    yield
    asyncio.run(security_store.clear_test_state())


@pytest.fixture
def make_session():
    def _make_session(execute_values=None):
        return DummySession(execute_values=execute_values)

    return _make_session


@pytest.fixture
def make_user():
    def _make_user(
        *,
        user_id=None,
        username=None,
        email=None,
        password="StrongPass123",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        is_google_auth=False,
    ):
        now = datetime.now(timezone.utc)
        user = User(
            username=username or f"user-{uuid4().hex[:8]}",
            email=email or f"{uuid4().hex[:8]}@example.com",
            full_name=full_name,
            hashed_password=hash_password(password),
            is_active=is_active,
            is_superuser=is_superuser,
            is_google_auth=is_google_auth,
        )
        user.id = user_id or uuid4()
        user.created_at = now
        user.updated_at = now
        return user

    return _make_user


@pytest.fixture
def make_service():
    def _make_service(
        *,
        service_id=None,
        name=None,
        owner_id=None,
        team_id=None,
        description="Test service",
    ):
        now = datetime.now(timezone.utc)
        service = Service(
            name=name or f"service-{uuid4().hex[:8]}",
            description=description,
            repository_url="https://example.com/repo.git",
            tags=[],
            meta_data={},
            owner_id=owner_id or uuid4(),
            team_id=team_id,
        )
        service.id = service_id or uuid4()
        service.created_at = now
        service.updated_at = now
        return service

    return _make_service


@pytest.fixture
def make_deployment():
    def _make_deployment(
        *,
        deployment_id=None,
        service_id=None,
        triggered_by=None,
        version="1.0.0",
        commit_sha="a" * 40,
        environment=Environment.STAGING,
    ):
        now = datetime.now(timezone.utc)
        deployment = Deployment(
            service_id=service_id or uuid4(),
            commit_sha=commit_sha,
            version=version,
            environment=environment,
            triggered_by=triggered_by or uuid4(),
        )
        deployment.id = deployment_id or uuid4()
        deployment.created_at = now
        deployment.updated_at = now
        return deployment

    return _make_deployment


@pytest.fixture
def auth_app():
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    return app


@pytest.fixture
def client(auth_app):
    with TestClient(auth_app) as test_client:
        yield test_client
    auth_app.dependency_overrides.clear()


@pytest.fixture
def override_db(auth_app):
    def _override(session):
        async def _db_override():
            yield session

        auth_app.dependency_overrides[get_db] = _db_override

    return _override


@pytest.fixture
def override_current_user(auth_app):
    def _override(user):
        async def _current_user_override():
            return user

        auth_app.dependency_overrides[get_current_user] = _current_user_override

    return _override
