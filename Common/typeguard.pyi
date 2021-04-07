"""
A typing stub file for typeguard. The vendored typeguard library does not use type hints
internally so this stub file adds type hints for the one portion of typeguard that is used
inside of our codebase.
"""
from typing import TypeVar, Callable

T = TypeVar('T', bound=Callable)    # type: ignore

def typechecked(f: T) -> T:
    pass