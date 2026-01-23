"""Core module exports."""

from youversion.core.client import AsyncYouVersionClient, YouVersionClient
from youversion.core.domain_errors import NotFoundError, ValidationError
from youversion.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ServerError,
    YouVersionError,
)
from youversion.core.result import Err, Ok, Result, is_err, is_ok

__all__ = [
    # Clients
    "YouVersionClient",
    "AsyncYouVersionClient",
    # Result types
    "Ok",
    "Err",
    "Result",
    "is_ok",
    "is_err",
    # Exceptions (raised)
    "YouVersionError",
    "NetworkError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    # Domain errors (returned)
    "NotFoundError",
    "ValidationError",
]
