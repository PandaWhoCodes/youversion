# Licenses API Reference

> Source: https://developers.youversion.com/api/licenses

**Base URL:** `https://api.youversion.com`

---

## Overview

Provides data about licenses in the YouVersion platform. These licenses are used by developers to get access to various types of content, e.g. Bibles.

---

## Get a Collection of Licenses

**Endpoint:** `GET /v1/licenses`

**Description:** Retrieves licenses for a specific Bible and developer combination.

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `bible_id` | integer (int32) | Yes | The Bible version identifier | 111 |
| `developer_id` | string (UUID) | Yes | The Developer's unique ID in the Platform | d0338b35-fe38-4ce4-b5fe-71e9a4a9a4c8 |
| `all_available` | boolean | No | Modifies response to include every license regardless of developer agreement status (default: false) | true |

### Response (200 - Success)

```json
{
  "data": [
    {
      "id": 123,
      "name": "Standard Bible License",
      "version": 1,
      "organization_id": "550e8400-e29b-41d4-a716-446655440000",
      "html": "<p>License terms...</p>",
      "bible_ids": [111, 112, 113],
      "uri": "https://example.com/license",
      "agreed_dt": "2024-01-15T10:30:00Z",
      "yvp_user_id": "550e8400-e29b-41d4-a716-446655440001"
    }
  ]
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of license objects |
| `data[].id` | integer | License identifier |
| `data[].name` | string | License name |
| `data[].version` | integer | License version number |
| `data[].organization_id` | string (UUID) | The YouVersion Organization ID that owns the license |
| `data[].html` | string | HTML representation of the license terms |
| `data[].bible_ids` | integer[] | Array of Bible IDs covered by this license |
| `data[].uri` | string (URI, nullable) | URI pointing to the license terms |
| `data[].agreed_dt` | string (date-time, nullable) | Date the developer agreed to this license (null if not agreed) |
| `data[].yvp_user_id` | string (UUID) | The YouVersion Platform User ID logged into the developer portal |

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Successful request |
| 4XX | Client error |
| 5XX | Server error |

### Error Response

```json
{
  "message": "Error message describing the issue"
}
```

---

## Usage Notes

1. **Filtering by Bible**: The `bible_id` parameter is required to get licenses for a specific Bible version.

2. **Developer ID**: The `developer_id` must be a valid UUID associated with a registered developer account.

3. **Agreement Status**: The `agreed_dt` field will be `null` if the developer has not yet agreed to the license terms.

4. **All Available**: Set `all_available=true` to see all licenses, including those the developer hasn't agreed to yet.
