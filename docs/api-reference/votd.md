# Verse of the Day API Reference

> Source: https://developers.youversion.com/api/verse-of-the-days

**Base URL:** `https://api.youversion.com`

---

## Overview

The Verse of the Days endpoints provide access to daily Bible verse selections from YouVersion's calendar system.

---

## 1. Get Full Year Verse Calendar

**Endpoint:** `GET /v1/verse_of_the_days`

**Description:** Returns the complete verse of the day calendar for the year. January 1 is day 1 and December 31 is day 365 (or 366 in a leap year).

### Parameters

None required.

### Response (200 - Success)

```json
{
  "data": [
    {
      "day": 1,
      "passage_id": "JHN.3.16"
    },
    {
      "day": 2,
      "passage_id": "PSA.23.1"
    },
    {
      "day": 3,
      "passage_id": "ROM.8.28"
    }
  ]
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Array of verse of the day objects |
| `data[].day` | integer | Day of the year (1-366) |
| `data[].passage_id` | string | USFM passage reference (e.g., "JHN.3.16") |

---

## 2. Get Verse for Specific Day

**Endpoint:** `GET /v1/verse_of_the_days/{day}`

**Description:** Returns the verse of the day for a specific day of the year. Day is the day of the year (1-366).

### Path Parameters

| Parameter | Type | Required | Description | Range |
|-----------|------|----------|-------------|-------|
| `day` | integer | Yes | The day of the year | 1-366 |

### Response (200 - Success)

```json
{
  "day": 1,
  "passage_id": "JHN.3.16"
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `day` | integer | Day of the year (1-366) |
| `passage_id` | string | USFM passage reference (e.g., "JHN.3.16") |

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 4XX | Client error (e.g., invalid day number) |
| 5XX | Server error |

### Error Response

```json
{
  "message": "Error message describing the issue"
}
```

---

## Day Number Reference

| Day | Date |
|-----|------|
| 1 | January 1 |
| 32 | February 1 |
| 60 | March 1 (non-leap year) / February 29 (leap year) |
| 91 | April 1 (non-leap year) |
| 121 | May 1 (non-leap year) |
| 152 | June 1 (non-leap year) |
| 182 | July 1 (non-leap year) |
| 213 | August 1 (non-leap year) |
| 244 | September 1 (non-leap year) |
| 274 | October 1 (non-leap year) |
| 305 | November 1 (non-leap year) |
| 335 | December 1 (non-leap year) |
| 365 | December 31 (non-leap year) |
| 366 | December 31 (leap year only) |

---

## Usage Notes

1. **Leap Years**: Day 366 is only valid during leap years (2024, 2028, etc.).

2. **Passage Format**: The `passage_id` uses USFM format: `{BOOK}.{CHAPTER}.{VERSE}` (e.g., "JHN.3.16" for John 3:16).

3. **Retrieving Content**: Use the passage_id with the Bibles API to get the actual verse text:
   ```
   GET /v1/bibles/{bible_id}/passages/{passage_id}
   ```
