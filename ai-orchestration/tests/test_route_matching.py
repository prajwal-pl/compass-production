from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.docs as docs_api
import api.metrics as metrics_api
from lib.auth_context import get_current_user


def _build_app(current_user):
    app = FastAPI()
    app.include_router(docs_api.router, prefix="/docs", tags=["docs"])
    app.include_router(metrics_api.router, prefix="/metrics", tags=["metrics"])

    async def _current_user_override():
        return current_user

    app.dependency_overrides[get_current_user] = _current_user_override
    return app


def test_docs_search_static_route_takes_precedence(make_user):
    user = make_user(is_superuser=True)
    app = _build_app(user)

    with TestClient(app) as client:
        response = client.get("/docs/search", params={"query": "compass"})

    assert response.status_code == 200
    assert response.json()["message"].startswith("Search docs for")


def test_metrics_overview_static_route_takes_precedence(make_user):
    user = make_user(is_superuser=True)
    app = _build_app(user)

    with TestClient(app) as client:
        response = client.get("/metrics/overview")

    assert response.status_code == 200
    assert response.json()["message"] == "Get platform metrics overview is a work in progress"
