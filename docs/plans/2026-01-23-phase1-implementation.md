# Phase 1: Core SDK Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the foundational YouVersion Python SDK with sync/async clients supporting Bible version, book, chapter, verse, and passage APIs.

**Architecture:** Domain-organized src layout with Pydantic models, Result types for domain errors, exceptions for unexpected errors, and httpx for HTTP. Mixins share logic between sync/async clients.

**Tech Stack:** Python 3.11+, Pydantic v2, httpx, pytest, respx, mypy, pyright, ruff

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/youversion/__init__.py`
- Create: `src/youversion/py.typed`
- Create: `.github/workflows/ci.yml`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "youversion"
version = "0.1.0"
description = "Python SDK for YouVersion API"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Ashish", email = "ashish@example.com" }
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.8",
    "pyright>=1.1.350",
    "ruff>=0.2",
]

[tool.hatch.build.targets.wheel]
packages = ["src/youversion"]

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "TCH"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["live: tests that hit real API"]
asyncio_mode = "auto"
```

**Step 2: Create src/youversion/__init__.py**

```python
"""YouVersion Python SDK."""

__version__ = "0.1.0"
```

**Step 3: Create src/youversion/py.typed (empty marker file)**

```
```

**Step 4: Create .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run mypy src/
      - run: uv run pyright src/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --dev
      - run: uv run pytest --cov=youversion --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

**Step 5: Initialize uv and verify setup**

Run: `cd /Users/ashish/Documents/PERSONAL/youversion && uv sync --dev`
Expected: Dependencies installed successfully

**Step 6: Commit**

```bash
git add pyproject.toml src/ .github/
git commit -m "feat: initialize project with pyproject.toml and CI"
```

---

## Task 2: Core Result Type

**Files:**
- Create: `src/youversion/core/__init__.py`
- Create: `src/youversion/core/result.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/core/__init__.py`
- Create: `tests/unit/core/test_result.py`

**Step 1: Write the failing test for Result type**

Create `tests/unit/core/test_result.py`:

```python
"""Tests for Result type."""

from youversion.core.result import Err, Ok, Result, is_err, is_ok


def test_ok_contains_value() -> None:
    result: Result[int, str] = Ok(42)
    assert is_ok(result)
    assert not is_err(result)
    assert result.value == 42


def test_err_contains_error() -> None:
    result: Result[int, str] = Err("something went wrong")
    assert is_err(result)
    assert not is_ok(result)
    assert result.error == "something went wrong"


def test_ok_is_frozen() -> None:
    result = Ok(42)
    try:
        result.value = 100  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_err_is_frozen() -> None:
    result = Err("error")
    try:
        result.error = "new error"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_pattern_matching_ok() -> None:
    result: Result[int, str] = Ok(42)
    match result:
        case Ok(value):
            assert value == 42
        case Err(_):
            assert False, "Should not match Err"


def test_pattern_matching_err() -> None:
    result: Result[int, str] = Err("oops")
    match result:
        case Ok(_):
            assert False, "Should not match Ok"
        case Err(error):
            assert error == "oops"
```

**Step 2: Create empty __init__.py files and run test to verify it fails**

Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/unit/core/__init__.py`, `src/youversion/core/__init__.py` (all empty).

Run: `uv run pytest tests/unit/core/test_result.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement Result type**

Create `src/youversion/core/result.py`:

```python
"""Result type for explicit error handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeGuard, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok[T]:
    """Represents a successful result containing a value."""

    value: T


@dataclass(frozen=True, slots=True)
class Err[E]:
    """Represents a failed result containing an error."""

    error: E


type Result[T, E] = Ok[T] | Err[E]


def is_ok[T, E](result: Result[T, E]) -> TypeGuard[Ok[T]]:
    """Check if result is Ok."""
    return isinstance(result, Ok)


def is_err[T, E](result: Result[T, E]) -> TypeGuard[Err[E]]:
    """Check if result is Err."""
    return isinstance(result, Err)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_result.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/core/result.py && uv run pyright src/youversion/core/result.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/core/ tests/
git commit -m "feat(core): add Result type with Ok/Err for explicit error handling"
```

---

## Task 3: Exception Hierarchy

**Files:**
- Create: `src/youversion/core/errors.py`
- Create: `tests/unit/core/test_errors.py`

