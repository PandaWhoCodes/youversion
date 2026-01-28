"""Tests for AsyncYouVersionClient."""

import json
from pathlib import Path

import pytest
import respx

from youversion.core.client import AsyncYouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestAsyncYouVersionClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_versions(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            json=load_fixture("versions.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_versions("en")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2
        assert result.value.data[0].abbreviation == "NIV"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_version(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json=load_fixture("version_111.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_version(111)

        assert isinstance(result, Ok)
        assert result.value.id == 111
        assert result.value.abbreviation == "NIV"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_version_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/999").respond(
            status_code=404, json={"error": "not_found"}
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_version(999)

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)
        assert result.error.resource == "version"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_books(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books").respond(
            json=load_fixture("books.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_books(111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_book(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN").respond(
            json=load_fixture("book_jhn.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_book(111, "JHN")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN"
        assert result.value.chapters is not None
        assert len(result.value.chapters) == 3

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_chapter(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN/chapters/3").respond(
            json=load_fixture("chapter_jhn3.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_chapter(111, "JHN", 3)

        assert isinstance(result, Ok)
        assert result.value.id == "3"
        assert result.value.verses is not None
        assert len(result.value.verses) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_passage(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/passages/JHN.3.16").respond(
            json=load_fixture("passage_jhn316.json")
        )
        async with AsyncYouVersionClient(api_key="test-key") as client:
            result = await client.get_passage(111, "JHN.3.16")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN.3.16"
        assert "God so loved" in result.value.content
