"""
Common operations for the 'lists' tool.

This module contains shared implementations for list operations that work
the same way regardless of expression language, plus framework for
expression-based operations.
"""

import json
import random
from typing import Any, Callable, Dict, Optional


# Sentinel for None keys in operations returning dictionaries (group_by, count_by,
# key_by) to avoid collision with legitimate string keys like "null" or "None".
NULL_SENTINEL = "(null)"


def _get_key_hash(k: Any) -> Any:
    """Get a hashable representation of a key, handling unhashable types."""
    if isinstance(k, (str, int, float, bool, type(None))):
        return k
    try:
        hash(k)
        return k
    except (TypeError, ValueError):
        try:
            if isinstance(k, (dict, list)):
                return json.dumps(k, sort_keys=True)
            return str(k)
        except Exception:
            return str(k)


# Pure operations that don't require expressions


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


# Expression-based operations that require handler functions


def op_sort_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Sorts items by expression result."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sort_by."}

    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    sort_expr = expression or (param if isinstance(param, str) else None)
    if not sort_expr:
        return {"value": None, "error": "expression is required for sort_by operation"}

    try:
        # Pre-compute sort keys with true indices to handle duplicate items correctly
        indexed_items = []
        for index, item in enumerate(items, 1):
            result = expr_handler(sort_expr, item, index, items)
            # Handle different result types for sorting
            if result is None:
                key = ""  # Sort None values first
            elif isinstance(result, dict):
                import json

                key = json.dumps(result, sort_keys=True)
            else:
                key = result
            indexed_items.append((key, index, item))

        # Sort by key, then by original index to ensure stability
        sorted_indexed = sorted(indexed_items, key=lambda x: (x[0], x[1]))
        return {"value": [item for key, index, item in sorted_indexed]}
    except Exception as e:
        return {"value": None, "error": f"sort_by failed: {str(e)}"}