**Step 1: Write the failing test for exceptions**

Create `tests/unit/core/test_errors.py`:

```python
"""Tests for exception hierarchy."""

import pytest

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
    YouVersionError,
)


def test_youversion_error_is_base() -> None:
    with pytest.raises(YouVersionError):
        raise YouVersionError("base error")


def test_network_error_inherits_from_base() -> None:
    with pytest.raises(YouVersionError):
        raise NetworkError("connection failed")


def test_authentication_error_inherits_from_base() -> None:
    with pytest.raises(YouVersionError):
        raise AuthenticationError("invalid api key")


def test_rate_limit_error_has_retry_after() -> None:
    error = RateLimitError("rate limited", retry_after=30.0)
    assert error.retry_after == 30.0
    assert "rate limited" in str(error)


def test_rate_limit_error_retry_after_optional() -> None:
    error = RateLimitError("rate limited")
    assert error.retry_after is None


def test_server_error_has_status_code() -> None:
    error = ServerError("internal error", status_code=500)
    assert error.status_code == 500
    assert "internal error" in str(error)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/core/test_errors.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement exception hierarchy**

Create `src/youversion/core/errors.py`:

```python
"""Exception hierarchy for unexpected errors."""

from __future__ import annotations


class YouVersionError(Exception):
    """Base exception for all SDK errors."""


class NetworkError(YouVersionError):
    """Connection failed, timeout, DNS issues."""


class AuthenticationError(YouVersionError):
    """Invalid or expired API key."""


class RateLimitError(YouVersionError):
    """429 - Rate limit exceeded."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(YouVersionError):
    """5xx responses from API."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_errors.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/core/errors.py && uv run pyright src/youversion/core/errors.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/core/errors.py tests/unit/core/test_errors.py
git commit -m "feat(core): add exception hierarchy for unexpected errors"
```

---

## Task 4: Domain Error Models

**Files:**
- Create: `src/youversion/core/domain_errors.py`
- Create: `tests/unit/core/test_domain_errors.py`

**Step 1: Write the failing test for domain errors**

Create `tests/unit/core/test_domain_errors.py`:

```python
"""Tests for domain error models."""

from youversion.core.domain_errors import NotFoundError, ValidationError


def test_not_found_error_fields() -> None:
    error = NotFoundError(resource="version", identifier="999", message="Bible version not found")
    assert error.resource == "version"
    assert error.identifier == "999"
    assert error.message == "Bible version not found"


def test_not_found_error_from_dict() -> None:
    data = {"resource": "book", "identifier": "XYZ", "message": "Book not found"}
    error = NotFoundError.model_validate(data)
    assert error.resource == "book"


def test_validation_error_fields() -> None:
    error = ValidationError(field="language_ranges", reason="Invalid format")
    assert error.field == "language_ranges"
    assert error.reason == "Invalid format"


def test_validation_error_from_dict() -> None:
    data = {"field": "day", "reason": "Must be 1-366"}
    error = ValidationError.model_validate(data)
    assert error.field == "day"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/core/test_domain_errors.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement domain error models**

Create `src/youversion/core/domain_errors.py`:

```python
"""Domain error models for expected errors (returned, not raised)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class NotFoundError(BaseModel, frozen=True):
    """Resource not found error."""

    resource: Literal[
        "version", "book", "chapter", "verse", "passage", "language", "highlight"
    ]
    identifier: str
    message: str


class ValidationError(BaseModel, frozen=True):
    """Validation error for invalid input."""

    field: str
    reason: str


type DomainError = NotFoundError | ValidationError
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_domain_errors.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/core/domain_errors.py && uv run pyright src/youversion/core/domain_errors.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/core/domain_errors.py tests/unit/core/test_domain_errors.py
git commit -m "feat(core): add domain error models (NotFoundError, ValidationError)"
```

---

## Task 5: Bible Models

**Files:**
- Create: `src/youversion/bibles/__init__.py`
- Create: `src/youversion/bibles/models.py`
- Create: `tests/unit/bibles/__init__.py`
- Create: `tests/unit/bibles/test_models.py`

**Step 1: Write the failing test for Bible models**

Create `tests/unit/bibles/test_models.py`:

