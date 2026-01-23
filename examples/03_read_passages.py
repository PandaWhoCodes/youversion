#!/usr/bin/env python3
"""Read Bible passages - the most common use case."""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 3: Reading Bible Passages")
print("=" * 60)

with YouVersionClient(API_KEY) as client:
    VERSION_ID = 12  # ASV

    # Read a single verse
    print("\n--- Single Verse: John 3:16 ---")
    result = client.get_passage(VERSION_ID, "JHN.3.16")
    if is_ok(result):
        passage = result.value
        print(f"Reference: {passage.reference}")
        print(f"Content: {passage.content}")

    # Read a verse range
    print("\n--- Verse Range: Psalm 23:1-3 ---")
    result = client.get_passage(VERSION_ID, "PSA.23.1-PSA.23.3")
    if is_ok(result):
        passage = result.value
        print(f"Reference: {passage.reference}")
        print(f"Content: {passage.content}")

    # Read an entire chapter
    print("\n--- Entire Chapter: Psalm 117 (shortest chapter) ---")
    result = client.get_passage(VERSION_ID, "PSA.117")
    if is_ok(result):
        passage = result.value
        print(f"Reference: {passage.reference}")
        print(f"Content: {passage.content}")
