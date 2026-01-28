"""YouVersion Python SDK."""

from youversion.bibles import (
    BibleBook,
    BibleBookIntro,
    BibleChapter,
    BiblePassage,
    BibleVerse,
    BibleVersion,
    PaginatedResponse,
)
from youversion.languages.models import Language
from youversion.core import (
    AsyncYouVersionClient,
    AuthenticationError,
    Err,
    NetworkError,
    NotFoundError,
    Ok,
    RateLimitError,
    Result,
    ServerError,
    ValidationError,
    YouVersionClient,
    YouVersionError,
    is_err,
    is_ok,
)

__version__ = "0.1.2"

__all__ = [
    # Version
    "__version__",
    # Clients
    "YouVersionClient",
    "AsyncYouVersionClient",
    # Bible models
    "BibleVersion",
    "BibleBook",
    "BibleBookIntro",
    "BibleChapter",
    "BibleVerse",
    "BiblePassage",
    "PaginatedResponse",
    # Language models
    "Language",
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
