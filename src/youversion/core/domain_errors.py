"""Domain error models for expected errors (returned, not raised)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class NotFoundError(BaseModel, frozen=True):
    """Resource not found error."""

    resource: Literal["version", "book", "chapter", "verse", "passage", "language", "highlight"]
    identifier: str
    message: str


class ValidationError(BaseModel, frozen=True):
    """Validation error for invalid input."""

    field: str
    reason: str


DomainError = NotFoundError | ValidationError
