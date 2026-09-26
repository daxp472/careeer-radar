import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.rate_limiter import rate_limiter

client = TestClient(app)


def test_security_headers_present():
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" in headers


def test_rate_limit_headers_and_enforcement():
    rate_limiter.reset()

    # Initial request should have limit and remaining headers
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers

    # Exceed limit for a tight path
    test_ip = "192.168.1.100"
    path = "/api/v1/jobs/admin/refresh"  # limit is 5/min
    
    for i in range(5):
        allowed, limit, remaining, retry_after = rate_limiter.check_rate_limit(test_ip, path)
        assert allowed is True

    # 6th request should be blocked
    allowed, limit, remaining, retry_after = rate_limiter.check_rate_limit(test_ip, path)
    assert allowed is False
    assert retry_after > 0

    rate_limiter.reset()
