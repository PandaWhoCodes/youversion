"""Tests for exception hierarchy."""

import pytest

from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
    YouVersionError,
)


def test_youversion_error_is_base() -> None:
    with pytest.raises(YouVersionError):
        raise YouVersionError("base error")


def test_network_error_inherits_from_base() -> None:
    with pytest.raises(YouVersionError):
        raise NetworkError("connection failed")


def test_authentication_error_inherits_from_base() -> None:
    with pytest.raises(YouVersionError):
        raise AuthenticationError("invalid api key")


def test_rate_limit_error_has_retry_after() -> None:
    error = RateLimitError("rate limited", retry_after=30.0)
    assert error.retry_after == 30.0
    assert "rate limited" in str(error)


def test_rate_limit_error_retry_after_optional() -> None:
    error = RateLimitError("rate limited")
    assert error.retry_after is None


def test_server_error_has_status_code() -> None:
    error = ServerError("internal error", status_code=500)
    assert error.status_code == 500
    assert "internal error" in str(error)
