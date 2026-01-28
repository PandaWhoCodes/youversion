"""Tests for VOTD API."""

import json
from pathlib import Path

import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import ValidationError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestVOTDAPI:
    @respx.mock
    def test_get_all_votd(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days").respond(
            json=load_fixture("votd_all.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_all_votd()

        assert isinstance(result, Ok)
        assert len(result.value.data) == 2
        assert result.value.data[0].day == 1
        assert result.value.data[0].passage_id == "JHN.3.16"

    @respx.mock
    def test_get_votd(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days/1").respond(
            json=load_fixture("votd_day.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_votd(1)

        assert isinstance(result, Ok)
        assert result.value.day == 1
        assert result.value.passage_id == "JHN.3.16"

    @respx.mock
    def test_get_votd_invalid_day(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/verse_of_the_days/999").respond(
            status_code=400
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_votd(999)

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)
