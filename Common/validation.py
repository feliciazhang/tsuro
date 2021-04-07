"""
Code used to do selective runtime validation of types. If a function is decorated with the @validate_types
decorator and the 'IS_TYPE_CHECKING' environment variable is set, the arguments and return values will be
validated at runtime. This is currently enabled in tests but not in "production" since there is an associated
performance hit.

While mypy does allow us to make compile time assertions about our types, we found this was not always sufficient
especially when interacting with untrusted untyped input such as JSON input in our test harnesses. This module
allows us to ensure at runtime that all methods are called with arguments of the correct type and all return
values are the correct type.
"""
import os
from typing import Any, TypeVar, cast

from Common.result import Result, error
from Common.typeguard import typechecked

TYPE_CHECKING_VAR = "IS_TYPE_CHECKING"

T = TypeVar("T")


def validate_types(func: T) -> T:
    """
    Validate that the given func is always called with inputs that match the type signatures and
    that it always returns values that match the type signature.

    Only enabled if 'IS_TYPE_CHECKING' is set in the environment.

    If the given function returns a Result, any type errors will be reported in an error result.
    Otherwise, a TypeError is raised.

    :param func:    The function to decorate
    :return:        The decorated version of the function
    """

    def inner(*args: Any, **kwargs: Any) -> Any:
        if os.environ.get(TYPE_CHECKING_VAR):
            try:
                return typechecked(func)(*args, **kwargs)  # type: ignore
            except TypeError as exc:
                return_type = func.__annotations__.get("return", None)
                if getattr(return_type, "__origin__", None) == Result:
                    return error(str(exc))
                else:
                    raise exc
        return func(*args, **kwargs)  # type: ignore

    return cast(T, inner)


def disable_validation(func: T) -> T:
    """
    Disable validation when running the given function. Meant to be used in the few times that
    @validate_types causes issues (the only known case of this right now is when mocking
    stdin/stdout in unit tests).

    :param func:    The function to decorate
    :return:        The decorated function
    """

    def inner(*args: Any, **kwargs: Any) -> Any:
        was_set = False
        try:
            if TYPE_CHECKING_VAR in os.environ:
                was_set = True
                del os.environ[TYPE_CHECKING_VAR]
            return func(*args, **kwargs)  # type: ignore
        finally:
            if was_set:
                os.environ[TYPE_CHECKING_VAR] = "True"

    return cast(T, inner)
