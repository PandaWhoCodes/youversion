# Simplify Sync/Async Client Architecture

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the mixin-based async-first architecture with separate, straightforward sync and async clients.

**Architecture:** Two independent client classes—`YouVersionClient` (sync) and `AsyncYouVersionClient` (async)—each with their own HTTP client and API methods. No mixins, no bridge classes, no fake async. Some code duplication is acceptable for clarity.

**Tech Stack:** httpx (sync Client and AsyncClient), pydantic models, Result type for error handling

---

## Summary of Changes

**Delete:**
- `src/youversion/bibles/api.py` - Remove `BibleAPIMixin` and `HTTPAdapter` protocol
- `_SyncBackedAsyncClient` class from `client.py`

**Simplify:**
- `src/youversion/core/http.py` - Make `SyncHTTPAdapter` truly sync (no async methods)
- `src/youversion/core/client.py` - Inline API methods directly in each client

**Update:**
- Tests to work with new structure

---

## Task 1: Create Sync HTTP Adapter (truly sync)

**Files:**
- Modify: `src/youversion/core/http.py`

**Step 1: Update SyncHTTPAdapter to be truly sync**

Remove `async` from all methods. The adapter should have plain sync methods.

```python
class SyncHTTPAdapter:
    """Synchronous HTTP adapter using httpx."""

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

    def get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a GET request."""
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

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
```

**Step 2: Run tests to check what breaks**

Run: `pytest tests/unit/core/test_http.py -v`
Expected: Tests will fail because they use `await adapter.get()`

**Step 3: Commit**

```bash
git add src/youversion/core/http.py
git commit -m "refactor: make SyncHTTPAdapter truly synchronous"
```

---

## Task 2: Update HTTP Adapter Tests

**Files:**
- Modify: `tests/unit/core/test_http.py`

**Step 1: Remove async from SyncHTTPAdapter tests**

Update all `SyncHTTPAdapter` tests to be synchronous:

```python
"""Tests for HTTP adapters."""

import pytest
import respx

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
)
from youversion.core.http import AsyncHTTPAdapter, SyncHTTPAdapter


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
            timeout=0.001,
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


class TestAsyncHTTPAdapter:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json={"id": 111, "title": "NIV"}
        )
        adapter = AsyncHTTPAdapter(
            api_key="test-key",
            base_url="https://api.youversion.com",
            timeout=30.0,
        )
        response = await adapter.get("/v1/bibles/111")
        assert response.status_code == 200
        await adapter.close()
```

**Step 2: Run tests**

Run: `pytest tests/unit/core/test_http.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/core/test_http.py
git commit -m "test: update HTTP adapter tests for sync adapter"
```

---

## Task 3: Rewrite YouVersionClient (sync) with inline API methods

**Files:**
- Modify: `src/youversion/core/client.py`

**Step 1: Rewrite YouVersionClient with direct API implementation**

Remove the mixin inheritance and bridge class. Implement API methods directly:

```python
"""YouVersion SDK clients."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import httpx

from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core.domain_errors import NotFoundError, ValidationError
from youversion.core.http import AsyncHTTPAdapter, SyncHTTPAdapter
from youversion.core.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

DEFAULT_BASE_URL = "https://api.youversion.com"
DEFAULT_TIMEOUT = 30.0


class YouVersionClient:
    """Synchronous YouVersion API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = SyncHTTPAdapter(api_key=api_key, base_url=base_url, timeout=timeout)

    def __enter__(self) -> YouVersionClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    # Version methods
    def get_versions(
        self,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = self._http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = self._http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    # Book methods
    def get_books(
        self, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = self._http.get(f"/v1/bibles/{version_id}/books")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(version_id),
                    message=f"Bible version {version_id} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleBook].model_validate(data))

    def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    # Chapter methods
    def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleChapter].model_validate(data))

    def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    # Verse methods
    def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses"
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVerse].model_validate(data))

    def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses/{verse}"
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="verse",
                    identifier=f"{book}.{chapter}.{verse}",
                    message=f"Verse {book} {chapter}:{verse} not found",
                )
            )

        return Ok(BibleVerse.model_validate(response.json()))

    # Passage methods
    def get_passage(
        self,
        version_id: int,
        usfm: str,
        *,
        format: Literal["text", "html"] = "text",
        include_headings: bool = False,
        include_notes: bool = False,
    ) -> Result[BiblePassage, NotFoundError | ValidationError]:
        """Get passage content."""
        params: dict[str, Any] = {
            "format": format,
            "include_headings": str(include_headings).lower(),
            "include_notes": str(include_notes).lower(),
        }
        response = self._http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="passage",
                    identifier=usfm,
                    message=f"Passage {usfm} not found",
                )
            )

        if response.status_code == 400:
            return Err(ValidationError(field="usfm", reason="Invalid USFM format"))

        return Ok(BiblePassage.model_validate(response.json()))


class AsyncYouVersionClient:
    """Asynchronous YouVersion API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = AsyncHTTPAdapter(api_key=api_key, base_url=base_url, timeout=timeout)

    async def __aenter__(self) -> AsyncYouVersionClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    # Version methods
    async def get_versions(
        self,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = await self._http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    async def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = await self._http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    # Book methods
    async def get_books(
        self, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(version_id),
                    message=f"Bible version {version_id} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleBook].model_validate(data))

    async def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    # Chapter methods
    async def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleChapter].model_validate(data))

    async def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    # Verse methods
    async def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = await self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses"
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVerse].model_validate(data))

    async def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = await self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses/{verse}"
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="verse",
                    identifier=f"{book}.{chapter}.{verse}",
                    message=f"Verse {book} {chapter}:{verse} not found",
                )
            )

        return Ok(BibleVerse.model_validate(response.json()))

    # Passage methods
    async def get_passage(
        self,
        version_id: int,
        usfm: str,
        *,
        format: Literal["text", "html"] = "text",
        include_headings: bool = False,
        include_notes: bool = False,
    ) -> Result[BiblePassage, NotFoundError | ValidationError]:
        """Get passage content."""
        params: dict[str, Any] = {
            "format": format,
            "include_headings": str(include_headings).lower(),
            "include_notes": str(include_notes).lower(),
        }
        response = await self._http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="passage",
                    identifier=usfm,
                    message=f"Passage {usfm} not found",
                )
            )

        if response.status_code == 400:
            return Err(ValidationError(field="usfm", reason="Invalid USFM format"))

        return Ok(BiblePassage.model_validate(response.json()))
```

