from typing import Any, Callable, Dict, Optional
import random
from .expressions import (
    op_all_by,
    op_any_by,
    op_count_by,
    op_difference_by,
    op_filter_by,
    op_find_by,
    op_flat_map,
    op_group_by,
    op_index_of,
    op_intersection_by,
    op_key_by,
    op_map,
    op_max_by,
    op_min_by,
    op_partition,
    op_pluck,
    op_random_except,
    op_reduce,
    op_remove_by,
    op_sort_by,
    op_uniq_by,
    op_zip_with,
)


def op_xor(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Symmetric difference between two lists."""
    if not isinstance(items, list) or not isinstance(others, list):
        return {"value": None, "error": "Both arguments must be lists for xor."}
    try:
        return {"value": list(set(items) ^ set(others))}
    except TypeError:
        # Fallback for unhashable types
        result = [x for x in items if x not in others] + [
            x for x in others if x not in items
        ]
        return {"value": result}


def op_shuffle(items: list, **kwargs) -> dict:
    """Randomizes order of items."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for shuffle."}
    result = items[:]
    random.shuffle(result)
    return {"value": result}


def op_sample_size(items: list, param: Any = None, **kwargs) -> dict:
    """Gets n random items."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sample_size."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    if n <= 0:
        return {"value": []}
    if n >= len(items):
        return {"value": items[:]}
    return {"value": random.sample(items, n)}


def op_is_empty(items: list, **kwargs) -> dict:
    """Checks if list is empty."""
    # Accept 0, False, None as empty for lists (matching original behavior)
    if items is None or items == 0 or items is False:
        return {"value": True}
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for is_empty."}
    return {"value": len(items) == 0}


def op_head(items: list, **kwargs) -> dict:
    """First element."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for head."}
    return {"value": items[0] if items else None}


def op_last(items: list, **kwargs) -> dict:
    """Last element."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for last."}
    return {"value": items[-1] if items else None}


def op_tail(items: list, **kwargs) -> dict:
    """All elements except first."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for tail."}
    return {"value": items[1:] if items else []}


def op_initial(items: list, **kwargs) -> dict:
    """All elements except last."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for initial."}
    return {"value": items[:-1] if items else []}


def op_drop(items: list, param: Any = None, **kwargs) -> dict:
    """Drops n elements from start."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for drop."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[n:]}


def op_drop_right(items: list, param: Any = None, **kwargs) -> dict:
    """Drops n elements from end."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for drop_right."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[:-n] if n > 0 else items}


def op_take(items: list, param: Any = None, **kwargs) -> dict:
    """Takes n elements from start."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for take."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[:n]}


def op_take_right(items: list, param: Any = None, **kwargs) -> dict:
    """Takes n elements from end."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for take_right."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[-n:] if n > 0 else []}


def op_flatten(items: list, **kwargs) -> dict:
    """Flattens one level of nesting."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for flatten."}
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return {"value": result}


def op_flatten_deep(items: list, **kwargs) -> dict:
    """Flattens nested lists completely."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for flatten_deep."}

    def flatten_recursive(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten_recursive(item))
            else:
                result.append(item)
        return result

    return {"value": flatten_recursive(items)}


def op_compact(items: list, **kwargs) -> dict:
    """Removes falsy values."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for compact."}

    def is_truthy(item):
        # Handle PythonMonkey null type specifically
        # PythonMonkey null comes through as the null type itself, not an instance
        if str(item) == "<class 'pythonmonkey.null'>":
            return False
        return bool(item)

    return {"value": [item for item in items if is_truthy(item)]}


def op_chunk(items: list, param: Any = None, **kwargs) -> dict:
    """Splits into chunks of specified size."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for chunk."}
    if param is None:
        return {"value": None, "error": "chunk operation requires a size parameter"}
    try:
        size = int(param)
        if size <= 0:
            return {"value": None, "error": "chunk size must be positive"}
        return {"value": [items[i : i + size] for i in range(0, len(items), size)]}
    except (ValueError, TypeError):
        return {"value": None, "error": "chunk size must be an integer"}


def op_zip_lists(items: list, **kwargs) -> dict:
    """Zips multiple lists together."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for zip_lists."}
    if not items:
        return {"value": []}
    return {"value": [list(t) for t in zip(*items)]}


