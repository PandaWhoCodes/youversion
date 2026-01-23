#!/usr/bin/env python3
"""Manual client management - using the client without context managers."""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 6: Manual Client Management (Sync)")
print("=" * 60)

# Create client without context manager
client = YouVersionClient(api_key=API_KEY)

try:
    # Get Bible versions
    result = client.get_versions("en")
    if is_ok(result):
        print(f"\nFound {len(result.value.data)} English versions")
        for v in result.value.data[:3]:
            print(f"  [{v.id:>4}] {v.abbreviation}")

    # Get a passage
    result = client.get_passage(12, "JHN.3.16")
    if is_ok(result):
        print(f"\n{result.value.reference}:")
        print(f"  {result.value.content}")

    # Get book info
    result = client.get_book(12, "PSA")
    if is_ok(result):
        print(f"\nBook: {result.value.title}")
        print(f"  Chapters: {len(result.value.chapters) if result.value.chapters else 'N/A'}")

finally:
    # Always close the client to release resources
    client.close()
    print("\nClient closed.")
