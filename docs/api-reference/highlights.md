# Highlights API Reference

> Source: https://developers.youversion.com/api/highlights

**Base URL:** `https://api.youversion.com`

**Authentication:** OAuth required (user access token)

---

## Overview

The Highlights API manages user annotations on scripture passages, allowing retrieval, creation, updates, and deletion of highlighted verses.

---

## 1. Get Highlights Collection

**Endpoint:** `GET /v1/highlights`

**Description:** Retrieves highlights for a passage. The response will return a color per verse without ranges.

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `bible_id` | integer (int32) | Yes | The Bible version identifier | 111 |
| `passage_id` | string | Yes | The passage identifier (verse or chapter USFM format) | MAT.1.1 |

### Response (200 - Success)

```json
{
  "data": [
    {
      "bible_id": 111,
      "passage_id": "MAT.1.1",
      "color": "44aa44"
    }
  ]
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of highlight objects (read-only) |
| `data[].bible_id` | integer (int32) | Bible version identifier |
| `data[].passage_id` | string | USFM passage reference |
| `data[].color` | string | Hex color (pattern: `^[0-9a-f]{6}$`) |

---

## 2. Create/Update Highlight

**Endpoint:** `POST /v1/highlights`

**Description:** Creates or updates a highlight. Verse ranges may be used in the POST body `passage_id` attribute.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bible_id` | integer (int32) | Yes | Bible version identifier |
| `passage_id` | string | Yes | The passage identifier (verse USFM format) |
| `color` | string | Yes | The highlight color in hex format (pattern: `^[0-9a-f]{6}$`) |

### Example Request

```json
{
  "bible_id": 111,
  "passage_id": "MAT.1.1",
  "color": "44aa44"
}
```

### Response (201 - Created)

```json
{
  "bible_id": 111,
  "passage_id": "MAT.1.1",
  "color": "44aa44"
}
```

---

## 3. Delete Highlights

**Endpoint:** `DELETE /v1/highlights/{passage_id_path}`

**Description:** Clear highlights for a passage.

### Path Parameters

| Parameter | Type | Required | Description | Default | Example |
|-----------|------|----------|-------------|---------|---------|
| `passage_id_path` | string | Yes | The passage identifier (verse or chapter USFM format) | JHN.3.16 | MAT.1.1 |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bible_id` | integer (int32) | Yes | The Bible version identifier |

### Response (204 - Success)

No content returned upon successful deletion.

---

## Color Format

Colors must be specified as 6-character lowercase hexadecimal strings without the `#` prefix.

**Pattern:** `^[0-9a-f]{6}$`

**Valid examples:**
- `44aa44` (green)
- `ff5733` (orange-red)
- `3366cc` (blue)

**Invalid examples:**
- `#44aa44` (no # prefix allowed)
- `44AA44` (must be lowercase)
- `green` (must be hex)

---

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid access token |
| 404 | Not Found - Bible or passage not found |
| 4XX | Other client errors |
| 5XX | Server errors |