```python
"""Tests for Bible models."""

from youversion.bibles.models import (
    BibleBook,
    BibleBookIntro,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)


def test_bible_version_from_api_response() -> None:
    data = {
        "id": 111,
        "abbreviation": "NIV",
        "title": "New International Version",
        "language_tag": "en",
        "copyright_short": "© Biblica",
        "copyright_long": "New International Version®, NIV® Copyright © 1973...",
    }
    version = BibleVersion.model_validate(data)
    assert version.id == 111
    assert version.abbreviation == "NIV"
    assert version.language_tag == "en"


def test_bible_version_optional_fields() -> None:
    data = {
        "id": 1,
        "abbreviation": "KJV",
        "title": "King James Version",
        "language_tag": "en",
    }
    version = BibleVersion.model_validate(data)
    assert version.copyright_short is None
    assert version.copyright_long is None


def test_bible_book_from_api_response() -> None:
    data = {
        "id": "GEN",
        "title": "Genesis",
        "abbreviation": "Gen",
        "canon": "old_testament",
    }
    book = BibleBook.model_validate(data)
    assert book.id == "GEN"
    assert book.canon == "old_testament"


def test_bible_book_with_chapters() -> None:
    data = {
        "id": "MAT",
        "title": "Matthew",
        "abbreviation": "Matt",
        "canon": "new_testament",
        "chapters": [
            {"id": 1, "passage": "MAT.1", "title": "Chapter 1"},
        ],
    }
    book = BibleBook.model_validate(data)
    assert book.chapters is not None
    assert len(book.chapters) == 1


def test_bible_chapter_from_api_response() -> None:
    data = {
        "id": 3,
        "passage": "JHN.3",
        "title": "Chapter 3",
    }
    chapter = BibleChapter.model_validate(data)
    assert chapter.id == 3
    assert chapter.passage == "JHN.3"


def test_bible_verse_from_api_response() -> None:
    data = {
        "id": 16,
        "passage": "JHN.3.16",
        "title": "Verse 16",
    }
    verse = BibleVerse.model_validate(data)
    assert verse.id == 16
    assert verse.passage == "JHN.3.16"


def test_bible_passage_from_api_response() -> None:
    data = {
        "id": "JHN.3.16",
        "content": "For God so loved the world...",
        "reference": "John 3:16",
    }
    passage = BiblePassage.model_validate(data)
    assert passage.id == "JHN.3.16"
    assert "God so loved" in passage.content


def test_paginated_response_with_versions() -> None:
    data = {
        "data": [
            {"id": 1, "abbreviation": "NIV", "title": "NIV", "language_tag": "en"},
            {"id": 2, "abbreviation": "ESV", "title": "ESV", "language_tag": "en"},
        ],
        "next_page_token": "abc123",
        "total_count": 100,
    }
    response = PaginatedResponse[BibleVersion].model_validate(data)
    assert len(response.data) == 2
    assert response.next_page_token == "abc123"
    assert response.total_count == 100


def test_paginated_response_no_next_page() -> None:
    data = {
        "data": [{"id": 1, "abbreviation": "NIV", "title": "NIV", "language_tag": "en"}],
    }
    response = PaginatedResponse[BibleVersion].model_validate(data)
    assert response.next_page_token is None
    assert response.total_count is None
```

**Step 2: Create __init__.py files and run test to verify it fails**

Create `src/youversion/bibles/__init__.py` and `tests/unit/bibles/__init__.py` (empty).

