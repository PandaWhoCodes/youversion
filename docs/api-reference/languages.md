# Languages API Reference

> Source: https://developers.youversion.com/api/languages

**Base URL:** `https://api.youversion.com`

---

## 1. Get Languages Collection

**Endpoint:** `GET /v1/languages`

**Description:** Get a collection of language objects. Add the `country` parameter to filter to prominent languages for that country.

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `page_size` | integer or string | No | Items per response (1-100); use "*" only with ≤3 fields | 25 |
| `fields[]` | string[] | No | Top-level fields to include; supports bracket notation | ["id", "language"] |
| `page_token` | string | No | Token for pagination | eyJzdGFydF9hdCI6IDI2fQ== |
| `country` | string | No | ISO 3166 two-character country code | US |

### Response (200 - Success)

```json
{
  "data": [
    {
      "id": "en",
      "language": "en",
      "script": "Latn",
      "script_name": "Latin",
      "aliases": ["english"],
      "display_names": {
        "en": "English"
      },
      "scripts": ["Latn"],
      "variants": [],
      "countries": ["US", "GB", "AU"],
      "text_direction": "ltr",
      "writing_population": 1327104050,
      "speaking_population": 1636485840,
      "default_bible_id": 111
    }
  ],
  "next_page_token": "eyJzdGFydF9hdCI6IDI2fQ==",
  "total_size": 2000
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of language objects |
| `data[].id` | string | BCP 47 language tag |
| `data[].language` | string | ISO 639 language code |
| `data[].script` | string or null | ISO 15924 script code |
| `data[].script_name` | string or null | Human-readable script name |
| `data[].aliases` | string[] | Alternative names for the language |
| `data[].display_names` | object | Localized display names (key: locale, value: name) |
| `data[].scripts` | string[] | Available scripts for this language |
| `data[].variants` | string[] | Language variants |
| `data[].countries` | string[] | Countries where language is spoken |
| `data[].text_direction` | string | Text direction: "ltr" or "rtl" |
| `data[].writing_population` | integer | Estimated writing population |
| `data[].speaking_population` | integer | Estimated speaking population |
| `data[].default_bible_id` | integer | Default Bible version for this language |
| `next_page_token` | string | Token for next page of results |
| `total_size` | integer | Total number of languages |

---

## 2. Get Single Language Details

**Endpoint:** `GET /v1/languages/{language_id}`

**Description:** Retrieve a single language resource using its BCP47 identifier.

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `language_id` | string | Yes | Canonical BCP 47 code (language or language+script) | en |

### Response (200 - Success)

Returns a language object matching the schema from the collection endpoint.

```json
{
  "id": "en",
  "language": "en",
  "script": "Latn",
  "script_name": "Latin",
  "aliases": ["english"],
  "display_names": {
    "en": "English"
  },
  "scripts": ["Latn"],
  "variants": [],
  "countries": ["US", "GB", "AU"],
  "text_direction": "ltr",
  "writing_population": 1327104050,
  "speaking_population": 1636485840,
  "default_bible_id": 111
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 301 | Redirect to canonical language code with script |
| 4XX | Client error with message property |
| 5XX | Server error |

---

## BCP 47 Language Tags

The API uses BCP 47 language tags for identification. Examples:

| Tag | Description |
|-----|-------------|
| `en` | English |
| `es` | Spanish |
| `zh-Hans` | Chinese (Simplified) |
| `zh-Hant` | Chinese (Traditional) |
| `sr-Latn` | Serbian (Latin script) |
| `sr-Cyrl` | Serbian (Cyrillic script) |

---

## Text Direction

| Value | Description |
|-------|-------------|
| `ltr` | Left-to-right (English, Spanish, etc.) |
| `rtl` | Right-to-left (Hebrew, Arabic, etc.) |
