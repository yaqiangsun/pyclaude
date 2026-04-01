"""
Polyfill for Promise.withResolvers() (ES2024, Node 22+).
"""

from typing import Any, Callable, Dict, Promise, TypeVar

T = TypeVar('T')


def with_resolvers() -> Dict[str, Any]:
    """Polyfill for Promise.withResolvers()."""
    resolve: Callable[[T | Any], None]
    reject: Callable[[Any], None]

    def resolve_func(value: T | Any) -> None:
        nonlocal resolve
        resolve(value)

    def reject_func(reason: Any) -> None:
        nonlocal reject
        reject(reason)

    promise = Promise(resolve_func, reject_func)  # type: ignore
    return {"promise": promise, "resolve": resolve_func, "reject": reject_func}