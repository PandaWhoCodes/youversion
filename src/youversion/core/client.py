"""YouVersion SDK clients."""

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
from youversion.languages.models import Language
from youversion.licenses.models import License
from youversion.core.http import AsyncHTTPAdapter, SyncHTTPAdapter
from youversion.core.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

DEFAULT_BASE_URL = "https://api.youversion.com"
DEFAULT_TIMEOUT = 30.0


class YouVersionClient:
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
        self,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = self._http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = self._http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    # Book methods
    def get_books(
        self, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = self._http.get(f"/v1/bibles/{version_id}/books")

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

    def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    # Chapter methods
    def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

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

    def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    # Verse methods
    def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses"
        )

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

    def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = self._http.get(
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
        params: dict[str, Any] = {
            "format": format,
            "include_headings": str(include_headings).lower(),
            "include_notes": str(include_notes).lower(),
        }
        response = self._http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

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

    # Language methods
    def get_languages(
        self,
        *,
        country: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> Result[PaginatedResponse[Language], None]:
        """Get available languages."""
        params: dict[str, Any] = {}
        if country is not None:
            params["country"] = country
        if page_size is not None:
            params["page_size"] = page_size
        if page_token is not None:
            params["page_token"] = page_token

        response = self._http.get("/v1/languages", params=params if params else None)
        data = response.json()
        return Ok(PaginatedResponse[Language].model_validate(data))

    def get_language(self, language_id: str) -> Result[Language, NotFoundError]:
        """Get a specific language by BCP 47 tag."""
        response = self._http.get(f"/v1/languages/{language_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="language",
                    identifier=language_id,
                    message=f"Language {language_id} not found",
                )
            )

        return Ok(Language.model_validate(response.json()))

    # License methods
    def get_licenses(
        self,
        bible_id: int,
        developer_id: str,
        *,
        all_available: bool = False,
    ) -> Result[PaginatedResponse[License], None]:
        """Get licenses for a Bible."""
        params: dict[str, Any] = {
            "bible_id": bible_id,
            "developer_id": developer_id,
        }
        if all_available:
            params["all_available"] = "true"

        response = self._http.get("/v1/licenses", params=params)
        data = response.json()
        return Ok(PaginatedResponse[License].model_validate(data))


class AsyncYouVersionClient:
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

    # Version methods
    async def get_versions(
        self,
        language_ranges: str,
        license_id: str | int | None = None,
    ) -> Result[PaginatedResponse[BibleVersion], ValidationError]:
        """Get Bible versions for a language."""
        params: dict[str, Any] = {"language_ranges[]": language_ranges}
        if license_id is not None:
            params["license_id"] = str(license_id)

        response = await self._http.get("/v1/bibles", params=params)

        if response.status_code == 400:
            return Err(
                ValidationError(field="language_ranges", reason="Invalid language range format")
            )

        data = response.json()
        return Ok(PaginatedResponse[BibleVersion].model_validate(data))

    async def get_version(self, bible_id: int) -> Result[BibleVersion, NotFoundError]:
        """Get a specific Bible version."""
        response = await self._http.get(f"/v1/bibles/{bible_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="version",
                    identifier=str(bible_id),
                    message=f"Bible version {bible_id} not found",
                )
            )

        return Ok(BibleVersion.model_validate(response.json()))

    # Book methods
    async def get_books(
        self, version_id: int
    ) -> Result[PaginatedResponse[BibleBook], NotFoundError]:
        """Get all books in a Bible version."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books")

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

    async def get_book(self, version_id: int, book: str) -> Result[BibleBook, NotFoundError]:
        """Get a specific book."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="book",
                    identifier=book,
                    message=f"Book {book} not found in version {version_id}",
                )
            )

        return Ok(BibleBook.model_validate(response.json()))

    # Chapter methods
    async def get_chapters(
        self, version_id: int, book: str
    ) -> Result[PaginatedResponse[BibleChapter], NotFoundError]:
        """Get all chapters in a book."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters")

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

    async def get_chapter(
        self, version_id: int, book: str, chapter: int
    ) -> Result[BibleChapter, NotFoundError]:
        """Get a specific chapter."""
        response = await self._http.get(f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="chapter",
                    identifier=f"{book}.{chapter}",
                    message=f"Chapter {book} {chapter} not found",
                )
            )

        return Ok(BibleChapter.model_validate(response.json()))

    # Verse methods
    async def get_verses(
        self, version_id: int, book: str, chapter: int
    ) -> Result[PaginatedResponse[BibleVerse], NotFoundError]:
        """Get all verses in a chapter."""
        response = await self._http.get(
            f"/v1/bibles/{version_id}/books/{book}/chapters/{chapter}/verses"
        )

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

    async def get_verse(
        self, version_id: int, book: str, chapter: int, verse: int
    ) -> Result[BibleVerse, NotFoundError]:
        """Get a specific verse."""
        response = await self._http.get(
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

    # Passage methods
    async def get_passage(
        self,
        version_id: int,
        usfm: str,
        *,
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
        response = await self._http.get(f"/v1/bibles/{version_id}/passages/{usfm}", params=params)

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

    # Language methods
    async def get_languages(
        self,
        *,
        country: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> Result[PaginatedResponse[Language], None]:
        """Get available languages."""
        params: dict[str, Any] = {}
        if country is not None:
            params["country"] = country
        if page_size is not None:
            params["page_size"] = page_size
        if page_token is not None:
            params["page_token"] = page_token

        response = await self._http.get("/v1/languages", params=params if params else None)
        data = response.json()
        return Ok(PaginatedResponse[Language].model_validate(data))

    async def get_language(self, language_id: str) -> Result[Language, NotFoundError]:
        """Get a specific language by BCP 47 tag."""
        response = await self._http.get(f"/v1/languages/{language_id}")

        if response.status_code == 404:
            return Err(
                NotFoundError(
                    resource="language",
                    identifier=language_id,
                    message=f"Language {language_id} not found",
                )
            )

        return Ok(Language.model_validate(response.json()))

    # License methods
    async def get_licenses(
        self,
        bible_id: int,
        developer_id: str,
        *,
        all_available: bool = False,
    ) -> Result[PaginatedResponse[License], None]:
        """Get licenses for a Bible."""
        params: dict[str, Any] = {
            "bible_id": bible_id,
            "developer_id": developer_id,
        }
        if all_available:
            params["all_available"] = "true"

        response = await self._http.get("/v1/licenses", params=params)
        data = response.json()
        return Ok(PaginatedResponse[License].model_validate(data))
