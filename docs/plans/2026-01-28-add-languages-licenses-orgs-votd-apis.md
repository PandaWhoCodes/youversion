# Add Languages, Licenses, Organizations, and VOTD APIs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add four new API modules (Languages, Licenses, Organizations, VOTD) following the validated API specs.

**Architecture:** Each API gets its own module with Pydantic models. Client methods are added inline to `YouVersionClient` and `AsyncYouVersionClient` following the established pattern. Uses Result types for error handling.

**Tech Stack:** Python 3.11+, Pydantic v2, httpx, pytest with respx mocking

---

### Task 1: Languages API - Models

**Files:**
- Create: `src/youversion/languages/__init__.py`
- Create: `src/youversion/languages/models.py`
- Modify: `src/youversion/__init__.py`

**Step 1: Create the Language model**

Create `src/youversion/languages/models.py`:
```python
"""Language models."""

from pydantic import BaseModel


class Language(BaseModel):
    """A language supported by YouVersion."""

    id: str  # BCP 47 tag
    language: str  # ISO 639
    script: str | None = None
    script_name: str | None = None
    aliases: list[str] = []
    display_names: dict[str, str] = {}
    scripts: list[str] = []
    variants: list[str] = []
    countries: list[str] = []
    text_direction: str  # "ltr" or "rtl"
    writing_population: int = 0
    speaking_population: int = 0
    default_bible_id: int | None = None
```

**Step 2: Create the module exports**

Create `src/youversion/languages/__init__.py`:
```python
"""Languages module exports."""

from youversion.languages.models import Language

__all__ = ["Language"]
```

**Step 3: Add to main package exports**

Add to `src/youversion/__init__.py` imports:
```python
from youversion.languages.models import Language
```

And add `"Language"` to `__all__`.

**Step 4: Run mypy to verify**

Run: `source .venv/bin/activate && mypy src/`
Expected: Success, no issues

**Step 5: Commit**

```bash
git add src/youversion/languages/ src/youversion/__init__.py
git commit -m "feat: add Language model"
```

---

### Task 2: Languages API - Client Methods

**Files:**
- Modify: `src/youversion/core/client.py`
- Create: `tests/unit/languages/__init__.py`
- Create: `tests/unit/languages/test_api.py`
- Create: `tests/fixtures/languages.json`
- Create: `tests/fixtures/language_en.json`

**Step 1: Create test fixtures**

Create `tests/fixtures/languages.json`:
```json
{
  "data": [
    {
      "id": "en",
      "language": "eng",
      "script": "Latn",
      "script_name": "Latin",
      "aliases": ["english"],
      "display_names": {"en": "English", "es": "Inglés"},
      "scripts": ["Latn"],
      "variants": [],
      "countries": ["US", "GB"],
      "text_direction": "ltr",
      "writing_population": 400000000,
      "speaking_population": 1500000000,
      "default_bible_id": 111
    }
  ],
  "next_page_token": null
}
```

Create `tests/fixtures/language_en.json`:
```json
{
  "id": "en",
  "language": "eng",
  "script": "Latn",
  "script_name": "Latin",
  "aliases": ["english"],
  "display_names": {"en": "English", "es": "Inglés"},
  "scripts": ["Latn"],
  "variants": [],
  "countries": ["US", "GB"],
  "text_direction": "ltr",
  "writing_population": 400000000,
  "speaking_population": 1500000000,
  "default_bible_id": 111
}
```

**Step 2: Write the failing tests**

Create `tests/unit/languages/__init__.py` (empty file).

Create `tests/unit/languages/test_api.py`:
```python
"""Tests for Languages API."""

import json
from pathlib import Path

import pytest
import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestLanguagesAPI:
    @respx.mock
    def test_get_languages(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages").respond(
            json=load_fixture("languages.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_languages()

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].id == "en"
        assert result.value.data[0].text_direction == "ltr"

    @respx.mock
    def test_get_languages_with_country_filter(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/languages").respond(
            json=load_fixture("languages.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            client.get_languages(country="US")

        assert "country=US" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_language(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages/en").respond(
            json=load_fixture("language_en.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_language("en")

        assert isinstance(result, Ok)
        assert result.value.id == "en"
        assert result.value.language == "eng"

    @respx.mock
    def test_get_language_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages/xyz").respond(status_code=404)
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_language("xyz")

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)
```

