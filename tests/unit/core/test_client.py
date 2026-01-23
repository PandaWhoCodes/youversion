"""Tests for YouVersionClient."""

import json
from pathlib import Path

import respx

from youversion.core.client import YouVersionClient
from youversion.core.result import Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestYouVersionClient:
    def test_creates_with_api_key(self) -> None:
        client = YouVersionClient(api_key="test-key")
        assert client._http._api_key == "test-key"

    def test_custom_base_url(self) -> None:
        client = YouVersionClient(api_key="test-key", base_url="https://custom.api.com")
        assert client._http._base_url == "https://custom.api.com"

    @respx.mock
    def test_get_versions(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles").respond(
            json=load_fixture("versions.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_versions("en")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    def test_get_version(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111").respond(
            json=load_fixture("version_111.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_version(111)

        assert isinstance(result, Ok)
        assert result.value.id == 111

    @respx.mock
    def test_get_books(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books").respond(
            json=load_fixture("books.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_books(111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2

    @respx.mock
    def test_get_book(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN").respond(
            json=load_fixture("book_jhn.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_book(111, "JHN")

        assert isinstance(result, Ok)
        assert result.value.id == "JHN"

    @respx.mock
    def test_get_chapter(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/books/JHN/chapters/3").respond(
            json=load_fixture("chapter_jhn3.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_chapter(111, "JHN", 3)

        assert isinstance(result, Ok)
        assert result.value.id == "3"

    @respx.mock
    def test_get_passage(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/bibles/111/passages/JHN.3.16").respond(
            json=load_fixture("passage_jhn316.json")
        )
        client = YouVersionClient(api_key="test-key")
        result = client.get_passage(111, "JHN.3.16")

        assert isinstance(result, Ok)
        assert "God so loved" in result.value.content

    def test_context_manager(self) -> None:
        with YouVersionClient(api_key="test-key") as client:
            assert client._http is not None
