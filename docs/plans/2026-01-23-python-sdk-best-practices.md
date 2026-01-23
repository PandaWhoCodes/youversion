# YouVersion Python SDK - Best Practices Design

## Overview

This document defines the architecture and best practices for building a strongly-typed Python SDK wrapping the YouVersion REST API. The design prioritizes type safety (Scala-inspired), explicit error handling, and developer experience.

---

## 1. Type System

### Philosophy

Treat types as documentation and contracts. Every API request and response has a corresponding Pydantic model.

### Tools

- **Pydantic v2** for all models
- **Generics** for paginated responses, Result types
- **Literal types** for enums/discriminated unions
- **`typing.Self`** for fluent builders
- **`@overload`** for methods with different return types

### Examples

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Literal

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    next_cursor: str | None
    has_more: bool

class Verse(BaseModel):
    reference: str
    content: str
    version: Literal["NIV", "ESV", "KJV", ...]
```

### Result Type

For domain errors, implement a simple `Result[T, E]` using pattern matching:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]
```

---

## 2. Client Architecture (Sync/Async)

### Unified Interface Pattern

Define a shared protocol for all API operations:

```python
from typing import Protocol

class YouVersionAPI(Protocol):
    def get_verse(self, reference: str) -> Result[Verse, NotFoundError]: ...
    def search_verses(self, query: str) -> Result[PaginatedResponse[Verse], ValidationError]: ...
    def get_plan(self, plan_id: str) -> Result[Plan, NotFoundError]: ...
```

### Two Client Classes

```python
class YouVersionClient:
    """Synchronous client using httpx.Client"""
    def __init__(self, api_key: str, *, base_url: str = DEFAULT_URL, timeout: float = 30.0): ...

class AsyncYouVersionClient:
    """Asynchronous client using httpx.AsyncClient"""
    def __init__(self, api_key: str, *, base_url: str = DEFAULT_URL, timeout: float = 30.0): ...
```

### Shared Implementation via Mixins

Domain logic lives in mixins. HTTP calls are abstracted:

```python
class VersesMixin:
    def _get_verse_impl(self, http: HTTPAdapter, reference: str) -> Result[Verse, NotFoundError]:
        response = http.get(f"/verses/{reference}")
        return self._handle_response(response, Verse)

class YouVersionClient(VersesMixin):
    def get_verse(self, reference: str) -> Result[Verse, NotFoundError]:
        return self._get_verse_impl(self._sync_http, reference)
```

The `HTTPAdapter` is a thin abstraction over sync/async httpx.

---

## 3. API Key Management

### Constructor Injection Only

Simple, explicit, testable:

```python
client = YouVersionClient(api_key="your-api-key")
async_client = AsyncYouVersionClient(api_key="your-api-key")
```

No magic environment variable resolution or config file discovery.

---

## 4. Error Handling

### Exception Hierarchy (Unexpected Errors)

Network failures, authentication issues, and server errors raise exceptions:

```python
class YouVersionError(Exception):
    """Base for all SDK exceptions"""

class NetworkError(YouVersionError):
    """Connection failed, timeout, DNS issues"""

class AuthenticationError(YouVersionError):
    """Invalid or expired API key"""

class RateLimitError(YouVersionError):
    """429 - includes retry_after hint"""
    retry_after: float | None

class ServerError(YouVersionError):
    """5xx responses from API"""
    status_code: int
```

### Result Types (Expected Domain Errors)

Domain errors are returned, not raised:

```python
class NotFoundError(BaseModel):
    resource: str
    identifier: str
    message: str

class ValidationError(BaseModel):
    field: str
    reason: str

DomainError = NotFoundError | ValidationError
```

### Usage Pattern

```python
# Exceptions: wrap in try/except at application boundary
try:
    result = client.get_verse("JHN.3.16")
except NetworkError:
    show_offline_message()
    return

# Results: must handle inline
match result:
    case Ok(verse):
        print(verse.content)
    case Err(NotFoundError() as e):
        print(f"Verse {e.identifier} not found")
```

---

## 5. Testing Strategy

### Three-Layer Pyramid

```
        /\
       /  \     Live tests (manual, optional)
      /----\
     /      \   Integration tests (recorded fixtures)
    /--------\
   /          \ Unit tests (mocks, fast)
  --------------
```

### Layer 1: Unit Tests

Test business logic in isolation with mocked HTTP:

```python
def test_verse_parsing():
    raw = {"reference": "JHN.3.16", "content": "For God so loved..."}
    verse = Verse.model_validate(raw)
    assert verse.reference == "JHN.3.16"

def test_handles_not_found():
    http = MockHTTPAdapter(status=404, body={"error": "not_found"})
    client = YouVersionClient(api_key="test", _http=http)
    result = client.get_verse("INVALID")
    assert isinstance(result, Err)
```

### Layer 2: Integration Tests (Recorded Fixtures)

Use `respx` to record/replay real API responses:

