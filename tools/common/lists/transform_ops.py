from typing import Any, Callable
import random


def op_shuffle(items: list, **kwargs) -> dict:
    """Randomizes order of items."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for shuffle."}
    result = items[:]
    random.shuffle(result)
    return {"value": result}


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
