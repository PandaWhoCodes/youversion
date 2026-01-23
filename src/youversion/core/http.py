"""HTTP adapter abstraction for sync/async requests - async-first design."""

from __future__ import annotations

from typing import Any

import httpx

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
)


class AsyncHTTPAdapter:
    """Asynchronous HTTP adapter using httpx - primary implementation."""

    def __init__(self, api_key: str, base_url: str, timeout: float) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "X-YVP-App-Key": api_key,
                "Accept": "application/json",
            },
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a GET request."""
        try:
            response = await self._client.get(path, params=params)
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

        self._check_error_status(response)
        return response

    def _check_error_status(self, response: httpx.Response) -> None:
        """Raise exceptions for unexpected errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid or missing API key")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=float(retry_after) if retry_after else None,
            )

        if response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()


class SyncHTTPAdapter:
    """Synchronous HTTP adapter that wraps sync calls as awaitables.

    This adapter uses httpx's sync client but provides an async-compatible
    interface by returning immediate awaitables. This allows the async-first
    mixin to work with both sync and async clients.
    """

    def __init__(self, api_key: str, base_url: str, timeout: float) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "X-YVP-App-Key": api_key,
                "Accept": "application/json",
            },
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a GET request - sync call wrapped as awaitable."""
        try:
            response = self._client.get(path, params=params)
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

        self._check_error_status(response)
        return response

    def _check_error_status(self, response: httpx.Response) -> None:
        """Raise exceptions for unexpected errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid or missing API key")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=float(retry_after) if retry_after else None,
            )

        if response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