Run: `uv run pytest tests/unit/bibles/test_models.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement Bible models**

Create `src/youversion/bibles/models.py`:

```python
"""Bible domain models."""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response from API."""

    data: list[T]
    next_page_token: str | None = None
    total_count: int | None = None


class BibleVersion(BaseModel, frozen=True):
    """Bible translation/version."""

    id: int
    abbreviation: str
    title: str
    language_tag: str
    copyright_short: str | None = None
    copyright_long: str | None = None


class BibleBookIntro(BaseModel, frozen=True):
    """Introductory content for a book."""

    id: str
    passage: str
    title: str


class BibleChapter(BaseModel, frozen=True):
    """Chapter within a book."""

    id: int
    passage: str
    title: str
    verses: list[BibleVerse] | None = None


class BibleVerse(BaseModel, frozen=True):
    """Verse metadata."""

    id: int
    passage: str
    title: str


class BibleBook(BaseModel, frozen=True):
    """Book within a Bible version."""

    id: str  # USFM identifier (e.g., "GEN", "MAT")
    title: str
    abbreviation: str
    canon: Literal["old_testament", "new_testament", "deuterocanon"]
    chapters: list[BibleChapter] | None = None
    intro: BibleBookIntro | None = None


class BiblePassage(BaseModel, frozen=True):
    """Actual passage content."""

    id: str  # USFM reference
    content: str
    reference: str  # Human-readable (e.g., "John 3:16")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/bibles/test_models.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/bibles/models.py && uv run pyright src/youversion/bibles/models.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/bibles/ tests/unit/bibles/
git commit -m "feat(bibles): add Bible domain models (Version, Book, Chapter, Verse, Passage)"
```

---

## Task 6: HTTP Adapter Abstraction

**Files:**
- Create: `src/youversion/core/http.py`
- Create: `tests/unit/core/test_http.py`

**Step 1: Write the failing test for HTTP adapter**

Create `tests/unit/core/test_http.py`:

```python
"""Tests for HTTP adapter."""

import httpx
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/core/test_http.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement HTTP adapter**

Create `src/youversion/core/http.py`:

```python
"""HTTP adapter abstraction for sync/async requests."""

from __future__ import annotations

from typing import Any

import httpx

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
)


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

    def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
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
        """Raise exceptions for unexpected errors (not 4xx domain errors)."""
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


class AsyncHTTPAdapter:
    """Asynchronous HTTP adapter using httpx."""

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

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_http.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/core/http.py && uv run pyright src/youversion/core/http.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/core/http.py tests/unit/core/test_http.py
git commit -m "feat(core): add sync/async HTTP adapters with error handling"
```

---

## Task 7: Bible API Mixin

**Files:**
- Create: `src/youversion/bibles/api.py`
- Create: `tests/unit/bibles/test_api.py`
- Create: `tests/fixtures/` directory
- Create: `tests/fixtures/versions.json`
- Create: `tests/fixtures/version_111.json`

**Step 1: Create test fixtures**

Create `tests/fixtures/versions.json`:

```json
{
  "data": [
    {
      "id": 111,
      "abbreviation": "NIV",
      "title": "New International Version",
      "language_tag": "en",
      "copyright_short": "© Biblica"
    },
    {
      "id": 59,
      "abbreviation": "ESV",
      "title": "English Standard Version",
      "language_tag": "en",
      "copyright_short": "© Crossway"
    }
  ],
  "next_page_token": null,
  "total_count": 2
}
```

Create `tests/fixtures/version_111.json`:

```json
{
  "id": 111,
  "abbreviation": "NIV",
  "title": "New International Version",
  "language_tag": "en",
  "copyright_short": "© Biblica",
  "copyright_long": "New International Version®, NIV® Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc.®"
}
```

Create `tests/fixtures/books.json`:

```json
{
  "data": [
    {
      "id": "GEN",
      "title": "Genesis",
      "abbreviation": "Gen",
      "canon": "old_testament"
    },
    {
      "id": "EXO",
      "title": "Exodus",
      "abbreviation": "Exod",
      "canon": "old_testament"
    }
  ]
}
```

Create `tests/fixtures/book_jhn.json`:

```json
{
  "id": "JHN",
  "title": "John",
  "abbreviation": "John",
  "canon": "new_testament",
  "chapters": [
    {"id": 1, "passage": "JHN.1", "title": "Chapter 1"},
    {"id": 2, "passage": "JHN.2", "title": "Chapter 2"},
    {"id": 3, "passage": "JHN.3", "title": "Chapter 3"}
  ]
}
```

Create `tests/fixtures/chapter_jhn3.json`:

```json
{
  "id": 3,
  "passage": "JHN.3",
  "title": "Chapter 3",
  "verses": [
    {"id": 1, "passage": "JHN.3.1", "title": "Verse 1"},
    {"id": 16, "passage": "JHN.3.16", "title": "Verse 16"}
  ]
}
```

Create `tests/fixtures/passage_jhn316.json`:

```json
{
  "id": "JHN.3.16",
  "content": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
  "reference": "John 3:16"
}
```

**Step 2: Write the failing test for Bible API**

Create `tests/unit/bibles/test_api.py`:

```python
"""Tests for Bible API mixin."""

import json
from pathlib import Path

import respx

from youversion.bibles.api import BibleAPIMixin
from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core.domain_errors import NotFoundError
from youversion.core.http import SyncHTTPAdapter
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestBibleAPIMixin:
    @respx.mock
    def test_get_versions(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            json=load_fixture("versions.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_versions(http, "en")

        assert isinstance(result, Ok)
        response = result.value
        assert isinstance(response, PaginatedResponse)
        assert len(response.data) == 2
        assert response.data[0].abbreviation == "NIV"

    @respx.mock
    def test_get_version(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json=load_fixture("version_111.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_version(http, 111)

        assert isinstance(result, Ok)
        version = result.value
        assert version.id == 111
        assert version.abbreviation == "NIV"

    @respx.mock
    def test_get_version_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/999").respond(
            status_code=404, json={"error": "not_found"}
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_version(http, 999)

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)
        assert result.error.resource == "version"

    @respx.mock
    def test_get_books(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books").respond(
            json=load_fixture("books.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_books(http, 111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    def test_get_book(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN").respond(
            json=load_fixture("book_jhn.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_book(http, 111, "JHN")

        assert isinstance(result, Ok)
        book = result.value
        assert book.id == "JHN"
        assert book.chapters is not None
        assert len(book.chapters) == 3

    @respx.mock
    def test_get_chapter(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN/chapters/3").respond(
            json=load_fixture("chapter_jhn3.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_chapter(http, 111, "JHN", 3)

        assert isinstance(result, Ok)
        chapter = result.value
        assert chapter.id == 3
        assert chapter.verses is not None
        assert len(chapter.verses) == 2

    @respx.mock
    def test_get_passage(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/passages/JHN.3.16").respond(
            json=load_fixture("passage_jhn316.json")
        )
        http = SyncHTTPAdapter("test-key", "https://api.youversion.com", 30.0)
        mixin = BibleAPIMixin()
        result = mixin._get_passage(http, 111, "JHN.3.16")

        assert isinstance(result, Ok)
        passage = result.value
        assert passage.id == "JHN.3.16"
        assert "God so loved" in passage.content
```

**Step 3: Run test to verify it fails**

Run: `uv run pytest tests/unit/bibles/test_api.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 4: Implement Bible API mixin**

Create `src/youversion/bibles/api.py`:

```python
"""Bible API implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core.domain_errors import NotFoundError, ValidationError
from youversion.core.result import Err, Ok, Result