def op_filter_by(
    items: list, expression: str, expr_handler: Callable, **kwargs
) -> dict:
    """Filters items where expression is truthy."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for filter_by."}
    if not expression:
        return {"value": None, "error": "Missing required expression for filter_by."}

    try:
        result = []
        for index, item in enumerate(items, 1):
            if expr_handler(expression, item, index, items):
                result.append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"filter_by failed: {str(e)}"}


def op_map(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Applies expression to each item."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for map."}
    if not expression:
        return {"value": None, "error": "Missing required expression for map."}

    try:
        result = []
        for index, item in enumerate(items, 1):
            result.append(expr_handler(expression, item, index, items))
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"map failed: {str(e)}"}


def op_find_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Finds first item where expression is truthy."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for find_by."}

    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    find_expr = expression or (param if isinstance(param, str) else None)
    if not find_expr:
        return {"value": None, "error": "expression is required for find_by operation"}

    try:
        for index, item in enumerate(items, 1):
            if expr_handler(find_expr, item, index, items):
                return {"value": item}
        return {"value": None}
    except Exception as e:
        return {"value": None, "error": f"find_by failed: {str(e)}"}


def op_group_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Groups items by expression result."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for group_by."}

    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    group_expr = expression or (param if isinstance(param, str) else None)
    if not group_expr:
        return {"value": None, "error": "expression is required for group_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            key = expr_handler(group_expr, item, index, items)
            # Convert result to string for consistent grouping
            key = str(key) if key is not None else NULL_SENTINEL
            result.setdefault(key, []).append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"group_by failed: {str(e)}"}


def op_uniq_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Remove duplicates by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    uniq_expr = expression or (param if isinstance(param, str) else None)
    if not uniq_expr:
        return {"value": None, "error": "expression is required for uniq_by operation"}

    try:
        seen = set()
        result = []
        for index, item in enumerate(items, 1):
            k = expr_handler(uniq_expr, item, index, items)
            k_hash = _get_key_hash(k)
            if k_hash not in seen:
                seen.add(k_hash)
                result.append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"uniq_by failed: {str(e)}"}


def op_partition(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Split list by expression result/boolean."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    part_expr = expression or (param if isinstance(param, str) else None)
    if not part_expr:
        return {
            "value": None,
            "error": "expression is required for partition operation",
        }

    try:
        trues, falses = [], []
        for index, item in enumerate(items, 1):
            result = expr_handler(part_expr, item, index, items)
            (trues if result else falses).append(item)
        return {"value": [trues, falses]}
    except Exception as e:
        return {"value": None, "error": f"partition failed: {str(e)}"}


def op_pluck(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Extract values by expression."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    pluck_expr = expression or (param if isinstance(param, str) else None)
    if not pluck_expr:
        return {"value": None, "error": "expression is required for pluck operation"}

    try:
        result = [
            expr_handler(pluck_expr, item, index, items)
            for index, item in enumerate(items, 1)
        ]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"pluck failed: {str(e)}"}


def op_remove_by(
    items: list, expression: str, expr_handler: Callable, **kwargs
) -> dict:
    """Remove items matching expression."""
    if not expression:
        return {
            "value": None,
            "error": "expression is required for remove_by operation",
        }

    try:
        result = [
            item
            for index, item in enumerate(items, 1)
            if not expr_handler(expression, item, index, items)
        ]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"remove_by failed: {str(e)}"}


def op_count_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Count occurrences by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    count_expr = expression or (param if isinstance(param, str) else None)
    if not count_expr:
        return {"value": None, "error": "expression is required for count_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            k = expr_handler(count_expr, item, index, items)
            # Convert result to string for consistent dictionary keys
            k = str(k) if k is not None else NULL_SENTINEL
            result[k] = result.get(k, 0) + 1
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"count_by failed: {str(e)}"}


def op_key_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Create dict keyed by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    key_expr = expression or (param if isinstance(param, str) else None)
    if not key_expr:
        return {"value": None, "error": "expression is required for key_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            k = expr_handler(key_expr, item, index, items)
            # Convert result to string for consistent dictionary keys
            # Use NULL_SENTINEL for None to avoid collision with string "null"
            if k is None:
                k = NULL_SENTINEL
            elif isinstance(k, int):
                k = str(k)
            result[k] = item
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"key_by failed: {str(e)}"}


def op_min_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find item with minimum property value."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    min_expr = expression or (param if isinstance(param, str) else None)
    if not min_expr:
        return {"value": None, "error": "expression is required for min_by operation"}

    try:
        if not items:
            return {"value": None}

        def min_key(indexed_item):
            index, x = indexed_item
            result = expr_handler(min_expr, x, index, items)
            return result if result is not None else float("inf")

        best_indexed_item = min(enumerate(items, 1), key=min_key)
        return {"value": best_indexed_item[1]}
    except Exception as e:
        return {"value": None, "error": f"min_by failed: {str(e)}"}


def op_max_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find item with maximum property value."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    max_expr = expression or (param if isinstance(param, str) else None)
    if not max_expr:
        return {"value": None, "error": "expression is required for max_by operation"}

    try:
        if not items:
            return {"value": None}

        def max_key(indexed_item):
            index, x = indexed_item
            result = expr_handler(max_expr, x, index, items)
            return result if result is not None else float("-inf")

        best_indexed_item = max(enumerate(items, 1), key=max_key)
        return {"value": best_indexed_item[1]}
    except Exception as e:
        return {"value": None, "error": f"max_by failed: {str(e)}"}


def op_index_of(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find index of first item matching expression."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    index_expr = expression or (param if isinstance(param, str) else None)
    if not index_expr:
        return {"value": None, "error": "expression is required for index_of operation"}

    try:
        for idx, item in enumerate(items):
            # Note: idx is 0-based for index_of operation, but we pass
            # 1-based index to expressions
            result = expr_handler(index_expr, item, idx + 1, items)
            if result:
                return {"value": idx}
        return {"value": -1}
    except Exception as e:
        return {"value": None, "error": f"index_of failed: {str(e)}"}


def op_random_except(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Get random item excluding condition."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    except_expr = expression or (param if isinstance(param, str) else None)
    if not except_expr:
        return {
            "value": None,
            "error": "expression is required for random_except operation",
        }

    try:
        import random

        # Exclude items where expression is truthy
        filtered = [
            item
            for index, item in enumerate(items, 1)
            if not expr_handler(except_expr, item, index, items)
        ]
        if not filtered:
            return {"value": None}
        return {"value": random.choice(filtered)}
    except Exception as e:
        return {"value": None, "error": f"random_except failed: {str(e)}"}


def op_flat_map(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Like map, but flattens one level if the mapping returns lists."""
    if not expression:
        return {"value": None, "error": "expression is required for flat_map operation"}

    try:
        result = []
        for index, item in enumerate(items, 1):
            mapped = expr_handler(expression, item, index, items)
            # Handle Lua tables or other wrapped formats
            if hasattr(mapped, "__iter__") and not isinstance(mapped, (str, bytes)):
                try:
                    result.extend(mapped)
                except TypeError:
                    result.append(mapped)
            else:
                result.append(mapped)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"flat_map failed: {str(e)}"}


