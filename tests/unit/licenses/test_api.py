"""Tests for Licenses API."""

import json
from pathlib import Path

import respx

from youversion import YouVersionClient
from youversion.core.result import Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestLicensesAPI:
    @respx.mock
    def test_get_licenses(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/licenses").respond(
            json=load_fixture("licenses.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_licenses(bible_id=111, developer_id="dev-uuid")

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].name == "Standard License"
        assert "bible_id=111" in str(route.calls[0].request.url)
        assert "developer_id=dev-uuid" in str(route.calls[0].request.url)
