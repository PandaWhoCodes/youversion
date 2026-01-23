"""Exception hierarchy for unexpected errors."""

from __future__ import annotations


class YouVersionError(Exception):
    """Base exception for all SDK errors."""


class NetworkError(YouVersionError):
    """Connection failed, timeout, DNS issues."""


class AuthenticationError(YouVersionError):
    """Invalid or expired API key."""


class RateLimitError(YouVersionError):
    """429 - Rate limit exceeded."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(YouVersionError):
    """5xx responses from API."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
