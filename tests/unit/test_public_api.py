"""Tests for public API exports."""


def test_main_package_exports_client() -> None:
    """Main package exports the sync client."""
    from youversion import YouVersionClient

    assert YouVersionClient is not None


def test_main_package_exports_async_client() -> None:
    """Main package exports the async client."""
    from youversion import AsyncYouVersionClient

    assert AsyncYouVersionClient is not None


def test_main_package_exports_models() -> None:
    """Main package exports all Bible models."""
    from youversion import (
        BibleBook,
        BibleBookIntro,
        BibleChapter,
        BiblePassage,
        BibleVerse,
        BibleVersion,
        PaginatedResponse,
    )

    assert BibleVersion is not None
    assert BibleBook is not None
    assert BibleBookIntro is not None
    assert BibleChapter is not None
    assert BibleVerse is not None
    assert BiblePassage is not None
    assert PaginatedResponse is not None


def test_main_package_exports_result_types() -> None:
    """Main package exports Result types."""
    from youversion import Err, Ok, Result, is_err, is_ok

    assert Ok is not None
    assert Err is not None
    assert Result is not None
    assert is_ok is not None
    assert is_err is not None


def test_main_package_exports_exceptions() -> None:
    """Main package exports exception hierarchy."""
    from youversion import (
        AuthenticationError,
        NetworkError,
        RateLimitError,
        ServerError,
        YouVersionError,
    )

    assert YouVersionError is not None
    assert NetworkError is not None
    assert AuthenticationError is not None
    assert RateLimitError is not None
    assert ServerError is not None


def test_main_package_exports_domain_errors() -> None:
    """Main package exports domain error models."""
    from youversion import NotFoundError, ValidationError

    assert NotFoundError is not None
    assert ValidationError is not None


def test_main_package_exports_version() -> None:
    """Main package exports version string."""
    from youversion import __version__

    assert isinstance(__version__, str)
    assert __version__ == "0.1.2"


def test_core_module_exports() -> None:
    """Core module exports its public API."""
    from youversion.core import (
        AsyncYouVersionClient,
        Err,
        Ok,
        Result,
        YouVersionClient,
    )

    assert YouVersionClient is not None
    assert AsyncYouVersionClient is not None
    assert Ok is not None
    assert Err is not None
    assert Result is not None


def test_bibles_module_exports() -> None:
    """Bibles module exports its public API."""
    from youversion.bibles import (
        BibleBook,
        BibleBookIntro,
        BibleChapter,
        BiblePassage,
        BibleVerse,
        BibleVersion,
        PaginatedResponse,
    )

    assert BibleVersion is not None
    assert BibleBook is not None
    assert BibleBookIntro is not None
    assert BibleChapter is not None
    assert BibleVerse is not None
    assert BiblePassage is not None
    assert PaginatedResponse is not None