if TYPE_CHECKING:
    from youversion.core.http import AsyncHTTPAdapter, SyncHTTPAdapter


class BibleAPIMixin:
    """Mixin providing Bible API methods."""

    def _get_versions(
        self,
        http: SyncHTTPAdapter,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    def _get_version(
        self, http: SyncHTTPAdapter, bible_id: int
    ) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    def _get_books(
        self, http: SyncHTTPAdapter, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = http.get(f"/v1/bibles/{version_id}/books")

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

    def _get_book(
        self, http: SyncHTTPAdapter, version_id: int, book: str
    ) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    def _get_chapters(
        self, http: SyncHTTPAdapter, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

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

    def _get_chapter(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    def _get_verses(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses")

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

    def _get_verse(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = http.get(
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

    def _get_passage(
        self,
        http: SyncHTTPAdapter,
        version_id: int,
        usfm: str,
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
        response = http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

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

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/unit/bibles/test_api.py -v`
Expected: All tests PASS

**Step 6: Run type checkers**

Run: `uv run mypy src/youversion/bibles/api.py && uv run pyright src/youversion/bibles/api.py`
Expected: No errors

**Step 7: Commit**

```bash
git add src/youversion/bibles/api.py tests/unit/bibles/test_api.py tests/fixtures/
git commit -m "feat(bibles): add Bible API mixin with all methods"
```

---

## Task 8: Sync Client

**Files:**
- Create: `src/youversion/core/client.py`
- Create: `tests/unit/core/test_client.py`

**Step 1: Write the failing test for sync client**

Create `tests/unit/core/test_client.py`:

```python
"""Tests for YouVersionClient."""

import json
from pathlib import Path

import respx

from youversion.core.client import YouVersionClient
from youversion.core.result import Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestYouVersionClient:
    def test_creates_with_api_key(self) -> None:
        client = YouVersionClient(api_key="test-key")
        assert client._http._api_key == "test-key"

    def test_custom_base_url(self) -> None:
        client = YouVersionClient(api_key="test-key", base_url="https://custom.api.com")
        assert client._http._base_url == "https://custom.api.com"

    @respx.mock
    def test_get_versions(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            json=load_fixture("versions.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_versions("en")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    def test_get_version(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json=load_fixture("version_111.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_version(111)

        assert isinstance(result, Ok)
        assert result.value.id == 111

    @respx.mock
    def test_get_books(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books").respond(
            json=load_fixture("books.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_books(111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    def test_get_book(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN").respond(
            json=load_fixture("book_jhn.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_book(111, "JHN")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN"

    @respx.mock
    def test_get_chapter(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN/chapters/3").respond(
            json=load_fixture("chapter_jhn3.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_chapter(111, "JHN", 3)

        assert isinstance(result, Ok)
        assert result.value.id == 3

    @respx.mock
    def test_get_passage(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/passages/JHN.3.16").respond(
            json=load_fixture("passage_jhn316.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_passage(111, "JHN.3.16")

        assert isinstance(result, Ok)
        assert "God so loved" in result.value.content

    def test_context_manager(self) -> None:
        with YouVersionClient(api_key="test-key") as client:
            assert client._http is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/core/test_client.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement sync client**

Create `src/youversion/core/client.py`:

```python
"""YouVersion SDK clients."""

from __future__ import annotations

from typing import Literal

from youversion.bibles.api import BibleAPIMixin
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
from youversion.core.result import Result

DEFAULT_BASE_URL = "https://api.youversion.com"
DEFAULT_TIMEOUT = 30.0


class YouVersionClient(BibleAPIMixin):
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
        self, language_ranges: str, license_id: str | int | None = None
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        return self._get_versions(self._http, language_ranges, license_id)

    def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        return self._get_version(self._http, bible_id)

    # Book methods
    def get_books(self, version_id: int) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        return self._get_books(self._http, version_id)

    def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        return self._get_book(self._http, version_id, book)

    # Chapter methods
    def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        return self._get_chapters(self._http, version_id, book)

    def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        return self._get_chapter(self._http, version_id, book, chapter)

    # Verse methods
    def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        return self._get_verses(self._http, version_id, book, chapter)

    def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        return self._get_verse(self._http, version_id, book, chapter, verse)

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
        return self._get_passage(
            self._http, version_id, usfm, format, include_headings, include_notes
        )


class AsyncYouVersionClient(BibleAPIMixin):
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

    # Async versions will be implemented in a follow-up task
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/core/test_client.py -v`
Expected: All tests PASS

**Step 5: Run type checkers**

Run: `uv run mypy src/youversion/core/client.py && uv run pyright src/youversion/core/client.py`
Expected: No errors

**Step 6: Commit**

```bash
git add src/youversion/core/client.py tests/unit/core/test_client.py
git commit -m "feat(core): add YouVersionClient with all Bible methods"
```

---

## Task 9: Public API Exports

**Files:**
- Modify: `src/youversion/__init__.py`
- Modify: `src/youversion/core/__init__.py`
- Modify: `src/youversion/bibles/__init__.py`
- Create: `tests/unit/test_public_api.py`

**Step 1: Write the failing test for public API**

Create `tests/unit/test_public_api.py`:

```python
"""Tests for public API exports."""


def test_import_clients() -> None:
    from youversion import AsyncYouVersionClient, YouVersionClient

    assert YouVersionClient is not None
    assert AsyncYouVersionClient is not None


def test_import_result_types() -> None:
    from youversion import Err, Ok, Result, is_err, is_ok

    assert Ok is not None
    assert Err is not None
    assert is_ok is not None
    assert is_err is not None


def test_import_models() -> None:
    from youversion import (
        BibleBook,
        BibleChapter,
        BiblePassage,
        BibleVerse,
        BibleVersion,
        PaginatedResponse,
    )

    assert BibleVersion is not None
    assert BibleBook is not None
    assert BibleChapter is not None
    assert BibleVerse is not None
    assert BiblePassage is not None
    assert PaginatedResponse is not None


def test_import_errors() -> None:
    from youversion import (
        AuthenticationError,
        NetworkError,
        NotFoundError,
        RateLimitError,
        ServerError,
        ValidationError,
        YouVersionError,
    )

    assert YouVersionError is not None
    assert NetworkError is not None
    assert AuthenticationError is not None
    assert RateLimitError is not None
    assert ServerError is not None
    assert NotFoundError is not None
    assert ValidationError is not None


def test_version_exposed() -> None:
    from youversion import __version__

    assert __version__ == "0.1.0"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_public_api.py -v`
Expected: FAIL with ImportError

**Step 3: Update module exports**

Update `src/youversion/core/__init__.py`:

```python
"""Core module exports."""

from youversion.core.client import AsyncYouVersionClient, YouVersionClient
from youversion.core.domain_errors import DomainError, NotFoundError, ValidationError
from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
    YouVersionError,
)
from youversion.core.result import Err, Ok, Result, is_err, is_ok

__all__ = [
    # Clients
    "YouVersionClient",
    "AsyncYouVersionClient",
    # Result types
    "Ok",
    "Err",
    "Result",
    "is_ok",
    "is_err",
    # Exceptions
    "YouVersionError",
    "NetworkError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    # Domain errors
    "NotFoundError",
    "ValidationError",
    "DomainError",
]
```

Update `src/youversion/bibles/__init__.py`:

```python
"""Bibles module exports."""

from youversion.bibles.models import (
    BibleBook,
    BibleBookIntro,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)

__all__ = [
    "BibleVersion",
    "BibleBook",
    "BibleBookIntro",
    "BibleChapter",
    "BibleVerse",
    "BiblePassage",
    "PaginatedResponse",
]
```

Update `src/youversion/__init__.py`:

```python
"""YouVersion Python SDK."""

from youversion.bibles import (
    BibleBook,
    BibleBookIntro,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core import (
    AsyncYouVersionClient,
    AuthenticationError,
    DomainError,
    Err,
    NetworkError,
    NotFoundError,
    Ok,
    RateLimitError,
    Result,
    ServerError,
    ValidationError,
    YouVersionClient,
    YouVersionError,
    is_err,
    is_ok,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Clients
    "YouVersionClient",
    "AsyncYouVersionClient",
    # Result types
    "Ok",
    "Err",
    "Result",
    "is_ok",
    "is_err",
    # Models
    "BibleVersion",
    "BibleBook",
    "BibleBookIntro",
    "BibleChapter",
    "BibleVerse",
    "BiblePassage",
    "PaginatedResponse",
    # Exceptions
    "YouVersionError",
    "NetworkError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    # Domain errors
    "NotFoundError",
    "ValidationError",
    "DomainError",
]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_public_api.py -v`
Expected: All tests PASS

**Step 5: Run all tests and type checkers**

Run: `uv run pytest tests/ -v && uv run mypy src/ && uv run pyright src/`
Expected: All pass

**Step 6: Commit**

```bash
git add src/youversion/
git commit -m "feat: expose public API with all exports"
```

---

## Task 10: Full Test Suite & Verification

**Files:**
- Create: `tests/conftest.py`
- Verify all tests pass

**Step 1: Create conftest.py**

Create `tests/conftest.py`:

```python
"""Shared test configuration and fixtures."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "live: tests that hit real API (skip by default)")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip live tests unless explicitly requested."""
    if config.getoption("-m") != "live":
        skip_live = pytest.mark.skip(reason="Live tests skipped (use -m live to run)")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)
```

**Step 2: Run full test suite**

Run: `uv run pytest tests/ -v --cov=youversion --cov-report=term-missing`
Expected: All tests PASS with coverage report

**Step 3: Run linting**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: No errors

**Step 4: Run type checkers**

Run: `uv run mypy src/ && uv run pyright src/`
Expected: No errors

**Step 5: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add conftest with live test marker configuration"
```

---

## Summary

Phase 1 complete. The SDK now has:

- **Result type** (`Ok`/`Err`) for explicit error handling
- **Exception hierarchy** for unexpected errors (network, auth, rate limit, server)
- **Domain error models** for expected errors (not found, validation)
- **Bible models** (Version, Book, Chapter, Verse, Passage)
- **HTTP adapter** abstraction for sync/async
- **Bible API mixin** with all core methods
- **YouVersionClient** (sync) with full Bible API
- **Public API exports** from top-level package
- **Test fixtures** for mocked API responses
- **CI pipeline** with lint, typecheck, test jobs

**Next steps (Phase 2):**
- Add async implementations
- Add `get_index`, VOTD, and Language methods
