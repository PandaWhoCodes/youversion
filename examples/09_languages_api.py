#!/usr/bin/env python3
"""Languages API - explore available languages for Bible translations.

This example demonstrates how to:
1. Get all available languages
2. Filter languages by country
3. Get details for a specific language by BCP 47 tag
4. Explore language metadata (scripts, populations, etc.)

Usage:
    export YOUVERSION_API_KEY="your-api-key"
    python examples/09_languages_api.py
"""

import os

from youversion import YouVersionClient, is_err, is_ok

API_KEY = os.environ.get("YOUVERSION_API_KEY")

if not API_KEY:
    print("Please set YOUVERSION_API_KEY environment variable")
    exit(1)

print("=" * 60)
print("Example: Languages API")
print("=" * 60)

with YouVersionClient(API_KEY) as client:
    # 1. Get all available languages
    print("\n1. Getting all available languages...")
    result = client.get_languages()

    if is_ok(result):
        languages = result.value.data
        print(f"   Found {len(languages)} languages\n")

        # Show first 10 languages
        print("   First 10 languages:")
        print("   " + "-" * 50)
        for lang in languages[:10]:
            direction = "RTL" if lang.text_direction == "rtl" else "LTR"
            default_bible = f"(default: {lang.default_bible_id})" if lang.default_bible_id else ""
            print(f"   {lang.id:<8} {lang.language:<6} {direction:<4} {default_bible}")
        if len(languages) > 10:
            print(f"   ... and {len(languages) - 10} more")
    else:
        print(f"   Error: {result.error}")

    # 2. Filter languages by country
    print("\n" + "=" * 60)
    print("\n2. Getting languages available in India (IN)...")
    result = client.get_languages(country="IN")

    if is_ok(result):
        languages = result.value.data
        print(f"   Found {len(languages)} languages in India\n")

        for lang in languages[:10]:
            # Get display name in English if available
            display_name = lang.display_names.get("en", lang.id)
            print(f"   {lang.id:<10} - {display_name}")
            if lang.scripts:
                print(f"              Scripts: {', '.join(lang.scripts)}")
    else:
        print(f"   Error: {result.error}")

    # 3. Get a specific language by BCP 47 tag
    print("\n" + "=" * 60)
    print("\n3. Getting details for Spanish (es)...")
    result = client.get_language("es")

    if is_ok(result):
        lang = result.value
        print(f"""
   Language ID:        {lang.id}
   ISO 639 Code:       {lang.language}
   Text Direction:     {lang.text_direction}
   Script:             {lang.script or 'N/A'} ({lang.script_name or 'N/A'})

   Available Scripts:  {', '.join(lang.scripts) if lang.scripts else 'N/A'}
   Variants:           {', '.join(lang.variants) if lang.variants else 'N/A'}
   Countries:          {', '.join(lang.countries[:5]) if lang.countries else 'N/A'}{'...' if len(lang.countries) > 5 else ''}
   Aliases:            {', '.join(lang.aliases) if lang.aliases else 'N/A'}

   Writing Population: {lang.writing_population:,}
   Speaking Population:{lang.speaking_population:,}
   Default Bible ID:   {lang.default_bible_id or 'N/A'}
""")

        if lang.display_names:
            print("   Display Names:")
            for code, name in list(lang.display_names.items())[:5]:
                print(f"      {code}: {name}")
    else:
        print(f"   Error: {result.error}")

    # 4. Try a language that doesn't exist
    print("\n" + "=" * 60)
    print("\n4. Trying to get a non-existent language...")
    result = client.get_language("xyz-invalid")

    if is_err(result):
        error = result.error
        print(f"   Expected error: {error.resource} '{error.identifier}' not found")
        print(f"   Message: {error.message}")
    else:
        print("   Unexpectedly found the language!")

print("\n" + "=" * 60)
print("Languages API example complete!")
print("=" * 60)
