# API Implementation Validation Report

Comparison of current SDK implementations against official YouVersion API documentation.

---

## Summary

| API | Status | Issues |
|-----|--------|--------|
| Highlights | **Needs Fix** | Wrong params, wrong delete endpoint, wrong model |
| Languages | **Needs Fix** | Missing params, missing method, wrong model |
| Licenses | **Needs Fix** | Missing required params, wrong model |
| Organizations | **Needs Fix** | Missing required params, wrong ID type, missing method, wrong model |
| VOTD | **Needs Fix** | Wrong endpoint URL, wrong params, wrong model |

---

## 1. Highlights API

### Official API Spec

| Endpoint | Method | Required Params |
|----------|--------|-----------------|
| `/v1/highlights` | GET | `bible_id` (int32), `passage_id` (string) |
| `/v1/highlights` | POST | Body: `bible_id`, `passage_id`, `color` (hex `^[0-9a-f]{6}$`) |
| `/v1/highlights/{passage_id_path}` | DELETE | Query: `bible_id` (int32) |

### Current Implementation Issues

#### 1.1 `get_highlights()` - Wrong parameters
```python
# Current (WRONG):
async def get_highlights(self, bible_id: int | None = None, usfm: str | None = None)

# Should be:
async def get_highlights(self, bible_id: int, passage_id: str)
```
- `bible_id` and `passage_id` are **required**, not optional
- Parameter name is `passage_id`, not `usfm`

#### 1.2 `create_highlight()` - Wrong JSON key
```python
# Current payload (WRONG):
{"bible_id": bible_id, "usfm": usfm, "color": color}

# Should be:
{"bible_id": bible_id, "passage_id": passage_id, "color": color}
```
- JSON key should be `passage_id`, not `usfm`

#### 1.3 `delete_highlights()` - Completely wrong signature
```python
# Current (WRONG):
async def delete_highlights(self, highlight_ids: list[str])
# Calls: DELETE /v1/highlights?ids[]=...

# Should be:
async def delete_highlight(self, passage_id: str, bible_id: int)
# Calls: DELETE /v1/highlights/{passage_id}?bible_id=X
```
- API uses path parameter `passage_id_path` and query param `bible_id`
- No `ids[]` parameter exists in the API

#### 1.4 Model Issues

```python
# Current Model (WRONG):
class Highlight:
    id: str
    bible_id: int
    usfm: str
    color: HighlightColor  # Object with name/hex
    user_id: str | None
    created_at: datetime | None
    updated_at: datetime | None

# Should be:
class Highlight:
    bible_id: int
    passage_id: str
    color: str  # Hex string like "44aa44"
```

---

## 2. Languages API

### Official API Spec

| Endpoint | Method | Params |
|----------|--------|--------|
| `/v1/languages` | GET | `page_size`, `fields[]`, `page_token`, `country` (all optional) |
| `/v1/languages/{language_id}` | GET | Path: `language_id` (BCP 47) |

### Current Implementation Issues

#### 2.1 `get_languages()` - Missing all parameters
```python
# Current (WRONG):
async def get_languages(self) -> Result[PaginatedResponse[Language], None]

# Should be:
async def get_languages(
    self,
    *,
    country: str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
    fields: list[str] | None = None,
) -> Result[PaginatedResponse[Language], None]
```

#### 2.2 Missing `get_language()` method
```python
# Missing:
async def get_language(self, language_id: str) -> Result[Language, NotFoundError]
```

#### 2.3 Model Issues

```python
# Current Model (WRONG):
class Language:
    tag: str
    name: str
    local_name: str | None
    script: str | None
    direction: str | None

# Should be:
class Language:
    id: str                        # BCP 47 tag
    language: str                  # ISO 639
    script: str | None             # ISO 15924
    script_name: str | None
    aliases: list[str]
    display_names: dict[str, str]
    scripts: list[str]
    variants: list[str]
    countries: list[str]
    text_direction: str            # "ltr" or "rtl"
    writing_population: int
    speaking_population: int
    default_bible_id: int | None
```

---

## 3. Licenses API

### Official API Spec

| Endpoint | Method | Required Params |
|----------|--------|-----------------|
| `/v1/licenses` | GET | `bible_id` (int32), `developer_id` (UUID) |

### Current Implementation Issues

#### 3.1 `get_licenses()` - Missing required parameters
```python
# Current (WRONG):
async def get_licenses(self) -> Result[PaginatedResponse[License], None]

# Should be:
async def get_licenses(
    self,
    bible_id: int,
    developer_id: str,
    *,
    all_available: bool = False,
) -> Result[PaginatedResponse[License], None]
```
- `bible_id` and `developer_id` are **required**

