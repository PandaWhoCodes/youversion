#!/usr/bin/env python3
"""Licenses API - check Bible licensing information.

This example demonstrates how to:
1. Get license information for a specific Bible
2. Check if you have agreed to a license
3. Get all available licenses for a Bible

Note: The Licenses API requires:
- Your API key
- Your developer ID (UUID from the Platform Portal)
- A bible_id to check licenses for

Usage:
    export YOUVERSION_API_KEY="your-api-key"
    export YOUVERSION_DEVELOPER_ID="your-developer-uuid"
    python examples/12_licenses_api.py
"""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ.get("YOUVERSION_API_KEY")
DEVELOPER_ID = os.environ.get("YOUVERSION_DEVELOPER_ID")

if not API_KEY:
    print("Please set YOUVERSION_API_KEY environment variable")
    exit(1)

if not DEVELOPER_ID:
    print("Please set YOUVERSION_DEVELOPER_ID environment variable")
    print("Get your developer ID from: https://developers.youversion.com")
    exit(1)

print("=" * 60)
print("Example: Licenses API")
print("=" * 60)

# Common Bible IDs for testing
NIV_BIBLE_ID = 111
KJV_BIBLE_ID = 1

with YouVersionClient(API_KEY) as client:
    # 1. Get licenses for NIV Bible
    print(f"\n1. Getting licenses for Bible ID {NIV_BIBLE_ID} (NIV)...")
    result = client.get_licenses(bible_id=NIV_BIBLE_ID, developer_id=DEVELOPER_ID)

    if is_ok(result):
        licenses = result.value.data
        print(f"   Found {len(licenses)} license(s)\n")

        for lic in licenses:
            print(f"   License: {lic.name}")
            print(f"   ID:      {lic.id}")
            print(f"   Version: {lic.version}")
            print(f"   Org ID:  {lic.organization_id}")

            if lic.uri:
                print(f"   URI:     {lic.uri}")

            if lic.agreed_dt:
                print(f"   Agreed:  {lic.agreed_dt}")
            else:
                print("   Agreed:  Not yet agreed")

            print(f"   Covers {len(lic.bible_ids)} Bible(s): {lic.bible_ids[:5]}...")
            print()

            # Show license HTML preview (first 200 chars)
            if lic.html:
                preview = lic.html[:200].replace("\n", " ")
                print(f"   License text preview:")
                print(f"   {preview}...")
            print()
    else:
        print(f"   Error: {result.error}")
        print("   Note: You may need to register your app for this Bible")

    # 2. Get licenses for KJV (typically public domain)
    print("=" * 60)
    print(f"\n2. Getting licenses for Bible ID {KJV_BIBLE_ID} (KJV)...")
    result = client.get_licenses(bible_id=KJV_BIBLE_ID, developer_id=DEVELOPER_ID)

    if is_ok(result):
        licenses = result.value.data
        print(f"   Found {len(licenses)} license(s)")

        for lic in licenses:
            print(f"   - {lic.name} (v{lic.version})")
    else:
        print(f"   Error: {result.error}")

    # 3. Get all available licenses (including those not agreed to)
    print("\n" + "=" * 60)
    print(f"\n3. Getting all available licenses for Bible ID {NIV_BIBLE_ID}...")
    result = client.get_licenses(
        bible_id=NIV_BIBLE_ID, developer_id=DEVELOPER_ID, all_available=True
    )

    if is_ok(result):
        licenses = result.value.data
        print(f"   Found {len(licenses)} available license(s)")

        for lic in licenses:
            status = "Agreed" if lic.agreed_dt else "Not agreed"
            print(f"   - {lic.name}: {status}")
    else:
        print(f"   Error: {result.error}")

print("\n" + "=" * 60)
print("Licenses API example complete!")
print("=" * 60)
print("\nNote: To agree to licenses, visit:")
print("https://developers.youversion.com/apps")
