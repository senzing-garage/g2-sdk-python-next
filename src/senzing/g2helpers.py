"""
TODO: g2helpers.py
"""

import json
import os
import sys
from ctypes import POINTER, ArgumentError, c_char_p, c_uint, c_void_p, cast
from typing import Any, Callable, Dict, TypeVar, Union

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

uintptr_type = POINTER(c_uint)
T = TypeVar("T")
P = ParamSpec("P")

# -----------------------------------------------------------------------------
# Decorators
# -----------------------------------------------------------------------------


def cast_ctypes_exceptions(function_to_decorate: Callable[P, T]) -> Callable[P, T]:
    """Modify a ctypes.ArgumentError to a TypeError."""

    def inner_function(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            result = function_to_decorate(*args, **kwargs)
        except ArgumentError as err:
            raise TypeError() from err
        except Exception as err:
            raise err
        return result

    return inner_function


# -----------------------------------------------------------------------------
# Helpers for working with parameters
# -----------------------------------------------------------------------------


def as_str(candidate_value: Union[str, Dict[Any, Any]]) -> str:
    """
    Given a string or dict, return a str.

    Args:
        candidate_value (Union[str, Dict[Any, Any]]): _description_

    Returns:
        str: The string representation of the candidate_value
    """
    if isinstance(candidate_value, dict):
        return json.dumps(candidate_value)
    return candidate_value


# -----------------------------------------------------------------------------
# Helpers for working with C
# -----------------------------------------------------------------------------


# TODO: Figure out better return type hint (e.g. POINTER[c_uint], _Pointer[c_uint])
def as_uintptr_t(candidate_value: int) -> Any:
    """
    Internal processing function.
    This converts many types of values to an integer.

    :meta private:
    """

    if not isinstance(candidate_value, int):
        raise TypeError(
            f"{candidate_value} is type{type(candidate_value)}. Needs to be type(int)"
        )
    result = cast(candidate_value, POINTER(c_uint))
    return result


def as_c_int(candidate_value: Any) -> int:
    """
    Internal processing function.
    This converts many types of values to an integer.

    :meta private:
    """

    if candidate_value is None:  # handle null string
        return int(0)
    if isinstance(candidate_value, str):  # if string is unicode, transcode to utf-8 str
        return int(candidate_value.encode("utf-8"))
    if isinstance(
        candidate_value, bytearray
    ):  # if input is bytearray, assumt utf-8 and convert to str
        return int(candidate_value)
    if isinstance(candidate_value, bytes):
        return int(candidate_value)
    # input is already an int
    return int(candidate_value)


def as_c_char_p(candidate_value: Any) -> Any:
    """
    Internal processing function.

    :meta private:
    """

    if candidate_value is None:  # handle null string
        return b""
    if isinstance(candidate_value, str):  # if string is unicode, transcode to utf-8 str
        return candidate_value.encode("utf-8")
    if isinstance(
        candidate_value, bytearray
    ):  # if input is bytearray, assumt utf-8 and convert to str
        return candidate_value.decode().encode("utf-8")
    if isinstance(candidate_value, bytes):
        return str(candidate_value).encode("utf-8")
    # input is already a str
    # return candidate_value
    # TODO Instead of TypeError can we utilise G2BadInputException and a new exception so a user only needs to catch
    # g2exception or G2BadInputException instead of knowing they must also catch TypeError. Would be more convenient and simpler
    raise TypeError(
        f"{candidate_value} has unsupported type of {type(candidate_value)}"
    )


def as_python_int(candidate_value: Any) -> int:
    """
    From a c_void_p, return a true python int.

    Args:
        candidate_value (Any): A c_void_p to be transformed.

    Returns:
        int: The python int representation

    :meta private:
    """

    result = cast(candidate_value, c_void_p).value
    if result is None:
        result = 0
    return result


def as_python_str(candidate_value: Any) -> str:
    """
    From a c_char_p, return a true python str,

    Args:
        candidate_value (Any): A c_char_p value to be transformed.

    Returns:
        str: The python string representation.

    :meta private:
    """
    result_raw = cast(candidate_value, c_char_p).value
    result = result_raw.decode() if result_raw else ""
    return result


# -----------------------------------------------------------------------------
# Helpers for working with files and directories.
# -----------------------------------------------------------------------------


def find_file_in_path(filename: str) -> str:
    """
    Find a file in the PATH environment variable.

    :meta private:
    """
    path_dirs = os.environ["PATH"].split(os.pathsep)
    for path_dir in path_dirs:
        file_path = os.path.join(path_dir, filename)
        if os.path.exists(file_path):
            return file_path
    return ""
