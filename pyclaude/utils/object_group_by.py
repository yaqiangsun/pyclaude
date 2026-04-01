"""
https://tc39.es/ecma262/multipage/fundamental-objects.html#sec-object.groupby
"""

from typing import Callable, Dict, Iterable, List, TypeVar, Any

T = TypeVar('T')
K = TypeVar('K')


def object_group_by(
    items: Iterable[T],
    key_selector: Callable[[T, int], K],
) -> Dict[K, List[T]]:
    """Group items by a key selector function."""
    result: Dict[K, List[T]] = {}
    index = 0
    for item in items:
        key = key_selector(item, index)
        if key not in result:
            result[key] = []
        result[key].append(item)
        index += 1
    return result