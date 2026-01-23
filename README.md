# YouVersion Python SDK

The un-official Python SDK for the YouVersion API. Access Bible versions, books, chapters, verses, and passages programmatically.

[![PyPI version](https://badge.fury.io/py/youversion.svg)](https://badge.fury.io/py/youversion)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)


## Getting Started

### 1. Get Your API Key

Request access to the YouVersion API at [platform.youversion.com/](https://platform.youversion.com/).

### 2. Install the SDK

```bash
pip install youversion
```

Or with uv:

```bash
uv add youversion
```

### 3. Initialize the Client

```python
from youversion import YouVersionClient

client = YouVersionClient(api_key="your-api-key")
```

### 4. Make Your First Request

```python
from youversion import YouVersionClient, is_ok

with YouVersionClient(api_key="your-api-key") as client:
    result = client.get_passage(12, "JHN.3.16")

    if is_ok(result):
        passage = result.value
        print(f"{passage.reference}")
        print(passage.content)
```

Output:
```
John 3:16
For God so loved the world, that he gave his only begotten Son,
that whosoever believeth on him should not perish, but have eternal life.
```

### 5. Display Copyright

When displaying Bible content, you must include the appropriate copyright notice:

```python
result = client.get_version(12)
if is_ok(result):
    version = result.value
    print(version.copyright_short)  # Display with content
```

---

## Installation

### pip

```bash
pip install youversion
```

### uv

```bash
uv add youversion
```

### Poetry

```bash
poetry add youversion
```

---

## Configuration

```python
from youversion import YouVersionClient

# Basic initialization
client = YouVersionClient(api_key="your-api-key")

# With custom settings
client = YouVersionClient(
    api_key="your-api-key",
    base_url="https://api.youversion.com",  # Default
    timeout=30.0,  # Request timeout in seconds
)

# Using context manager (recommended)
with YouVersionClient(api_key="your-api-key") as client:
    # Client automatically closes when done
    pass
```

### Environment Variables

```python
import os
from youversion import YouVersionClient

client = YouVersionClient(api_key=os.environ["YOUVERSION_API_KEY"])
```

---

## Sync vs Async Clients

The SDK provides both synchronous and asynchronous clients with identical APIs.

### Synchronous Client

Use `YouVersionClient` for synchronous code:

```python
from youversion import YouVersionClient, is_ok

# With context manager (recommended)
with YouVersionClient(api_key="your-api-key") as client:
    result = client.get_versions("en")
    if is_ok(result):
        for version in result.value.data:
            print(version.title)
```

### Asynchronous Client

Use `AsyncYouVersionClient` for async code:

```python
import asyncio
from youversion import AsyncYouVersionClient, is_ok

async def main():
    async with AsyncYouVersionClient(api_key="your-api-key") as client:
        result = await client.get_versions("en")
        if is_ok(result):
            for version in result.value.data:
                print(version.title)

asyncio.run(main())
```

---

## Manual Client Management

If you need more control over the client lifecycle, you can manage it manually instead of using context managers.

### Sync Client (Manual)

```python
from youversion import YouVersionClient, is_ok

client = YouVersionClient(api_key="your-api-key")

try:
    result = client.get_versions("en")
    if is_ok(result):
        print(f"Found {len(result.value.data)} versions")

    result = client.get_passage(12, "JHN.3.16")
    if is_ok(result):
        print(result.value.content)
finally:
    # Always close the client to release resources
    client.close()
```

### Async Client (Manual)

```python
import asyncio
from youversion import AsyncYouVersionClient, is_ok

async def main():
    client = AsyncYouVersionClient(api_key="your-api-key")

    try:
        result = await client.get_versions("en")
        if is_ok(result):
            print(f"Found {len(result.value.data)} versions")

        result = await client.get_passage(12, "JHN.3.16")
        if is_ok(result):
            print(result.value.content)
    finally:
        # Always close the client to release resources
        await client.close()

asyncio.run(main())
```

### When to Use Manual Management

- **Connection pooling**: Keep a client alive across multiple operations
- **Application lifecycle**: Initialize once at startup, close at shutdown
- **Custom resource management**: Integration with dependency injection or frameworks

---

## Documentation

- [API Reference](docs/api.md) - Complete API documentation with all methods, types, and error handling