"""Tests for Languages API."""

import json
from pathlib import Path

import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestLanguagesAPI:
    @respx.mock
    def test_get_languages(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages").respond(
            json=load_fixture("languages.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_languages()

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].id == "en"
        assert result.value.data[0].text_direction == "ltr"

    @respx.mock
    def test_get_languages_with_country_filter(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/languages").respond(
            json=load_fixture("languages.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            client.get_languages(country="US")

        assert "country=US" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_language(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages/en").respond(
            json=load_fixture("language_en.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_language("en")

        assert isinstance(result, Ok)
        assert result.value.id == "en"
        assert result.value.language == "eng"

    @respx.mock
    def test_get_language_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/languages/xyz").respond(status_code=404)
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_language("xyz")

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)
