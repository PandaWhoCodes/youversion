#!/usr/bin/env python3
"""Basic SDK usage - getting started with YouVersion API."""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 1: Basic SDK Usage")
print("=" * 60)

# Create client with context manager (auto-closes)
with YouVersionClient(API_KEY) as client:
    # Get available Bible versions for English
    result = client.get_versions("en")

    if is_ok(result):
        versions = result.value
        print(f"\nFound {len(versions.data)} English Bible versions:\n")
        for v in versions.data[:5]:  # Show first 5
            print(f"  [{v.id:>4}] {v.abbreviation:<10} - {v.title}")
        if len(versions.data) > 5:
            print(f"  ... and {len(versions.data) - 5} more")
    else:
        print(f"Error: {result.error}")
