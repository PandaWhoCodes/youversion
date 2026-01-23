# YouVersion Python SDK

The un-official Python SDK for the YouVersion API. Access Bible versions, books, chapters, verses, and passages programmatically.

[![PyPI version](https://badge.fury.io/py/youversion.svg)](https://badge.fury.io/py/youversion)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)


## Getting Started

### 1. Get Your API Key

Request access to the YouVersion API at [platform.youversion.com/](https://platform.youversion.com/).

### 2. Install the SDK

```bash
pip install youversion
```

Or with uv:

```bash
uv add youversion
```

### 3. Initialize the Client

```python
from youversion import YouVersionClient

client = YouVersionClient(api_key="your-api-key")
```

### 4. Make Your First Request

```python
from youversion import YouVersionClient, is_ok

with YouVersionClient(api_key="your-api-key") as client:
    result = client.get_passage(12, "JHN.3.16")

    if is_ok(result):
        passage = result.value
        print(f"{passage.reference}")
        print(passage.content)
```

Output:
```
John 3:16
For God so loved the world, that he gave his only begotten Son,
that whosoever believeth on him should not perish, but have eternal life.
```

### 5. Display Copyright

When displaying Bible content, you must include the appropriate copyright notice:

```python
result = client.get_version(12)
if is_ok(result):
    version = result.value
    print(version.copyright_short)  # Display with content
```

---

## Installation

### pip

```bash
pip install youversion
```

### uv

```bash
uv add youversion
```

### Poetry

```bash
poetry add youversion
```

---

## Configuration

```python
from youversion import YouVersionClient

# Basic initialization
client = YouVersionClient(api_key="your-api-key")

# With custom settings
client = YouVersionClient(
    api_key="your-api-key",
    base_url="https://api.youversion.com",  # Default
    timeout=30.0,  # Request timeout in seconds
)

# Using context manager (recommended)
with YouVersionClient(api_key="your-api-key") as client:
    # Client automatically closes when done
    pass
```

### Environment Variables

```python
import os
from youversion import YouVersionClient

client = YouVersionClient(api_key=os.environ["YOUVERSION_API_KEY"])
```

---

## Sync vs Async Clients

The SDK provides both synchronous and asynchronous clients with identical APIs.

### Synchronous Client

Use `YouVersionClient` for synchronous code:

```python
from youversion import YouVersionClient, is_ok

# With context manager (recommended)
with YouVersionClient(api_key="your-api-key") as client:
    result = client.get_versions("en")
    if is_ok(result):
        for version in result.value.data:
            print(version.title)
```

### Asynchronous Client

Use `AsyncYouVersionClient` for async code:

```python
import asyncio
from youversion import AsyncYouVersionClient, is_ok

async def main():
    async with AsyncYouVersionClient(api_key="your-api-key") as client:
        result = await client.get_versions("en")
        if is_ok(result):
            for version in result.value.data:
                print(version.title)

asyncio.run(main())
```

---

## Manual Client Management

If you need more control over the client lifecycle, you can manage it manually instead of using context managers.

### Sync Client (Manual)

```python
from youversion import YouVersionClient, is_ok

client = YouVersionClient(api_key="your-api-key")

try:
    result = client.get_versions("en")
    if is_ok(result):
        print(f"Found {len(result.value.data)} versions")

    result = client.get_passage(12, "JHN.3.16")
    if is_ok(result):
        print(result.value.content)
finally:
    # Always close the client to release resources
    client.close()
```

### Async Client (Manual)

```python
import asyncio
from youversion import AsyncYouVersionClient, is_ok

async def main():
    client = AsyncYouVersionClient(api_key="your-api-key")

    try:
        result = await client.get_versions("en")
        if is_ok(result):
            print(f"Found {len(result.value.data)} versions")

        result = await client.get_passage(12, "JHN.3.16")
        if is_ok(result):
            print(result.value.content)
    finally:
        # Always close the client to release resources
        await client.close()

asyncio.run(main())
```

### When to Use Manual Management

- **Connection pooling**: Keep a client alive across multiple operations
- **Application lifecycle**: Initialize once at startup, close at shutdown
- **Custom resource management**: Integration with dependency injection or frameworks

---

## YouVersionClient API

### Version Methods

#### `get_versions(language_ranges, license_id=None)`

Get all Bible versions for a language.

```python
result = client.get_versions("en")

if is_ok(result):
    for version in result.value.data:
        print(f"{version.id}: {version.abbreviation} - {version.title}")
```

Output:
```
12: ASV - American Standard Version
1932: FBV - Free Bible Version
3034: BSB - Berean Standard Bible
...
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `language_ranges` | `str` | Language tag (e.g., `"en"`, `"es"`, `"en-US"`) |
| `license_id` | `str \| int \| None` | Optional license filter |

**Returns:** `Result[PaginatedResponse[BibleVersion], ValidationError]`

---

#### `get_version(bible_id)`

Get a specific Bible version by ID.

```python
result = client.get_version(12)

if is_ok(result):
    version = result.value
    print(f"{version.abbreviation}: {version.title}")
    print(f"Language: {version.language_tag}")
    print(f"Copyright: {version.copyright_short}")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `bible_id` | `int` | The Bible version ID |

**Returns:** `Result[BibleVersion, NotFoundError]`

---

### Book Methods

#### `get_books(version_id)`

Get all books in a Bible version.

```python
result = client.get_books(12)

if is_ok(result):
    for book in result.value.data:
        print(f"{book.id}: {book.title} ({book.canon})")
```

Output:
```
GEN: Genesis (old_testament)
EXO: Exodus (old_testament)
...
MAT: Matthew (new_testament)
...
REV: Revelation (new_testament)
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |

**Returns:** `Result[PaginatedResponse[BibleBook], NotFoundError]`

---

#### `get_book(version_id, book)`

Get a specific book.

```python
result = client.get_book(12, "GEN")

if is_ok(result):
    book = result.value
    print(f"{book.title} ({book.abbreviation})")
    print(f"Canon: {book.canon}")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `book` | `str` | USFM book identifier (e.g., `"GEN"`, `"MAT"`, `"REV"`) |

**Returns:** `Result[BibleBook, NotFoundError]`

---

### Chapter Methods

#### `get_chapters(version_id, book)`

Get all chapters in a book.

```python
result = client.get_chapters(12, "GEN")

if is_ok(result):
    print(f"Genesis has {len(result.value.data)} chapters")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `book` | `str` | USFM book identifier |

**Returns:** `Result[PaginatedResponse[BibleChapter], NotFoundError]`

---

#### `get_chapter(version_id, book, chapter)`

Get a specific chapter.

```python
result = client.get_chapter(12, "GEN", 1)

if is_ok(result):
    chapter = result.value
    print(f"Chapter: {chapter.title}")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `book` | `str` | USFM book identifier |
| `chapter` | `int` | Chapter number |

**Returns:** `Result[BibleChapter, NotFoundError]`

---

### Verse Methods

#### `get_verses(version_id, book, chapter)`

Get all verses in a chapter.

```python
result = client.get_verses(12, "GEN", 1)

if is_ok(result):
    print(f"Genesis 1 has {len(result.value.data)} verses")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `book` | `str` | USFM book identifier |
| `chapter` | `int` | Chapter number |

**Returns:** `Result[PaginatedResponse[BibleVerse], NotFoundError]`

---

#### `get_verse(version_id, book, chapter, verse)`

Get a specific verse.

```python
result = client.get_verse(12, "GEN", 1, 1)

if is_ok(result):
    verse = result.value
    print(f"Verse: {verse.title}")
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `book` | `str` | USFM book identifier |
| `chapter` | `int` | Chapter number |
| `verse` | `int` | Verse number |

**Returns:** `Result[BibleVerse, NotFoundError]`

---

### Passage Methods

#### `get_passage(version_id, usfm, *, format="text", include_headings=False, include_notes=False)`

Get passage content by USFM reference.

```python
# Single verse
result = client.get_passage(12, "JHN.3.16")

# Verse range (same chapter)
result = client.get_passage(12, "GEN.1.1-3")

# With HTML formatting
result = client.get_passage(12, "JHN.3.16", format="html")

# With headings and notes
result = client.get_passage(
    12,
    "PSA.23.1-6",
    include_headings=True,
    include_notes=True
)

if is_ok(result):
    passage = result.value
    print(f"{passage.reference}")
    print(passage.content)
```

**USFM Reference Format:**
- Single verse: `JHN.3.16` (Book.Chapter.Verse)
- Verse range: `GEN.1.1-3` (Book.Chapter.StartVerse-EndVerse)

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `version_id` | `int` | The Bible version ID |
| `usfm` | `str` | USFM reference (e.g., `"JHN.3.16"`, `"GEN.1.1-3"`) |
| `format` | `"text" \| "html"` | Output format (default: `"text"`) |
| `include_headings` | `bool` | Include section headings (default: `False`) |
| `include_notes` | `bool` | Include footnotes (default: `False`) |

**Returns:** `Result[BiblePassage, NotFoundError | ValidationError]`

---

## Types

### BibleVersion

```python
class BibleVersion:
    id: int                      # Unique identifier
    abbreviation: str            # Short name (e.g., "ASV", "KJV")
    title: str                   # Full name
    language_tag: str            # Language code (e.g., "en")
    copyright_short: str | None  # Short copyright notice
    copyright_long: str | None   # Full copyright text
```

### BibleBook

```python
class BibleBook:
    id: str                              # USFM identifier (e.g., "GEN", "MAT")
    title: str                           # Book name
    full_title: str | None               # Full book name
    abbreviation: str                    # Short name
    canon: "old_testament" | "new_testament" | "deuterocanon"
    chapters: list[BibleChapter] | None  # Chapters (when included)
    intro: BibleBookIntro | None         # Book introduction
```

### BibleChapter

```python
class BibleChapter:
    id: str                          # Chapter identifier
    passage_id: str                  # USFM reference
    title: str                       # Chapter title
    verses: list[BibleVerse] | None  # Verses (when included)
```

### BibleVerse

```python
class BibleVerse:
    id: str          # Verse identifier
    passage_id: str  # USFM reference
    title: str       # Verse title
```

### BiblePassage

```python
class BiblePassage:
    id: str         # USFM reference
    content: str    # Passage text (plain text or HTML)
    reference: str  # Human-readable reference (e.g., "John 3:16")
```

### PaginatedResponse

```python
class PaginatedResponse[T]:
    data: list[T]                  # Results
    next_page_token: str | None    # Pagination token
    total_count: int | None        # Total results
```

---

## Error Handling

The SDK uses a `Result` type for explicit error handling instead of exceptions for API errors.

### Result Type

```python
from youversion import is_ok, is_err

result = client.get_version(999999)

if is_ok(result):
    version = result.value
    print(version.title)
else:
    error = result.error
    print(f"Error: {error.message}")
```

### Domain Errors (Returned in Result)

These errors are returned as `Err` values:

| Error | Description |
|-------|-------------|
| `NotFoundError` | Resource not found (404) |
| `ValidationError` | Invalid request parameters (400) |

```python
from youversion import NotFoundError, ValidationError, is_err

result = client.get_version(999999)

if is_err(result):
    match result.error:
        case NotFoundError(resource=r, identifier=id):
            print(f"{r} '{id}' not found")
        case ValidationError(field=f, reason=r):
            print(f"Invalid {f}: {r}")
```

### Exceptions (Raised)

These errors are raised as exceptions for infrastructure issues:

| Exception | Description |
|-----------|-------------|
| `NetworkError` | Connection failed |
| `AuthenticationError` | Invalid API key (401) |
| `RateLimitError` | Too many requests (429) |
| `ServerError` | Server error (5xx) |

```python
from youversion import (
    YouVersionClient,
    NetworkError,
    AuthenticationError,
    RateLimitError,
)

try:
    with YouVersionClient(api_key="invalid") as client:
        result = client.get_versions("en")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except NetworkError:
    print("Connection failed")
```

---

## USFM Book Identifiers

| Old Testament | | New Testament | |
|--------------|---|--------------|---|
| GEN - Genesis | EXO - Exodus | MAT - Matthew | MRK - Mark |
| LEV - Leviticus | NUM - Numbers | LUK - Luke | JHN - John |
| DEU - Deuteronomy | JOS - Joshua | ACT - Acts | ROM - Romans |
| JDG - Judges | RUT - Ruth | 1CO - 1 Corinthians | 2CO - 2 Corinthians |
| 1SA - 1 Samuel | 2SA - 2 Samuel | GAL - Galatians | EPH - Ephesians |
| 1KI - 1 Kings | 2KI - 2 Kings | PHP - Philippians | COL - Colossians |
| 1CH - 1 Chronicles | 2CH - 2 Chronicles | 1TH - 1 Thessalonians | 2TH - 2 Thessalonians |
| EZR - Ezra | NEH - Nehemiah | 1TI - 1 Timothy | 2TI - 2 Timothy |
| EST - Esther | JOB - Job | TIT - Titus | PHM - Philemon |
| PSA - Psalms | PRO - Proverbs | HEB - Hebrews | JAS - James |
| ECC - Ecclesiastes | SNG - Song of Solomon | 1PE - 1 Peter | 2PE - 2 Peter |
| ISA - Isaiah | JER - Jeremiah | 1JN - 1 John | 2JN - 2 John |
| LAM - Lamentations | EZK - Ezekiel | 3JN - 3 John | JUD - Jude |
| DAN - Daniel | HOS - Hosea | REV - Revelation | |
| JOL - Joel | AMO - Amos | | |
| OBA - Obadiah | JON - Jonah | | |
| MIC - Micah | NAM - Nahum | | |
| HAB - Habakkuk | ZEP - Zephaniah | | |
| HAG - Haggai | ZEC - Zechariah | | |
| MAL - Malachi | | | |

---