**Step 3: Run tests to verify they fail**

Run: `source .venv/bin/activate && pytest tests/unit/languages/test_api.py -v`
Expected: FAIL with AttributeError (get_languages not defined)

**Step 4: Implement client methods**

Add to `src/youversion/core/client.py` imports:
```python
from youversion.languages.models import Language
```

Add to `YouVersionClient` class (after passage methods):
```python
    # Language methods
    def get_languages(
        self,
        *,
        country: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> Result[PaginatedResponse[Language], None]:
        """Get available languages."""
        params: dict[str, Any] = {}
        if country is not None:
            params["country"] = country
        if page_size is not None:
            params["page_size"] = page_size
        if page_token is not None:
            params["page_token"] = page_token

        response = self._http.get("/v1/languages", params=params if params else None)
        data = response.json()
        return Ok(PaginatedResponse[Language].model_validate(data))

    def get_language(self, language_id: str) -> Result[Language, NotFoundError]:
        """Get a specific language by BCP 47 tag."""
        response = self._http.get(f"/v1/languages/{language_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="language",
                    identifier=language_id,
                    message=f"Language {language_id} not found",
                )
            )

        return Ok(Language.model_validate(response.json()))
```

Add same methods to `AsyncYouVersionClient` (with async/await):
```python
    # Language methods
    async def get_languages(
        self,
        *,
        country: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> Result[PaginatedResponse[Language], None]:
        """Get available languages."""
        params: dict[str, Any] = {}
        if country is not None:
            params["country"] = country
        if page_size is not None:
            params["page_size"] = page_size
        if page_token is not None:
            params["page_token"] = page_token

        response = await self._http.get("/v1/languages", params=params if params else None)
        data = response.json()
        return Ok(PaginatedResponse[Language].model_validate(data))

    async def get_language(self, language_id: str) -> Result[Language, NotFoundError]:
        """Get a specific language by BCP 47 tag."""
        response = await self._http.get(f"/v1/languages/{language_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="language",
                    identifier=language_id,
                    message=f"Language {language_id} not found",
                )
            )

        return Ok(Language.model_validate(response.json()))
```

**Step 5: Run tests to verify they pass**

Run: `source .venv/bin/activate && pytest tests/unit/languages/test_api.py -v`
Expected: PASS (4 tests)

**Step 6: Run mypy**

Run: `source .venv/bin/activate && mypy src/`
Expected: Success

**Step 7: Commit**

```bash
git add src/youversion/core/client.py tests/unit/languages/ tests/fixtures/languages.json tests/fixtures/language_en.json
git commit -m "feat: add Languages API methods"
```

---

### Task 3: Licenses API - Models and Client Methods

**Files:**
- Create: `src/youversion/licenses/__init__.py`
- Create: `src/youversion/licenses/models.py`
- Modify: `src/youversion/__init__.py`
- Modify: `src/youversion/core/client.py`
- Create: `tests/unit/licenses/__init__.py`
- Create: `tests/unit/licenses/test_api.py`
- Create: `tests/fixtures/licenses.json`

**Step 1: Create the License model**

Create `src/youversion/licenses/models.py`:
```python
"""License models."""

from datetime import datetime

from pydantic import BaseModel


class License(BaseModel):
    """A Bible license."""

    id: int
    name: str
    version: int
    organization_id: str  # UUID
    html: str
    bible_ids: list[int] = []
    uri: str | None = None
    agreed_dt: datetime | None = None
    yvp_user_id: str
```

**Step 2: Create module exports**

Create `src/youversion/licenses/__init__.py`:
```python
"""Licenses module exports."""

from youversion.licenses.models import License

__all__ = ["License"]
```

**Step 3: Add to main package exports**

