from __future__ import annotations

from typing import Callable, TypeVar, Any

F = TypeVar("F", bound=Callable[..., Any])


def _identity(func: F) -> F:
    return func


try:
    from numba import njit  # type: ignore

    def jit(func: F) -> F:
        return njit(cache=True)(func)  # type: ignore

    NUMBA_AVAILABLE = True
except Exception:
    jit = _identity
    NUMBA_AVAILABLE = False
