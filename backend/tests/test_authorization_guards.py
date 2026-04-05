from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.dependencies as dependencies_api
import api.deployments as deployments_api
import api.docs as docs_api
import api.metrics as metrics_api
import api.services as services_api
from db.db import get_db
from lib.auth_context import get_current_user


def _build_app(current_user, session):
    app = FastAPI()
    app.include_router(services_api.router, prefix="/services", tags=["services"])
    app.include_router(deployments_api.router, prefix="/deployments", tags=["deployments"])
    app.include_router(docs_api.router, prefix="/docs", tags=["docs"])
    app.include_router(metrics_api.router, prefix="/metrics", tags=["metrics"])
    app.include_router(dependencies_api.router, prefix="/dependencies", tags=["dependencies"])

    async def _current_user_override():
        return current_user

    async def _db_override():
        yield session

    app.dependency_overrides[get_current_user] = _current_user_override
    app.dependency_overrides[get_db] = _db_override
    return app


def test_services_update_requires_owner_or_superuser(make_session, make_service, make_user):
    current_user = make_user(is_superuser=False)
    service = make_service(owner_id=make_user().id)

    session = make_session([service])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        response = client.put(f"/services/{service.id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Owner or superuser access required"


def test_services_get_allows_owner(make_session, make_service, make_user):
    current_user = make_user(is_superuser=False)
    service = make_service(owner_id=current_user.id)

    session = make_session([service])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        response = client.get(f"/services/{service.id}")

    assert response.status_code == 200


def test_docs_generate_requires_owner(make_session, make_service, make_user):
    current_user = make_user(is_superuser=False)
    service = make_service(owner_id=make_user().id)

    session = make_session([service])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        response = client.post(f"/docs/{service.id}/generate")

    assert response.status_code == 403
    assert response.json()["detail"] == "Owner or superuser access required"


def test_deployments_list_requires_superuser_without_service_filter(make_session, make_user):
    current_user = make_user(is_superuser=False)
    session = make_session([])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        response = client.get("/deployments/")

    assert response.status_code == 403
    assert response.json()["detail"] == "Superuser privileges are required"


def test_deployment_access_requires_owner_team_or_superuser(
    make_session,
    make_deployment,
    make_service,
    make_user,
):
    current_user = make_user(is_superuser=False)
    service = make_service(owner_id=make_user().id)
    deployment = make_deployment(service_id=service.id)

    # deployment query -> service query -> team-membership check (None)
    session = make_session([deployment, service, None])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        response = client.get(f"/deployments/{deployment.id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this service"


def test_metrics_and_dependency_graph_require_superuser(make_session, make_user):
    current_user = make_user(is_superuser=False)
    session = make_session([])
    app = _build_app(current_user, session)

    with TestClient(app) as client:
        metrics_response = client.get("/metrics/overview")
        dependencies_response = client.get("/dependencies/")

    assert metrics_response.status_code == 403
    assert dependencies_response.status_code == 403