**Step 2: Run client tests**

Run: `pytest tests/unit/core/test_client.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add src/youversion/core/client.py
git commit -m "refactor: simplify clients with inline API methods"
```

---

## Task 4: Delete the mixin file and update exports

**Files:**
- Delete: `src/youversion/bibles/api.py`
- Modify: `src/youversion/bibles/__init__.py`

**Step 1: Check what bibles/__init__.py exports**

Read the file first.

**Step 2: Remove api.py imports from bibles/__init__.py if any**

The mixin was internal, so likely nothing to remove from public exports.

**Step 3: Delete api.py**

```bash
rm src/youversion/bibles/api.py
```

**Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: Some tests in `test_api.py` will fail (they test the mixin directly)

**Step 5: Commit deletion**

```bash
git add -A
git commit -m "refactor: remove BibleAPIMixin (no longer needed)"
```

---

## Task 5: Update or remove mixin tests

**Files:**
- Modify: `tests/unit/bibles/test_api.py`

**Step 1: Decide what to do with mixin tests**

The mixin tests (`test_api.py`) tested the mixin directly. Since we're removing the mixin, we have two options:
1. Delete the tests (sync client tests already cover the same functionality)
2. Convert them to async client tests

Since `test_client.py` already tests the sync client, convert `test_api.py` to test `AsyncYouVersionClient`:

```python
"""Tests for AsyncYouVersionClient."""

import json
from pathlib import Path

import pytest
import respx

from youversion.core.client import AsyncYouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestAsyncYouVersionClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_versions(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            json=load_fixture("versions.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_versions("en")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2
        assert result.value.data[0].abbreviation == "NIV"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_version(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json=load_fixture("version_111.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_version(111)

        assert isinstance(result, Ok)
        assert result.value.id == 111
        assert result.value.abbreviation == "NIV"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_version_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/999").respond(
            status_code=404, json={"error": "not_found"}
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_version(999)

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)
        assert result.error.resource == "version"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_books(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books").respond(
            json=load_fixture("books.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_books(111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_book(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN").respond(
            json=load_fixture("book_jhn.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_book(111, "JHN")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN"
        assert result.value.chapters is not None
        assert len(result.value.chapters) == 3

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_chapter(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN/chapters/3").respond(
            json=load_fixture("chapter_jhn3.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_chapter(111, "JHN", 3)

        assert isinstance(result, Ok)
        assert result.value.id == "3"
        assert result.value.verses is not None
        assert len(result.value.verses) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_passage(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/passages/JHN.3.16").respond(
            json=load_fixture("passage_jhn316.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_passage(111, "JHN.3.16")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN.3.16"
        assert "God so loved" in result.value.content
```

**Step 2: Run tests**

Run: `pytest tests/unit/bibles/test_api.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/bibles/test_api.py
git commit -m "test: convert mixin tests to async client tests"
```

---

## Task 6: Final verification and cleanup

**Files:**
- Check all imports work correctly

**Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 2: Run type checker**

Run: `mypy src/youversion`
Expected: No errors

**Step 3: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "chore: cleanup after sync/async refactor"
```

---

## Summary of Final Architecture

```
src/youversion/
├── core/
│   ├── client.py          # YouVersionClient (sync) + AsyncYouVersionClient (async)
│   ├── http.py            # SyncHTTPAdapter + AsyncHTTPAdapter
│   ├── errors.py          # Exceptions
│   ├── domain_errors.py   # Result errors
│   └── result.py          # Result type
└── bibles/
    ├── models.py          # Pydantic models
    └── __init__.py        # Exports
```

No mixins. No bridge classes. Two straightforward clients.
