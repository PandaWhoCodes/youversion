#!/usr/bin/env python3
"""Organizations API - explore Bible publishers and their translations.

This example demonstrates how to:
1. Get organizations that publish a specific Bible version
2. Get details for a specific organization
3. Get all Bibles published by an organization
4. Use Accept-Language header for localized responses

Usage:
    export YOUVERSION_API_KEY="your-api-key"
    python examples/10_organizations_api.py
"""

import os

from youversion import YouVersionClient, is_err, is_ok

API_KEY = os.environ.get("YOUVERSION_API_KEY")

if not API_KEY:
    print("Please set YOUVERSION_API_KEY environment variable")
    exit(1)

print("=" * 60)
print("Example: Organizations API")
print("=" * 60)

# NIV Bible ID for example
NIV_BIBLE_ID = 111

with YouVersionClient(API_KEY) as client:
    # 1. Get organizations for a Bible version
    print(f"\n1. Getting organizations for Bible ID {NIV_BIBLE_ID} (NIV)...")
    result = client.get_organizations(bible_id=NIV_BIBLE_ID)

    org_id = None
    if is_ok(result):
        orgs = result.value.data
        print(f"   Found {len(orgs)} organization(s)\n")

        for org in orgs:
            org_id = org.id  # Save for later
            print(f"   Organization: {org.name}")
            print(f"   ID:           {org.id}")
            if org.description:
                desc = org.description
                if len(desc) > 80:
                    desc = desc[:80] + "..."
                print(f"   Description:  {desc}")
            print(f"   Website:      {org.website_url}")
            print(f"   Language:     {org.primary_language}")
            if org.email:
                print(f"   Email:        {org.email}")
            print()

            # Show address if available
            if org.address:
                addr = org.address
                print(f"   Address:      {addr.formatted_address}")
                print(f"   Location:     {addr.locality}, {addr.country}")
                print(f"   Coordinates:  ({addr.latitude}, {addr.longitude})")
            print()
    else:
        print(f"   Error: {result.error}")

    # 2. Get organizations with Spanish localization
    print("=" * 60)
    print("\n2. Getting organizations in Spanish (Accept-Language: es)...")
    result = client.get_organizations(bible_id=NIV_BIBLE_ID, accept_language="es")

    if is_ok(result):
        orgs = result.value.data
        for org in orgs:
            print(f"   Organization: {org.name}")
            print(f"   Description:  {org.description[:100]}...")
            print()
    else:
        print(f"   Error: {result.error}")

    # 3. Get specific organization details
    if org_id:
        print("=" * 60)
        print("\n3. Getting organization details by ID...")
        print(f"   ID: {org_id}")
        result = client.get_organization(org_id)

        if is_ok(result):
            org = result.value
            print(f"\n   Name:         {org.name}")
            print(f"   Website:      {org.website_url}")
            if org.phone:
                print(f"   Phone:        {org.phone}")
            if org.parent_organization_id:
                print(f"   Parent Org:   {org.parent_organization_id}")
        else:
            print(f"   Error: {result.error}")

    # 4. Get Bibles from an organization
    if org_id:
        print("\n" + "=" * 60)
        print("\n4. Getting Bibles published by this organization...")
        result = client.get_organization_bibles(org_id)

        if is_ok(result):
            bibles = result.value.data
            print(f"   Found {len(bibles)} Bible(s)\n")

            for bible in bibles[:10]:
                print(f"   [{bible.id:>4}] {bible.abbreviation:<10} - {bible.title}")
            if len(bibles) > 10:
                print(f"   ... and {len(bibles) - 10} more")
        else:
            print(f"   Error: {result.error}")

    # 5. Try a non-existent organization
    print("\n" + "=" * 60)
    print("\n5. Trying to get a non-existent organization...")
    from youversion import ServerError
    try:
        result = client.get_organization("00000000-0000-0000-0000-000000000000")
        if is_err(result):
            error = result.error
            print(f"   Expected error: {error.resource} not found")
            print(f"   Message: {error.message}")
        else:
            print("   Unexpectedly found the organization!")
    except ServerError as e:
        print("   Server returned error (API returns 500 for invalid UUIDs)")
        print(f"   Error: {e}")

print("\n" + "=" * 60)
print("Organizations API example complete!")
print("=" * 60)
