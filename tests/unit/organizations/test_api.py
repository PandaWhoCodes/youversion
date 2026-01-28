"""Tests for Organizations API."""

import json
from pathlib import Path

import respx

from youversion import YouVersionClient
from youversion.core.domain_errors import NotFoundError
from youversion.core.result import Err, Ok

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestOrganizationsAPI:
    @respx.mock
    def test_get_organizations(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/organizations").respond(
            json=load_fixture("organizations.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organizations(bible_id=111)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
        assert result.value.data[0].name == "Bible Society"
        assert "bible_id=111" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_organizations_with_accept_language(self, respx_mock: respx.MockRouter) -> None:
        route = respx_mock.get("https://api.youversion.com/v1/organizations").respond(
            json=load_fixture("organizations.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            client.get_organizations(bible_id=111, accept_language="es")

        assert route.calls[0].request.headers["Accept-Language"] == "es"

    @respx.mock
    def test_get_organization(self, respx_mock: respx.MockRouter) -> None:
        org_id = "550e8400-e29b-41d4-a716-446655440000"
        respx_mock.get(f"https://api.youversion.com/v1/organizations/{org_id}").respond(
            json=load_fixture("organization.json")
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization(org_id)

        assert isinstance(result, Ok)
        assert result.value.id == org_id
        assert result.value.address.country == "US"

    @respx.mock
    def test_get_organization_not_found(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.youversion.com/v1/organizations/bad-uuid").respond(status_code=404)
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization("bad-uuid")

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)

    @respx.mock
    def test_get_organization_bibles(self, respx_mock: respx.MockRouter) -> None:
        org_id = "550e8400-e29b-41d4-a716-446655440000"
        respx_mock.get(f"https://api.youversion.com/v1/organizations/{org_id}/bibles").respond(
            json={
                "data": [
                    {"id": 111, "abbreviation": "NIV", "title": "NIV Bible", "language_tag": "en"}
                ],
                "next_page_token": None,
            }
        )
        with YouVersionClient(api_key="test-key") as client:
            result = client.get_organization_bibles(org_id)

        assert isinstance(result, Ok)
        assert len(result.value.data) == 1
