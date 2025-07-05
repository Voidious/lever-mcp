"""
Lists tool implementation for Lever MCP.

This module contains the lists tool functionality for list operations
including mutations, selections, set-like operations, grouping, and filtering.
"""

from typing import Any, Optional
import random
import json
from lib.lua import _unwrap_input, _apply_wrapping, _wrap_result, evaluate_expression


def lists_tool(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for list operations."""
    return _lists_impl(items, operation, param, others, expression, wrap=False)


def _evaluate_expression_optimized(expr, item, index=None, items_list=None):
    """Optimized expression evaluation with fast path for simple key access."""
    if isinstance(item, dict) and expr.isidentifier() and expr in item:
        # Fast path: simple key lookup without Lua runtime
        return item[expr]
    else:
        # Full expression evaluation with lists context
        context = {"item": item}
        if index is not None:
            context["index"] = index
        if items_list is not None:
            context["items"] = items_list
        return evaluate_expression(expr, item, context=context)


def _lists_impl(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    if others is None:
        others = []

    # Handle wrapped list objects
    if isinstance(items, dict) and "__type" in items and "data" in items:
        if items["__type"] == "list":
            items = items["data"]
            # Convert Lua table to Python list if needed
            if hasattr(items, "keys"):
                keys = list(items.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    items = [items.get(k) for k in range(1, max_k + 1)]
                else:
                    items = list(items.values())

    if isinstance(others, dict) and "__type" in others and "data" in others:
        if others["__type"] == "list":
            others = others["data"]
            # Convert Lua table to Python list if needed
            if hasattr(others, "keys"):
                keys = list(others.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    others = [others.get(k) for k in range(1, max_k + 1)]
                else:
                    others = list(others.values())

    # Support xor, shuffle, sample_size, is_empty as well
    if operation == "xor":
        if not isinstance(items, list) or not isinstance(others, list):
            return {"value": None, "error": "Both arguments must be lists for xor."}
        try:
            return {"value": list(set(items) ^ set(others))}
        except TypeError:
            # Fallback for unhashable types (e.g., lists of lists/dicts)
            result = [x for x in items if x not in others] + [
                x for x in others if x not in items
            ]
            return {"value": result}
    elif operation == "shuffle":
        if not isinstance(items, list):
            return {"value": None, "error": "Argument must be a list for shuffle."}
        result = items[:]
        random.shuffle(result)
        return {"value": result}
    elif operation == "sample_size":
        if not isinstance(items, list):
            return {
                "value": None,
                "error": "Argument must be a list for sample_size.",
            }
        n = param if isinstance(param, int) else 1
        if n < 0:
            return {"value": None, "error": "sample_size must be non-negative."}
        return {"value": random.sample(items, min(n, len(items)))}
    elif operation == "is_empty":
        # Accept 0, False as empty for lists
        if items is None or items == 0 or items is False:
            return {"value": True}
        return {"value": len(items) == 0}

    """
    Performs list operations, including mutation, selection, set-like, grouping,
    and property checks. For set-like operations, use items as the first list and
    others as the second list.

    Supported operations: all_by, any_by, chunk, compact, contains, count_by,
    difference, difference_by, drop, drop_right, filter_by, find_by, flat_map,
    flatten, flatten_deep, group_by, head, index_of, initial, intersection,
    intersection_by, is_equal, key_by, last, map, max_by, min_by, nth, partition,
    pluck, random_except, reduce, remove_by, sample, sort_by, tail, take,
    take_right, union, uniq_by, unzip_list, zip_lists, zip_with
    """

    # Unwrap input parameters
    items = _unwrap_input(items)
    param = _unwrap_input(param)
    others = _unwrap_input(others)

    try:
        # Mutations
        if operation == "flatten_deep":
            result = []

            def _flatten(lst):
                for i in lst:
                    if isinstance(i, list):
                        _flatten(i)
                    else:
                        result.append(i)

            _flatten(items)
            return {"value": result}
        elif operation == "sort_by":
            # Use expression if provided, otherwise use param as expression
            sort_expr = expression or (param if isinstance(param, str) else None)
            if not sort_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'sort_by'."
                    ),
                }

            def get_sort_key(x):
                # For sort operations, we don't have a meaningful index context since
                # the order changes
                result = _evaluate_expression_optimized(sort_expr, x)
                # Handle different result types for sorting
                if result is None:
                    return ""  # Sort None values first
                elif isinstance(result, dict):
                    return json.dumps(result, sort_keys=True)
                return result

            return {"value": sorted(items, key=get_sort_key)}
        elif operation == "uniq_by":
            # Use expression if provided, otherwise use param as expression
            uniq_expr = expression or (param if isinstance(param, str) else None)
            if not uniq_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'uniq_by'."
                    ),
                }
            seen = set()
            result = []
            for index, item in enumerate(items, 1):
                k = _evaluate_expression_optimized(uniq_expr, item, index, items)
                k_hash = json.dumps(k, sort_keys=True) if isinstance(k, dict) else k
                if k_hash not in seen:
                    seen.add(k_hash)
                    result.append(item)
            return {"value": result}
        elif operation == "partition":
            # Use expression if provided, otherwise use param as expression
            part_expr = expression or (param if isinstance(param, str) else None)
            if not part_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'partition'."
                    ),
                }
            trues, falses = [], []
            for index, item in enumerate(items, 1):
                result = _evaluate_expression_optimized(part_expr, item, index, items)
                (trues if result else falses).append(item)
            return {"value": [trues, falses]}
        elif operation == "pluck":
            # Use expression if provided, otherwise use param as expression
            pluck_expr = expression or (param if isinstance(param, str) else None)
            if not pluck_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'pluck'."
                    ),
                }
            return {
                "value": [
                    _evaluate_expression_optimized(pluck_expr, item, index, items)
                    for index, item in enumerate(items, 1)
                ]
            }
        elif operation == "compact":
            return {"value": [item for item in items if item]}
        elif operation == "chunk":
            size = int(param)
            return {"value": [items[i : i + size] for i in range(0, len(items), size)]}
        elif operation == "zip_lists":
            return {"value": [list(t) for t in zip(*items)]}
        elif operation == "unzip_list":
            return {"value": [list(t) for t in zip(*items)]}
        elif operation == "remove_by":
            if not expression:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression parameter for operation "
                        "'remove_by'."
                    ),
                }
            return {
                "value": [
                    item
                    for index, item in enumerate(items, 1)
                    if not _evaluate_expression_optimized(
                        expression, item, index, items
                    )
                ]
            }
        elif operation == "tail":
            result = {"value": items[1:] if len(items) > 1 else []}
            return _wrap_result(result, wrap)
        elif operation == "initial":
            result = {"value": items[:-1] if items else []}
            return _wrap_result(result, wrap)
        elif operation == "drop":
            return {"value": items[int(param) :]}
        elif operation == "drop_right":
            return {"value": items[: -int(param)] if int(param) > 0 else items[:]}
        elif operation == "take":
            return {"value": items[: int(param)]}
        elif operation == "take_right":
            result = {"value": items[-int(param) :] if int(param) > 0 else []}
            return _wrap_result(result, wrap)
        elif operation == "flatten":
            result = []
            for sublist in items:
                if isinstance(sublist, list):
                    result.extend(sublist)
                else:
                    result.append(sublist)
            return {"value": result}
        elif operation == "union":
            result = []
            seen = set()
            for sublist in items:
                for item in sublist:
                    if item not in seen:
                        seen.add(item)
                        result.append(item)
            return {"value": result}
        # Set-like operations
        elif operation == "difference_by":
            # Use expression if provided, otherwise use param as expression
            diff_expr = expression or (param if isinstance(param, str) else None)
            if not diff_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'difference_by'."
                    ),
                }

            # Extract keys from others list using expression
            others_keys = set()
            for index, item in enumerate(others, 1):
                key_val = _evaluate_expression_optimized(diff_expr, item, index, others)
                others_keys.add(key_val)

            # Return items from main list whose key is not in others_keys
            result = []
            for index, item in enumerate(items, 1):
                key_val = _evaluate_expression_optimized(diff_expr, item, index, items)
                if key_val not in others_keys:
                    result.append(item)

            return {"value": result}
        elif operation == "intersection_by":
            # Use expression if provided, otherwise use param as expression
            inter_expr = expression or (param if isinstance(param, str) else None)
            if not inter_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'intersection_by'."
                    ),
                }

            # Extract keys from others list using expression
            others_keys = set()
            for index, item in enumerate(others, 1):
                key_val = _evaluate_expression_optimized(
                    inter_expr, item, index, others
                )
                others_keys.add(key_val)

            # Return items from main list whose key is in others_keys
            result = []
            for index, item in enumerate(items, 1):
                key_val = _evaluate_expression_optimized(inter_expr, item, index, items)
                if key_val in others_keys:
                    result.append(item)

            return {"value": result}
        elif operation == "intersection":
            # Support intersection for multiple lists (not just two)
            if isinstance(items, list) and all(isinstance(x, list) for x in items):
                # If others is provided and is a list of lists, do value-based
                # intersection
                if others and all(isinstance(x, list) for x in others):
                    result = [x for x in items if any(x == y for y in others)]
                    return {"value": result}
                # Otherwise, do intersection across all sublists (lists of lists of
                # lists)
                if not items:
                    return {"value": []}
                result = (
                    set(tuple(x) for x in items[0])
                    if all(isinstance(x, list) for x in items[0])
                    else set(tuple(x) for x in items[0:1])
                )
                for sublist in items[1:]:
                    result &= set(tuple(x) for x in sublist)
                return {"value": [list(x) for x in result]}
            elif isinstance(items, list) and isinstance(others, list):
                # If both are lists of lists, compare by value (not tuple)
                if all(isinstance(x, list) for x in items) and all(
                    isinstance(x, list) for x in others
                ):
                    result = [x for x in items if any(x == y for y in others)]
                    return {"value": result}
                try:
                    return {"value": [item for item in items if item in others]}
                except TypeError:
                    # Fallback for unhashable types
                    return {
                        "value": [
                            item
                            for item in items
                            if any(
                                json.dumps(item, sort_keys=True)
                                == json.dumps(other, sort_keys=True)
                                for other in others
                            )
                        ]
                    }
            else:
                return {"value": []}
        elif operation == "difference":
            if isinstance(items, list) and all(isinstance(x, list) for x in items):
                if not items:
                    return {"value": []}
                result = set(items[0])
                for sublist in items[1:]:
                    result -= set(sublist)
                return {"value": list(result)}
            elif isinstance(items, list) and isinstance(others, list):
                try:
                    return {"value": [item for item in items if item not in others]}
                except TypeError:
                    # Fallback for unhashable types
                    return {
                        "value": [
                            item
                            for item in items
                            if all(
                                json.dumps(item, sort_keys=True)
                                != json.dumps(other, sort_keys=True)
                                for other in others
                            )
                        ]
                    }
            else:
                return {"value": []}
        # Grouping/Counting
        elif operation == "group_by":
            # Use expression if provided, otherwise use param as expression
            group_expr = expression or (param if isinstance(param, str) else None)
            if not group_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'group_by'."
                    ),
                }
            result = {}
            for index, item in enumerate(items, 1):
                try:
                    k = _evaluate_expression_optimized(group_expr, item, index, items)
                    # Convert result to string for consistent grouping
                    k = str(k) if k is not None else "None"
                    result.setdefault(k, []).append(item)
                except Exception:
                    # If expression fails, group under "error"
                    result.setdefault("error", []).append(item)
            return {"value": result}
        elif operation == "count_by":
            # Use expression if provided, otherwise use param as expression
            count_expr = expression or (param if isinstance(param, str) else None)
            if not count_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'count_by'."
                    ),
                }
            result = {}
            for index, item in enumerate(items, 1):
                k = _evaluate_expression_optimized(count_expr, item, index, items)
                # Convert result to string for consistent dictionary keys
                k = str(k) if k is not None else "null"
                result[k] = result.get(k, 0) + 1
            return {"value": result}
        elif operation == "key_by":
            # Use expression if provided, otherwise use param as expression
            key_expr = expression or (param if isinstance(param, str) else None)
            if not key_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'key_by'."
                    ),
                }
            # Convert integer keys to strings to avoid Lua table->list conversion
            result = {}
            for index, item in enumerate(items, 1):
                k = _evaluate_expression_optimized(key_expr, item, index, items)
                # Convert integer keys to strings like JSON does
                if isinstance(k, int):
                    k = str(k)
                result[k] = item
            return {"value": result}
        # Selection
        elif operation == "find_by":
            # Use expression if provided, otherwise use param as expression
            find_expr = expression or (param if isinstance(param, str) else None)
            if not find_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'find_by'."
                    ),
                }

            # Find first item where expression is truthy
            for index, item in enumerate(items, 1):
                result = _evaluate_expression_optimized(find_expr, item, index, items)
                if result:
                    return {"value": item}
            return {"value": None}
        elif operation == "head":
            if not isinstance(items, list):
                return {"value": None, "error": "head operation requires a list"}
            return {"value": items[0] if items else None}
        elif operation == "last":
            if not isinstance(items, list):
                return {"value": None, "error": "last operation requires a list"}
            return {"value": items[-1] if items else None}
        elif operation == "sample":
            if not isinstance(items, list):
                return {"value": None, "error": "sample operation requires a list"}
            if not items:
                return {"value": None}
            return {"value": random.choice(items)}
        elif operation == "nth":
            if not isinstance(items, list):
                return {"value": None, "error": "nth operation requires a list"}
            idx = param
            if param is None:
                return {
                    "value": None,
                    "error": "nth operation requires an index parameter",
                }
            if -len(items) <= idx < len(items):
                return {"value": items[idx]}
            return {"value": None}
        elif operation == "min_by":
            # Use expression if provided, otherwise use param as expression
            min_expr = expression or (param if isinstance(param, str) else None)
            if not min_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'min_by'."
                    ),
                }

            def min_key(x):
                # For sort operations, we don't have a meaningful index context
                result = _evaluate_expression_optimized(min_expr, x)
                return result if result is not None else float("inf")

            return {"value": min(items, key=min_key)}
        elif operation == "max_by":
            # Use expression if provided, otherwise use param as expression
            max_expr = expression or (param if isinstance(param, str) else None)
            if not max_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'max_by'."
                    ),
                }

            def max_key(x):
                # For sort operations, we don't have a meaningful index context
                result = _evaluate_expression_optimized(max_expr, x)
                return result if result is not None else float("-inf")

            return {"value": max(items, key=max_key)}
        elif operation == "index_of":
            # Use expression if provided, otherwise use param as expression
            index_expr = expression or (param if isinstance(param, str) else None)
            if not index_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'index_of'."
                    ),
                }

            # Find first item where expression is truthy
            for idx, item in enumerate(items):
                # Note: idx is 0-based for index_of operation, but we pass 1-based index
                # to expressions
                result = _evaluate_expression_optimized(
                    index_expr, item, idx + 1, items
                )
                if result:
                    return {"value": idx}
            return {"value": -1}
        elif operation == "random_except":
            # Use expression if provided, otherwise use param as expression
            except_expr = expression or (param if isinstance(param, str) else None)
            if not except_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'random_except'."
                    ),
                }

            # Exclude items where expression is truthy
            filtered = [
                item
                for index, item in enumerate(items, 1)
                if not _evaluate_expression_optimized(except_expr, item, index, items)
            ]
            if not filtered:
                return {"value": None}
            return {"value": random.choice(filtered)}
        # New: contains, is_equal
        elif operation == "contains":
            return {"value": param in items}
        elif operation == "is_equal":
            return {"value": items == param}
        # --- New Functional Operations ---
        elif operation == "map":
            if not expression:
                return {"value": None, "error": "'expression' is required for map."}
            result = []
            for index, item in enumerate(items, 1):
                mapped = _evaluate_expression_optimized(
                    expression, item, index=index, items_list=items
                )
                result.append(mapped)
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "reduce":
            if not expression:
                return {"value": None, "error": "'expression' is required for reduce."}
            if not items:
                return {"value": param if param is not None else None}
            acc = param if param is not None else items[0]
            start_idx = 0 if param is not None else 1
            for i in range(start_idx, len(items)):
                # The Lua expression can use 'acc' and 'item'
                acc = evaluate_expression(
                    expression, None, context={"acc": acc, "item": items[i]}
                )
            return {"value": acc}
        elif operation == "flat_map":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for flat_map.",
                }
            result = []
            for index, item in enumerate(items, 1):
                mapped = _evaluate_expression_optimized(
                    expression, item, index=index, items_list=items
                )
                # Convert Lua tables to Python lists
                from lib.lua import lua_to_python

                if "LuaTable" in type(mapped).__name__:
                    mapped = lua_to_python(mapped)
                if isinstance(mapped, list):
                    result.extend(mapped)
                else:
                    result.append(mapped)
            return {"value": result}
        elif operation in ("all_by", "every"):
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for all_by/every.",
                }
            return {
                "value": all(
                    bool(
                        _evaluate_expression_optimized(
                            expression, item, index=index, items_list=items
                        )
                    )
                    for index, item in enumerate(items, 1)
                )
            }
        elif operation in ("any_by", "some"):
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for any_by/some.",
                }
            return {
                "value": any(
                    bool(
                        _evaluate_expression_optimized(
                            expression, item, index=index, items_list=items
                        )
                    )
                    for index, item in enumerate(items, 1)
                )
            }
        elif operation == "filter_by":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for filter_by.",
                }
            return {
                "value": [
                    item
                    for index, item in enumerate(items, 1)
                    if bool(
                        _evaluate_expression_optimized(
                            expression, item, index=index, items_list=items
                        )
                    )
                ]
            }
        elif operation == "zip_with":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for zip_with.",
                }
            if not isinstance(items, list) or not isinstance(others, list):
                return {
                    "value": None,
                    "error": "Both 'items' and 'others' must be lists for zip_with.",
                }
            min_len = min(len(items), len(others))
            result = []
            for i in range(min_len):
                val = evaluate_expression(
                    expression, None, context={"item": items[i], "other": others[i]}
                )
                result.append(val)
            return {"value": result}
        # --- End New Functional Operations ---
        elif operation == "min":
            if not items:
                return {"value": None, "error": "Cannot find minimum of empty list"}
            try:
                return {"value": min(items)}
            except TypeError as e:
                return {
                    "value": None,
                    "error": f"Cannot compare items for minimum: {e}",
                }
        elif operation == "max":
            if not items:
                return {"value": None, "error": "Cannot find maximum of empty list"}
            try:
                return {"value": max(items)}
            except TypeError as e:
                return {
                    "value": None,
                    "error": f"Cannot compare items for maximum: {e}",
                }
        elif operation == "join":
            delimiter = param if param is not None else ""
            return {"value": delimiter.join(str(item) for item in items)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


# Export the main function for use in other modules
__all__ = ["lists_tool", "_lists_impl"]
