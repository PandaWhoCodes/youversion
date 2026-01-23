#!/usr/bin/env python3
"""Async client usage - using the async-first API."""

import asyncio
import os

from youversion import AsyncYouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 7: Async Client Usage")
print("=" * 60)


async def main() -> None:
    # Using context manager (recommended)
    async with AsyncYouVersionClient(api_key=API_KEY) as client:
        # Get Bible versions
        result = await client.get_versions("en")
        if is_ok(result):
            print(f"\nFound {len(result.value.data)} English versions")
            for v in result.value.data[:3]:
                print(f"  [{v.id:>4}] {v.abbreviation}")

        # Get a passage
        result = await client.get_passage(12, "JHN.3.16")
        if is_ok(result):
            print(f"\n{result.value.reference}:")
            print(f"  {result.value.content}")

    print("\n--- Manual client management ---")

    # Without context manager
    client = AsyncYouVersionClient(api_key=API_KEY)
    try:
        result = await client.get_book(12, "PSA")
        if is_ok(result):
            print(f"\nBook: {result.value.title}")
            print(f"  Chapters: {len(result.value.chapters) if result.value.chapters else 'N/A'}")
    finally:
        await client.close()
        print("\nAsync client closed.")


if __name__ == "__main__":
    asyncio.run(main())
