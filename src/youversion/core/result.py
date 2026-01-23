"""Result type for explicit error handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeGuard, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value."""

    value: T


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed result containing an error."""

    error: E


Result = Ok[T] | Err[E]


def is_ok(result: Result[T, E]) -> TypeGuard[Ok[T]]:
    """Check if result is Ok."""
    return isinstance(result, Ok)


def is_err(result: Result[T, E]) -> TypeGuard[Err[E]]:
    """Check if result is Err."""
    return isinstance(result, Err)
