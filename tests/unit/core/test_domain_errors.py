"""Tests for domain error models."""

from youversion.core.domain_errors import NotFoundError, ValidationError


def test_not_found_error_fields() -> None:
    error = NotFoundError(resource="version", identifier="999", message="Bible version not found")
    assert error.resource == "version"
    assert error.identifier == "999"
    assert error.message == "Bible version not found"


def test_not_found_error_from_dict() -> None:
    data = {"resource": "book", "identifier": "XYZ", "message": "Book not found"}
    error = NotFoundError.model_validate(data)
    assert error.resource == "book"


def test_validation_error_fields() -> None:
    error = ValidationError(field="language_ranges", reason="Invalid format")
    assert error.field == "language_ranges"
    assert error.reason == "Invalid format"


def test_validation_error_from_dict() -> None:
    data = {"field": "day", "reason": "Must be 1-366"}
    error = ValidationError.model_validate(data)
    assert error.field == "day"
