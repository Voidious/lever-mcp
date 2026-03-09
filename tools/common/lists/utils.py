from typing import Any, Callable
import random


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
            # Convert integer keys to strings like JSON does
            if isinstance(k, int):
                k = str(k)
            result[k] = item
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"key_by failed: {str(e)}"}


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