def op_difference_by(
    items: list,
    others: list,
    expression: str,
    expr_handler: Callable,
    param: Any = None,
    **kwargs,
) -> dict:
    """Items in first not matching expression in second."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    diff_expr = expression or (param if isinstance(param, str) else None)
    if not diff_expr:
        return {
            "value": None,
            "error": "expression is required for difference_by operation",
        }

    try:
        # Extract keys from others list using expression
        others_keys = set()
        for index, item in enumerate(others, 1):
            key_val = expr_handler(diff_expr, item, index, others)
            others_keys.add(_get_key_hash(key_val))

        # Return items from main list whose key is not in others_keys
        result = []
        for index, item in enumerate(items, 1):
            key_val = expr_handler(diff_expr, item, index, items)
            if _get_key_hash(key_val) not in others_keys:
                result.append(item)

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"difference_by failed: {str(e)}"}


def op_intersection_by(
    items: list,
    others: list,
    expression: str,
    expr_handler: Callable,
    param: Any = None,
    **kwargs,
) -> dict:
    """Items in first list matching expression in second."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    inter_expr = expression or (param if isinstance(param, str) else None)
    if not inter_expr:
        return {
            "value": None,
            "error": "expression is required for intersection_by operation",
        }

    try:
        # Extract keys from others list using expression
        others_keys = set()
        for index, item in enumerate(others, 1):
            key_val = expr_handler(inter_expr, item, index, others)
            others_keys.add(_get_key_hash(key_val))

        # Return items from main list whose key is in others_keys
        result = []
        for index, item in enumerate(items, 1):
            key_val = expr_handler(inter_expr, item, index, items)
            if _get_key_hash(key_val) in others_keys:
                result.append(item)

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"intersection_by failed: {str(e)}"}


def op_all_by(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Check if all items match expression."""
    if not expression:
        return {"value": None, "error": "expression is required for all_by operation"}

    try:
        result = all(
            bool(expr_handler(expression, item, index, items))
            for index, item in enumerate(items, 1)
        )
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"all_by failed: {str(e)}"}


def op_any_by(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Check if any items match expression."""
    if not expression:
        return {"value": None, "error": "expression is required for any_by operation"}

    try:
        result = any(
            bool(expr_handler(expression, item, index, items))
            for index, item in enumerate(items, 1)
        )
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"any_by failed: {str(e)}"}


def op_reduce(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Aggregate the list using a binary expression."""
    if not expression:
        return {"value": None, "error": "expression is required for reduce operation"}

    try:
        if not items:
            return {"value": param if param is not None else None}

        # Use the provided expr_handler with 'acc' and 'item' context
        acc = param if param is not None else items[0]
        start_idx = 0 if param is not None else 1
        for i in range(start_idx, len(items)):
            # The expression can use 'acc' and 'item'
            acc = expr_handler(
                expression,
                items[i],
                i + 1,
                items,
                context={"acc": acc, "item": items[i]},
            )
        return {"value": acc}
    except Exception as e:
        return {"value": None, "error": f"reduce failed: {str(e)}"}


def op_zip_with(
    items: list, others: list, expression: str, expr_handler: Callable, **kwargs
) -> dict:
    """Combine two lists element-wise using expression."""
    if not expression:
        return {"value": None, "error": "expression is required for zip_with operation"}

    try:
        if not isinstance(items, list) or not isinstance(others, list):
            return {
                "value": None,
                "error": "Both 'items' and 'others' must be lists for zip_with",
            }

        min_len = min(len(items), len(others))
        result = []
        for i in range(min_len):
            val = expr_handler(
                expression,
                items[i],
                i + 1,
                items,
                context={"item": items[i], "other": others[i]},
            )
            result.append(val)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"zip_with failed: {str(e)}"}


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


def lists_operation(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
    expr_handler: Optional[Callable] = None,
) -> dict:
    """
    Execute a lists tool operation.

    Args:
        items: The input list to operate on
        operation: Name of the operation to perform
        param: Optional parameter for some operations
        others: Optional second list for set operations
        expression: Optional expression for expression-based operations
        expr_handler: Function to handle expression evaluation

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    try:
        # Check if it's a pure operation
        if operation in PURE_OPERATIONS:
            op_func = PURE_OPERATIONS[operation]
            result = op_func(
                items=items,
                param=param,
                others=others,
            )
            return result

        # Check if it's an expression-based operation
        elif operation in EXPRESSION_OPERATIONS:
            # Some operations can use param as expression fallback
            # (backward compatibility)
            backward_compat_ops = [
                "min_by",
                "max_by",
                "sort_by",
                "uniq_by",
                "partition",
                "pluck",
                "group_by",
                "count_by",
                "key_by",
                "find_by",
                "index_of",
                "random_except",
                "difference_by",
                "intersection_by",
            ]
            if not expression and (operation not in backward_compat_ops or not param):
                return {
                    "value": None,
                    "error": (
                        f"Missing required expression for operation '{operation}'."
                    ),
                }
            if not expr_handler:
                return {
                    "value": None,
                    "error": (
                        f"No expression handler provided for operation '{operation}'."
                    ),
                }

            op_func = EXPRESSION_OPERATIONS[operation]
            result = op_func(
                items=items,
                expression=expression,
                expr_handler=expr_handler,
                param=param,
                others=others,
            )
            return result

        else:
            return {"value": None, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"value": None, "error": f"Lists operation failed: {str(e)}"}
