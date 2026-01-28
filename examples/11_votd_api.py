#!/usr/bin/env python3
"""Verse of the Day API - get daily scripture passages.

This example demonstrates how to:
1. Get all verses of the day (1-366)
2. Get the verse for a specific day of the year
3. Handle validation errors for invalid day numbers
4. Combine with passages API to get full text

Usage:
    export YOUVERSION_API_KEY="your-api-key"
    python examples/11_votd_api.py
"""

import os
from datetime import datetime

from youversion import YouVersionClient, is_err, is_ok

API_KEY = os.environ.get("YOUVERSION_API_KEY")

if not API_KEY:
    print("Please set YOUVERSION_API_KEY environment variable")
    exit(1)

print("=" * 60)
print("Example: Verse of the Day API")
print("=" * 60)

# Get today's day of year (1-366)
today = datetime.now()
day_of_year = today.timetuple().tm_yday

with YouVersionClient(API_KEY) as client:
    # 1. Get today's verse of the day
    print(f"\n1. Getting today's verse (Day {day_of_year} of {today.year})...")
    result = client.get_votd(day_of_year)

    if is_ok(result):
        votd = result.value
        print(f"   Day:        {votd.day}")
        print(f"   Passage ID: {votd.passage_id}")

        # Fetch the actual passage text
        print(f"\n   Fetching passage text (NIV)...")
        passage_result = client.get_passage(111, votd.passage_id)  # 111 = NIV

        if is_ok(passage_result):
            passage = passage_result.value
            print(f"\n   {passage.reference}:")
            print(f"   {'-' * 40}")
            # Clean up the text for display
            text = passage.content or ""
            # Wrap text at ~60 chars
            words = text.split()
            line = "   "
            for word in words:
                if len(line) + len(word) > 65:
                    print(line)
                    line = "   " + word
                else:
                    line += " " + word if line.strip() else word
            if line.strip():
                print(line)
        else:
            print(f"   Could not fetch passage: {passage_result.error}")
    else:
        print(f"   Error: {result.error}")

    # 2. Get verse for a specific day
    print("\n" + "=" * 60)
    print("\n2. Getting verse for Day 1 (January 1st)...")
    result = client.get_votd(1)

    if is_ok(result):
        votd = result.value
        print(f"   Day 1 passage: {votd.passage_id}")
    else:
        print(f"   Error: {result.error}")

    # 3. Get verse for last day of year
    print("\n" + "=" * 60)
    print("\n3. Getting verse for Day 365...")
    result = client.get_votd(365)

    if is_ok(result):
        votd = result.value
        print(f"   Day 365 passage: {votd.passage_id}")
    else:
        print(f"   Error: {result.error}")

    # 4. Get all VOTD entries
    print("\n" + "=" * 60)
    print("\n4. Getting all verses of the day...")
    result = client.get_all_votd()

    if is_ok(result):
        all_votd = result.value.data
        print(f"   Total VOTD entries: {len(all_votd)}")

        # Show a sample
        print("\n   Sample entries:")
        print("   " + "-" * 40)
        for votd in all_votd[:5]:
            print(f"   Day {votd.day:>3}: {votd.passage_id}")
        print("   ...")
        for votd in all_votd[-3:]:
            print(f"   Day {votd.day:>3}: {votd.passage_id}")
    else:
        print(f"   Error: {result.error}")

    # 5. Handle invalid day number
    print("\n" + "=" * 60)
    print("\n5. Trying invalid day number (999)...")
    result = client.get_votd(999)

    if is_err(result):
        error = result.error
        print(f"   Expected validation error:")
        print(f"   Field: {error.field}")
        print(f"   Reason: {error.reason}")
    else:
        print("   Unexpectedly got a result!")

    # 6. Practical example: Build a week's worth of VOTD
    print("\n" + "=" * 60)
    print("\n6. Building this week's verses of the day...")

    week_start = day_of_year
    print(f"\n   Week starting Day {week_start}:")
    print("   " + "-" * 40)

    for i in range(7):
        day = week_start + i
        if day > 366:
            day = day - 366  # Wrap around

        result = client.get_votd(day)
        if is_ok(result):
            votd = result.value
            print(f"   Day {day:>3}: {votd.passage_id}")
        else:
            print(f"   Day {day:>3}: (error)")

print("\n" + "=" * 60)
print("Verse of the Day API example complete!")
print("=" * 60)
