"""YouVersion SDK clients."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from youversion.bibles.api import BibleAPIMixin
from youversion.core.http import AsyncHTTPAdapter, SyncHTTPAdapter

if TYPE_CHECKING:
    from youversion.bibles.models import (
        BibleBook,
        BibleChapter,
        BiblePassage,
        BibleVerse,
        BibleVersion,
        PaginatedResponse,
    )
    from youversion.core.domain_errors import NotFoundError, ValidationError
    from youversion.core.result import Result

DEFAULT_BASE_URL = "https://api.youversion.com"
DEFAULT_TIMEOUT = 30.0


class YouVersionClient(BibleAPIMixin):
    """Synchronous YouVersion API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = SyncHTTPAdapter(api_key=api_key, base_url=base_url, timeout=timeout)

    def __enter__(self) -> YouVersionClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    # Version methods
    def get_versions(
        self, language_ranges: str, license_id: str | int | None = None
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        return self._get_versions(self._http, language_ranges, license_id)

    def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        return self._get_version(self._http, bible_id)

    # Book methods
    def get_books(self, version_id: int) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        return self._get_books(self._http, version_id)

    def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        return self._get_book(self._http, version_id, book)

    # Chapter methods
    def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        return self._get_chapters(self._http, version_id, book)

    def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        return self._get_chapter(self._http, version_id, book, chapter)

    # Verse methods
    def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        return self._get_verses(self._http, version_id, book, chapter)

    def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        return self._get_verse(self._http, version_id, book, chapter, verse)

    # Passage methods
    def get_passage(
        self,
        version_id: int,
        usfm: str,
        *,
        format: Literal["text", "html"] = "text",
        include_headings: bool = False,
        include_notes: bool = False,
    ) -> Result[BiblePassage, NotFoundError | ValidationError]:
        """Get passage content."""
        return self._get_passage(
            self._http, version_id, usfm, format, include_headings, include_notes
        )


class AsyncYouVersionClient(BibleAPIMixin):
    """Asynchronous YouVersion API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = AsyncHTTPAdapter(api_key=api_key, base_url=base_url, timeout=timeout)

    async def __aenter__(self) -> AsyncYouVersionClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    # Async versions will be implemented in a follow-up task
