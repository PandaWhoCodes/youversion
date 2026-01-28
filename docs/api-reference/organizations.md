# Organizations API Reference

> Source: https://developers.youversion.com/api/organizations

**Base URL:** `https://api.youversion.com`

---

## 1. Get Organizations Collection

**Endpoint:** `GET /v1/organizations`

**Description:** Returns a list of Organization objects for a given Bible version.

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `bible_id` | integer (int32) | Yes | The Bible version identifier | 111 |

### Headers

| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `Accept-Language` | string | Yes | Localization preference per RFC 2616 section 14.4 | en |

### Response (200 - Success)

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "parent_organization_id": null,
      "name": "Biblica",
      "description": "Biblica is the worldwide publisher and translation sponsor of the New International Version.",
      "email": "contact@biblica.com",
      "phone": "+1-555-123-4567",
      "primary_language": "en",
      "website_url": "https://www.biblica.com",
      "address": {
        "formatted_address": "123 Main St, Colorado Springs, CO 80903, USA",
        "place_id": "ChIJ...",
        "latitude": 38.8339,
        "longitude": -104.8214,
        "administrative_area_level_1": "Colorado",
        "locality": "Colorado Springs",
        "country": "US"
      }
    }
  ],
  "next_page_token": "eyJzdGFydF9hdCI6IDI2fQ=="
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of Organization objects (read-only) |
| `data[].id` | string (UUID) | Unique organization identifier |
| `data[].parent_organization_id` | string (UUID, nullable) | Parent organization ID if applicable |
| `data[].name` | string | Publisher name in negotiated language |
| `data[].description` | string | Organization purpose and mission statement |
| `data[].email` | string (nullable) | Contact email |
| `data[].phone` | string (nullable) | Contact phone |
| `data[].primary_language` | string | Primary language code (e.g., "en") |
| `data[].website_url` | string | Organization website |
| `data[].address` | object | Address information |
| `data[].address.formatted_address` | string | Full formatted address |
| `data[].address.place_id` | string | Google Places ID |
| `data[].address.latitude` | number | Latitude coordinate |
| `data[].address.longitude` | number | Longitude coordinate |
| `data[].address.administrative_area_level_1` | string | State/province |
| `data[].address.locality` | string | City |
| `data[].address.country` | string | Country code |
| `next_page_token` | string | Pagination token |

---

## 2. Get Organization Details

**Endpoint:** `GET /v1/organizations/{organization_id}`

**Description:** Retrieves a single organization resource by its unique identifier.

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `organization_id` | string (UUID) | Yes | Organization unique ID | 550e8400-e29b-41d4-a716-446655440000 |

### Headers

| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `Accept-Language` | string | Yes | Localization preference per RFC 2616 | en |

### Response (200 - Success)

Returns a complete Organization object with identical properties as listed above.

---

## 3. Get Organization's Bibles

**Endpoint:** `GET /v1/organizations/{organization_id}/bibles`

**Description:** Returns Bibles associated with a specific organization.

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `organization_id` | string (UUID) | Yes | Organization unique ID | 550e8400-e29b-41d4-a716-446655440000 |

### Query Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `page_size` | integer or string | No | Items per page (1-100); "*" supported with ≤3 fields | 25 |
| `fields[]` | string[] | No | Top-level fields to include | - |
| `page_token` | string | No | Pagination token for result continuation | - |

### Response (200 - Success)

```json
{
  "data": [
    {
      "id": 111,
      "abbreviation": "NIV",
      "title": "New International Version 2011",
      "localized_title": "New International Version",
      "language_tag": "en",
      "copyright": "Copyright © 1973, 1978, 1984, 2011 by Biblica, Inc.®",
      "promotional_content": "Extended copyright/publisher information",
      "publisher_url": "https://www.biblica.com/yv-learn-more/",
      "books": ["GEN", "EXO", "LEV"],
      "youversion_deep_link": "https://www.bible.com/versions/111"
    }
  ],
  "next_page_token": "eyJzdGFydF9hdCI6IDI2fQ==",
  "total_size": 15
}
```

### Bible Object Properties

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Bible version identifier |
| `abbreviation` | string | Version abbreviation (e.g., "NIV") |
| `title` | string | English Bible title |
| `localized_title` | string | Localized Bible title |
| `language_tag` | string | BCP47 language tag |
| `copyright` | string | Copyright text |
| `promotional_content` | string | Extended copyright/publisher information |
| `publisher_url` | string | Publisher webpage link |
| `books` | string[] | Ordered book ID list |
| `youversion_deep_link` | string | Direct link to Bible version on YouVersion |

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 4XX | Client error |
| 5XX | Server error |
