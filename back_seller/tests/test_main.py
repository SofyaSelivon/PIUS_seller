import pytest
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.main import (
    app,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

client = TestClient(app)


@pytest.mark.asyncio
async def test_http_exception_handler():
    request = Request(scope={"type": "http"})
    exc = HTTPException(status_code=400, detail="Bad request")

    response = await http_exception_handler(request, exc)

    assert response.status_code == 400

    body = response.body.decode()

    assert "Bad request" in body
    assert "400" in body


@pytest.mark.asyncio
async def test_validation_exception_handler():
    request = Request(scope={"type": "http"})
    exc = RequestValidationError(errors=[{"msg": "invalid"}])

    response = await validation_exception_handler(request, exc)

    assert response.status_code == 422

    body = response.body.decode()

    assert "Validation failed" in body
    assert "VALIDATION_ERROR" in body


@pytest.mark.asyncio
async def test_generic_exception_handler():
    request = Request(scope={"type": "http"})
    exc = Exception("boom")

    response = await generic_exception_handler(request, exc)

    assert response.status_code == 500

    body = response.body.decode()

    assert "Internal server error" in body
    assert "INTERNAL_ERROR" in body


def test_app_has_routes():
    routes = [route.path for route in app.routes]

    assert any("/api" in r or "/" in r for r in routes)


def test_cors_middleware_enabled():
    middleware_types = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_types
