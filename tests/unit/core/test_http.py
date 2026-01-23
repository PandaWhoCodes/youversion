"""Tests for HTTP adapter."""

import pytest
import respx

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
)
from youversion.core.http import SyncHTTPAdapter


class TestSyncHTTPAdapter:
    def test_creates_with_api_key(self) -> None:
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        assert adapter._api_key == "test-key"

    @respx.mock
    def test_get_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json={"id": 111, "title": "NIV"}
        )
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        response = adapter.get("/v1/bibles/111")
        assert response.status_code == 200
        assert response.json() == {"id": 111, "title": "NIV"}

    @respx.mock
    def test_get_includes_api_key_header(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/bibles").respond(json={})
        adapter = SyncHTTPAdapter(
            api_key="my-secret-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        adapter.get("/v1/bibles")
        assert route.calls[0].request.headers["X-YVP-App-Key"] == "my-secret-key"

    @respx.mock
    def test_get_with_query_params(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/bibles").respond(json={})
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        adapter.get("/v1/bibles", params={"language_ranges[]": "en"})
        assert "language_ranges%5B%5D=en" in str(route.calls[0].request.url)

    @respx.mock
    def test_raises_authentication_error_on_401(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(status_code=401)
        adapter = SyncHTTPAdapter(
            api_key="bad-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        with pytest.raises(AuthenticationError):
            adapter.get("/v1/bibles")

    @respx.mock
    def test_raises_rate_limit_error_on_429(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            status_code=429, headers={"Retry-After": "60"}
        )
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        with pytest.raises(RateLimitError) as exc_info:
            adapter.get("/v1/bibles")
        assert exc_info.value.retry_after == 60.0

    @respx.mock
    def test_raises_server_error_on_500(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(status_code=500)
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        with pytest.raises(ServerError) as exc_info:
            adapter.get("/v1/bibles")
        assert exc_info.value.status_code == 500

    def test_raises_network_error_on_connection_failure(self) -> None:
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=0.001,  # Very short timeout to trigger failure
        )
        with pytest.raises(NetworkError):
            adapter.get("/v1/bibles")

    @respx.mock
    def test_returns_response_for_404(self, respx_mock: respx.MockRouter) -> None:
        """404 is a domain error, not an exception - let caller handle it."""
        respx_mock.get("https://api.youversion.com/v1/bibles/999").respond(status_code=404)
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        response = adapter.get("/v1/bibles/999")
        assert response.status_code == 404

    @respx.mock
    def test_returns_response_for_400(self, respx_mock: respx.MockRouter) -> None:
        """400 is a validation error, not an exception - let caller handle it."""
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(status_code=400)
        adapter = SyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        response = adapter.get("/v1/bibles")
        assert response.status_code == 400
