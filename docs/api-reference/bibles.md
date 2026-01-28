# Bibles API Reference

> Source: https://developers.youversion.com/api/bibles

**Base URL:** `https://api.youversion.com`

---

## 1. Get a Bible Collection

**Endpoint:** `GET /v1/bibles`

**Description:** Retrieves a paginated list of available Bible versions, filtering by language ranges.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `language_ranges[]` | string[] | Yes | Ordered language ranges in bracket notation (RFC 4647 format) |
| `all_available` | boolean | No | Include all Bibles regardless of licensing (default: false) |
| `license_id` | integer | No | Filter by license identifier |
| `page_size` | integer/string | No | Items per page (1-100) or "*" with ≤3 fields |
| `fields[]` | string[] | No | Specific top-level fields to return |
| `page_token` | string | No | Token for retrieving next results page |

### Response (200)

```json
{
  "data": [
    {
      "id": 111,
      "abbreviation": "NIV",
      "title": "New International Version 2011",
      "localized_title": "New International Version",
      "language_tag": "en",
      "copyright": "...",
      "youversion_deep_link": "https://www.bible.com/versions/111",
      "organization_id": "uuid"
    }
  ],
  "next_page_token": "string",
  "total_size": 42
}
```

---

## 2. Get a Bible's Data

**Endpoint:** `GET /v1/bibles/{bible_id_path}`

**Description:** Retrieves metadata for a single Bible version (excludes text content).

### Path Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `bible_id_path` | integer | Yes | 206 |

### Response (200)

```json
{
  "id": 111,
  "abbreviation": "NIV",
  "title": "New International Version 2011",
  "localized_abbreviation": "NIV",
  "localized_title": "New International Version",
  "language_tag": "en",
  "copyright": "...",
  "promotional_content": "...",
  "info": "The Holy Bible",
  "publisher_url": "https://www.biblica.com/yv-learn-more/",
  "books": ["GEN", "EXO", "LEV"],
  "youversion_deep_link": "https://www.bible.com/versions/111",
  "organization_id": "uuid"
}
```

---

## 3. Get the Index for a Bible

**Endpoint:** `GET /v1/bibles/{bible_id_path}/index`

**Description:** Returns the complete hierarchical structure of books, chapters, and verses.

### Path Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `bible_id_path` | integer | Yes | 206 |

### Response (200)

```json
{
  "text_direction": "ltr",
  "books": [
    {
      "id": "GEN",
      "title": "Genesis",
      "full_title": "The Book of Genesis",
      "abbreviation": "Gen.",
      "canon": "old_testament",
      "chapters": [
        {
          "id": 1,
          "passage_id": "GEN.1",
          "title": 1,
          "verses": [
            {
              "id": 1,
              "passage_id": "GEN.1.1",
              "title": 1
            }
          ]
        }
      ],
      "intro": {}
    }
  ]
}
```

---

## 4. Get a Passage of Bible Text

**Endpoint:** `GET /v1/bibles/{bible_id_path}/passages/{passage_id_path}`

**Description:** Retrieves scripture text in specified format with optional headings and notes.

### Path Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `bible_id_path` | integer | Yes | 206 |
| `passage_id_path` | string | Yes | JHN.3.16 |

### Query Parameters

| Parameter | Type | Required | Options | Default |
|-----------|------|----------|---------|---------|
| `format` | string | No | text, html | text |
| `include_headings` | boolean | No | - | false* |
| `include_notes` | boolean | No | - | false* |

*Defaults to true for chapter/intro references

### Response (200)

```json
{
  "id": "MAT.1.1",
  "content": "The book of the genealogy of Jesus Christ...",
  "reference": "Matthew 1:1"
}
```

---

## 5. Get a Book Collection for a Bible

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books`

**Description:** Lists all books for a specified Bible version.

### Path Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `bible_id_path` | integer | Yes | 206 |

### Query Parameters

| Parameter | Type | Required | Options |
|-----------|------|----------|---------|
| `canon` | string | No | new_testament, old_testament, deuterocanon |

### Response (200)

Returns an array of book objects (see structure in Index response).

---

## 6. Get a Book's Data

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books/{book_id}`

**Description:** Retrieves metadata for a single book (no text content).

### Path Parameters

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `bible_id_path` | integer | Yes | 206 | |
| `book_id` | string | Yes | GEN | 3-character USFM code |

### Response (200)

Returns a single book object with chapters array.

---

## 7. Get a Chapter Collection for a Book

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books/{book_id}/chapters`

**Description:** Retrieves all chapters within a specified book.

### Path Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `bible_id_path` | integer | Yes | 206 |
| `book_id` | string | Yes | GEN |

### Response (200)

Returns an array of chapter objects with verse collections.

---

## 8. Get a Chapter's Data

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books/{book_id}/chapters/{chapter_id}`

**Description:** Returns chapter metadata including verse structure.

### Path Parameters

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `bible_id_path` | integer | Yes | |
| `book_id` | string | Yes | 3-character code |
| `chapter_id` | string | Yes | 1-7 characters |

### Response (200)

Returns a chapter object with verses array.

---

## 9. Get a Verse Collection for a Chapter

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books/{book_id}/chapters/{chapter_id}/verses`

**Description:** Lists all verses in a specified chapter.

### Path Parameters

Same as Chapter endpoint, includes `chapter_id`.

### Response (200)

Returns an array of verse objects with IDs and passage identifiers.

---

## 10. Get a Verse's Data

**Endpoint:** `GET /v1/bibles/{bible_id_path}/books/{book_id}/chapters/{chapter_id}/verses/{verse_id}`

**Description:** Retrieves individual verse metadata (no text).

### Path Parameters

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `bible_id_path` | integer | Yes | |
| `book_id` | string | Yes | 3-character |
| `chapter_id` | string | Yes | 1-7 chars |
| `verse_id` | string | Yes | 1-7 chars |

### Response (200)

```json
{
  "id": "1",
  "passage_id": "GEN.1.1",
  "title": "1"
}
```

---

## Standard Response Codes

| Code | Description |
|------|-------------|
| 200/204 | Success |
| 4XX | Client errors (invalid parameters, missing auth) |
| 5XX | Server errors |
