#!/usr/bin/env python3
"""Browse Bible structure - versions, books, chapters."""

import os

from youversion import YouVersionClient, is_ok

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 2: Browsing Bible Structure")
print("=" * 60)

with YouVersionClient(API_KEY) as client:
    # Get ASV (American Standard Version) - public domain
    VERSION_ID = 12

    result = client.get_version(VERSION_ID)
    if is_ok(result):
        version = result.value
        print(f"\nBible Version: {version.title} ({version.abbreviation})")
        print(f"Language: {version.language_tag}")

    # Get all books
    result = client.get_books(VERSION_ID)
    if is_ok(result):
        books = result.value

        # Separate by canon
        ot_books = [b for b in books.data if b.canon == "old_testament"]
        nt_books = [b for b in books.data if b.canon == "new_testament"]

        print(f"\nOld Testament: {len(ot_books)} books")
        print(f"  First: {ot_books[0].title}, Last: {ot_books[-1].title}")

        print(f"\nNew Testament: {len(nt_books)} books")
        print(f"  First: {nt_books[0].title}, Last: {nt_books[-1].title}")

    # Get details for a specific book
    result = client.get_book(VERSION_ID, "PSA")
    if is_ok(result):
        book = result.value
        print(f"\nBook Details: {book.title}")
        print(f"  ID: {book.id}")
        print(f"  Abbreviation: {book.abbreviation}")
        print(f"  Chapters: {len(book.chapters) if book.chapters else 0}")