```python
@respx.mock
def test_get_verse_integration(respx_mock):
    respx_mock.get("/verses/JHN.3.16").respond(json=RECORDED_RESPONSE)
    client = YouVersionClient(api_key="test")
    result = client.get_verse("JHN.3.16")
    assert result == Ok(Verse(...))
```

Fixtures live in `tests/fixtures/` as JSON files.

### Layer 3: Live Tests

Marked with `@pytest.mark.live`, skipped by default:

```bash
YOUVERSION_API_KEY=xxx pytest -m live
```

---

## 6. Versioning & Deprecation

### Semantic Versioning

- **MAJOR (1.x → 2.0)**: Breaking changes after deprecation window
- **MINOR (1.1 → 1.2)**: New features, deprecation announcements
- **PATCH (1.1.1 → 1.1.2)**: Bug fixes only

### Deprecation Window Policy

1. **MINOR release**: Add deprecation warning, introduce replacement
2. **Next MAJOR release**: Remove deprecated code

Minimum window: 3 months or 2 minor releases, whichever is longer.

### Deprecation Tooling

```python
import warnings
from typing import deprecated  # Python 3.13+ or typing_extensions

@deprecated("Use get_verse() instead. Will be removed in v2.0")
def fetch_verse(self, ref: str) -> Verse:
    warnings.warn(
        "fetch_verse is deprecated, use get_verse()",
        DeprecationWarning,
        stacklevel=2
    )
    return self.get_verse(ref)
```

### Changelog

Maintain `CHANGELOG.md` with sections: Added, Changed, Deprecated, Removed, Fixed.

### Version Exposure

```python
# youversion/__init__.py
__version__ = "1.0.0"
```

---

## 7. Project Structure

```
youversion/
├── src/
│   └── youversion/
│       ├── __init__.py           # Public API exports, __version__
│       ├── py.typed              # PEP 561 marker
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py         # YouVersionClient, AsyncYouVersionClient
│       │   ├── http.py           # HTTPAdapter abstraction
│       │   ├── result.py         # Ok, Err, Result type
│       │   └── errors.py         # Exception hierarchy
│       │
│       ├── verses/
│       │   ├── __init__.py
│       │   ├── models.py         # Verse, VerseSearch, etc.
│       │   └── api.py            # VerseMixin implementation
│       │
│       └── plans/
│           ├── __init__.py
│           ├── models.py         # Plan, PlanDay, etc.
│           └── api.py            # PlanMixin implementation
│
├── tests/
│   ├── conftest.py               # Shared fixtures, markers
│   ├── fixtures/                 # Recorded API responses
│   ├── unit/
│   └── integration/
│
├── .github/
│   └── workflows/
│       └── ci.yml                # CI pipeline
│
├── pyproject.toml                # Single source of truth
├── CHANGELOG.md
└── README.md
```

---

## 8. Dependencies & Tooling

### Runtime Dependencies

```toml
[project]
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "pytest-cov>=4.0",

    # Type checking
    "mypy>=1.8",
    "pyright>=1.1.350",

    # Linting & formatting
    "ruff>=0.2",

    # Docs
    "mkdocs-material>=9.0",
]
```

### Tool Configuration

```toml
[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.pyright]
typeCheckingMode = "strict"

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "UP", "B", "SIM", "TCH"]

[tool.pytest.ini_options]
markers = ["live: tests that hit real API"]
asyncio_mode = "auto"
```

---

## 9. GitHub Actions CI

### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

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
```

### CI Requirements

All checks must pass before merging to main:
1. `ruff check .` - Linting
2. `ruff format --check .` - Formatting
3. `mypy src/` - Type checking
4. `pyright src/` - Second type checker
5. `pytest --cov=youversion` - Tests with coverage

---

## 10. Public API Design

### Clean Exports

Users import everything from the top level:

```python
from youversion import (
    # Clients
    YouVersionClient,
    AsyncYouVersionClient,

    # Models
    Verse,
    Plan,
    PaginatedResponse,

    # Result types
    Ok,
    Err,
    Result,

    # Errors (exceptions)
    YouVersionError,
    NetworkError,
    AuthenticationError,
    RateLimitError,

    # Domain errors (for Result matching)
    NotFoundError,
    ValidationError,

    # Version
    __version__,
)
```

### `__all__` for Explicit API

```python
__all__ = [
    "YouVersionClient",
    "AsyncYouVersionClient",
    # ... all public exports
]
```

### Usage Example

```python
from youversion import YouVersionClient, Ok, Err

client = YouVersionClient(api_key="your-api-key")

match client.get_verse("JHN.3.16"):
    case Ok(verse):
        print(verse.content)
    case Err(error):
        print(f"Error: {error.message}")
```

---

## Summary of Decisions

| Aspect | Decision |
|--------|----------|
| Type Safety | Practical strictness - Pydantic models, generics, plain IDs |
| Sync/Async | Httpx-style unified - separate clients, shared interface |
| API Key | Constructor injection only |
| Error Handling | Hybrid - exceptions for unexpected, Result for domain |
| Testing | Layered pyramid - unit, integration (recorded), live |
| Versioning | SemVer with deprecation windows |
| Structure | Domain-organized |
