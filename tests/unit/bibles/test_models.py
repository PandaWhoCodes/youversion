"""Tests for Bible models."""

from youversion.bibles.models import (
    BibleBook,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)


def test_bible_version_from_api_response() -> None:
    data = {
        "id": 111,
        "abbreviation": "NIV",
        "title": "New International Version",
        "language_tag": "en",
        "copyright_short": "© Biblica",
        "copyright_long": "New International Version®, NIV® Copyright © 1973...",
    }
    version = BibleVersion.model_validate(data)
    assert version.id == 111
    assert version.abbreviation == "NIV"
    assert version.language_tag == "en"


def test_bible_version_optional_fields() -> None:
    data = {
        "id": 1,
        "abbreviation": "KJV",
        "title": "King James Version",
        "language_tag": "en",
    }
    version = BibleVersion.model_validate(data)
    assert version.copyright_short is None
    assert version.copyright_long is None


def test_bible_book_from_api_response() -> None:
    data = {
        "id": "GEN",
        "title": "Genesis",
        "abbreviation": "Gen",
        "canon": "old_testament",
    }
    book = BibleBook.model_validate(data)
    assert book.id == "GEN"
    assert book.canon == "old_testament"


def test_bible_book_with_chapters() -> None:
    data = {
        "id": "MAT",
        "title": "Matthew",
        "abbreviation": "Matt",
        "canon": "new_testament",
        "chapters": [
            {"id": "1", "passage_id": "MAT.1", "title": "1"},
        ],
    }
    book = BibleBook.model_validate(data)
    assert book.chapters is not None
    assert len(book.chapters) == 1


def test_bible_chapter_from_api_response() -> None:
    data = {
        "id": "3",
        "passage_id": "JHN.3",
        "title": "3",
    }
    chapter = BibleChapter.model_validate(data)
    assert chapter.id == "3"
    assert chapter.passage_id == "JHN.3"


def test_bible_verse_from_api_response() -> None:
    data = {
        "id": "16",
        "passage_id": "JHN.3.16",
        "title": "16",
    }
    verse = BibleVerse.model_validate(data)
    assert verse.id == "16"
    assert verse.passage_id == "JHN.3.16"


def test_bible_passage_from_api_response() -> None:
    data = {
        "id": "JHN.3.16",
        "content": "For God so loved the world...",
        "reference": "John 3:16",
    }
    passage = BiblePassage.model_validate(data)
    assert passage.id == "JHN.3.16"
    assert "God so loved" in passage.content


def test_paginated_response_with_versions() -> None:
    data = {
        "data": [
            {"id": 1, "abbreviation": "NIV", "title": "NIV", "language_tag": "en"},
            {"id": 2, "abbreviation": "ESV", "title": "ESV", "language_tag": "en"},
        ],
        "next_page_token": "abc123",
        "total_count": 100,
    }
    response = PaginatedResponse[BibleVersion].model_validate(data)
    assert len(response.data) == 2
    assert response.next_page_token == "abc123"
    assert response.total_count == 100


def test_paginated_response_no_next_page() -> None:
    data = {
        "data": [{"id": 1, "abbreviation": "NIV", "title": "NIV", "language_tag": "en"}],
    }
    response = PaginatedResponse[BibleVersion].model_validate(data)
    assert response.next_page_token is None
    assert response.total_count is None
