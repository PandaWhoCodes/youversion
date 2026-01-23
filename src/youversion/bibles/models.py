"""Bible domain models."""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response from API."""

    data: list[T]
    next_page_token: str | None = None
    total_count: int | None = None


class BibleVersion(BaseModel, frozen=True):
    """Bible translation/version."""

    id: int
    abbreviation: str
    title: str
    language_tag: str
    copyright_short: str | None = None
    copyright_long: str | None = None


class BibleBookIntro(BaseModel, frozen=True):
    """Introductory content for a book."""

    id: str
    passage_id: str
    title: str


class BibleVerse(BaseModel, frozen=True):
    """Verse metadata."""

    id: str
    passage_id: str
    title: str


class BibleChapter(BaseModel, frozen=True):
    """Chapter within a book."""

    id: str
    passage_id: str
    title: str
    verses: list[BibleVerse] | None = None


class BibleBook(BaseModel, frozen=True):
    """Book within a Bible version."""

    id: str  # USFM identifier (e.g., "GEN", "MAT")
    title: str
    full_title: str | None = None
    abbreviation: str
    canon: Literal["old_testament", "new_testament", "deuterocanon"]
    chapters: list[BibleChapter] | None = None
    intro: BibleBookIntro | None = None


class BiblePassage(BaseModel, frozen=True):
    """Actual passage content."""

    id: str  # USFM reference
    content: str
    reference: str  # Human-readable (e.g., "John 3:16")