Add to `src/youversion/__init__.py`:
```python
from youversion.licenses.models import License
```
And add `"License"` to `__all__`.

**Step 4: Create test fixture**

Create `tests/fixtures/licenses.json`:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Standard License",
      "version": 1,
      "organization_id": "550e8400-e29b-41d4-a716-446655440000",
      "html": "<p>License terms...</p>",
      "bible_ids": [111, 112],
      "uri": "https://example.com/license",
      "agreed_dt": "2024-01-15T10:30:00Z",
      "yvp_user_id": "user-uuid-123"
    }
  ],
  "next_page_token": null
}
```

**Step 5: Write the failing tests**

Create `tests/unit/licenses/__init__.py` (empty).

Create `tests/unit/licenses/test_api.py`:
```python
"""Tests for Licenses API."""

import json
from pathlib import Path

import pytest
import respx

from youversion import YouVersionClient
from youversion.core.result import Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestLicensesAPI:
    @respx.mock
    def test_get_licenses(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/licenses").respond(
            json=load_fixture("licenses.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_licenses(bible_id=111, developer_id="dev-uuid")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].name == "Standard License"
        assert "bible_id=111" in str(route.calls[0].request.url)
        assert "developer_id=dev-uuid" in str(route.calls[0].request.url)
```

**Step 6: Run tests to verify they fail**

Run: `source .venv/bin/activate && pytest tests/unit/licenses/test_api.py -v`
Expected: FAIL

**Step 7: Implement client methods**

Add to `src/youversion/core/client.py` imports:
```python
from youversion.licenses.models import License
```

Add to `YouVersionClient`:
```python
    # License methods
    def get_licenses(
        self,
        bible_id: int,
        developer_id: str,
        *,
        all_available: bool = False,
    ) -> Result[PaginatedResponse[License], None]:
        """Get licenses for a Bible."""
        params: dict[str, Any] = {
            "bible_id": bible_id,
            "developer_id": developer_id,
        }
        if all_available:
            params["all_available"] = "true"

        response = self._http.get("/v1/licenses", params=params)
        data = response.json()
        return Ok(PaginatedResponse[License].model_validate(data))
```

Add to `AsyncYouVersionClient`:
```python
    # License methods
    async def get_licenses(
        self,
        bible_id: int,
        developer_id: str,
        *,
        all_available: bool = False,
    ) -> Result[PaginatedResponse[License], None]:
        """Get licenses for a Bible."""
        params: dict[str, Any] = {
            "bible_id": bible_id,
            "developer_id": developer_id,
        }
        if all_available:
            params["all_available"] = "true"

        response = await self._http.get("/v1/licenses", params=params)
        data = response.json()
        return Ok(PaginatedResponse[License].model_validate(data))
```

**Step 8: Run tests**

Run: `source .venv/bin/activate && pytest tests/unit/licenses/test_api.py -v`
Expected: PASS

**Step 9: Commit**

```bash
git add src/youversion/licenses/ src/youversion/__init__.py src/youversion/core/client.py tests/unit/licenses/ tests/fixtures/licenses.json
git commit -m "feat: add Licenses API"
```

---

### Task 4: Organizations API - Models

**Files:**
- Create: `src/youversion/organizations/__init__.py`
- Create: `src/youversion/organizations/models.py`
- Modify: `src/youversion/__init__.py`

**Step 1: Create Organization models**

Create `src/youversion/organizations/models.py`:
```python
"""Organization models."""

from pydantic import BaseModel


class OrganizationAddress(BaseModel):
    """Organization physical address."""

    formatted_address: str
    place_id: str
    latitude: float
    longitude: float
    administrative_area_level_1: str
    locality: str
    country: str


class Organization(BaseModel):
    """A Bible publisher/organization."""

    id: str  # UUID
    parent_organization_id: str | None = None
    name: str
    description: str
    email: str | None = None
    phone: str | None = None
    primary_language: str
    website_url: str
    address: OrganizationAddress
```

**Step 2: Create module exports**

Create `src/youversion/organizations/__init__.py`:
```python
"""Organizations module exports."""

from youversion.organizations.models import Organization, OrganizationAddress

__all__ = ["Organization", "OrganizationAddress"]
```

**Step 3: Add to main package**

Add to `src/youversion/__init__.py`:
```python
from youversion.organizations.models import Organization, OrganizationAddress
```
Add `"Organization"`, `"OrganizationAddress"` to `__all__`.

**Step 4: Run mypy**

Run: `source .venv/bin/activate && mypy src/`
Expected: Success

**Step 5: Commit**

```bash
git add src/youversion/organizations/ src/youversion/__init__.py
git commit -m "feat: add Organization models"
```

---

### Task 5: Organizations API - Client Methods

**Files:**
- Modify: `src/youversion/core/client.py`
- Create: `tests/unit/organizations/__init__.py`
- Create: `tests/unit/organizations/test_api.py`
- Create: `tests/fixtures/organizations.json`
- Create: `tests/fixtures/organization.json`

**Step 1: Create test fixtures**

Create `tests/fixtures/organizations.json`:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "parent_organization_id": null,
      "name": "Bible Society",
      "description": "A Bible publisher",
      "email": "info@biblesociety.org",
      "phone": "+1-555-1234",
      "primary_language": "en",
      "website_url": "https://biblesociety.org",
      "address": {
        "formatted_address": "123 Main St, City, ST 12345",
        "place_id": "ChIJ...",
        "latitude": 40.7128,
        "longitude": -74.006,
        "administrative_area_level_1": "New York",
        "locality": "New York City",
        "country": "US"
      }
    }
  ],
  "next_page_token": null
}
```

Create `tests/fixtures/organization.json`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "parent_organization_id": null,
  "name": "Bible Society",
  "description": "A Bible publisher",
  "email": "info@biblesociety.org",
  "phone": "+1-555-1234",
  "primary_language": "en",
  "website_url": "https://biblesociety.org",
  "address": {
    "formatted_address": "123 Main St, City, ST 12345",
    "place_id": "ChIJ...",
    "latitude": 40.7128,
    "longitude": -74.006,
    "administrative_area_level_1": "New York",
    "locality": "New York City",
    "country": "US"
  }
}
```

**Step 2: Write failing tests**

Create `tests/unit/organizations/__init__.py` (empty).

Create `tests/unit/organizations/test_api.py`:
```python
"""Tests for Organizations API."""

import json
from pathlib import Path

import pytest
import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestOrganizationsAPI:
    @respx.mock
    def test_get_organizations(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/organizations").respond(
            json=load_fixture("organizations.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organizations(bible_id=111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].name == "Bible Society"
        assert "bible_id=111" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_organizations_with_accept_language(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/organizations").respond(
            json=load_fixture("organizations.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            client.get_organizations(bible_id=111, accept_language="es")

        assert route.calls[0].request.headers["Accept-Language"] == "es"

    @respx.mock
    def test_get_organization(self, respx_mock: respx.MockRouter) -> None:
        org_id = "550e8400-e29b-41d4-a716-446655440000"
        respx_mock.get(f"https://api.youversion.com/v1/organizations/{org_id}").respond(
            json=load_fixture("organization.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization(org_id)

        assert isinstance(result, Ok)
        assert result.value.id == org_id
        assert result.value.address.country == "US"

    @respx.mock
    def test_get_organization_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/organizations/bad-uuid").respond(status_code=404)
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization("bad-uuid")

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)

    @respx.mock
    def test_get_organization_bibles(self, respx_mock: respx.MockRouter) -> None:
        org_id = "550e8400-e29b-41d4-a716-446655440000"
        respx_mock.get(f"https://api.youversion.com/v1/organizations/{org_id}/bibles").respond(
            json={"data": [{"id": 111, "abbreviation": "NIV", "title": "NIV Bible", "local_title": "NIV"}], "next_page_token": None}
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization_bibles(org_id)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
```

**Step 3: Run tests to verify they fail**

Run: `source .venv/bin/activate && pytest tests/unit/organizations/test_api.py -v`
Expected: FAIL

**Step 4: Add headers support to HTTP adapter**

The Organizations API requires `Accept-Language` header. Add header parameter to HTTP adapters.

Modify `src/youversion/core/http.py` - update `SyncHTTPAdapter.get()`:
```python
    def get(
        self, path: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """Make a GET request."""
        try:
            response = self._client.get(path, params=params, headers=headers)
        # ... rest unchanged
```

And `AsyncHTTPAdapter.get()`:
```python
    async def get(
        self, path: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """Make a GET request."""
        try:
            response = await self._client.get(path, params=params, headers=headers)
        # ... rest unchanged
```

**Step 5: Implement client methods**

Add to `src/youversion/core/client.py` imports:
```python
from youversion.organizations.models import Organization
```

Add to `YouVersionClient`:
```python
    # Organization methods
    def get_organizations(
        self,
        bible_id: int,
        *,
        accept_language: str = "en",
    ) -> Result[PaginatedResponse[Organization], None]:
        """Get organizations for a Bible."""
        response = self._http.get(
            "/v1/organizations",
            params={"bible_id": bible_id},
            headers={"Accept-Language": accept_language},
        )
        data = response.json()
        return Ok(PaginatedResponse[Organization].model_validate(data))

    def get_organization(
        self,
        organization_id: str,
        *,
        accept_language: str = "en",
    ) -> Result[Organization, NotFoundError]:
        """Get a specific organization by UUID."""
        response = self._http.get(
            f"/v1/organizations/{organization_id}",
            headers={"Accept-Language": accept_language},
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="organization",
                    identifier=organization_id,
                    message=f"Organization {organization_id} not found",
                )
            )

        return Ok(Organization.model_validate(response.json()))

    def get_organization_bibles(
        self,
        organization_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], NotFoundError]:
        """Get Bibles from an organization."""
        params: dict[str, Any] = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_token is not None:
            params["page_token"] = page_token

        response = self._http.get(
            f"/v1/organizations/{organization_id}/bibles",
            params=params if params else None,
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="organization",
                    identifier=organization_id,
                    message=f"Organization {organization_id} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))
```

Add same methods to `AsyncYouVersionClient` with async/await.

**Step 6: Run tests**

Run: `source .venv/bin/activate && pytest tests/unit/organizations/test_api.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/youversion/core/http.py src/youversion/core/client.py tests/unit/organizations/ tests/fixtures/organizations.json tests/fixtures/organization.json
git commit -m "feat: add Organizations API"
```

---

### Task 6: VOTD API - Models and Client Methods

**Files:**
- Create: `src/youversion/votd/__init__.py`
- Create: `src/youversion/votd/models.py`
- Modify: `src/youversion/__init__.py`
- Modify: `src/youversion/core/client.py`
- Create: `tests/unit/votd/__init__.py`
- Create: `tests/unit/votd/test_api.py`
- Create: `tests/fixtures/votd_all.json`
- Create: `tests/fixtures/votd_day.json`

**Step 1: Create VOTD model**

Create `src/youversion/votd/models.py`:
```python
"""Verse of the Day models."""

from pydantic import BaseModel


class VerseOfTheDay(BaseModel):
    """Verse of the Day entry."""

    day: int  # 1-366
    passage_id: str
```

**Step 2: Create module exports**

Create `src/youversion/votd/__init__.py`:
```python
"""Verse of the Day module exports."""

from youversion.votd.models import VerseOfTheDay

__all__ = ["VerseOfTheDay"]
```

**Step 3: Add to main package**

Add to `src/youversion/__init__.py`:
```python
from youversion.votd.models import VerseOfTheDay
```
Add `"VerseOfTheDay"` to `__all__`.

**Step 4: Create test fixtures**

Create `tests/fixtures/votd_all.json`:
```json
{
  "data": [
    {"day": 1, "passage_id": "JHN.3.16"},
    {"day": 2, "passage_id": "PSA.23.1"}
  ],
  "next_page_token": null
}
```

Create `tests/fixtures/votd_day.json`:
```json
{
  "day": 1,
  "passage_id": "JHN.3.16"
}
```

**Step 5: Write failing tests**

Create `tests/unit/votd/__init__.py` (empty).

Create `tests/unit/votd/test_api.py`:
```python
"""Tests for VOTD API."""

import json
from pathlib import Path

import pytest
import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import ValidationError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestVOTDAPI:
    @respx.mock
    def test_get_all_votd(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days").respond(
            json=load_fixture("votd_all.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_all_votd()

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2
        assert result.value.data[0].day == 1
        assert result.value.data[0].passage_id == "JHN.3.16"

    @respx.mock
    def test_get_votd(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days/1").respond(
            json=load_fixture("votd_day.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_votd(1)

        assert isinstance(result, Ok)
        assert result.value.day == 1
        assert result.value.passage_id == "JHN.3.16"

    @respx.mock
    def test_get_votd_invalid_day(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days/999").respond(status_code=400)
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_votd(999)

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)
```

**Step 6: Run tests to verify they fail**

Run: `source .venv/bin/activate && pytest tests/unit/votd/test_api.py -v`
Expected: FAIL

**Step 7: Implement client methods**

Add to `src/youversion/core/client.py` imports:
```python
from youversion.votd.models import VerseOfTheDay
```

Add to `YouVersionClient`:
```python
    # VOTD methods
    def get_all_votd(self) -> Result[PaginatedResponse[VerseOfTheDay], None]:
        """Get all verses of the day (1-366)."""
        response = self._http.get("/v1/verse_of_the_days")
        data = response.json()
        return Ok(PaginatedResponse[VerseOfTheDay].model_validate(data))

    def get_votd(self, day: int) -> Result[VerseOfTheDay, ValidationError]:
        """Get verse of the day for a specific day (1-366)."""
        response = self._http.get(f"/v1/verse_of_the_days/{day}")

        if response.status_code == 400:
            return Err(
                ValidationError(
                    field="day",
                    reason=f"Invalid day {day}. Must be 1-366.",
                )
            )

        return Ok(VerseOfTheDay.model_validate(response.json()))
```

Add same methods to `AsyncYouVersionClient` with async/await.

**Step 8: Run tests**

Run: `source .venv/bin/activate && pytest tests/unit/votd/test_api.py -v`
Expected: PASS

**Step 9: Run full test suite**

Run: `source .venv/bin/activate && pytest -v`
Expected: All tests pass

**Step 10: Run mypy**

Run: `source .venv/bin/activate && mypy src/`
Expected: Success

**Step 11: Commit**

```bash
git add src/youversion/votd/ src/youversion/__init__.py src/youversion/core/client.py tests/unit/votd/ tests/fixtures/votd_all.json tests/fixtures/votd_day.json
git commit -m "feat: add VOTD API"
```

---

### Task 7: Final Verification and Cleanup

**Step 1: Run full test suite**

Run: `source .venv/bin/activate && pytest -v`
Expected: All tests pass

**Step 2: Run mypy**

Run: `source .venv/bin/activate && mypy src/`
Expected: Success

**Step 3: Verify exports**

Add test to `tests/unit/test_public_api.py`:
```python
def test_main_package_exports_new_models() -> None:
    from youversion import Language, License, Organization, OrganizationAddress, VerseOfTheDay

    assert Language is not None
    assert License is not None
    assert Organization is not None
    assert OrganizationAddress is not None
    assert VerseOfTheDay is not None
```

Run: `source .venv/bin/activate && pytest tests/unit/test_public_api.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add tests/unit/test_public_api.py
git commit -m "test: verify new model exports"
```

---

## Summary

| Task | Description | New Files | Tests |
|------|-------------|-----------|-------|
| 1 | Languages models | 2 | - |
| 2 | Languages client methods | 2 | 4 |
| 3 | Licenses API | 3 | 1 |
| 4 | Organizations models | 2 | - |
| 5 | Organizations client methods | 2 | 5 |
| 6 | VOTD API | 4 | 3 |
| 7 | Final verification | 1 | 1 |

Total: ~14 new tests, 4 new API modules
