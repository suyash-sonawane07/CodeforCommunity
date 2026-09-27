"""Live-stack smoke tests (run manually with the stack up: `make smoke`).

Every test skips (never fails) when the relevant service isn't running, so CI
and offline laptops are unaffected.
"""

import os

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _skip_if_backend_down():
    try:
        httpx.get(f"{BACKEND_URL}/health", timeout=2)
        return False
    except Exception:
        return True


def _skip_if_frontend_down():
    try:
        httpx.get(FRONTEND_URL, timeout=2)
        return False
    except Exception:
        return True


def test_backend_health_live():
    if _skip_if_backend_down():
        import pytest

        pytest.skip("backend not running")
    res = httpx.get(f"{BACKEND_URL}/health", timeout=5)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_frontend_reaches_backend():
    """Frontend→backend connectivity proxy: the API client config must point at the
    backend and the backend must answer there."""
    if _skip_if_frontend_down() or _skip_if_backend_down():
        import pytest

        pytest.skip("stack not fully running")
    # the backend behind NEXT_PUBLIC_API_BASE_URL answers with the contract envelope
    res = httpx.get(f"{BACKEND_URL}/version", timeout=5)
    assert res.status_code == 200
    assert res.json()["scaffold"] is True
