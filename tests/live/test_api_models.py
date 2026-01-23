"""Live API tests to validate models against real API responses.

Run with: uv run pytest tests/live -m live -v
"""

from __future__ import annotations

import os

import pytest

from youversion import YouVersionClient
from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core.result import is_ok, is_err

pytestmark = pytest.mark.live

# ASV (American Standard Version) - a version commonly available with API keys
TEST_VERSION_ID = 12


@pytest.fixture(scope="module")
def api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("YOUVERSION_API_KEY")
    if not key:
        pytest.skip("YOUVERSION_API_KEY not set")
    return key


@pytest.fixture(scope="module")
def client(api_key: str) -> YouVersionClient:
    """Create a client for testing."""
    with YouVersionClient(api_key) as c:
        yield c


class TestBibleVersions:
    """Test Bible version endpoints and models."""

    def test_get_versions(self, client: YouVersionClient) -> None:
        """Test fetching versions for English."""
        result = client.get_versions("en")
        assert is_ok(result), f"Failed: {result}"

        response = result.value
        assert isinstance(response, PaginatedResponse)
        assert len(response.data) > 0, "Expected at least one English version"

        version = response.data[0]
        assert isinstance(version, BibleVersion)
        assert version.id > 0
        assert version.abbreviation
        assert version.title
        assert version.language_tag

        print(f"\n  Found {len(response.data)} English versions")
        print(f"  Sample: {version.abbreviation} - {version.title}")

    def test_get_version_by_id(self, client: YouVersionClient) -> None:
        """Test fetching a specific version (ASV = 12)."""
        result = client.get_version(TEST_VERSION_ID)
        assert is_ok(result), f"Failed: {result}"

        version = result.value
        assert isinstance(version, BibleVersion)
        assert version.id == TEST_VERSION_ID
        assert version.abbreviation
        print(f"\n  Version: {version.abbreviation} - {version.title}")

    def test_get_version_not_found(self, client: YouVersionClient) -> None:
        """Test 404 handling for non-existent version."""
        result = client.get_version(999999)
        assert is_err(result), "Expected not found error"
        print(f"\n  Correctly returned error: {result.error}")


class TestBibleBooks:
    """Test Bible book endpoints and models."""

    def test_get_books(self, client: YouVersionClient) -> None:
        """Test fetching all books for ASV."""
        result = client.get_books(TEST_VERSION_ID)
        assert is_ok(result), f"Failed: {result}"

        response = result.value
        assert isinstance(response, PaginatedResponse)
        assert len(response.data) >= 66, "Expected at least 66 books"

        book = response.data[0]
        assert isinstance(book, BibleBook)
        assert book.id
        assert book.title
        assert book.abbreviation
        assert book.canon in ("old_testament", "new_testament", "deuterocanon")

        print(f"\n  Found {len(response.data)} books")
        print(f"  First book: {book.title} ({book.id})")

    def test_get_book_genesis(self, client: YouVersionClient) -> None:
        """Test fetching Genesis specifically."""
        result = client.get_book(TEST_VERSION_ID, "GEN")
        assert is_ok(result), f"Failed: {result}"

        book = result.value
        assert isinstance(book, BibleBook)
        assert book.id == "GEN"
        assert book.canon == "old_testament"
        print(f"\n  Book: {book.title} ({book.abbreviation})")

    def test_get_book_matthew(self, client: YouVersionClient) -> None:
        """Test fetching Matthew (New Testament)."""
        result = client.get_book(TEST_VERSION_ID, "MAT")
        assert is_ok(result), f"Failed: {result}"

        book = result.value
        assert book.canon == "new_testament"
        print(f"\n  Book: {book.title} - Canon: {book.canon}")


class TestBibleChapters:
    """Test Bible chapter endpoints and models."""

    def test_get_chapters(self, client: YouVersionClient) -> None:
        """Test fetching chapters for Genesis."""
        result = client.get_chapters(TEST_VERSION_ID, "GEN")
        assert is_ok(result), f"Failed: {result}"

        response = result.value
        assert isinstance(response, PaginatedResponse)
        assert len(response.data) == 50, f"Genesis has 50 chapters, got {len(response.data)}"

        chapter = response.data[0]
        assert isinstance(chapter, BibleChapter)
        assert chapter.id
        assert chapter.title

        print(f"\n  Found {len(response.data)} chapters")
        print(f"  First chapter: {chapter.title}")

    def test_get_chapter(self, client: YouVersionClient) -> None:
        """Test fetching a specific chapter."""
        result = client.get_chapter(TEST_VERSION_ID, "GEN", 1)
        assert is_ok(result), f"Failed: {result}"

        chapter = result.value
        assert isinstance(chapter, BibleChapter)
        print(f"\n  Chapter: {chapter.title} (ID: {chapter.id})")


class TestBibleVerses:
    """Test Bible verse endpoints and models."""

    def test_get_verses(self, client: YouVersionClient) -> None:
        """Test fetching verses for Genesis 1."""
        result = client.get_verses(TEST_VERSION_ID, "GEN", 1)
        assert is_ok(result), f"Failed: {result}"

        response = result.value
        assert isinstance(response, PaginatedResponse)
        assert len(response.data) == 31, f"Genesis 1 has 31 verses, got {len(response.data)}"

        verse = response.data[0]
        assert isinstance(verse, BibleVerse)
        assert verse.id
        assert verse.title

        print(f"\n  Found {len(response.data)} verses")
        print(f"  First verse: {verse.title}")

    def test_get_verse(self, client: YouVersionClient) -> None:
        """Test fetching a specific verse."""
        result = client.get_verse(TEST_VERSION_ID, "GEN", 1, 1)
        assert is_ok(result), f"Failed: {result}"

        verse = result.value
        assert isinstance(verse, BibleVerse)
        print(f"\n  Verse: {verse.title} (ID: {verse.id})")


class TestBiblePassages:
    """Test Bible passage endpoints and models."""

    def test_get_passage_single_verse(self, client: YouVersionClient) -> None:
        """Test fetching John 3:16."""
        result = client.get_passage(TEST_VERSION_ID, "JHN.3.16")
        assert is_ok(result), f"Failed: {result}"

        passage = result.value
        assert isinstance(passage, BiblePassage)
        assert passage.id
        assert passage.content
        assert passage.reference

        print(f"\n  Reference: {passage.reference}")
        print(f"  Content: {passage.content[:100]}...")

    def test_get_passage_range(self, client: YouVersionClient) -> None:
        """Test fetching a verse range."""
        result = client.get_passage(TEST_VERSION_ID, "GEN.1.1-3")
        assert is_ok(result), f"Failed: {result}"

        passage = result.value
        assert passage.content
        print(f"\n  Reference: {passage.reference}")
        print(f"  Content length: {len(passage.content)} chars")

    def test_get_passage_html_format(self, client: YouVersionClient) -> None:
        """Test fetching passage in HTML format."""
        result = client.get_passage(TEST_VERSION_ID, "JHN.3.16", format="html")
        assert is_ok(result), f"Failed: {result}"

        passage = result.value
        assert "<" in passage.content, "Expected HTML tags in content"
        print(f"\n  HTML content: {passage.content[:150]}...")

    def test_get_passage_not_found(self, client: YouVersionClient) -> None:
        """Test 404 handling for invalid passage."""
        result = client.get_passage(TEST_VERSION_ID, "INVALID.1.1")
        assert is_err(result), "Expected not found error"
        print(f"\n  Correctly returned error: {result.error}")
