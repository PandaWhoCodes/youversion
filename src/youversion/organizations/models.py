"""Organization models."""

from pydantic import BaseModel


class OrganizationAddress(BaseModel):
    """Organization physical address."""

    formatted_address: str
    place_id: str
    latitude: float
    longitude: float
    administrative_area_level_1: str
    locality: str
    country: str


class Organization(BaseModel):
    """A Bible publisher/organization."""

    id: str  # UUID
    parent_organization_id: str | None = None
    name: str
    description: str
    email: str | None = None
    phone: str | None = None
    primary_language: str
    website_url: str
    address: OrganizationAddress
