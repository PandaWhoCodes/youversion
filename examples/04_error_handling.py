#!/usr/bin/env python3
"""Proper error handling with Result types."""

import os

from youversion import (
    Err,
    NotFoundError,
    Ok,
    YouVersionClient,
    is_err,
    is_ok,
)

API_KEY = os.environ["YOUVERSION_API_KEY"]

print("=" * 60)
print("Example 4: Error Handling")
print("=" * 60)

with YouVersionClient(API_KEY) as client:
    # Example 1: Handle not found error
    print("\n--- Requesting non-existent version ---")
    result = client.get_version(99999)

    if is_ok(result):
        print(f"Found: {result.value.title}")
    else:
        error = result.error
        print(f"Error type: {type(error).__name__}")
        if isinstance(error, NotFoundError):
            print(f"  Resource: {error.resource}")
            print(f"  Identifier: {error.identifier}")
            print(f"  Message: {error.message}")

    # Example 2: Handle non-existent book
    print("\n--- Requesting non-existent book ---")
    result = client.get_book(12, "INVALID")

    if is_err(result):
        error = result.error
        print(f"Error: {error.message}")

    # Example 3: Pattern matching with match/case
    print("\n--- Pattern matching on result ---")
    result = client.get_version(12)

    match result:
        case Ok(value):
            print(f"Success: {value.title}")
        case Err(error):
            print(f"Failed: {error.message}")
