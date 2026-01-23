#!/usr/bin/env python3
"""Working with multiple languages."""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 5: Multiple Languages")
print("=" * 60)

with YouVersionClient(API_KEY) as client:
    # Get versions for different languages
    languages = [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("de", "German"),
        ("pt", "Portuguese"),
    ]

    print("\nBible versions by language:\n")

    for lang_code, lang_name in languages:
        result = client.get_versions(lang_code)
        if is_ok(result):
            versions = result.value
            print(f"{lang_name} ({lang_code}): {len(versions.data)} versions")
            if versions.data:
                first = versions.data[0]
                print(f"  Example: {first.abbreviation} - {first.title}")
        else:
            print(f"{lang_name}: No versions found")