def op_unzip_list(items: list, **kwargs) -> dict:
    """Unzips list of lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for unzip_list."}
    if not items:
        return {"value": []}
    return {"value": [list(t) for t in zip(*items)]}


def op_union(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Unique values from multiple lists. Expects items to be a list of lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for union."}

    try:
        result = []
        seen = set()
        for sublist in items:
            if isinstance(sublist, list):
                for item in sublist:
                    try:
                        if item not in seen:
                            seen.add(item)
                            result.append(item)
                    except TypeError:
                        # Handle unhashable types
                        if item not in result:
                            result.append(item)
            else:
                # Handle case where items is not a list of lists
                try:
                    if sublist not in seen:
                        seen.add(sublist)
                        result.append(sublist)
                except TypeError:
                    if sublist not in result:
                        result.append(sublist)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"union failed: {str(e)}"}


def op_intersection(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Items present in both lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for intersection."}
    if others is None:
        others = []
    if not isinstance(others, list):
        return {"value": None, "error": "Others must be a list for intersection."}

    try:
        return {"value": list(set(items) & set(others))}
    except TypeError:
        # Fallback for unhashable types
        return {"value": [x for x in items if x in others]}


def op_difference(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Items in first list not in second."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for difference."}
    if others is None:
        others = []
    if not isinstance(others, list):
        return {"value": None, "error": "Others must be a list for difference."}

    try:
        return {"value": list(set(items) - set(others))}
    except TypeError:
        # Fallback for unhashable types
        return {"value": [x for x in items if x not in others]}


def op_sample(items: list, **kwargs) -> dict:
    """One random item."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sample."}
    return {"value": random.choice(items) if items else None}


def op_nth(items: list, param: Any = None, **kwargs) -> dict:
    """Element at specific index."""
    if not isinstance(items, list):
        return {"value": None, "error": "nth operation requires a list"}
    if param is None:
        return {"value": None, "error": "nth operation requires an index parameter"}
    if not isinstance(param, int):
        return {"value": None, "error": "nth index must be an integer"}
    try:
        if -len(items) <= param < len(items):
            return {"value": items[param]}
        return {"value": None}
    except Exception as e:
        return {"value": None, "error": f"nth failed: {str(e)}"}


def op_contains(items: list, param: Any = None, **kwargs) -> dict:
    """Checks if list contains specific value."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for contains."}
    return {"value": param in items}


def op_is_equal(items: list, param: Any = None, **kwargs) -> dict:
    """Checks if two lists are equal."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for is_equal."}
    if not isinstance(param, list):
        return {"value": False}
    return {"value": items == param}


def op_min(items: list, **kwargs) -> dict:
    """Minimum value in list."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for min."}
    if not items:
        return {"value": None, "error": "Cannot find minimum of empty list"}
    try:
        return {"value": min(items)}
    except TypeError as e:
        return {"value": None, "error": f"Cannot compare items for minimum: {e}"}


def op_max(items: list, **kwargs) -> dict:
    """Maximum value in list."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for max."}
    if not items:
        return {"value": None, "error": "Cannot find maximum of empty list"}
    try:
        return {"value": max(items)}
    except TypeError as e:
        return {"value": None, "error": f"Cannot compare items for maximum: {e}"}


def op_join(items: list, param: Any = None, **kwargs) -> dict:
    """Joins list items into string with delimiter."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for join."}
    delimiter = str(param) if param is not None else ""
    try:

        def convert_item(item):
            # Convert float integers to ints before stringifying
            if isinstance(item, float) and item.is_integer():
                return str(int(item))
            return str(item)

        return {"value": delimiter.join(convert_item(item) for item in items)}
    except Exception as e:
        return {"value": None, "error": f"Join failed: {str(e)}"}


# Pure operations registry - these don't require expressions
PURE_OPERATIONS: Dict[str, Callable] = {
    "xor": op_xor,
    "shuffle": op_shuffle,
    "sample_size": op_sample_size,
    "is_empty": op_is_empty,
    "head": op_head,
    "last": op_last,
    "tail": op_tail,
    "initial": op_initial,
    "drop": op_drop,
    "drop_right": op_drop_right,
    "take": op_take,
    "take_right": op_take_right,
    "flatten": op_flatten,
    "flatten_deep": op_flatten_deep,
    "compact": op_compact,
    "chunk": op_chunk,
    "zip_lists": op_zip_lists,
    "unzip_list": op_unzip_list,
    "union": op_union,
    "intersection": op_intersection,
    "difference": op_difference,
    "sample": op_sample,
    "nth": op_nth,
    "contains": op_contains,
    "is_equal": op_is_equal,
    "min": op_min,
    "max": op_max,
    "join": op_join,
}

# Expression-based operations registry - these require an expression handler
EXPRESSION_OPERATIONS: Dict[str, Callable] = {
    "sort_by": op_sort_by,
    "filter_by": op_filter_by,
    "map": op_map,
    "find_by": op_find_by,
    "group_by": op_group_by,
    "uniq_by": op_uniq_by,
    "partition": op_partition,
    "pluck": op_pluck,
    "remove_by": op_remove_by,
    "count_by": op_count_by,
    "key_by": op_key_by,
    "min_by": op_min_by,
    "max_by": op_max_by,
    "index_of": op_index_of,
    "random_except": op_random_except,
    "flat_map": op_flat_map,
    "difference_by": op_difference_by,
    "intersection_by": op_intersection_by,
    "all_by": op_all_by,
    "every": op_all_by,  # Alias for all_by
    "any_by": op_any_by,
    "some": op_any_by,  # Alias for any_by
    "reduce": op_reduce,
    "zip_with": op_zip_with,
}
