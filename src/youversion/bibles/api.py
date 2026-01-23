"""Bible API implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.core.domain_errors import NotFoundError, ValidationError
from youversion.core.result import Err, Ok, Result

if TYPE_CHECKING:
    from youversion.core.http import SyncHTTPAdapter


class BibleAPIMixin:
    """Mixin providing Bible API methods."""

    def _get_versions(
        self,
        http: SyncHTTPAdapter,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    def _get_version(
        self, http: SyncHTTPAdapter, bible_id: int
    ) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    def _get_books(
        self, http: SyncHTTPAdapter, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = http.get(f"/v1/bibles/{version_id}/books")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(version_id),
                    message=f"Bible version {version_id} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleBook].model_validate(data))

    def _get_book(
        self, http: SyncHTTPAdapter, version_id: int, book: str
    ) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    def _get_chapters(
        self, http: SyncHTTPAdapter, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleChapter].model_validate(data))

    def _get_chapter(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    def _get_verses(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVerse].model_validate(data))

    def _get_verse(
        self, http: SyncHTTPAdapter, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses/{verse}"
        )

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="verse",
                    identifier=f"{book}.{chapter}.{verse}",
                    message=f"Verse {book} {chapter}:{verse} not found",
                )
            )

        return Ok(BibleVerse.model_validate(response.json()))

    def _get_passage(
        self,
        http: SyncHTTPAdapter,
        version_id: int,
        usfm: str,
        format: Literal["text", "html"] = "text",
        include_headings: bool = False,
        include_notes: bool = False,
    ) -> Result[BiblePassage, NotFoundError | ValidationError]:
        """Get passage content."""
        params: dict[str, Any] = {
            "format": format,
            "include_headings": str(include_headings).lower(),
            "include_notes": str(include_notes).lower(),
        }
        response = http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="passage",
                    identifier=usfm,
                    message=f"Passage {usfm} not found",
                )
            )

        if response.status_code == 400:
            return Err(ValidationError(field="usfm", reason="Invalid USFM format"))

        return Ok(BiblePassage.model_validate(response.json()))
