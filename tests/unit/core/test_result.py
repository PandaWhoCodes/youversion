"""Tests for Result type."""

import pytest

from youversion.core.result import Err, Ok, Result, is_err, is_ok


def test_ok_contains_value() -> None:
    result: Result[int, str] = Ok(42)
    assert is_ok(result)
    assert not is_err(result)
    assert result.value == 42


def test_err_contains_error() -> None:
    result: Result[int, str] = Err("something went wrong")
    assert is_err(result)
    assert not is_ok(result)
    assert result.error == "something went wrong"


def test_ok_is_frozen() -> None:
    result = Ok(42)
    with pytest.raises(AttributeError):
        result.value = 100  # type: ignore[misc]


def test_err_is_frozen() -> None:
    result = Err("error")
    with pytest.raises(AttributeError):
        result.error = "new error"  # type: ignore[misc]


def test_pattern_matching_ok() -> None:
    result: Result[int, str] = Ok(42)
    match result:
        case Ok(value=value):
            assert value == 42
        case Err(error=_):  # type: ignore[misc]
            pytest.fail("Should not match Err")


def test_pattern_matching_err() -> None:
    result: Result[int, str] = Err("oops")
    match result:
        case Ok(value=_):  # type: ignore[misc]
            pytest.fail("Should not match Ok")
        case Err(error=error):
            assert error == "oops"