#### 3.2 Model Issues

```python
# Current Model (WRONG):
class License:
    id: int
    name: str
    description: str | None

# Should be:
class License:
    id: int
    name: str
    version: int
    organization_id: str           # UUID
    html: str
    bible_ids: list[int]
    uri: str | None
    agreed_dt: datetime | None
    yvp_user_id: str               # UUID
```

---

## 4. Organizations API

### Official API Spec

| Endpoint | Method | Params | Headers |
|----------|--------|--------|---------|
| `/v1/organizations` | GET | `bible_id` (required) | `Accept-Language` (required) |
| `/v1/organizations/{organization_id}` | GET | Path: UUID | `Accept-Language` (required) |
| `/v1/organizations/{organization_id}/bibles` | GET | `page_size`, `fields[]`, `page_token` | - |

### Current Implementation Issues

#### 4.1 `get_organizations()` - Missing required parameter
```python
# Current (WRONG):
async def get_organizations(self) -> Result[PaginatedResponse[Organization], None]

# Should be:
async def get_organizations(
    self,
    bible_id: int,
    *,
    accept_language: str = "en",
) -> Result[PaginatedResponse[Organization], None]
```

#### 4.2 `get_organization()` - Wrong ID type
```python
# Current (WRONG):
async def get_organization(self, org_id: int)

# Should be:
async def get_organization(
    self,
    organization_id: str,  # UUID, not int!
    *,
    accept_language: str = "en",
) -> Result[Organization, NotFoundError]
```

#### 4.3 Missing `get_organization_bibles()` method
```python
# Missing:
async def get_organization_bibles(
    self,
    organization_id: str,
    *,
    page_size: int | None = None,
    page_token: str | None = None,
    fields: list[str] | None = None,
) -> Result[PaginatedResponse[BibleVersion], NotFoundError]
```

#### 4.4 Model Issues

```python
# Current Model (WRONG):
class Organization:
    id: int            # Should be str (UUID)
    name: str
    website: str | None

# Should be:
class Organization:
    id: str                           # UUID
    parent_organization_id: str | None
    name: str
    description: str
    email: str | None
    phone: str | None
    primary_language: str
    website_url: str
    address: OrganizationAddress

class OrganizationAddress:
    formatted_address: str
    place_id: str
    latitude: float
    longitude: float
    administrative_area_level_1: str
    locality: str
    country: str
```

---

## 5. Verse of the Day API

### Official API Spec

| Endpoint | Method | Params |
|----------|--------|--------|
| `/v1/verse_of_the_days` | GET | None |
| `/v1/verse_of_the_days/{day}` | GET | Path: `day` (1-366) |

### Current Implementation Issues

#### 5.1 Wrong endpoint URL
```python
# Current (WRONG):
"/v1/verse-of-the-days"  # Hyphen

# Should be:
"/v1/verse_of_the_days"  # Underscore
```

#### 5.2 Wrong method signature
```python
# Current (WRONG):
async def get_verse_of_the_day(
    self,
    bible_id: int,              # API doesn't accept this!
    year: int | None = None,    # API doesn't accept this!
    month: int | None = None,   # API doesn't accept this!
    day: int | None = None,     # Wrong - should be path param
)

# Should have TWO methods:
async def get_all_votd(self) -> Result[PaginatedResponse[VerseOfTheDay], None]
    # GET /v1/verse_of_the_days

async def get_votd(self, day: int) -> Result[VerseOfTheDay, ValidationError]
    # GET /v1/verse_of_the_days/{day}
```

#### 5.3 Model Issues

```python
# Current Model (WRONG):
class VerseOfTheDay:
    date: date
    bible_id: int
    usfm: str
    reference: str
    content: str | None
    image_url: str | None

# Should be:
class VerseOfTheDay:
    day: int           # 1-366, not date!
    passage_id: str    # Not usfm, reference, content, image_url, or bible_id
```

---

## Recommended Actions

1. **Highlights API**: Fix all three methods and rewrite the model
2. **Languages API**: Add missing params, add `get_language()`, rewrite model
3. **Licenses API**: Add required params, rewrite model
4. **Organizations API**: Add required params, fix ID type to UUID, add missing method, rewrite model
5. **VOTD API**: Fix endpoint URL, split into two methods, rewrite model

---

## Priority

1. **High**: Fix endpoint URLs and required parameters (will cause API calls to fail)
2. **Medium**: Fix models to match API response schema (may cause parsing errors)
3. **Low**: Add missing methods for full API coverage
